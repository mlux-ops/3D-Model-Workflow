# -*- coding: utf-8 -*-
"""Native source-backed fixture completion; invoke only through revit_run.py."""
import os,sys,json,math,traceback,hashlib
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from wieland_native import WielandFixture,DB,xyz
from native_fixture_support import all_solids,loop
from System.Collections.Generic import List
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO=os.path.dirname(os.path.dirname(os.path.dirname(ROOT)))

def motif(f,m):
    f.cylinder('15-inch canopy',xyz(),DB.XYZ.BasisZ,7.5,0,2,m['Metal Finish'],.06)
    positions=[]
    for radius,bottom in [(6.,31.25),(3.,51.625)]:
        for i in range(6):
            a=math.radians(i*60);positions.append((radius*math.cos(a),radius*math.sin(a),bottom))
    positions.append((0.,0.,72.))
    for i,(x,y,bottom) in enumerate(positions):
        top=bottom-20.625;origin=xyz(x,y,0)
        f.cylinder('Cord %d'%i,origin,DB.XYZ.BasisZ,.035,2,top,m['Metal Finish'])
        pieces=[f.cylinder('Upper ferrule %d'%i,origin,DB.XYZ.BasisZ,.375,top,top+.7,m['Metal Finish'])]
        pieces.append(f.tube('Clear optical tube %d'%i,origin,DB.XYZ.BasisZ,.375,.315,top+.7,bottom-.7,m['Glass Finish']))
        pieces.append(f.cylinder('Lower ferrule %d'%i,origin,DB.XYZ.BasisZ,.375,bottom-.7,bottom,m['Metal Finish']))
        f.cylinder('Filament %d'%i,origin,DB.XYZ.BasisZ,.085,top+.8,bottom-.8,m['Diffuser Finish'])
        f.check_component('Pendant body %d'%i,pieces,[.75,.75,20.625],'MP75121 manufacturer spec')

def wrap(f,m):
    f.box('Sheet-metal housing',-24.015,-2.99,0,24.015,2.99,.7,m['Metal Finish'],.08)
    profile=[(-2.89,.6),(-2.75,2.30),('arc',(-2.50,2.85),(-2.10,2.99)),(2.10,2.99),('arc',(2.50,2.85),(2.75,2.30)),(2.89,.6)]
    solid=DB.GeometryCreationUtilities.CreateExtrusionGeometry(List[DB.CurveLoop]([loop(xyz(-23.9,0,0),DB.XYZ.BasisY,DB.XYZ.BasisZ,profile)]),DB.XYZ.BasisX,47.8/12.)
    f.add('Continuous wraparound diffuser',solid,m['Diffuser Finish'])
    for x in [-24.015,23.90]:f.box('End cap',x,-2.91,.55,x+.115,2.91,2.99,m['Metal Finish'])

def qc4(f,m):
    can=xyz(1.50,0,0)
    body=f.tube('Open can',can,DB.XYZ.BasisZ,2.25,2.17,-5.375,0,m['Metal Finish'])
    f.cylinder('Can lid',can,DB.XYZ.BasisZ,2.25,-5.375,-5.225,m['Metal Finish'])
    frame=f.box('Plaster frame',-4.5,-3.,-.12,4.5,3.,0,m['Metal Finish'])
    from native_fixture_support import cylinder_solid
    f.doc.Regenerate()
    original=list(all_solids(frame.get_Geometry(DB.Options())))[0]
    cutter=cylinder_solid(can,DB.XYZ.BasisZ,2.25,-.3,.2)
    cut=DB.BooleanOperationsUtils.ExecuteBooleanOperation(original,cutter,DB.BooleanOperationsType.Difference)
    frame.UpdateSolidGeometry(cut)
    for x in [-4.4,4.22]:f.box('Supplied 13.5-inch bar hanger',x,-6.75,-.38,x+.18,6.75,-.12,m['Metal Finish'])
    f.box('Junction box',-4.15,-1.35,-4.45,-2.4,1.35,-.12,m['Metal Finish'])
    f.cylinder('Orange quick connector',can,DB.XYZ.BasisZ,.19,-.60,-.15,m['Connector Finish'])
    f.check_component('Housing height and can mouth',[body],[4.5,4.5,5.375],'QC4 manufacturer dimension drawing; nominal cutout')

