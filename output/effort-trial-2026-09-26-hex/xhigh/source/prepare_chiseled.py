"""Chiseled source pools, one per groove orientation class (90 / 30 / 150 deg, image coords).

From each fully visible Chiseled face of the render:
  * colour residual and relief band with the grooves notched out (Gaussian notches, sigma
    0.04 cycles/px, at the fundamental and 2nd / 3rd harmonics): the face's own non-groove
    roughness and mottling
  * groove amplitude modulation: complex demodulation of the band-passed luminance at the
    groove frequency, smoothed (sigma 3 render px), as A / median(A) - 1: how strongly each
    part of each ridge is cut (the broken-ridge look)
Each face crop is rotated so its grooves point along the target class direction (rotation by
multiples of 60 deg maps the hexagon onto itself), then all faces are packed into one mosaic per
class. Writes _work/chis_pool.npz and _work/chis_pool.json.
"""
import os
import json
import numpy as np
from scipy import ndimage as ndi
from guard import WORK_DIR, write_text, safe

P = np.load(os.path.join(WORK_DIR, "pools.npz"))
INFO = json.load(open(os.path.join(WORK_DIR, "pools.json")))
L = json.load(open(os.path.join(WORK_DIR, "render_lattice.json")))
cells = {"%d,%d" % (c["j"], c["k"]): c for c in L["cells"]}
keys = INFO["keys"]
owner = P["owner"]
pool_ch = P["pool_chiseled"]
resid = P["resid"].astype(np.float64)
lw = np.array([0.2126, 0.7152, 0.0722])
Yres = resid @ lw
NW = 0.04
HALF = 190
# pad by HALF so crops of faces near the render border stay in range (padding is outside every mask)
pad2 = ((HALF, HALF), (HALF, HALF))
resid = np.pad(resid, pad2 + ((0, 0),), mode="edge")
Yres = np.pad(Yres, pad2, mode="edge")
owner = np.pad(owner, pad2, constant_values=-1)
pool_ch = np.pad(pool_ch, pad2, constant_values=False)
CLASSES = (90, 30, 150)


def notch_filter(img, k0):
    n = img.shape[0]
    fy, fx = np.meshgrid(np.fft.fftfreq(n), np.fft.fftfreq(n), indexing="ij")
    notch = np.ones((n, n))
    for h in (1, 2, 3):
        for s in (1, -1):
            d2 = (fx - s * h * k0[0]) ** 2 + (fy - s * h * k0[1]) ** 2
            notch *= 1 - np.exp(-d2 / (2 * NW ** 2))
    return np.real(np.fft.ifft2(np.fft.fft2(img) * notch))


def groove_angle(img, period):
    """groove direction (deg, image coords) from the 2D spectrum peak near 1/period."""
    n = img.shape[0]
    w = np.outer(np.hanning(n), np.hanning(n))
    F = np.abs(np.fft.fft2((img - img.mean()) * w, (1024, 1024)))
    fy, fx = np.meshgrid(np.fft.fftfreq(1024), np.fft.fftfreq(1024), indexing="ij")
    fr = np.hypot(fx, fy)
    band = (fr > 0.8 / period) & (fr < 1.25 / period) & (fx >= 0)
    i = np.argmax(np.where(band, F, 0))
    return (np.degrees(np.arctan2(fy.flat[i], fx.flat[i])) + 90) % 180


crops = []
for k, m in INFO["chiseled_measure"].items():
    c = cells[k]
    cx, cy = int(round(c["cx"])) + HALF, int(round(c["cy"])) + HALF        # padded coordinates
    sl = (slice(cy - HALF, cy + HALF), slice(cx - HALF, cx + HALF))
    n = keys.index(k)
    mask = pool_ch[sl] & (owner[sl] == n)
    ang = m["groove_deg_img"]
    nrm = np.radians(ang - 90.0)
    k0 = np.array([np.cos(nrm), np.sin(nrm)]) / m["period_px"]
    # fill outside the face with the face mean before filtering (avoid joint / neighbour leakage)
    fill = lambda a: np.where(mask, a, a[mask].mean())
    rgb = np.dstack([notch_filter(fill(resid[sl][..., ch]), k0) for ch in range(3)])
    y = fill(Yres[sl])
    # same relief band as Raw (calibrate_raw_band.py); the groove frequency is notched out below
    g05, g3, g12 = (ndi.gaussian_filter(y, s) for s in (0.5, 3.0, 12.0))
    band = (g05 - g3) + 0.3 * (g3 - g12)
    rough = notch_filter(band, k0)
    yy, xx = np.mgrid[-HALF:HALF, -HALF:HALF]
    u = xx * k0[0] + yy * k0[1]
    z = band * np.exp(-2j * np.pi * u)
    zs = ndi.gaussian_filter(z.real, 3.0) + 1j * ndi.gaussian_filter(z.imag, 3.0)
    amp = np.abs(zs)
    mod = np.clip(amp / np.median(amp[mask]) - 1.0, -0.8, 0.8)
    ymatch = notch_filter(y, k0)
    crops.append({"key": k, "angle": ang, "period": m["period_px"], "mask": mask,
                  "stack": np.dstack([rgb, rough, mod, ymatch])})
    print("%s angle %.1f: notched rgb std %s, rough std %.2f, mod cv %.2f" % (
        k, ang, np.round(rgb[mask].std(axis=0), 2), rough[mask].std(), mod[mask].std()))

