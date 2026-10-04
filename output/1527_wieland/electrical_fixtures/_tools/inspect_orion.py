# -*- coding: utf-8 -*-
"""Native inspection and 2025 source upgrade for the public Orion Tube RFA."""
import os,sys,json,traceback,datetime
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from native_fixture_support import DB,all_solids
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def ascii_text(value):return ''.join(c if ord(c)<128 else '[U+%04X]'%ord(c) for c in unicode(value))
def main(app):
    record=next(r for r in json.load(open(os.path.join(ROOT,'FINAL_SOURCE_RECEIPTS.json'))) if 'extracted_files' in r)
    path=next(p for p in record['extracted_files'] if os.path.basename(p)=='Orion Tube Light.rfa')
    report={'source':path,'started_utc':datetime.datetime.utcnow().isoformat()+'Z'}
    doc=None
    try:
        basic=DB.BasicFileInfo.Extract(path);report['source_revit_version']=str(basic.Format);basic.Dispose()
        doc=app.OpenDocumentFile(path);fm=doc.FamilyManager
        report.update(category=doc.OwnerFamily.FamilyCategory.Name,placement=str(doc.OwnerFamily.FamilyPlacementType),types=[ascii_text(t.Name) for t in fm.Types],parameters=[],forms=[])
        for p in fm.Parameters:
            entry={'name':ascii_text(p.Definition.Name),'data_type':p.Definition.GetDataType().TypeId,'formula':ascii_text(p.Formula),'storage':str(p.StorageType)}
            if p.StorageType==DB.StorageType.Double:
                value=fm.CurrentType.AsDouble(p);entry['inches']=value*12 if value is not None else None
            elif p.StorageType==DB.StorageType.String:entry['value']=ascii_text(fm.CurrentType.AsString(p))
            elif p.StorageType==DB.StorageType.ElementId:
                element=doc.GetElement(fm.CurrentType.AsElementId(p));entry['value']=ascii_text(element.Name) if element else None
            report['parameters'].append(entry)
        opts=DB.Options();opts.DetailLevel=DB.ViewDetailLevel.Fine;opts.IncludeNonVisibleObjects=True
        for e in DB.FilteredElementCollector(doc).WhereElementIsNotElementType():
            if not isinstance(e,(DB.GenericForm,DB.FamilyInstance,DB.ImportInstance,DB.DirectShape)):continue
            solids=list(all_solids(e.get_Geometry(opts)))
            points=[]
            for solid in solids:
                for face in solid.Faces:points.extend(face.Triangulate(1).Vertices)
            entry={'id':str(e.Id.Value),'class':e.GetType().Name,'solids':len(solids),'category':e.Category.Name if e.Category else None}
            if points:entry['bounds_in']=[min(getattr(p,a) for p in points)*12 for a in ('X','Y','Z')]+[max(getattr(p,a) for p in points)*12 for a in ('X','Y','Z')]
            param=e.get_Parameter(DB.BuiltInParameter.MATERIAL_ID_PARAM)
            if param:
                mat=doc.GetElement(param.AsElementId());fp=fm.GetAssociatedFamilyParameter(param)
                entry.update(material=ascii_text(mat.Name) if mat else None,material_parameter=ascii_text(fp.Definition.Name) if fp else None)
            report['forms'].append(entry)
        report['warnings']=[ascii_text(w.GetDescriptionText()) for w in doc.GetWarnings()]
        upgraded=os.path.join(os.path.dirname(path),'Orion_Tube_OEM_2025.rfa')
        if not os.path.isfile(upgraded):doc.SaveAs(upgraded,DB.SaveAsOptions())
        report.update(upgraded_path=upgraded,stage='inspected_and_upgraded')
    except Exception:report.update(stage='failed',error=traceback.format_exc())
    finally:
        if doc:doc.Close(False)
    with open(os.path.join(ROOT,'ORION_NATIVE_INSPECTION.json'),'w') as f:json.dump(report,f,indent=2)

if __name__=='__main__':main(__revit__.Application)
