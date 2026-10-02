# -*- coding: utf-8 -*-
"""Native Revit 2025 validation of the KW1041MBK family (pyRevit, IronPython 2.7).
Reopens the saved RFA, loads it into a disposable project, hosts it on a wall, measures everything the acceptance gates ask for,
exports the hosted-on-wall view and writes work/validation_raw.json (finalised into validation.json by finalize.py)."""
import sys
import os
import math
import itertools
import traceback
RUN = 'E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce/xhigh/'
sys.path.insert(0, RUN + 'source')
from guard import dump_json, safe_path
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB
from System.Collections.Generic import List

RFA = RUN + 'Visual_Comfort_Nodes_KW1041MBK_Midnight_Black_R2025.rfa'
OUTD = RUN + 'work/export_hosted/'
rep = {}
docs = []
IN = 12.0


def inch(v):
    return v * IN


def solids_of(geo):
    for it in geo:
        if isinstance(it, DB.Solid) and it.Volume > 1e-12:
            yield it
        elif isinstance(it, DB.GeometryInstance):
            for s in solids_of(it.GetInstanceGeometry()):
                yield s


class Ext(object):
    def __init__(self):
        self.lo = [1e9, 1e9, 1e9]
        self.hi = [-1e9, -1e9, -1e9]

    def add(self, p):
        for k, c in enumerate((p.X, p.Y, p.Z)):
            if c < self.lo[k]:
                self.lo[k] = c
            if c > self.hi[k]:
                self.hi[k] = c

    def out(self, origin):
        if self.lo[0] > 1e8:
            return None
        return {'lo_in': [inch(self.lo[k] - origin[k]) for k in range(3)], 'hi_in': [inch(self.hi[k] - origin[k]) for k in range(3)],
                'size_in': [inch(self.hi[k] - self.lo[k]) for k in range(3)]}


def extents(solids, origin):
    t = Ext()
    b = Ext()
    e = Ext()
    for s in solids:
        for f in s.Faces:
            for v in f.Triangulate(1.0).Vertices:
                t.add(v)
        bb = s.GetBoundingBox()
        for cx, cy, cz in itertools.product((bb.Min.X, bb.Max.X), (bb.Min.Y, bb.Max.Y), (bb.Min.Z, bb.Max.Z)):
            b.add(bb.Transform.OfPoint(DB.XYZ(cx, cy, cz)))
        for edge in s.Edges:
            c = edge.AsCurve()
            if isinstance(c, DB.Line):
                e.add(c.GetEndPoint(0))
                e.add(c.GetEndPoint(1))
            else:
                for i in range(0, 721):
                    e.add(c.Evaluate(i / 720.0, True))
    return {'tessellated_lod1': t.out(origin), 'solid_bbox': b.out(origin), 'edge_sampled': e.out(origin)}


def classify(doc, inst, opts, volumes_in3):
    parts = {}
    diag = []
    for s in solids_of(inst.get_Geometry(opts)):
        name = None
        gs = doc.GetElement(s.GraphicsStyleId) if s.GraphicsStyleId.Value > 0 else None
        if gs is not None and gs.GraphicsStyleCategory is not None:
            name = gs.GraphicsStyleCategory.Name
        if name in (None, 'Lighting Fixtures'):
            v = s.Volume * 1728.0
            best = min(volumes_in3.items(), key=lambda kv: abs(kv[1] - v))
            name = best[0] if abs(best[1] - v) < 0.02 * best[1] else 'unknown'
            diag.append(['volume_fallback', name, v])
        parts.setdefault(name, []).append(s)
    return parts, diag


def part_sizes(parts, origin):
    return dict((n, extents(ss, origin)) for n, ss in parts.items())


def face_counts(doc, parts):
    out = {}
    for n, ss in parts.items():
        d = {}
        for s in ss:
            for f in s.Faces:
                m = f.MaterialElementId
                nm = doc.GetElement(m).Name if m.Value > 0 else 'none'
                d[nm] = d.get(nm, 0) + 1
        out[n] = {'faces': sum(d.values()), 'by_material': d}
    return out


