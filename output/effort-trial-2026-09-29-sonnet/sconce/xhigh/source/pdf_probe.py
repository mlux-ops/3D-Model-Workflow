# -*- coding: utf-8 -*-
"""Probe PDFs (no rasterizer on PATH): list objects, extract embedded JPEG/Flate images."""
import os
import re
import sys
import zlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from guard import safe_path

IN = 'E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce/inputs/'
OUT = 'E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce/xhigh/work/pdf/'
os.makedirs(OUT, exist_ok=True)

for name in ['KW1041_install_instructions_20230426.pdf', '833918_lightology_spec_sheet.pdf']:
    data = open(IN + name, 'rb').read()
    print(name, len(data), 'bytes')
    print('  /Type /Page count:', len(re.findall(rb'/Type\s*/Page[^s]', data)))
    print('  Images:', len(re.findall(rb'/Subtype\s*/Image', data)))
    print('  DCTDecode:', data.count(b'DCTDecode'), ' FlateDecode:', data.count(b'FlateDecode'))
    print('  Forms:', len(re.findall(rb'/Subtype\s*/Form', data)))
    # dump every JPEG stream
    n = 0
    for m in re.finditer(rb'\xff\xd8\xff', data):
        s = m.start()
        e = data.find(b'\xff\xd9', s)
        if e > s + 2000:
            fn = OUT + os.path.splitext(name)[0] + '_jpg%d.jpg' % n
            open(safe_path(fn), 'wb').write(data[s:e + 2])
            print('  wrote', fn, e - s)
            n += 1
    # look at the image dictionaries
    for m in re.finditer(rb'<<[^>]*?/Subtype\s*/Image[^>]*?>>', data, re.S):
        print('  IMG DICT:', m.group(0)[:300].replace(b'\n', b' '))
