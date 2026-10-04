# -*- coding: utf-8 -*-
import os, sys
OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(OUT), '_tools'))
from wieland_native import build_maxim
build_maxim(__revit__.Application, OUT)
