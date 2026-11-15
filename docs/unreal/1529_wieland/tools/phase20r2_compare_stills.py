"""Phase 20 round 2: each still beside round 1's (review/phase20/stills -> review/phase20/round2/stills).

Usage:  python -B phase20r2_compare_stills.py
Writes review/phase20/round2/stills/compare_<view>_realtime.jpg and compare_D1_pathtraced.jpg (round 1 left,
round 2 right, 1,600 px each) and prints the share of pixels whose brightness changed by more than 10 levels.
"""
import os

import numpy as np
from PIL import Image

DOCS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R1 = os.path.join(DOCS, 'review', 'phase20', 'stills')
R2 = os.path.join(DOCS, 'review', 'phase20', 'round2', 'stills')
VIEWS = ['S1', 'S2', 'S3', 'S4', 'S5', 'S6', 'S9', 'D1', 'D2', 'D3', 'D4', 'D5']


def one(name):
    a = Image.open(os.path.join(R1, name + '.0000.png')).convert('RGB')
    b = Image.open(os.path.join(R2, name + '.0000.png')).convert('RGB')
    la = np.asarray(a.convert('L'), dtype=np.int16)
    lb = np.asarray(b.convert('L').resize(a.size), dtype=np.int16)
    share = float((np.abs(la - lb) > 10).mean())
    w = 1600
    a2 = a.resize((w, int(a.size[1] * w / a.size[0])))
    b2 = b.resize((w, int(b.size[1] * w / b.size[0])))
    out = Image.new('RGB', (2 * w + 10, a2.size[1]), (255, 255, 255))
    out.paste(a2, (0, 0))
    out.paste(b2, (w + 10, 0))
    out.save(os.path.join(R2, 'compare_%s.jpg' % name.replace('.0000', '')), quality=88)
    return share


if __name__ == '__main__':
    for v in VIEWS:
        print(v, 'realtime changed share %.3f' % one(v + '_realtime'))
    if os.path.exists(os.path.join(R2, 'D1_pathtraced.0000.png')):
        print('D1 pathtraced changed share %.3f' % one('D1_pathtraced'))
    else:
        print('D1 pathtraced: no round-2 picture')
