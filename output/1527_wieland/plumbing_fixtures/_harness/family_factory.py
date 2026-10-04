# -*- coding: utf-8 -*-
"""Construct explicitly sourced fixture geometry and verify it in native Revit 2025."""
import os, sys, json, math, traceback, hashlib, datetime
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB
from System.Collections.Generic import List
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from native_plumbing_support import NativeFixture, xyz, loop, rounded_rect, measured_geometry_bounds

SECTION = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def circle(center,normal,radius):
    normal=normal.Normalize()
    u=DB.XYZ.BasisX if abs(normal.X)<.9 else DB.XYZ.BasisY
    u=u.Subtract(normal.Multiply(u.DotProduct(normal))).Normalize()
    v=normal.CrossProduct(u).Normalize()
    result=DB.CurveLoop()
    for i in range(4):
        result.Append(DB.Arc.Create(center,radius/12.,i*math.pi/2.,(i+1)*math.pi/2.,u,v))
    return result

def loft_profile(section):
    x,y,z=section.get('center',[0,0,section.get('z',0)])
    w,d=section['size']
    if section.get('shape')=='ellipse':
        result=DB.CurveLoop()
        for i in range(4):
            result.Append(DB.Ellipse.CreateCurve(xyz(x,y,z),w/24.,d/24.,DB.XYZ.BasisX,DB.XYZ.BasisY,i*math.pi/2.,(i+1)*math.pi/2.))
        return result
    r=section.get('radius',min(w,d)*.12)
    return loop(xyz(x,y,z),DB.XYZ.BasisX,DB.XYZ.BasisY,rounded_rect(-w/2.,-d/2.,w/2.,d/2.,r))

def create_solid(part):
    kind=part['kind']
    if kind=='box':
        x0,y0,z0,x1,y1,z1=part['bounds']
        radius=part.get('radius',0)
        points=rounded_rect(x0,y0,x1,y1,radius) if radius else [(x0,y0),(x1,y0),(x1,y1),(x0,y1)]
        profile=loop(xyz(0,0,z0),DB.XYZ.BasisX,DB.XYZ.BasisY,points)
        return DB.GeometryCreationUtilities.CreateExtrusionGeometry(List[DB.CurveLoop]([profile]),DB.XYZ.BasisZ,(z1-z0)/12.)
    if kind=='cut':
        result=create_solid(part['base'])
        for cutter in part['cutters']:
            result=DB.BooleanOperationsUtils.ExecuteBooleanOperation(result,create_solid(cutter),DB.BooleanOperationsType.Difference)
        return result
    if kind=='cylinder':
        origin=xyz(*part['origin']);axis=DB.XYZ(*part['axis']).Normalize()
        a=part.get('a',0);b=part['b'];radius=part['radius']
        start=origin.Add(axis.Multiply(a/12.))
        profile=circle(start,axis,radius)
        loops=List[DB.CurveLoop]([profile])
        if part.get('inner_radius'):
            loops.Add(circle(start,axis,part['inner_radius']))
        return DB.GeometryCreationUtilities.CreateExtrusionGeometry(loops,axis,(b-a)/12.)
    if kind=='sweep':
        points=part['path'];p=xyz(*points[0]);path=DB.CurveLoop();first=p
        for step in points[1:]:
            if step[0]=='arc':
                end=xyz(*step[2]);path.Append(DB.Arc.Create(p,end,xyz(*step[1])))
            else:
                end=xyz(*step);path.Append(DB.Line.CreateBound(p,end))
            p=end
        first_curve=list(path)[0]
        tangent=first_curve.ComputeDerivatives(first_curve.GetEndParameter(0),False).BasisX.Normalize()
        profile=circle(first,tangent,part.get('radius',.25))
        if part.get('oval'):
            u=DB.XYZ.BasisX if abs(tangent.X)<.9 else DB.XYZ.BasisY
            u=u.Subtract(tangent.Multiply(u.DotProduct(tangent))).Normalize();v=tangent.CrossProduct(u)
            profile=DB.CurveLoop()
            for i in range(4):profile.Append(DB.Ellipse.CreateCurve(first,part['oval'][0]/24.,part['oval'][1]/24.,u,v,i*math.pi/2.,(i+1)*math.pi/2.))
        return DB.GeometryCreationUtilities.CreateSweptGeometry(path,0,first_curve.GetEndParameter(0),List[DB.CurveLoop]([profile]))
    if kind in ['loft','shell']:
        options=DB.SolidOptions(DB.ElementId.InvalidElementId,DB.ElementId.InvalidElementId)
        profiles=List[DB.CurveLoop]([loft_profile(s) for s in part['sections']])
        outer=DB.GeometryCreationUtilities.CreateLoftGeometry(profiles,options)
        if kind=='loft':return outer
        inner=DB.GeometryCreationUtilities.CreateLoftGeometry(List[DB.CurveLoop]([loft_profile(s) for s in part['inner']]),options)
        return DB.BooleanOperationsUtils.ExecuteBooleanOperation(outer,inner,DB.BooleanOperationsType.Difference)
    if kind=='profile':
        profile=loop(xyz(*part.get('origin',[0,0,0])),DB.XYZ(*part['u']),DB.XYZ(*part['v']),part['points'])
        return DB.GeometryCreationUtilities.CreateExtrusionGeometry(List[DB.CurveLoop]([profile]),DB.XYZ(*part['normal']),part['length']/12.)
    raise ValueError('Unsupported solid kind: '+kind)

