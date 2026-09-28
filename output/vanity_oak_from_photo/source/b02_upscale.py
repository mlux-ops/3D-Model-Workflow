"""Upscale the assembled real-photo map once, at the end, and export the 8-bit sRGB colour map.

- Input: _work/assembly_32ppi.npy (linear RGB float64, 1536 x 768 = 48 x 24 in at 32 px/in).
- Encode to sRGB float64, then 2x cubic-spline interpolation (scipy map order 3, periodic 'grid-wrap' boundary so
  the wrap stays seamless) to 64 px/in = 3072 x 1536.
- Mild unsharp step along the across-grain axis only (y), periodic: out = up + AMOUNT * (up - gauss_y(up, SIGMA)).
  This restores the crispness of the grain lines lost to interpolation; it adds no noise and no new structure.
- Clip, round, write 8-bit RGB PNG (colour type 2). Float64 until this point.

Writes Color.png and _work/upscale.json."""
import json

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

from common import lin_to_srgb, ihdr
from guard import out_path

SCALE = 2
PPI_OUT = 64
SIGMA = 1.4      # px at 64 px/in, across grain only
AMOUNT = 0.45


def main():
    a = np.load(out_path("_work/assembly_32ppi.npy"))
    s = lin_to_srgb(a)                               # float64 0..255
    up = np.stack([ndi.zoom(s[..., c], SCALE, order=3, mode="grid-wrap", grid_mode=True) for c in range(3)], -1)
    blur = ndi.gaussian_filter1d(up, SIGMA, axis=0, mode="wrap")
    out = up + AMOUNT * (up - blur)
    clip_lo, clip_hi = int((out < 0).sum()), int((out > 255).sum())
    img = np.clip(np.round(out), 0, 255).astype(np.uint8)
    p = out_path("Color.png")
    Image.fromarray(img, "RGB").save(p, optimize=True)
    info = {"input": "_work/assembly_32ppi.npy", "input_px": [a.shape[1], a.shape[0]], "input_ppi": 32,
            "method": "sRGB-encoded float64, scipy.ndimage.zoom order=3 (cubic B-spline interpolation), "
                      "mode=grid-wrap, x%d; then unsharp along y only (sigma %.2f px, amount %.2f, wrap)"
                      % (SCALE, SIGMA, AMOUNT),
            "output_px": [img.shape[1], img.shape[0]], "output_ppi": PPI_OUT,
            "pixels_clipped_low": clip_lo, "pixels_clipped_high": clip_hi, "ihdr": ihdr(p)}
    json.dump(info, open(out_path("_work/upscale.json"), "w"), indent=1)
    print(json.dumps(info))


if __name__ == "__main__":
    main()
