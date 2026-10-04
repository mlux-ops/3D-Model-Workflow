import os,sys
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import build_completion,inspect_orion
build_completion.main(__revit__.Application)
inspect_orion.main(__revit__.Application)
