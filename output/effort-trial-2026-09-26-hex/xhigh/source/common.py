"""Shared constants and geometry for the ELM Formed Hexagon Sand atlas.

Fixed geometry (trial brief, do not change):
  flat-top regular hexagons, 10.000 in across the flats (11.547 in point to point)
  1/8 in joint -> module across the flats 10.125 in
  atlas 8 columns x 7 rows = 56 hexagons at 64 px/in -> 4489 x 4536 px
  Revit Sample Size 70.148 x 70.875 in, Repeat on in both directions

Lattice: column j (0..7) centre x = (j + 0.5) * W/8; even columns have centres at
y = H/14 * (2i + 1) (their horizontal joints lie on y = 0, 648, ...), odd columns at
y = i * H/7.  Pixel centres are at (x + 0.5, y + 0.5).  Everything is computed on the
torus, so the image wraps by construction.
"""
import numpy as np

PX_PER_IN = 64.0
MM_PER_IN = 25.4
FLATS_IN = 10.0
JOINT_IN = 0.125
MODULE_F_IN = FLATS_IN + JOINT_IN               # 10.125 in across flats
MODULE_C_IN = MODULE_F_IN * 2.0 / np.sqrt(3.0)  # 11.691 in point to point (module)
NC, NR = 8, 7
W, H = 4489, 4536
PITCH_X = W / float(NC)          # 561.125 px   (ideal 1.5 * R = 561.18; 0.01 % anisotropy)
PITCH_Y = H / float(NR)          # 648 px
HALF_JOINT_PX = JOINT_IN * PX_PER_IN / 2.0       # 4 px -> 8 px joint
SAMPLE_W_IN = NC * 0.75 * MODULE_C_IN            # 70.148 in
SAMPLE_H_IN = NR * MODULE_F_IN                   # 70.875 in
MM_PER_PX = MM_PER_IN / PX_PER_IN                # 0.396875 mm


def face_centres():
    """(56, 2) array of face centres in pixel coordinates, index = i*8 + j (face index - 1)."""
    c = np.zeros((NR * NC, 2))
    for i in range(NR):
        for j in range(NC):
            x = (j + 0.5) * PITCH_X
            y = (i + 0.5) * PITCH_Y if j % 2 == 0 else i * PITCH_Y
            c[i * NC + j] = (x, y)
    return c


def neighbours(n):
    """Indices of the 6 torus neighbours of face n (= i*8 + j)."""
    i, j = divmod(n, NC)
    out = [((i - 1) % NR, j), ((i + 1) % NR, j)]
    for dj in (-1, 1):
        jj = (j + dj) % NC
        if j % 2 == 0:       # even column centre at (i+0.5)*P; odd neighbours at rows i and i+1
            rows = (i, i + 1)
        else:                # odd column centre at i*P; even neighbours at rows i-1 and i
            rows = (i - 1, i)
        for ii in rows:
            out.append((ii % NR, jj))
    return [a * NC + b for a, b in out]


def lattice_maps():
    """owner (nearest face, int16), edge_d (px to the joint centreline), dx, dy (torus offset
    from the owner centre, px).  Computed in strips to bound memory."""
    owner = np.zeros((H, W), np.int16)
    edge_d = np.zeros((H, W), np.float32)
    dxm = np.zeros((H, W), np.float32)
    dym = np.zeros((H, W), np.float32)
    xs = np.arange(W) + 0.5
    strip = 256
    for y0 in range(0, H, strip):
        y1 = min(H, y0 + strip)
        X, Y = np.meshgrid(xs, np.arange(y0, y1) + 0.5)
        jc = np.floor(X / PITCH_X).astype(np.int64)          # column whose centre is nearest in x
        cand = []                                            # (cx, cy, face) arrays, unwrapped
        for dj in (-1, 0, 1):
            j = jc + dj
            cx = (j + 0.5) * PITCH_X
            off = np.where(j % 2 == 0, 0.5 * PITCH_Y, 0.0)
            i_f = np.floor((Y - off) / PITCH_Y).astype(np.int64)
            for di in (-1, 0, 1, 2):
                i = i_f + di
                cy = (i * PITCH_Y) + off
                face = (i % NR) * NC + (j % NC)
                cand.append((cx, cy, face))
        d = np.stack([(X - c[0]) ** 2 + (Y - c[1]) ** 2 for c in cand])   # (12, h, w)
        k0 = np.argmin(d, axis=0)
        best = np.take_along_axis(d, k0[None], 0)[0]
        CX = np.stack([c[0] for c in cand])
        CY = np.stack([c[1] for c in cand])
        FC = np.stack([c[2] for c in cand])
        c0x = np.take_along_axis(CX, k0[None], 0)[0]
        c0y = np.take_along_axis(CY, k0[None], 0)[0]
        ed = np.full(best.shape, 1e9)
        for k in range(len(cand)):
            sep = np.hypot(CX[k] - c0x, CY[k] - c0y)
            ok = sep > 1.0
            v = np.where(ok, (d[k] - best) / (2.0 * np.maximum(sep, 1.0)), 1e9)
            ed = np.minimum(ed, v)
        owner[y0:y1] = np.take_along_axis(FC, k0[None], 0)[0].astype(np.int16)
        edge_d[y0:y1] = ed
        dxm[y0:y1] = X - c0x
        dym[y0:y1] = Y - c0y
    return owner, edge_d, dxm, dym


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def to_srgb8(rgb):
    return np.clip(np.round(rgb), 0, 255).astype(np.uint8)
