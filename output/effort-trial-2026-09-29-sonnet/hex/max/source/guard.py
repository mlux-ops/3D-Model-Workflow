"""Shared helpers: write guard (nothing may be written outside the run folder),
input path resolution, PNG save with the errno-22 retry, and PNG header reader."""

import os
import struct
import time

import numpy as np
from PIL import Image

RUN_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
INPUT_DIR = os.path.abspath(os.path.join(RUN_DIR, "..", "inputs"))

RENDER_PATH = os.path.join(INPUT_DIR, "elm_formed_hex_sand_layout_render.webp")
LIFESTYLE_PATH = os.path.join(INPUT_DIR, "elm_formed_hex_sand_lifestyle_angled.webp")


def out_path(*parts):
    """Absolute path inside the run folder; raises for anything that escapes it."""
    p = os.path.abspath(os.path.join(RUN_DIR, *parts))
    if os.path.commonpath([p, RUN_DIR]) != RUN_DIR:
        raise RuntimeError("refusing to write outside the run folder: %s" % p)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    return p


def _retry(fn, what, tries=6):
    last = None
    for k in range(tries):
        try:
            return fn()
        except OSError as e:
            last = e
            print("  OSError while writing %s (attempt %d): %s" % (what, k + 1, e))
            time.sleep(0.5 * (k + 1))
    raise last


def save_image(img, *parts, **kw):
    """Save a PIL image through the guard, retrying the known errno-22 failure."""
    p = out_path(*parts)
    _retry(lambda: img.save(p, **kw), p)
    return p


def save_bytes(data, *parts):
    p = out_path(*parts)

    def w():
        with open(p, "wb") as f:
            f.write(data)
    _retry(w, p)
    return p


def save_text(text, *parts):
    p = out_path(*parts)

    def w():
        with open(p, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
    _retry(w, p)
    return p


def save_npy(arr, *parts):
    p = out_path(*parts)
    _retry(lambda: np.save(p, arr), p)
    return p


def png_header(path):
    """(width, height, bit_depth, colour_type) from the IHDR chunk bytes."""
    with open(path, "rb") as f:
        head = f.read(33)
    if head[:8] != b"\x89PNG\r\n\x1a\n" or head[12:16] != b"IHDR":
        raise ValueError("not a PNG: %s" % path)
    w, h, depth, ctype = struct.unpack(">IIBB", head[16:26])
    return w, h, depth, ctype


def load_gray16(path):
    """16-bit greyscale PNG as uint16 array (PIL mode I;16 or I)."""
    im = Image.open(path)
    return np.asarray(im).astype(np.uint16)
