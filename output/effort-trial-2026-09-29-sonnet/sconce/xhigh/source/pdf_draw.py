# -*- coding: utf-8 -*-
"""Render the exploded-assembly vector drawing from the install sheet page (streams 3..10) with PIL."""
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
    try:
        streams.append(zlib.decompress(data[s:e]))
    except Exception:
        pass
content = b'\n'.join(streams[3:11]).decode('latin-1')

TOK = re.compile(r"\((?:\\.|[^\\)])*\)|\[|\]|<<|>>|/[^\s\[\]()<>/]*|[-+]?(?:\d+\.?\d*|\.\d+)|[A-Za-z\*'\"]+")
tokens = TOK.findall(content)

SCALE = 3.0
PW, PH = 612.0, 792.0
img = Image.new('RGB', (int(PW * SCALE), int(PH * SCALE)), 'white')
d = ImageDraw.Draw(img)


def mmul(a, b):
    # a, b = (a,b,c,d,e,f); returns a x b (apply a first, then b)
    return (a[0] * b[0] + a[1] * b[2], a[0] * b[1] + a[1] * b[3],
            a[2] * b[0] + a[3] * b[2], a[2] * b[1] + a[3] * b[3],
            a[4] * b[0] + a[5] * b[2] + b[4], a[4] * b[1] + a[5] * b[3] + b[5])


def tf(m, x, y):
    return (m[0] * x + m[2] * y + m[4], m[1] * x + m[3] * y + m[5])


def px(p):
    return (p[0] * SCALE, (PH - p[1]) * SCALE)


ctm = (1, 0, 0, 1, 0, 0)
stack = []
lw = 1.0
stroke_col = (0, 0, 0)
fill_col = (170, 170, 170)
subs = []
cur = []
cp = (0, 0)
stack_nums = []
in_text = False
skipped = {}
paths_drawn = 0
REC = []
PTS = []


def flatten_c(p0, p1, p2, p3, n=12):
    out = []
    for i in range(1, n + 1):
        t = i / float(n)
        u = 1 - t
        out.append((u ** 3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t ** 3 * p3[0],
                    u ** 3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t ** 3 * p3[1]))
    return out


def paint(stroke, fill, close):
    global subs, cur, paths_drawn
    if cur:
        subs.append(cur)
    for sp in subs:
        pts = [px(p) for p in sp]
        if len(pts) < 2:
            continue
        if close and pts[0] != pts[-1]:
            pts.append(pts[0])
        if fill and len(pts) > 2:
            d.polygon(pts, fill=fill_col)
        if stroke:
            w = max(1, int(round(lw * ctm_scale() * SCALE)))
            d.line(pts, fill=stroke_col, width=w)
    allp = [q for sp in subs for q in sp]
    if allp:
        PTS.append([list(q) for q in allp]) if len(allp) >= 30 else None
        REC.append((min(q[0] for q in allp), min(q[1] for q in allp), max(q[0] for q in allp), max(q[1] for q in allp), len(allp), stroke, fill, lw * ctm_scale()))
    paths_drawn += 1
    subs = []
    cur = []


def ctm_scale():
    return (abs(ctm[0] * ctm[3] - ctm[1] * ctm[2])) ** 0.5


i = 0
nums = []
while i < len(tokens):
    t = tokens[i]
    i += 1
    if re.match(r'^[-+]?(?:\d+\.?\d*|\.\d+)$', t):
        nums.append(float(t))
        continue
    if t.startswith('(') or t.startswith('/') or t in ('[', ']', '<<', '>>'):
        nums = []
        continue
    op = t
    if op == 'BT':
        in_text = True
    elif op == 'ET':
        in_text = False
    elif in_text:
        pass
    elif op == 'q':
        stack.append((ctm, lw, stroke_col, fill_col))
    elif op == 'Q':
        if stack:
            ctm, lw, stroke_col, fill_col = stack.pop()
    elif op == 'cm' and len(nums) >= 6:
        ctm = mmul(tuple(nums[-6:]), ctm)
    elif op == 'w' and nums:
        lw = nums[-1]
    elif op == 'm' and len(nums) >= 2:
        if cur:
            subs.append(cur)
        cp = tf(ctm, nums[-2], nums[-1])
        cur = [cp]
    elif op == 'l' and len(nums) >= 2:
        cp = tf(ctm, nums[-2], nums[-1])
        cur.append(cp)
    elif op == 'c' and len(nums) >= 6:
        p1 = tf(ctm, nums[-6], nums[-5])
        p2 = tf(ctm, nums[-4], nums[-3])
        p3 = tf(ctm, nums[-2], nums[-1])
        cur.extend(flatten_c(cp, p1, p2, p3))
        cp = p3
    elif op == 're' and len(nums) >= 4:
        x, y, w, h = nums[-4:]
        if cur:
            subs.append(cur)
        cur = [tf(ctm, x, y), tf(ctm, x + w, y), tf(ctm, x + w, y + h), tf(ctm, x, y + h), tf(ctm, x, y)]
        cp = cur[0]
    elif op == 'h':
        if cur:
            cur.append(cur[0])
    elif op == 'S':
        paint(True, False, False)
    elif op == 's':
        paint(True, False, True)
    elif op in ('f', 'F', 'f*'):
        paint(False, True, True)
    elif op in ('B', 'B*'):
        paint(True, True, True)
    elif op in ('b', 'b*'):
        paint(True, True, True)
    elif op == 'n':
        subs = []
        cur = []
    elif op in ('W', 'W*'):
        pass
    elif op in ('k', 'K', 'g', 'G', 'rg', 'RG', 'gs', 'd', 'j', 'J', 'i', 'M', 'Tf', 'Tm', 'Td', 'Tj', 'TJ', 'Tc', 'Tw', 'TL', 'T*', 'Tz', 'Ts', 'Tr', 'Do', 'sh', 'cs', 'CS', 'sc', 'scn', 'SC', 'SCN', 'ri', 'BDC', 'EMC', 'BMC', 'MP', 'DP', 'BI', 'ID', 'EI'):
        pass
    else:
        skipped[op] = skipped.get(op, 0) + 1
    nums = []

print('paths', paths_drawn, 'skipped', skipped)
full = OUT + 'install_page1_full.png'
img.save(safe_path(full))
# crop the drawing region (page points): find ink bbox
import numpy as np
a = np.asarray(img.convert('L'))
ys, xs = np.nonzero(a < 200)
print('ink bbox px', xs.min(), xs.max(), ys.min(), ys.max(), ' pt x', xs.min() / SCALE, xs.max() / SCALE, ' y', PH - ys.max() / SCALE, PH - ys.min() / SCALE)

import json
open(safe_path(OUT + 'paths.json'), 'w').write(json.dumps(REC))
print('recorded', len(REC))

open(safe_path(OUT + 'points.json'), 'w').write(json.dumps(PTS))