def build(key,app):
    out=os.path.join(SECTION,key)
    spec_path=os.path.join(out,'source','model_spec.json')
    raw=open(spec_path,'rb').read();spec=json.loads(raw)
    input_hash=hashlib.sha256(raw).hexdigest()
    f=None
    try:
        f=NativeFixture(app,out,spec['basename'],spec['manufacturer'],spec['model'],spec['type_name'],spec['host'],spec['configured_dimensions_in'])
        f.report.update(source_spec_path=spec_path,source_spec_sha256=input_hash,source_references=spec['sources'],
                        source_dimensions=spec.get('dimension_authority',[]),limitations=spec.get('limitations',[]),
                        rfa_search=spec.get('rfa_search'),acceptance='UNREVIEWED')
        f.note(' | '.join(spec.get('limitations',[])))
        materials={}
        used=set(p.get('material','Finish') for p in spec['geometry'])
        for label in sorted(used):
            m=spec['materials'][label]
            materials[label]=f.material(label,tuple(m['rgb']),m.get('gloss',.3),m.get('transparency',0),m.get('reflectivity',.15),material_class=m.get('class','Metal'))
        by_name={}
        for p in spec['geometry']:
            material=materials[p.get('material','Finish')]
            kind=p['kind']
            if kind=='box':
                e=f.box(p['name'],*(p['bounds']+[material,p.get('radius',0)]))
            elif kind=='revolve':
                e=f.revolve(p['name'],xyz(*p['origin']),DB.XYZ(*p['axis']),p['profile'],material)
            else:
                e=f.add(p['name'],create_solid(p),material)
            by_name[p['name']]=e
        f.doc.Regenerate()
        f.report['native_path_checks']=[]
        for check in spec.get('native_path_checks',[]):
            part=next(p for p in spec['geometry'] if p['name']==check['part'])
            current=xyz(*part['path'][0]);length=0.0
            for step in part['path'][1:]:
                if step[0]=='arc':
                    endpoint=xyz(*step[2]);curve=DB.Arc.Create(current,endpoint,xyz(*step[1]))
                else:
                    endpoint=xyz(*step);curve=DB.Line.CreateBound(current,endpoint)
                length+=curve.Length*12.0;current=endpoint
            f.report['native_path_checks'].append({'part':check['part'],'actual_mm':length*25.4,'nominal_mm':check['nominal_in']*25.4,
                                                  'pass':abs(length-check['nominal_in'])*25.4<=1.0})
        f.report['dimension_anchor_checks']=[]
        for anchor in spec.get('anchors',[]):
            bounds=measured_geometry_bounds([by_name[name] for name in anchor['parts']])
            axis=anchor['axis'];actual=bounds[axis+3]-bounds[axis]
            f.report['dimension_anchor_checks'].append({'label':anchor['label'],'actual_mm':actual*25.4,'nominal_mm':anchor['nominal_in']*25.4,
                                                       'deviation_mm':(actual-anchor['nominal_in'])*25.4,'pass':abs(actual-anchor['nominal_in'])*25.4<=1.0})
        result=f.finish()
        result['native_gates_pass']=result['technical_pass'] and all(a['pass'] for a in result['dimension_anchor_checks']) and all(a['pass'] for a in result['native_path_checks'])
        result['all_overall_dimensions_authoritative']=spec.get('all_overall_dimensions_authoritative',False)
        result['visual_review']='PENDING_NATIVE_IMAGE_REVIEW'
        result['acceptance']='NATIVE_GATES_PASSED_PENDING_VISUAL_REVIEW' if result['native_gates_pass'] else 'FAILED_NATIVE_GATES'
        with open(os.path.join(out,'validation.json'),'w') as handle:json.dump(result,handle,indent=2,default=str)
        return result
    except Exception:
        if f is not None:
            f.fail()
            return f.report
        result={'model':key,'stage':'factory_initialization_failed','technical_pass':False,'error':traceback.format_exc()}
        if not os.path.isdir(out):os.makedirs(out)
        with open(os.path.join(out,'validation.json'),'w') as handle:json.dump(result,handle,indent=2)
        return result

def run_queue(app):
    queue=json.load(open(os.path.join(SECTION,'_harness','build_queue.json')))
    report={'started_utc':datetime.datetime.utcnow().isoformat()+'Z','items':[]}
    for key in queue:
        result=build(key,app)
        report['items'].append({'key':key,'stage':result.get('stage'),'native_gates_pass':result.get('native_gates_pass',False),
                                'technical_pass':result.get('technical_pass',False),'rfa_path':result.get('rfa_path'),'error':result.get('error')})
        with open(os.path.join(SECTION,'_harness','batch_current.json'),'w') as handle:json.dump(report,handle,indent=2,default=str)
    report['finished_utc']=datetime.datetime.utcnow().isoformat()+'Z'
    with open(os.path.join(SECTION,'_harness','batch_current.json'),'w') as handle:json.dump(report,handle,indent=2,default=str)
    return report
