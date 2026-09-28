"""Shared helpers: colour transforms, image IO, IHDR reader, thumbnails, bilinear sampling."""
import struct

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

LUMA = np.array([0.2126, 0.7152, 0.0722])


def srgb_to_lin(c):
    c = np.asarray(c, dtype=np.float64) / 255.0
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def lin_to_srgb(c):
    c = np.clip(c, 0, 1)
    return 255.0 * np.where(c <= 0.0031308, c * 12.92, 1.055 * np.power(c, 1 / 2.4) - 0.055)


def lum(a):
    return a @ LUMA


def load_rgb(path):
    return np.asarray(Image.open(path).convert("RGB"), dtype=np.float64)


def ihdr(path):
    with open(path, "rb") as f:
        b = f.read(33)
    assert b[:8] == b"\x89PNG\r\n\x1a\n" and b[12:16] == b"IHDR", path
    w, h, depth, ctype, comp, filt, inter = struct.unpack(">IIBBBBB", b[16:29])
    return {"w": w, "h": h, "bit_depth": depth, "colour_type": ctype, "interlace": inter}


def thumb(arr_or_img, path, maxdim=800, quality=92):
    """Save a <= maxdim px JPEG view (box-filtered, so no aliasing)."""
    im = arr_or_img if isinstance(arr_or_img, Image.Image) else Image.fromarray(
        np.clip(np.round(arr_or_img), 0, 255).astype(np.uint8))
    s = min(1.0, maxdim / max(im.size))
    if s < 1:
        im = im.resize((max(1, round(im.size[0] * s)), max(1, round(im.size[1] * s))), Image.LANCZOS)
    im.save(path, quality=quality)
    return im.size


def sample_bilinear(img, xs, ys):
    """Sample an HxWxC float image at float pixel-centre coords (order-1 spline, per channel)."""
    out = np.empty(xs.shape + (img.shape[2],))
    for c in range(img.shape[2]):
        out[..., c] = ndi.map_coordinates(img[..., c], [ys, xs], order=1, mode="nearest")
    return out


def sample_cubic(img, xs, ys):
    out = np.empty(xs.shape + (img.shape[2],))
    for c in range(img.shape[2]):
        out[..., c] = ndi.map_coordinates(img[..., c], [ys, xs], order=3, mode="nearest", prefilter=True)
    return out


def ftin(x):
    ft = int(x // 12)
    return "%d'-%.3fin" % (ft, x - 12 * ft)
