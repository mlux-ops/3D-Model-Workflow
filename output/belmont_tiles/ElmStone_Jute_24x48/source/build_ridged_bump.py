"""Build a finely-ridged bump map VARIANT for the existing ELM ElmStone Jute Vein-Cut
24x48 material. This adds a new companion file; it does not touch or regenerate
Color.png, Normal.png, Roughness.png, Bump.png, the VRMAT, or the VRSCENE.

Why a variant, not a replacement
---------------------------------
The delivered Bump.png is intentionally flat (interior std 0.0; a 0.25 mm total range
with a thin 1/16 in edge reveal only) because the shipped finish is a printed, unsculpted
vein-cut face — see README.md: "Printed veins remain flat... Fine glaze/stone relief
cannot be recovered reliably from one lit photo and is not fabricated." The user has now
asked for a second, genuinely ridged finish option of the SAME colour map: a fine linear
("reeded"/"rigato") surface, shown in references/manufacturer_04_installed_ridged.jpg.

Geometry, not photo pixels
---------------------------
Per the repo's fluted-tile precedent (output/remedy_hydro), the ridges are built as a
pure function of the across-ridge coordinate, independent of any photo, so they are
geometrically guaranteed straight, parallel and exactly periodic — never derived from an
angled/perspective shot.

Ridge direction: PARALLEL TO THE VEINING, per user correction 2026-09-20 (the reference
install photo showed vertical ridges, but that is a different panel/orientation than the
shipped colour map and was not the right cue to follow). The shipped Color.png's vein
grain was measured directly with a structure-tensor gradient analysis and runs at
178.4 deg from the image x-axis, i.e. horizontal, parallel to the 48 in width. Ridges
here run along x (constant along x, periodic along y across the 24 in height) to match.
The install photo is retained only as evidence that the finish is fine and uniform; its
own pixel pitch (4.88-5.23 px, self-consistent top-to-bottom within a column) is not a
mm calibration - there is no scale reference in that frame. The 2.00 mm pitch used here
is a stated design estimate for a "finely ridged" linear finish, not a measured fact.
See SOURCE_SELECTION_ridged.md.

Registration
-------------
Output is pixel-identical in size (4096 x 2051) and physical extent
(48.0625 x 24.0625 in) to the shipped Color.png, so it drops in as its Bump slot without
any UV or scale change. The same thin edge-reveal band the shipped Bump.png uses (4 px,
~1/16 in physical module gap) is reproduced here so both bump variants remain consistent
companions to the one Color/Normal/Roughness set.

Relief budget (0.55 mm encoded in the full 16-bit range)
-----------------------------------------------------------
  joint / reveal floor          0.00 mm
  tile plane (ridge valley)     0.15 mm   -> a 0.15 mm riser off the reveal floor
  ridge crest                   0.50 mm   -> 0.35 mm peak-to-valley ridge relief
  headroom to the 16-bit ceiling 0.05 mm  (kept clear of the top so AA never clips)
Ridge relief (0.35 mm) is the pattern term; the reveal floor is untouched and is not
deepened to compensate, per the repo's dimensional-tile rule. The ridge valley — the
pattern's lowest point — sits 0.15 mm clear of the reveal floor (clearance, > 0).

Output
------
textures/Bump_FinelyRidged16.png   16-bit greyscale, 4096 x 2051
textures/ridged_build_report.json
"""

import json
import os
import struct

import numpy as np
from PIL import Image

PRODUCT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def out_path(*parts):
    p = os.path.abspath(os.path.join(PRODUCT_DIR, *parts))
    if os.path.commonpath([p, PRODUCT_DIR]) != PRODUCT_DIR:
        raise RuntimeError("refusing to write outside the product dir: %s" % p)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    return p


SPEC = json.load(open(os.path.join(PRODUCT_DIR, "SPEC.json")))
W_IN, H_IN = SPEC["repeat_inches"]           # 48.0625 x 24.0625 in, matches Color.png
W_PX, H_PX = SPEC["pixels"]                  # 4096 x 2051, matches Color.png exactly

RIDGE_PITCH_MM = 2.00                        # design estimate, see module docstring
RIDGE_PROFILE_POWER = 0.62                   # < 1 sharpens the crest, widens the valley

TOTAL_RANGE_MM = 0.55
RISER_MM = 0.15                              # reveal floor -> tile plane / ridge valley
RIDGE_PTP_MM = 0.35                          # ridge peak-to-valley

REVEAL_BAND_PX = 4                           # matches the shipped Bump.png exactly


