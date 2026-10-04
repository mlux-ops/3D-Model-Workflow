# -*- coding: utf-8 -*-
import os, sys
section=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0,os.path.join(section,'rework_round1'))
from native_rebuild import build_one
build_one('miele_kwtus7172f',__revit__.Application)
