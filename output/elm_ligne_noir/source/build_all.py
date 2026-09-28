"""Rebuild everything from references/ in order; stops at the first failing step."""
import subprocess
import sys
import os

HERE = os.path.dirname(os.path.abspath(__file__))
STEPS = ["a00_thumbs.py", "a01_pdf_images.py", "a02_measure.py", "b01_build.py", "b02_previews.py",
         "b03_verify.py", "e01_model_pattern.py", ["b01_build.py", "charcoal"], "d01_package.py"]

for s in STEPS:
    args = s if isinstance(s, list) else [s]
    print("==>", " ".join(args), flush=True)
    r = subprocess.run([sys.executable, os.path.join(HERE, args[0])] + args[1:], cwd=HERE)
    if r.returncode != 0:
        sys.exit("step failed: %s (exit %d)" % (s, r.returncode))
