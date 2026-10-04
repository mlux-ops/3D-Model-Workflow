# -*- coding: utf-8 -*-
"""One serialized native session for Orion and unchanged-file visual evidence."""
import os,sys,imp,json,traceback
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,os.path.join(ROOT,'_tools'))
OUT=os.path.join(ROOT,'Best_option_-_Orion_Tube_Pendant__1967952628416388')
vp=os.path.join(OUT,'validation.json')
try:
    existing=json.load(open(vp)) if os.path.isfile(vp) else {}
    if not existing.get('technical_pass'):
        module=imp.load_source('orion_final_build',os.path.join(OUT,'source','build_family.py'))
        module.main(__revit__.Application)
except Exception:
    with open(os.path.join(ROOT,'ORION_BUILD_ERROR.txt'),'w') as stream:stream.write(traceback.format_exc())
from export_geometry_review import main
main(__revit__.Application)
