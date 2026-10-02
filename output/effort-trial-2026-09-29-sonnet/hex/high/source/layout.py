"""Face-type / orientation layout for the 8x7 atlas (simulated annealing, wrap-aware adjacency)."""
import json
from common import *

NC, NR = COLS, ROWS
COUNTS = {"matte": 32, "raw": 11, "chiseled": 13}
ORIENT_COUNTS = {90: 4, 30: 6, 150: 3}         # groove direction (deg, image coords, y down)


def index_of(i, j):
    return i * NR + j + 1


def neighbours(i, j):
    if i % 2 == 0:
        cand = [(i, j - 1), (i, j + 1), (i - 1, j - 1), (i - 1, j), (i + 1, j - 1), (i + 1, j)]
    else:
        cand = [(i, j - 1), (i, j + 1), (i - 1, j), (i - 1, j + 1), (i + 1, j), (i + 1, j + 1)]
    return [(a % NC, b % NR) for a, b in cand]


def energy(types, orient):
    e = 0.0
    for i in range(NC):
        for j in range(NR):
            t = types[i][j]
            nb = neighbours(i, j)
            same = 0
            for (a, b) in nb:
                u = types[a][b]
                if (a, b) > (i, j):        # count each edge once
                    if t == u and t != "matte":
                        e += 12 if t == "raw" else 12
                    elif t != "matte" and u != "matte":
                        e += 3
                if u == t:
                    same += 1
            if t == "matte" and same == 6:
                e += 6
            if t != "matte" and same == 0 and all(types[a][b] == "matte" for a, b in nb):
                pass
            # 2nd ring clumping of textured faces
        # nothing else
    # textured faces should be spread: penalise textured faces sharing a matte-free neighbourhood
    for i in range(NC):
        for j in range(NR):
            if types[i][j] != "matte":
                k = sum(1 for (a, b) in neighbours(i, j) if types[a][b] != "matte")
                e += 1.5 * k * k
    for i in range(NC):
        for j in range(NR):
            if types[i][j] == "chiseled":
                for (a, b) in neighbours(i, j):
                    if types[a][b] == "chiseled" and orient[a][b] == orient[i][j]:
                        e += 8
    return e


def make_layout(seed=2026):
    rng = np.random.default_rng(seed)
    flat = ["matte"] * COUNTS["matte"] + ["raw"] * COUNTS["raw"] + ["chiseled"] * COUNTS["chiseled"]
    rng.shuffle(flat)
    types = [[flat[i * NR + j] for j in range(NR)] for i in range(NC)]
    ors = []
    for d, n in ORIENT_COUNTS.items():
        ors += [d] * n
    rng.shuffle(ors)
    orient = [[0] * NR for _ in range(NC)]
    k = 0
    for i in range(NC):
        for j in range(NR):
            if types[i][j] == "chiseled":
                orient[i][j] = ors[k]; k += 1
    e = energy(types, orient)
    T = 6.0
    for it in range(60000):
        T = max(0.05, 6.0 * (1 - it / 50000))
        i1, j1, i2, j2 = rng.integers(0, NC), rng.integers(0, NR), rng.integers(0, NC), rng.integers(0, NR)
        if types[i1][j1] == types[i2][j2] and not (types[i1][j1] == "chiseled" and orient[i1][j1] != orient[i2][j2]):
            continue
        types[i1][j1], types[i2][j2] = types[i2][j2], types[i1][j1]
        orient[i1][j1], orient[i2][j2] = orient[i2][j2], orient[i1][j1]
        e2 = energy(types, orient)
        if e2 <= e or rng.random() < np.exp((e - e2) / T):
            e = e2
        else:
            types[i1][j1], types[i2][j2] = types[i2][j2], types[i1][j1]
            orient[i1][j1], orient[i2][j2] = orient[i2][j2], orient[i1][j1]
    return types, orient, e


if __name__ == "__main__":
    types, orient, e = make_layout()
    print("energy", e)
    faces = []
    for i in range(NC):
        for j in range(NR):
            faces.append(dict(index=index_of(i, j), col=i, row=j, type=types[i][j], groove_dir=orient[i][j] if types[i][j] == "chiseled" else None))
    json.dump(faces, open(guard(RUN + "/work/layout.json"), "w"), indent=1)
    for j in range(NR):
        print(" ".join({"matte": " . ", "raw": " R ", "chiseled": "C%3d" % orient[i][j]}[types[i][j]] for i in range(NC)))
    from collections import Counter
    print(Counter(f["type"] for f in faces))
    adj_rr = adj_cc = adj_rc = 0
    for i in range(NC):
        for j in range(NR):
            for (a, b) in neighbours(i, j):
                if (a, b) > (i, j):
                    p = {types[i][j], types[a][b]}
                    if p == {"raw"}: adj_rr += 1
                    if p == {"chiseled"}: adj_cc += 1
                    if p == {"raw", "chiseled"}: adj_rc += 1
    print("adjacent pairs raw-raw", adj_rr, "chis-chis", adj_cc, "raw-chis", adj_rc)
