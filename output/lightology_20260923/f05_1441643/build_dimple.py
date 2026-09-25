# -*- coding: utf-8 -*-
"""RBW Dimple, two user-selected 3000 K black-anodized variants."""
import os,sys,json
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,os.path.join(ROOT,'tools'))
from native_fixture_support import NativeFixture, DB, xyz
OUT=os.path.dirname(os.path.abspath(__file__))
reports=[]
for variant,sku in [('White_Interior','DP-WS-S1-AA04-30-10_TRIAC_120V-IP65'),('Amber','DP-WS-S3-AA04-30-10_TRIAC_120V-IP65')]:
    builder=None
    try:
        name='RBW_Dimple_Black_Anodized_'+variant+'_3000K_R2025'
        builder=NativeFixture(__revit__.Application,OUT,name,'RBW',sku,'Black Anodized - '+variant.replace('_',' ')+' - 3000 K','wall',[5.,5.,3.3],3000)
        metal=builder.material('Black Anodized Finish',(24,25,26),.28,0,.1)
        clear=builder.material('Cast Glass Finish',(238,244,245) if variant=='White_Interior' else (192,112,35),.98,.88 if variant=='White_Interior' else .65,.06,0,None,'Glass')
        diffuser=builder.material('Interior Diffuser Finish',(246,243,235) if variant=='White_Interior' else (255,224,159),.20,0,.025,70,3000,'Glass')
        builder.note('Lightology specifies 5 in diameter and 3.3 in projection, black anodized aluminum, cast glass and 3000 K. White S1 and amber S3 IP65 variants follow the user selections. Concave front/rolled rim and separate inner diffuser are reconstructed from saved photographs. Backplate diameter, lens thickness, internal optics and dimple curvature are inferred. Material glow is an appearance aid, not photometric output.')
        builder.cylinder('Black anodized wall plate',xyz(),DB.XYZ.BasisZ,2.29,0,.62,metal,.07)
        profile=[(2.18,.57),(2.32,.57),('arc',(2.447279,.622721),(2.5,.75)),(2.5,2.88),
                 ('arc',(2.376985,3.176985),(2.08,3.30)),('arc',(1.04,2.904),(0,2.78)),
                 (0,2.51),('arc',(1.0,2.63),(1.96,3.05)),('arc',(2.18,2.95),(2.22,2.60)),(2.22,1.12),(2.18,.57)]
        builder.revolve('Cast glass concave lens with rolled rim',xyz(),DB.XYZ.BasisZ,profile,clear)
        inner=[(0,.66),(2.10,.66),('arc',(2.15,.9),(2.15,1.2)),(2.15,2.08),
               ('arc',(1.88,2.29),(1.55,2.35)),('arc',(.78,2.42),(0,2.45))]
        builder.revolve('Luminous inner optical body',xyz(),DB.XYZ.BasisZ,inner,diffuser)
        reports.append(builder.finish())
    except Exception:
        if builder is not None:builder.fail()
        raise
with open(os.path.join(OUT,'validation.json'),'w') as stream:
    json.dump({'technical_pass':all(r['technical_pass'] for r in reports),'stage':'complete','variants':reports},stream,indent=2,default=str)