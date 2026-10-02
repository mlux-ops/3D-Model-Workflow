# -*- coding: utf-8 -*-
"""Exploration 6 (pyRevit): type vs instance material params on a placed instance, IS_VISIBLE binding, wall orientation, LightFamily/LightType setters."""
import sys
import math
import traceback
sys.path.insert(0, 'E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce/xhigh/source')
from guard import dump_json, safe_path
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB
from System.Collections.Generic import List

RUN = 'E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce/xhigh/'
TDIR = 'C:\\ProgramData\\Autodesk\\RVT 2025\\Family Templates\\English-Imperial\\'
rep = {}
docs = []


def save():
    dump_json(rep, RUN + 'work/explore6.json')


def box(doc, x0, y0, z0, x1, y1, z1):
    z = z0 / 12.0
    pts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    loop = DB.CurveLoop()
    for i in range(4):
        a = pts[i]
        b = pts[(i + 1) % 4]
        loop.Append(DB.Line.CreateBound(DB.XYZ(a[0] / 12.0, a[1] / 12.0, z), DB.XYZ(b[0] / 12.0, b[1] / 12.0, z)))
    s = DB.GeometryCreationUtilities.CreateExtrusionGeometry(List[DB.CurveLoop]([loop]), DB.XYZ.BasisZ, (z1 - z0) / 12.0)
    return DB.FreeFormElement.Create(doc, s)


def solids(geo):
    for it in geo:
        if isinstance(it, DB.Solid) and it.Volume > 1e-12:
            yield it
        elif isinstance(it, DB.GeometryInstance):
            for s in solids(it.GetInstanceGeometry()):
                yield s


def ext(inst):
    opts = DB.Options()
    lo = [1e9] * 3
    hi = [-1e9] * 3
    n = 0
    mats = []
    for s in solids(inst.get_Geometry(opts)):
        n += 1
        for f in s.Faces:
            mats.append(str(f.MaterialElementId.Value))
            m = f.Triangulate(0.05)
            for v in m.Vertices:
                for k, c in enumerate((v.X, v.Y, v.Z)):
                    lo[k] = min(lo[k], c)
                    hi[k] = max(hi[k], c)
    return {'n_solids': n, 'lo_in': [round(c * 12, 4) for c in lo], 'hi_in': [round(c * 12, 4) for c in hi], 'mats': sorted(set(mats))}


