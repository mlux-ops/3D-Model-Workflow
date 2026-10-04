# Run this absolute script path through the shared revit_run.py only.
import os,sys
section=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0,section)
from build_custom import build_one
build_one('summit_sdhwc98pnr', __revit__.Application)
