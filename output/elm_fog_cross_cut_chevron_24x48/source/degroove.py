"""REJECTED approach, kept for comparison and for oriented_energy().

The build removes the grooves with grooves.degroove_slab (extruded measured
profile). This frequency notch left the groove sub-harmonics (1.47x-3.5x the
pitch) as visible diagonal streaks: _analysis/degroove_hp_degrooved.jpg.

Remove the baked chevron-groove shading from ELM's slab swatch.

The grooves are a narrow-band periodic signal: two line orientations (one per
alternate band) at a measured 7.55-8.38 px pitch, plus harmonics. A smooth
Gaussian-tapered polar notch around those frequencies removes them from each
colour channel while leaving the cross-cut stone graphic intact.

Validation (run this file directly): ELM also publishes the same stone graphic
without the chevron structure, pixel-registered. Downscaled to its size, the
de-grooved result should (a) lose the oriented groove energy and (b) move
closer to that groove-free render. Both numbers are written to
_analysis/degroove_check.json.
"""
import json
import os

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

import chevron_common as cc


def groove_normals_deg():
    # normal of each measured band direction, folded into [0, 180)
    return sorted({round((a - 90.0) % 180.0, 2) for a in cc.BAND_LINE_DEG})


def notch_mask(h, w, ang_halfwidth=3.0, rad_pad=0.05, harmonics=(1, 2, 3)):
    fy = np.fft.fftfreq(h)[:, None]
    fx = np.fft.fftfreq(w)[None, :]
    r = np.hypot(fx, fy)
    ang = np.degrees(np.arctan2(fy, fx)) % 180.0
    fmin = 1.0 / max(cc.BAND_PITCH_PX)
    fmax = 1.0 / min(cc.BAND_PITCH_PX)
    keep = np.ones((h, w))
    normals = groove_normals_deg()
    # the two orientation families: ~40.4-41.7 and ~139.3-139.6 degrees
    fam = [[n for n in normals if n < 90], [n for n in normals if n >= 90]]
    for group in fam:
        a0, a1 = min(group), max(group)
        da = np.minimum(np.abs(ang - a0), np.abs(ang - a1))
        inside = (ang >= a0) & (ang <= a1)
        da = np.where(inside, 0.0, da)
        wa = np.exp(-0.5 * (da / ang_halfwidth) ** 2)
        for k in harmonics:
            lo, hi = k * fmin * (1 - rad_pad), k * fmax * (1 + rad_pad)
            dr = np.where(r < lo, lo - r, np.where(r > hi, r - hi, 0.0))
            wr = np.exp(-0.5 * (dr / (0.012 * k)) ** 2)
            keep *= 1.0 - wa * wr
    return keep


def degroove(rgb, **kw):
    h, w = rgb.shape[:2]
    keep = notch_mask(h, w, **kw)
    out = np.empty_like(rgb)
    for c in range(3):
        ch = rgb[..., c]
        m = ch.mean()
        out[..., c] = np.real(np.fft.ifft2(np.fft.fft2(ch - m) * keep)) + m
    return out, keep


def oriented_energy(L):
    """Fraction of high-pass energy inside the groove notch (0 = no grooves)."""
    hp = L - ndi.gaussian_filter(L, 10)
    F = np.abs(np.fft.fft2(hp)) ** 2
    keep = notch_mask(*L.shape)
    return float((F * (1 - keep)).sum() / F.sum())


def main():
    rgb = cc.load_rgb(cc.SLAB_SRC)
    dg, keep = degroove(rgb)
    ref = cc.load_rgb(cc.GROOVE_FREE_CHECK)
    size = (ref.shape[1], ref.shape[0])

    def small(a):
        return np.asarray(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).resize(size, Image.LANCZOS)).astype(np.float64)

    s_raw, s_dg = small(rgb), small(dg)
    rep = {
        "notch_normals_deg": groove_normals_deg(),
        "oriented_energy_raw_full": oriented_energy(cc.lum(rgb)),
        "oriented_energy_degrooved_full": oriented_energy(cc.lum(dg)),
        "oriented_energy_groove_free_ref": oriented_energy(cc.lum(ref)),
        "mad_vs_groove_free_raw": float(np.abs(s_raw - ref).mean()),
        "mad_vs_groove_free_degrooved": float(np.abs(s_dg - ref).mean()),
        "hp_mad_vs_groove_free_raw": float(np.abs((cc.lum(s_raw) - ndi.gaussian_filter(cc.lum(s_raw), 4))
                                                  - (cc.lum(ref) - ndi.gaussian_filter(cc.lum(ref), 4))).mean()),
        "hp_mad_vs_groove_free_degrooved": float(np.abs((cc.lum(s_dg) - ndi.gaussian_filter(cc.lum(s_dg), 4))
                                                        - (cc.lum(ref) - ndi.gaussian_filter(cc.lum(ref), 4))).mean()),
        "mean_rgb_raw": rgb.reshape(-1, 3).mean(0).tolist(),
        "mean_rgb_degrooved": dg.reshape(-1, 3).mean(0).tolist(),
        "removed_std_per_channel": (rgb - dg).reshape(-1, 3).std(0).tolist(),
    }
    out = os.path.join(cc.HERE, "_analysis")
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "degroove_check.json"), "w") as fh:
        json.dump(rep, fh, indent=1)
    print(json.dumps(rep, indent=1))
    # diagnostics: high-pass of raw vs de-grooved, same native crop
    for nm, a in (("raw", rgb), ("degrooved", dg)):
        L = cc.lum(a)[545:745, 2000:2400]
        hp = L - ndi.gaussian_filter(L, 10)
        g = np.clip((hp + 6) / 12, 0, 1)
        Image.fromarray((g * 255).astype(np.uint8)).resize((800, 400), Image.NEAREST).save(
            os.path.join(out, "degroove_hp_%s.jpg" % nm), quality=92)
    t = Image.fromarray(np.clip(dg, 0, 255).astype(np.uint8))
    t.thumbnail((800, 800))
    t.save(os.path.join(out, "degrooved_thumb.jpg"), quality=90)


if __name__ == "__main__":
    main()
