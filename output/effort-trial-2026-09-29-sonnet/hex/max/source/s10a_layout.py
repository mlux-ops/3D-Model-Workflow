"""Step 10a: atlas layout. Which of the 56 faces is matte / raw / chiseled (and which chiseled
orientation), which two source faces feed each atlas face, and with what rotation / mirror.

Types: 32 matte, 11 raw, 13 chiseled (4 vertical, 6 diagS, 3 diagF), the render's mix
(22 / 8 / 9 complete faces = 56.4 / 20.5 / 23.1 %) scaled to 56 faces. Placement is a seeded
random sequential placement on the torus (no two chiseled or two raw faces edge-to-edge, no two
chiseled faces of one orientation within the second ring), followed by selection of the candidate
whose textured-face field looks least patterned: flat Fourier spectrum on the torus, few collinear
triples, balanced rows and columns, no over-dispersion, no all-matte flower of 7 faces, matte
adjacency like the render's. (The first version minimised an adjacency cost by annealing and
produced an alternating-column stripe, see ERRORS.md.)

Source assignment (seeded, constraint-checked):
* every atlas face is a composite of two distinct source faces; no unordered pair is used twice;
* the uses of one source are spread evenly around the 60 deg circle (beta = +-alpha mod 60, sign
  by mirror), 20 deg apart for three uses and 30 deg for two, so a whole-face comparison over the
  six 60 deg rotations and mirrors cannot line two faces up;
* raw pairs are rotated so the second source's informed light axis is as close to 90 deg from
  the first's as the 60 deg steps allow (never worse than 30 deg; the shading inversion is blind
  perpendicular to the light, the partner fills that gap);
* chiseled sources are moved into the target orientation by the D6 elements that map their groove
  direction onto it; a residual rotation of <= 0.4 deg makes the atlas grooves exactly nominal."""

import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from guard import save_text, out_path  # noqa: E402
from geometry import face_centres, neighbour_lists, torus_delta, N_FACES, MODULE, NCOL, NROW, W, H  # noqa: E402

SEED = 2026092901
COUNTS = [32, 11, 4, 6, 3]                       # matte, raw, vert, diagS, diagF
NAMES = ["matte", "raw", "vert", "diagS", "diagF"]
TARGET_DEG = {"vert": 90.0, "diagS": 30.0, "diagF": 150.0}
N_CANDIDATES = 30000
MATTE_PAIRS_TARGET = 46.0    # ring-1 matte-matte pairs: 54.06 for a random placement, the render sits 2.6 sigma below that


def wrap60(x):
    return (x + 30.0) % 60.0 - 30.0


def wrap180(x):
    return (x + 90.0) % 180.0 - 90.0


def lattice_tables(faces, rings):
    """Torus Fourier characters (spectral check), pair distances and direction-sorted neighbour tables.

    Lattice coordinates (i, j') with j' = j - i // 2 turn the flat-top layout into a plain lattice.
    The atlas torus is Z^2 / <(8, -4), (0, 7)>, so its 55 non-zero characters are
    exp(2 pi i (u i + v j')) with v = m / 7 and u = (n + 4 m / 7) / 8."""
    n = len(faces)
    ii = np.array([f["i"] for f in faces])
    jp = np.array([f["j"] for f in faces]) - ii // 2
    ks = [((q + 4.0 * m / 7.0) / 8.0, m / 7.0) for m in range(NROW) for q in range(NCOL) if (m, q) != (0, 0)]
    ph = np.array([np.exp(2j * np.pi * (u * ii + v * jp)) for u, v in ks]).astype(np.complex64)
    cx = np.array([f["cx"] for f in faces])
    cy = np.array([f["cy"] for f in faces])
    dx = torus_delta(cx[:, None], cx[None, :], W)
    dy = torus_delta(cy[:, None], cy[None, :], H)
    ang = np.arctan2(dy, dx)

    def by_angle(ring):
        out = np.zeros_like(ring)
        for a in range(n):
            nb = ring[a]
            out[a] = nb[np.argsort(ang[a, nb])]
        return out

    return {"ph": ph, "dist": np.hypot(dx, dy), "n1": by_angle(rings[0]), "n3": by_angle(rings[2])}