def main():
    mm_per_px_x = W_IN * 25.4 / W_PX
    mm_per_px_y = H_IN * 25.4 / H_PX
    print("canvas %d x %d px, %.4f x %.4f in  (%.5f vs %.5f mm/px - should match)"
          % (W_PX, H_PX, W_IN, H_IN, mm_per_px_x, mm_per_px_y))

    # Exact analytic periodicity: choose an integer ridge count over the full pixel
    # HEIGHT closest to the target pitch, so cos(2*pi*N*y/H_PX) is identically equal at
    # y=0 and the (nonexistent) y=H_PX -- pixel 0 and pixel H_PX-1 sit one grid step
    # apart from a true repeat, which is exactly what a wrapped texture needs. Ridges
    # run parallel to the veining (horizontal, along x), so they are periodic in y and
    # constant along x.
    n_ridges = round(H_IN * 25.4 / RIDGE_PITCH_MM)
    actual_pitch_mm = H_IN * 25.4 / n_ridges
    print("ridges across the full height: %d  (actual pitch %.4f mm, target %.2f mm)"
          % (n_ridges, actual_pitch_mm, RIDGE_PITCH_MM))

    y = np.arange(H_PX, dtype=np.float64)
    phase = 2.0 * np.pi * n_ridges * y / H_PX
    c = np.cos(phase)
    shape = np.sign(c) * np.abs(c) ** RIDGE_PROFILE_POWER      # [-1, 1], crest-biased
    ridge_mm_col = RISER_MM + RIDGE_PTP_MM * (shape * 0.5 + 0.5)   # [RISER, RISER+PTP]

    height_mm = np.tile(ridge_mm_col[:, None], (1, W_PX))

    # Edge reveal: pinch all four borders down to the floor over the same pixel band
    # width the shipped Bump.png uses, so this variant wraps exactly (edge column 0
    # equals edge column W_PX-1, edge row 0 equals edge row H_PX-1) and stays a
    # physically consistent companion to the shipped reveal geometry.
    def edge_fade(n, band):
        """0 at the very edge pixel, smoothstepped up to 1 by pixel `band`."""
        f = np.ones(n, dtype=np.float64)
        t = np.arange(band, dtype=np.float64) / band          # 0/band .. (band-1)/band
        ramp = t * t * (3.0 - 2.0 * t)
        f[:band] = ramp
        f[-band:] = ramp[::-1]
        return f

    fx = edge_fade(W_PX, REVEAL_BAND_PX)
    fy = edge_fade(H_PX, REVEAL_BAND_PX)
    fade = fx[None, :] * fy[:, None]
    height_mm = height_mm * fade                      # fades all the way to 0 at the edge

    lo, hi = float(height_mm.min()), float(height_mm.max())
    print("height range achieved: %.4f - %.4f mm (budget 0.00 - %.2f mm)"
          % (lo, hi, RISER_MM + RIDGE_PTP_MM))
    clearance = RISER_MM   # the pattern's lowest non-edge point above the reveal floor
    print("ridge-valley clearance above the reveal floor: %.3f mm" % clearance)
    if clearance <= 0:
        raise RuntimeError("ridge valley does not clear the reveal floor")

    encoded = np.clip(height_mm / TOTAL_RANGE_MM, 0.0, 1.0)
    bump16 = np.round(encoded * 65535.0).astype(np.uint16)

    out = out_path("textures", "Bump_FinelyRidged16.png")
    Image.fromarray(bump16).save(out)

    # verify the on-disk bit depth from the PNG header bytes, not from PIL's dtype
    raw = open(out, "rb").read()
    pw, ph, depth, ctype = struct.unpack(">IIBB", raw[16:26])
    print("wrote %s: header %dx%d depth=%d colour-type=%d (want depth=16, type=0)"
          % (out, pw, ph, depth, ctype))
    assert (pw, ph, depth, ctype) == (W_PX, H_PX, 16, 0), "unexpected PNG header"

    # Wrap check. The ridges are periodic in y and constant in x, so the meaningful
    # "typical neighbour step" comparison is between adjacent ROWS (y direction),
    # where the ridge pattern is actually varying; adjacent columns are identical by
    # construction and would trivially report zero either way.
    lr = float(np.abs(bump16[:, 0].astype(np.int64) - bump16[:, -1].astype(np.int64)).mean())
    tb = float(np.abs(bump16[0, :].astype(np.int64) - bump16[-1, :].astype(np.int64)).mean())
    inner = float(np.abs(bump16[10, :].astype(np.int64) - bump16[11, :].astype(np.int64)).mean())
    print("wrap check: L/R step %.2f   T/B step %.2f   typical neighbour (row-to-row) step %.2f"
          % (lr, tb, inner))

    report = {
        "file": "Bump_FinelyRidged16.png",
        "pixels": [W_PX, H_PX],
        "physical_in": [W_IN, H_IN],
        "ridge_pitch_mm": actual_pitch_mm,
        "ridge_pitch_target_mm": RIDGE_PITCH_MM,
        "ridge_count_across_height": int(n_ridges),
        "ridge_orientation": "horizontal, parallel to the veining "
                              "(constant along width, periodic across height)",
        "vein_angle_deg_measured": 178.4,
        "relief_mm": {
            "total_range": TOTAL_RANGE_MM,
            "reveal_floor": 0.0,
            "tile_plane_ridge_valley": RISER_MM,
            "ridge_peak_to_valley": RIDGE_PTP_MM,
            "ridge_crest": RISER_MM + RIDGE_PTP_MM,
            "clearance_above_reveal_floor": clearance,
        },
        "edge_reveal_band_px": REVEAL_BAND_PX,
        "wrap_check": {"lr_step": lr, "tb_step": tb, "typical_neighbour_step": inner},
        "source": "procedural, direction and fineness informed by "
                   "references/manufacturer_04_installed_ridged.jpg; "
                   "pitch is a design estimate, not measured (no scale reference "
                   "in that photo) - see SOURCE_SELECTION_ridged.md",
    }
    json.dump(report, open(out_path("textures", "ridged_build_report.json"), "w"), indent=2)
    print("wrote textures/ridged_build_report.json")


if __name__ == "__main__":
    main()
