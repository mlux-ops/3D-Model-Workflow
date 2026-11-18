"""Phase 20 round 2: the labelled roof-deck panorama sheets with all 27 landmarks of the owner's sheet.

Usage:  python -B phase20r2_panorama_sheet.py <deck D1|D1S>

Pastes the five frames of review/phase20/round2/panorama/ (yaw -90 to +30, left = east) and marks each of the
27 landmarks at its modelled tip (and a tick at its main roof), with the sheet's number and name, using the
model's positions from review/phase20/round2/landmarks.csv (roof centre, roof and tip heights; Two Prudential's
tip is its added spire). Writes <deck>_panorama_sheet_r2.png, <deck>_panorama_sheet_r2_labels.json, and
<deck>_landmark_crops_r2.png (one 240 px crop per landmark around its tip and roof, for judging what is seen).
"""
import csv
import json
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from phase17_panorama import project  # noqa: E402

DOCS = os.path.dirname(HERE)
PANO = os.path.join(DOCS, 'review', 'phase20', 'round2', 'panorama')
EYES = {'D1': (-1300.0, -1560.0, 1684.0), 'D1S': (-208.8, -1560.0, 1684.0)}
SPIRE_TOP = {'869122': 29047.0}   # Two Prudential's spire (tools/phase20r2_spire.py)


def frames_of(deck):
    recs = {}
    for line in open(os.path.join(PANO, 'frames.jsonl'), encoding='utf-8'):
        r = json.loads(line)
        if r['deck'] == deck:
            recs[r['yaw']] = r
    return [recs[y] for y in sorted(recs)]


def main(deck):
    eye = EYES[deck]
    frames = frames_of(deck)
    ims = [Image.open(os.path.join(PANO, os.path.basename(f['image']))).convert('RGB') for f in frames]
    W, H = ims[0].size
    top_band, strip = 260, 50
    sheet = Image.new('RGB', (W * len(ims), H + top_band + strip), (255, 255, 255))
    draw = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype('arial.ttf', 22)
        small = ImageFont.truetype('arial.ttf', 18)
    except OSError:
        font = small = ImageFont.load_default()
    for i, (f, im) in enumerate(zip(frames, ims)):
        sheet.paste(im, (i * W, top_band))
        draw.text((i * W + 10, top_band + H + 12), '%s  yaw %.0f deg, pitch %.0f deg, horizontal field %.0f deg' % (deck, f['yaw'], f['pitch'], f['fov']),
                  fill=(0, 0, 0), font=small)
    rows = list(csv.DictReader(open(os.path.join(DOCS, 'review', 'phase20', 'round2', 'landmarks.csv'), encoding='utf-8')))
    labels, crops = [], []
    lanes = []
    for r in sorted(rows, key=lambda r: float(r['model_bearing'])):
        cx, cy = float(r['roof_cx_cm']), float(r['roof_cy_cm'])
        tip_z = SPIRE_TOP.get(r['county_id'], float(r['model_tip_z_cm']))
        roof_z = float(r['model_roof_z_cm'])
        placed = None
        for i, f in enumerate(frames):
            pt = project(eye, f['yaw'], f['pitch'], f['fov'], W, H, (cx, cy, tip_z))
            pr = project(eye, f['yaw'], f['pitch'], f['fov'], W, H, (cx, cy, roof_z))
            if pt is not None and 0 <= pt[0] < W and pr is not None:
                placed = (i, pt, pr)
                break
        if placed is None:
            labels.append({'no': r['no'], 'landmark': r['landmark'], 'frame': None})
            continue
        i, pt, pr = placed
        x, y = i * W + pt[0], top_band + pt[1]
        xr, yr = i * W + pr[0], top_band + pr[1]
        text = '%s %s' % (r['no'], r['landmark'].replace(' (Hancock)', '').replace('Trump International Hotel & Tower', 'Trump Tower')[:30])
        tw = draw.textlength(text, font=font)
        lane = 0
        while any(abs(x - lx) < (tw + lw) / 2 + 6 and ln == lane for lx, lw, ln in lanes):
            lane += 1
        lanes.append((x, tw, lane))
        ty = 8 + (lane % 8) * 30
        draw.line([(x, ty + 26), (x, y - 4)], fill=(200, 30, 30), width=2)
        draw.ellipse([x - 5, y - 5, x + 5, y + 5], outline=(200, 30, 30), width=2)
        draw.line([(xr - 8, yr), (xr + 8, yr)], fill=(255, 200, 0), width=3)
        draw.text((x - tw / 2, ty), text, fill=(150, 0, 0), font=font)
        labels.append({'no': r['no'], 'landmark': r['landmark'], 'county_id': r['county_id'], 'frame': i + 1,
                       'u_tip': round(pt[0], 1), 'v_tip': round(pt[1], 1), 'u_roof': round(pr[0], 1), 'v_roof': round(pr[1], 1)})
        c = ims[i].crop((int(pt[0]) - 120, int(min(pt[1], pr[1])) - 40, int(pt[0]) + 120, int(max(pt[1], pr[1])) + 200))
        crops.append((r['no'], r['landmark'], c.resize((240, 240))))
    out = os.path.join(PANO, '%s_panorama_sheet_r2.png' % deck)
    sheet.save(out)
    json.dump(labels, open(out.replace('.png', '_labels.json'), 'w', encoding='utf-8'), indent=1)
    cols = 9
    grid = Image.new('RGB', (cols * 250, ((len(crops) + cols - 1) // cols) * 275), (255, 255, 255))
    gd = ImageDraw.Draw(grid)
    for k, (no, name, c) in enumerate(crops):
        gx, gy = (k % cols) * 250, (k // cols) * 275
        grid.paste(c, (gx + 5, gy + 30))
        gd.text((gx + 5, gy + 5), '%s %s' % (no, name[:24]), fill=(0, 0, 0), font=small)
    grid.save(os.path.join(PANO, '%s_landmark_crops_r2.png' % deck))
    print(deck, 'labelled', sum(1 for l in labels if l.get('frame')), 'of', len(labels), out)


if __name__ == '__main__':
    main(sys.argv[1])
