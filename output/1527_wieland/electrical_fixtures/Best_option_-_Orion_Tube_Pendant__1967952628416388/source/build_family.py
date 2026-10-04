# -*- coding: utf-8 -*-
"""Build current Orion through the shared revit_run.py harness only."""
import os,sys,json,traceback,math
OUT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,os.path.join(os.path.dirname(OUT),'_tools'))
from wieland_native import WielandFixture,DB,xyz
from native_fixture_support import sphere_solid
from System.Collections.Generic import List

def cable(f,label,x,r,start,end,material):
    # Circular arcs avoid a sub-tolerance radial closing edge of a revolve.
    ring=DB.CurveLoop()
    center=xyz(x,0,start)
    ring.Append(DB.Arc.Create(center,r/12.,0,math.pi,DB.XYZ.BasisX,DB.XYZ.BasisY))
    ring.Append(DB.Arc.Create(center,r/12.,math.pi,2*math.pi,DB.XYZ.BasisX,DB.XYZ.BasisY))
    solid=DB.GeometryCreationUtilities.CreateExtrusionGeometry(List[DB.CurveLoop]([ring]),DB.XYZ.BasisZ,(end-start)/12.)
    return f.add(label,solid,material)

def main(app):
    job=json.load(open(os.path.join(OUT,'source','orion_definition.json')))
    f=None
    try:
        f=WielandFixture(app,OUT,job['name'],job['manufacturer'],job['model'],job['model'],job['host'],job['dimensions'])
        materials={}
        for entry in job['materials']:
            data=dict(entry);label=data.pop('label');materials[label]=f.material(label,**data)
        metal=materials['Metal Finish'];opal=materials['Opal Tube Finish']
        body_z=48.-5.125/2.;left=-34.5/2.;right=34.5/2.
        globe_x=left+34.5*.25
        globe=f.add('Off-center polished metal globe',sphere_solid(xyz(globe_x,0,body_z),5.125/2.),metal)
        tube=f.cylinder('Continuous opal acrylic tube',xyz(0,0,body_z),DB.XYZ.BasisX,15./25.4,left,right,opal)
        f.check_component('Current US fixture body',[globe,tube],job['body_dimensions'],'EN 0626rev21 US page 2, 34.5 by 5.125 inches')
        f.check_component('Polished metal globe',[globe],[5.125,5.125,5.125],'EN 0626rev21 US page 2')
        for index,x in enumerate([left,right]):
            canopy=f.cylinder('Mini canopy %d'%(index+1),xyz(x,0,0),DB.XYZ.BasisZ,1.625/2.,0,.625,metal,.06)
            f.check_component('Mini canopy %d'%(index+1),[canopy],[1.625,1.625,.625],'EN 0626rev21 US page 2, printed inch dimensions')
            cord=materials['Clear Cord Finish'] if index==0 else materials['Tensile Wire Finish']
            cable(f,'Electrical cord' if index==0 else 'Steel tensile wire',x,.036 if index==0 else .023,.625,body_z,cord)
            a,b=(left,left+.12) if index==0 else (right-.12,right)
            f.cylinder('Small polished end ferrule %d'%(index+1),xyz(0,0,body_z),DB.XYZ.BasisX,15./25.4,a,b,metal)
        f.note(job['notes'])
        f.report.update(source_url=job['source_url'],source_spec_page=2,limitations=job['notes'],
            needs_user=['NEEDS_USER_ORION_CONFIGURATION'],
            rfa_search='Anonymous manufacturer Orion-1.zip passed CRC and source RFA opened/upgraded from 2019. Imported Generic Models geometry has no finish parameters and differs from current dimensional sheet; replaced with native face-based dimensioned geometry. Original source retained.',
            body_dimensions_basis='US printed inch dimensions control; metric equivalents are rounded.',
            source_review='source/SOURCE_REVIEW.md')
        f.finish()
    except Exception:
        if f:
            f.fail()
            with open(os.path.join(OUT,'validation.json'),'w') as stream:json.dump(f.report,stream,indent=2,default=str)
        raise

if __name__=='__main__':main(__revit__.Application)
