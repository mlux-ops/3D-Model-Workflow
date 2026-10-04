# -*- coding: utf-8 -*-
"""Inspect manufacturer solids including native visibility settings; no source edits."""
import os, sys, json, traceback, datetime
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,os.path.join(ROOT,'_tools'))
from native_fixture_support import DB, all_solids
app=__revit__.Application
sources=json.load(open(os.path.join(ROOT,'OEM_EXTRACTED_FILES.json')))
jobs=[(os.path.basename(r['path']),r['path']) for r in sources if r['extension']=='.rfa' and os.path.basename(r['path']).startswith('Lighting-')]
repo=os.path.dirname(os.path.dirname(os.path.dirname(ROOT)))
jobs.append(('Focus',os.path.join(repo,'output','focus','DCW_Focus_X3_Black_Adjustable_R2025.rfa')))
reports=[]
for key,path in jobs:
    doc=None
    row={'key':key,'source':path,'started':datetime.datetime.utcnow().isoformat()+'Z'}
    try:
        doc=app.OpenDocumentFile(path)
        row['category']=doc.OwnerFamily.FamilyCategory.Name
        row['forms']=[]
        options=DB.Options();options.DetailLevel=DB.ViewDetailLevel.Fine;options.IncludeNonVisibleObjects=True
        for e in DB.FilteredElementCollector(doc).WhereElementIsNotElementType():
            if not isinstance(e,(DB.GenericForm,DB.FamilyInstance)):continue
            if e.Category is not None and e.Category.Name=='Host':continue
            solids=list(all_solids(e.get_Geometry(options)))
            entry={'id':str(e.Id.Value),'class':e.GetType().Name,'solids':len(solids),'volumes':[s.Volume for s in solids]}
            if isinstance(e,DB.GenericForm):
                entry['is_solid']=e.IsSolid
                vis=e.GetVisibility()
                entry['visibility']={'fine':vis.IsShownInFine,'medium':vis.IsShownInMedium,'coarse':vis.IsShownInCoarse}
            p=e.get_Parameter(DB.BuiltInParameter.MATERIAL_ID_PARAM)
            if p:
                fp=doc.FamilyManager.GetAssociatedFamilyParameter(p)
                entry['material_parameter']=fp.Definition.Name if fp else None
            pts=[]
            for s in solids:
                for face in s.Faces:pts.extend(list(face.Triangulate(.5).Vertices))
            if pts:entry['bounds_in']=[min(getattr(p,a) for p in pts)*12 for a in ('X','Y','Z')]+[max(getattr(p,a) for p in pts)*12 for a in ('X','Y','Z')]
            row['forms'].append(entry)
        row['stage']='inspected'
        row['warnings']=[w.GetDescriptionText() for w in doc.GetWarnings()]
    except Exception:row.update(stage='failed',error=traceback.format_exc())
    finally:
        if doc:doc.Close(False)
    reports.append(row)
    with open(os.path.join(ROOT,'COMPLETION_NATIVE_INSPECTION.json'),'w') as out:json.dump(reports,out,indent=2,default=str)
