"""Phase 13: one expression against the editor modules wieland_hotel (as wh) and wieland_site (as ws), both
reloaded so that edits to the files count. The expression's value comes back as text.

Usage, from the plan folder: python -B review/phase13/scripts/wh.py "<expression>" [timeout seconds]
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(HERE))), "tools").replace(os.sep, "/")
source = ("import sys\nimport importlib\nsys.dont_write_bytecode = True\n"
          "TOOLS = %r\nif TOOLS not in sys.path:\n    sys.path.insert(0, TOOLS)\n"
          "import wieland_site as ws\nimportlib.reload(ws)\n"
          "import wieland_hotel as wh\nimportlib.reload(wh)\n" % TOOLS) + sys.argv[1] + "\n"
timeout = sys.argv[2] if len(sys.argv) > 2 else "300"
sys.exit(subprocess.call([sys.executable, "-B", os.path.join(TOOLS, "ue_call.py"), "pyc", source, timeout]))
