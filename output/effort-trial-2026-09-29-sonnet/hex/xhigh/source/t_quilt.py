"""Quick test of the quilting on the matte and raw libraries: speed and a preview crop."""
import os
import sys
import time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image
import guard
import render_grid as rg
import quilt

Z = np.load(rg.WORK + "libs.npz")
print(sorted(Z.files)[:12], len(Z.files))
for name, block, ov in (("matte", 56, 14), ("raw", 36, 10)):
    n = int(Z[name + "_n"])
    stack = quilt.pad_windows([Z["%s_%d_ch" % (name, k)] for k in range(n)])
    masks = quilt.pad_windows([Z["%s_%d_m" % (name, k)] for k in range(n)], False)
    print(name, stack.shape, masks.shape, masks.mean())
    lib = quilt.Library(stack, masks, block)
    print(" candidates", len(lib.cand), "scale", lib.scale)
    rng = np.random.default_rng(1)
    t0 = time.time()
    canvas, placed = quilt.quilt(lib, 327, 375, ov, rng)
    print(" quilt time %.1f s canvas %s" % (time.time() - t0, canvas.shape))
    z = canvas[..., 0]
    print(" z std", z.std(), "min", z.min(), "max", z.max())
    v = np.clip(128 + z * (40.0 / max(z.std(), 1e-6)) * 0.5, 0, 255).astype(np.uint8)
    guard.save_image(Image.fromarray(v), rg.WORK + "thumbs/t_quilt_%s.png" % name)
