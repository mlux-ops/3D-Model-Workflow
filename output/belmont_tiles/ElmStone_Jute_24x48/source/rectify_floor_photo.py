"""Perspective-correct the user-supplied angled floor photo of the cross-cut finish,
per WORKFLOW.md: "Correct photographic perspective and baked lighting while preserving
the product's actual color and character." This is a genuine second real photograph of
the cross-cut material (references/07_new_floor_angled_crosscut.jpg, 2000x349), which
matters because the earlier cross-cut atlas had only one source photo and could not
show two truly different real crops -- see build_nonrepeating_color.py's docstring.

Method: single-vanishing-point ground-plane rectification
--------------------------------------------------------------
The photo shows floor tiles receding away from the camera with no roll (the photographer
held the camera level). Four grout joints running in the "away" direction were found by
a simple weighted Hough line search (near-vertical lines, x = m*y + b) over a
"locally darker than its blurred surround" mask -- the standard way grout has been
isolated elsewhere in this repo. Their pairwise intersections agree tightly:

    line (m, b)              pairwise VP estimate
    (-0.03, 1116)             (1143.9, -928.6)
    (-0.45,  726)             (1144.1, -935.0)
    (-0.86,  340)             (1144.1, -936.6)
    ( 0.38, 1500)

  -> vanishing point (VP_X, VP_Y) = (1144.0, -933.4), the average.

These 4 joints are also confirmed to be evenly spaced in the WORLD (not just visually
plausible): at the bottom row their pixel spacing is 528/537/527 px (essentially equal),
and standard ground-plane perspective predicts that a constant world-space spacing
projects to image spacing proportional to v(y) = y - VP_Y. Checking that prediction
against two different rows (spacing 530.7 px at y=348 where v=1281.4, spacing 407.3 px
at y=50 where v=983.4; predicted ratio 1281.4/983.4=1.303, measured ratio
530.7/407.3=1.303) confirms VP_Y to within better than a pixel. That agreement is what
justifies treating this as a real single-point ground-plane perspective, not just a
plausible-looking curve fit.

Rectification then follows the standard single-vanishing-point ground-plane formula,
using a **locally-isotropic simplification**: the true metric relationship between
image-row and world depth also depends on the camera's tilt/focal length, which are not
recoverable from one photo, so an exact metric rectification is not attempted -- this
is a texture-extraction task, not a survey. Instead, the local magnification factor
v(y)/v(reference row) is applied to BOTH axes at each row, which straightens and evenly
spaces the joints (the visually dominant defect) at the cost of a small, unmeasured
residual error in the exact depth compression. The bottom row (closest to the camera,
native resolution highest) is the reference scale, so no row is upsampled beyond its own
native detail; only farther rows are stretched to remove their compression, which is the
correct direction for a rectification (adds no fabricated detail, only undoes the
photographed compression).

Output is cropped to the horizontal extent visible at the reference (bottom) row only,
which guarantees every rectified pixel has real photographed content behind it -- the
alternative (keeping the wider extent visible in farther rows) would leave the near
rows' edges empty, since the camera's fixed field of view genuinely does not see that
far to the sides at close range.

A shadow (from an off-frame object) in the original photo's top-right corner was
checked and is not a problem: the reference-row-width crop naturally excludes most of
it (rows where the shadow appears have ratio < 1, so their sampled horizontal range
does not reach that far right), and a numeric check found under 0.01% of the rectified
image below a shadow-level brightness threshold.

Outputs
-------
references/07_floor_rectified.png     the corrected floor photo, 2000 x 301
references/07_crop_tile1.jpg          clean, joint-free crop from one tile
references/07_crop_tile3.jpg          clean, joint-free crop from a different tile
"""

import os

import numpy as np
from PIL import Image

FLAT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BELMONT_DIR = os.path.dirname(FLAT_DIR)
CROSSCUT_DIR = os.path.join(BELMONT_DIR, "ElmStone_Jute_CrossCut_24x48")
REFS = os.path.join(CROSSCUT_DIR, "references")

SRC = os.path.join(REFS, "07_new_floor_angled_crosscut.jpg")
VP_X, VP_Y = 1144.0, -933.4


def rectify(src_path, vp_x, vp_y):
    im = np.asarray(Image.open(src_path).convert("RGB"), dtype=np.float64)
    h, w, _ = im.shape

    def v(y):
        return y - vp_y

    v_ref = v(h - 1)   # closest row = reference scale (native resolution preserved there)

    ys = np.arange(h, dtype=np.float64)
    row_scale = v(ys) / v_ref
    cum = np.concatenate([[0.0], np.cumsum((row_scale[:-1] + row_scale[1:]) * 0.5)])
    out_h = int(np.ceil(cum[-1]))
    out_rows = np.arange(out_h, dtype=np.float64)
    src_y = np.interp(out_rows, cum, ys)

    x0_ref, x1_ref = (0 - vp_x), (w - 1 - vp_x)   # bottom row's own extent, ratio = 1
    out_w = int(round(x1_ref - x0_ref)) + 1
    Xp = np.linspace(x0_ref, x1_ref, out_w)

    out = np.zeros((out_h, out_w, 3), dtype=np.float64)
    for r in range(out_h):
        sy = src_y[r]
        ratio = v(sy) / v_ref
        sx = np.clip(vp_x + Xp * ratio, 0, w - 1)
        xi0 = np.floor(sx).astype(int)
        xi1 = np.clip(xi0 + 1, 0, w - 1)
        fx = sx - xi0
        yi0 = int(np.floor(sy))
        yi1 = min(yi0 + 1, h - 1)
        fy = sy - yi0
        row0 = im[yi0, xi0] * (1 - fx)[:, None] + im[yi0, xi1] * fx[:, None]
        row1 = im[yi1, xi0] * (1 - fx)[:, None] + im[yi1, xi1] * fx[:, None]
        out[r] = row0 * (1 - fy) + row1 * fy

    return np.clip(out, 0, 255).astype(np.uint8)


def main():
    rect = rectify(SRC, VP_X, VP_Y)
    print("rectified %s -> %s" % (Image.open(SRC).size, (rect.shape[1], rect.shape[0])))

    g = rect.mean(axis=2)
    dark = (g < 170).mean()
    print("residual-shadow check: %.4f%% of pixels below brightness 170" % (dark * 100))

    out_path = os.path.join(REFS, "07_floor_rectified.png")
    Image.fromarray(rect).save(out_path)
    print("wrote", out_path)

    # Three clean, joint-free, differently-composed crops for use as atlas sources.
    # Joint x-positions at the reference row were computed during line-fitting (see
    # module docstring): approx 41, 569, 1106, 1633 -- these bounds sit safely inside
    # each of the first three tiles, as wide as the tile allows.
    Image.fromarray(rect[8:296, 62:550]).save(
        os.path.join(REFS, "07_crop_tile1.jpg"), quality=95)
    Image.fromarray(rect[8:296, 590:1085]).save(
        os.path.join(REFS, "07_crop_tile2.jpg"), quality=95)
    Image.fromarray(rect[8:296, 1125:1615]).save(
        os.path.join(REFS, "07_crop_tile3.jpg"), quality=95)
    print("wrote 07_crop_tile1.jpg, 07_crop_tile2.jpg, 07_crop_tile3.jpg")


if __name__ == "__main__":
    main()