try:
    app = __revit__.Application
    doc = app.NewFamilyDocument(TDIR + 'Generic Model face based.rft')
    docs.append(doc)
    tx = DB.Transaction(doc, 'build')
    tx.Start()
    doc.OwnerFamily.FamilyCategory = DB.Category.GetCategory(doc, DB.BuiltInCategory.OST_LightingFixtures)
    doc.OwnerFamily.get_Parameter(DB.BuiltInParameter.FAMILY_ALWAYS_VERTICAL).Set(0)
    fm = doc.FamilyManager
    fm.NewType('T1')
    m1 = doc.GetElement(DB.Material.Create(doc, 'M1'))
    m2 = doc.GetElement(DB.Material.Create(doc, 'M2'))
    tp = fm.AddParameter('TP', DB.GroupTypeId.Materials, DB.SpecTypeId.Reference.Material, False)
    ip = fm.AddParameter('IP', DB.GroupTypeId.Materials, DB.SpecTypeId.Reference.Material, True)
    vis = fm.AddParameter('Vis', DB.GroupTypeId.Graphics, DB.SpecTypeId.Boolean.YesNo, True)
    fm.Set(tp, m1.Id)
    fm.Set(ip, m2.Id)
    fm.Set(vis, 1)
    a = box(doc, -1, 0, 0, 1, 4, 1)
    b = box(doc, -1, 0, 1, 1, 6, 2)
    doc.FamilyManager.AssociateElementParameterToFamilyParameter(a.get_Parameter(DB.BuiltInParameter.MATERIAL_ID_PARAM), tp)
    doc.FamilyManager.AssociateElementParameterToFamilyParameter(b.get_Parameter(DB.BuiltInParameter.MATERIAL_ID_PARAM), ip)
    vp = b.get_Parameter(DB.BuiltInParameter.IS_VISIBLE_PARAM)
    doc.FamilyManager.AssociateElementParameterToFamilyParameter(vp, vis)
    # light source + LightFamily/LightType setters
    L = {}
    rep['light'] = L
    doc.OwnerFamily.get_Parameter(DB.BuiltInParameter.FBX_ASSET_TYPE).Set(1)
    try:
        lf = DB.Lighting.LightFamily.GetLightFamily(doc)
        L['n_types'] = lf.GetNumberOfLightTypes()
        L['style_before'] = [str(lf.GetLightShapeStyle()), str(lf.GetLightDistributionStyle())]
        lf.SetLightShapeStyle(DB.Lighting.LightShapeStyle.Point)
        lf.SetLightDistributionStyle(DB.Lighting.LightDistributionStyle.Spherical)
        L['style_after'] = [str(lf.GetLightShapeStyle()), str(lf.GetLightDistributionStyle())]
        lt = lf.GetLightType(0)
        L['intensity_before'] = [type(lt.GetInitialIntensity()).__name__, lt.GetInitialIntensity().InitialIntensityValue]
        L['color_before'] = [type(lt.GetInitialColor()).__name__, lt.GetInitialColor().TemperatureValue]
        L['loss_before'] = [type(lt.GetLossFactor()).__name__, lt.GetLossFactor().LossFactorValue]
        lt.SetInitialIntensity(DB.Lighting.InitialFluxIntensity(250.0))
        lt.SetInitialColor(DB.Lighting.CustomInitialColor(2700.0))
        lt.SetLossFactor(DB.Lighting.BasicLossFactor(1.0))
        lt.SetLightShape(DB.Lighting.PointLightShape())
        lt.SetLightDistribution(DB.Lighting.SphericalLightDistribution())
        lt = lf.GetLightType(0)
        L['intensity_after'] = [type(lt.GetInitialIntensity()).__name__, lt.GetInitialIntensity().InitialIntensityValue]
        L['color_after'] = [type(lt.GetInitialColor()).__name__, lt.GetInitialColor().TemperatureValue]
        L['loss_after'] = [type(lt.GetLossFactor()).__name__, lt.GetLossFactor().LossFactorValue]
        L['shape_after'] = type(lt.GetLightShape()).__name__
        L['dist_after'] = type(lt.GetLightDistribution()).__name__
    except Exception:
        L['error'] = traceback.format_exc()
    src = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_LightingFixtureSource).FirstElement()
    bb = src.get_BoundingBox(None)
    L['src_bbox_in_after_point'] = [round(c * 12, 4) for c in (bb.Min.X, bb.Min.Y, bb.Min.Z, bb.Max.X, bb.Max.Y, bb.Max.Z)] if bb else None
    L['fm_values'] = {}
    for q in fm.Parameters:
        if q.Definition.Name in ('Initial Intensity', 'Initial Color', 'Light Loss Factor', 'Emit from Line Length', 'Light Source Symbol Size'):
            try:
                L['fm_values'][q.Definition.Name] = fm.CurrentType.AsValueString(q)
            except Exception as ex:
                L['fm_values'][q.Definition.Name] = 'ERR ' + str(ex)[:80]
    tx.Commit()
    save()

    path = safe_path(RUN + 'work/explore6.rfa')
    so = DB.SaveAsOptions()
    so.OverwriteExistingFile = True
    doc.SaveAs(path, so)
    docs.remove(doc)
    doc.Close(False)
    fdoc = app.OpenDocumentFile(path)
    docs.append(fdoc)
    project = app.NewProjectDocument(DB.UnitSystem.Imperial)
    docs.append(project)
    fam = fdoc.LoadFamily(project)
    symbol = project.GetElement(list(fam.GetFamilySymbolIds())[0])
    t2 = DB.Transaction(project, 'place')
    t2.Start()
    level = next(iter(DB.FilteredElementCollector(project).OfClass(DB.Level)))
    wt = next(w for w in DB.FilteredElementCollector(project).OfClass(DB.WallType) if w.Kind == DB.WallKind.Basic)
    wall = DB.Wall.Create(project, DB.Line.CreateBound(DB.XYZ(-8, 0, 0), DB.XYZ(8, 0, 0)), wt.Id, level.Id, 10, 0, False, False)
    symbol.Activate()
    project.Regenerate()
    ref = DB.HostObjectUtils.GetSideFaces(wall, DB.ShellLayerType.Exterior)[0]
    face = wall.GetGeometryObjectFromReference(ref)
    rep['ext_face_normal'] = [face.FaceNormal.X, face.FaceNormal.Y, face.FaceNormal.Z]
    rep['wall_orientation'] = [wall.Orientation.X, wall.Orientation.Y, wall.Orientation.Z]
    pt = face.Project(DB.XYZ(0, 0, 5)).XYZPoint
    rep['place_point'] = [pt.X, pt.Y, pt.Z]
    inst = project.Create.NewFamilyInstance(ref, pt, DB.XYZ.BasisX, symbol)
    project.Regenerate()
    tr = inst.GetTransform()
    rep['inst_transform'] = {'X': [tr.BasisX.X, tr.BasisX.Y, tr.BasisX.Z], 'Y': [tr.BasisY.X, tr.BasisY.Y, tr.BasisY.Z],
                             'Z': [tr.BasisZ.X, tr.BasisZ.Y, tr.BasisZ.Z], 'O': [tr.Origin.X, tr.Origin.Y, tr.Origin.Z]}
    rep['ext_on'] = ext(inst)
    P = {}
    rep['params'] = P
    for nm in ('TP', 'IP', 'Vis'):
        e = {}
        p = inst.LookupParameter(nm)
        e['inst_lookup'] = None if p is None else {'ro': p.IsReadOnly, 'storage': str(p.StorageType)}
        q = symbol.LookupParameter(nm)
        e['symbol_lookup'] = None if q is None else {'ro': q.IsReadOnly, 'storage': str(q.StorageType)}
        e['in_inst_Parameters'] = nm in [x.Definition.Name for x in inst.Parameters]
        P[nm] = e
    # vis off
    v = inst.LookupParameter('Vis')
    v.Set(0)
    project.Regenerate()
    rep['ext_off'] = ext(inst)
    v.Set(1)
    # material swap via instance param (IP) and via whichever path works for TP
    alt = DB.Material.Create(project, 'ALT')
    P['IP']['set_inst'] = str(inst.LookupParameter('IP').Set(alt))
    project.Regenerate()
    rep['ext_ip_swapped'] = ext(inst)
    try:
        tpi = inst.LookupParameter('TP')
        P['TP']['set_inst'] = None if tpi is None else str(tpi.Set(alt))
    except Exception:
        P['TP']['set_inst'] = 'ERR ' + traceback.format_exc().strip().split('\n')[-1][:120]
    project.Regenerate()
    rep['ext_tp_inst_attempt'] = ext(inst)
    rep['alt_id'] = str(alt.Value)
    t2.Commit()
    rep['project_warnings'] = [w.GetDescriptionText() for w in project.GetWarnings()]
    rep['family_warnings'] = [w.GetDescriptionText() for w in fdoc.GetWarnings()]
except Exception:
    rep['error'] = traceback.format_exc()
finally:
    for d in reversed(docs):
        try:
            d.Close(False)
        except Exception:
            pass
    rep['done'] = True
    save()
