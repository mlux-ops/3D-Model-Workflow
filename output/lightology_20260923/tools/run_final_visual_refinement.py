# -*- coding: utf-8 -*-
import os,json,traceback
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for rel in ['f01_816712/build_f01_816712.py','f10_1242580/build_covet.py','tools/export_native_meshes.py']:
    path=os.path.join(ROOT,*rel.split('/'))
    execfile(path,{'__file__':path,'__name__':'__main__','__revit__':__revit__})
path=os.path.join(ROOT,'tools','final_native_review.py')
execfile(path,{'__file__':path,'__name__':'__main__','__revit__':__revit__,'REVIEW_KEYS':['f01','f10']})