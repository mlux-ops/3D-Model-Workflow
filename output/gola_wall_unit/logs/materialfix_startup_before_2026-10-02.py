# -*- coding: utf-8 -*-
"""MaterialFix routes (added 2026-09-26 by Claude for the Ligne Noir texture/pattern alignment fix).

Read and set a material's texture transforms and inspect its surface patterns, over pyRevit Routes:
  POST /material-fix/materials/inspect   {"bitmap_contains": "Ligne", "name_contains": ""}
  POST /material-fix/materials/set_texture
       {"material_id": "123", "scale_x_in": 35.25, "scale_y_in": 39.5,
        "offset_x_in": 0, "offset_y_in": 0, "rotation_deg": 0, "dry_run": true}
  POST /material-fix/document/save        {}   (local save only; never synchronises with central)

Safe to delete this folder; nothing else depends on it.
"""
from pyrevit import routes
from Autodesk.Revit import DB
from Autodesk.Revit.DB import Visual

api = routes.API("material-fix")

BITMAP_PROPS = ("generic_diffuse", "generic_bump_map", "generic_reflectivity_at_0deg", "generic_glossiness",
                "generic_transparency", "generic_cutout_opacity")
T_SX = "texture_RealWorldScaleX"
T_SY = "texture_RealWorldScaleY"
T_OX = "texture_RealWorldOffsetX"
T_OY = "texture_RealWorldOffsetY"
T_ROT = "texture_WAngle"
T_LOCK = "texture_ScaleLock"
T_LINK = "texture_LinkTextureTransforms"
T_UREP = "texture_URepeat"
T_VREP = "texture_VRepeat"
T_PATH = "unifiedbitmap_Bitmap"
FT_TO_IN = 12.0


def _dist_in(prop):
    """AssetPropertyDistance -> inches."""
    try:
        return DB.UnitUtils.Convert(prop.Value, prop.GetUnitTypeId(), DB.UnitTypeId.Inches)
    except Exception:
        return None


def _set_dist_in(prop, inches):
    v = DB.UnitUtils.Convert(float(inches), DB.UnitTypeId.Inches, prop.GetUnitTypeId())
    if not prop.IsValidValue(v):
        raise ValueError("value %r (%s units) rejected for %s" % (v, prop.GetUnitTypeId().TypeId, prop.Name))
    prop.Value = v
    return v


def _val(asset, name):
    p = asset.FindByName(name)
    if p is None:
        return None
    if isinstance(p, Visual.AssetPropertyDistance):
        return {"in": _dist_in(p), "raw": p.Value, "unit": p.GetUnitTypeId().TypeId}
    try:
        return p.Value
    except Exception:
        return str(p)


def _bitmaps(asset):
    out = []
    for i in range(asset.Size):
        prop = asset.Get(i)
        try:
            n = prop.NumberOfConnectedProperties
        except Exception:
            n = 0
        if n < 1:
            continue
        try:
            conn = prop.GetSingleConnectedAsset()
        except Exception:
            continue
        if conn is None or conn.FindByName(T_PATH) is None:
            continue
        rec = {"slot": prop.Name}
        for key, name in (("path", T_PATH), ("scale_x", T_SX), ("scale_y", T_SY), ("offset_x", T_OX),
                          ("offset_y", T_OY), ("rotation_deg", T_ROT), ("scale_lock", T_LOCK),
                          ("link_transforms", T_LINK), ("u_repeat", T_UREP), ("v_repeat", T_VREP)):
            v = _val(conn, name)
            rec[key] = v
        out.append(rec)
    return out


def _pattern(doc, pid):
    if pid is None or pid == DB.ElementId.InvalidElementId:
        return None
    fpe = doc.GetElement(pid)
    if fpe is None:
        return None
    fp = fpe.GetFillPattern()
    grids = []
    for g in fp.GetFillGrids():
        grids.append({"angle_deg": g.Angle * 180.0 / 3.141592653589793,
                      "origin_in": [g.Origin.U * FT_TO_IN, g.Origin.V * FT_TO_IN],
                      "offset_in": g.Offset * FT_TO_IN, "shift_in": g.Shift * FT_TO_IN,
                      "segments_in": [s * FT_TO_IN for s in g.GetSegments()]})
    return {"id": str(pid.Value if hasattr(pid, "Value") else pid.IntegerValue), "name": fpe.Name,
            "target": str(fp.Target), "grids": grids}


