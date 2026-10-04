# -*- coding: utf-8 -*-
"""Source-informed native remaining families. All calls require revit_run.py."""
import os,sys,json,math,traceback
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from wieland_native import WielandFixture,DB,xyz,measured_geometry_bounds
from native_fixture_support import loop,all_solids,cylinder_solid
from build_completion import ellipsoid
from System.Collections.Generic import List
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def ellipse_loop(center,u,v,ra,rb):
    result=DB.CurveLoop()
    for a,b in [(0,math.pi),(math.pi,2*math.pi)]:result.Append(DB.Ellipse.CreateCurve(center,ra/12.,rb/12.,u,v,a,b))
    return result

def loft(profiles):
    return DB.GeometryCreationUtilities.CreateLoftGeometry(List[DB.CurveLoop](profiles),DB.SolidOptions(DB.ElementId.InvalidElementId,DB.ElementId.InvalidElementId))

def solid_points(solid):
    points=[]
    for face in solid.Faces:points.extend(face.Triangulate(1).Vertices)
    for edge in solid.Edges:
        curve=edge.AsCurve();points.extend(curve.Evaluate(float(i)/256,True) for i in range(257))
    return points

def juno_trim(f,m):
    f.cylinder('Black driver case',xyz(),DB.XYZ.BasisZ,1.52,-2.96,-1.94,m['Metal Finish'],.05)
    f.cylinder('White mixing chamber',xyz(),DB.XYZ.BasisZ,1.60,-1.95,-.80,m['Trim Finish'])
    # Open 4-inch visible aperture, stepped conical white baffle and 5.25-inch flange.
    profile=[(1.25,-.90),(1.6,-.90)]
    for i in range(9):
        y=-.90+i*.1;r=1.6+i*.05
        profile.extend([(r,y),(r+.04,y+.04)])
    profile.extend([(2.625,.08),(2.625,.20),(2.,.20),(1.25,-.75)])
    f.revolve('Baffle and overlap trim',xyz(),DB.XYZ.BasisZ,profile,m['Trim Finish'])
    f.cylinder('Recessed diffuser',xyz(),DB.XYZ.BasisZ,1.26,-.89,-.74,m['Diffuser Finish'])
    for sign in [-1,1]:
        x0,x1=sorted([sign*1.58,sign*2.05])
        f.box('Retention clip',x0,-.23,-1.92,x1,.23,-1.80,m['Trim Finish'])

def hold(f,m):
    f.cylinder('5-inch wall plate',xyz(0,6.5,0),DB.XYZ.BasisZ,2.5,0,.15,m['Metal Finish'],.04)
    stations=[(-9,.10,.08),(-8.75,.65,.38),(-7.4,1.9,1.03),(-5.1,2.43,1.4),(-2.6,1.92,1.22),(-.5,.96,.62),(.7,.61,.41),(2.0,.71,.33),(3.0,.43,.22)]
    sx=sz=1.
    for attempt in range(3):
        outer=loft([ellipse_loop(xyz(0,y,3.75),DB.XYZ.BasisX,DB.XYZ.BasisZ,rx*sx,rz*sz) for y,rx,rz in stations])
        points=solid_points(outer)
        width=(max(p.X for p in points)-min(p.X for p in points))*12
        depth=(max(p.Z for p in points)-min(p.Z for p in points))*12
        if abs(width-5)<.003 and abs(depth-3.5)<.003:break
        sx*=5./width;sz*=3.5/depth
    inner_stations=[(-8.75,.10,.07),(-8.45,.5,.25),(-7.4,1.9*sx-.14,1.03*sz-.14),(-5.1,2.43*sx-.14,1.4*sz-.14),(-2.6,1.92*sx-.14,1.22*sz-.14),(-.5,.96*sx-.13,.62*sz-.13),(.7,.48*sx,.29*sz),(2.0,.50*sx,.2*sz)]
    inner=loft([ellipse_loop(xyz(0,y,3.75),DB.XYZ.BasisX,DB.XYZ.BasisZ,rx,rz) for y,rx,rz in inner_stations])
    shell=DB.BooleanOperationsUtils.ExecuteBooleanOperation(outer,inner,DB.BooleanOperationsType.Difference)
    opening=DB.GeometryCreationUtilities.CreateExtrusionGeometry(List[DB.CurveLoop]([ellipse_loop(xyz(0,1.3,0),DB.XYZ.BasisX,DB.XYZ.BasisY,.40,1.20)]),DB.XYZ.BasisZ,6./12)
    shell=DB.BooleanOperationsUtils.ExecuteBooleanOperation(shell,opening,DB.BooleanOperationsType.Difference)
    vessel=f.add('Open handblown white vessel',shell,m['Glass Finish'])
    f.check_component('12-inch glass vessel',[vessel],[5,12,3.5],'SkLO June 2026: width and height nominal; glass depth drawing-derived')
    path=DB.CurveLoop();p0=xyz(0,6.5,.15);p1=xyz(0,6.5,3.2);p2=xyz(0,6.,3.7);p3=xyz(0,3.1,3.7);p4=xyz(0,2.6,4.2);p5=xyz(0,2.6,4.6)
    path.Append(DB.Line.CreateBound(p0,p1));path.Append(DB.Arc.Create(p1,p2,xyz(0,6.353553,3.553553)))
    path.Append(DB.Line.CreateBound(p2,p3));path.Append(DB.Arc.Create(p3,p4,xyz(0,2.746447,3.846447)));path.Append(DB.Line.CreateBound(p4,p5))
    hook=DB.GeometryCreationUtilities.CreateSweptGeometry(path,0,0,List[DB.CurveLoop]([ellipse_loop(p0,DB.XYZ.BasisX,DB.XYZ.BasisY,.18,.18)]))
    f.add('Continuous curved brass hook',hook,m['Metal Finish'])
    f.cylinder('Suspended black cord',xyz(0,0,4.15),DB.XYZ.BasisY,.045,-4.,2.5,m['Cord Finish'])
    f.cylinder('Lamp socket',xyz(0,0,4.15),DB.XYZ.BasisY,.28,-4.9,-4,m['Metal Finish'])
    f.add('Internal lamp',ellipsoid(xyz(0,-5.65,4.15),.45,.75),m['Diffuser Finish'])

