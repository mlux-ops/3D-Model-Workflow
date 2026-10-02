"""Measure the delivered maps against the acceptance gates and write textures/report.json."""
import json
import struct
import time
from scipy import ndimage, signal
from common import *
import srcs
import chis

Image.MAX_IMAGE_PIXELS = None
TEX = RUN + "/textures/"
H_LO, H_HI = -1.6, 0.8
JOINT_MM = 1.6
LUMV = np.array([0.299, 0.587, 0.114])
rep = {}


def png_header(p):
    with open(p, "rb") as f:
        b = f.read(33)
    assert b[:8] == b"\x89PNG\r\n\x1a\n" and b[12:16] == b"IHDR"
    w, h, bd, ct = struct.unpack(">IIBB", b[16:26])
    return dict(width=w, height=h, bit_depth=bd, colour_type=ct)


# ---------------------------------------------------------------- formats
rep["png_headers"] = {n: png_header(TEX + n) for n in ("Color.png", "Bump16.png", "face_ids.png")}
ph = rep["png_headers"]
rep["format_ok"] = bool(
    all((v["width"], v["height"]) == (W, H) for v in ph.values())
    and ph["Color.png"]["bit_depth"] == 8 and ph["Color.png"]["colour_type"] == 2
    and ph["Bump16.png"]["bit_depth"] == 16 and ph["Bump16.png"]["colour_type"] == 0
    and ph["face_ids.png"]["bit_depth"] == 16 and ph["face_ids.png"]["colour_type"] == 0)
print("headers", ph, rep["format_ok"])

col = np.asarray(Image.open(TEX + "Color.png")).astype(np.float32)
v16 = np.asarray(Image.open(TEX + "Bump16.png")).astype(np.float64)
ids = np.asarray(Image.open(TEX + "face_ids.png")).astype(np.int32)
hmm = v16 / 65535.0 * (H_HI - H_LO) + H_LO
meta = json.load(open(RUN + "/work/build_meta.json"))
tmap = {m["index"]: m["type"] for m in meta}

# ---------------------------------------------------------------- ids and joints
u = np.unique(ids)
rep["face_ids"] = dict(min=int(u.min()), max=int(u.max()), n_unique_faces=int((u > 0).sum()), all_1_to_56=bool(set(u[u > 0]) == set(range(1, 57))))
joint = ids == 0
rep["face_ids"]["joint_fraction"] = float(joint.mean())
exp_frac = 1.0 - 56 * (6 * 320.0 ** 2 / np.sqrt(3.0)) / (W * H)
rep["face_ids"]["joint_fraction_expected"] = float(exp_frac)


def runs(line):
    z = np.concatenate([[0], line.astype(np.int8), [0]])
    d = np.diff(z)
    s = np.where(d == 1)[0]; e = np.where(d == -1)[0]
    return e - s


vw = []                                    # horizontal joints measured vertically at hex column centres
for i in range(8):
    cx = int(round(W / 12.0 * (1 + 1.5 * i)))
    r = runs(joint[:, cx])
    vw += list(r)
rep["joint_width_px_vertical_runs"] = dict(values=sorted(set(int(x) for x in vw)), median=float(np.median(vw)))
# slanted edges: measure the run along the edge normal (30 deg from horizontal) by sampling map_coordinates
wn = []
for (i, j) in [(1, 1), (2, 2), (3, 3), (4, 2), (5, 4)]:
    cx = W / 12.0 * (1 + 1.5 * i); cy = 324.0 + 648.0 * j + (324.0 if i % 2 else 0)
    ang = np.deg2rad(30)                       # normal of the up-right edge (image coords, y down)
    n = np.array([np.cos(-ang), np.sin(-ang)])
    t = np.arange(-40, 40.01, 0.25)
    for frac in (0.3, 0.5, 0.7):
        # point on the up-right edge: apothem 320 along n, then slide along the edge
        tang = np.array([-n[1], n[0]])
        p = np.array([cx, cy]) + n * 324.0 + tang * (frac - 0.5) * 300
        xs = p[0] + n[0] * t; ys = p[1] + n[1] * t
        z = ndimage.map_coordinates((ids > 0).astype(np.float32), [ys, xs], order=1)
        wn.append(float((z < 0.5).sum() * 0.25))