def sample_labels(rng, ring1, ring2):
    """One random placement: chiseled faces first (never edge-to-edge with another chiseled face,
    never within the second ring of one of the same orientation), then raw faces (never edge-to-edge
    with another raw face). Labels: 0 matte, 1 raw, 2 vert, 3 diagS, 4 diagF. None if it jams."""
    lab = np.zeros(ring1.shape[0], np.int8)
    for o in rng.permutation(np.repeat([2, 3, 4], COUNTS[2:])):
        blocked = (lab != 0) | (lab[ring1] >= 2).any(axis=1) | (lab[ring2] == o).any(axis=1)
        free = np.nonzero(~blocked)[0]
        if free.size == 0:
            return None
        lab[rng.choice(free)] = o
    for _ in range(COUNTS[1]):
        blocked = (lab != 0) | (lab[ring1] == 1).any(axis=1)
        free = np.nonzero(~blocked)[0]
        if free.size == 0:
            return None
        lab[rng.choice(free)] = 1
    return lab


def nearest_distance(ind, dist):
    """Mean distance from each selected face to the nearest other selected face; ind is (M, n) bool."""
    d = dist.astype(np.float32).copy()
    np.fill_diagonal(d, np.inf)
    out = np.empty(ind.shape[0])
    for s in range(0, ind.shape[0], 1000):
        sub = ind[s:s + 1000]
        nearest = np.where(sub[:, None, :], d[None], np.inf).min(axis=2)
        out[s:s + 1000] = (nearest * sub).sum(axis=1) / sub.sum(axis=1)
    return out


def layout_metrics(L, T, ring1):
    """Pattern statistics for a batch of label arrays L (M, n)."""
    M, n = L.shape
    tex, raw, chis, matte = L > 0, L == 1, L >= 2, L == 0
    out = {}
    for name, ind in (("tex", tex), ("raw", raw), ("chis", chis)):
        s = np.abs(ind.astype(np.float32) @ T["ph"].T) ** 2
        nt = ind.sum(axis=1).astype(np.float64)
        out["peak_" + name] = s.max(axis=1) / (nt * (n - nt) / (n - 1))
    for tag, nb in (("1", T["n1"]), ("3", T["n3"])):
        cnt = np.zeros(M)
        for k in range(3):
            cnt += (tex & tex[:, nb[:, k]] & tex[:, nb[:, k + 3]]).sum(axis=1)
        out["collinear_triples_spacing" + tag] = cnt
    out["same_orientation_pairs_ring3"] = ((L[:, :, None] == L[:, T["n3"]]) & (L[:, :, None] >= 2)).sum(axis=(1, 2)) / 2.0
    out["matte_matte_pairs_ring1"] = (matte[:, :, None] & matte[:, ring1]).sum(axis=(1, 2)) / 2.0
    out["all_matte_flowers"] = (matte & matte[:, ring1].all(axis=2)).sum(axis=1).astype(float)
    per_col = tex.reshape(M, NCOL, NROW).sum(axis=2)
    per_row = tex.reshape(M, NCOL, NROW).sum(axis=1)
    out["textured_per_column_min"], out["textured_per_column_max"] = per_col.min(axis=1), per_col.max(axis=1)
    out["textured_per_row_min"], out["textured_per_row_max"] = per_row.min(axis=1), per_row.max(axis=1)
    out["nearest_distance_raw_px"] = nearest_distance(raw, T["dist"])
    out["nearest_distance_chis_px"] = nearest_distance(chis, T["dist"])
    return out


