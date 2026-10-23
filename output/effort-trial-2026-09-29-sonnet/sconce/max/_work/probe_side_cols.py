# -*- coding: utf-8 -*-
"""Column occupancy of the side photo and my hosted no-disc side render (data only, prints numbers)."""
import numpy as np
from PIL import Image

ROOT = "E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce"
RUN = ROOT + "/max"


def cols(path, thr):
    a = np.asarray(Image.open(path).convert("RGB")).astype(int).min(axis=2)
    m = a < thr
    cnt = m.sum(axis=0)
    return a, m, cnt


for name, path, thr in [("photo", ROOT + "/inputs/KW1041_MWT_side_reference.jpg", 250),
                        ("mine", RUN + "/views/hosted_no_disc_side.png", 250)]:
    a, m, cnt = cols(path, thr)
    ys, xs = np.nonzero(m)
    print(name, a.shape, "bbox x %d..%d y %d..%d" % (xs.min(), xs.max(), ys.min(), ys.max()))
    nz = np.nonzero(cnt > 0)[0]
    x0 = nz.min()
    step = max(1, (nz.max() - x0) // 40)
    out = []
    for x in range(x0, nz.max() + 1, step):
        col = np.nonzero(m[:, x])[0]
        if len(col) == 0:
            out.append("%d:0" % x)
            continue
        out.append("%d:%d(%d-%d)" % (x, cnt[x], col.min(), col.max()))
    print(" ".join(out))
