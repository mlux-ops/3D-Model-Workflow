"""Assign face types and chiseled groove orientations to the 8 x 7 torus of hexagons, without clumping or a repeating pattern.

Cells are (i, j): column i (0..7), row j (0..6). Even columns are centred at (j + 0.5) rows, odd columns at j rows,
so even-column joint lines lie on the atlas top/bottom edge. Neighbours wrap on both axes.
Types: 0 matte, 1 raw, 2 chiseled. Chiseled orientation o in {0, 60, 120}: groove wave-vector angle in image coordinates (y down).
"""
import json
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import guard
import render_grid as rg

NC, NR = 8, 7
TARGET = {0: 32, 1: 11, 2: 13}
ORIENT_TARGET = {0: 4, 60: 3, 120: 6}   # render: 3 vertical (wave 0), 2 wave 60, 4 wave 120  -> scaled to 13 faces


def neighbours(i, j):
    out = [(i, (j - 1) % NR), (i, (j + 1) % NR)]
    if i % 2 == 0:
        for di in (-1, 1):
            out += [((i + di) % NC, j), ((i + di) % NC, (j + 1) % NR)]
    else:
        for di in (-1, 1):
            out += [((i + di) % NC, j), ((i + di) % NC, (j - 1) % NR)]
    return out


CELLS = [(i, j) for i in range(NC) for j in range(NR)]
NB = {c: neighbours(*c) for c in CELLS}
# second ring
NB2 = {}
for c in CELLS:
    s = set()
    for n in NB[c]:
        s.update(NB[n])
    s.discard(c)
    s -= set(NB[c])
    NB2[c] = sorted(s)


def energy(T, O):
    e = 0.0
    for i in range(NC):
        cnt = sum(1 for j in range(NR) if T[(i, j)] != 0)
        e += 3.0 * (cnt - 24.0 / NC) ** 2
    for c in CELLS:
        cnt = sum(1 for n in NB[c] + [c] if T[n] != 0)
        e += (cnt - 3.0) ** 2 * 1.0
        cnt2 = sum(1 for n in NB[c] + NB2[c] + [c] if T[n] != 0)
        e += 0.15 * (cnt2 - 24.0 / 56.0 * 19) ** 2
        for n in NB[c]:
            if c < n:
                if T[c] == 1 and T[n] == 1:
                    e += 4.0
                if T[c] == 2 and T[n] == 2:
                    e += 4.0 + (5.0 if O[c] == O[n] else 0.0)
        if T[c] == 2:
            for n in NB2[c]:
                if c < n and T[n] == 2 and O[c] == O[n]:
                    e += 1.5
        if T[c] == 1:
            for n in NB2[c]:
                if c < n and T[n] == 1:
                    e += 1.0
    return e


def shift_match(T, O):
    """Max over non-identity lattice-preserving translations of the fraction of cells with identical (type, orientation)."""
    best = 0.0
    arg = None
    for di in (0, 2, 4, 6):
        for dj in range(NR):
            if di == 0 and dj == 0:
                continue
            m = sum(1 for (i, j) in CELLS if T[(i, j)] == T[((i + di) % NC, (j + dj) % NR)] and (T[(i, j)] != 2 or O[(i, j)] == O[((i + di) % NC, (j + dj) % NR)]))
            f = m / len(CELLS)
            if f > best:
                best, arg = f, (di, dj)
    return best, arg


def anneal(seed, iters=12000):
    rng = np.random.default_rng(seed)
    labels = [0] * TARGET[0] + [1] * TARGET[1] + [2] * TARGET[2]
    rng.shuffle(labels)
    orients = [0] * ORIENT_TARGET[0] + [60] * ORIENT_TARGET[60] + [120] * ORIENT_TARGET[120]
    rng.shuffle(orients)
    T, O = {}, {}
    k = 0
    for c, l in zip(CELLS, labels):
        T[c] = l
        O[c] = 0
        if l == 2:
            O[c] = orients[k]
            k += 1
    E = energy(T, O)
    for it in range(iters):
        temp = 3.0 * (0.02 / 3.0) ** (it / iters)
        a, b = CELLS[rng.integers(len(CELLS))], CELLS[rng.integers(len(CELLS))]
        if T[a] == T[b] and (T[a] != 2 or O[a] == O[b]):
            continue
        T[a], T[b] = T[b], T[a]
        O[a], O[b] = O[b], O[a]
        E2 = energy(T, O)
        if E2 <= E or rng.random() < np.exp((E - E2) / temp):
            E = E2
        else:
            T[a], T[b] = T[b], T[a]
            O[a], O[b] = O[b], O[a]
    return E, T, O


if __name__ == "__main__":
    results = []
    for seed in range(16):
        E, T, O = anneal(seed)
        sm, arg = shift_match(T, O)
        print("seed %2d energy %.1f  max shift match %.3f at %s" % (seed, E, sm, arg))
        results.append((E + 40.0 * max(0.0, sm - 0.50), seed, E, sm, T, O))
    results.sort(key=lambda t: t[0])
    _, seed, E, sm, T, O = results[0]
    print("chosen seed", seed, "energy", E, "max shift match", sm)
    grid = []
    for j in range(NR):
        row = ""
        for i in range(NC):
            t = T[(i, j)]
            row += {0: " M ", 1: " R ", 2: {0: " | ", 60: " / ", 120: " \\ "}[O[(i, j)]]}[t] if False else {0: " M ", 1: " R ", 2: " C%d" % (O[(i, j)] // 60)}[t]
        grid.append(row)
    print("\n".join(grid))
    types = {"%d,%d" % c: int(T[c]) for c in CELLS}
    orient = {"%d,%d" % c: int(O[c]) for c in CELLS}
    adj_rr = sum(1 for c in CELLS for n in NB[c] if c < n and T[c] == 1 and T[n] == 1)
    adj_cc = sum(1 for c in CELLS for n in NB[c] if c < n and T[c] == 2 and T[n] == 2)
    print("raw-raw adjacencies", adj_rr, " chiseled-chiseled adjacencies", adj_cc)
    json.dump(dict(seed=int(seed), energy=float(E), max_shift_match=float(sm), types=types, orient=orient, raw_raw_adjacent=adj_rr, chis_chis_adjacent=adj_cc),
              open(guard.safe(rg.WORK + "layout.json"), "w"), indent=1)
