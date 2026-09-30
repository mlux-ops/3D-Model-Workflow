# -*- coding: utf-8 -*-
"""Which face reference of a Casework instance hosts a line-based Gola on that instance (as a UI click does)?"""
import json, traceback, clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB
RUN = 'E:/Claude/3D-Model-Workflow/output/gola_wall_unit'
out = {'cases': []}


def save():
    with open(RUN + '/logs/probe_face_refs.json', 'w') as f: json.dump(out, f, indent=2, default=str)


def mm(v): return v / 304.8


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
    refs = {}
    for g in box.get_Geometry(o):
        if isinstance(g, DB.GeometryInstance):
            tr = g.Transform
            for s in g.GetInstanceGeometry():
                if isinstance(s, DB.Solid):
                    for f in s.Faces:
                        if isinstance(f, DB.PlanarFace) and f.FaceNormal.Y < -0.99: refs['instance_geometry'] = f.Reference
            for s in g.GetSymbolGeometry():
                if isinstance(s, DB.Solid):
                    for f in s.Faces:
                        if isinstance(f, DB.PlanarFace) and tr.OfVector(f.FaceNormal).Y < -0.99:
                            refs['symbol_geometry'] = f.Reference
                            st = '%s:0:INSTANCE:%s' % (box.UniqueId, f.Reference.ConvertToStableRepresentation(doc))
                            out['stable'] = st
                            refs['stable_instance'] = DB.Reference.ParseFromStableRepresentation(doc, st)
    for name, ref in refs.items():
        for z in (-350, -700):
            row = {'ref': name, 'z_mm': z, 'ref_element': ref.ElementId.Value if ref else None,
                   'stable': ref.ConvertToStableRepresentation(doc) if ref else None}
            sub = DB.SubTransaction(doc); sub.Start()
            try:
                g = doc.Create.NewFamilyInstance(ref, DB.Line.CreateBound(DB.XYZ(mm(250), 0, mm(z)), DB.XYZ(mm(1750), 0, mm(z))), syms['gola'])
                doc.Regenerate()
                row['host'] = '%s %s' % (g.Host.GetType().Name, g.Host.Id.Value) if g.Host else None
                row['host_is_box'] = g.Host is not None and g.Host.Id == box.Id
                row['depends_on_box'] = any(i == g.Id for i in box.GetDependentElements(None))
            except Exception as ex:
                row['error'] = str(ex)
            sub.RollBack()
            out['cases'].append(row); save()
    t.RollBack(); doc.Close(False)
    save()
except Exception:
    out['error'] = traceback.format_exc(); save(); raise
