# -*- coding: utf-8 -*-
"""Independent native grader for the 2026-09-29 Nodes sconce trial (pyRevit IronPython, Revit 2025).

Reads grade_targets.json ({label: absolute RFA path}) beside this file. For each RFA it:
  - opens the family: category, placement type, parameters, light source, family warnings;
  - loads it into a disposable imperial project, hosts it on a wall's exterior face at 5 ft;
  - measures the placed solids along the wall (W), vertical (H) and wall normal (D), with Show Disc on and off;
  - finds the backplate (solids within 0.2 in of the face) and the shade (solids painted with Glass Finish),
    measuring the shade's axial length and max diameter as the min / max caliper over 2,562 directions;
  - substitutes a new material in Metal Finish and in Glass Finish and counts faces that carry it;
  - exports identical front / side / oblique views with one renderer for the blind review (hosting is
    checked numerically; a wall-in-view export rendered the wall over the fixture and was dropped).
Writes grade_report.json and views to grade_views/<label>/. Every document is closed without saving.
"""
import json, math, os, traceback, clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB
from System.Collections.Generic import List

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'grade_report.json')
VIEWS = os.path.join(HERE, 'grade_views')
FT = 12.0
app = __revit__.Application
report = {'atlases': {}, 'errors': []}


def save():
    with open(OUT, 'w') as f:
        json.dump(report, f, indent=2, default=str)


def fib_dirs(n=2562):
    dirs = []
    ga = math.pi * (3.0 - math.sqrt(5.0))
    for i in range(n):
        z = 1.0 - (i + 0.5) * 2.0 / n
        r = math.sqrt(max(0.0, 1.0 - z * z))
        dirs.append((r * math.cos(ga * i), r * math.sin(ga * i), z))
    return [d for d in dirs if d[2] >= 0.0]  # a caliper width is symmetric in +/- d


DIRS = fib_dirs()


LIGHT_SRC_CAT = int(DB.BuiltInCategory.OST_LightingFixtureSource)


def is_light_source(doc, g):
    gs = doc.GetElement(g.GraphicsStyleId) if g.GraphicsStyleId != DB.ElementId.InvalidElementId else None
    cat = gs.GraphicsStyleCategory if gs else None
    while cat is not None:
        if cat.Id.Value == LIGHT_SRC_CAT:
            return True
        cat = cat.Parent
    return False


def solids_of(inst, light=None):
    """Physical solids only. Revit adds a light-source proxy solid to a light family's instance geometry;
    it is excluded here and, when `light` is a list, collected into it."""
    opt = DB.Options(); opt.DetailLevel = DB.ViewDetailLevel.Fine; opt.ComputeReferences = False
    out = []

    def walk(ge):
        for g in ge:
            if isinstance(g, DB.Solid) and g.Volume > 1e-9:
                if is_light_source(inst.Document, g):
                    if light is not None:
                        light.append(g)
                else:
                    out.append(g)
            elif isinstance(g, DB.GeometryInstance):
                walk(g.GetInstanceGeometry())
    walk(inst.get_Geometry(opt))
    return out


def solid_points(s):
    # Finest face meshes plus edge tessellation: coarse meshes cut chords off circles and read ~1.5 % small.
    pts = []
    for f in s.Faces:
        m = f.Triangulate(1.0)
        for i in range(m.Vertices.Count):
            pts.append(m.Vertices[i])
    for ed in s.Edges:
        for p in ed.Tessellate():
            pts.append(p)
    return pts


def frame_coords(pts, origin, ux, uy, uz):
    return [((p - origin).DotProduct(ux) * FT, (p - origin).DotProduct(uy) * FT, (p - origin).DotProduct(uz) * FT) for p in pts]


def extents(c):
    if not c:
        return None
    return {'min': [min(p[i] for p in c) for i in range(3)], 'max': [max(p[i] for p in c) for i in range(3)],
            'size': [max(p[i] for p in c) - min(p[i] for p in c) for i in range(3)]}


def _width(c, d):
    v = [p[0] * d[0] + p[1] * d[1] + p[2] * d[2] for p in c]
    return max(v) - min(v)