def choose_layout(rng, faces, rings):
    """Sample N_CANDIDATES placements, keep those passing the hard filters, return the one whose worst
    pattern statistic (z-score over the kept set) is lowest, plus a record of what was measured."""
    T = lattice_tables(faces, rings)
    ring1, ring2 = rings[0], rings[1]
    cands, jammed = [], 0
    while len(cands) < N_CANDIDATES:
        lab = sample_labels(rng, ring1, ring2)
        if lab is None:
            jammed += 1
        else:
            cands.append(lab)
    L = np.array(cands)
    m = layout_metrics(L, T, ring1)
    filters = {"columns": (m["textured_per_column_min"] >= 2) & (m["textured_per_column_max"] <= 4),
               "rows": (m["textured_per_row_min"] >= 2) & (m["textured_per_row_max"] <= 5),
               "flowers": m["all_matte_flowers"] <= 1}
    keep = np.ones(len(L), bool)
    for k, f in filters.items():
        keep &= f
    idx = np.nonzero(keep)[0]
    print("candidates %d (%d jammed), pass hard filters %d" % (len(L), jammed, idx.size))
    print("filter pass rates: " + ", ".join("%s %.3f" % (k, f.mean()) for k, f in filters.items()))
    print("mean nearest same-type distance in modules (render: raw 1.70, chiseled 1.60): candidates raw %.2f, chiseled %.2f"
          % (np.median(m["nearest_distance_raw_px"][idx]) / MODULE, np.median(m["nearest_distance_chis_px"][idx]) / MODULE))
    if idx.size < 50:
        raise RuntimeError("hard filters leave only %d candidates" % idx.size)
    score_keys = ["peak_tex", "peak_raw", "peak_chis", "collinear_triples_spacing1", "collinear_triples_spacing3",
                  "same_orientation_pairs_ring3"]
    z = []
    for k in score_keys:
        v = m[k][idx]
        z.append((v - v.mean()) / (v.std() + 1e-9))
    mp = m["matte_matte_pairs_ring1"][idx]
    z.append(np.abs(mp - MATTE_PAIRS_TARGET) / (mp.std() + 1e-9))
    score = np.max(np.array(z), axis=0)
    best = int(idx[np.argmin(score)])
    lab = L[best].astype(int)
    record = {"candidates": int(len(L)), "jammed_placements_discarded": int(jammed), "passed_hard_filters": int(idx.size),
              "hard_filters": {"textured_per_column": [2, 4], "textured_per_row": [2, 5], "all_matte_flowers_max": 1},
              "score_keys": score_keys + ["matte_pairs_distance_from_target"], "score_max_z": float(score.min()),
              "selected": {k: float(m[k][best]) for k in m},
              "selected_nearest_same_type_distance_modules": {k: float(m["nearest_distance_%s_px" % k][best] / MODULE)
                                                              for k in ("raw", "chis")},
              "kept_set_median": {k: float(np.median(m[k][idx])) for k in score_keys},
              "kept_set_p95": {k: float(np.percentile(m[k][idx], 95)) for k in score_keys}}
    return lab, record


def schedule_uses(rng, n_uses, n_src):
    """Spread n_uses source uses over n_src sources as evenly as possible. A use is (source, beta,
    mirrored) where beta = alpha (unmirrored) or -alpha (mirrored), taken mod 60: two uses of one
    source are D6-equivalent exactly when their betas coincide, so each source's betas are spaced
    evenly around the 60 deg circle (20 deg apart for three uses, 30 deg for two)."""
    base, extra = divmod(n_uses, n_src)
    counts = np.full(n_src, base)
    counts[rng.permutation(n_src)[:extra]] += 1
    uses = []
    for s in range(n_src):
        u = int(counts[s])
        beta0 = rng.uniform(0.0, 60.0)
        for k in range(u):
            beta = (beta0 + 60.0 / u * k + rng.uniform(-2.0, 2.0)) % 60.0
            uses.append([s, float(beta), bool(rng.integers(2))])
    return uses


def match_uses(rng, uses, restarts=20000):
    n = len(uses)
    for _ in range(restarts):
        free = [int(x) for x in rng.permutation(n)]
        pairs, used = [], set()
        ok = True
        while free:
            a = free.pop(0)
            cand = [b for b in free if uses[b][0] != uses[a][0]
                    and (min(uses[a][0], uses[b][0]), max(uses[a][0], uses[b][0])) not in used]
            if not cand:
                ok = False
                break
            b = cand[int(rng.integers(len(cand)))]
            free.remove(b)
            pairs.append((a, b))
            used.add((min(uses[a][0], uses[b][0]), max(uses[a][0], uses[b][0])))
        if ok:
            return pairs
    raise RuntimeError("no feasible matching of source uses")


