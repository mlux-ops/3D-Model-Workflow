# -*- coding: utf-8 -*-
"""Make <=800 px thumbnails of the inputs into xhigh/work/thumbs (image work outside Revit)."""
import os
import sys
import glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from guard import safe_path
from PIL import Image

IN = 'E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce/inputs'
OUT = 'E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce/xhigh/work/thumbs'
if not os.path.isdir(OUT):
    os.makedirs(OUT)

for f in sorted(glob.glob(IN + '/*.jpg') + glob.glob(IN + '/*.png')):
    im = Image.open(f).convert('RGB')
    im.thumbnail((780, 780), Image.LANCZOS)
    dst = os.path.join(OUT, os.path.splitext(os.path.basename(f))[0] + '_t.png')
    im.save(safe_path(dst))
    print(dst, im.size)
