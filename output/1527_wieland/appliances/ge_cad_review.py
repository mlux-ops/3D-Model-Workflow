# -*- coding: utf-8 -*-
"""Inspect exact GE 3D DWGs in isolated native family candidates."""
import os,sys,traceback,datetime
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from family_common import *
from build_custom import TEMPLATE,Builder

def solids(geometry):
    for g in geometry:
        if isinstance(g,DB.GeometryInstance):
            for s in solids(g.GetInstanceGeometry()):
                yield s
        elif isinstance(g,DB.Solid) and g.Volume>1e-10:
            yield g

app=__revit__.Application
models=json.load(open(os.path.join(ROOT,'custom_models.json')))
for c in [x for x in models if x['brand']=='GE']:
    folder=os.path.join(ROOT,c['slug']);doc=None;tx=None
    r={'slug':c['slug'],'started_utc':str(datetime.datetime.utcnow()),'ok':False,'stage':'starting'}
    try:
        doc=app.NewFamilyDocument(TEMPLATE)
        tx=DB.Transaction(doc,'Import official GE CAD');tx.Start()
        doc.OwnerFamily.FamilyCategory=DB.Category.GetCategory(doc,DB.BuiltInCategory.OST_SpecialityEquipment)
        doc.OwnerFamily.get_Parameter(DB.BuiltInParameter.FAMILY_WORK_PLANE_BASED).Set(1)
        doc.FamilyManager.NewType(c['model'])
        vt=next(v for v in DB.FilteredElementCollector(doc).OfClass(DB.ViewFamilyType) if v.ViewFamily==DB.ViewFamily.ThreeDimensional)
        view=DB.View3D.CreateIsometric(doc,vt.Id)
        opts=DB.DWGImportOptions();opts.ThisViewOnly=False;opts.Placement=DB.ImportPlacement.Origin;opts.Unit=DB.ImportUnit.Default
        ref=clr.Reference[DB.ElementId]()
        imported=doc.Import(os.path.join(folder,'source','official_3D.dwg'),opts,view,ref)
        doc.Regenerate()
        element=doc.GetElement(ref.Value)
        r['import_success']=imported
        r['cad_bounds']=measure([element])
        opt=DB.Options();opt.DetailLevel=DB.ViewDetailLevel.Fine
        cad_solids=list(solids(element.get_Geometry(opt)))
        r['solid_count']=len(cad_solids)
        r['target_xyz_mm']=[c['width'],c['depth'],c['height']]
        size=r['cad_bounds']['xyz_size_mm']
        r['dimension_delta_mm']=[size[i]-r['target_xyz_mm'][i] for i in range(3)]
        r['dimension_gate']=all(abs(v)<=1.0 for v in r['dimension_delta_mm'])
        tx.Commit()
        r['previews']=export_view(doc,os.path.join(folder,'views'),'official_cad',r['cad_bounds'],(-1,1.5,-0.7),doc.OwnerFamily.FamilyCategory.Id)
        out=os.path.join(folder,'source','official_cad_review_R2025.rfa')
        options=DB.SaveAsOptions();options.OverwriteExistingFile=True
        doc.SaveAs(out,options)
        r['review_rfa']=out
        r['ok']=True;r['stage']='imported_measured_previewed_saved'
    except Exception:
        r['error']=traceback.format_exc()
        if tx:
            try:
                if tx.GetStatus()==DB.TransactionStatus.Started:tx.RollBack()
            except Exception:pass
    finally:
        if doc:
            try:doc.Close(False)
            except Exception:pass
        r['finished_utc']=str(datetime.datetime.utcnow())
        write_json(os.path.join(folder,'source','cad_review.json'),r)
