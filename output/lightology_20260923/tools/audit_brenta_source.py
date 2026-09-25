# -*- coding: utf-8 -*-
import os,json,clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB
root=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
path=os.path.join(root,'f03_1241670','source','visualcomfort_arn2473_reference.rfa')
doc=__revit__.Application.OpenDocumentFile(path)
def solids(g):
    if g is None:return
    for item in g:
        if isinstance(item,DB.Solid) and item.Volume>1e-12:yield item
        elif isinstance(item,DB.GeometryInstance):
            for s in solids(item.GetInstanceGeometry()):yield s
rows=[]
try:
    opt=DB.Options();opt.DetailLevel=DB.ViewDetailLevel.Fine
    for element in DB.FilteredElementCollector(doc).WhereElementIsNotElementType():
        try:geo=element.get_Geometry(opt)
        except Exception:continue
        for solid in solids(geo):
            bb=solid.GetBoundingBox();corners=[bb.Transform.OfPoint(DB.XYZ(x,y,z)) for x in [bb.Min.X,bb.Max.X] for y in [bb.Min.Y,bb.Max.Y] for z in [bb.Min.Z,bb.Max.Z]]
            mn=[min(getattr(p,a) for p in corners)*12 for a in ['X','Y','Z']];mx=[max(getattr(p,a) for p in corners)*12 for a in ['X','Y','Z']]
            mats=[]
            for face in solid.Faces:
                mat=doc.GetElement(face.MaterialElementId)
                if mat is not None and mat.Name not in mats:mats.append(mat.Name)
            rows.append({'index':len(rows),'element':int(element.Id.Value),'minimum_in':mn,'maximum_in':mx,'size_in':[mx[i]-mn[i] for i in range(3)],'volume_ft3':solid.Volume,'materials':mats,'face_count':solid.Faces.Size})
    with open(os.path.join(root,'f03_1241670','source_geometry_measurements.json'),'w') as stream:json.dump(rows,stream,indent=2)
finally:doc.Close(False)