def dew(f,m):
    f.cylinder('Wall plate',xyz(),DB.XYZ.BasisZ,1.8,0,.35,m['Metal Finish'],.08)
    f.revolve('Hand-blown clear rounded vessel',xyz(),DB.XYZ.BasisZ,[(.8,.35),(1.8,.35),('arc',(2.48,.65),(2.555,1.3)),('arc',(2.4,2.6),(1.,3.07)),(.1,3.07),(.1,2.98),(1.,2.98),('arc',(2.29,2.51),(2.44,1.3)),('arc',(2.35,.76),(1.8,.46)),(.8,.46)],m['Glass Finish'])
    f.cylinder('Central optical module',xyz(),DB.XYZ.BasisZ,1.05,.4,2.30,m['Diffuser Finish'],.12)

def faro(f,m):
    f.cylinder('Canopy',xyz(),DB.XYZ.BasisZ,2.375,0,.75,m['Metal Finish'],.05)
    f.cylinder('Suspension',xyz(),DB.XYZ.BasisZ,.045,.75,37,m['Metal Finish'])
    f.cylinder('Upper cap',xyz(),DB.XYZ.BasisZ,3.0,37,37.25,m['Metal Finish'])
    f.revolve('Clear upper vessel',xyz(),DB.XYZ.BasisZ,[(3.,37.12),(5.5,37.12),('arc',(6.6,37.6),(7.,39.1)),(7.,41.0),('arc',(6.6,42.9),(5.25,43.65)),(2.8,43.65),(2.8,43.50),(5.2,43.50),('arc',(6.46,42.8),(6.85,41.0)),(6.85,39.1),('arc',(6.45,37.75),(5.5,37.27)),(3.,37.27)],m['Glass Finish'])
    f.cylinder('Axial support',xyz(),DB.XYZ.BasisZ,.20,37.20,44,m['Metal Finish'])
    f.cylinder('Dark separator ring',xyz(),DB.XYZ.BasisZ,3.1,43.5,44.25,m['Metal Finish'],.06)
    f.revolve('Opal lower vessel',xyz(),DB.XYZ.BasisZ,[(0,44.12),(3.2,44.12),('arc',(4.4,44.8),(4.35,46.2)),('arc',(3.2,47.7),(0,48))],m['Diffuser Finish'])

def jube(f,m):
    f.cylinder('4.5-inch wall plate',xyz(0,-3.1,0),DB.XYZ.BasisZ,2.25,0,.55,m['Metal Finish'],.06)
    f.cylinder('Lower projecting arm',xyz(0,-3.1,0),DB.XYZ.BasisZ,.18,.5,4.5,m['Metal Finish'])
    axis=DB.XYZ.BasisY;origin=xyz(0,0,4.5)
    f.cylinder('Full vertical stem',origin,axis,.17,-7,7,m['Metal Finish'])
    f.revolve('Open smoke glass vessel',origin,axis,[(3.25,-.4),(3.5,.15),(3.5,4.55),('arc',(2.98,5.9),(1.35,6.25)),(.4,6.25),(.4,6.12),(1.35,6.12),('arc',(2.88,5.82),(3.37,4.55)),(3.37,.15),(3.12,-.27)],m['Glass Finish'])
    f.cylinder('Upper cover',origin,axis,1.30,6.15,6.35,m['Metal Finish'])
    f.cylinder('Internal light engine',origin,axis,2.0,2.75,3.7,m['Metal Finish'],.04)
    f.cylinder('Downward opal optic',origin,axis,1.96,2.57,2.77,m['Diffuser Finish'])

def verto(f,m):
    f.cylinder('Canopy',xyz(),DB.XYZ.BasisZ,2.5,0,.75,m['Metal Finish'],.05)
    f.cylinder('Two 12-inch rods',xyz(),DB.XYZ.BasisZ,.18,.75,24.75,m['Metal Finish'])
    top=24.75
    f.cylinder('Top cap',xyz(),DB.XYZ.BasisZ,.72,top,top+1.35,m['Metal Finish'],.05)
    f.revolve('Clear elongated spindle',xyz(),DB.XYZ.BasisZ,[(.62,top+.8),('arc',(1.18,top+3.0),(1.5,top+7.5)),(1.5,top+12.75),('arc',(1.18,top+17.25),(.62,top+19.4)),(.54,top+19.4),('arc',(1.08,top+17.20),(1.42,top+12.75)),(1.42,top+7.5),('arc',(1.08,top+3.05),(.54,top+.8))],m['Glass Finish'])
    f.cylinder('Acrylic inner diffuser',xyz(),DB.XYZ.BasisZ,.36,top+1.15,top+19.1,m['Diffuser Finish'])
    f.cylinder('Lower cap',xyz(),DB.XYZ.BasisZ,.72,top+18.9,45,m['Metal Finish'],.05)