def _refine(c, d, sign):
    """Local search around direction d (sign -1 minimises width, +1 maximises); coarse grid is ~4 deg apart."""
    best, bw = d, _width(c, d)
    step = 0.06
    while step > 1e-4:
        improved = False
        for a in (0, 1, 2):
            for s_ in (-step, step):
                q = list(best); q[a] += s_
                n = math.sqrt(q[0] ** 2 + q[1] ** 2 + q[2] ** 2); q = (q[0] / n, q[1] / n, q[2] / n)
                w = _width(c, q)
                if (w - bw) * sign > 1e-9:
                    best, bw, improved = q, w, True
        if not improved:
            step *= 0.5
    return bw


def calipers(c):
    if not c:
        return None
    w = [(_width(c, d), d) for d in DIRS]
    lo = min(w, key=lambda x: x[0]); hi = max(w, key=lambda x: x[0])
    return {'min_width': _refine(c, lo[1], -1), 'max_width': _refine(c, hi[1], +1)}


def solid_material_ids(s):
    return set(f.MaterialElementId.Value for f in s.Faces)


def find_param(inst, name):
    p = inst.LookupParameter(name)
    if p is None:
        p = inst.Symbol.LookupParameter(name)
    return p


def grade(label, path):
    r = {'rfa': path, 'exists': os.path.isfile(path)}
    report['atlases'][label] = r; save()
    if not r['exists']:
        return
    fam = app.OpenDocumentFile(path)
    try:
        r['family_warnings'] = [w.GetDescriptionText() for w in fam.GetWarnings()]
        of = fam.OwnerFamily
        r['category'] = of.FamilyCategory.Name if of.FamilyCategory else None
        fm = fam.FamilyManager
        r['family_params'] = sorted(p.Definition.Name for p in fm.Parameters)
        r['types'] = [t.Name for t in fm.Types]
        try:
            lf = DB.Lighting.LightFamily.GetLightFamily(fam)
            r['light_family'] = lf is not None
            if lf is not None:
                r['light_types'] = lf.GetNumberOfLightTypes()
        except Exception as ex:
            r['light_family'] = 'ERR ' + str(ex)
        srcs = list(DB.FilteredElementCollector(fam).OfCategory(DB.BuiltInCategory.OST_LightingFixtureSource).WhereElementIsNotElementType())
        r['light_source_elements'] = len(srcs)
        r['light_source_family_xyz_in'] = None
        for e in srcs:
            bb = e.get_BoundingBox(None)
            if bb:
                c = (bb.Min + bb.Max) * 0.5
                r['light_source_family_xyz_in'] = [c.X * FT, c.Y * FT, c.Z * FT]
    finally:
        fam.Close(False)

    doc = app.NewProjectDocument(DB.UnitSystem.Imperial)
    try:
        t = DB.Transaction(doc, 'grade'); t.Start()
        fr = clr.Reference[DB.Family]()
        doc.LoadFamily(path, fr)
        family = fr.Value
        sym = doc.GetElement(list(family.GetFamilySymbolIds())[0]); sym.Activate()
        r['placement_type'] = str(family.FamilyPlacementType)
        level = DB.FilteredElementCollector(doc).OfClass(DB.Level).FirstElement()
        wall = DB.Wall.Create(doc, DB.Line.CreateBound(DB.XYZ(-5, 0, 0), DB.XYZ(5, 0, 0)), level.Id, False)
        wall.get_Parameter(DB.BuiltInParameter.WALL_USER_HEIGHT_PARAM).Set(10.0)
        doc.Regenerate()
        ref = list(DB.HostObjectUtils.GetSideFaces(wall, DB.ShellLayerType.Exterior))[0]
        face = wall.GetGeometryObjectFromReference(ref)
        n = face.FaceNormal
        pt = face.Project(DB.XYZ(0, n.Y * 5, 5.0)).XYZPoint
        inst = doc.Create.NewFamilyInstance(ref, pt, DB.XYZ(1, 0, 0), sym)
        doc.Regenerate()
        r['host'] = inst.Host.Id == wall.Id if inst.Host else False
        r['face_normal'] = [n.X, n.Y, n.Z]
        ux, uy, uz = DB.XYZ(1, 0, 0), DB.XYZ(0, 0, 1), n
        light_solids = []
        sol = solids_of(inst, light_solids)
        r['light_proxy_solids'] = len(light_solids)
        pts = [p for s in sol for p in solid_points(s)]
        c = frame_coords(pts, pt, ux, uy, uz)
        e = extents(c)
        r['envelope_in'] = {'W': e['size'][0], 'H': e['size'][1], 'D': e['size'][2],
                            'D_min_from_face': e['min'][2], 'D_max_from_face': e['max'][2]}
        r['projects_out_of_wall'] = e['max'][2] > 1.0 and e['min'][2] > -0.02
        r['solid_count'] = len(sol)

        metal_p = find_param(inst, 'Metal Finish'); glass_p = find_param(inst, 'Glass Finish')
        glass_mid = glass_p.AsElementId().Value if glass_p else None
        metal_mid = metal_p.AsElementId().Value if metal_p else None
        glass_c, back_c = [], []
        for s in sol:
            sc = frame_coords(solid_points(s), pt, ux, uy, uz)
            if glass_mid is not None and glass_mid in solid_material_ids(s):
                glass_c += sc
            if sc and max(p[2] for p in sc) <= 0.2:
                back_c += sc
        r['shade_in'] = calipers(glass_c)
        if glass_c:
            r['shade_in']['bbox'] = extents(glass_c)['size']
        be = extents(back_c)
        r['backplate_in'] = {'W': be['size'][0], 'H': be['size'][1], 'D': be['max'][2] - be['min'][2]} if be else None

        disc = inst.LookupParameter('Show Disc')
        r['show_disc_param'] = disc is not None
        if disc is not None and not disc.IsReadOnly:
            disc.Set(0); doc.Regenerate()
            c2 = frame_coords([p for s in solids_of(inst) for p in solid_points(s)], pt, ux, uy, uz)
            e2 = extents(c2)
            r['envelope_disc_off_in'] = {'W': e2['size'][0], 'H': e2['size'][1], 'D': e2['size'][2]}
            gl2 = []
            for s in solids_of(inst):
                if glass_mid is not None and glass_mid in solid_material_ids(s):
                    gl2 += frame_coords(solid_points(s), pt, ux, uy, uz)
            g1, g2 = extents(glass_c), extents(gl2)
            r['shade_moved_when_disc_off_in'] = max(abs(g1['min'][i] - g2['min'][i]) + abs(g1['max'][i] - g2['max'][i]) for i in range(3)) if g1 and g2 else None
            disc.Set(1); doc.Regenerate()

        mats = {}
        for name, p in (('Metal Finish', metal_p), ('Glass Finish', glass_p)):
            row = {'found': p is not None}
            if p is not None and not p.IsReadOnly:
                old = p.AsElementId()
                mid = DB.Material.Create(doc, 'GRADER_' + name.replace(' ', '_'))
                p.Set(mid); doc.Regenerate()
                faces = [f for s in solids_of(inst) for f in s.Faces]
                row['faces_total'] = len(faces)
                row['faces_with_substitute'] = sum(1 for f in faces if f.MaterialElementId == mid)
                p.Set(old); doc.Regenerate()
            elif p is not None:
                row['read_only'] = True
            mats[name] = row
        r['materials'] = mats
        r['project_warnings'] = [w.GetDescriptionText() for w in doc.GetWarnings()]

        if light_solids and glass_c:
            # The proxy is centred on the light source, so its centroid is the source position.
            try:
                wp = light_solids[0].ComputeCentroid()
            except Exception:
                sb = light_solids[0].GetBoundingBox()  # centroid can fail on the proxy; its box is centred on the source
                wp = sb.Transform.OfPoint((sb.Min + sb.Max) * 0.5)
            lc = frame_coords([wp], pt, ux, uy, uz)[0]
            ge = extents(glass_c)
            r['light_source_in_frame'] = list(lc)
            r['light_inside_shade_bbox'] = all(ge['min'][i] <= lc[i] <= ge['max'][i] for i in range(3))
        t.Commit()

        vt = next(x for x in DB.FilteredElementCollector(doc).OfClass(DB.ViewFamilyType) if x.ViewFamily == DB.ViewFamily.ThreeDimensional)
        center = pt + n.Multiply(2.75 / FT)
        shots = {'front': (n, DB.XYZ(0, 0, 1), False), 'side': (DB.XYZ(1, 0, 0), DB.XYZ(0, 0, 1), False),
                 'oblique': ((n.Multiply(1.0) + DB.XYZ(0.8, 0, 0) + DB.XYZ(0, 0, 0.45)).Normalize(), DB.XYZ(0, 0, 1), False)}
        t2 = DB.Transaction(doc, 'views'); t2.Start()
        ids = List[DB.ElementId]()
        vnames = {}
        for key, (eye_dir, up0, keep_wall) in shots.items():
            v = DB.View3D.CreateIsometric(doc, vt.Id)
            v.Name = '%s_%s' % (label, key)
            fwd = eye_dir.Negate()
            right = fwd.CrossProduct(up0).Normalize()
            up = right.CrossProduct(fwd).Normalize()
            v.SetOrientation(DB.ViewOrientation3D(center + eye_dir.Multiply(20), up, fwd))
            bb = DB.BoundingBoxXYZ()
            m = 6.0 / FT
            fy = pt.Y
            y0, y1 = (fy - 1.0 / FT, fy + 12.0 / FT) if n.Y > 0 else (fy - 12.0 / FT, fy + 1.0 / FT)
            bb.Min = DB.XYZ(-m, y0, 5.0 - m)
            bb.Max = DB.XYZ(m, y1, 5.0 + m)
            v.SetSectionBox(bb)
            v.DetailLevel = DB.ViewDetailLevel.Fine
            try:
                v.DisplayStyle = DB.DisplayStyle.Realistic
            except Exception:
                v.DisplayStyle = DB.DisplayStyle.Shading
            if not keep_wall:
                v.SetCategoryHidden(DB.ElementId(DB.BuiltInCategory.OST_Walls), True)
            v.SetCategoryHidden(DB.ElementId(DB.BuiltInCategory.OST_SectionBox), True)
            v.SetCategoryHidden(DB.ElementId(DB.BuiltInCategory.OST_Levels), True)
            # Frame every view on the fixture itself (hosted view: with a wider margin of wall).
            # Physical solids only: the instance bounding box includes Revit's 24 in light-source proxy.
            crop = v.CropBox
            inv = crop.Transform.Inverse
            cs = [inv.OfPoint(q) for q in pts]
            pad = 0.6 if keep_wall else 0.08
            x0, x1 = min(q.X for q in cs), max(q.X for q in cs)
            y0, y1 = min(q.Y for q in cs), max(q.Y for q in cs)
            dx, dy = (x1 - x0) * pad, (y1 - y0) * pad
            crop.Min = DB.XYZ(x0 - dx, y0 - dy, crop.Min.Z)
            crop.Max = DB.XYZ(x1 + dx, y1 + dy, crop.Max.Z)
            v.CropBox = crop
            v.CropBoxActive = True
            v.CropBoxVisible = False
            ids.Add(v.Id); vnames[key] = v.Name
        t2.Commit()
        d = os.path.join(VIEWS, label)
        if not os.path.isdir(d):
            os.makedirs(d)
        o = DB.ImageExportOptions()
        o.ExportRange = DB.ExportRange.SetOfViews
        o.SetViewsAndSheets(ids)
        o.ZoomType = DB.ZoomFitType.FitToPage
        o.PixelSize = 1000
        o.ImageResolution = DB.ImageResolution.DPI_150
        o.HLRandWFViewsFileType = DB.ImageFileType.PNG
        o.ShadowViewsFileType = DB.ImageFileType.PNG
        o.FilePath = os.path.join(d, 'view')
        doc.ExportImage(o)
        r['views'] = sorted(os.listdir(d))
    except Exception:
        r['error'] = traceback.format_exc()
    finally:
        for tx in (locals().get('t2'), locals().get('t')):
            if tx is not None and tx.HasStarted() and not tx.HasEnded():
                tx.RollBack()
        doc.Close(False)
    save()


try:
    targets = json.load(open(os.path.join(HERE, 'grade_targets.json')))
    for label in sorted(targets):
        try:
            grade(label, targets[label])
        except Exception:
            report['errors'].append([label, traceback.format_exc()]); save()
except Exception:
    report['errors'].append(['main', traceback.format_exc()])
report['done'] = True
save()