def ename(e):
    return DB.Element.Name.GetValue(e)


def vec(v):
    return [v.X, v.Y, v.Z]


try:
    app = __revit__.Application
    build = None
    try:
        import json
        f = open(RUN + 'work/build_report.json')
        build = json.loads(f.read())
        f.close()
    except Exception:
        build = None
    theta = math.radians(build['design']['theta_deg'])
    volumes = dict((n, p['volume_in3']) for n, p in build['parts'].items())
    volumes['Light Source'] = 0.0
    fdoc = app.OpenDocumentFile(RFA)
    docs.append(fdoc)
    fm = fdoc.FamilyManager
    rep['family_doc'] = {'path': RFA, 'size_bytes': os.path.getsize(RFA), 'category': fdoc.OwnerFamily.FamilyCategory.Name,
                         'placement_type': str(fdoc.OwnerFamily.FamilyPlacementType), 'warnings': [w.GetDescriptionText() for w in fdoc.GetWarnings()],
                         'types': [t.Name for t in fm.Types], 'current_type': fm.CurrentType.Name,
                         'parameters': dict((q.Definition.Name, {'instance': q.IsInstance, 'storage': str(q.StorageType)}) for q in fm.Parameters
                                            if q.Definition.Name in ('Metal Finish', 'Glass Finish', 'Show Disc', 'Lamp', 'Wattage Comments', 'Apparent Power',
                                                                     'Manufacturer', 'Model', 'Description', 'Light Source Symbol Size'))}
    ct = fm.CurrentType
    ident = {}
    for bip in (DB.BuiltInParameter.ALL_MODEL_MANUFACTURER, DB.BuiltInParameter.ALL_MODEL_MODEL, DB.BuiltInParameter.ALL_MODEL_DESCRIPTION):
        q = fm.get_Parameter(bip)
        ident[str(bip)] = ct.AsString(q) if q is not None else None
    for q in fm.Parameters:
        if q.Definition.Name in ('Lamp', 'Wattage Comments'):
            ident[q.Definition.Name] = ct.AsString(q)
        if q.Definition.Name == 'Apparent Power':
            ident[q.Definition.Name] = ct.AsValueString(q)
        if q.Definition.Name in ('Metal Finish', 'Glass Finish'):
            mid = ct.AsElementId(q)
            ident[q.Definition.Name] = fdoc.GetElement(mid).Name if mid.Value > 0 else None
        if q.Definition.Name == 'Show Disc':
            ident['Show Disc (default)'] = ct.AsInteger(q)
    rep['family_doc']['identity_and_defaults'] = ident
    mats = {}
    for m in DB.FilteredElementCollector(fdoc).OfClass(DB.Material):
        if m.Name.startswith('KW1041'):
            e = {'class': m.MaterialClass, 'shading_rgb': [m.Color.Red, m.Color.Green, m.Color.Blue]}
            aa = fdoc.GetElement(m.AppearanceAssetId) if m.AppearanceAssetId.Value > 0 else None
            if aa is not None:
                asset = aa.GetRenderingAsset()
                for key in ('generic_diffuse',):
                    p = asset.FindByName(key)
                    if p is not None:
                        c = p.GetValueAsColor()
                        e['appearance_diffuse_rgb'] = [c.Red, c.Green, c.Blue]
                for key in ('generic_glossiness', 'generic_reflectivity_at_0deg'):
                    p = asset.FindByName(key)
                    if p is not None:
                        e['appearance_' + key] = p.Value
            mats[m.Name] = e
    rep['family_doc']['materials'] = mats
    lf = DB.Lighting.LightFamily.GetLightFamily(fdoc)
    lt = lf.GetLightType(0)
    o = lf.GetLightSourceTransform().Origin
    srcs = list(DB.FilteredElementCollector(fdoc).OfCategory(DB.BuiltInCategory.OST_LightingFixtureSource))
    bb = srcs[0].get_BoundingBox(None)
    rep['family_doc']['light'] = {'source_elements': len(srcs), 'shape': str(lf.GetLightShapeStyle()), 'distribution': str(lf.GetLightDistributionStyle()),
                                  'flux_lm': lt.GetInitialIntensity().InitialIntensityValue, 'cct_K': lt.GetInitialColor().TemperatureValue,
                                  'loss_factor': lt.GetLossFactor().LossFactorValue,
                                  'source_origin_in': [inch(o.X), inch(o.Y), inch(o.Z)],
                                  'source_bbox_centre_in': [inch((bb.Min.X + bb.Max.X) / 2), inch((bb.Min.Y + bb.Max.Y) / 2), inch((bb.Min.Z + bb.Max.Z) / 2)]}
    dim = {}
    for ff in DB.FilteredElementCollector(fdoc).OfClass(DB.FreeFormElement):
        cat = ff.Subcategory.Name if ff.Subcategory is not None else None
        mp = ff.get_Parameter(DB.BuiltInParameter.MATERIAL_ID_PARAM)
        vp = ff.get_Parameter(DB.BuiltInParameter.IS_VISIBLE_PARAM)
        dim[cat] = {}
        try:
            assoc = fm.GetAssociatedFamilyParameter(mp)
            dim[cat]['material_bound_to'] = assoc.Definition.Name if assoc is not None else None
            assoc2 = fm.GetAssociatedFamilyParameter(vp)
            dim[cat]['visibility_bound_to'] = assoc2.Definition.Name if assoc2 is not None else None
        except Exception:
            dim[cat]['assoc_err'] = traceback.format_exc().strip().split('\n')[-1][:150]
    rep['family_doc']['part_bindings'] = dim
    dump_json(rep, RUN + 'work/validation_raw.json')

    project = app.NewProjectDocument(DB.UnitSystem.Imperial)
    docs.append(project)
    fam = fdoc.LoadFamily(project)
    symbol = project.GetElement(list(fam.GetFamilySymbolIds())[0])
    rep['project_symbol'] = {'family': ename(fam), 'type': ename(symbol), 'family_category': fam.FamilyCategory.Name}
    tx = DB.Transaction(project, 'place')
    tx.Start()
    level = next(iter(DB.FilteredElementCollector(project).OfClass(DB.Level)))
    wt = next(w for w in DB.FilteredElementCollector(project).OfClass(DB.WallType) if w.Kind == DB.WallKind.Basic)
    wall = DB.Wall.Create(project, DB.Line.CreateBound(DB.XYZ(-8, 0, 0), DB.XYZ(8, 0, 0)), wt.Id, level.Id, 10, 0, False, False)
    symbol.Activate()
    project.Regenerate()
    ref = DB.HostObjectUtils.GetSideFaces(wall, DB.ShellLayerType.Exterior)[0]
    face = wall.GetGeometryObjectFromReference(ref)
    normal = face.FaceNormal
    up = DB.XYZ.BasisZ
    upright_dir = up.CrossProduct(normal)
    rep['wall'] = {'exterior_face_normal': vec(normal), 'wall_orientation': vec(wall.Orientation), 'wall_type': ename(wt),
                   'upright_reference_direction': vec(upright_dir)}
    ptA = face.Project(DB.XYZ(0, 0, 5)).XYZPoint
    ptB = face.Project(DB.XYZ(5, 0, 5)).XYZPoint
    instA = project.Create.NewFamilyInstance(ref, ptA, upright_dir, symbol)
    instB = project.Create.NewFamilyInstance(ref, ptB, DB.XYZ.BasisX, symbol)
    project.Regenerate()
    pmats = {}
    for m in DB.FilteredElementCollector(project).OfClass(DB.Material):
        if m.Name.startswith('KW1041'):
            pmats[m.Name] = {'shading_rgb': [m.Color.Red, m.Color.Green, m.Color.Blue], 'use_render_appearance_for_shading': m.UseRenderAppearanceForShading,
                             'transparency': m.Transparency, 'appearance_asset_valid': m.AppearanceAssetId.Value > 0}
    rep['project_materials'] = pmats
    opts = DB.Options()
    opts.DetailLevel = DB.ViewDetailLevel.Fine
    opts.ComputeReferences = False
    originA = (ptA.X, ptA.Y, ptA.Z)
    originB = (ptB.X, ptB.Y, ptB.Z)
    rep['placement'] = {}
    for tag, inst, origin in (('upright_ref_dir_up_x_normal', instA, originA), ('reference_dir_plus_x', instB, originB)):
        tr = inst.GetTransform()
        host = inst.Host
        e = {'host_is_wall': host is not None and host.Id == wall.Id, 'host_face_reference_present': inst.HostFace is not None,
             'facing_orientation': vec(inst.FacingOrientation), 'transform_basis': {'X': vec(tr.BasisX), 'Y': vec(tr.BasisY), 'Z': vec(tr.BasisZ)},
             'origin_ft': vec(tr.Origin), 'face_point_ft': list(origin),
             'placement_type_of_symbol': str(fam.FamilyPlacementType if hasattr(fam, 'FamilyPlacementType') else None)}
        e['show_disc_instance_param'] = inst.LookupParameter('Show Disc').AsInteger()
        e['metal_finish_is_type_param_on_instance'] = inst.LookupParameter('Metal Finish') is not None and inst.LookupParameter('Metal Finish').Element.Id != symbol.Id
        rep['placement'][tag] = e
    parts, diag = classify(project, instA, opts, volumes)
    rep['classification_diag'] = diag
    rep['envelope_disc_on'] = extents([s for ss in parts.values() for s in ss], originA)
    rep['envelope_disc_on_excluding_light_source'] = extents([s for n, ss in parts.items() if n != 'Light Source' for s in ss], originA)
    rep['part_extents_disc_on'] = part_sizes(parts, originA)
    ibb = instA.get_BoundingBox(None)
    rep['instance_bbox_get_BoundingBox'] = {'lo_in': [inch(ibb.Min.X - originA[0]), inch(ibb.Min.Y - originA[1]), inch(ibb.Min.Z - originA[2])],
                                            'hi_in': [inch(ibb.Max.X - originA[0]), inch(ibb.Max.Y - originA[1]), inch(ibb.Max.Z - originA[2])]}
    rep['part_face_counts_default'] = face_counts(project, parts)
    rep['part_solid_counts'] = dict((n, len(ss)) for n, ss in parts.items())
    dump_json(rep, RUN + 'work/validation_raw.json')

    # analytic part sizes: backplate diameter, shade max diameter and axial height
    tr = instA.GetTransform()
    axis = tr.OfVector(DB.XYZ(0, -math.sin(theta), math.cos(theta))).Normalize()
    ps = {}
    plate_arcs = [edge.AsCurve() for s in parts['Backplate'] for edge in s.Edges if isinstance(edge.AsCurve(), DB.Arc)]
    ps['backplate_arc_diameters_in'] = sorted(set(round(inch(2 * a.Radius), 4) for a in plate_arcs))
    shade = parts['Shade']
    sh_arcs = [edge.AsCurve() for s in shade for edge in s.Edges if isinstance(edge.AsCurve(), DB.Arc)]
    ps['shade_arc_radii_in'] = sorted(set(round(inch(a.Radius), 4) for a in sh_arcs))
    base_face = None
    for s_ in shade:
        for f in s_.Faces:
            if isinstance(f, DB.PlanarFace) and f.FaceNormal.DotProduct(axis) < -0.99:
                base_face = f
    ps['shade_base_face_normal_dot_minus_axis'] = -base_face.FaceNormal.DotProduct(axis) if base_face is not None else None
    ps['shade_face_types'] = [type(f).__name__ for s_ in shade for f in s_.Faces]
    if base_face is not None:
        bo = base_face.Origin
        big_arc = max([a for a in sh_arcs if abs(a.Normal.DotProduct(axis)) > 0.99], key=lambda a: a.Radius)
        bc = big_arc.Center
        ps['shade_base_ring_center_offset_from_face_origin_in'] = inch(bc.DistanceTo(bo))
        fits = []
        for s_ in shade:
            for f in s_.Faces:
                if isinstance(f, DB.RevolvedFace):
                    xs_ = []
                    ys_ = []
                    for v in f.Triangulate(1.0).Vertices:
                        w = v.Subtract(bc)
                        a_ = w.DotProduct(axis)
                        r2 = w.Subtract(axis.Multiply(a_)).GetLength() ** 2
                        xs_.append(a_)
                        ys_.append(r2 + a_ * a_)
                    n_ = float(len(xs_))
                    mx = sum(xs_) / n_
                    my = sum(ys_) / n_
                    sxx = sum((x - mx) ** 2 for x in xs_)
                    sxy = sum((x - mx) * (y - my) for x, y in zip(xs_, ys_))
                    m_ = sxy / sxx
                    t_ = m_ / 2.0
                    k_ = my - m_ * mx
                    rr = math.sqrt(k_ + t_ * t_)
                    resl = sorted(abs(math.sqrt(y - 2 * t_ * x + t_ * t_) - rr) for x, y in zip(xs_, ys_))
                    res = resl[-1]
                    fits.append({'n_vertices': int(n_), 'radius_in': inch(rr), 'centre_along_axis_from_base_in': inch(t_),
                                 'apex_along_axis_from_base_in': inch(t_ + rr), 'max_residual_in': inch(res), 'median_residual_in': inch(resl[len(resl) // 2])})
        ps['shade_sphere_fits'] = fits
        if fits:
            outer_fit = max(fits, key=lambda q: q['radius_in'])
            ps['shade_max_diameter_analytic_in'] = 2 * outer_fit['radius_in']
            ps['shade_axial_height_analytic_in'] = outer_fit['apex_along_axis_from_base_in']
        vmax = -1e9
        vmin = 1e9
        rmax = 0.0
        for s in shade:
            for f in s.Faces:
                for v in f.Triangulate(1.0).Vertices:
                    a = v.Subtract(bo).DotProduct(axis)
                    vmax = max(vmax, a)
                    vmin = min(vmin, a)
                    rad = v.Subtract(bo).Subtract(axis.Multiply(a)).GetLength()
                    rmax = max(rmax, rad)
        ps['shade_axial_height_tessellated_in'] = inch(vmax - vmin)
        ps['shade_max_diameter_tessellated_in'] = inch(2 * rmax)
        base_arcs = [a for a in sh_arcs if abs(a.Normal.DotProduct(axis)) > 0.99]
        ps['shade_base_circle_diameters_in'] = sorted(set(round(inch(2 * a.Radius), 4) for a in base_arcs))
        ps['shade_axis_world'] = vec(axis)
    disc_arcs = [edge.AsCurve() for s in parts['Disc'] for edge in s.Edges if isinstance(edge.AsCurve(), DB.Arc)]
    ps['disc_circle_diameters_in'] = sorted(set(round(inch(2 * a.Radius), 4) for a in disc_arcs))
    body_arcs = [edge.AsCurve() for s in parts['Body'] for edge in s.Edges if isinstance(edge.AsCurve(), DB.Arc)]
    ps['body_arc_diameters_in'] = sorted(set(round(inch(2 * a.Radius), 4) for a in body_arcs))
    sock_arcs = [edge.AsCurve() for s in parts['Socket'] for edge in s.Edges if isinstance(edge.AsCurve(), DB.Arc)]
    ps['socket_arc_diameters_in'] = sorted(set(round(inch(2 * a.Radius), 4) for a in sock_arcs))
    rep['analytic_part_sizes'] = ps

    # light source position relative to the shade, in family coordinates
    inv = tr.Inverse
    ls = parts.get('Light Source', [])
    if ls:
        le = Ext()
        for s in ls:
            bb2 = s.GetBoundingBox()
            for cx, cy, cz in itertools.product((bb2.Min.X, bb2.Max.X), (bb2.Min.Y, bb2.Max.Y), (bb2.Min.Z, bb2.Max.Z)):
                le.add(bb2.Transform.OfPoint(DB.XYZ(cx, cy, cz)))
        cw = DB.XYZ((le.lo[0] + le.hi[0]) / 2, (le.lo[1] + le.hi[1]) / 2, (le.lo[2] + le.hi[2]) / 2)
        cf = inv.OfPoint(cw)
        rep['light_in_instance'] = {'symbol_solid_centre_family_in': [inch(cf.X), inch(cf.Y), inch(cf.Z)]}
    N_fam = (0.0, -math.sin(theta), math.cos(theta))
    base_c = (0.0, 0.0, build['design']['zc_in'])
    sphere_c = [base_c[i] + N_fam[i] * build['design']['sphere_centre_offset_along_axis_in'] for i in range(3)]
    rep['light_in_instance']['shade_sphere_centre_family_in'] = sphere_c
    dist = math.sqrt(sum((rep['light_in_instance']['symbol_solid_centre_family_in'][i] - sphere_c[i]) ** 2 for i in range(3)))
    rep['light_in_instance']['distance_from_sphere_centre_in'] = dist
    rep['light_in_instance']['inner_glass_radius_in'] = 1.75 - 0.10
    rep['light_in_instance']['inside_shade_cavity'] = dist + 0.36 < 1.65
    dump_json(rep, RUN + 'work/validation_raw.json')

    # Show Disc off
    p = instA.LookupParameter('Show Disc')
    p.Set(0)
    project.Regenerate()
    parts_off, _ = classify(project, instA, opts, volumes)
    rep['envelope_disc_off'] = extents([s for ss in parts_off.values() for s in ss], originA)
    rep['envelope_disc_off_excluding_light_source'] = extents([s for n, ss in parts_off.items() if n != 'Light Source' for s in ss], originA)
    rep['part_extents_disc_off'] = part_sizes(parts_off, originA)
    rep['parts_present_disc_off'] = sorted(parts_off.keys())
    p.Set(1)
    project.Regenerate()

    # material substitution through the type parameters
    alt_m = DB.Material.Create(project, 'ZZ Test Metal')
    alt_g = DB.Material.Create(project, 'ZZ Test Glass')
    swaps = {}
    originals = {}
    for tag, param, alt in (('metal', 'Metal Finish', alt_m), ('glass', 'Glass Finish', alt_g)):
        q = symbol.LookupParameter(param)
        originals[param] = q.AsElementId()
        swaps[tag + '_param_set_ok'] = q.Set(alt)
        project.Regenerate()
        pp, _ = classify(project, instA, opts, volumes)
        swaps[tag + '_swapped'] = face_counts(project, pp)
    for param, oid in originals.items():
        symbol.LookupParameter(param).Set(oid)
    project.Regenerate()
    pp, _ = classify(project, instA, opts, volumes)
    swaps['restored_after_swaps'] = face_counts(project, pp)
    swaps['restored_type_params'] = dict((param, project.GetElement(symbol.LookupParameter(param).AsElementId()).Name) for param in originals)
    rep['material_swaps'] = swaps
    tx.Commit()
    rep['project_warnings'] = [w.GetDescriptionText() for w in project.GetWarnings()]
    dump_json(rep, RUN + 'work/validation_raw.json')

    # hosted-on-wall views (from the exterior side, left-front three-quarter like the black product photo)
    tx = DB.Transaction(project, 'view')
    tx.Start()
    vtype = next(v for v in DB.FilteredElementCollector(project).OfClass(DB.ViewFamilyType) if v.ViewFamily == DB.ViewFamily.ThreeDimensional)
    keep = (DB.BuiltInCategory.OST_Walls, DB.BuiltInCategory.OST_LightingFixtures)
    keep_ids = [DB.Category.GetCategory(project, k).Id.Value for k in keep]
    left = normal.CrossProduct(DB.XYZ.BasisZ)
    tgt = DB.XYZ(ptA.X, ptA.Y + 3.5 / 12.0, ptA.Z)
    variants = [('Hosted on wall', DB.DisplayStyle.Shading, True, (45.2, 38.0, 10.4)),
                ('Hosted on wall - side', DB.DisplayStyle.Shading, True, (0.0, 60.0, 0.0)),
                ('Hosted on wall - front', DB.DisplayStyle.Shading, True, (60.0, 0.0, 0.0))]
    vids = []
    for vname, vstyle, vsec, voff in variants:
        eye = tgt.Add(normal.Multiply(voff[0] / 12.0)).Add(left.Multiply(voff[1] / 12.0)).Add(DB.XYZ.BasisZ.Multiply(voff[2] / 12.0))
        fwd = tgt.Subtract(eye).Normalize()
        right = fwd.CrossProduct(DB.XYZ.BasisZ).Normalize()
        if abs(fwd.Z) > 0.99:
            right = DB.XYZ.BasisX
        view = DB.View3D.CreateIsometric(project, vtype.Id)
        view.Name = vname
        view.SetOrientation(DB.ViewOrientation3D(eye, right.CrossProduct(fwd).Normalize(), fwd))
        view.DetailLevel = DB.ViewDetailLevel.Fine
        view.DisplayStyle = vstyle
        for cat in project.Settings.Categories:
            if cat.Id.Value not in keep_ids and view.CanCategoryBeHidden(cat.Id):
                view.SetCategoryHidden(cat.Id, True)
        if vsec:
            region = DB.BoundingBoxXYZ()
            region.Min = DB.XYZ(ptA.X - 14.0 / 12.0, ptA.Y - 4.0 / 12.0, ptA.Z - 12.0 / 12.0)
            region.Max = DB.XYZ(ptA.X + 14.0 / 12.0, ptA.Y + 8.0 / 12.0, ptA.Z + 12.0 / 12.0)
            view.SetSectionBox(region)
            view.IsSectionBoxActive = True
        project.Regenerate()
        view.CropBoxActive = True
        view.CropBoxVisible = False
        cb = view.CropBox
        inv2 = cb.Transform.Inverse
        xs = []
        ys = []
        for cx, cy, cz in itertools.product((ptA.X - 5.0 / 12.0, ptA.X + 5.0 / 12.0), (ptA.Y - 4.0 / 12.0, ptA.Y + 6.0 / 12.0), (ptA.Z - 4.5 / 12.0, ptA.Z + 4.5 / 12.0)):
            q = inv2.OfPoint(DB.XYZ(cx, cy, cz))
            xs.append(q.X)
            ys.append(q.Y)
        pad = 2.0 / 12.0
        cb.Min = DB.XYZ(min(xs) - pad, min(ys) - pad, cb.Min.Z)
        cb.Max = DB.XYZ(max(xs) + pad, max(ys) + pad, cb.Max.Z)
        view.CropBox = cb
        vids.append(view.Id)
    tx.Commit()
    if not os.path.isdir(OUTD):
        os.makedirs(OUTD)
    safe_path(OUTD + 'x')
    eo = DB.ImageExportOptions()
    eo.ExportRange = DB.ExportRange.SetOfViews
    eo.SetViewsAndSheets(List[DB.ElementId](vids))
    eo.FilePath = OUTD + 'hosted'
    eo.HLRandWFViewsFileType = DB.ImageFileType.PNG
    eo.ShadowViewsFileType = DB.ImageFileType.PNG
    eo.ImageResolution = DB.ImageResolution.DPI_150
    eo.ZoomType = DB.ZoomFitType.FitToPage
    eo.PixelSize = 1200
    project.ExportImage(eo)
    rep['hosted_exports'] = sorted(os.listdir(OUTD))
    rep['project_warnings_after_view'] = [w.GetDescriptionText() for w in project.GetWarnings()]
except Exception:
    rep['error'] = traceback.format_exc()
finally:
    rep['done'] = True
    dump_json(rep, RUN + 'work/validation_raw.json')
    for d in reversed(docs):
        try:
            d.Close(False)
        except Exception:
            pass
