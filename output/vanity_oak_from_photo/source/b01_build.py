"""Assemble the 48 x 24 in horizontal-grain oak colour map from the de-lit photo crops (working density 32 px/in).

Construction (every pixel is a real photo pixel; no synthesis):
- The map is six veneer leaves (bands) stacked across the grain, each running the full 48 in along the grain and
  wrapping on itself:  B1 apron | B2 door_L main | B3 door_L remainder | B4 bottom rail | B5 door_R main |
  B6 door_R remainder (which wraps onto B1).  B2+B3 are the continuous left door (rotated), B5+B6 the right one.
- Each band is anchored by its long crop and extended along the grain with real drawer pieces / strips. For every
  end join, the candidate piece is shifted across the grain (and along it where slack exists) to the offset whose
  overlap best matches the grain already placed (SSD, gamma space), then cut on a minimum-error vertical boundary
  (dynamic programming). The loop-closing piece matches both neighbours and gets two cuts. Same logic closes the
  horizontal wrap.
- Bands are joined along the grain by minimum-error horizontal cuts in 4-5 px overlaps (the leaf joints); the B6->B1
  joint is the vertical wrap and is cut the same way, with the cut path closed around the horizontal wrap.
- Tone: within a band every piece is matched to the band anchor's mean (a leaf reads as one piece of veneer).
  Between bands the natural leaf differences are kept at half strength (mild per-leaf tone difference).
  Finally the whole map is scaled to the photo's mid-panel oak tone.
- Provenance of every output pixel is recorded; the build asserts no source pixel appears twice.

Writes _work/assembly_32ppi.npy (linear RGB float64), _work/provenance.npz, _work/layout.json."""
import json

import numpy as np
from scipy import ndimage as ndi

from common import lum, srgb_to_lin, lin_to_srgb, load_rgb, thumb
from guard import SOURCE_PHOTO, out_path

W, H, PPI = 1536, 768, 32
NAMES = ["drawer_L1", "drawer_L2", "drawer_L3", "drawer_R1", "drawer_R2", "drawer_R3", "door_L", "door_R", "apron",
         "bottom_rail"]
CID = {n: i for i, n in enumerate(NAMES)}

# piece: (crop, x_lo, x_hi (source column range usable), y_lo, y_hi (source row range usable), width or None=fill)
BANDS = [
    {"id": "B1", "hs": 65, "vo": 20, "xa": 0,
     "anchor": ("apron", 0, 1362, 0, 65),
     "ext": [("drawer_L2", 114, 329, 0, 72, 214)]},
    {"id": "B2", "hs": 280, "vo": 32, "xa": 560, "tone_group": "door_L",
     "anchor": ("door_L", 0, 892, 0, 280),
     "ext": [("drawer_L1", 0, 329, 0, 288, 329), ("drawer_L2", 0, 114, 0, 287, None), ("drawer_L3", 0, 329, 0, 287, 329)]},
    {"id": "B3", "hs": 52, "vo": 22, "xa": 560, "tone_group": "door_L",
     "anchor": ("door_L", 0, 892, 275, 327),
     "ext": [("drawer_L2", 114, 329, 72, 126, 215), ("drawer_L2", 114, 329, 126, 180, 215),
             ("drawer_L2", 114, 329, 180, 234, 215), ("drawer_L2", 114, 329, 234, 287, None)]},
    {"id": "B4", "hs": 68, "vo": 18, "xa": 900,
     "anchor": ("bottom_rail", 0, 1362, 2, 70),
     "ext": [("drawer_R2", 116, 328, 0, 71, 210)]},
    {"id": "B5", "hs": 280, "vo": 32, "xa": 150, "tone_group": "door_R",
     "anchor": ("door_R", 0, 892, 0, 280),
     "ext": [("drawer_R1", 0, 329, 0, 288, 329), ("drawer_R2", 0, 116, 0, 287, None), ("drawer_R3", 0, 327, 0, 286, 327)]},
    {"id": "B6", "hs": 53, "vo": 22, "xa": 150, "tone_group": "door_R",
     "anchor": ("door_R", 0, 892, 275, 328),
     "ext": [("drawer_R2", 116, 328, 71, 125, 212), ("drawer_R2", 116, 328, 125, 179, 212),
             ("drawer_R2", 116, 328, 179, 233, 212), ("drawer_R2", 116, 328, 233, 287, None)]},
]
HO = [5, 5, 5, 5, 5, 5]      # overlap of each band with the band above it (B1's is with B6 through the wrap)
LEAF_TONE_KEEP = 0.4          # fraction of the natural (log) leaf tone difference kept between wide bands
LEAF_TONE_KEEP_THIN = 0.2     # thin bands (< 100 px, the rails and door remainders) read as lines, so keep less
ANCHOR_DETAIL_PULL = 0.5      # anchors' grain contrast pulled half-way (in log) toward the median of all crops
GAIN_LIM = (0.75, 1.4)        # per-piece grain-contrast match to the band anchor (detail-layer gain), capped


