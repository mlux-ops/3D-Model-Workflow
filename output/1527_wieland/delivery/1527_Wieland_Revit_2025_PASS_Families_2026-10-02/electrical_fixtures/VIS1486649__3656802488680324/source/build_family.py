import os,sys
OUT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,os.path.join(os.path.dirname(OUT),'_tools'))
from build_completion import run_one
run_one(__revit__.Application,'VIS1486649')
