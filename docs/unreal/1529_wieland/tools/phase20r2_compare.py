"""Phase 20 round 2: the round-2 panorama sheets beside round 1's, and beside the two licensed skyline photographs.

Usage:  python -B phase20r2_compare.py
Writes review/phase20/round2/panorama/compare_<deck>_r1_r2.jpg (round 1 above round 2, 3,200 px wide; share of
pixels whose brightness changed by more than 10 levels printed) and, outside the repository because it holds
other people's photographs, E:/Wieland1529_site_data/phase20/round2/sheets/skyline_beside_photos_r2.jpg (the
round-2 D1S sheet above round 1's sheet with the 2023 and 2014 North Avenue Beach photographs, J7).
"""
import os
import numpy as np
from PIL import Image

DOCS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R1 = os.path.join(DOCS, 'review', 'phase20', 'panorama')
R2 = os.path.join(DOCS, 'review', 'phase20', 'round2', 'panorama')
W = 3200


def fit(im):
    return im.resize((W, int(im.size[1] * W / im.size[0])))


for deck in ('D1', 'D1S'):
    a = Image.open(os.path.join(R1, '%s_panorama_sheet_p20.png' % deck)).convert('RGB')
    b = Image.open(os.path.join(R2, '%s_panorama_sheet_r2.png' % deck)).convert('RGB')
    # brightness change over the frames only (round 2 has a 260 px label band on top, round 1 none)
    fa = np.asarray(a.crop((0, 0, a.size[0], 1080)).convert('L'), dtype=np.int16)
    fb = np.asarray(b.crop((0, 260, b.size[0], 1340)).convert('L'), dtype=np.int16)
    share = float((np.abs(fa - fb) > 10).mean())
    a, b = fit(a), fit(b)
    out = Image.new('RGB', (W, a.size[1] + b.size[1] + 10), (255, 255, 255))
    out.paste(a, (0, 0))
    out.paste(b, (0, a.size[1] + 10))
    out.save(os.path.join(R2, 'compare_%s_r1_r2.jpg' % deck), quality=88)
    print(deck, 'changed share %.3f' % share)
photos = 'E:/Wieland1529_site_data/phase20/sheets/skyline_beside_photos.jpg'
if os.path.exists(photos):
    p = fit(Image.open(photos).convert('RGB'))
    b = fit(Image.open(os.path.join(R2, 'D1S_panorama_sheet_r2.png')).convert('RGB'))
    out = Image.new('RGB', (W, p.size[1] + b.size[1] + 10), (255, 255, 255))
    out.paste(b, (0, 0))
    out.paste(p, (0, b.size[1] + 10))
    os.makedirs('E:/Wieland1529_site_data/phase20/round2/sheets', exist_ok=True)
    out.save('E:/Wieland1529_site_data/phase20/round2/sheets/skyline_beside_photos_r2.jpg', quality=88)
    print('beside photos written')