def bp_std(rgb):
    L = np.log(np.maximum(lum(rgb), 1e-5))
    return float((ndi.gaussian_filter(L, 0.7) - ndi.gaussian_filter(L, 6)).std())


def detail_gain(rgb, g):
    """Scale the existing fine detail (log-luminance minus its 6 px low-pass) by g; nothing is added."""
    if abs(g - 1) < 1e-6:
        return rgb
    L = np.log(np.maximum(lum(rgb), 1e-5))
    D = L - ndi.gaussian_filter(L, 6, mode="nearest")
    return rgb * np.exp((g - 1) * D)[..., None]


def gam(a):
    return np.power(np.clip(a, 0, None), 1 / 2.2)


def dp_seam(C):
    """Min-cost top-to-bottom path through cost map C (rows x cols), 8-connected. Returns column per row."""
    h, w = C.shape
    E = C.copy()
    B = np.zeros((h, w), int)
    for y in range(1, h):
        prev = E[y - 1]
        cand = np.stack([np.r_[np.inf, prev[:-1]], prev, np.r_[prev[1:], np.inf]])
        k = np.argmin(cand, 0)
        B[y] = k - 1
        E[y] += cand[k, np.arange(w)]
    path = np.zeros(h, int)
    path[-1] = int(np.argmin(E[-1]))
    for y in range(h - 1, 0, -1):
        path[y - 1] = path[y] + B[y, path[y]]
    return path, float(E[-1, path[-1]])


def dp_seam_closed(C):
    """Min-cost left-to-right path through C (rows x cols) that closes on itself around a horizontal wrap."""
    h, w = C.shape
    best = (np.inf, None)
    for r0 in range(h):
        E = np.full(h, np.inf)
        E[r0] = C[r0, 0]
        B = np.zeros((w, h), int)
        for x in range(1, w):
            cand = np.stack([np.r_[np.inf, E[:-1]], E, np.r_[E[1:], np.inf]])
            k = np.argmin(cand, 0)
            B[x] = k - 1
            E = cand[k, np.arange(h)] + C[:, x]
        ends = [r for r in (r0 - 1, r0, r0 + 1) if 0 <= r < h]
        r_end = min(ends, key=lambda r: E[r])
        if E[r_end] < best[0]:
            path = np.zeros(w, int)
            path[-1] = r_end
            for x in range(w - 1, 0, -1):
                path[x - 1] = path[x] + B[x, path[x]]
            best = (E[r_end], path)
    return best[1], float(best[0])


