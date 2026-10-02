# -*- coding: utf-8 -*-
"""Tiny vector renderer for the install-sheet drawing (no PDF rasterizer on this machine).

Handles the path operators q Q cm w m l c re h S s f F f* B b n, plus rg/RG/g/G colours, and prints
what it skips. Output goes to xhigh/work/pdf/.
"""
import os
import re
import sys
import zlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from guard import safe_path
from PIL import Image, ImageDraw

IN = 'E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce/inputs/KW1041_install_instructions_20230426.pdf'
OUT = 'E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce/xhigh/work/pdf/'
os.makedirs(OUT, exist_ok=True)

data = open(IN, 'rb').read()
streams = []
for m in re.finditer(rb'stream\r?\n', data):
    s = m.end()
    e = data.find(b'endstream', s)
    raw = data[s:e]
    try:
        txt = zlib.decompress(raw)
    except Exception:
        continue
    streams.append(txt)
print('decoded streams', len(streams), [len(x) for x in streams])
for i, s in enumerate(streams):
    head = s[:120].replace(b'\n', b' ')
    print(i, len(s), head)
    open(safe_path(OUT + 'stream%02d.txt' % i), 'wb').write(s)
