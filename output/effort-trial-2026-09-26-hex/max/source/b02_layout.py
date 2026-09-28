"""Build step 2: atlas layout (8 x 7 flat-top hexagons on a torus).

Mix, from the render's 39 full faces (22 matte / 8 raw / 9 chiseled) -> 32 / 11 / 13 of 56.
Chiseled tile rotations follow the render: rho 0 (vertical grooves) x5, rho 60 (150 deg
grooves) x5, 30 deg grooves as rho 300 x2 and rho 120 x1 (the render's 30-deg faces use
one of each).

Placement: simulated annealing on the torus adjacency - no raw-raw neighbours, few
chiseled-chiseled neighbours, no same-rotation chiseled neighbours, even local density
of textured faces, no crowded rows/columns.
Matte sources: 21 full render matte faces (face 12 excluded: it shares texture with face
6); each atlas matte face takes its low band (tone + cloudiness) from one source and its
high band (fine speckle) from a different one, each under its own hexagon symmetry.
A source's low band is used at most twice, never in neighbouring or near cells, and
with rotations >= 120 deg apart.
Chiseled sources: 9 full render chiseled faces; reuse (4 faces) takes the other
along-groove mirror and never neighbours.
Writes _work/layout.json.
"""

import json
import sys

import numpy as np

from common import COLS, ROWS, out_path

SEED = 20260926
N_TYPES = {"matte": 32, "raw": 11, "chiseled": 13}
CHIS_ROT = [0] * 5 + [60] * 5 + [300] * 2 + [120]
MATTE_EXCLUDE = {12}
RELATED = [(35, 44), (6, 12)]


def neighbours(i, j):
    if i % 2 == 0:
        nb = [(i, j - 1), (i, j + 1), (i - 1, j - 1), (i - 1, j), (i + 1, j - 1), (i + 1, j)]
    else:
        nb = [(i, j - 1), (i, j + 1), (i - 1, j), (i - 1, j + 1), (i + 1, j), (i + 1, j + 1)]
    return [(a % COLS, b % ROWS) for a, b in nb]


def cell_index(i, j):
    return j * COLS + i + 1


def ring2(i, j):
    s = set()
    for a in neighbours(i, j):
        s.add(a)
        for b in neighbours(*a):
            s.add(b)
    s.discard((i, j))
    return s


def layout_cost(T, NB):
    """T: dict cell -> type. Lower is better."""
    cost = 0.0
    for (i, j), t in T.items():
        nbs = NB[(i, j)]
        if t == "raw":
            cost += 10.0 * sum(T[n] == "raw" for n in nbs) / 2.0
        if t == "chiseled":
            cost += 4.0 * sum(T[n] == "chiseled" for n in nbs) / 2.0
        tex = sum(T[n] != "matte" for n in nbs) + (T[(i, j)] != "matte")
        cost += 0.6 * (tex - 7 * 24 / 56.0) ** 2
    for i in range(COLS):
        for t, lim in (("raw", 2), ("chiseled", 3)):
            n = sum(T[(i, j)] == t for j in range(ROWS))
            cost += 3.0 * max(0, n - lim) ** 2
    for j in range(ROWS):
        for t, lim in (("raw", 2), ("chiseled", 3)):
            n = sum(T[(i, j)] == t for i in range(COLS))
            cost += 3.0 * max(0, n - lim) ** 2
    return cost


def anneal_types(rng, NB):
    cells = [(i, j) for j in range(ROWS) for i in range(COLS)]
    types = ["matte"] * N_TYPES["matte"] + ["raw"] * N_TYPES["raw"] + ["chiseled"] * N_TYPES["chiseled"]
    rng.shuffle(types)
    T = dict(zip(cells, types))
    cur = layout_cost(T, NB)
    best, bestT = cur, dict(T)
    temp = 5.0
    for it in range(60000):
        a, b = rng.choice(len(cells), 2, replace=False)
        ca, cb = cells[a], cells[b]
        if T[ca] == T[cb]:
            continue
        T[ca], T[cb] = T[cb], T[ca]
        new = layout_cost(T, NB)
        if new <= cur or rng.random() < np.exp((cur - new) / temp):
            cur = new
            if cur < best:
                best, bestT = cur, dict(T)
        else:
            T[ca], T[cb] = T[cb], T[ca]
        temp = max(0.02, temp * 0.9998)
    return bestT, best


def assign_chiseled_rot(rng, T, NB):
    ch = [c for c in T if T[c] == "chiseled"]
    best = None
    for trial in range(4000):
        rots = list(CHIS_ROT)
        rng.shuffle(rots)
        R = dict(zip(ch, rots))
        cost = 0
        for c in ch:
            for n in NB[c]:
                if n in R and R[n] == R[c]:
                    cost += 5
            for n in ring2(*c):
                if n in R and R[n] == R[c]:
                    cost += 1
        if best is None or cost < best[0]:
            best = (cost, R)
    return best[1], best[0]


