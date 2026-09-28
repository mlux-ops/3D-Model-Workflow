# -*- coding: utf-8 -*-
"""Extract single-type line-based Gola families from the combined four-type family.

Run with: pyrevit run "<abs path>/extract_types.py" --revit=2025
Source: source/Richelieu_Gola_Channel_Profiles_2025.rfa (Gola_Cutting_Recess_R2025_Package, with recess void).
Keeps the target type, its solids (visibility driven by 'Type XX' or 'XX ...' parameters) and the recess void;
deletes every other type and its solids. Verified by placing combined and extracted families on the same line.
"""
import os, json, traceback, clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB

RUN = 'E:/Claude/3D-Model-Workflow/output/gola_setback2'
SRC = RUN + '/source/Richelieu_Gola_Channel_Profiles_2025.rfa'
JOBS = [('HC', 'Horizontal - C - Double Grip', 'Richelieu_Gola_C_Channel_Horizontal_2025.rfa'),
        ('VS', 'Vertical - Single Grip', 'Richelieu_Gola_Vertical_Single_Grip_2025.rfa')]
KEYS = ('HC', 'HL', 'VS', 'VD')
report = {'stage': 'start', 'source': SRC, 'jobs': []}


def out_path(*parts):
    p = os.path.normpath(os.path.join(RUN, *parts))
    if not p.lower().startswith(os.path.normpath(RUN).lower() + os.sep): raise ValueError('outside run dir: ' + p)
    return p


def check(stage):
    report['stage'] = stage
    with open(out_path('validation_extract.json'), 'w') as f: json.dump(report, f, indent=2, default=str)


def mm(v): return v / 304.8


def form_key(doc, e):
    """Which profile type a form belongs to, from the parameter driving its visibility; None for shared forms."""
    p = e.get_Parameter(DB.BuiltInParameter.IS_VISIBLE_PARAM)
    fp = doc.FamilyManager.GetAssociatedFamilyParameter(p) if p is not None else None
    if fp is None: return None
    n = fp.Definition.Name
    for k in KEYS:
        if n == 'Type ' + k or n.startswith(k + ' '): return k
    raise ValueError('Form %d visibility driven by unrecognised parameter %s' % (e.Id.Value, n))


def solids(geom):
    for g in geom:
        if isinstance(g, DB.Solid) and g.Volume > 1e-12: yield g
        elif isinstance(g, DB.GeometryInstance):
            for s in solids(g.GetInstanceGeometry()): yield s


def ext_vol(inst):
    ss = list(solids(inst.get_Geometry(DB.Options())))
    ps = [p for s in ss for ed in s.Edges for p in ed.Tessellate()]
    return (sum(s.Volume for s in ss) * 304.8 ** 3,
            [round(v * 304.8, 4) for v in (min(p.X for p in ps), min(p.Y for p in ps), min(p.Z for p in ps),
                                           max(p.X for p in ps), max(p.Y for p in ps), max(p.Z for p in ps))])


try:
    app = __revit__.Application
    for key, tname, dst in JOBS:
        job = {'key': key, 'type': tname, 'rfa': out_path(dst)}; report['jobs'].append(job)
        check('extract ' + key)
        doc = app.OpenDocumentFile(SRC)
        fm = doc.FamilyManager
        tx = DB.Transaction(doc, 'Extract ' + key); tx.Start()
        forms = list(DB.FilteredElementCollector(doc).OfClass(DB.GenericForm))
        drop = [e.Id for e in forms if form_key(doc, e) not in (None, key)]
        kept = [e for e in forms if form_key(doc, e) in (None, key)]
        job['forms_kept'] = [[e.Id.Value, 'solid' if e.IsSolid else 'void', e.Subcategory.Name if e.Subcategory else None] for e in kept]
        job['forms_deleted'] = len(drop)
        for i in drop: doc.Delete(i)
        target = next(t for t in fm.Types if t.Name == tname)
        for t in [t for t in fm.Types if t.Name != tname]:
            fm.CurrentType = t; fm.DeleteCurrentType()
        fm.CurrentType = target
        doc.Regenerate()
        job['types_left'] = [t.Name for t in fm.Types]
        if tx.Commit() != DB.TransactionStatus.Committed: raise ValueError('extract %s did not commit' % key)
        so = DB.SaveAsOptions(); so.OverwriteExistingFile = True; so.MaximumBackups = 1
        doc.SaveAs(out_path(dst), so); doc.Close(False)

        check('compare ' + key)
        proj = app.NewProjectDocument(DB.UnitSystem.Metric)
        tx = DB.Transaction(proj, 'compare'); tx.Start()
        fams = []
        for path in (SRC, out_path(dst)):
            ref = clr.Reference[DB.Family]()
            if not proj.LoadFamily(path, ref): raise ValueError('did not load ' + path)
            fams.append(ref.Value)
        level = DB.FilteredElementCollector(proj).OfClass(DB.Level).FirstElement()
        line = DB.Line.CreateBound(DB.XYZ.Zero, DB.XYZ(mm(1000), 0, 0))
        res = []
        for fam in fams:
            sym = next(proj.GetElement(i) for i in fam.GetFamilySymbolIds() if DB.Element.Name.GetValue(proj.GetElement(i)) == tname)
            sym.Activate()
            inst = proj.Create.NewFamilyInstance(line, sym, level, DB.Structure.StructuralType.NonStructural)
            proj.Regenerate()
            res.append(ext_vol(inst))
        job['combined_volume_mm3'], job['combined_extents_mm'] = res[0]
        job['extracted_volume_mm3'], job['extracted_extents_mm'] = res[1]
        job['extracted_placement'] = str(fams[1].FamilyPlacementType)
        tx.RollBack(); proj.Close(False)
    check('complete')
except Exception:
    report['error'] = traceback.format_exc(); check('failed: ' + report['stage']); raise
