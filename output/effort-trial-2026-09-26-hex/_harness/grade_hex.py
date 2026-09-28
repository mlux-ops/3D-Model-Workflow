"""Objective grading for the 2026-09-26 hex effort trial (high / xhigh / max + baseline).

Usage: python grade_hex.py   -> writes grade_report.json next to this file and prints a summary.

Face masks come from each arm's face_ids.png when present; otherwise (baseline) faces are found as
connected regions above the joint floor of Bump16, labelled on a 3x3 wrap tiling so every face is
counted once and whole. Face types are classified independently from the bump (relief energy and
groove coherence) so an arm's own labels are checked, not trusted.
"""
import json
import os
import struct
import sys
import zlib  # noqa: F401  (kept for PNG header helpers readability)

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

Image.MAX_IMAGE_PIXELS = None
HERE = os.path.dirname(os.path.abspath(__file__))
TRIAL = os.path.dirname(HERE)
REPO = os.path.abspath(os.path.join(TRIAL, "..", ".."))
TRANSCRIPTS = os.path.expanduser(r"~/.claude/projects/E--Claude-3D-Model-Workflow")
EXPECTED = (4489, 4536)
PPI = 64
DS = 4  # downsample factor for texture comparisons (64 -> 16 px/in)

ARMS = {
    "high": os.path.join(TRIAL, "high", "textures"),
    "xhigh": os.path.join(TRIAL, "xhigh", "textures"),
    "max": os.path.join(TRIAL, "max", "textures"),
}
BASELINE = os.path.join(REPO, "output", "hex_10in_dimensional", "textures")


def png_header(path):
    with open(path, "rb") as fh:
        sig = fh.read(8)
        if sig != b"\x89PNG\r\n\x1a\n":
            return None
        _len, ctype = struct.unpack(">I4s", fh.read(8))
        w, h, depth, colour = struct.unpack(">IIBB", fh.read(10))
        return {"w": w, "h": h, "bit_depth": depth, "colour_type": colour}


def load_grey16(path):
    im = Image.open(path)
    a = np.asarray(im)
    if a.ndim == 3:
        a = a[..., 0]
    return a.astype(np.float64)


def wrap_steps(a):
    a = a.astype(np.float64)
    if a.ndim == 2:
        a = a[..., None]
    lr = np.abs(a[:, 0] - a[:, -1]).mean()
    tb = np.abs(a[0, :] - a[-1, :]).mean()
    ix = np.abs(np.diff(a[:, 1:-1], axis=1)).mean()
    iy = np.abs(np.diff(a[1:-1, :], axis=0)).mean()
    return {"lr": round(float(lr), 3), "tb": round(float(tb), 3), "interior_x": round(float(ix), 3), "interior_y": round(float(iy), 3)}


def faces_from_bump(bump):
    """Label faces as connected regions above the joint floor, wrap-aware (baseline only)."""
    lo = np.percentile(bump, 1.0)
    med = np.median(bump)
    thr = lo + 0.35 * (med - lo)
    up = bump > thr
    h, w = up.shape
    big = np.tile(up, (3, 3))
    lab, n = ndi.label(big)
    ids = np.zeros((h, w), np.int32)
    k = 0
    objs = ndi.find_objects(lab)
    for i, sl in enumerate(objs, start=1):
        if sl is None:
            continue
        y0, y1, x0, x1 = sl[0].start, sl[0].stop, sl[1].start, sl[1].stop
        if y0 == 0 or x0 == 0 or y1 == 3 * h or x1 == 3 * w:
            continue
        m = lab[sl] == i
        if m.sum() < 0.3 * (PPI * 10) ** 2:
            continue
        cy, cx = ndi.center_of_mass(m)
        cy += y0
        cx += x0
        if not (h <= cy < 2 * h and w <= cx < 2 * w):
            continue
        k += 1
        yy, xx = np.nonzero(m)
        ids[(yy + y0) % h, (xx + x0) % w] = k
    return ids


