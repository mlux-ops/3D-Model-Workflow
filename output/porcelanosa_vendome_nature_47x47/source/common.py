"""Shared helpers: colour transforms, 16-bit PNG writer, IHDR reader, NCC."""
import struct
import zlib

import numpy as np
from scipy.signal import fftconvolve

MM = 25.4
LUMA = np.array([0.2126, 0.7152, 0.0722])


def srgb_to_lin(c):
    c = np.asarray(c, dtype=np.float64) / 255.0
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def lin_to_srgb(c):
    c = np.clip(c, 0, 1)
    return 255.0 * np.where(c <= 0.0031308, c * 12.92, 1.055 * np.power(c, 1 / 2.4) - 0.055)


def lum(a):
    return a @ LUMA


def write_png16(path, arr16):
    h, w = arr16.shape
    raw = b"".join(b"\x00" + arr16[y].astype(">u2").tobytes() for y in range(h))

    def chunk(t, d):
        c = struct.pack(">I", len(d)) + t + d
        return c + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)
    png = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 16, 0, 0, 0, 0))
           + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(png)


def ihdr(path):
    with open(path, "rb") as f:
        b = f.read(33)
    assert b[:8] == b"\x89PNG\r\n\x1a\n" and b[12:16] == b"IHDR", path
    w, h, depth, ctype, comp, filt, inter = struct.unpack(">IIBBBBB", b[16:29])
    return {"w": w, "h": h, "bit_depth": depth, "colour_type": ctype, "interlace": inter}


def ncc_map(img, tpl):
    t = tpl - tpl.mean()
    tn = np.sqrt((t * t).sum())
    num = fftconvolve(img, t[::-1, ::-1], mode="valid")
    o = np.ones_like(t)
    s1 = fftconvolve(img, o, mode="valid")
    s2 = fftconvolve(img * img, o, mode="valid")
    return num / (np.sqrt(np.maximum(s2 - s1 * s1 / t.size, 1e-9)) * tn)


def orient(a, t):
    """Orientation-preserving transforms of a horizontally-veined face (veins stay horizontal)."""
    return {"r0": a, "flipH": a[:, ::-1], "flipV": a[::-1], "r180": a[::-1, ::-1]}[t]


def ftin(x):
    ft = int(x // 12)
    return "%d'-%.3fin" % (ft, x - 12 * ft)