rep["joint_width_px_edge_normal"] = dict(values=[round(x, 2) for x in wn], median=float(np.median(wn)))
print("joint width vertical", rep["joint_width_px_vertical_runs"], "normal", rep["joint_width_px_edge_normal"]["median"])
rep["joint_width_in"] = 8 / 64.0

# ---------------------------------------------------------------- joint values
jj = ndimage.binary_erosion(joint, iterations=2)
rep["joint_bump_v16_center"] = dict(min=int(v16[jj].min()), max=int(v16[jj].max()))
rep["joint_colour_rgb_center"] = col[jj].mean(0).round(1).tolist()

# ---------------------------------------------------------------- seams
def step(a, axis):
    """mean abs difference across the wrap vs mean abs difference between neighbouring lines inside the map."""
    if axis == 1:
        wrap = np.abs(a[:, 0] - a[:, -1]).mean(); inner = np.abs(a[:, 1:] - a[:, :-1]).mean()
    else:
        wrap = np.abs(a[0] - a[-1]).mean(); inner = np.abs(a[1:] - a[:-1]).mean()
    return float(wrap), float(inner)

sl = col @ LUMV
seam = {}
for name, arr, unit in (("colour_lum_8bit", sl, "levels"), ("bump_mm", hmm, "mm")):
    for ax, an in ((1, "x"), (0, "y")):
        w_, i_ = step(arr, ax)
        seam["%s_%s" % (name, an)] = dict(wrap_step=round(w_, 5), interior_step=round(i_, 5), ratio=round(w_ / i_, 3), unit=unit)
seam["colour_rgb_max_wrap_step_x"] = float(np.abs(col[:, 0] - col[:, -1]).max())
seam["colour_rgb_max_wrap_step_y"] = float(np.abs(col[0] - col[-1]).max())
def pct(a, axis):
    if axis == 1:
        w_ = np.abs(a[:, 0] - a[:, -1]); i_ = np.abs(a[:, 1:] - a[:, :-1])
    else:
        w_ = np.abs(a[0] - a[-1]); i_ = np.abs(a[1:] - a[:-1])
    return dict(wrap_p99=round(float(np.percentile(w_, 99)), 4), interior_p99=round(float(np.percentile(i_, 99)), 4),
                wrap_max=round(float(w_.max()), 4), interior_max=round(float(i_.max()), 4))

seam["percentiles"] = {"colour_lum_x": pct(sl, 1), "colour_lum_y": pct(sl, 0), "bump_mm_x": pct(hmm, 1), "bump_mm_y": pct(hmm, 0)}
seam["note_y"] = "rows 0 and H-1 both lie in the joint centre line of the even columns (joint centred on y=0), so the y wrap step is smaller than typical interior steps by construction; the x wrap crosses faces and junctions"
rep["seams"] = seam
print("seams", json.dumps(seam, indent=0))

# ---------------------------------------------------------------- relief
er = ndimage.binary_erosion(ids > 0, iterations=6)
rel = {}
for t in ("matte", "raw", "chiseled"):
    sel = np.isin(ids, [k for k, v in tmap.items() if v == t]) & er
    v = hmm[sel]
    face_mean = float(v.mean())
    p1, p99 = np.percentile(v, [1, 99])
    rel[t] = dict(face_mean_mm=round(face_mean, 4), rms_mm=round(float(v.std()), 4), p1_mm=round(float(p1), 3), p99_mm=round(float(p99), 3),
                  p1_p99_span_mm=round(float(p99 - p1), 3), min_mm=round(float(v.min()), 3), max_mm=round(float(v.max()), 3),
                  deepest_pattern_below_face_plane_mm=round(float(-v.min()), 3),
                  clearance_to_joint_floor_mm=round(float(JOINT_MM + v.min()), 3),
                  clearance_p1_to_joint_floor_mm=round(float(JOINT_MM + p1), 3))
    if t == "chiseled":
        # groove peak-to-valley from the per-face 1..99 percentile average
        pv = []
        for k in [k for k, v_ in tmap.items() if v_ == t]:
            s = (ids == k) & er
            a, b = np.percentile(hmm[s], [1, 99]); pv.append(b - a)
        rel[t]["per_face_p1_p99_span_mm_mean"] = round(float(np.mean(pv)), 3)
