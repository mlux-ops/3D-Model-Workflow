# -*- coding: utf-8 -*-
import os,sys
sys.path.insert(0,os.path.abspath(os.path.join(os.path.dirname(__file__),"..","..","_harness")))
from family_factory import build
build('T84613-BNX_SH84103-BNX_R84100',__revit__.Application)
