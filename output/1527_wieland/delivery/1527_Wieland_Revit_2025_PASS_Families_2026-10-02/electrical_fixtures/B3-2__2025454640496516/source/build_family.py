# -*- coding: utf-8 -*-
import os, sys
OUT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,os.path.join(os.path.dirname(OUT),'_tools'))
from rebuild_from_source import run_one
run_one(__revit__.Application, 'AST1561665')