def _material_record(doc, mat):
    rec = {"id": str(mat.Id.Value if hasattr(mat.Id, "Value") else mat.Id.IntegerValue), "name": mat.Name,
           "surface_fg": _pattern(doc, mat.SurfaceForegroundPatternId),
           "surface_bg": _pattern(doc, mat.SurfaceBackgroundPatternId),
           "use_render_appearance": getattr(mat, "UseRenderAppearanceForShading", None),
           "appearance": None, "bitmaps": []}
    aid = mat.AppearanceAssetId
    if aid is None or aid == DB.ElementId.InvalidElementId:
        return rec
    ae = doc.GetElement(aid)
    if ae is None:
        return rec
    rec["appearance"] = ae.Name
    try:
        rec["bitmaps"] = _bitmaps(ae.GetRenderingAsset())
    except Exception as e:
        rec["bitmaps_error"] = str(e)
    return rec


@api.route('/materials/inspect', methods=['POST'])
def inspect(doc, request):
    data = request.data or {}
    bc = (data.get("bitmap_contains") or "").lower()
    nc = (data.get("name_contains") or "").lower()
    found, scanned = [], 0
    for mat in DB.FilteredElementCollector(doc).OfClass(DB.Material):
        scanned += 1
        name_hit = bool(nc) and nc in mat.Name.lower()
        if nc and not bc and not name_hit:
            continue
        try:
            rec = _material_record(doc, mat)
        except Exception as e:
            continue
        bm_hit = bool(bc) and any(bc in (b.get("path") or "").lower() for b in rec["bitmaps"])
        if name_hit or bm_hit:
            found.append(rec)
    return routes.Response(status=200, data={"status": "success", "scanned": scanned, "materials": found})


@api.route('/materials/set_texture', methods=['POST'])
def set_texture(doc, request):
    data = request.data or {}
    mat = doc.GetElement(DB.ElementId(int(data["material_id"])))
    if not isinstance(mat, DB.Material):
        return routes.Response(status=400, data={"status": "error", "error": "not a material"})
    before = _material_record(doc, mat)
    if data.get("dry_run", True):
        return routes.Response(status=200, data={"status": "dry_run", "before": before})
    slots = data.get("slots") or ["generic_diffuse", "generic_bump_map"]
    changed = []
    t = DB.Transaction(doc, "MaterialFix: set texture transforms")
    t.Start()
    try:
        with Visual.AppearanceAssetEditScope(doc) as scope:
            editable = scope.Start(mat.AppearanceAssetId)
            for slot in slots:
                prop = editable.FindByName(slot)
                if prop is None or prop.NumberOfConnectedProperties < 1:
                    continue
                conn = prop.GetSingleConnectedAsset()
                lock = conn.FindByName(T_LOCK)
                lock_was = bool(lock.Value) if lock is not None else None
                if lock is not None and lock.Value:
                    lock.Value = False  # lock rescales the other axis on write; restored below
                _set_dist_in(conn.FindByName(T_SX), data["scale_x_in"])
                _set_dist_in(conn.FindByName(T_SY), data["scale_y_in"])
                if conn.FindByName(T_OX) is not None:
                    _set_dist_in(conn.FindByName(T_OX), data.get("offset_x_in", 0.0))
                    _set_dist_in(conn.FindByName(T_OY), data.get("offset_y_in", 0.0))
                if conn.FindByName(T_ROT) is not None:
                    conn.FindByName(T_ROT).Value = float(data.get("rotation_deg", 0.0))
                if lock is not None:
                    lock.Value = lock_was
                changed.append(slot)
            scope.Commit(True)
        t.Commit()
    except Exception as e:
        if t.HasStarted() and not t.HasEnded():
            t.RollBack()
        return routes.Response(status=500, data={"status": "error", "error": str(e), "before": before})
    after = _material_record(doc, mat)
    return routes.Response(status=200, data={"status": "success", "changed": changed, "before": before, "after": after})


def _eid(e):
    return str(e.Value if hasattr(e, "Value") else e.IntegerValue)