def blade_solid(sweep,zephyr=False):
    shape=[(3.7,-.4,1.4,28),(7.,-.1,3.3,22),(14.,.5,3.5,13),(21.,1.9,3.0,8),(26.,3.,2.5,5)] if zephyr else [(3.5,0.,3.1,32),(7.,.3,3.75,26),(15.,.2,3.55,14),(23.,.0,3.05,6),(28.,-.3,2.65,3)]
    height=14.3 if zephyr else 10.0
    factor=1.
    for attempt in range(4):
        profiles=[]
        for r,side,half_width,pitch in shape:
            a=math.radians(pitch);u=DB.XYZ(0,math.cos(a),math.sin(a));v=DB.XYZ(0,-math.sin(a),math.cos(a))
            profiles.append(ellipse_loop(xyz(r*factor,side*factor,height),u,v,half_width*factor,.12))
        solid=loft(profiles)
        diameter=2*max(math.hypot(p.X*12,p.Y*12) for p in solid_points(solid))
        if abs(diameter-sweep)<.002:break
        factor*=sweep/diameter
    return solid

def fan(f,m,zephyr=False):
    sweep=52. if zephyr else 56.;height=18.125 if zephyr else 14.45
    canopy_radius=3.5 if zephyr else 2.75
    canopy=f.cylinder('Manufacturer canopy diameter',xyz(),DB.XYZ.BasisZ,canopy_radius,0,1.35 if zephyr else 1.25,m['Metal Finish'],.10)
    f.revolve('Canopy shoulder',xyz(),DB.XYZ.BasisZ,[(0,1.2),(canopy_radius-.1,1.2),(1.,2.35 if zephyr else 2.0),(0,2.35 if zephyr else 2.0)],m['Metal Finish'])
    f.cylinder('Included downrod',xyz(),DB.XYZ.BasisZ,.375 if zephyr else .30,1.3,11.0 if zephyr else 7.3,m['Metal Finish'])
    if zephyr:
        f.revolve('Aerodynamic motor housing',xyz(),DB.XYZ.BasisZ,[(0,10.7),(.7,10.7),(1.1,11.5),(2.3,12.5),(3.6,13.4),(4.05,14.5),(3.65,16.3),(2.82,17.7),(0,17.7)],m['Metal Finish'])
        light=f.add('5.625-inch opal luminaire',ellipsoid(xyz(0,0,17.575),2.8125,.55),m['Diffuser Finish'])
        f.check_component('Luminaire diameter',[light],[5.625,5.625,None],'Modern Forms Zephyr 52 factory drawing')
    else:
        f.revolve('Upper motor shoulder',xyz(),DB.XYZ.BasisZ,[(0,6.5),(.7,6.5),(.9,7.0),(2.7,7.6),(3.6,8.3),(0,8.3)],m['Metal Finish'])
        housing=f.cylinder('7.9-inch motor housing',xyz(),DB.XYZ.BasisZ,3.95,8.3,13.35,m['Metal Finish'],.15)
        f.cylinder('Optional 870 LED collar',xyz(),DB.XYZ.BasisZ,2.8,13.3,14.,m['Metal Finish'],.05)
        light=f.add('Optional 870 opal diffuser',ellipsoid(xyz(0,0,14.0),2.8,.45),m['Diffuser Finish'])
        f.check_component('Motor housing diameter',[housing],[7.9,7.9,None],'Modern Fan Ambit factory cut sheet')
    source=blade_solid(sweep,zephyr);blades=[]
    for i in range(3):
        rotation=DB.Transform.CreateRotation(DB.XYZ.BasisZ,math.radians(i*120))
        blades.append(f.add('Shaped ABS blade %d'%(i+1),DB.SolidUtils.CreateTransformed(source,rotation),m['Blade Finish']))
    f.check_component('Canopy diameter',[canopy],[2*canopy_radius,2*canopy_radius,None],'Manufacturer dimension drawing')
    f.report['radial_checks']=[{'label':'Swept blade diameter','element_ids':[str(b.Id.Value) for b in blades],'expected_diameter_in':sweep,'center_in':[0,0],'source':'Manufacturer nominal blade sweep'}]
    f.doc.Regenerate();box=measured_geometry_bounds(f.forms)
    f.expected=[box[3]-box[0],box[4]-box[1],height]
    f.report['expected_dimensions_in']=f.expected
    f.report['nominal_product_dimensions']={'blade_sweep_in':sweep,'installed_drop_in':height,'rectangular_bounds_basis':'Stationary three-blade envelope; informational, not the nominal circular sweep.'}
    for name,value in [('Model Width',f.expected[0]),('Model Depth',f.expected[1])]:f.fm.SetFormula(f.fm.get_Parameter(name),str(value)+' in')
    f.length('Blade Sweep Diameter',sweep)

