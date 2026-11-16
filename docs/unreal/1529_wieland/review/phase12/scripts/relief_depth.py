"""Phase 12, step 12.5: depth of the relief of a sculpted finish, in millimetres, from its relief image.

    python -P -B relief_depth.py <relief.json> <material> <relief image> <field U in m> <field V in m> <strength> [...]

A relief image (normal map) holds the slope of the surface at every pixel. The slopes are summed back
into heights (the Frankot-Chellappa method, which suits an image that repeats) using the size of one
pixel on the real surface. The depth given is the height between the lowest 2 % and the highest 2 % of
the surface, so that single stray pixels do not set it. Arguments come in groups of five.
"""
import json
import sys

import numpy as np
from PIL import Image

Image.MAX_IMAGE_PIXELS = None


def depth_mm(path, field_u, field_v, strength):
    data = np.asarray(Image.open(path).convert("RGB"), dtype=np.float64) / 255.0 * 2.0 - 1.0
    nz = np.clip(data[:, :, 2], 0.05, 1.0)
    slope_u = -data[:, :, 0] / nz * strength
    slope_v = -data[:, :, 1] / nz * strength
    height, width = slope_u.shape
    step_u, step_v = field_u / width, field_v / height          # metres per pixel
    wu = 2.0 * np.pi * np.fft.fftfreq(width, d=step_u)[None, :]
    wv = 2.0 * np.pi * np.fft.fftfreq(height, d=step_v)[:, None]
    bottom = wu * wu + wv * wv
    bottom[0, 0] = 1.0
    spectrum = (-1j * wu * np.fft.fft2(slope_u) - 1j * wv * np.fft.fft2(slope_v)) / bottom
    spectrum[0, 0] = 0.0
    surface = np.real(np.fft.ifft2(spectrum))
    low, high = np.percentile(surface, [2.0, 98.0])
    return (high - low) * 1000.0


if __name__ == "__main__":
    out, result = sys.argv[1], {}
    groups = sys.argv[2:]
    for index in range(0, len(groups), 5):
        name, path, field_u, field_v, strength = groups[index:index + 5]
        value = depth_mm(path, float(field_u), float(field_v), float(strength))
        result[name] = {"depth_mm": round(value, 2),
                        "how": "summed from the slopes of the relief image over a field of %s by %s m, lowest 2 %% to "
                               "highest 2 %% of the surface" % (field_u, field_v)}
        print(name, "%.2f mm" % value)
    with open(out, "w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=1, sort_keys=True)
