"""Source decoding: the Porcelanosa JPEGs carry an Adobe RGB (1998) ICC profile. Decode to float64 LINEAR sRGB
(D65) via the published Adobe RGB -> XYZ -> sRGB matrices (pure 563/256 gamma), no 8-bit round trip.
Out-of-sRGB-gamut values are clipped to [0, 1] and counted (see gamut_report)."""
import io
import os

import numpy as np
from PIL import Image, ImageCms

from common import LUMA
from guard import ref

ADOBE_TO_XYZ = np.array([[0.5767309, 0.1855540, 0.1881852],
                         [0.2973769, 0.6273491, 0.0752741],
                         [0.0270343, 0.0706872, 0.9911085]])
XYZ_TO_SRGB = np.array([[3.2404542, -1.5371385, -0.4985314],
                        [-0.9692660, 1.8760108, 0.0415560],
                        [0.0556434, -0.2040259, 1.0572252]])
M = XYZ_TO_SRGB @ ADOBE_TO_XYZ
GAMMA = 563.0 / 256.0


def face_file(i):
    return ref("100348304_%s.jpg" % (("%03d" % i) if isinstance(i, int) else i))


def profile_name(path):
    im = Image.open(path)
    icc = im.info.get("icc_profile")
    return ImageCms.getProfileDescription(ImageCms.ImageCmsProfile(io.BytesIO(icc))).strip() if icc else None


def load_face_lin(i, report=None):
    p = face_file(i)
    if profile_name(p) != "Adobe RGB (1998)":
        raise ValueError("unexpected colour profile in %s: %s" % (os.path.basename(p), profile_name(p)))
    a = np.asarray(Image.open(p).convert("RGB")).astype(np.float64) / 255.0
    lin = (a ** GAMMA) @ M.T
    if report is not None:
        report[os.path.basename(p)] = {"below0": float((lin < 0).mean()), "above1": float((lin > 1).mean())}
    return np.clip(lin, 0, 1)


def lum(a):
    return a @ LUMA