@api.route('/materials/usage', methods=['POST'])
def usage(doc, request):
    """Elements that carry the material (by type/layer or by Paint), with the faces that show it:
    face type, area, bounding box of the face in its own UV (feet -> in), and whether the face is planar."""
    data = request.data or {}
    mid = DB.ElementId(int(data["material_id"]))
    limit = int(data.get("limit", 40))
    out = []
    opts = DB.Options()
    opts.ComputeReferences = False
    coll = DB.FilteredElementCollector(doc).WhereElementIsNotElementType()
    for el in coll:
        try:
            by_type = mid in el.GetMaterialIds(False)
            by_paint = mid in el.GetMaterialIds(True)
        except Exception:
            continue
        if not (by_type or by_paint):
            continue
        rec = {"id": _eid(el.Id), "category": el.Category.Name if el.Category else None,
               "name": el.Name, "by_type": by_type, "painted": by_paint, "faces": []}
        try:
            t = doc.GetElement(el.GetTypeId())
            rec["type"] = (t.FamilyName + " : " + t.Name) if t is not None and hasattr(t, "FamilyName") else None
        except Exception:
            rec["type"] = None
        try:
            geo = el.get_Geometry(opts)
            stack = list(geo) if geo is not None else []
            while stack:
                g = stack.pop()
                if isinstance(g, DB.GeometryInstance):
                    stack.extend(list(g.GetInstanceGeometry()))
                    continue
                if not isinstance(g, DB.Solid):
                    continue
                for f in g.Faces:
                    if f.MaterialElementId != mid and not (by_paint and doc.IsPainted(el.Id, f)):
                        continue
                    bb = f.GetBoundingBox()
                    fr = {"type": f.GetType().Name, "area_sf": f.Area,
                          "uv_min_in": [bb.Min.U * FT_TO_IN, bb.Min.V * FT_TO_IN],
                          "uv_max_in": [bb.Max.U * FT_TO_IN, bb.Max.V * FT_TO_IN]}
                    if isinstance(f, DB.PlanarFace):
                        n = f.FaceNormal
                        fr["normal"] = [n.X, n.Y, n.Z]
                        fr["x_vec"] = [f.XVector.X, f.XVector.Y, f.XVector.Z]
                        fr["y_vec"] = [f.YVector.X, f.YVector.Y, f.YVector.Z]
                    # 3D edge lengths vs UV extent: shows whether face UV is real-world scaled
                    try:
                        p00 = f.Evaluate(DB.UV(bb.Min.U, bb.Min.V))
                        p10 = f.Evaluate(DB.UV(bb.Max.U, bb.Min.V))
                        p01 = f.Evaluate(DB.UV(bb.Min.U, bb.Max.V))
                        fr["xyz_len_u_in"] = p00.DistanceTo(p10) * FT_TO_IN
                        fr["xyz_len_v_in"] = p00.DistanceTo(p01) * FT_TO_IN
                    except Exception as e:
                        fr["eval_error"] = str(e)
                    rec["faces"].append(fr)
                    if len(rec["faces"]) >= 12:
                        break
        except Exception as e:
            rec["geometry_error"] = str(e)
        out.append(rec)
        if len(out) >= limit:
            break
    return routes.Response(status=200, data={"status": "success", "elements": out})


@api.route('/views/find', methods=['POST'])
def views_find(doc, request):
    data = request.data or {}
    words = [w.lower() for w in (data.get("contains") or [])]
    out = []
    for v in DB.FilteredElementCollector(doc).OfClass(DB.View):
        try:
            if v.IsTemplate:
                continue
            n = v.Name.lower()
            if words and not any(w in n for w in words):
                continue
            d = v.ViewDirection
            out.append({"id": _eid(v.Id), "name": v.Name, "type": str(v.ViewType),
                        "direction": [round(d.X, 3), round(d.Y, 3), round(d.Z, 3)],
                        "style": str(v.DisplayStyle), "scale": v.Scale})
        except Exception:
            continue
    return routes.Response(status=200, data={"status": "success", "views": out})


