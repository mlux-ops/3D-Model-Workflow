"""Production step c03: measure the tile tone in the lifestyle (installed) image.

The owner judged the installed image a darker beige than the render (2026-09-26). The render is
CG artwork whose Matte faces average sRGB 243/231/207; the lifestyle image is the only view of the
tile under real lighting. This script takes the median colour of shadow-free, joint-free Matte
windows chosen by eye (native pixel boxes, drawn on _work/lifestyle_tone_windows.png for the
record). The target is their mean in linear light. Soap and countertop windows are recorded but
not used: they are horizontal surfaces under different light. Writes _work/lifestyle_tone.json.
"""
import json

import numpy as np
from PIL import Image, ImageDraw

from guard import LIFESTYLE_PATH, out_path, save_image
from common import srgb_to_lin, lin_to_srgb

# native boxes (x0, y0, x1, y1) in the 1414 x 2000 lifestyle image
MATTE_WINDOWS = {
    "top_centre_face": (470, 160, 570, 290),
    "centre_face": (410, 600, 590, 780),
    "top_right_face": (740, 20, 880, 130),
}
WHITE_REF = {"soap_bar_top": (150, 1728, 240, 1745), "countertop": (760, 1760, 900, 1800)}


def med(a, box):
    x0, y0, x1, y1 = box
    return np.median(a[y0:y1, x0:x1].reshape(-1, 3), axis=0)


def main():
    L = np.asarray(Image.open(LIFESTYLE_PATH).convert("RGB")).astype(np.float64)
    out = {"matte_windows": {}, "white_ref": {}}
    for k, b in MATTE_WINDOWS.items():
        m = med(L, b)
        lin = srgb_to_lin(m)
        out["matte_windows"][k] = {"box": b, "srgb": m.round(1).tolist(), "lin_r_over_g": float(lin[0] / lin[1]),
                                   "lin_b_over_g": float(lin[2] / lin[1])}
    for k, b in WHITE_REF.items():
        out["white_ref"][k] = {"box": b, "srgb": med(L, b).round(1).tolist()}
    lins = np.array([srgb_to_lin(np.array(v["srgb"])) for v in out["matte_windows"].values()])
    # mean in linear light over the lit Matte windows: the top windows are the brightest-lit,
    # the centre face is typical; the white references sit under different light (horizontal
    # surfaces, shadow), so they are recorded but not used
    target_lin = lins.mean(axis=0)
    out["target_lin"] = target_lin.tolist()
    out["target_srgb"] = np.round(lin_to_srgb(target_lin), 1).tolist()
    json.dump(out, open(out_path("_work", "lifestyle_tone.json"), "w"), indent=1)
    th = Image.fromarray(L.astype(np.uint8)).resize((566, 800), Image.LANCZOS)
    d = ImageDraw.Draw(th)
    s = 566 / L.shape[1]
    for b in list(MATTE_WINDOWS.values()) + list(WHITE_REF.values()):
        d.rectangle([b[0] * s, b[1] * s, b[2] * s, b[3] * s], outline=(255, 0, 0), width=2)
    save_image(th, "_work", "lifestyle_tone_windows.png")
    for k, v in out["matte_windows"].items():
        print("%-18s sRGB %s  lin R/G %.3f B/G %.3f" % (k, v["srgb"], v["lin_r_over_g"], v["lin_b_over_g"]))
    for k, v in out["white_ref"].items():
        print("%-18s sRGB %s" % (k, v["srgb"]))
    print("target (mean of Matte windows, linear) sRGB %s" % out["target_srgb"])


if __name__ == "__main__":
    main()
