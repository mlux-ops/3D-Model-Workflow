# -*- coding: utf-8 -*-
"""Minka Lavery Vantage 759-2-66A-L, Coal 11 inch."""
import os,sys,json
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,os.path.join(ROOT,'tools'))
from native_fixture_support import NativeFixture,DB,xyz
OUT=os.path.dirname(os.path.abspath(__file__))
f=None
try:
    f=NativeFixture(__revit__.Application,OUT,'Minka_Vantage_759-2-66A-L_Coal_11_R2025','Minka Lavery','759-2-66A-L','Coal - 11 inch - 3000K','ceiling',[11.,11.,1.5],3000)
    coal=f.material('Coal Finish',(30,29,28),.25,0,.08)
    acrylic=f.material('Clear Acrylic Finish',(244,247,248),.94,.84,.04,0,None,'Glass')
    diffuse=f.material('Warm White Diffuser Finish',(250,246,232),.17,0,.025,85,3000,'Plastic')
    f.note('Exact requested11in Coal option is Lightology1418168 /759-2-66A-L, replacing generic-page7in option. Printed11W x1.5H,11in canopy x.63H,3000K. Photo shows clear acrylic drum/rim around flat luminous diffuser beneath a Coal cap. Acrylic wall/rim thickness, .06in edge rounds and hidden internal diffuser depth are inferred. No electrical or photometric source; appearance glow uses3000K.')
    f.cylinder('Coal ceiling canopy',xyz(),DB.XYZ.BasisZ,5.5,0,.63,coal,.06)
    f.revolve('Clear acrylic side and rolled lower edge',xyz(),DB.XYZ.BasisZ,[(5.25,.56),(5.47,.56),(5.47,1.40),('arc',(5.44071,1.47071),(5.37,1.5)),(5.25,1.5)],acrylic)
    f.cylinder('Continuous luminous diffuser',xyz(),DB.XYZ.BasisZ,5.25,.61,1.38,diffuse,.035)
    f.report['resolved_url']='https://www.lightology.com/index.php?module=prod_detail&prod_id=1418164&option_id=1418168'
    f.report['nominal_canopy_in']=[11.,.63]
    report=f.finish()
    with open(os.path.join(OUT,'validation.json'),'w') as stream:json.dump(report,stream,indent=2,default=str)
except Exception:
    if f is not None:f.fail()
    raise