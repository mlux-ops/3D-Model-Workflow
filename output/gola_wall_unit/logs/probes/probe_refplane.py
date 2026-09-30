# -*- coding: utf-8 -*-
"""Where does NewReferencePlane2(p0, p1, p0+u, view) put the plane relative to the Gola's location line?"""
import json, traceback, clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB
RUN = 'E:/Claude/3D-Model-Workflow/output/gola_wall_unit'
out = {'cases': []}


def save():
    with open(RUN + '/logs/probe_refplane.json', 'w') as f: json.dump(out, f, indent=2, default=str)


def mm(v): return v / 304.8
def v3(p): return [round(x * 304.8, 4) for x in (p.X, p.Y, p.Z)]


try:
    app = __revit__.Application
    doc = app.NewProjectDocument(DB.UnitSystem.Metric)
    t = DB.Transaction(doc, 'p'); t.Start()
    syms = {}
    for k, p in (('gola', RUN + '/Richelieu_Gola_Wall_Unit_Upper_Cabinet_2025.rfa'), ('box', RUN + '/test_families/Test_Cabinet_Box_cuttable.rfa')):
        r = clr.Reference[DB.Family]()
        doc.LoadFamily(p, r); syms[k] = doc.GetElement(list(r.Value.GetFamilySymbolIds())[0]); syms[k].Activate()
    level = DB.FilteredElementCollector(doc).OfClass(DB.Level).FirstElement()
    box = doc.Create.NewFamilyInstance(DB.XYZ.Zero, syms['box'], level, DB.Structure.StructuralType.NonStructural)
    doc.Regenerate()
    o = DB.Options(); o.ComputeReferences = True
    ref = None
    for g in box.get_Geometry(o):
        if isinstance(g, DB.GeometryInstance):
            for s in g.GetSymbolGeometry():
                if isinstance(s, DB.Solid):
                    for f in s.Faces:
                        if isinstance(f, DB.PlanarFace) and g.Transform.OfVector(f.FaceNormal).Y < -0.99: ref = f.Reference
    gi = doc.Create.NewFamilyInstance(ref, DB.Line.CreateBound(DB.XYZ(mm(250), 0, mm(-700)), DB.XYZ(mm(1750), 0, mm(-700))), syms['gola'])
    doc.Regenerate()
    c = gi.Location.Curve; p0, p1 = c.GetEndPoint(0), c.GetEndPoint(1)
    tr = gi.GetTransform()
    out['location'] = [v3(p0), v3(p1)]
    wp = gi.get_Parameter(DB.BuiltInParameter.SKETCH_PLANE_PARAM)
    out['face_hosted_work_plane_param'] = wp.AsString() if wp else None
    out['face_hosted_host'] = '%s %s' % (gi.Host.GetType().Name, DB.Element.Name.GetValue(gi.Host)) if gi.Host else None
    out['box_family_type'] = '%s : %s' % (box.Symbol.Family.Name, DB.Element.Name.GetValue(box.Symbol))
    hp = gi.get_Parameter(DB.BuiltInParameter.INSTANCE_FREE_HOST_PARAM)
    out['host_param'] = hp.AsString() if hp else None
    save(); t.RollBack(); doc.Close(False); raise SystemExit
    out['transform'] = {'origin': v3(tr.Origin), 'x': [tr.BasisX.X, tr.BasisX.Y, tr.BasisX.Z], 'y': [tr.BasisY.X, tr.BasisY.Y, tr.BasisY.Z], 'z': [tr.BasisZ.X, tr.BasisZ.Y, tr.BasisZ.Z]}
    vt = next(x for x in DB.FilteredElementCollector(doc).OfClass(DB.ViewFamilyType) if x.ViewFamily == DB.ViewFamily.ThreeDimensional)
    views = {'3d': DB.View3D.CreateIsometric(doc, vt.Id)}
    views['plan'] = next(v for v in DB.FilteredElementCollector(doc).OfClass(DB.ViewPlan) if not v.IsTemplate)
    n = tr.BasisZ; d = p1.Subtract(p0).Normalize(); u = n.CrossProduct(d)
    E = mm(300)
    variants = {
        'edge_on_line': (p0, p1, p0.Add(u)),
        'extended_along_run': (p0.Subtract(d.Multiply(E)), p1.Add(d.Multiply(E)), p0.Add(u)),
        'offset_plus_u': (p0.Subtract(d.Multiply(E)).Add(u.Multiply(E)), p1.Add(d.Multiply(E)).Add(u.Multiply(E)), p0),
        'offset_minus_u': (p0.Subtract(d.Multiply(E)).Subtract(u.Multiply(E)), p1.Add(d.Multiply(E)).Subtract(u.Multiply(E)), p0),
    }
    for vname, view in views.items():
        for label, (b0, b1, b2) in variants.items():
            sub = DB.SubTransaction(doc); sub.Start()
            row = {'view': vname, 'variant': label}
            try:
                rp = doc.Create.NewReferencePlane2(b0, b1, b2, view)
                pl = rp.GetPlane()
                row['rp_normal'] = [round(pl.Normal.X, 6), round(pl.Normal.Y, 6), round(pl.Normal.Z, 6)]
                row['dist_mm'] = [abs(q.Subtract(pl.Origin).DotProduct(pl.Normal)) * 304.8 for q in (p0, p1)]
                try:
                    ni = doc.Create.NewFamilyInstance(rp.GetReference(), DB.Line.CreateBound(p0, p1), syms['gola'])
                    doc.Regenerate()
                    row['place'] = 'ok host %s' % (ni.Host.GetType().Name if ni.Host else None)
                    row['new_transform_z'] = [round(ni.GetTransform().BasisZ.X, 6), round(ni.GetTransform().BasisZ.Y, 6), round(ni.GetTransform().BasisZ.Z, 6)]
                    bb = ni.get_BoundingBox(None); row['new_bbox'] = v3(bb.Min) + v3(bb.Max)
                except Exception as ex:
                    row['place'] = 'FAIL ' + str(ex)
            except Exception as ex:
                row['error'] = str(ex)
            sub.RollBack()
            out['cases'].append(row); save()
    bb = gi.get_BoundingBox(None); out['orig_bbox'] = v3(bb.Min) + v3(bb.Max)
    t.RollBack(); doc.Close(False); save()
except Exception:
    out['error'] = traceback.format_exc(); save(); raise
