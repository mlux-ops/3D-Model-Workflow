"""Phase 9, step 9.8: compare pictures of view S1 computed at 60, 67 and 75 percent of the output size (and at 100
percent as the reference) on foliage and on brick.

Usage:
    python -B upscale_compare.py

Reads review/phase9/realtime/U60, U67, U75 and U100 (S1_realtime.0000.png, 3840 by 2160). For each crop it prints
the fine detail kept, as a share of the 100 percent picture's (mean strength of the pixel-to-pixel contrast, the
Laplacian, of the luminance), and the mean difference to the 100 percent picture in percent of its brightness.
Writes one sheet per crop to review/phase9/sheets/j8_upscale_<crop>.jpg, the four pictures side by side at full size.
"""

import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__)).replace(os.sep, "/")
P9 = HERE.rsplit("/", 1)[0]
STATES = [("100 percent (reference)", "U100"), ("75 percent", "U75"), ("67 percent (the plan's tier)", "U67"), ("60 percent", "U60")]
CROPS = {"foliage_left": (0, 0, 624, 576), "foliage_right": (2808, 72, 3168, 720), "brick": (0, 600, 864, 1248),
         "railing": (1500, 1500, 2260, 1760)}


def luminance(image):
    c = np.asarray(image.convert("RGB")).astype(np.float32) / 255.0
    lin = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    return 0.2126 * lin[..., 0] + 0.7152 * lin[..., 1] + 0.0722 * lin[..., 2]


def detail(lum):
    lap = 4 * lum[1:-1, 1:-1] - lum[:-2, 1:-1] - lum[2:, 1:-1] - lum[1:-1, :-2] - lum[1:-1, 2:]
    return float(np.abs(lap).mean())


def main():
    pictures = {tag: Image.open("%s/realtime/%s/S1_realtime.0000.png" % (P9, tag)).convert("RGB") for _, tag in STATES}
    os.makedirs(P9 + "/sheets", exist_ok=True)
    print("| Crop of view S1 | Computed at | Fine detail kept (100 percent picture = 100) | Mean difference to the 100 percent picture |")
    print("|---|---|---|---|")
    for name, box in CROPS.items():
        crops = [(caption, pictures[tag].crop(box)) for caption, tag in STATES]
        reference = luminance(crops[0][1])
        for caption, crop in crops:
            lum = luminance(crop)
            print("| %s | %s | %.0f | %.1f %% |" % (name, caption, 100.0 * detail(lum) / detail(reference),
                                                   100.0 * float(np.abs(lum - reference).mean()) / float(reference.mean())))
        width, height = crops[0][1].size
        sheet = Image.new("RGB", (width * len(crops) + 8 * (len(crops) - 1), height + 28), "white")
        draw = ImageDraw.Draw(sheet)
        for index, (caption, crop) in enumerate(crops):
            left = index * (width + 8)
            draw.text((left + 4, 6), "S1 %s: %s" % (name, caption), fill="black")
            sheet.paste(crop, (left, 28))
        sheet.save("%s/sheets/j8_upscale_%s.jpg" % (P9, name), quality=92)
    return 0


if __name__ == "__main__":
    sys.exit(main())