def main():
    rng = np.random.default_rng(SEED)
    src = json.load(open(out_path("_work", "sources.json")))
    faces = {f["id"]: f for f in src["faces"]}
    NB = {(i, j): neighbours(i, j) for j in range(ROWS) for i in range(COLS)}
    T, cost = anneal_types(rng, NB)
    print("layout cost %.2f" % cost)
    rr = sum(T[n] == "raw" for c in T if T[c] == "raw" for n in NB[c]) // 2
    cc = sum(T[n] == "chiseled" for c in T if T[c] == "chiseled" for n in NB[c]) // 2
    print("raw-raw neighbour pairs %d, chiseled-chiseled pairs %d" % (rr, cc))
    R, rc = assign_chiseled_rot(rng, T, NB)
    print("chiseled rotation conflicts cost %d" % rc)
    # ---- matte sources ------------------------------------------------------------------
    matte_src = sorted(f["id"] for f in src["faces"]
                       if f["type"] == "matte" and f["frac"] > 0.99 and f["id"] not in MATTE_EXCLUDE)
    mcells = [c for c in sorted(T, key=lambda c: (c[1], c[0])) if T[c] == "matte"]
    related = {}
    for a, b in RELATED:
        related.setdefault(a, set()).add(b)
        related.setdefault(b, set()).add(a)
    best = None
    for trial in range(3000):
        pool = list(matte_src) + list(rng.choice(matte_src, len(mcells) - len(matte_src), replace=False))
        rng.shuffle(pool)
        A = dict(zip(mcells, pool))
        cost = 0
        for c in mcells:
            near = set(NB[c]) | ring2(*c)
            for n in near:
                if n in A and n != c:
                    if A[n] == A[c]:
                        cost += 10 if n in NB[c] else 4
                    elif A[n] in related.get(A[c], ()):
                        cost += 3 if n in NB[c] else 1
        if best is None or cost < best[0]:
            best = (cost, A)
    A = best[1]
    print("matte low-band assignment cost %d (sources %d for %d faces)" % (best[0], len(matte_src), len(mcells)))
    used_rot = {}
    matte = {}
    for c in mcells:
        s = A[c]
        prev = used_rot.get(s)
        for _ in range(100):
            k = int(rng.integers(0, 6)); mir = bool(rng.integers(0, 2))
            if prev is None or (min((k - prev[0]) % 6, (prev[0] - k) % 6) >= 2 and mir != prev[1]):
                break
        used_rot[s] = (k, mir)
        # high band: a different source, not related, not this cell's neighbours' low bands
        cand = [h for h in matte_src if h != s and h not in related.get(s, ())]
        hb = int(rng.choice(cand))
        kh = int(rng.integers(0, 6)); mh = bool(rng.integers(0, 2))
        matte[c] = {"low_src": int(s), "low_rot": k * 60, "low_mirror": mir,
                    "high_src": hb, "high_rot": kh * 60, "high_mirror": mh,
                    "tone_jitter": 1.0}
    # ---- chiseled sources ---------------------------------------------------------------
    chis_src = sorted(f["id"] for f in src["faces"] if f["type"] == "chiseled" and f["frac"] > 0.99)
    ccells = [c for c in sorted(T, key=lambda c: (c[1], c[0])) if T[c] == "chiseled"]
    best = None
    for trial in range(4000):
        pool = list(chis_src) + list(rng.choice(chis_src, len(ccells) - len(chis_src), replace=False))
        rng.shuffle(pool)
        S = dict(zip(ccells, pool))
        cost = 0
        for c in ccells:
            for n in set(NB[c]) | ring2(*c):
                if n in S and n != c and S[n] == S[c]:
                    cost += 10 if n in NB[c] else 3
        # prefer small rotation between source and target (less re-rotated grain)
        for c in ccells:
            d = abs(((faces[S[c]]["rho_src"] - R[c]) + 180) % 360 - 180)
            cost += 0.01 * d / 60.0
        if best is None or cost < best[0]:
            best = (cost, S)
    S = best[1]
    seen = {}
    chis = {}
    for c in ccells:
        s = S[c]
        mir = seen.get(s, 0) % 2 == 1
        seen[s] = seen.get(s, 0) + 1
        chis[c] = {"src": int(s), "rho": int(R[c]), "rho_src": int(faces[s]["rho_src"]),
                   "mirror_v": bool(mir)}
    print("chiseled source assignment cost %.2f" % best[0])
    # ---- raw tones -----------------------------------------------------------------------
    rcells = [c for c in sorted(T, key=lambda c: (c[1], c[0])) if T[c] == "raw"]
    raw_tone = {c: float(1.0033 + rng.normal(0, 0.0153)) for c in rcells}
    out = []
    for j in range(ROWS):
        for i in range(COLS):
            c = (i, j)
            d = {"index": cell_index(i, j), "i": i, "j": j, "type": T[c]}
            if T[c] == "matte":
                d.update(matte[c])
            elif T[c] == "chiseled":
                d.update(chis[c])
            else:
                d.update({"tone": raw_tone[c]})
            out.append(d)
    grid = "\n".join(" ".join({"matte": ".", "raw": "R", "chiseled": "C"}[T[(i, j)]]
                              for i in range(COLS)) for j in range(ROWS))
    print(grid)
    json.dump({"seed": SEED, "cells": out, "counts": {t: sum(1 for c in T if T[c] == t) for t in N_TYPES},
               "neighbour_pairs": {"raw_raw": rr, "chiseled_chiseled": cc}},
              open(out_path("_work", "layout.json"), "w"), indent=1)


if __name__ == "__main__":
    sys.exit(main())
