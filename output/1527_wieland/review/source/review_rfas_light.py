# -*- coding: utf-8 -*-
"""Independent saved-RFA dimension/category reviewer without image export.

Reads ../review_targets.json and writes ../light_native_review.json.
Measures physical GenericForm bounding boxes after excluding each family's
template form IDs from its validation receipt. If no GenericForm exists,
falls back to FamilyInstance bounding boxes for downloaded/nested RFAs.
"""
import json
import os
import traceback
import clr

clr.AddReference("RevitAPI")
from Autodesk.Revit import DB

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TARGETS = os.path.join(ROOT, "review_targets.json")
OUT = os.path.join(ROOT, "light_native_review.json")
MM_PER_FOOT = 304.8
app = __revit__.Application


def write(report):
    with open(OUT, "w") as f:
        json.dump(report, f, indent=2, default=str)


def union_boxes(elements, skip_ids):
    mins = [None, None, None]
    maxs = [None, None, None]
    count = 0
    for element in elements:
        try:
            if str(element.Id.Value) in skip_ids:
                continue
            box = element.get_BoundingBox(None)
            if box is None:
                continue
            vals_min = [box.Min.X, box.Min.Y, box.Min.Z]
            vals_max = [box.Max.X, box.Max.Y, box.Max.Z]
            # Reject pathological reference/control boxes.
            dims = [(vals_max[i] - vals_min[i]) * MM_PER_FOOT for i in range(3)]
            if max(dims) > 10000.0:
                continue
            count += 1
            for i in range(3):
                mins[i] = vals_min[i] if mins[i] is None else min(mins[i], vals_min[i])
                maxs[i] = vals_max[i] if maxs[i] is None else max(maxs[i], vals_max[i])
        except Exception:
            pass
    if not count:
        return None, 0
    return [(maxs[i] - mins[i]) * MM_PER_FOOT for i in range(3)], count


def compare(actual, expected):
    if not actual or not expected:
        return None
    axes = []
    passed = True
    authoritative = 0
    for i in range(min(3, len(expected), len(actual))):
        exp = expected[i]
        if exp is None:
            axes.append({"axis": i, "expected_mm": None, "actual_mm": actual[i], "error_mm": None, "pass": None})
            continue
        authoritative += 1
        err = abs(actual[i] - float(exp))
        ok = err <= 1.0
        passed = passed and ok
        axes.append({"axis": i, "expected_mm": float(exp), "actual_mm": actual[i], "error_mm": err, "pass": ok})
    return {
        "axes": axes,
        "authoritative_axis_count": authoritative,
        "all_authoritative_axes_within_1mm": passed if authoritative else None,
    }


targets = json.load(open(TARGETS))
report = {"targets": [], "errors": []}
write(report)

for target in targets:
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
    report["targets"].append(row)
    write(report)
    doc = None
    try:
        skip_ids = set()
        vp = row.get("validation_path")
        if vp and os.path.isfile(vp):
            try:
                v = json.load(open(vp))
                skip_ids = set(str(x) for x in (v.get("template_form_ids") or []))
            except Exception:
                pass
        doc = app.OpenDocumentFile(row["rfa"])
        row["stage"] = "opened"
        row["is_family_document"] = bool(doc.IsFamilyDocument)
        family = doc.OwnerFamily if doc.IsFamilyDocument else None
        row["category"] = family.FamilyCategory.Name if family and family.FamilyCategory else None
        row["category_match"] = row["expected_category"] is None or row["category"] == row["expected_category"]
        row["warnings"] = [w.GetDescriptionText() for w in doc.GetWarnings()]
        write(report)

        actual, count = union_boxes(DB.FilteredElementCollector(doc).OfClass(DB.GenericForm), skip_ids)
        method = "GenericForm"
        if actual is None:
            actual, count = union_boxes(DB.FilteredElementCollector(doc).OfClass(DB.FamilyInstance), skip_ids)
            method = "FamilyInstance"
        row["measurement_method"] = method
        row["physical_element_count"] = count
        row["measured_dimensions_mm"] = actual
        row["dimension_compare"] = compare(actual, row["expected_dimensions_mm"])
        row["stage"] = "measured"
    except Exception:
        row["stage"] = "error"
        row["error"] = traceback.format_exc()
        report["errors"].append({"group_key": row["group_key"], "error": row["error"]})
    finally:
        if doc is not None:
            try:
                doc.Close(False)
            except Exception:
                pass
        write(report)

write(report)
