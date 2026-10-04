# -*- coding: utf-8 -*-
import os,sys
sys.path.insert(0,os.path.abspath(os.path.join(os.path.dirname(__file__),"..","..","_harness")))
from family_factory import build
build('81392-BNX-2.5',__revit__.Application)
