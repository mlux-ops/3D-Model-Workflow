import os,sys
OUT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,os.path.join(os.path.dirname(OUT),'_tools'))
from build_remaining import run_one
run_one(__revit__.Application,'4BEMW_SWW5_90CRI_M6')
