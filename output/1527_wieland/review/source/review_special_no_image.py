# -*- coding: utf-8 -*-
"""Lightweight independent RFA reviewer for families that stall image/mesh export.

Reads ../special_target.json (one target) and writes ../special_native_review.json.
It opens the saved RFA in Revit 2025, checks category/warnings, and measures an
independent union of element bounding boxes. It never saves or modifies the family.
"""
import json
import os
import traceback
import clr

clr.AddReference("RevitAPI")
from Autodesk.Revit import DB

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TARGET_PATH = os.path.join(ROOT, "special_target.json")
OUT = os.path.join(ROOT, "special_native_review.json")
MM_PER_FOOT = 304.8
app = __revit__.Application


def write(data):
    with open(OUT, "w") as f:
        json.dump(data, f, indent=2, default=str)


target = json.load(open(TARGET_PATH))
if isinstance(target, list):
    target = target[0]

row = {
    "group_key": target.get("group_key"),
    "row_ids": target.get("row_ids") or [str(target.get("row_id"))],
    "section": target.get("section"),
    "rfa": target.get("rfa"),
    "expected_category": target.get("expected_category"),
    "expected_dimensions_mm": target.get("expected_dimensions_mm"),
    "validation_path": target.get("validation_path"),
    "stage": "starting",
}
write(row)

template_ids = set()
try:
    vp = row.get("validation_path")
    if vp and os.path.isfile(vp):
        v = json.load(open(vp))
        template_ids = set(str(x) for x in (v.get("template_form_ids") or []))
except Exception:
    template_ids = set()

doc = None
try:
    doc = app.OpenDocumentFile(row["rfa"])
    row["stage"] = "opened"
    row["is_family_document"] = bool(doc.IsFamilyDocument)
    family = doc.OwnerFamily if doc.IsFamilyDocument else None
    row["category"] = family.FamilyCategory.Name if family and family.FamilyCategory else None
    row["category_match"] = row["expected_category"] is None or row["category"] == row["expected_category"]
    row["warnings"] = [w.GetDescriptionText() for w in doc.GetWarnings()]
    write(row)

    mins = [None, None, None]
    maxs = [None, None, None]
    bbox_count = 0
    # Family reference planes/levels can carry enormous nominal bounding boxes.
    # For these custom families the physical solids are GenericForm elements,
    # so measure those directly.
    collector = DB.FilteredElementCollector(doc).OfClass(DB.GenericForm)
    for element in collector:
        try:
            if str(element.Id.Value) in template_ids:
                continue
            if element.Category is not None and element.Category.Id.Value in (
                int(DB.BuiltInCategory.OST_ReferenceLines),
                int(DB.BuiltInCategory.OST_LightingFixtureSource),
            ):
                continue
            box = element.get_BoundingBox(None)
            if box is None:
                continue
            bbox_count += 1
            vals_min = [box.Min.X, box.Min.Y, box.Min.Z]
            vals_max = [box.Max.X, box.Max.Y, box.Max.Z]
            for i in range(3):
                mins[i] = vals_min[i] if mins[i] is None else min(mins[i], vals_min[i])
                maxs[i] = vals_max[i] if maxs[i] is None else max(maxs[i], vals_max[i])
        except Exception:
            pass

    row["bbox_element_count"] = bbox_count
    if bbox_count:
        actual = [(maxs[i] - mins[i]) * MM_PER_FOOT for i in range(3)]
        row["bbox_extents_mm"] = {
            "min_ft": mins,
            "max_ft": maxs,
            "size_mm_xyz": actual,
        }
        expected = row.get("expected_dimensions_mm") or []
        axes = []
        passed = True
        authoritative = 0
        for i in range(min(3, len(expected))):
            exp = expected[i]
            if exp is None:
                axes.append({"axis": i, "expected_mm": None, "actual_mm": actual[i], "error_mm": None, "pass": None})
                continue
            authoritative += 1
            err = abs(actual[i] - float(exp))
            ok = err <= 1.0
            passed = passed and ok
            axes.append({"axis": i, "expected_mm": float(exp), "actual_mm": actual[i], "error_mm": err, "pass": ok})
        row["dimension_compare"] = {
            "axes": axes,
            "authoritative_axis_count": authoritative,
            "all_authoritative_axes_within_1mm": passed if authoritative else None,
        }
    row["stage"] = "measured"
except Exception:
    row["stage"] = "error"
    row["error"] = traceback.format_exc()
finally:
    if doc is not None:
        try:
            doc.Close(False)
        except Exception:
            pass
    write(row)