def face_crops(ids, arrays, pad=0):
    """Per face: wrap-safe crop (via 3x3 tiling of each array) and mask, centred on the face."""
    h, w = ids.shape
    out = {}
    for fid in np.unique(ids):
        if fid == 0:
            continue
        yy, xx = np.nonzero(ids == fid)
        # unwrap coordinates around the face's circular mean
        ay = np.angle(np.exp(2j * np.pi * yy / h).mean()) / (2 * np.pi) * h
        ax = np.angle(np.exp(2j * np.pi * xx / w).mean()) / (2 * np.pi) * w
        uy = ((yy - ay + h / 2) % h) - h / 2 + ay
        ux = ((xx - ax + w / 2) % w) - w / 2 + ax
        cy, cx = uy.mean(), ux.mean()
        r = int(max(np.abs(uy - cy).max(), np.abs(ux - cx).max())) + 2 + pad
        ys = (np.arange(int(cy) - r, int(cy) + r + 1)) % h
        xs = (np.arange(int(cx) - r, int(cx) + r + 1)) % w
        mask = ids[np.ix_(ys, xs)] == fid
        out[int(fid)] = {"mask": mask, "crops": [a[np.ix_(ys, xs)] for a in arrays], "area": int(len(yy))}
    return out


def highpass(a, sigma):
    return a - ndi.gaussian_filter(a, sigma)


def bandpass_ds(a):
    """Band-pass (removes tone and sub-sample grain) then downsample by DS without aliasing."""
    b = ndi.gaussian_filter(a, DS * 0.6) - ndi.gaussian_filter(a, 10.0)
    return b[::DS, ::DS]


def classify(bump_crop, mask, full_range):
    """Relief energy and orientation coherence of one face's bump -> matte / raw / chiseled."""
    inner = ndi.binary_erosion(mask, iterations=12)
    if inner.sum() < 100:
        inner = mask
    hp = highpass(bump_crop, 6.0)
    energy = float(hp[inner].std() / full_range)
    gy, gx = np.gradient(ndi.gaussian_filter(bump_crop, 1.5))
    jxx = ndi.gaussian_filter(gx * gx, 4)[inner].mean()
    jyy = ndi.gaussian_filter(gy * gy, 4)[inner].mean()
    jxy = ndi.gaussian_filter(gx * gy, 4)[inner].mean()
    tr = jxx + jyy
    coh = float(np.sqrt((jxx - jyy) ** 2 + 4 * jxy ** 2) / tr) if tr > 0 else 0.0
    ang = float(np.degrees(0.5 * np.arctan2(2 * jxy, jxx - jyy)))  # gradient direction; grooves run perpendicular
    return energy, coh, ang


def rot_face(a, k60, mirror):
    b = np.fliplr(a) if mirror else a
    return ndi.rotate(b, 60 * k60, reshape=False, order=1, mode="nearest")


def ncc_masked(a, b, m):
    x = a[m] - a[m].mean()
    y = b[m] - b[m].mean()
    d = np.sqrt((x * x).sum() * (y * y).sum())
    return float((x * y).sum() / d) if d > 0 else 0.0


def raw_face_repetition(faces, raw_ids):
    """Max NCC between Raw faces over 60-degree rotations and mirrors (hex-aligned whole-face reuse)."""
    prepared = {}
    for fid in raw_ids:
        f = faces[fid]
        g = f["crops"][0]
        g = bandpass_ds(g)
        m = f["mask"][::DS, ::DS][: g.shape[0], : g.shape[1]]
        m = ndi.binary_erosion(m, iterations=6)
        prepared[fid] = (g, m)
    pairs = []
    ids = list(prepared)
    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
            a, ma = prepared[ids[i]]
            b, mb = prepared[ids[j]]
            s = min(a.shape[0], b.shape[0]), min(a.shape[1], b.shape[1])
            a2, b2 = a[: s[0], : s[1]], b[: s[0], : s[1]]
            m2 = ma[: s[0], : s[1]] & mb[: s[0], : s[1]]
            best = max(ncc_masked(a2, rot_face(b2, k, mir), m2) for k in range(6) for mir in (False, True))
            pairs.append({"faces": [ids[i], ids[j]], "max_ncc": round(best, 3)})
    pairs.sort(key=lambda p: -p["max_ncc"])
    vals = [p["max_ncc"] for p in pairs]
    return {"n_raw": len(ids), "top3": pairs[:3], "pairs_over_0.6": sum(v > 0.6 for v in vals),
            "median": round(float(np.median(vals)), 3) if vals else None}


