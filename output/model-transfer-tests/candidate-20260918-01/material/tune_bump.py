# -*- coding: utf-8 -*-
"""Bump-amplitude comparison strip for the reviewer.

Reviewer feedback 2026-09-18: the grout relief is right, the geometric pattern
relief should be more pronounced. In build_maps.py the two are independent:

    height = .15 + (.5 + (height - .5) * mask - .15) * mask

grout depth is fixed by the .15 floor and the mask, while the pattern is
.5 +/- PATTERN_AMP * tanh(signal) around mid face. Raising PATTERN_AMP deepens
the pattern only.

This renders candidate amplitudes at preview resolution so one can be chosen
before committing to a full 4096 x 2048 rebuild. It writes only into
logs/bump-tuning and never touches the deliverable maps.
"""
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..', '..'))
SRC = os.path.join(ROOT, 'references', 'adella', 'crawl2.jpg')
OUT_DIR = os.path.join(HERE, 'logs', 'bump-tuning')

CROP = (12, 12, 2548, 1257)
PREVIEW_W, PREVIEW_H = 1400, 700          # preview only, not a deliverable size
REPEAT_MM = (611.1875, 306.3875)          # baseline, 1/16 in grout
HALF_JOINT_MM = (1.0 / 16.0) * 25.4 / 2.0
BEVEL_MM = 2.0
HEIGHT_RANGE_MM = 0.6
CURRENT_AMP = 0.20
CANDIDATES = [0.20, 0.30, 0.40, 0.50]


def blur(a, s):
    p = int(s * 4) + 1
    b = np.pad(a, ((p, p), (p, p)), mode='reflect')
    fy = np.fft.fftfreq(b.shape[0])[:, None]
    fx = np.fft.rfftfreq(b.shape[1])[None, :]
    b = np.fft.irfft2(
        np.fft.rfft2(b) * np.exp(-2 * np.pi ** 2 * s * s * (fx * fx + fy * fy)), s=b.shape)
    return b[p:-p, p:-p]


def resize(a):
    return np.asarray(
        Image.fromarray(a.astype('float32')).resize((PREVIEW_W, PREVIEW_H),
                                                    Image.Resampling.BICUBIC),
        dtype=float)


def main():
    if not os.path.isdir(OUT_DIR):
        os.makedirs(OUT_DIR)

    photo = np.asarray(Image.open(SRC).convert('RGB').crop(CROP), dtype=np.float64) / 255
    lum = photo @ np.array([.2126, .7152, .0722])
    smooth = blur(lum, 3)
    signal = smooth - blur(smooth, 100)          # independent of amplitude
    scale = np.percentile(np.abs(signal), 99)
    unit = resize(np.tanh(signal / max(scale, 1e-6)))

    y, x = np.mgrid[:PREVIEW_H, :PREVIEW_W]
    edge = np.minimum.reduce([
        x * REPEAT_MM[0] / PREVIEW_W, (PREVIEW_W - 1 - x) * REPEAT_MM[0] / PREVIEW_W,
        y * REPEAT_MM[1] / PREVIEW_H, (PREVIEW_H - 1 - y) * REPEAT_MM[1] / PREVIEW_H,
    ])
    t = np.clip((edge - HALF_JOINT_MM) / BEVEL_MM, 0, 1)
    mask = t * t * (3 - 2 * t)

    base = np.stack([resize(blur(photo[:, :, i], 2)) for i in range(3)], axis=2)
    base = .85 * np.median(photo, axis=(0, 1)) + .15 * base
    base = base * mask[:, :, None] + .86 * (1 - mask[:, :, None])

    # Grazing light: this is where shallow relief either reads or disappears.
    light = np.array([-.94, .12, .32])
    light /= np.linalg.norm(light)

    panels, stats = [], []
    for amp in CANDIDATES:
        height = .5 + amp * unit
        height = .15 + (.5 + (height - .5) * mask - .15) * mask
        dy, dx = np.gradient(height * HEIGHT_RANGE_MM,
                             REPEAT_MM[1] / PREVIEW_H, REPEAT_MM[0] / PREVIEW_W)
        n = np.stack([-dx, dy, np.ones_like(dx)], axis=2)
        n /= np.linalg.norm(n, axis=2)[:, :, None]
        shaded = np.clip(base * (.35 + .75 * np.maximum(0, n @ light)[:, :, None]), 0, 1)

        interior = height[mask > .999]
        stats.append({
            'amp': amp,
            'pattern_span_mm': float((interior.max() - interior.min()) * HEIGHT_RANGE_MM),
            'grout_step_mm': float((interior.mean() - .15) * HEIGHT_RANGE_MM),
            'min_vs_grout': float(interior.min() - .15),
        })
        panels.append(np.uint8(shaded * 255 + .5))

    strip = np.concatenate(panels, axis=0)
    path = os.path.join(OUT_DIR, 'bump_amplitude_comparison.jpg')
    Image.fromarray(strip).resize((1100, 550 * len(panels) // 1 // len(panels) * len(panels))).save(
        path, quality=90)
    Image.fromarray(strip).save(os.path.join(OUT_DIR, 'bump_amplitude_comparison_full.jpg'),
                                quality=92)

    print('panels top to bottom, grazing light:')
    for s in stats:
        flag = '  <-- current' if abs(s['amp'] - CURRENT_AMP) < 1e-9 else ''
        print('  amp %.2f | pattern relief %.3f mm | grout step %.3f mm | '
              'clearance above grout floor %.3f%s'
              % (s['amp'], s['pattern_span_mm'], s['grout_step_mm'], s['min_vs_grout'], flag))
    print('')
    print('written:', path)


if __name__ == '__main__':
    main()