def assign_pairs(rng, n_faces, n_src, psi_src=None):
    """Returns one ((srcA, alphaA, mirA), (srcB, alphaB, mirB)) per face."""
    uses = schedule_uses(rng, 2 * n_faces, n_src)
    out = []
    for a, b in match_uses(rng, uses):
        (sa, beta_a, ma), (sb, beta_b, mb) = uses[a], uses[b]
        alpha_a = (-beta_a if ma else beta_a) + 60.0 * int(rng.integers(6))
        if psi_src is None:
            alpha_b = (-beta_b if mb else beta_b) + 60.0 * int(rng.integers(6))
        else:
            cands = [(-beta_b if mb else beta_b) + 60.0 * k for k in range(6)]
            psi_a = (-psi_src if ma else psi_src) + alpha_a
            devs = [abs(wrap180((-psi_src if mb else psi_src) + c - psi_a - 90.0)) for c in cands]
            alpha_b = cands[int(np.argmin(devs))]
        out.append(((sa, float(alpha_a % 360.0), ma), (sb, float(alpha_b % 360.0), mb)))
    return out


def uses_min_separation(plan):
    """Smallest |wrap60| distance between any two uses of the same source (D6-equivalence test)."""
    per = {}
    for (a, alpha_a, ma), (b, alpha_b, mb) in plan:
        per.setdefault(a, []).append((alpha_a, ma))
        per.setdefault(b, []).append((alpha_b, mb))
    worst = 60.0
    for s, lst in per.items():
        for x in range(len(lst)):
            for y in range(x + 1, len(lst)):
                (a1, m1), (a2, m2) = lst[x], lst[y]
                d = wrap60(a1 - a2) if m1 == m2 else wrap60(a1 + a2)
                worst = min(worst, abs(d))
    return worst


def raw_axis_deviation(plan, psi_src):
    devs = []
    for (a, alpha_a, ma), (b, alpha_b, mb) in plan:
        psi_a = (-psi_src if ma else psi_src) + alpha_a
        psi_b = (-psi_src if mb else psi_src) + alpha_b
        devs.append(abs(wrap180(psi_b - psi_a - 90.0)))
    return devs


def chis_elements(theta_src, target):
    out = []
    for m in (0, 1):
        for r in range(6):
            ang = (-theta_src if m else theta_src) + 60.0 * r
            d = wrap180(target - ang)
            if abs(d) < 1.5:
                out.append((r, m, float(d)))
    return out


def assign_chiseled(rng, orient_of_face, chis, cap=3, restarts=2000):
    n_src = len(chis)
    for _ in range(restarts):
        cnt = np.zeros(n_src, int)
        used_pairs = set()
        used_elem = [set() for _ in range(n_src)]
        out = []
        failed = False
        for f, orient in enumerate(orient_of_face):
            tgt = TARGET_DEG[orient]
            done = False
            for _try in range(2000):
                w = np.clip(cap - cnt, 0, None).astype(float) ** 2
                if (w > 0).sum() < 2:
                    break
                a = int(rng.choice(n_src, p=w / w.sum()))
                w2 = w.copy()
                w2[a] = 0.0
                b = int(rng.choice(n_src, p=w2 / w2.sum()))
                if (min(a, b), max(a, b)) in used_pairs:
                    continue
                ea = chis_elements(chis[a]["line_dir_deg"], tgt)
                eb = chis_elements(chis[b]["line_dir_deg"], tgt)
                assert len(ea) == 4 and len(eb) == 4, (len(ea), len(eb))
                ea = [e for e in ea if (tgt, e[0], e[1]) not in used_elem[a]]
                eb = [e for e in eb if (tgt, e[0], e[1]) not in used_elem[b]]
                if not ea or not eb:
                    continue
                r_a, m_a, d_a = ea[int(rng.integers(len(ea)))]
                r_b, m_b, d_b = eb[int(rng.integers(len(eb)))]
                used_elem[a].add((tgt, r_a, m_a))
                used_elem[b].add((tgt, r_b, m_b))
                used_pairs.add((min(a, b), max(a, b)))
                cnt[a] += 1
                cnt[b] += 1
                out.append(((a, r_a, m_a, d_a), (b, r_b, m_b, d_b)))
                done = True
                break
            if not done:
                failed = True
                break
        if not failed:
            return out
    raise RuntimeError("no feasible chiseled assignment")