rel["joint_floor_mm"] = -JOINT_MM
rel["joint_step_mm_below_face_plane"] = JOINT_MM
rel["bump16_encoding"] = "mm = v/65535*(0.8-(-1.6)) + (-1.6); v=0 -> -1.6 mm (joint floor); face plane 0 mm = v 43690; full scale 2.4 mm"
rel["quantisation_mm_per_16bit_step"] = 2.4 / 65535
rep["relief"] = rel
print("relief", json.dumps(rel, indent=0))

# slopes (grazing legibility): max and p99 surface slope in degrees per type
gy, gx = np.gradient(hmm, 25.4 / 64.0)
sl_deg = np.degrees(np.arctan(np.hypot(gx, gy)))
rep["slope_deg"] = {}
for t in ("matte", "raw", "chiseled"):
    sel = np.isin(ids, [k for k, v in tmap.items() if v == t]) & er
    rep["slope_deg"][t] = dict(median=round(float(np.median(sl_deg[sel])), 2), p99=round(float(np.percentile(sl_deg[sel], 99)), 2))
print("slope", rep["slope_deg"])

# ---------------------------------------------------------------- mix
cnt = {t: sum(1 for v in tmap.values() if v == t) for t in ("matte", "raw", "chiseled")}
hexes = srcs.HEXES
full = [h for h in hexes if h["cov"] >= 0.97]
mfull = {t: sum(1 for h in full if srcs.classify(h) == t) for t in cnt}
mall = {t: sum(1 for h in hexes if srcs.classify(h) == t) for t in cnt}
rep["mix"] = dict(
    used_counts=cnt, used_pct={t: round(100 * v / 56, 1) for t, v in cnt.items()},
    measured_full_hexes=dict(n=len(full), counts=mfull, pct={t: round(100 * v / len(full), 1) for t, v in mfull.items()}),
    measured_all_visible_hexes=dict(n=len(hexes), counts=mall, pct={t: round(100 * v / len(hexes), 1) for t, v in mall.items()}))
print("mix", json.dumps(rep["mix"]))

# clumping: adjacency (wrap-aware)
import layout
lay = json.load(open(RUN + "/work/layout.json"))
grid = {(f["col"], f["row"]): f["type"] for f in lay}
adj = {"raw-raw": 0, "chiseled-chiseled": 0, "raw-chiseled": 0, "textured_with_no_textured_neighbour": 0}
same_orient = 0
orient = {(f["col"], f["row"]): f["groove_dir"] for f in lay}
for (i, j), t in grid.items():
    nb = layout.neighbours(i, j)
    if t != "matte" and all(grid[n] == "matte" for n in nb):
        adj["textured_with_no_textured_neighbour"] += 1
    for n in nb:
        if n > (i, j):
            pair = {t, grid[n]}
            if pair == {"raw"}: adj["raw-raw"] += 1
            elif pair == {"chiseled"}: adj["chiseled-chiseled"] += 1
            elif pair == {"raw", "chiseled"}: adj["raw-chiseled"] += 1
            if pair == {"chiseled"} and orient[(i, j)] == orient[n]:
                same_orient += 1
adj["chiseled_neighbours_same_direction"] = same_orient
rep["mix"]["adjacency_wrap_aware"] = adj
# largest connected textured cluster (wrap-aware)
seen = set(); best = 0
for k, t in grid.items():
    if t == "matte" or k in seen:
        continue
    stack = [k]; seen.add(k); n = 0
    while stack:
        c = stack.pop(); n += 1
        for m in layout.neighbours(*c):
            if grid[m] != "matte" and m not in seen:
                seen.add(m); stack.append(m)
    best = max(best, n)
