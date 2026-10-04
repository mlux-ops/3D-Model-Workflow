# -*- coding: utf-8 -*-
"""Independent batch reviewer for 1527 Wieland RFA spot checks.

Run only through the shared serialized Revit runner. Reads review_targets.json
from the parent review directory and writes native_review.json plus one fresh
preview image per target. It never saves or modifies a reviewed family.
"""
import json
import os
import traceback
import clr

clr.AddReference("RevitAPI")
from Autodesk.Revit import DB
from System.Collections.Generic import List

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TARGETS = os.path.join(ROOT, "review_targets.json")
OUT = os.path.join(ROOT, "native_review.json")
PREVIEWS = os.path.join(ROOT, "previews")
MM_PER_FOOT = 304.8
app = __revit__.Application


def write_report(report):
    with open(OUT, "w") as handle:
        json.dump(report, handle, indent=2, default=str)


def point_tuple(p):
    return (p.X, p.Y, p.Z)


def walk_geometry(ge, points, doc):
    for g in ge:
        if isinstance(g, DB.Solid) and g.Volume > 1e-10:
            gs = doc.GetElement(g.GraphicsStyleId) if g.GraphicsStyleId != DB.ElementId.InvalidElementId else None
            cat = gs.GraphicsStyleCategory if gs else None
            skip = False
            while cat is not None:
                if cat.Id.Value == int(DB.BuiltInCategory.OST_LightingFixtureSource):
                    skip = True
                    break
                cat = cat.Parent
            if skip:
                continue
            for face in g.Faces:
                try:
                    mesh = face.Triangulate(1.0)
                    for i in range(mesh.Vertices.Count):
                        points.append(point_tuple(mesh.Vertices[i]))
                except Exception:
                    pass
            for edge in g.Edges:
                try:
                    for p in edge.Tessellate():
                        points.append(point_tuple(p))
                except Exception:
                    pass
        elif isinstance(g, DB.GeometryInstance):
            try:
                walk_geometry(g.GetInstanceGeometry(), points, doc)
            except Exception:
                try:
                    walk_geometry(g.GetSymbolGeometry(), points, doc)
                except Exception:
                    pass


def collect_points(doc):
    options = DB.Options()
    options.DetailLevel = DB.ViewDetailLevel.Fine
    options.ComputeReferences = False
    points = []
    ids_seen = set()
    collector = DB.FilteredElementCollector(doc).WhereElementIsNotElementType()
    for element in collector:
        try:
            if element.Id.Value in ids_seen:
                continue
            ids_seen.add(element.Id.Value)
            if element.Category is not None and element.Category.Id.Value == int(DB.BuiltInCategory.OST_LightingFixtureSource):
                continue
            ge = element.get_Geometry(options)
            if ge is not None:
                walk_geometry(ge, points, doc)
        except Exception:
            continue
    return points


def extents_mm(points):
    if not points:
        return None
    mins = [min(p[i] for p in points) for i in range(3)]
    maxs = [max(p[i] for p in points) for i in range(3)]
    size = [(maxs[i] - mins[i]) * MM_PER_FOOT for i in range(3)]
    return {
        "min_ft": mins,
        "max_ft": maxs,
        "size_mm_xyz": size,
        "sorted_size_mm": sorted(size, reverse=True),
    }


def dimension_compare(actual_mm, expected_mm):
    if not actual_mm or not expected_mm:
        return None
    actual = [float(x) for x in actual_mm]
    expected = [None if x is None else float(x) for x in expected_mm]
    # Families in this project are authored in their intended axes, so compare
    # axis-for-axis. Null expected values are explicitly non-authoritative.
    axes = []
    all_authoritative_pass = True
    authoritative_count = 0
    for i in range(min(3, len(actual), len(expected))):
        e = expected[i]
        a = actual[i]
        if e is None:
            axes.append({"axis": i, "actual_mm": a, "expected_mm": None, "error_mm": None, "pass": None})
            continue
        authoritative_count += 1
        err = abs(a - e)
        passed = err <= 1.0
        if not passed:
            all_authoritative_pass = False
        axes.append({"axis": i, "actual_mm": a, "expected_mm": e, "error_mm": err, "pass": passed})
    return {
        "axes": axes,
        "authoritative_axis_count": authoritative_count,
        "all_authoritative_axes_within_1mm": all_authoritative_pass if authoritative_count else None,
    }


