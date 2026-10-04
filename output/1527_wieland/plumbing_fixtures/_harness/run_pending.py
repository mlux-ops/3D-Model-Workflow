# -*- coding: utf-8 -*-
import os,sys
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from family_factory import run_queue
run_queue(__revit__.Application)
