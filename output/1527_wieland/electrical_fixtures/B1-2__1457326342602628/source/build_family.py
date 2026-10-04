# -*- coding: utf-8 -*-
import os,sys
ROOT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0,os.path.join(ROOT,'_tools'))
from build_catalog import run_one
run_one(__revit__.Application,'700TRSPPYL1RNB-LED930')
