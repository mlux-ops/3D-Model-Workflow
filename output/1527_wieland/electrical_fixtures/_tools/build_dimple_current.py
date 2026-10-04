# -*- coding: utf-8 -*-
"""Current S1 Dimple reconstruction from previously inspected native profiles."""
import os,sys,json,traceback
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,os.path.join(ROOT,'_tools'))
from wieland_native import WielandFixture, DB, xyz
OUT=os.path.join(ROOT,'B2-2__5960925969973124')
b=None
try:
    b=WielandFixture(__revit__.Application,OUT,'RBW_Dimple_S1_AA04_White_Interior_R2025',
                     'RBW','DP-WS-S1-AA04-30-10_TRIAC_120V-IP65','S1 White Interior - Black Anodized','wall',[5.,5.,3.3])
    metal=b.material('Black Backplate Finish',(24,24,24),.28)
    glass=b.material('Clear Glass Finish',(245,247,248),.98,.88,.06,0,None,'Glass')
    diffuser=b.material('White Interior Finish',(249,249,245),.20,0,.025,0,None,'Glass')
    b.cylinder('Black anodized wall plate',xyz(),DB.XYZ.BasisZ,2.29,0,.62,metal,.07)
    profile=[(2.18,.57),(2.32,.57),('arc',(2.447279,.622721),(2.5,.75)),(2.5,2.88),
             ('arc',(2.376985,3.176985),(2.08,3.30)),('arc',(1.04,2.904),(0,2.78)),
             (0,2.51),('arc',(1.0,2.63),(1.96,3.05)),('arc',(2.18,2.95),(2.22,2.60)),(2.22,1.12),(2.18,.57)]
    b.revolve('Cast glass concave lens with rolled rim',xyz(),DB.XYZ.BasisZ,profile,glass)
    inner=[(0,.66),(2.10,.66),('arc',(2.15,.9),(2.15,1.2)),(2.15,2.08),
           ('arc',(1.88,2.29),(1.55,2.35)),('arc',(.78,2.42),(0,2.45))]
    b.revolve('White interior optical body',xyz(),DB.XYZ.BasisZ,inner,diffuser)
    b.note('Current S1 black anodized/white interior SKU; 5-inch diameter x 3.3-inch projection. '
           'Concave front, rolled rim and separate interior follow saved product photos and the prior native Dimple profile builder. '
           'ASSUMPTION: glass thickness, backplate diameter, internal optics and exact dimple curvature. '
           'Older public manufacturer 305-D-FM RFA was rejected as an exact match and retained in source. Fixed product geometry; three editable material finishes.')
    b.report['source_url']='https://rbw.com/products/dimple-sconce/dimple-sconce'
    b.report['profile_source']='output/lightology_20260923/f05_1441643/build_dimple.py'
    b.report['rfa_search']='Manufacturer public RFA downloaded; old SKU/dimensions and missing Fine-detail lens solids prevented exact-current release. Independent native reconstruction used.'
    b.finish()
except Exception:
    if b is not None:
        b.fail()
        with open(os.path.join(OUT,'validation.json'),'w') as f:json.dump(b.report,f,indent=2,default=str)
    raise
