import os,sys
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import build_remaining,inspect_orion
build_remaining.main(__revit__.Application)
inspect_orion.main(__revit__.Application)