def ambit(f,m):fan(f,m,False)
def zephyr(f,m):fan(f,m,True)

def modena(f,m):
    f.cylinder('Manufacturer canopy',xyz(),DB.XYZ.BasisZ,2.35,0,1,m['Metal Finish'],.05)
    start=len(f.forms);radius=(27.8-4.7)/(2*math.cos(math.radians(15)))
    for i,degrees in enumerate([15,75,135]):
        a=math.radians(degrees);axis=DB.XYZ(math.cos(a),math.sin(a),0);z=44.45+i*.6
        f.cylinder('Crossed bar %d'%i,xyz(0,0,z),axis,.26,-radius,radius,m['Metal Finish'],.08)
        for side in [-1,1]:
            center=xyz(side*radius*math.cos(a),side*radius*math.sin(a),z)
            f.globe('Smoked globe %d %d'%(i,side),center,2.35,.09,axis.Multiply(-side),.58,m['Glass Finish'])
            f.cylinder('Socket %d %d'%(i,side),center,axis,.43,-1.5,-.7,m['Metal Finish'])
            f.cylinder('Lamp %d %d'%(i,side),center,axis,.32,-.7,1.,m['Diffuser Finish'],.12)
    body=list(f.forms[start:]);f.check_component('Six-globe fixture body',body,[27.8,27.8,5.9],'Artcraft AC11976SM published body dimensions')
    for i in range(3):
        a=math.radians(15+i*120);position=xyz(4.3*math.cos(a),4.3*math.sin(a),0)
        ceiling=xyz(1.1*math.cos(a),1.1*math.sin(a),1.)
        lower=xyz(position.X*12,position.Y*12,44.45+i*.6)
        direction=lower.Subtract(ceiling);f.cylinder('Suspension cord %d'%i,ceiling,direction.Normalize(),.042,0,direction.GetLength()*12,m['Metal Finish'])

def run_one(app,key):
    job=next(j for j in json.load(open(os.path.join(ROOT,'REMAINING_JOBS.json'))) if j['key']==key)
    f=None
    try:
        f=WielandFixture(app,job['out'],job['name'],job['manufacturer'],job['model'],job['model'],job['host'],job['dimensions'])
        mats={}
        for entry in job['materials']:
            data=dict(entry);label=data.pop('label');mats[label]=f.material(label,**data)
        globals()[job['builder']](f,mats)
        f.note(job['notes']);f.report.update(source_url=job['source_url'],limitations=job['notes'],rfa_search='Public manufacturer and reputable BIM resource searches retained. No exact acceptable anonymous native RFA accepted; see acquisition evidence.')
        return f.finish()
    except Exception:
        if f:
            f.fail()
            with open(os.path.join(job['out'],'validation.json'),'w') as out:json.dump(f.report,out,indent=2,default=str)
        raise

def main(app):
    jobs=json.load(open(os.path.join(ROOT,'REMAINING_JOBS.json')));selection=os.path.join(ROOT,'REMAINING_RUN_KEYS.json')
    keys=json.load(open(selection)) if os.path.isfile(selection) else [j['key'] for j in jobs]
    results=[]
    for key in keys:
        try:
            r=run_one(app,key);results.append({'key':key,'pass':r['technical_pass'],'rfa':r['rfa_path']})
        except Exception:results.append({'key':key,'pass':False,'error':traceback.format_exc()})
        with open(os.path.join(ROOT,'REMAINING_BATCH_RESULT.json'),'w') as out:json.dump(results,out,indent=2)

if __name__=='__main__':main(__revit__.Application)