@api.route('/views/export', methods=['POST'])
def views_export(doc, request):
    """Export one view (by id) to PNG without activating it. Read-only."""
    import os
    data = request.data or {}
    vid = DB.ElementId(int(data["view_id"]))
    folder = data.get("folder") or os.path.join(os.environ.get("TEMP", "C:/Temp"), "MaterialFix")
    if not os.path.isdir(folder):
        os.makedirs(folder)
    prefix = os.path.join(folder, data.get("prefix") or ("view_" + data["view_id"]))
    opts = DB.ImageExportOptions()
    opts.ExportRange = DB.ExportRange.SetOfViews
    ids = __import__("System").Collections.Generic.List[DB.ElementId]()
    ids.Add(vid)
    opts.SetViewsAndSheets(ids)
    opts.FilePath = prefix
    opts.HLRandWFViewsFileType = DB.ImageFileType.PNG
    opts.ShadowViewsFileType = DB.ImageFileType.PNG
    opts.ZoomType = DB.ZoomFitType.FitToPage
    opts.PixelSize = int(data.get("pixel_size", 4000))
    opts.FitDirection = DB.FitDirectionType.Horizontal
    opts.ImageResolution = DB.ImageResolution.DPI_300
    doc.ExportImage(opts)
    files = sorted([os.path.join(folder, f) for f in os.listdir(folder) if f.startswith(os.path.basename(prefix))],
                   key=os.path.getmtime)
    return routes.Response(status=200, data={"status": "success", "files": files[-3:]})


