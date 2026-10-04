# -*- coding: utf-8 -*-
import os,sys
sys.path.insert(0,os.path.abspath(os.path.join(os.path.dirname(__file__),"..","..","_harness")))
from family_factory import build
build('BT062415-BNX',__revit__.Application)