out = {}
meta = {"notch_sigma_cyc_per_px": NW, "classes": {}}
S = 2 * HALF
for cls in CLASSES:
    tiles, masks, kmap = [], [], []
    for c in crops:
        delta = cls - c["angle"]
        # choose the rotation sign that brings the grooves to the class angle, checked on the data:
        # rotate the un-notched luminance crop (which carries the grooves) and re-measure its angle
        rots = {}
        for sgn in (1, -1):
            cx, cy = int(round(cells[c["key"]]["cx"])) + HALF, int(round(cells[c["key"]]["cy"])) + HALF
            ylum = Yres[cy - HALF:cy + HALF, cx - HALF:cx + HALF]
            rl = ndi.rotate(ylum, sgn * delta, reshape=False, order=1, mode="nearest")
            core = rl[HALF - 110:HALF + 110, HALF - 110:HALF + 110]
            meas = groove_angle(core, c["period"])
            err = abs(((meas - cls) + 90) % 180 - 90)
            rots[sgn] = err
        sgn = min(rots, key=rots.get)
        if abs(delta) < 1e-6:
            st, mk = c["stack"], c["mask"]
        else:
            st = np.dstack([ndi.rotate(c["stack"][..., ch], sgn * delta, reshape=False, order=1, mode="nearest")
                            for ch in range(c["stack"].shape[2])])
            mk = ndi.rotate(c["mask"].astype(float), sgn * delta, reshape=False, order=1) > 0.99
            mk = ndi.binary_erosion(mk, iterations=2)
        tiles.append(st)
        masks.append(mk)
        kmap.append(c["key"])
        meta["classes"].setdefault(str(cls), []).append({"source": c["key"], "source_angle": c["angle"],
                                                         "rotation_deg": float(sgn * delta if delta else 0.0),
                                                         "angle_error_after_rotation_deg": float(rots[sgn])})
    # pack in one row: mosaic of S x (S * n)
    n = len(tiles)
    field = np.zeros((S, S * n, 6), np.float32)
    msk = np.zeros((S, S * n), bool)
    kid = np.zeros((S, S * n), np.int16)
    for i, (st, mk) in enumerate(zip(tiles, masks)):
        field[:, i * S:(i + 1) * S] = st
        msk[:, i * S:(i + 1) * S] = mk
        kid[:, i * S:(i + 1) * S] = i
    out["field_%d" % cls] = field
    out["mask_%d" % cls] = msk
    out["kid_%d" % cls] = kid
    meta["classes"][str(cls) + "_keys"] = kmap
    print("class %d: %d source faces, pool px %d, max rotation-sign error %.1f deg" % (
        cls, n, msk.sum(), max(e["angle_error_after_rotation_deg"] for e in meta["classes"][str(cls)])))
allm = np.concatenate([c["mask"][..., None] for c in crops], axis=2)
meta["rough_std"] = float(np.concatenate([c["stack"][..., 3][c["mask"]] for c in crops]).std())
meta["mod_std"] = float(np.concatenate([c["stack"][..., 4][c["mask"]] for c in crops]).std())
np.savez_compressed(safe(os.path.join(WORK_DIR, "chis_pool.npz")), **out)
write_text(os.path.join(WORK_DIR, "chis_pool.json"), json.dumps(meta, indent=1))
print("rough std %.3f levels, mod std %.3f" % (meta["rough_std"], meta["mod_std"]))
