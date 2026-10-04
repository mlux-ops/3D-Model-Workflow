# -*- coding: utf-8 -*-
"""Export opaque outline views of accepted saved families without resaving them."""
import os,sys,json,math,traceback,hashlib,datetime
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from native_fixture_support import NativeFixture,DB,xyz,measured_geometry_bounds
from System.Collections.Generic import List
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def main(app):
    groups=json.load(open(os.path.join(ROOT,'GROUPS.json')))['groups']
    folders=[os.path.join(ROOT,g['canonical_item']) for g in groups]
    folders.append(os.path.join(ROOT,'K1-1__8353463272013700'))
    results=[]
    for folder in folders:
        vp=os.path.join(folder,'validation.json')
        if not os.path.isfile(vp):continue
        validation=json.load(open(vp))
        if not validation.get('technical_pass'):continue
        path=validation['rfa_path'];before=hashlib.sha256(open(path,'rb').read()).hexdigest()
        existing=os.path.join(folder,'evidence','geometry_review.json')
        if os.path.isfile(existing):
            old=json.load(open(existing))
            if old.get('rfa_sha256')==before and old.get('pass'):
                results.append(old);continue
        doc=None;tx=None;row={'rfa_path':path,'rfa_sha256':before,'started_utc':datetime.datetime.utcnow().isoformat()+'Z'}
        try:
            doc=app.OpenDocumentFile(path)
            elements=[doc.GetElement(DB.ElementId(int(p['id']))) for p in validation['parts']]
            box=measured_geometry_bounds(elements);center=xyz(*[(box[i]+box[i+3])/2 for i in range(3)])
            span=max(box[i+3]-box[i] for i in range(3))*2+12
            wall=validation['host']['host_kind']=='wall';up=DB.XYZ.BasisY if wall else DB.XYZ(0,0,-1)
            helper=NativeFixture.__new__(NativeFixture);helper.evidence=os.path.join(folder,'evidence')
            template=[DB.ElementId(int(i)) for i in validation['template_form_ids']]
            tx=DB.Transaction(doc,'Unsaved geometry diagnostic views');tx.Start()
            # Family documents reject SetElementOverrides. Opaque unsaved
            # material edits support hidden-line review without changing RFA.
            for material in DB.FilteredElementCollector(doc).OfClass(DB.Material):
                material.Transparency=0
            poses=[('Geometry Front',center.Add(xyz(0,0,span)) if wall else center.Add(xyz(0,-span,0))),('Geometry Oblique',center.Add(xyz(span*.65,-span*.45,span*.65)))]
            views=[]
            for name,eye in poses:
                view=helper._view(doc,name,eye,center,up,elements,False,template)
                view.DisplayStyle=DB.DisplayStyle.HLR
                views.append(view)
            tx.Commit();tx=None
            helper._export(doc,views,'GeometryReview')
            files=[os.path.join(folder,'evidence',n) for n in os.listdir(helper.evidence) if n.startswith('GeometryReview') and n.endswith('.png')]
            row.update(files=files,pass_=len(files)==2,category=doc.OwnerFamily.FamilyCategory.Name,
                       measured_bounds_in=box,measured_dimensions_in=[box[i+3]-box[i] for i in range(3)])
            doc.Close(False);doc=None
            row['unchanged_after_review']=hashlib.sha256(open(path,'rb').read()).hexdigest()==before
            row['pass']=row.pop('pass_') and row['unchanged_after_review']
        except Exception:row.update(error=traceback.format_exc(),**{'pass':False})
        finally:
            if tx:
                try:tx.RollBack()
                except Exception:pass
            if doc:doc.Close(False)
        with open(existing,'w') as f:json.dump(row,f,indent=2)
        results.append(row)
        with open(os.path.join(ROOT,'GEOMETRY_REVIEW_EXPORT.json'),'w') as f:json.dump(results,f,indent=2)

if __name__=='__main__':main(__revit__.Application)
