"""Shared constants and helpers for the ELM Fog Cross-Cut Chevron 24x48 build.

Every measured number here comes from source/_analysis (analyse_chevron.py,
analyse_grooves.py) run on ELM's flat straight-on swatch of the 48 x 110 in
slab. Assumed numbers are marked ASSUMED.
"""
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
PROD = os.path.dirname(HERE)
REF = os.path.join(PROD, "references", "candidates")

SLAB_SRC = os.path.join(REF, "6508c8490fee3dfe7508423d_ElmStone_Fog_Cross-Cut_Chevron-Deco_48x110_01.jpg")
# Florim's own copy of the same swatch (MILE stone), stored portrait. Pixel-registered
# with SLAB_SRC once rotated (shift 0,0, low-pass r 0.995) but with 2.2x the JPEG bits
# and no 8x8 block artefacts, so it supplies the slab pixels. SLAB_SRC stays the
# geometry-analysis and identification reference.
SLAB_PIXELS_SRC = os.path.join(REF, "MILE_stone_EcoStone_Fog_CrossCut_ChevronDeco_48x110_01.jpg")
FACE24_SRC = os.path.join(REF, "6508c8490fee3dfe75084232_ELMStone_Fog_Cross_Cut_24x48_03.jpg")
# ELM's groove-free render of the same 48 x 110 stone graphic, pixel-registered with
# SLAB_SRC (phase-correlation shift 0,0; low-pass r = 0.990). Used only to validate
# the de-grooving, never as a colour source (it is 2000 px wide versus 4460).
GROOVE_FREE_CHECK = os.path.join(PROD, "..", "belmont_tiles", "ElmStone_Jute_24x48",
                                 "references", "manufacturer_03_flat_swatch.webp")

SLAB_IN = (110.0, 48.0)                     # manufacturer size, W x H, landscape

# ---- measured chevron geometry (slab swatch, px, y down) --------------------------
SPINE_ROWS = [0, 309, 645, 974, 1264, 1625, 1951]
BAND_LINE_DEG = [130.40, 49.36, 131.67, 49.58, 130.48, 49.32]    # groove line angle
BAND_PITCH_PX = [7.580, 8.155, 7.846, 7.579, 8.380, 7.550]      # perpendicular pitch

# ---- module (repo rule: nominal size = installed module) ----------------------------
MODULE_IN = (48.0, 24.0)                    # landscape; long side parallel to the spines
JOINT_IN = 1.0 / 16.0                       # ASSUMED: ELM/Florim publish no joint width
COLS, ROWS = 3, 4                           # even row count keeps the band alternation
PPI = 6144 / (COLS * MODULE_IN[0])          # 42.667 px/in -> 6144 x 4096 px

# ---- relief budget, mm above the grout floor ------------------------------------------
HEIGHT_RANGE_MM = 1.70                      # full 0..65535 range of the bump PNG
GROUT_FLOOR_MM = 0.00
TILE_PLANE_MM = 1.50                        # crest level of the chevron ridges
GROOVE_DEPTH_MM = 0.80                      # crest to valley, the sculpted pattern
MICRO_MM = 0.02                             # matte micro-relief, +/-
CHAMFER_MM = 0.30                           # eased rectified edge, drop at the arris
CHAMFER_W_MM = 1.50                         # width of that ease on the tile face

# ---- colour / roughness targets -------------------------------------------------------
GROUT_RGB = (222.0, 217.0, 206.0)           # ASSUMED matching light grout
ROUGH_FACE = 0.62                           # ASSUMED matte porcelain estimate
ROUGH_VALLEY_ADD = 0.06
ROUGH_GROUT = 0.90


def load_rgb(path):
    return np.asarray(Image.open(path).convert("RGB")).astype(np.float64)


def load_slab():
    """Slab swatch pixels, landscape 4460 x 1951, same orientation as SLAB_SRC."""
    im = Image.open(SLAB_PIXELS_SRC).convert("RGB").transpose(Image.Transpose.ROTATE_270)
    a = np.asarray(im).astype(np.float64)
    assert a.shape[:2] == (1951, 4460), a.shape
    return a


def srgb_to_lin(c):
    c = c / 255.0
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def lin_to_srgb(c):
    c = np.clip(c, 0.0, 1.0)
    return 255.0 * np.where(c <= 0.0031308, c * 12.92, 1.055 * np.power(c, 1 / 2.4) - 0.055)


def lum(rgb):
    return rgb[..., 0] * 0.2126 + rgb[..., 1] * 0.7152 + rgb[..., 2] * 0.0722


def png_header(path):
    """(width, height, bit_depth, colour_type) straight from the IHDR chunk."""
    with open(path, "rb") as fh:
        b = fh.read(33)
    assert b[:8] == b"\x89PNG\r\n\x1a\n" and b[12:16] == b"IHDR", path
    w = int.from_bytes(b[16:20], "big")
    h = int.from_bytes(b[20:24], "big")
    return w, h, b[24], b[25]