@api.route('/views/temp_face_export', methods=['POST'])
def temp_face_export(doc, request):
    """Create a temporary orthographic Realistic 3D view looking straight at one face direction of an
    element (section box around the element), export it, then delete the view. Returns the image path
    and the view's world-to-image mapping so a caller can measure in inches."""
    import os
    data = request.data or {}
    el = doc.GetElement(DB.ElementId(int(data["element_id"])))
    n = data["normal"]                               # outward face normal, e.g. [1,0,0]
    normal = DB.XYZ(float(n[0]), float(n[1]), float(n[2])).Normalize()
    margin = float(data.get("margin_in", 2.0)) / 12.0
    bb = el.get_BoundingBox(None)
    folder = data.get("folder") or os.path.join(os.environ.get("TEMP", "C:/Temp"), "MaterialFix")
    if not os.path.isdir(folder):
        os.makedirs(folder)
    prefix = os.path.join(folder, data.get("prefix") or ("face_" + data["element_id"]))
    vft = None
    for t in DB.FilteredElementCollector(doc).OfClass(DB.ViewFamilyType):
        if t.ViewFamily == DB.ViewFamily.ThreeDimensional:
            vft = t
            break
    tx = DB.Transaction(doc, "MaterialFix: temporary face view")
    tx.Start()
    try:
        v = DB.View3D.CreateIsometric(doc, vft.Id)
        v.Name = "zz MaterialFix temp " + data["element_id"]
        centre = (bb.Min + bb.Max) * 0.5
        eye = centre + normal * 20.0
        up = DB.XYZ.BasisZ if abs(normal.Z) < 0.9 else DB.XYZ.BasisY
        v.SetOrientation(DB.ViewOrientation3D(eye, up, normal.Negate()))
        sb = DB.BoundingBoxXYZ()
        sb.Min = DB.XYZ(bb.Min.X - margin, bb.Min.Y - margin, bb.Min.Z - margin)
        sb.Max = DB.XYZ(bb.Max.X + margin, bb.Max.Y + margin, bb.Max.Z + margin)
        v.SetSectionBox(sb)
        v.DisplayStyle = DB.DisplayStyle.Realistic
        try:
            v.DetailLevel = DB.ViewDetailLevel.Fine
        except Exception:
            pass
        for bic in (DB.BuiltInCategory.OST_Levels, DB.BuiltInCategory.OST_Grids,
                    DB.BuiltInCategory.OST_SectionBox):
            try:
                v.SetCategoryHidden(DB.Category.GetCategory(doc, bic).Id, True)
            except Exception:
                pass
        # crop to the element's extent in view coordinates so the export is the wall, not the model
        doc.Regenerate()
        cb = v.CropBox
        inv = cb.Transform.Inverse
        xs, ys = [], []
        for cx in (bb.Min.X, bb.Max.X):
            for cy in (bb.Min.Y, bb.Max.Y):
                for cz in (bb.Min.Z, bb.Max.Z):
                    p = inv.OfPoint(DB.XYZ(cx, cy, cz))
                    xs.append(p.X)
                    ys.append(p.Y)
        nb = DB.BoundingBoxXYZ()
        nb.Transform = cb.Transform
        nb.Min = DB.XYZ(min(xs) - margin, min(ys) - margin, cb.Min.Z)
        nb.Max = DB.XYZ(max(xs) + margin, max(ys) + margin, cb.Max.Z)
        v.CropBox = nb
        v.CropBoxActive = True
        v.CropBoxVisible = False
        vid = v.Id
        tx.Commit()
    except Exception as e:
        if tx.HasStarted() and not tx.HasEnded():
            tx.RollBack()
        return routes.Response(status=500, data={"status": "error", "stage": "create", "error": str(e)})
    result = {"status": "success"}
    try:
        opts = DB.ImageExportOptions()
        opts.ExportRange = DB.ExportRange.SetOfViews
        ids = __import__("System").Collections.Generic.List[DB.ElementId]()
        ids.Add(vid)
        opts.SetViewsAndSheets(ids)
        opts.FilePath = prefix
        opts.HLRandWFViewsFileType = DB.ImageFileType.PNG
        opts.ShadowViewsFileType = DB.ImageFileType.PNG
        opts.ZoomType = DB.ZoomFitType.FitToPage
        opts.PixelSize = int(data.get("pixel_size", 4000))
        opts.FitDirection = DB.FitDirectionType.Horizontal
        opts.ImageResolution = DB.ImageResolution.DPI_300
        doc.ExportImage(opts)
        files = sorted([os.path.join(folder, f) for f in os.listdir(folder)
                        if f.startswith(os.path.basename(prefix))], key=os.path.getmtime)
        result["files"] = files[-2:]
        v = doc.GetElement(vid)
        outl = v.Outline                                   # view-plane extents of the exported area (feet)
        result["outline_ft"] = [outl.Min.U, outl.Min.V, outl.Max.U, outl.Max.V]
        vo = v.GetOrientation()
        right = vo.UpDirection.CrossProduct(vo.ForwardDirection)
        result["right"] = [right.X, right.Y, right.Z]
        result["up"] = [vo.UpDirection.X, vo.UpDirection.Y, vo.UpDirection.Z]
        result["bbox_ft"] = [bb.Min.X, bb.Min.Y, bb.Min.Z, bb.Max.X, bb.Max.Y, bb.Max.Z]
        c2 = v.CropBox
        result["crop_view_ft"] = [c2.Min.X, c2.Min.Y, c2.Max.X, c2.Max.Y]
        o = c2.Transform.Origin
        result["crop_origin_ft"] = [o.X, o.Y, o.Z]
        result["crop_basis_x"] = [c2.Transform.BasisX.X, c2.Transform.BasisX.Y, c2.Transform.BasisX.Z]
        result["crop_basis_y"] = [c2.Transform.BasisY.X, c2.Transform.BasisY.Y, c2.Transform.BasisY.Z]
    except Exception as e:
        result = {"status": "error", "stage": "export", "error": str(e)}
    tx2 = DB.Transaction(doc, "MaterialFix: delete temporary face view")
    tx2.Start()
    try:
        doc.Delete(vid)
        tx2.Commit()
        result["temp_view_deleted"] = True
    except Exception as e:
        if tx2.HasStarted() and not tx2.HasEnded():
            tx2.RollBack()
        result["temp_view_deleted"] = False
        result["delete_error"] = str(e)
    return routes.Response(status=200 if result.get("status") == "success" else 500, data=result)


@api.route('/document/save', methods=['POST'])
def save(doc, request):
    """Local save only. For a workshared cloud model this writes the local cache; it does not sync."""
    try:
        if doc.IsWorkshared:
            opts = DB.SaveOptions()
            doc.Save(opts)
        else:
            doc.Save()
        return routes.Response(status=200, data={"status": "success", "workshared": doc.IsWorkshared})
    except Exception as e:
        return routes.Response(status=500, data={"status": "error", "error": str(e)})