def patch_search(grey, ids, raw_ids, n=40, win_in=3.0, seed=7):
    """Random windows inside Raw faces; best circular NCC match elsewhere in the atlas (flips included)."""
    g = bandpass_ds(grey)
    idd = ids[::DS, ::DS][: g.shape[0], : g.shape[1]]
    g = g[: idd.shape[0], : idd.shape[1]]
    g = np.where(idd > 0, g, 0.0)
    H, W = g.shape
    win = int(round(win_in * PPI / DS))
    rng = np.random.default_rng(seed)
    rawmask = np.isin(idd, list(raw_ids))
    inside = ndi.binary_erosion(rawmask, structure=np.ones((win, win)), border_value=0)
    cand = np.argwhere(inside)
    if len(cand) == 0:
        return {"windows": 0}
    pick = cand[rng.choice(len(cand), size=min(n, len(cand)), replace=False)]
    F = np.fft.rfft2(g)
    ones = np.zeros_like(g)
    ones[:win, :win] = 1
    Fo = np.fft.rfft2(ones)
    s1 = np.fft.irfft2(np.fft.rfft2(g) * np.conj(Fo), s=g.shape)
    s2 = np.fft.irfft2(np.fft.rfft2(g * g) * np.conj(Fo), s=g.shape)
    local_var = np.maximum(s2 - s1 * s1 / (win * win), 1e-9)
    best_vals = []
    for (cy, cx) in pick:
        y0, x0 = cy - win // 2, cx - win // 2
        t = np.roll(np.roll(g, -y0, 0), -x0, 1)[:win, :win].copy()
        best = 0.0
        for tt in (t, np.fliplr(t), np.flipud(t), np.flipud(np.fliplr(t))):
            tz = tt - tt.mean()
            tn = np.sqrt((tz * tz).sum())
            if tn == 0:
                continue
            k = np.zeros_like(g)
            k[:win, :win] = tz
            num = np.fft.irfft2(F * np.conj(np.fft.rfft2(k)), s=g.shape)
            ncc = num / (np.sqrt(local_var) * tn)
            dy = (np.arange(H)[:, None] - y0 + H // 2) % H - H // 2
            dx = (np.arange(W)[None, :] - x0 + W // 2) % W - W // 2
            ncc[(np.abs(dy) < win) & (np.abs(dx) < win)] = -1
            best = max(best, float(ncc.max()))
        best_vals.append(best)
    v = np.array(best_vals)
    return {"windows": int(len(v)), "window_in": win_in, "max": round(float(v.max()), 3),
            "median": round(float(np.median(v)), 3), "frac_over_0.8": round(float((v > 0.8).mean()), 3),
            "frac_over_0.9": round(float((v > 0.9).mean()), 3)}


def grade(tex_dir, use_face_ids=True):
    cpath = next((os.path.join(tex_dir, f) for f in ("Color.png", "Hex10_Dimensional_Color.png") if os.path.exists(os.path.join(tex_dir, f))), None)
    bpath = next((os.path.join(tex_dir, f) for f in ("Bump16.png", "Hex10_Dimensional_Bump16.png") if os.path.exists(os.path.join(tex_dir, f))), None)
    if not cpath or not bpath:
        return {"present": False}
    out = {"present": True, "color_header": png_header(cpath), "bump_header": png_header(bpath)}
    ch, bh = out["color_header"], out["bump_header"]
    out["format_ok"] = bool(ch and bh and (ch["w"], ch["h"]) == EXPECTED and (bh["w"], bh["h"]) == EXPECTED
                            and ch["bit_depth"] == 8 and ch["colour_type"] == 2 and bh["bit_depth"] == 16 and bh["colour_type"] == 0)
    col = np.asarray(Image.open(cpath).convert("RGB")).astype(np.float64)
    bump = load_grey16(bpath)
    full = float(bump.max() - bump.min()) or 1.0
    out["wrap_color"] = wrap_steps(col)
    out["wrap_bump"] = wrap_steps(bump / full * 255.0)
    fpath = os.path.join(tex_dir, "face_ids.png")
    if use_face_ids and os.path.exists(fpath):
        ids = load_grey16(fpath).astype(np.int32)
        out["face_ids_header"] = png_header(fpath)
        out["face_source"] = "face_ids.png"
    else:
        ids = faces_from_bump(bump)
        out["face_source"] = "derived from Bump16"
    nf = len(np.unique(ids)) - (1 if (ids == 0).any() else 0)
    out["n_faces"] = int(nf)
    joint = ids == 0
    out["joint_fraction"] = round(float(joint.mean()), 4)
    grey = col.mean(axis=2)
    faces = face_crops(ids, [grey, bump])
    # relief and clearance (normalised to the bump's full range)
    joint_level = float(np.median(bump[joint])) if joint.any() else float(np.percentile(bump, 1))
    face_px = bump[~joint]
    out["relief"] = {"joint_level_norm": round((joint_level - bump.min()) / full, 4),
                     "face_min_p0.1_norm": round((float(np.percentile(face_px, 0.1)) - bump.min()) / full, 4),
                     "clearance_norm": round((float(np.percentile(face_px, 0.1)) - joint_level) / full, 4)}
    # independent classification
    cls = {}
    for fid, f in faces.items():
        e, c, a = classify(f["crops"][1], f["mask"], full)
        cls[fid] = {"energy": round(e, 4), "coherence": round(c, 3), "grad_angle_deg": round(a, 1)}
    energies = np.array([v["energy"] for v in cls.values()])
    flat_thr = max(0.004, float(np.percentile(energies, 20)) * 2.5)
    for v in cls.values():
        if v["energy"] < flat_thr:
            v["class"] = "matte"
        elif v["coherence"] > 0.45:
            v["class"] = "chiseled"
        else:
            v["class"] = "raw"
    mix = {}
    for v in cls.values():
        mix[v["class"]] = mix.get(v["class"], 0) + 1
    out["classified_mix"] = mix
    ang = sorted(round(((v["grad_angle_deg"] + 90) % 180) - 90) for v in cls.values() if v["class"] == "chiseled")
    out["chiseled_groove_normals_deg"] = ang
    # arm's own labels vs classification
    rpath = os.path.join(tex_dir, "report.json")
    labels = {}
    if os.path.exists(rpath):
        try:
            rep = json.load(open(rpath, encoding="utf-8"))
            fl = rep.get("faces") or rep.get("per_face") or []
            for f in fl:
                if isinstance(f, dict) and "index" in f and "type" in f:
                    labels[int(f["index"])] = str(f["type"]).lower()
        except (json.JSONDecodeError, ValueError, TypeError):
            pass
    if labels:
        agree = sum(1 for fid, v in cls.items() if labels.get(fid) == v["class"])
        own = {}
        for t in labels.values():
            own[t] = own.get(t, 0) + 1
        out["own_label_mix"] = own
        out["label_agreement"] = f"{agree}/{len(cls)}"
    raw_ids = [fid for fid, v in cls.items() if v["class"] == "raw"]
    out["raw_face_repetition"] = raw_face_repetition(faces, raw_ids) if len(raw_ids) > 1 else {"n_raw": len(raw_ids)}
    out["raw_patch_search"] = patch_search(grey, ids, raw_ids) if raw_ids else {"windows": 0}
    return out


def arm_session(arm):
    res_path = os.path.join(HERE, f"result-{arm}.json")
    result = None
    if os.path.exists(res_path) and os.path.getsize(res_path) > 0:
        try:
            result = json.load(open(res_path, encoding="utf-8"))
        except json.JSONDecodeError:
            result = None
    sid = result.get("session_id") if result else None
    tpath = os.path.join(TRANSCRIPTS, f"{sid}.jsonl") if sid else None
    if not tpath or not os.path.exists(tpath):
        marker = f"effort-trial-2026-09-26-hex/{arm}/"
        for f in sorted(os.listdir(TRANSCRIPTS)):
            p = os.path.join(TRANSCRIPTS, f)
            if f.endswith(".jsonl"):
                with open(p, encoding="utf-8", errors="ignore") as fh:
                    head = fh.read(200000)
                if marker in head and "one arm of a controlled effort-level trial" in head:
                    tpath = p
    tot = {"input": 0, "cache_write": 0, "cache_read": 0, "output": 0}
    calls = tools = 0
    last_ctx = 0
    seen = set()
    if tpath and os.path.exists(tpath):
        for line in open(tpath, encoding="utf-8", errors="ignore"):
            try:
                o = json.loads(line)
            except json.JSONDecodeError:
                continue
            msg = o.get("message") or {}
            if o.get("type") != "assistant" or not isinstance(msg, dict):
                continue
            for b in msg.get("content") or []:
                if isinstance(b, dict) and b.get("type") == "tool_use":
                    tools += 1
            mid = msg.get("id")
            if mid in seen:
                continue
            seen.add(mid)
            u = msg.get("usage") or {}
            calls += 1
            tot["input"] += u.get("input_tokens", 0)
            tot["cache_write"] += u.get("cache_creation_input_tokens", 0)
            tot["cache_read"] += u.get("cache_read_input_tokens", 0)
            tot["output"] += u.get("output_tokens", 0)
            last_ctx = u.get("input_tokens", 0) + u.get("cache_creation_input_tokens", 0) + u.get("cache_read_input_tokens", 0)
    all_in = tot["input"] + tot["cache_write"] + tot["cache_read"]
    out = {"transcript": tpath, "api_calls": calls, "tool_calls": tools, "tokens": tot,
           "cache_share": round(tot["cache_read"] / all_in, 3) if all_in else None,
           "output_to_input": round(tot["output"] / all_in, 4) if all_in else None,
           "final_context": last_ctx,
           "total_input_over_final_context": round(all_in / last_ctx, 1) if last_ctx else None}
    if result:
        out["result"] = {k: result.get(k) for k in ("subtype", "is_error", "num_turns", "duration_ms", "total_cost_usd", "terminal_reason")}
        mu = result.get("modelUsage") or {}
        out["result"]["models"] = {m: {"thinkingTokens": v.get("thinkingTokens"), "outputTokens": v.get("outputTokens"), "costUSD": v.get("costUSD")} for m, v in mu.items()}
    return out


def main(only=None):
    targets = dict(ARMS)
    targets["baseline_2026-09-19"] = BASELINE
    if only:
        targets = {k: v for k, v in targets.items() if k in only}
    rep = {"atlases": {}, "sessions": {}}
    for k, d in targets.items():
        rep["atlases"][k] = grade(d, use_face_ids=(k != "baseline_2026-09-19"))
    for arm in ARMS:
        if not only or arm in only:
            rep["sessions"][arm] = arm_session(arm)
    name = "grade_report.json" if not only else "grade_report_partial.json"
    json.dump(rep, open(os.path.join(HERE, name), "w", encoding="utf-8"), indent=1)
    for k, a in rep["atlases"].items():
        if not a.get("present"):
            print(f"{k}: MISSING")
            continue
        print(f"{k}: format_ok={a['format_ok']} faces={a['n_faces']} ({a['face_source']}) joint={a['joint_fraction']} "
              f"wrapC={a['wrap_color']} wrapB={a['wrap_bump']} relief={a['relief']} mix={a['classified_mix']} "
              f"own={a.get('own_label_mix')} agree={a.get('label_agreement')} chisel_normals={a['chiseled_groove_normals_deg']} "
              f"rawrep={a['raw_face_repetition']} patch={a['raw_patch_search']}")
    for arm, s in rep["sessions"].items():
        print(f"{arm}: {json.dumps(s)}")


if __name__ == "__main__":
    main(sys.argv[1:] or None)