rep["mix"]["largest_textured_cluster_faces"] = best
print("adjacency", adj, "largest textured cluster", best)

# ---------------------------------------------------------------- repetition
t0 = time.time()
rng = np.random.default_rng(7)
Hh = hmm.astype(np.float32)
hp = Hh - ndimage.gaussian_filter(Hh, 6.0)                        # remove low frequency for correlation
lumc = (sl - ndimage.gaussian_filter(sl, 8.0)).astype(np.float32)

LAST = []


def patch_search(field, face_ids_sel, n_patches, P=112, exclude=40, label=""):
    """for random patches inside faces of a type, best normalised correlation against the same-type areas of the whole atlas (8 dihedral variants)."""
    m = np.isin(ids, face_ids_sel) & ndimage.binary_erosion(ids > 0, iterations=P // 2 + 4)
    fm = np.where(np.isin(ids, face_ids_sel), 1.0, 0.0).astype(np.float32)
    ys, xs = np.where(m)
    pick = rng.choice(len(ys), n_patches, replace=False)
    f = field.astype(np.float32)
    f2 = f * f
    kern = np.ones((P, P), np.float32)
    # local sums for normalisation (same-type mask applied so background does not win)
    fmasked = f * fm
    s1 = signal.fftconvolve(fmasked, kern, mode="same")
    s2 = signal.fftconvolve(f2 * fm, kern, mode="same")
    sm = signal.fftconvolve(fm, kern, mode="same")
    out = []
    for k in pick:
        y, x = ys[k], xs[k]
        pt = f[y - P // 2:y + P // 2, x - P // 2:x + P // 2]
        ptz = pt - pt.mean()
        pn = np.sqrt((ptz ** 2).sum())
        best = -1.0; where = None
        for tr in range(8):
            q = np.rot90(ptz, tr % 4)
            if tr >= 4:
                q = q[:, ::-1]
            q = np.ascontiguousarray(q)
            cc = signal.fftconvolve(fmasked, q[::-1, ::-1], mode="same")
            # numerator with mean removal: sum(f*q) - mean(q)*... q already zero-mean so numerator is exact
            den = np.sqrt(np.maximum(s2 - s1 * s1 / np.maximum(sm, 1), 1e-6)) * pn
            ncc = cc / den
            ncc[sm < 0.9 * P * P] = -1                             # only windows completely inside same-type faces
            y0, y1 = max(0, y - exclude), min(H, y + exclude + 1)
            x0, x1 = max(0, x - exclude), min(W, x + exclude + 1)
            ncc[y0:y1, x0:x1] = -1
            mx = float(ncc.max())
            if mx > best:
                yy_, xx_ = np.unravel_index(int(ncc.argmax()), ncc.shape)
                best = mx; where = (int(yy_), int(xx_), tr)
        out.append(best)
        LAST.append(dict(ncc=best, y=int(y), x=int(x), match=where, P=P))
    return out

raw_ids = [k for k, v in tmap.items() if v == "raw"]
mat_ids = [k for k, v in tmap.items() if v == "matte"]
# baseline: the same statistic for two different source-independent noise fields is ~0.2-0.4 at P=112
rp = patch_search(hp, raw_ids, int(__import__("os").environ.get("PROBES", 6)), label="raw height")
json.dump(list(LAST), open(guard(RUN + "/work/raw_patch_matches.json"), "w"))
LAST.clear()
mp_ = patch_search(lumc, mat_ids, int(__import__("os").environ.get("PROBES", 6)), label="matte colour")
mat_info = list(LAST)
json.dump(mat_info, open(guard(RUN + "/work/matte_patch_matches.json"), "w"))
rep["repetition"] = dict(
    raw_height_patch112_best_ncc_vs_rest=dict(values=[round(x, 3) for x in rp], max=round(max(rp), 3), median=round(float(np.median(rp)), 3)),
    matte_colour_patch112_best_ncc_vs_rest=dict(values=[round(x, 3) for x in mp_], max=round(max(mp_), 3), median=round(float(np.median(mp_)), 3)),
    note="normalised cross-correlation of random 112 px (1.75 in) patches against all other same-type faces, 8 rotations/mirrors, self area excluded; a copied patch would score >0.9")
print("repetition", rep["repetition"], "%.0fs" % (time.time() - t0))

# whole-face raw vs raw: 8 dihedral variants of the central 480 px block
def core(k):
    m = meta[[m_["index"] for m_ in meta].index(k)]
    cx, cy = int(round(m["cx"])), int(round(m["cy"]))
    ys = np.arange(cy - 240, cy + 240) % H; xs = np.arange(cx - 240, cx + 240) % W
    return hp[np.ix_(ys, xs)]

cores = {k: core(k) for k in raw_ids}
worst = (0, None)
for a in raw_ids:
    A = cores[a] - cores[a].mean()
    for b in raw_ids:
        if b <= a:
            continue
        B0 = cores[b] - cores[b].mean()
        for tr in range(8):
            B = np.rot90(B0, tr % 4)
            if tr >= 4:
                B = B[:, ::-1]
            cc = signal.fftconvolve(A, np.ascontiguousarray(B[::-1, ::-1]), mode="full")
            # global normalised peak on the overlap-limited window; use coarse normalisation
            ncc = cc.max() / (np.sqrt((A ** 2).sum() * (B ** 2).sum()))
            if ncc > worst[0]:
                worst = (float(ncc), (a, b, tr))
rep["repetition"]["raw_face_pairs_max_peak_ncc_8_dihedral"] = dict(value=round(worst[0], 3), pair_and_transform=worst[1])
print("raw face pairs worst", worst)

# chiseled: compare envelope and phase-wobble fields between same-orientation faces
cm = [m for m in meta if m["type"] == "chiseled"]
K = chis.K_SRC / srcs.F_UP
fields = {}
for m in cm:
    a = np.deg2rad(float(m["rotation_deg"]))
    cx, cy = int(round(m["cx"])), int(round(m["cy"]))
    ys = np.arange(cy - 200, cy + 200) % H; xs = np.arange(cx - 200, cx + 200) % W
    blk = Hh[np.ix_(ys, xs)]
    Y, X = np.mgrid[-200:200, -200:200].astype(np.float32)
    t = X * (-np.sin(a)) + Y * np.cos(a)
    z = ndimage.gaussian_filter(blk * np.cos(K * t), 9.0) + 1j * ndimage.gaussian_filter(blk * (-np.sin(K * t)), 9.0)
    env = np.abs(z)
    ph_ = np.unwrap(np.unwrap(np.angle(z), axis=0), axis=1)
    yy, xx = np.mgrid[0:400, 0:400]
    Amat = np.stack([xx.ravel(), yy.ravel(), np.ones(400 * 400)], 1)
    coef, *_ = np.linalg.lstsq(Amat[::7], ph_.ravel()[::7], rcond=None)
    wob = ph_ - (Amat @ coef).reshape(400, 400)
    fields[m["index"]] = (env, wob, float(np.degrees(wob.std())))
res_pairs = []
for x in cm:
    for y in cm:
        if y["index"] <= x["index"] or x["rotation_deg"] != y["rotation_deg"]:
            continue
        e1, w1, _ = fields[x["index"]]; e2, w2, _ = fields[y["index"]]
        best = -1
        for tr in range(4):
            a2 = e2 if tr == 0 else (e2[::-1] if tr == 1 else (e2[:, ::-1] if tr == 2 else e2[::-1, ::-1]))
            best = max(best, float(np.corrcoef((e1 - e1.mean()).ravel(), (a2 - a2.mean()).ravel())[0, 1]))
        res_pairs.append(best)
rep["repetition"]["chiseled_same_direction_envelope_ncc"] = dict(n_pairs=len(res_pairs), max=round(max(res_pairs), 3) if res_pairs else None)
rep["chiseled_groove_wobble"] = dict(phase_wobble_std_deg_per_face={str(k): round(v[2], 1) for k, v in fields.items()},
                                     envelope_cv_per_face={str(k): round(float(v[0].std() / v[0].mean()), 3) for k, v in fields.items()})
print("chis env ncc", rep["repetition"]["chiseled_same_direction_envelope_ncc"], "wobble", rep["chiseled_groove_wobble"])


# ---------------------------------------------------------------- fidelity: colour and texture energy vs the render (render scale)
fm = {k: col[(ids == k) & er].astype(np.float64).mean(0) for k in tmap}
def hpf(l, s1=1.5, s2=12.0):
    return ndimage.gaussian_filter(l, s1) - ndimage.gaussian_filter(l, s2)
small = ndimage.zoom(sl.astype(np.float32), 1.0 / srcs.F_UP, order=1)
idsS = ndimage.zoom(ids.astype(np.float32), 1.0 / srcs.F_UP, order=0).astype(np.int32)
hpA = hpf(small)
innerS = ndimage.binary_erosion(idsS > 0, iterations=14)
lumR = np.asarray(srcs._im).astype(np.float32) @ LUMV
hpR = hpf(lumR)
fid = {}
for t in ("matte", "raw", "chiseled"):
    ks = [k for k, v in tmap.items() if v == t]
    e_a = float(np.concatenate([hpA[(idsS == k) & innerS] for k in ks]).std())
    vals, cols = [], []
    for h_ in srcs.HEXES:
        if srcs.classify(h_) != t:
            continue
        x0, y0, w_, hh_ = srcs.window_of(h_)
        m_ = srcs.hex_mask_window(h_["cx"], h_["cy"], 0.85, x0, y0, w_, hh_)
        if m_.sum() > 6000:
            vals.append(srcs.crop(hpR, x0, y0, w_, hh_)[m_])
            cols.append(srcs.crop(srcs._im, x0, y0, w_, hh_)[m_].mean(0))
    fid[t] = dict(atlas_mean_rgb=np.mean([fm[k] for k in ks], 0).round(1).tolist(),
                  render_mean_rgb=np.mean(cols, 0).round(1).tolist(),
                  atlas_face_to_face_lum_std=round(float(np.std([fm[k].mean() for k in ks])), 2),
                  render_hex_to_hex_lum_std=round(float(np.std([c.mean() for c in cols])), 2),
                  atlas_texture_energy_hp_std=round(e_a, 3),
                  render_texture_energy_hp_std=round(float(np.concatenate(vals).std()), 3))
rep["fidelity_vs_render"] = fid
rep["fidelity_vs_render_note"] = "texture energy = std of luminance band-passed (gauss 1.5 px minus 12 px) at render scale (atlas resampled by 1/2.0585); colour = mean over the inner 85 % of each hexagon"
print("fidelity", json.dumps(fid))

rep["sample_size"] = dict(width_in=W / 64.0, height_in=H / 64.0, width_str="5'-10.148in", height_str="5'-10.875in",
                          note="4489/64 = 70.1406 in and 4536/64 = 70.875 in; the brief's 70.148 in is 70.1406 rounded up by 0.0074 in (0.01 %)")
rep["size_assumption"] = "10.000 in across flats (flat-top), 1/8 in joint, 10.125 in module; if the tile is really 10 in point-to-point, scale everything by 0.866"
rep["suggested_revit_bump"] = dict(editor_scale_value=100, stored_value=1.0,
                                   basis="AGENTS.md calibration for a full-range dimensional map (2.6 mm full scale, 1.6 mm joint) was 100 on the editor scale; this map is 2.4 mm full scale with the same 1.6 mm joint, so start at 100 (about 8 % less amplitude per unit than that calibration)")

# ---------------------------------------------------------------- per face table
faces = []
for m in meta:
    faces.append(dict(index=m["index"], type=m["type"], rotation_deg=(int(m["rotation_deg"]) if m["rotation_deg"] is not None else 0),
                      mirrored=False, source=m["source_patches"],
                      note_source="dict = number of quilt patches (render-hex label i<col>j<row>) that were cut from each source hexagon in the render"))
rep["faces"] = faces
json.dump(rep, open(guard(TEX + "report.json"), "w"), indent=1, default=str)
print("wrote report.json")