def export_preview(doc, label, ext):
    if ext is None:
        return None
    view_types = [
        x for x in DB.FilteredElementCollector(doc).OfClass(DB.ViewFamilyType)
        if x.ViewFamily == DB.ViewFamily.ThreeDimensional
    ]
    if not view_types:
        return None
    tx = DB.Transaction(doc, "Temporary review view")
    tx.Start()
    view = DB.View3D.CreateIsometric(doc, view_types[0].Id)
    view.Name = "1527 REVIEW " + str(label)[:80]
    center = DB.XYZ(
        (ext["min_ft"][0] + ext["max_ft"][0]) * 0.5,
        (ext["min_ft"][1] + ext["max_ft"][1]) * 0.5,
        (ext["min_ft"][2] + ext["max_ft"][2]) * 0.5,
    )
    raw = [
        max(1e-3, ext["max_ft"][i] - ext["min_ft"][i])
        for i in range(3)
    ]
    span = max(raw)
    eye_dir = DB.XYZ(1.0, -1.0, 0.75).Normalize()
    fwd = eye_dir.Negate()
    right = fwd.CrossProduct(DB.XYZ.BasisZ).Normalize()
    up = right.CrossProduct(fwd).Normalize()
    view.SetOrientation(DB.ViewOrientation3D(center + eye_dir.Multiply(span * 3.0 + 2.0), up, fwd))
    pad = max(span * 0.12, 0.08)
    box = DB.BoundingBoxXYZ()
    box.Min = DB.XYZ(ext["min_ft"][0] - pad, ext["min_ft"][1] - pad, ext["min_ft"][2] - pad)
    box.Max = DB.XYZ(ext["max_ft"][0] + pad, ext["max_ft"][1] + pad, ext["max_ft"][2] + pad)
    view.SetSectionBox(box)
    view.DetailLevel = DB.ViewDetailLevel.Fine
    try:
        view.DisplayStyle = DB.DisplayStyle.Shading
    except Exception:
        pass
    tx.Commit()

    if not os.path.isdir(PREVIEWS):
        os.makedirs(PREVIEWS)
    safe = "".join(c if c.isalnum() or c in "-_." else "_" for c in str(label))
    stem = os.path.join(PREVIEWS, safe)
    opts = DB.ImageExportOptions()
    opts.ExportRange = DB.ExportRange.SetOfViews
    ids = List[DB.ElementId]()
    ids.Add(view.Id)
    opts.SetViewsAndSheets(ids)
    opts.ZoomType = DB.ZoomFitType.FitToPage
    opts.PixelSize = 900
    opts.ImageResolution = DB.ImageResolution.DPI_150
    opts.HLRandWFViewsFileType = DB.ImageFileType.PNG
    opts.ShadowViewsFileType = DB.ImageFileType.PNG
    opts.FilePath = stem
    doc.ExportImage(opts)
    files = [
        os.path.join(PREVIEWS, name) for name in os.listdir(PREVIEWS)
        if name.startswith(safe) and name.lower().endswith(".png")
    ]
    return sorted(files)


targets = json.load(open(TARGETS))
report = {"targets": [], "errors": []}
write_report(report)

for target in targets:
    row = {
        "row_id": str(target.get("row_id")),
        "section": target.get("section"),
        "status": target.get("status"),
        "rfa": target.get("rfa"),
        "item": target.get("item"),
        "group_key": target.get("group_key"),
        "row_ids": target.get("row_ids") or [str(target.get("row_id"))],
        "manufacturer": target.get("manufacturer"),
        "expected_category": target.get("expected_category"),
        "expected_dimensions_mm": target.get("expected_dimensions_mm"),
        "worker_native_pass": target.get("worker_native_pass"),
        "source_urls": target.get("source_urls") or [],
        "exists": os.path.isfile(target.get("rfa") or ""),
    }
    report["targets"].append(row)
    write_report(report)
    if not row["exists"]:
        row["error"] = "RFA missing"
        continue
    doc = None
    try:
        doc = app.OpenDocumentFile(row["rfa"])
        row["is_family_document"] = bool(doc.IsFamilyDocument)
        family = doc.OwnerFamily if doc.IsFamilyDocument else None
        row["category"] = family.FamilyCategory.Name if family and family.FamilyCategory else None
        row["placement_type"] = str(family.FamilyPlacementType) if family else None
        row["warnings"] = [w.GetDescriptionText() for w in doc.GetWarnings()]
        points = collect_points(doc)
        row["geometry_point_count"] = len(points)
        row["geometry_extents"] = extents_mm(points)
        if row["geometry_extents"] is not None:
            row["dimension_compare"] = dimension_compare(
                row["geometry_extents"]["size_mm_xyz"],
                row["expected_dimensions_mm"],
            )
        row["category_match"] = (
            row["expected_category"] is None or row["category"] == row["expected_category"]
        )
        row["preview_files"] = export_preview(doc, row["row_id"], row["geometry_extents"])
    except Exception:
        row["error"] = traceback.format_exc()
        report["errors"].append({"row_id": row["row_id"], "error": row["error"]})
    finally:
        if doc is not None:
            try:
                doc.Close(False)
            except Exception:
                pass
        write_report(report)

write_report(report)
