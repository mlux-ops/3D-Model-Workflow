"""Step 11: verification of the delivered maps and textures/report.json.

Everything is measured from the PNG files themselves (IHDR header bytes, face_ids.png, Bump16.png,
Color.png) together with the layout / inventory JSON of the earlier steps. Only the atlas geometry
constants are shared with the build.

python s11_verify.py     ->  textures/report.json  (plus a printed summary)

Sections of report.json: atlas, formats, face_ids, joints, wrap_seam_steps, relief, grooves, colour,
mix, arrangement, repetition, sample_size, checks, faces (56 entries)."""

import json
import os
import sys
import time
from collections import Counter

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from guard import out_path, save_text, png_header  # noqa: E402
from geometry import (W, H, MM_PER_PX, PPI, N_FACES, NCOL, NROW, MODULE, INSET, FACE_FLATS,  # noqa: E402
                      face_centres, neighbour_lists, hex_inside, window_indices, window_offsets, torus_delta)
from design import JOINT_RGB, FULL_SCALE_MM  # noqa: E402
from s08_raw_height import face_centre  # noqa: E402
from s10a_layout import lattice_tables, layout_metrics  # noqa: E402

MM_PER_LEVEL = FULL_SCALE_MM / 65535.0
HALF = 384
RNG_SEED = 20260929
EL_DEG = 20.0
TARGET_DIR_DEG = {"vert": 90.0, "diagS": 30.0, "diagF": 150.0}
EXPECT = {
    "Color.png": (W, H, 8, 2, "8-bit RGB"),
    "Bump16.png": (W, H, 16, 0, "16-bit greyscale"),
    "face_ids.png": (W, H, 16, 0, "16-bit greyscale"),
}


