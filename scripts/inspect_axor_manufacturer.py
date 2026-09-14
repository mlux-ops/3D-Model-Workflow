import os,json,traceback,clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB
ROOT=r"C:\Users\found\OneDrive\Documents\ChatGPT\3D Model Workflow"
OUT=os.path.join(ROOT,'output','axor_angled','manufacturer_inspection.json')
SOURCE=os.path.join(ROOT,'references','axor_angled','16__Kitchen_Taps-Mixers_AXOR_39835USA-AXOR-Citterio-Single-lever-kitc_rfa.rfa')
r={}; doc=None
def geometry(g):
    result=[]
    for s in g:
        if isinstance(s,DB.GeometryInstance): result.extend(geometry(s.GetInstanceGeometry()))
        elif isinstance(s,DB.Solid) and s.Volume>1e-10:
            pts=[]
            for edge in s.Edges:
                pts.extend(list(edge.Tessellate()))
            result.append({'volume':s.Volume,'triangles':[[[v.X*12,v.Y*12,v.Z*12] for v in [mesh.get_Triangle(i).get_Vertex(j) for j in range(3)]] for face in s.Faces for mesh in [face.Triangulate()] for i in range(mesh.NumTriangles)],'faces':s.Faces.Size,'bounds_inches':[min(getattr(p,a) for p in pts)*12 for a in ['X','Y','Z']]+[max(getattr(p,a) for p in pts)*12 for a in ['X','Y','Z']]})
    return result
try:
    app=__revit__.Application
    doc=app.OpenDocumentFile(SOURCE)
    r['version']=app.VersionNumber; r['family']=doc.IsFamilyDocument
    r['elements']=[]
    for e in DB.FilteredElementCollector(doc).WhereElementIsNotElementType():
        try:
            g=e.get_Geometry(DB.Options())
            if g is None: continue
            r.setdefault('geometry_classes',[]).append({'id':str(e.Id.Value),'class':e.GetType().Name,'geometry':[x.GetType().Name for x in g]}); solids=geometry(g)
            if solids:r['elements'].append({'id':str(e.Id.Value),'class':e.GetType().Name,'parameters':[{ 'name':p.Definition.Name,'value':str(p.AsValueString())} for p in e.Parameters], 'category':e.Category.Name if e.Category else '', 'solids':solids})
        except Exception:r.setdefault('element_errors',[]).append(traceback.format_exc())
except Exception:r['error']=traceback.format_exc()
finally:
    if doc:doc.Close(False)
    with open(OUT,'w') as f:json.dump(r,f,indent=2)