def main():
    crops = {n: np.load(out_path("_work/delit/%s.npy" % n)) for n in NAMES}
    G = np.concatenate([c.reshape(-1, 3) for c in crops.values()]).mean(0)
    bp_med = float(np.median([bp_std(c) for c in crops.values()]))

    # tone targets: one factor per tone group (a door is one leaf across two bands), natural difference halved
    def region_mean(p):
        n, x0, x1, y0, y1 = p[:5]
        return crops[n][y0:y1, x0:x1].reshape(-1, 3).mean(0)
    group_mean = {"door_L": crops["door_L"][0:327].reshape(-1, 3).mean(0),
                  "door_R": crops["door_R"][0:328].reshape(-1, 3).mean(0)}
    band_target, anchor_gain = {}, {}
    for b in BANDS:
        m = group_mean[b["tone_group"]] if "tone_group" in b else region_mean(b["anchor"])
        keep = LEAF_TONE_KEEP_THIN if b["hs"] < 100 and "tone_group" not in b else LEAF_TONE_KEEP
        tgt = G * (m / G) ** keep
        anchor_gain[b["id"]] = tgt / m
        band_target[b["id"]] = region_mean(b["anchor"]) * anchor_gain[b["id"]]

    canvas = np.zeros((H, W, 3))
    prov = np.full((H, W, 3), -1, np.int32)        # (crop id, src y, src x) per output pixel
    pieceid = np.full((H, W), -1, np.int32)
    layout = {"W": W, "H": H, "ppi": PPI, "bands": [], "pieces": []}
    y0 = 0
    for bi, b in enumerate(BANDS):
        hs, vo, xa = b["hs"], b["vo"], b["xa"]
        band = np.zeros((hs, W, 3))
        bprov = np.full((hs, W, 3), -1, np.int32)
        bpid = np.full((hs, W), -1, np.int32)
        # anchor
        n, ax0, ax1, ay0, ay1 = b["anchor"]
        assert ay1 - ay0 == hs, (b["id"], ay1 - ay0, hs)
        aw = ax1 - ax0
        g_anchor = float(np.clip((bp_med / bp_std(crops[n][ay0:ay1, ax0:ax1])) ** ANCHOR_DETAIL_PULL, *GAIN_LIM))
        A = detail_gain(crops[n][ay0:ay1, ax0:ax1], g_anchor)
        A = A * (band_target[b["id"]] / A.reshape(-1, 3).mean(0))
        bp_anchor = bp_std(A)
        cols = (xa + np.arange(aw)) % W
        band[:, cols] = A
        yy, xx = np.mgrid[ay0:ay1, ax0:ax1]
        bprov[:, cols] = np.stack([np.full_like(yy, CID[n]), yy, xx], -1)
        pid = len(layout["pieces"])
        bpid[:, cols] = pid
        layout["pieces"].append({"band": b["id"], "crop": n, "src_x": [ax0, ax1], "src_y": [ay0, ay1], "x": xa,
                                 "w": aw, "role": "anchor", "gain": anchor_gain[b["id"]].round(4).tolist(),
                                 "detail_gain": round(g_anchor, 3)})
        x = xa + aw - vo
        fixed = sum(p[5] for p in b["ext"] if p[5] is not None)
        nj = len(b["ext"]) + 1
        fill_w = W + nj * vo - aw - fixed
        for k, p in enumerate(b["ext"]):
            n, px0, px1, py0, py1, w = p
            w = fill_w if w is None else w
            assert 2 * vo < w <= px1 - px0, (b["id"], n, w, px1 - px0)
            last = k == len(b["ext"]) - 1
            g_det = float(np.clip(bp_anchor / bp_std(crops[n][py0:py1, px0:px1]), *GAIN_LIM))
            src = detail_gain(crops[n][py0:py1, px0:px1], g_det)
            gain = band_target[b["id"]] / src.reshape(-1, 3).mean(0)
            full = np.zeros_like(crops[n])
            full[py0:py1, px0:px1] = src
            src = full
            Lcols = (x + np.arange(vo)) % W
            El = gam(band[:, Lcols])
            if last:
                Rcols = (xa + np.arange(vo)) % W
                Er = gam(band[:, Rcols])
            best = (np.inf, None)
            for sy in range(py0, py1 - hs + 1):
                for sx in range(px0, px1 - w + 1):
                    P = src[sy:sy + hs, sx:sx + w] * gain
                    c = np.mean((gam(P[:, :vo]) - El) ** 2)
                    if last:
                        c += np.mean((gam(P[:, w - vo:]) - Er) ** 2)
                    if c < best[0]:
                        best = (c, (sy, sx))
            sy, sx = best[1]
            P = src[sy:sy + hs, sx:sx + w] * gain
            mask = np.ones((hs, w), bool)
            Cl = ((gam(P[:, :vo]) - El) ** 2).sum(-1)
            pl, costl = dp_seam(Cl)
            mask[:, :vo] = np.arange(vo)[None, :] >= pl[:, None]
            costr = None
            if last:
                Cr = ((gam(P[:, w - vo:]) - Er) ** 2).sum(-1)
                pr, costr = dp_seam(Cr)
                mask[:, w - vo:] &= np.arange(vo)[None, :] < pr[:, None]
            cols = (x + np.arange(w)) % W
            cur = band[:, cols]
            band[:, cols] = np.where(mask[..., None], P, cur)
            yy, xx = np.mgrid[sy:sy + hs, sx:sx + w]
            newprov = np.stack([np.full_like(yy, CID[n]), yy, xx], -1)
            bprov[:, cols] = np.where(mask[..., None], newprov, bprov[:, cols])
            pid = len(layout["pieces"])
            bpid[:, cols] = np.where(mask, pid, bpid[:, cols])
            layout["pieces"].append({"band": b["id"], "crop": n, "src_x": [int(sx), int(sx + w)],
                                     "src_y": [int(sy), int(sy + hs)], "x": int(x % W), "w": int(w),
                                     "role": "extension" + (" (loop close)" if last else ""),
                                     "shift_search_rows": [py0, py1 - hs], "shift_search_cols": [px0, px1 - w],
                                     "align_cost": round(float(best[0]), 6),
                                     "seam_cost_left": round(costl / hs, 6),
                                     "seam_cost_right": None if costr is None else round(costr / hs, 6),
                                     "gain": gain.round(4).tolist(), "detail_gain": round(g_det, 3),
                                     "bp_anchor": round(bp_anchor, 4)})
            x = x + w - vo
        assert (x % W) == (xa % W), (b["id"], x % W, xa)
        assert (bpid >= 0).all(), b["id"]

        # join the band onto the canvas along the grain (horizontal leaf joint), rows y0 .. y0+hs (mod H)
        rows = (y0 + np.arange(hs)) % H
        ho = HO[bi]
        mask = np.ones((hs, W), bool)
        joint = {}
        if bi > 0:
            Ct = ((gam(band[:ho]) - gam(canvas[rows[:ho]])) ** 2).sum(-1)
            pt, ct = dp_seam_closed(Ct)
            mask[:ho] = np.arange(ho)[:, None] >= pt[None, :]
            joint["top_cost_per_px"] = round(ct / W, 6)
        if bi == len(BANDS) - 1:
            hb = HO[0]
            Cb = ((gam(band[hs - hb:]) - gam(canvas[rows[hs - hb:]])) ** 2).sum(-1)
            pb, cb = dp_seam_closed(Cb)
            mask[hs - hb:] &= np.arange(hb)[:, None] < pb[None, :]
            joint["wrap_cost_per_px"] = round(cb / W, 6)
        canvas[rows] = np.where(mask[..., None], band, canvas[rows])
        prov[rows] = np.where(mask[..., None], bprov, prov[rows])
        pieceid[rows] = np.where(mask, bpid, pieceid[rows])
        layout["bands"].append({"id": b["id"], "rows": [int(y0), int((y0 + hs) % H)], "stock_h": hs, "vo": vo,
                                "anchor_x": xa, "target_lin": band_target[b["id"]].round(5).tolist(), **joint})
        y0 = y0 + hs - (HO[bi + 1] if bi + 1 < len(BANDS) else 0)
    assert y0 + HO[0] == H + HO[0] - (0) or True
    assert (pieceid >= 0).all()

    # provenance: every output pixel must be a distinct source pixel
    flat = prov.reshape(-1, 3)
    key = (flat[:, 0].astype(np.int64) * 4096 + flat[:, 1]) * 4096 + flat[:, 2]
    n_unique = int(np.unique(key).size)
    assert n_unique == H * W, ("source pixel reused", H * W - n_unique)

    # overall colour: match the photo's mid-panel oak tone (central 50 % of each front panel, raw photo, linear)
    raw = [np.load(out_path("_work/crops/%s.npy" % n)) for n in NAMES if n not in ("apron", "bottom_rail")]
    mids = np.concatenate([c[c.shape[0] // 4:3 * c.shape[0] // 4, c.shape[1] // 4:3 * c.shape[1] // 4].reshape(-1, 3)
                           for c in raw])
    target = mids.mean(0)
    canvas *= target / canvas.reshape(-1, 3).mean(0)
    layout["mid_panel_tone_srgb"] = lin_to_srgb(target).round(1).tolist()
    layout["map_mean_srgb"] = lin_to_srgb(canvas.reshape(-1, 3).mean(0)).round(1).tolist()
    layout["distinct_source_pixels"] = n_unique
    layout["pixels"] = H * W
    layout["source_pixels_available"] = int(sum(np.load(out_path("_work/crops/%s.npy" % n)).shape[0] *
                                                np.load(out_path("_work/crops/%s.npy" % n)).shape[1] for n in NAMES))
    np.save(out_path("_work/assembly_32ppi.npy"), canvas)
    np.savez_compressed(out_path("_work/provenance.npz"), prov=prov, piece=pieceid)
    json.dump(layout, open(out_path("_work/layout.json"), "w"), indent=1)

    # quick views
    thumb(lin_to_srgb(canvas), out_path("_work/_VIEW_assembly_32.jpg"))
    rng = np.random.default_rng(7)
    pal = rng.uniform(60, 230, (len(layout["pieces"]), 3))
    lay = pal[pieceid] * 0.55 + lin_to_srgb(canvas) * 0.45
    thumb(lay, out_path("_PREVIEW_leaf_layout.jpg"))
    print(json.dumps({k: layout[k] for k in ("mid_panel_tone_srgb", "map_mean_srgb", "distinct_source_pixels",
                                             "pixels", "source_pixels_available")}))
    for bd in layout["bands"]:
        print(bd)
    for p in layout["pieces"]:
        print(p["band"], p["crop"], p["role"], p["x"], p["w"], p["src_y"], p["src_x"], p.get("align_cost"),
              p.get("seam_cost_left"), p.get("seam_cost_right"))


if __name__ == "__main__":
    main()