def py(x, nd=6):
    """numpy -> plain python for json, floats rounded to nd decimals."""
    if isinstance(x, dict):
        return {str(k): py(v, nd) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [py(v, nd) for v in x]
    if isinstance(x, np.ndarray):
        return py(x.tolist(), nd)
    if isinstance(x, (np.bool_, bool)):
        return bool(x)
    if isinstance(x, (np.integer, int)):
        return int(x)
    if isinstance(x, (np.floating, float)):
        return round(float(x), nd)
    return x


def check_formats():
    out = {}
    for name, (w, h, depth, ctype, label) in EXPECT.items():
        p = out_path("textures", name)
        got = png_header(p)
        out[name] = {"ihdr_width": got[0], "ihdr_height": got[1], "ihdr_bit_depth": got[2],
                     "ihdr_colour_type": got[3], "expected": "%dx%d %s (colour type %d)" % (w, h, label, ctype),
                     "ok": got == (w, h, depth, ctype), "file_bytes": os.path.getsize(p)}
    return out


def load_maps():
    im = Image.open(out_path("textures", "Color.png"))
    assert im.mode == "RGB", im.mode
    colour = np.asarray(im).astype(np.int16)
    level = np.asarray(Image.open(out_path("textures", "Bump16.png"))).astype(np.uint16)
    fid = np.asarray(Image.open(out_path("textures", "face_ids.png"))).astype(np.uint16)
    assert colour.shape == (H, W, 3) and level.shape == (H, W) and fid.shape == (H, W)
    return colour, level, fid


def ownership(centres):
    owner = np.zeros((H, W), np.int16)
    best = np.full((H, W), -1e9, np.float32)
    for c in centres:
        _, _, xi, yi = window_indices(c["cx"], c["cy"], HALF)
        dx, dy = window_offsets(c["cx"], c["cy"], HALF)
        ins = hex_inside(dx, dy).astype(np.float32)
        ix = np.ix_(yi, xi)
        cur = best[ix]
        upd = ins > cur
        best[ix] = np.where(upd, ins, cur)
        owner[ix] = np.where(upd, np.int16(c["index"]), owner[ix])
    return owner, best


def bilinear_wrap(a, px, py_):
    x, y = px - 0.5, py_ - 0.5
    x0, y0 = np.floor(x).astype(np.int64), np.floor(y).astype(np.int64)
    fx, fy = x - x0, y - y0
    x0m, x1m, y0m, y1m = x0 % W, (x0 + 1) % W, y0 % H, (y0 + 1) % H
    return (a[y0m, x0m] * (1 - fx) * (1 - fy) + a[y0m, x1m] * fx * (1 - fy)
            + a[y1m, x0m] * (1 - fx) * fy + a[y1m, x1m] * fx * fy)


def face_id_checks(fid, owner, own_in, centres, rng):
    ids = np.unique(fid)
    counts = np.bincount(fid.ravel(), minlength=N_FACES + 1)
    ideal_face = (np.sqrt(3.0) / 2.0) * FACE_FLATS ** 2
    expected = np.where(own_in >= 4.0, owner, 0).astype(np.uint16)
    mismatch = int((fid != expected).sum())
    cx = np.array([c["cx"] for c in centres])
    cy = np.array([c["cy"] for c in centres])
    xs, ys = rng.integers(0, W, 400000), rng.integers(0, H, 400000)
    keep = fid[ys, xs] > 0
    xs, ys = xs[keep][:200000], ys[keep][:200000]
    px, py_ = xs + 0.5, ys + 0.5
    dxm = torus_delta(px[:, None], cx[None, :], W)
    dym = torus_delta(py_[:, None], cy[None, :], H)
    nearest = np.argmin(dxm ** 2 + dym ** 2, axis=1) + 1
    voronoi_mismatch = int((nearest != fid[ys, xs]).sum())
    areas = counts[1:]
    return {
        "unique_values_min_max": [int(ids.min()), int(ids.max())],
        "all_56_indices_present": bool(np.array_equal(ids[ids > 0], np.arange(1, N_FACES + 1))),
        "joint_pixels_are_zero_count": int(counts[0]),
        "joint_pixel_fraction": float(counts[0]) / fid.size,
        "face_area_px_min_mean_max": [int(areas.min()), float(areas.mean()), int(areas.max())],
        "ideal_10in_flat_hexagon_area_px": float(ideal_face),
        "mismatch_vs_geometry_pixels": mismatch,
        "voronoi_nearest_centre_mismatch_in_200000_random_face_pixels": voronoi_mismatch,
    }


def joint_widths(fid, level, centres, face_level):
    """Joint width measured along the normal of every ring-1 edge (168 edges x 9 positions)."""
    rings = neighbour_lists(centres)
    s = np.arange(-14.0, 14.0, 0.05)
    tpos = np.linspace(-100.0, 100.0, 9)
    res = {"horizontal": {"id": [], "half": []}, "slanted": {"id": [], "half": []}}
    thr = 0.5 * face_level
    pairs = sorted({(min(a, b), max(a, b)) for a in range(N_FACES) for b in rings[0][a]})
    for a, b in pairs:
        dx = torus_delta(centres[a]["cx"], centres[b]["cx"], W)
        dy = torus_delta(centres[a]["cy"], centres[b]["cy"], H)
        d = float(np.hypot(dx, dy))
        nx, ny = dx / d, dy / d
        ex, ey = -ny, nx
        mx, my = centres[a]["cx"] + dx / 2.0, centres[a]["cy"] + dy / 2.0
        kind = "horizontal" if abs(ny) > 0.9 else "slanted"
        for t in tpos:
            px = mx + t * ex + s * nx
            py_ = my + t * ey + s * ny
            ids = fid[np.floor(py_).astype(np.int64) % H, np.floor(px).astype(np.int64) % W]
            res[kind]["id"].append(float((ids == 0).sum() * 0.05))
            lv = bilinear_wrap(level, px, py_)
            res[kind]["half"].append(float((lv < thr).sum() * 0.05))
    out = {"edges_measured": len(pairs), "positions_per_edge": len(tpos)}
    for kind in res:
        for src, arr in res[kind].items():
            arr = np.array(arr)
            out["%s_edges_%s_width_px" % (kind, "face_id_zero_run" if src == "id" else "bump_half_depth")] = {
                "n": int(arr.size), "mean": float(arr.mean()), "min": float(arr.min()), "max": float(arr.max())}
    allid = np.array(res["horizontal"]["id"] + res["slanted"]["id"])
    allhalf = np.array(res["horizontal"]["half"] + res["slanted"]["half"])
    out["all_edges_face_id_zero_run_px_mean_min_max"] = [float(allid.mean()), float(allid.min()), float(allid.max())]
    out["all_edges_bump_half_depth_width_px_mean_min_max"] = [float(allhalf.mean()), float(allhalf.min()), float(allhalf.max())]
    return out


def joint_area_width(fid):
    """Second, geometry-free width estimate: joint area / total joint centreline length."""
    area = float((fid == 0).sum())
    side = MODULE / np.sqrt(3.0)
    length = N_FACES * 6.0 * side / 2.0
    ideal = N_FACES * (np.sqrt(3.0) / 2.0) * (MODULE ** 2 - FACE_FLATS ** 2)
    return {"joint_area_px": area, "total_centreline_length_px": length, "mean_width_px": area / length,
            "ideal_joint_area_px_exact_hexagons": float(ideal), "measured_over_ideal_area": area / float(ideal),
            "note": "area / length is below 8 px because the three bands overlap at each of the 112 vertices; the "
                    "0.5 % area shortfall against the exact-hexagon area is the atlas width 4489 px versus 4489.5 px"}


def run_lengths_zero(fid, axis_name):
    """Histogram of joint run lengths along vertical (columns) or horizontal (rows) scan lines."""
    a = (fid == 0)
    if axis_name == "vertical":
        a = a.T
    hist = Counter()
    for row in a[:: 7]:
        d = np.diff(np.concatenate([[0], row.astype(np.int8), [0]]))
        starts, ends = np.nonzero(d == 1)[0], np.nonzero(d == -1)[0]
        for L in (ends - starts):
            hist[int(L)] += 1
    total = sum(hist.values())
    top = hist.most_common(4)
    return {"scan_lines": int(a[::7].shape[0]), "runs": total, "most_common_run_lengths_px": [[k, v] for k, v in top]}


def step_stats(a, axis, rng):
    """Wrap pair vs interior pairs along axis (1 = x, 0 = y). a: int16 (H,W) or (H,W,3)."""
    a = a if a.ndim == 3 else a[..., None]
    n = a.shape[axis]
    if axis == 1:
        first, last = a[:, 0], a[:, n - 1]
    else:
        first, last = a[0], a[n - 1]
    seam = np.abs(first.astype(np.float32) - last.astype(np.float32)).mean(axis=-1)
    pair_means = np.zeros(n - 1, np.float64)
    pooled = []
    sample_pairs = set(rng.choice(n - 1, 300, replace=False).tolist())
    for k in range(n - 1):
        if axis == 1:
            d = np.abs(a[:, k + 1].astype(np.float32) - a[:, k].astype(np.float32)).mean(axis=-1)
        else:
            d = np.abs(a[k + 1].astype(np.float32) - a[k].astype(np.float32)).mean(axis=-1)
        pair_means[k] = d.mean()
        if k in sample_pairs:
            pooled.append(d)
    pooled = np.concatenate(pooled)
    seam_mean = float(seam.mean())
    return {
        "seam_step_mean_abs": seam_mean,
        "interior_pair_mean_abs_median": float(np.median(pair_means)),
        "interior_pair_mean_abs_p99": float(np.percentile(pair_means, 99)),
        "interior_pair_mean_abs_max": float(pair_means.max()),
        "seam_over_interior_median": seam_mean / float(np.median(pair_means)),
        "seam_percentile_rank_among_interior_pairs": float((pair_means <= seam_mean).mean()),
        "per_pixel_p99_seam": float(np.percentile(seam, 99)),
        "per_pixel_p99_interior_pooled": float(np.percentile(pooled, 99)),
        "per_pixel_max_seam": float(seam.max()),
        "per_pixel_max_interior_pooled": float(pooled.max()),
        "seam_ok_not_above_interior_p99": bool(seam_mean <= np.percentile(pair_means, 99)),
    }


def lambert_r(gx, gy, az_deg, el_deg=EL_DEG, gain=0.9):
    az, el = np.deg2rad(az_deg), np.deg2rad(el_deg)
    lx, ly, lz = float(np.cos(el) * np.cos(az)), float(np.cos(el) * np.sin(az)), float(np.sin(el))
    r = (lz - gx * lx - gy * ly) / np.sqrt(1.0 + gx * gx + gy * gy) / lz
    return np.clip(gain * r, 0.0, 1.25)


def relief_report(level, tmap, own_in, owner, layout_faces, centres, psi_light):
    hmm = level.astype(np.float32) * MM_PER_LEVEL
    core = own_in >= 6.0
    jcore = own_in <= 2.0
    codes = {"matte": 1, "raw": 2, "chiseled_vert": 3, "chiseled_diagS": 4, "chiseled_diagF": 5}
    matte = core & (tmap == 1)
    face_level = int(np.median(level[matte]))
    matte_levels = np.unique(level[matte])
    joint_levels = np.unique(level[jcore])
    face_mm = face_level * MM_PER_LEVEL
    joint_mm = float(np.median(hmm[jcore]))
    gy, gx = np.gradient(hmm, MM_PER_PX)
    rB = lambert_r(gx, gy, psi_light + 90.0)
    rR = lambert_r(gx, gy, psi_light)
    out = {
        "mm_per_bump_level": MM_PER_LEVEL, "bump_full_scale_mm": FULL_SCALE_MM,
        "face_plane_level": face_level, "face_plane_mm_above_joint_floor": face_mm,
        "joint_floor_level_values": [int(joint_levels.min()), int(joint_levels.max())],
        "joint_depth_mm": face_mm - joint_mm,
        "matte_face_distinct_levels": int(matte_levels.size),
        "matte_max_abs_dev_from_face_plane_mm": float(np.abs(hmm[matte] - face_mm).max()),
        "shading_light_azimuths_deg": {"light_B": psi_light + 90.0, "light_R_render_axis": psi_light},
        "shading_elevation_deg": EL_DEG,
        "types": {},
    }
    for name in ("matte", "raw", "chiseled", "chiseled_vert", "chiseled_diagS", "chiseled_diagF"):
        if name == "chiseled":
            m = core & (tmap >= 3)
        else:
            m = core & (tmap == codes[name])
        h = hmm[m]
        rel = h - face_mm
        sl2 = gx[m] ** 2 + gy[m] ** 2
        p1, p99 = np.percentile(h, [1, 99])
        out["types"][name] = {
            "faces": int(len({int(v) for v in np.unique(owner[m])})),
            "pixels": int(m.sum()),
            "height_mm_above_joint_floor_min_p1_median_p99_max": [float(h.min()), float(p1), float(np.median(h)), float(p99), float(h.max())],
            "relief_vs_face_plane_mm_min_max": [float(rel.min()), float(rel.max())],
            "pattern_relief_p1_to_p99_mm": float(p99 - p1),
            "pattern_relief_rms_about_type_mean_mm": float(h.std()),
            "deepest_pattern_point_below_face_plane_mm": float(face_mm - h.min()),
            "clearance_deepest_point_to_joint_floor_mm": float(h.min() - joint_mm),
            "clearance_as_fraction_of_joint_depth": float((h.min() - joint_mm) / (face_mm - joint_mm)),
            "slope_rms_mm_per_mm": float(np.sqrt(sl2.mean())),
            "slope_p99_mm_per_mm": float(np.percentile(np.sqrt(sl2), 99)),
            "relief_p1_to_p99_as_fraction_of_full_grey_range": float((p99 - p1) / FULL_SCALE_MM),
            "lambert_ratio_std_light_B_20deg": float(rB[m].std()),
            "lambert_ratio_std_light_R_20deg": float(rR[m].std()),
        }
    pat = core & (tmap >= 2)
    out["pattern_faces_raw_and_chiseled"] = {
        "deepest_point_mm_above_joint_floor": float(hmm[pat].min()),
        "clearance_to_joint_floor_mm": float(hmm[pat].min() - joint_mm),
        "joint_depth_mm": face_mm - joint_mm,
        "grey_range_share_joint_step": float((face_mm - joint_mm) / FULL_SCALE_MM),
    }
    per_face = {}
    for f, c in zip(layout_faces, centres):
        _, _, xi, yi = window_indices(c["cx"], c["cy"], HALF)
        ix = np.ix_(yi, xi)
        m = core[ix] & (owner[ix] == f["index"])
        h = hmm[ix][m]
        s2 = gx[ix][m] ** 2 + gy[ix][m] ** 2
        per_face[f["index"]] = {
            "height_min_mm": float(h.min()), "height_max_mm": float(h.max()),
            "clearance_to_joint_floor_mm": float(h.min() - joint_mm),
            "relief_std_mm": float(h.std()), "slope_rms": float(np.sqrt(s2.mean())),
        }
    del gx, gy, rB, rR
    return out, per_face, hmm


def groove_report(hmm, layout_faces, centres):
    """Groove direction and pitch of every Chiseled face, measured from Bump16 (windowed FFT peak)."""
    n_win, n_fft = 400, 2048
    hw = np.outer(np.hanning(n_win), np.hanning(n_win))
    fx = np.fft.fftfreq(n_fft)
    FX, FY = np.meshgrid(fx, fx)
    rad = np.hypot(FX, FY)
    ann = (rad > 0.05) & (rad < 0.12)
    out = {}
    for f, c in zip(layout_faces, centres):
        if f["type"] != "chiseled":
            continue
        _, _, xi, yi = window_indices(c["cx"], c["cy"], n_win // 2)
        blk = hmm[np.ix_(yi, xi)].astype(np.float64)
        blk = (blk - blk.mean()) * hw
        p = np.abs(np.fft.fft2(blk, s=(n_fft, n_fft))) ** 2
        pa = np.where(ann, p, 0.0)
        k = int(np.argmax(pa))
        ky, kx = np.unravel_index(k, pa.shape)
        fkx, fky = FX[ky, kx], FY[ky, kx]
        theta_k = np.degrees(np.arctan2(fky, fkx))
        line_dir = (theta_k + 90.0) % 180.0
        pitch_px = 1.0 / np.hypot(fkx, fky)
        target = TARGET_DIR_DEG[f["orientation"]]
        dev = (line_dir - target + 90.0) % 180.0 - 90.0
        out[f["index"]] = {
            "orientation": f["orientation"], "measured_groove_direction_deg": float(line_dir),
            "expected_direction_deg": target, "deviation_deg": float(dev),
            "pitch_px": float(pitch_px), "pitch_mm": float(pitch_px * MM_PER_PX),
            "peak_to_annulus_mean_power": float(pa.max() / pa[ann].mean()),
        }
    return out


def mix_report(pool_info, faces):
    n = len(faces)
    used = Counter(f["type"] for f in faces)
    render = {"matte": len(pool_info["matte"]), "raw": len(pool_info["raw"]), "chiseled": len(pool_info["chiseled"])}
    nr = sum(render.values())
    r_or = Counter(c["kind"] for c in pool_info["chiseled"])
    u_or = Counter(f["orientation"] for f in faces if f["type"] == "chiseled")
    frac = lambda d, tot: {k: d[k] / tot for k in ("matte", "raw", "chiseled")}
    fr, fu = frac(render, nr), frac(used, n)
    return {
        "render_whole_hexagons_counted": nr,
        "render_counts": render, "render_fractions": fr,
        "atlas_counts": {k: used[k] for k in ("matte", "raw", "chiseled")}, "atlas_fractions": fu,
        "abs_difference_percentage_points": {k: 100.0 * abs(fr[k] - fu[k]) for k in fr},
        "render_chiseled_orientation_counts": {k: r_or[k] for k in ("vert", "diagS", "diagF")},
        "atlas_chiseled_orientation_counts": {k: u_or[k] for k in ("vert", "diagS", "diagF")},
        "render_chiseled_orientation_fractions": {k: r_or[k] / sum(r_or.values()) for k in ("vert", "diagS", "diagF")},
        "atlas_chiseled_orientation_fractions": {k: u_or[k] / sum(u_or.values()) for k in ("vert", "diagS", "diagF")},
        "render_note": "39 whole hexagons; the partly visible hexagons at the image border are not counted",
    }


def arrangement_report(faces, centres, rng, n_perm=20000):
    rings = neighbour_lists(centres)
    codes = np.array([{"matte": 0, "raw": 1, "chiseled": 2}[f["type"]] for f in faces])
    edges = sorted({(min(a, b), max(a, b)) for a in range(N_FACES) for b in rings[0][a]})
    ea, eb = np.array([e[0] for e in edges]), np.array([e[1] for e in edges])
    perms = rng.permuted(np.tile(codes, (n_perm, 1)), axis=1)
    pa, pb = perms[:, ea], perms[:, eb]
    out = {"ring1_edges": len(edges), "random_arrangements": n_perm, "same_type_neighbour_pairs": {}}
    for t, name in enumerate(("matte", "raw", "chiseled")):
        obs = int(((codes[ea] == t) & (codes[eb] == t)).sum())
        rnd = ((pa == t) & (pb == t)).sum(axis=1)
        out["same_type_neighbour_pairs"][name] = {
            "observed": obs, "random_mean": float(rnd.mean()), "random_std": float(rnd.std()),
            "z": float((obs - rnd.mean()) / rnd.std()), "fraction_of_random_with_count_le_observed": float((rnd <= obs).mean())}
    # ring 1 + ring 2 same-orientation Chiseled pairs
    ori = np.array([f["orientation"] or "" for f in faces])
    near = set()
    for r in (0, 1):
        for a in range(N_FACES):
            for b in rings[r][a]:
                near.add((min(a, b), max(a, b)))
    same_or = sum(1 for a, b in near if ori[a] and ori[a] == ori[b])
    out["chiseled_same_orientation_pairs_ring1_and_ring2"] = int(same_or)
    # dispersion (Clark-Evans style mean nearest-neighbour distance, torus) of the special faces
    D = np.zeros((N_FACES, N_FACES))
    for a in range(N_FACES):
        for b in range(N_FACES):
            D[a, b] = np.hypot(torus_delta(centres[a]["cx"], centres[b]["cx"], W),
                               torus_delta(centres[a]["cy"], centres[b]["cy"], H))
    np.fill_diagonal(D, np.inf)
    out["dispersion_mean_nearest_neighbour_distance"] = {}
    for name, sel in (("raw", codes == 1), ("chiseled", codes == 2), ("raw_and_chiseled", codes >= 1)):
        idx = np.nonzero(sel)[0]
        obs = float(D[np.ix_(idx, idx)].min(axis=1).mean())
        subs = np.argsort(rng.random((n_perm, N_FACES)), axis=1)[:, :idx.size]
        sub = D[subs[:, :, None], subs[:, None, :]]
        rnd = sub.min(axis=2).mean(axis=1)
        out["dispersion_mean_nearest_neighbour_distance"][name] = {
            "observed_px": obs, "random_mean_px": float(rnd.mean()), "random_std_px": float(rnd.std()),
            "observed_modules": obs / MODULE, "random_mean_modules": float(rnd.mean()) / MODULE,
            "z": float((obs - rnd.mean()) / rnd.std()), "fraction_of_random_le_observed": float((rnd <= obs).mean())}
    rings_np = [np.array(r) for r in rings]
    T = lattice_tables(centres, rings_np)
    lab = np.array([0 if f["type"] == "matte" else 1 if f["type"] == "raw" else {"vert": 2, "diagS": 3, "diagF": 4}[f["orientation"]]
                    for f in faces])
    n_ref = 5000
    obs_m = layout_metrics(lab[None, :], T, rings_np[0])
    rnd_m = layout_metrics(rng.permuted(np.tile(lab, (n_ref, 1)), axis=1), T, rings_np[0])
    out["pattern_statistics_vs_random_permutations"] = {"random_arrangements": n_ref}
    for k in ("peak_tex", "peak_raw", "peak_chis", "collinear_triples_spacing1", "collinear_triples_spacing3",
              "same_orientation_pairs_ring3", "all_matte_flowers"):
        v = rnd_m[k]
        out["pattern_statistics_vs_random_permutations"][k] = {
            "observed": float(obs_m[k][0]), "random_median": float(np.median(v)), "random_p95": float(np.percentile(v, 95)),
            "fraction_of_random_le_observed": float((v <= obs_m[k][0]).mean())}
    out["pattern_statistics_vs_random_permutations"]["note"] = (
        "peak_* = largest non-zero Fourier component of the torus indicator field of that type, divided by its expectation for a "
        "random placement (a period-2 column stripe scores 14 for the textured field); collinear_triples = three textured faces "
        "in a straight line at spacing 1 or 2; a value near the random median or below means no periodic structure")
    adj = [[] for _ in range(N_FACES)]
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)

    def largest_cluster(cd, t):
        seen, best = set(), 0
        for s0 in np.nonzero(cd == t)[0]:
            if int(s0) in seen:
                continue
            stack, size = [int(s0)], 0
            seen.add(int(s0))
            while stack:
                u = stack.pop()
                size += 1
                for v in adj[u]:
                    if cd[v] == t and v not in seen:
                        seen.add(v)
                        stack.append(v)
            best = max(best, size)
        return best

    obs_cluster = largest_cluster(codes, 0)
    rnd_cluster = np.array([largest_cluster(perms[i], 0) for i in range(2000)])
    out["largest_matte_cluster"] = {
        "observed_faces": int(obs_cluster), "matte_faces": int((codes == 0).sum()),
        "random_mean_faces": float(rnd_cluster.mean()), "random_std_faces": float(rnd_cluster.std()),
        "random_arrangements": 2000,
        "note": "at 57 % matte on a hexagonal lattice (site percolation threshold 0.5) one connected matte field is the normal outcome"}
    return out


def render_arrangement_report(pool_info, grid, rng, n_perm=5000):
    """The same adjacency / dispersion statistics for the 39 whole hexagons of the render (no torus)."""
    items = [("matte", i, j) for i, j in pool_info["matte"]] + [("raw", i, j) for i, j in pool_info["raw"]] \
        + [("chiseled", c["i"], c["j"]) for c in pool_info["chiseled"]]
    pos = np.array([face_centre(grid, i, j) for _, i, j in items])
    typ = np.array([t for t, _, _ in items])
    n = len(items)
    D = np.hypot(pos[:, None, 0] - pos[None, :, 0], pos[:, None, 1] - pos[None, :, 1])
    adj = (D < grid["F_px"] * 1.05) & (D > 0)
    out = {"whole_hexagons": n, "adjacent_pairs": int(adj.sum() // 2), "random_arrangements": n_perm, "same_type_neighbour_pairs": {}}
    for t in ("matte", "raw", "chiseled"):
        obs = int(((typ[:, None] == t) & (typ[None, :] == t) & adj).sum() // 2)
        rnd = np.array([int(((p[:, None] == t) & (p[None, :] == t) & adj).sum() // 2)
                        for p in (rng.permutation(typ) for _ in range(n_perm))])
        out["same_type_neighbour_pairs"][t] = {"observed": obs, "random_mean": float(rnd.mean()), "random_std": float(rnd.std()),
                                               "z": float((obs - rnd.mean()) / rnd.std())}
    Dm = D.copy()
    np.fill_diagonal(Dm, np.inf)
    out["dispersion_mean_nearest_neighbour_distance"] = {}
    for name, sel in (("raw", typ == "raw"), ("chiseled", typ == "chiseled"), ("raw_and_chiseled", typ != "matte")):
        idx = np.nonzero(sel)[0]
        obs = float(Dm[np.ix_(idx, idx)].min(axis=1).mean())
        rnd = np.array([Dm[np.ix_(s, s)].min(axis=1).mean() for s in (rng.permutation(n)[:idx.size] for _ in range(n_perm))])
        out["dispersion_mean_nearest_neighbour_distance"][name] = {
            "observed_px": obs, "random_mean_px": float(rnd.mean()), "random_std_px": float(rnd.std()),
            "observed_modules": obs / grid["F_px"], "random_mean_modules": float(rnd.mean()) / grid["F_px"],
            "z": float((obs - rnd.mean()) / rnd.std())}
    return out


def repetition_summary():
    rep = json.load(open(out_path("work", "repetition.json")))
    keep = ("faces", "pairs", "rotation_step_deg", "max_ncc_any_transform", "max_ncc_d6_elements", "max_ncc_off_d6_angles",
            "median_pair_max_ncc_d6", "p95_pair_max_ncc_d6", "median_pair_max_ncc_off_d6")
    out = {"method": rep["_note"]}
    for k in ("raw_whole_face_bump", "raw_whole_face_colour", "matte_whole_face_colour"):
        out[k] = {kk: rep[k][kk] for kk in keep if kk in rep[k]}
        out[k]["top3_pairs"] = rep[k]["top5_pairs"][:3]
    out["whole_face_positive_controls"] = rep["whole_face_positive_controls"]
    for k in ("raw_patch_search_bump", "raw_patch_search_colour"):
        d = rep[k]
        out[k] = {kk: d[kk] for kk in d if kk not in ("top4_windows", "top4_null_windows", "per_window")}
    out["interpretation"] = [
        "Bump: whole-face NCC over the 12 D6 elements (mirror x 0/60/.../300 deg, 5 deg-sweep free rotation reported separately) "
        "is at the noise floor; the 20/40 deg null transforms and the D6 elements give the same patch-search maximum, "
        "so the bump shows no reuse beyond what a random 256 px window search finds by chance.",
        "Colour: the layout keeps repeated use of one render face at rotations at least 17 deg away from any D6 element, so the D6 "
        "tests are clean, but the 20/40 deg patch search finds a colour window pair with NCC 0.81: Raw faces are built from 8 "
        "source faces (11 Raw faces, each a blend of two), so partial colour reuse at other angles is measurable. It is faint, "
        "low contrast albedo mottling and was not recognisable in the side-by-side review.",
        "Whole-face colour NCC medians of 0.24 (Raw) and 0.15 (Matte) come from low-frequency cloudiness shared by all faces, "
        "not from repeated patches.",
    ]
    return out


def main():
    t0 = time.time()
    rng = np.random.default_rng(RNG_SEED)
    layout = json.load(open(out_path("work", "layout.json")))
    faces = layout["faces"]
    pool_info = json.load(open(out_path("work", "pool_info.json")))
    raw_info = json.load(open(out_path("work", "pool_raw_info.json")))
    grid = json.load(open(out_path("work", "render_grid.json")))
    centres = face_centres()
    assert [f["index"] for f in faces] == [c["index"] for c in centres]

    formats = check_formats()
    print("formats", {k: (v["ihdr_bit_depth"], v["ihdr_colour_type"], v["ok"]) for k, v in formats.items()})
    colour, level, fid = load_maps()
    owner, own_in = ownership(centres)
    print("loaded + ownership %.0fs" % (time.time() - t0))

    tcode = np.zeros(N_FACES + 1, np.uint8)
    for f in faces:
        tcode[f["index"]] = 1 if f["type"] == "matte" else 2 if f["type"] == "raw" else \
            {"vert": 3, "diagS": 4, "diagF": 5}[f["orientation"]]
    tmap = tcode[owner]

    fid_rep = face_id_checks(fid, owner, own_in, centres, rng)
    print("face ids", fid_rep)

    core = own_in >= 6.0
    matte_core = core & (tmap == 1)
    face_level = float(np.median(level[matte_core]))
    jw = joint_widths(fid, level, centres, face_level)
    jw["area_over_length"] = joint_area_width(fid)
    jw["vertical_scan_run_lengths_of_joint_pixels"] = run_lengths_zero(fid, "vertical")
    jw["horizontal_scan_run_lengths_of_joint_pixels"] = run_lengths_zero(fid, "horizontal")
    jw["expected"] = {"normal_width_px": 2 * INSET, "normal_width_in": 2 * INSET / PPI,
                      "horizontal_joint_vertical_run_px": 2 * INSET,
                      "slanted_joint_horizontal_run_px": 2 * INSET / np.cos(np.deg2rad(30.0)),
                      "slanted_joint_vertical_run_px": 2 * INSET / np.sin(np.deg2rad(30.0))}
    print("joint widths", jw["all_edges_face_id_zero_run_px_mean_min_max"], jw["all_edges_bump_half_depth_width_px_mean_min_max"],
          jw["area_over_length"]["mean_width_px"])

    seam = {"colour_8bit_levels": {}, "bump_16bit_levels": {}}
    for axis, name in ((1, "x_wrap_left_right"), (0, "y_wrap_top_bottom")):
        c_st = step_stats(colour, axis, rng)
        b_st = step_stats(level, axis, rng)
        for key in ("seam_step_mean_abs", "interior_pair_mean_abs_median", "interior_pair_mean_abs_p99"):
            b_st[key + "_mm"] = b_st[key] * MM_PER_LEVEL
        seam["colour_8bit_levels"][name] = c_st
        seam["bump_16bit_levels"][name] = b_st
        print("seam", name, "colour seam/median/p99", round(c_st["seam_step_mean_abs"], 3),
              round(c_st["interior_pair_mean_abs_median"], 3), round(c_st["interior_pair_mean_abs_p99"], 3),
              "bump seam/median/p99", round(b_st["seam_step_mean_abs"], 2), round(b_st["interior_pair_mean_abs_median"], 2),
              round(b_st["interior_pair_mean_abs_p99"], 2))
    print("seams %.0fs" % (time.time() - t0))

    psi = raw_info["psi_toward_light_deg"]
    relief, per_face_relief, hmm = relief_report(level, tmap, own_in, owner, faces, centres, psi)
    print("relief", {k: (round(v["pattern_relief_p1_to_p99_mm"], 3), round(v["clearance_deepest_point_to_joint_floor_mm"], 3),
                         round(v["slope_rms_mm_per_mm"], 4)) for k, v in relief["types"].items()})
    print("relief %.0fs" % (time.time() - t0))

    grooves = groove_report(hmm, faces, centres)
    print("grooves", {k: (v["orientation"], round(v["measured_groove_direction_deg"], 2), round(v["pitch_px"], 3)) for k, v in grooves.items()})

    tone = {}
    for name, code in (("matte", 1), ("raw", 2), ("chiseled", None)):
        m = core & ((tmap >= 3) if code is None else (tmap == code))
        tone[name] = [float(colour[..., c][m].mean()) for c in range(3)]
    jcore = own_in <= 2.0
    joint_rgb = [float(colour[..., c][jcore].mean()) for c in range(3)]
    joint_std = [float(colour[..., c][jcore].std()) for c in range(3)]
    lum = (colour[..., 0].astype(np.float32) * 0.2126 + colour[..., 1].astype(np.float32) * 0.7152
           + colour[..., 2].astype(np.float32) * 0.0722)
    colour_rep = {
        "joint_rgb_used": JOINT_RGB.tolist(), "joint_core_mean_rgb_measured": joint_rgb, "joint_core_std_rgb": joint_std,
        "face_mean_rgb_atlas_by_type": tone,
        "face_mean_rgb_render_by_type": pool_info["tone_mean_rgb"],
        "luminance_std_within_type_pixels": {n: float(lum[core & ((tmap >= 3) if c is None else (tmap == c))].std())
                                             for n, c in (("matte", 1), ("raw", 2), ("chiseled", None))},
        "joint_colour_note": "darkest across-joint bin of the render (about 13 % darker than the face tone); the render joint is "
                             "only about 1.5 px wide, so its colour is mixed with the face edge and is a lower bound of the true joint tone",
    }
    del lum

    mix = mix_report(pool_info, faces)
    arrangement = arrangement_report(faces, centres, rng)
    arrangement["render_for_comparison"] = render_arrangement_report(pool_info, grid, rng)
    print("mix", mix["atlas_fractions"], "arrangement", {k: round(v["z"], 2) for k, v in arrangement["dispersion_mean_nearest_neighbour_distance"].items()})
    repetition = repetition_summary()

    sample = {
        "brief_sample_size_in": [70.148, 70.875], "brief_sample_size_ft_in": ["5'-10 5/32\"", "5'-10 7/8\""],
        "atlas_extent_in_at_64_px_per_in": [W / PPI, H / PPI],
        "true_pattern_period_in": [8 * 1.5 * (MODULE / PPI) / np.sqrt(3.0), 7 * MODULE / PPI],
        "exact_quarter_inch": [False, False],
        "nearest_quarter_inch": [70.25, [70.75, 71.0]],
        "relative_error_if_rounded_to_quarter_inch_pct": [100 * (70.25 / 70.148 - 1), [100 * (70.75 / 70.875 - 1), 100 * (71.0 / 70.875 - 1)]],
        "note": "Fixed by the brief. Revit's Texture Editor rounds Sample Size to the project's length unit, so in a 1/4 in project "
                "these values are not stored exactly; an exact quarter-inch alternative is 70.25 x 71.0 in (stretch +0.15 % / +0.18 %), not applied.",
    }

    face_entries = []
    for f, c in zip(faces, centres):
        A, B, bl = f["A"], f["B"], f["blend"]

        def one(s):
            t = "render face (%d,%d), rotated %.2f deg%s" % (s["src"][0], s["src"][1], s["rotation_deg"], ", mirrored" if s["mirrored"] else "")
            if "kind" in s:
                t += " [%s-groove source, D6 element r60=%d]" % (s["kind"], s["r60"])
            return t
        blend = "ramp blend axis %.1f deg, offset %.0f px, ramp %.0f px" % (bl["phi_deg"], bl["offset_px"], bl["ramp_px"])
        if f["type"] == "matte":
            txt = "Matte tone and cloudiness fluctuation from %s (A) and %s (B); %s, variance-preserving; face tone from the source face means; height flat" % (one(A), one(B), blend)
        elif f["type"] == "raw":
            txt = ("Raw relief (Wiener-inverted shading, Fourier-domain mixture weighted by the measured angular gain) and albedo from %s (A) and %s (B); %s"
                   % (one(A), one(B), blend))
        else:
            txt = ("Chiseled %s (grooves at %.0f deg): RGB and groove component from %s (A) and %s (B), pitch-normalised, phase-aligned; %s; "
                   "height = land plane minus groove weight x groove depth" % (f["orientation"], TARGET_DIR_DEG[f["orientation"]], one(A), one(B), blend))
        entry = {
            "index": f["index"], "type": f["type"], "rotation_deg": A["rotation_deg"], "mirrored": bool(A["mirrored"]),
            "source": txt,
            "orientation": f["orientation"], "column": f["col"], "row": f["row"], "centre_px": [c["cx"], c["cy"]],
            "sources": [dict(role="A", render_face=A["src"], rotation_deg=A["rotation_deg"], mirrored=bool(A["mirrored"])),
                        dict(role="B", render_face=B["src"], rotation_deg=B["rotation_deg"], mirrored=bool(B["mirrored"]))],
            "blend": bl,
        }
        entry.update({"measured_" + k: v for k, v in per_face_relief[f["index"]].items()})
        if f["type"] == "chiseled":
            g = grooves[f["index"]]
            entry["measured_groove_direction_deg"] = g["measured_groove_direction_deg"]
            entry["measured_groove_pitch_mm"] = g["pitch_mm"]
        face_entries.append(entry)

    types = relief["types"]
    seam_ok = all(v["seam_ok_not_above_interior_p99"] for grp in seam.values() for v in grp.values())
    checks = {
        "format_headers_all_ok": all(v["ok"] for v in formats.values()),
        "face_ids_geometry_mismatch_pixels_zero": fid_rep["mismatch_vs_geometry_pixels"] == 0,
        "face_ids_all_56_present": fid_rep["all_56_indices_present"],
        "face_ids_voronoi_mismatch_zero": fid_rep["voronoi_nearest_centre_mismatch_in_200000_random_face_pixels"] == 0,
        "joint_width_face_id_mean_within_0.1px_of_8": abs(jw["all_edges_face_id_zero_run_px_mean_min_max"][0] - 8.0) < 0.1,
        "joint_width_bump_half_depth_mean_within_0.3px_of_8": abs(jw["all_edges_bump_half_depth_width_px_mean_min_max"][0] - 8.0) < 0.3,
        "wrap_seam_not_above_interior_p99_all_four": seam_ok,
        "clearance_deepest_pattern_point_to_joint_floor_mm_positive": relief["pattern_faces_raw_and_chiseled"]["clearance_to_joint_floor_mm"] > 0,
        "matte_flat_within_1_level": relief["matte_max_abs_dev_from_face_plane_mm"] <= MM_PER_LEVEL * 1.5,
        "mix_within_3_percentage_points": max(mix["abs_difference_percentage_points"].values()) < 3.0,
        "raw_and_chiseled_have_no_same_type_ring1_neighbours": (arrangement["same_type_neighbour_pairs"]["raw"]["observed"] == 0
                                                             and arrangement["same_type_neighbour_pairs"]["chiseled"]["observed"] == 0),
        "chiseled_groove_directions_within_1deg_of_target": max(abs(g["deviation_deg"]) for g in grooves.values()) < 1.0,
        "no_periodic_structure_all_spectral_peaks_at_or_below_random_p95": all(
            arrangement["pattern_statistics_vs_random_permutations"][k]["observed"]
            <= arrangement["pattern_statistics_vs_random_permutations"][k]["random_p95"] for k in ("peak_tex", "peak_raw", "peak_chis")),
        "collinear_triples_and_same_orientation_ring3_pairs_at_or_below_random_p95": all(
            arrangement["pattern_statistics_vs_random_permutations"][k]["observed"]
            <= arrangement["pattern_statistics_vs_random_permutations"][k]["random_p95"]
            for k in ("collinear_triples_spacing1", "collinear_triples_spacing3", "same_orientation_pairs_ring3")),
        "sample_size_exact_quarter_inch": False,
    }
    print("checks", checks)

    report = {
        "generated": "2026-09-29",
        "atlas": {"size_px": [W, H], "px_per_in": PPI, "columns": NCOL, "rows": NROW, "faces": N_FACES,
                  "module_across_flats_in": MODULE / PPI, "face_across_flats_in": FACE_FLATS / PPI, "joint_in": 2 * INSET / PPI,
                  "joint_px": 2 * INSET, "orientation": "flat-top hexagons",
                  "rotation_convention": "atlas = Rot(rotation_deg) applied after an optional top-bottom mirror (mirrored) of the render "
                                         "face, in image coordinates (x right, y down; positive = clockwise on screen); rotation_deg and "
                                         "mirrored in each face entry are source A's, both sources are listed in sources[]",
                  "render_scale": {"render_px_per_in_if_10in_across_flats": grid["px_per_in_if_10in_flats"],
                                   "atlas_px_per_render_px": PPI / grid["px_per_in_if_10in_flats"]}},
        "size_assumption": "10.000 in across the flats (11.547 in point to point), as fixed by the brief; if the tile is really 10 in "
                           "point to point every dimension scales by 0.866",
        "joint_colour_rgb": JOINT_RGB.astype(int).tolist(),
        "suggested_revit_bump_amount": 100,
        "suggested_revit_bump_amount_note": "Revit editor scale (whole number, 100 x the stored float). Start value taken from the repo "
                                            "calibration for a full-range 16-bit dimensional map (about 2.6 mm full scale, 1.6 mm joint); "
                                            "this map is 2.2 mm full scale with a 1.6 mm joint. Not checked in Revit in this trial; the "
                                            "pattern relief is a smaller share of the grey range than the joint step, so raise it if the "
                                            "pattern reads soft.",
        "formats": formats,
        "face_ids": fid_rep,
        "joints": jw,
        "wrap_seam_steps": seam,
        "relief": relief,
        "grooves_measured_from_bump": grooves,
        "colour": colour_rep,
        "mix": mix,
        "arrangement": arrangement,
        "repetition": repetition,
        "sample_size": sample,
        "checks": checks,
        "faces": face_entries,
    }
    save_text(json.dumps(py(report), indent=1), "textures", "report.json")
    print("report.json written %.0fs" % (time.time() - t0))


if __name__ == "__main__":
    main()
