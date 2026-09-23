"""Independent gate check for the ELM Fog Cross-Cut Chevron 24x48 deliverable.

Re-derives every gate from the exported files (never from the builder's own
report values) and exits non-zero on any failure. Writes ../validation.json.
"""
import json
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from scipy.signal import fftconvolve

import chevron_common as cc
import make_model_pattern as mmp

T = os.path.join(cc.PROD, "textures")
NAME = "ELM_Fog_CrossCut_Chevron_24x48"
ATLAS_IN = (144.0, 96.0)
COLS, ROWS = 3, 4
HEIGHT_RANGE_MM = 1.70


def main():
    gates = {}
    fails = []

    def gate(key, ok, **info):
        gates[key] = dict(info, passed=bool(ok))
        if not ok:
            fails.append(key)

    p = {k: os.path.join(T, "%s_%s.png" % (NAME, k)) for k in ("Color", "Bump16", "Roughness")}
    hdr = {k: cc.png_header(v) for k, v in p.items()}
    gate("png_headers", hdr["Color"][2:] == (8, 2) and hdr["Bump16"][2:] == (16, 0) and hdr["Roughness"][2:] == (8, 0)
         and len({h[:2] for h in hdr.values()}) == 1, ihdr=hdr)
    W, H = hdr["Color"][:2]
    ppi_x, ppi_y = W / ATLAS_IN[0], H / ATLAS_IN[1]
    gate("aspect_equals_sample_size", abs(ppi_x - ppi_y) < 1e-9, px_per_in=[ppi_x, ppi_y],
         sample_size_in=list(ATLAS_IN), revit="12'-0\" x 8'-0\"")

    col = np.asarray(Image.open(p["Color"])).astype(np.int32)
    bmp = np.asarray(Image.open(p["Bump16"])).astype(np.int32)
    rgh = np.asarray(Image.open(p["Roughness"])).astype(np.int32)

    # registration: the grout core is the same set of pixels in all three maps
    core = bmp == 0
    grout_c = np.abs(col - np.array(cc.GROUT_RGB)[None, None, :]).max(-1) <= 1
    grout_r = np.abs(rgh - round(cc.ROUGH_GROUT * 255)) <= 1
    gate("registration_grout_core", core.any() and (grout_c[core].mean() == 1.0) and (grout_r[core].mean() == 1.0),
         core_px=int(core.sum()), colour_match=float(grout_c[core].mean()), rough_match=float(grout_r[core].mean()))

    # joint grid positions: columns / rows that are grout for their whole length
    jc = np.where(core.mean(0) > 0.5)[0].tolist()
    jr = np.where(core.mean(1) > 0.5)[0].tolist()
    exp_c = sorted({0, W - 1} | {int(round(k * W / COLS)) + d for k in range(1, COLS) for d in (-1, 0)})
    exp_r = sorted({0, H - 1} | {int(round(k * H / ROWS)) + d for k in range(1, ROWS) for d in (-1, 0)})
    gate("joint_grid", jc == exp_c and jr == exp_r, joint_cols=jc, joint_rows=jr, expected_cols=exp_c, expected_rows=exp_r)

    # wrap: opposite edges identical, and the step across the wrap no larger than
    # the step across an interior joint centreline
    wrap = {}
    for k, a in (("Color", col), ("Bump16", bmp), ("Roughness", rgh)):
        lr = np.abs(a[:, 0] - a[:, -1]).max()
        tb = np.abs(a[0] - a[-1]).max()
        mid_c = W // COLS
        inner = np.abs(a[:, mid_c - 1] - a[:, mid_c]).max()
        wrap[k] = {"left_right_max_step": int(lr), "top_bottom_max_step": int(tb), "interior_joint_step": int(inner)}
    gate("wrap_seamless", all(v["left_right_max_step"] == 0 and v["top_bottom_max_step"] == 0 for v in wrap.values()),
         **wrap)

    # relief, from the 16-bit map only
    h = bmp / 65535.0 * HEIGHT_RANGE_MM
    dist = ndi.distance_transform_edt(~core)            # px from the nearest grout-core pixel
    face = dist > 1.5                                   # tile face incl. eased edge
    interior = dist > (1.5 + cc.CHAMFER_W_MM / (25.4 / ppi_x) + 1)
    floor = float(np.median(h[core]))
    plane = float(np.percentile(h[interior], 90))
    p1 = float(np.percentile(h[interior], 1))
    rel = {
        "grout_floor_mm": floor,
        "tile_plane_mm_p90": plane,
        "grout_step_mm": plane - floor,
        "groove_relief_mm_p90_minus_p1": plane - p1,
        "deepest_face_point_mm": float(h[face].min()),
        "clearance_above_grout_floor_mm": float(h[face].min()) - floor,
        "max_height_mm": float(h.max()),
        "bump_unique_levels": int(np.unique(bmp).size),
    }
    gate("dimensional_relief", rel["clearance_above_grout_floor_mm"] > 0 and rel["groove_relief_mm_p90_minus_p1"] >= 0.6
         and bmp.max() < 65535, **rel)

    # groove geometry actually present in the bump: two directions, ~49 deg, pitch ~0.19 in
    ch_px, cw_px = H // ROWS, W // COLS
    tile_h = h[40:ch_px - 40, 40:cw_px - 40]
    hp = tile_h - ndi.gaussian_filter(tile_h, 20)
    gy, gx = np.gradient(ndi.gaussian_filter(hp, 1.0))
    jxx, jyy, jxy = (ndi.gaussian_filter(v, 6) for v in (gx * gx, gy * gy, gx * gy))
    line = (np.degrees(0.5 * np.arctan2(2 * jxy, jxx - jyy)) + 90) % 180
    hist = np.histogram(line, bins=180, range=(0, 180))[0]
    pk1 = int(np.argmax(hist[:90]))
    pk2 = 90 + int(np.argmax(hist[90:]))
    gate("groove_directions", 45 <= pk1 <= 53 and 127 <= pk2 <= 135, line_angle_peaks_deg=[pk1 + 0.5, pk2 + 0.5])

    # colour value versus the product swatch (chevron slab, as supplied)
    sw = cc.load_slab().reshape(-1, 3).mean(0)
    tile_mean = col[~core].reshape(-1, 3).mean(0)
    dev = float(np.abs(tile_mean - sw).max() / sw.mean())
    gate("colour_value_matches_swatch", dev < 0.01, swatch_mean=sw.tolist(), atlas_face_mean=tile_mean.tolist(), max_rel_dev=dev)

    # per-tile tone spread (no landmark tile)
    Lc = cc.lum(col.astype(np.float64))
    cells = [Lc[r * ch_px + 30:(r + 1) * ch_px - 30, c * cw_px + 30:(c + 1) * cw_px - 30].mean()
             for r in range(ROWS) for c in range(COLS)]
    spread = float((max(cells) - min(cells)) / np.mean(cells))
    gate("tile_tone_spread", spread < 0.02, cell_luminance=[round(v, 2) for v in cells], rel_spread=spread)

    # fine-grain consistency between faces from differently compressed sources
    fine = []
    for r in range(ROWS):
        for c in range(COLS):
            a = Lc[r * ch_px + 40:(r + 1) * ch_px - 40, c * cw_px + 40:(c + 1) * cw_px - 40]
            fine.append(float((a - ndi.gaussian_filter(a, 1.0)).std()))
    ratio = max(fine) / min(fine)
    gate("tile_fine_detail_consistent", ratio < 1.5, fine_band_std=[round(v, 2) for v in fine], max_over_min=ratio)

    # face identity: which cells share a source face (expected: 5 designed repeats,
    # never adjacent on the torus)
    def feat(r, c):
        a = Lc[r * ch_px + 60:(r + 1) * ch_px - 60, c * cw_px + 60:(c + 1) * cw_px - 60]
        a = np.asarray(Image.fromarray(a.astype(np.float32)).resize((a.shape[1] // 8, a.shape[0] // 8), Image.BILINEAR),
                       dtype=np.float64)
        a = a - ndi.gaussian_filter(a, 6)
        return (a - a.mean()) / (a.std() + 1e-9)
    F = {(r, c): feat(r, c) for r in range(ROWS) for c in range(COLS)}
    pairs = []
    for i, (ka, fa) in enumerate(F.items()):
        for kb, fb in list(F.items())[i + 1:]:
            best = 0.0
            for g in (fb, fb[::-1, ::-1], fb[:, ::-1], fb[::-1]):
                best = max(best, float((fa * g).mean()))
            if best > 0.5:
                adj = (min((ka[0] - kb[0]) % ROWS, (kb[0] - ka[0]) % ROWS) <= 1 and
                       min((ka[1] - kb[1]) % COLS, (kb[1] - ka[1]) % COLS) <= 1)
                pairs.append({"a": ka, "b": kb, "ncc": round(best, 3), "adjacent": adj})
    gate("repeat_faces_not_adjacent", len(pairs) <= 5 and not any(q["adjacent"] for q in pairs),
         same_face_pairs=pairs, distinct_faces=ROWS * COLS - len(pairs))

    # model pattern registers with the joints
    pat = os.path.join(cc.PROD, "pattern", NAME + "_Landscape.pat")
    res, _ = mmp.check_against_joints(pat, p["Bump16"], *ATLAS_IN)
    res.pop("families")
    gate("model_pattern_registers", res["pass"], **res)

    out = {"product": NAME, "gates": gates, "failed": fails, "all_passed": not fails}
    with open(os.path.join(cc.PROD, "validation.json"), "w") as fh:
        json.dump(out, fh, indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o))
    for k, v in gates.items():
        print("%-32s %s" % (k, "PASS" if v["passed"] else "FAIL"))
    if fails:
        print("FAILED:", fails)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
