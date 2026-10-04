# -*- coding: utf-8 -*-
import os
HERE=os.path.dirname(os.path.abspath(__file__))
for filename in ['inspect_assets_upgrade_oem.py','inspect_oem_families.py']:
    path=os.path.join(HERE,filename)
    execfile(path,{'__file__':path,'__name__':'__main__','__revit__':__revit__})
