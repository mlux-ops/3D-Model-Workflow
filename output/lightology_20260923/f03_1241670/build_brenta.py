# -*- coding: utf-8 -*-
"""Brenta source-measured visual correction, preserving nominal envelope."""
import os,sys,json,math
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,os.path.join(ROOT,'tools'))
from native_fixture_support import NativeFixture, DB, xyz
OUT=os.path.dirname(os.path.abspath(__file__))
f=None
try:
    f=NativeFixture(__revit__.Application,OUT,'AERIN_Brenta_ARN2473BZ-CG_Bronze_R2025','Visual Comfort Signature / AERIN','ARN2473BZ-CG','Bronze - White Glass - 2700K','wall',[3.5,18.5,3.75],2700)
    bronze=f.material('Bronze Finish',(61,49,39),.42,0,.23)
    glass=f.material('Clear Glass Finish',(244,246,242),.90,.86,.04,0,None,'Glass')
    diffuser=f.material('2700K Diffuser Finish',(249,239,219),.18,0,.025,100,2700,'Glass')
    f.note('Published3.5W x18.5H x3.75projection and3.5x5.25plate govern. Official product photograph and dimension drawing show subtly flared glass and inner diffuser, not straight cylinders. Manufacturer RFA supports glass2.024OD,inner1.347OD x17.237long,central sleeve1.914OD x3.611H. Plate thickness.875in and conical wall thickness.085in are source-informed inferences. Native smooth reconstruction preserves printed nominal dimensions over slight source-RFA oversize; endcaps and small rounding inferred. Face host supports rotating horizontal/vertical installation.')
    f.length('Backplate Width',3.5);f.length('Backplate Height',5.25)
    f.box('Raised rectangular bronze backplate',-1.75,-2.625,0,1.75,2.625,.875,bronze,.045)
    f.box('Short mounting standoff',-.56,-1.24,.875,.56,1.24,1.87,bronze,.045)
    axis_offset=3.75-1.012
    f.cylinder('Bronze central sleeve',xyz(0,0,axis_offset),DB.XYZ.BasisY,.957,-1.8055,1.8055,bronze,.05)
    for label,sign in [('Upper',1),('Lower',-1)]:
        axis=DB.XYZ(0,sign,0)
        # A closed-end clear shell; optical center is hollow around the diffuser.
        profile=[(.825,1.70),(.91,1.70),(1.012,9.215),('arc',(1.00175,9.23975),(.977,9.25)),
                 (0,9.25),(0,9.165),(.925,9.165),(.825,1.70)]
        f.revolve(label+' subtly flared clear glass shell',xyz(0,0,axis_offset),axis,profile,glass)
        inner=[(0,1.68),(.56,1.68),(.6735,8.5585),('arc',(.65593,8.60093),(.6135,8.6185)),(0,8.6185)]
        f.revolve(label+' tapered warm white inner diffuser',xyz(0,0,axis_offset),axis,inner,diffuser)
    f.report['source_measurements_file']='source_geometry_measurements.json'
    f.report['source_review_file']='SOURCE_REVIEW.md'
    f.report['resolved_bronze_url']='https://www.lightology.com/index.php?module=prod_detail&prod_id=1241670&option_id=1241668'
    f.report['source_informed_sizes_in']={'glass_end_diameter':2.024,'glass_neck_diameter':1.82,'diffuser_end_diameter':1.347,'diffuser_total_length':17.237,'sleeve_diameter':1.914,'sleeve_height':3.611,'backplate_projection_inferred':.875}
    report=f.finish()
    with open(os.path.join(OUT,'validation.json'),'w') as s:json.dump(report,s,indent=2,default=str)
except Exception:
    if f is not None:f.fail()
    raise