"""Independent re-check of the delivered Ligne Noir maps, read back from disk (CPython 3).

    python verify_maps.py      -> exit 0 only if every check passes

Checks: PNG IHDR bytes (colour 8-bit RGB, bump 16-bit grey, same size), pixel aspect equals
the 36 x 40 in Sample Size, exact bump wrap and near-noise colour wrap, 10 ribs per tile,
bump range (grout floor 0, rib tops 1), clearance of the channel floor above the grout,
48 distinct tile faces, colour mean against the swatch. Does not import the builder.
"""
import hashlib
import os
import struct
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
TEX = os.path.normpath(os.path.join(HERE, '..', 'textures'))
COLOR = os.path.join(TEX, 'ELM_Ligne_Noir_3x10_Color.png')
BUMP = os.path.join(TEX, 'ELM_Ligne_Noir_3x10_Bump16.png')
SAMPLE_IN = (36.0, 40.0)
MODULE_PX = (300, 1000)
FLUTES = 10


def ihdr(path):
    with open(path, 'rb') as fh:
        head = fh.read(26)
    assert head[:8] == b'\x89PNG\r\n\x1a\n', 'not a PNG: ' + path
    w, h = struct.unpack('>II', head[16:24])
    return w, h, head[24], head[25]


def main():
    problems = []
    cw, ch, cd, ct = ihdr(COLOR)
    bw, bh, bd, bt = ihdr(BUMP)
    if (cd, ct) != (8, 2):
        problems.append('colour IHDR bit depth %d colour type %d (expected 8 / 2)' % (cd, ct))
    if (bd, bt) != (16, 0):
        problems.append('bump IHDR bit depth %d colour type %d (expected 16 / 0)' % (bd, bt))
    if (cw, ch) != (bw, bh):
        problems.append('size mismatch colour %dx%d bump %dx%d' % (cw, ch, bw, bh))
    if abs(cw / float(ch) - SAMPLE_IN[0] / SAMPLE_IN[1]) > 1e-9:
        problems.append('pixel aspect %.6f != Sample Size aspect %.6f' % (cw / float(ch), SAMPLE_IN[0] / SAMPLE_IN[1]))

    c = np.asarray(Image.open(COLOR).convert('RGB')).astype(np.float64)
    b = np.asarray(Image.open(BUMP)).astype(np.float64) / 65535.0
    if b.ndim != 2:
        problems.append('bump did not decode as single-channel')
    for name, a in (('colour', c.mean(axis=2)), ('bump', b * 255.0)):
        sx, sy = np.abs(a[:, 0] - a[:, -1]).mean(), np.abs(a[0] - a[-1]).mean()
        tx, ty = np.abs(np.diff(a, axis=1)).mean(), np.abs(np.diff(a, axis=0)).mean()
        if sx > 1.5 * tx or sy > 1.5 * ty:
            problems.append('%s wrap step %.3f/%.3f vs typical %.3f/%.3f' % (name, sx, sy, tx, ty))
    if abs(b.min()) > 1e-6 or abs(b.max() - 1.0) > 1e-3:
        problems.append('bump range %.5f..%.5f (expected 0..1)' % (b.min(), b.max()))

    mw, ml = MODULE_PX
    cols, rows = cw // mw, ch // ml
    counts, hashes, floors = [], set(), []
    for r in range(rows):
        for q in range(cols):
            seg = b[r * ml + ml // 2, q * mw:(q + 1) * mw]
            counts.append(int(np.sum(np.diff((seg > 0.9).astype(int)) == 1)))
            inner = b[r * ml + 40:(r + 1) * ml - 40, q * mw + 12:(q + 1) * mw - 12]
            floors.append(inner.min())
            cell = c[r * ml + 12:(r + 1) * ml - 12, q * mw + 12:(q + 1) * mw - 12]
            hashes.add(hashlib.sha1(np.ascontiguousarray(cell[::4, ::4]).tobytes()).hexdigest())
    if min(counts) != FLUTES or max(counts) != FLUTES:
        problems.append('ribs per tile %d..%d (expected %d)' % (min(counts), max(counts), FLUTES))
    if min(floors) <= 0.05:
        problems.append('channel floor touches the grout floor (min %.4f of range)' % min(floors))
    if len(hashes) != cols * rows:
        problems.append('%d distinct tile faces of %d' % (len(hashes), cols * rows))

    face = np.ones(c.shape[:2], bool)
    x = np.arange(cw)
    y = np.arange(ch)
    face &= ((x % mw > 8) & (x % mw < mw - 8))[None, :]
    face &= ((y % ml > 8) & (y % ml < ml - 8))[:, None]
    mean = c[face].mean(axis=0)
    print('colour face mean sRGB %.1f %.1f %.1f' % tuple(mean))
    if not (np.all(mean > 25) and np.all(mean < 70)):
        problems.append('face colour mean %r outside the swatch range' % (mean.round(1).tolist(),))

    if problems:
        print('FAIL')
        for p in problems:
            print('  - ' + p)
        return 1
    print('PASS: %dx%d, colour 8-bit RGB, bump 16-bit grey, Sample Size 36 x 40 in, %d tiles x %d ribs, '
          'channel floor %.3f of range above grout, %d distinct faces, both maps wrap.'
          % (cw, ch, cols * rows, FLUTES, min(floors), len(hashes)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