def source_copy(f,m,kind):
    inspections=json.load(open(os.path.join(ROOT,'COMPLETION_NATIVE_INSPECTION.json')))
    source=next(r for r in inspections if (kind=='focus_source' and r['key']=='Focus') or (kind=='tris_source' and 'Tris_Bath_Bar' in r['key']) or (kind=='milan_source' and 'Milan_24' in r['key']))
    path=source['source'];digest=hashlib.sha256(open(path,'rb').read()).hexdigest();doc=f.app.OpenDocumentFile(path)
    copied=[];detail=[]
    try:
        options=DB.Options();options.DetailLevel=DB.ViewDetailLevel.Fine;options.IncludeNonVisibleObjects=True
        for entry in source['forms']:
            eid=entry['id']
            if eid=='1537' or (kind=='tris_source' and eid=='718010'):continue
            element=doc.GetElement(DB.ElementId(int(eid)))
            for idx,solid in enumerate(all_solids(element.get_Geometry(options))):
                label='Metal Finish'
                names=[]
                for face in solid.Faces:
                    mat=doc.GetElement(face.MaterialElementId)
                    if mat is not None and mat.Name not in names:names.append(mat.Name)
                if kind=='focus_source':
                    if any('disc' in n.lower() or 'acrylic' in n.lower() for n in names):label='Disc Finish'
                elif entry.get('material_parameter')=='Lens':label='Diffuser Finish'
                form=f.add('Source '+eid+' / '+str(idx),DB.SolidUtils.CreateTransformed(solid,DB.Transform.Identity),m[label])
                if eid=='4027':copied.append(form)
                detail.append({'source_id':eid,'label':label,'source_materials':names})
        if kind=='tris_source':
            f.box('Current-spec 5 x 4.3 backplate',-2.5,-2.15,0,2.5,2.15,.562,m['Metal Finish'])
        if kind=='focus_source':f.check_component('Native mobile height',copied,[None,None,1037/25.4],'DCW Focus X3 US technical sheet')
        f.report.update(source_rfa=path,source_rfa_sha256=digest,source_material_mapping=detail,source_file_unchanged=hashlib.sha256(open(path,'rb').read()).hexdigest()==digest)
    finally:doc.Close(False)

def run_one(app,key):
    jobs=json.load(open(os.path.join(ROOT,'COMPLETION_JOBS.json')));j=next(x for x in jobs if x['key']==key)
    f=None
    try:
        f=WielandFixture(app,j['out'],j['name'],j['manufacturer'],j['model'],j['model'],j['host'],j['dimensions'])
        materials={}
        for row in j['materials']:
            data=dict(row);label=data.pop('label');materials[label]=f.material(label,**data)
        if j['builder'].endswith('_source'):source_copy(f,materials,j['builder'])
        else:globals()[j['builder']](f,materials)
        f.note(j['notes']);f.report.update(source_url=j['source_url'],limitations=j['notes'],rfa_search=j.get('rfa_search','Official product resources and verified BIM listings searched; no exact, usable anonymous RFA accepted. See retained source resources and manufacturer acquisition/inspection receipts.'))
        return f.finish()
    except Exception:
        if f is not None:
            f.fail()
            with open(os.path.join(j['out'],'validation.json'),'w') as out:json.dump(f.report,out,indent=2,default=str)
        raise

def main(app):
    jobs=json.load(open(os.path.join(ROOT,'COMPLETION_JOBS.json')))
    selection=os.path.join(ROOT,'COMPLETION_RUN_KEYS.json')
    keys=json.load(open(selection)) if os.path.isfile(selection) else [j['key'] for j in jobs]
    result=[]
    for key in keys:
        try:
            report=run_one(app,key);result.append({'key':key,'pass':report['technical_pass'],'rfa':report['rfa_path']})
        except Exception:result.append({'key':key,'pass':False,'error':traceback.format_exc()})
        with open(os.path.join(ROOT,'COMPLETION_BATCH_RESULT.json'),'w') as out:json.dump(result,out,indent=2)

if __name__=='__main__':main(__revit__.Application)
