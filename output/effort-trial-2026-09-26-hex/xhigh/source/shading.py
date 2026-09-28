"""Grazing-light shading of the height field, shared by make_previews.py and calibrate_relief.py."""
import numpy as np
import common as C


def shade(hmm, elev_deg=15.0, az_deg=200.0, shadows=True):
    """Lambert shading of a height field in mm at 0.397 mm/px; az = direction the light comes FROM,
    image coords (0 = from +x/right, 90 = from +y/below, 180 = from the left, 270 = from above).
    Returned value is n.l / sin(elev), so a flat face is 1.0. Cast shadows by a horizon test along
    the light direction on the wrapped (tiling) height field."""
    h = hmm.astype(np.float64)
    # periodic central differences: the texture tiles, so the edges must not use one-sided slopes
    gx = (np.roll(h, -1, axis=1) - np.roll(h, 1, axis=1)) / (2.0 * C.MM_PER_PX)
    gy = (np.roll(h, -1, axis=0) - np.roll(h, 1, axis=0)) / (2.0 * C.MM_PER_PX)
    e, a = np.radians(elev_deg), np.radians(az_deg)
    lx, ly, lz = np.cos(e) * np.cos(a), np.cos(e) * np.sin(a), np.sin(e)
    n = np.sqrt(gx * gx + gy * gy + 1.0)
    ndl = (-gx * lx - gy * ly + lz) / n
    s = np.clip(ndl, 0, None) / np.sin(e)
    if shadows:
        lit = np.ones(hmm.shape, dtype=bool)
        tan_e = np.tan(e) * C.MM_PER_PX
        for t in range(1, 48):
            ix, iy = int(round(np.cos(a) * t)), int(round(np.sin(a) * t))
            hs = np.roll(np.roll(hmm, -iy, axis=0), -ix, axis=1)
            lit &= hs <= hmm + np.hypot(ix, iy) * tan_e
        s = np.where(lit, s, 0.0)
    return s


def tone(colr, s, amb=0.28):
    """colour x (ambient + diffuse * shading), soft highlight roll-off, 8-bit."""
    x = colr / 255.0 * (amb + (1 - amb) * s)[..., None]
    x = x / (1.0 + 0.18 * x) * 1.18
    return np.clip(x * 255.0, 0, 255).astype(np.uint8)