def blend_params(rng, ramp_lo, ramp_hi):
    return {"phi_deg": float(rng.uniform(0.0, 360.0)),
            "offset_px": float(rng.uniform(-0.25, 0.25) * MODULE),
            "ramp_px": float(rng.uniform(ramp_lo, ramp_hi))}


def main():
    ss = np.random.SeedSequence(SEED)
    r_types, r_raw, r_matte, r_chis, r_bl = [np.random.default_rng(s) for s in ss.spawn(5)]
    info = json.load(open(out_path("work", "pool_info.json")))
    raw_info = json.load(open(out_path("work", "pool_raw_info.json")))
    psi_axis = raw_info["psi_axis_deg"]
    matte_src = info["matte"]
    raw_src = [[f["i"], f["j"]] for f in raw_info["faces"]]
    chis = info["chiseled"]
    assert len(matte_src) == 22 and len(raw_src) == 8 and len(chis) == 9

    faces = face_centres()
    rings = [np.array(r) for r in neighbour_lists(faces)]
    lab, selection = choose_layout(r_types, faces, rings)
    cost = selection["score_max_z"]
    print("selection score (worst pattern z over the kept candidates) %.2f" % cost)
    print(json.dumps({k: (round(v, 3) if isinstance(v, float) else v) for k, v in selection["selected"].items()}))

    idx_of = {k: [f for f in range(N_FACES) if lab[f] == k] for k in range(5)}
    raw_plan = assign_pairs(r_raw, len(idx_of[1]), 8, psi_src=psi_axis)
    matte_plan = assign_pairs(r_matte, len(idx_of[0]), 22, psi_src=None)
    devs = raw_axis_deviation(raw_plan, psi_axis)
    print("raw pairs: min D6-separation between uses of one source %.1f deg; light-axis deviation from 90 deg: "
          "mean %.1f, max %.1f" % (uses_min_separation(raw_plan), np.mean(devs), np.max(devs)))
    print("matte pairs: min D6-separation %.1f deg" % uses_min_separation(matte_plan))
    chis_faces = sorted(idx_of[2] + idx_of[3] + idx_of[4])
    orient_of_face = [NAMES[lab[f]] for f in chis_faces]
    chis_plan = assign_chiseled(r_chis, orient_of_face, chis)

    out_faces = [None] * N_FACES
    for n, f in enumerate(idx_of[1]):
        (a, aa, ma), (b, ab, mb) = raw_plan[n]
        out_faces[f] = {"type": "raw", "orientation": None,
                        "A": {"pool": "raw", "k": a, "src": raw_src[a], "rotation_deg": aa, "mirrored": ma},
                        "B": {"pool": "raw", "k": b, "src": raw_src[b], "rotation_deg": ab, "mirrored": mb},
                        "blend": blend_params(r_bl, 150.0, 260.0)}
    for n, f in enumerate(idx_of[0]):
        (a, aa, ma), (b, ab, mb) = matte_plan[n]
        out_faces[f] = {"type": "matte", "orientation": None,
                        "A": {"pool": "matte", "k": a, "src": matte_src[a], "rotation_deg": aa, "mirrored": ma},
                        "B": {"pool": "matte", "k": b, "src": matte_src[b], "rotation_deg": ab, "mirrored": mb},
                        "blend": blend_params(r_bl, 150.0, 260.0)}
    for n, f in enumerate(chis_faces):
        (a, ra, ma, da), (b, rb, mb, db) = chis_plan[n]
        orient = orient_of_face[n]
        out_faces[f] = {"type": "chiseled", "orientation": orient,
                        "A": {"pool": "chis", "k": a, "src": [chis[a]["i"], chis[a]["j"]], "kind": chis[a]["kind"],
                              "rotation_deg": 60.0 * ra + da, "r60": ra, "mirrored": bool(ma),
                              "line_dir_src_deg": chis[a]["line_dir_deg"], "pitch_src_px": chis[a]["pitch_px"]},
                        "B": {"pool": "chis", "k": b, "src": [chis[b]["i"], chis[b]["j"]], "kind": chis[b]["kind"],
                              "rotation_deg": 60.0 * rb + db, "r60": rb, "mirrored": bool(mb),
                              "line_dir_src_deg": chis[b]["line_dir_deg"], "pitch_src_px": chis[b]["pitch_px"]},
                        "blend": blend_params(r_bl, 100.0, 120.0)}
    for f in range(N_FACES):
        out_faces[f]["index"] = f + 1
        out_faces[f]["col"] = faces[f]["i"]
        out_faces[f]["row"] = faces[f]["j"]

    typ = np.array([0 if x["type"] == "matte" else (1 if x["type"] == "raw" else 2) for x in out_faces])
    stats = {}
    for name, tk in (("matte", 0), ("raw", 1), ("chiseled", 2)):
        pairs = sum(int(typ[a] == tk and typ[b] == tk) for a in range(N_FACES) for b in rings[0][a]) // 2
        stats[name] = {"count": int((typ == tk).sum()), "adjacent_same_type_pairs_ring1": pairs}
    same_orient = sum(int(lab[a] == lab[b] and lab[a] >= 2) for a in range(N_FACES) for b in np.concatenate([rings[0][a], rings[1][a]])) // 2
    stats["chiseled_same_orientation_pairs_ring1_2"] = same_orient
    # expected same-type adjacent pairs for a random placement: 168 ring-1 pairs
    n_pairs = N_FACES * 6 // 2
    for name, tk in (("matte", 0), ("raw", 1), ("chiseled", 2)):
        n = int((typ == tk).sum())
        stats[name]["expected_adjacent_pairs_if_random"] = float(n_pairs * n * (n - 1) / (N_FACES * (N_FACES - 1)))
    # largest connected matte cluster (ring 1)
    seen, largest = set(), 0
    for s in range(N_FACES):
        if typ[s] != 0 or s in seen:
            continue
        stack, comp = [s], 0
        seen.add(s)
        while stack:
            x = stack.pop()
            comp += 1
            for y in rings[0][x]:
                if typ[y] == 0 and y not in seen:
                    seen.add(int(y))
                    stack.append(int(y))
        largest = max(largest, comp)
    stats["largest_matte_cluster"] = largest
    print(json.dumps(stats, indent=1))
    uses = {}
    for x in out_faces:
        for role in ("A", "B"):
            key = (x[role]["pool"], x[role]["k"])
            uses[key] = uses.get(key, 0) + 1
    print("source uses:", {"%s%d" % k: v for k, v in sorted(uses.items())})

    lay = {"seed": SEED, "cost": float(cost), "counts": {"matte": COUNTS[0], "raw": COUNTS[1],
                                                         "chiseled": sum(COUNTS[2:]),
                                                         "vert": COUNTS[2], "diagS": COUNTS[3], "diagF": COUNTS[4]},
           "raw_min_d6_separation_deg": uses_min_separation(raw_plan),
           "matte_min_d6_separation_deg": uses_min_separation(matte_plan),
           "raw_axis_deviation_from_90_deg": [float(d) for d in devs], "psi_axis_deg": psi_axis,
           "stats": stats, "selection": selection, "faces": out_faces}
    save_text(json.dumps(lay, indent=1), "work", "layout.json")
    grid = [[NAMES[lab[i * 7 + j]] for j in range(7)] for i in range(8)]
    print("layout by column (rows down):")
    for i in range(8):
        print(" col %d %s" % (i, " ".join("%-6s" % g for g in grid[i])))


if __name__ == "__main__":
    main()
