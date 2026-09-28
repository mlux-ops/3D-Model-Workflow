"""Ground-plane geometry of crosscut_floor_angled.jpg.

The floor photo is a pure-pitch view of a stacked 24 x 48 in grid: the depth
joints converge on one vanishing point, the cross joint is level, and the
depth joints are evenly spaced along every row (no yaw, no roll). For such a
view the plane-to-image mapping is

    X = K * (x - x_vp) / u              u = y - y_vp          (across, inches)
    Z = alpha * (1/u - 1/u_j)                                  (depth, inches)

K is fixed by the 24.0625 in joint pitch. alpha (the camera height / focal
length term) cannot be read from joints because only one cross joint is in
frame; calibrate_floor.py measures it from texture isotropy and stores it in
floor_calibration.json.
"""
import json
import os

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.dirname(HERE)
INPUTS = os.path.normpath(os.path.join(RUN, "..", "inputs"))
FLOOR = os.path.join(INPUTS, "crosscut_floor_angled.jpg")
SWATCH = os.path.join(INPUTS, "crosscut_swatch.webp")
CALIB = os.path.join(HERE, "floor_calibration.json")

PITCH_IN = 24.0625          # tile + joint, across the floor photo
Y_CROSS_JOINT = 260.5       # measured row of the level cross joint
# rough (x at y=0, x at y=349) of the five depth joints, refined by fit_joints()
ROUGH_JOINTS = [(337, 40), (725, 570), (1114, 1104), (1500, 1635), (1887, 2159)]


def load_gray(path):
    return np.asarray(Image.open(path).convert("L")).astype(np.float64)


def load_rgb(path):
    return np.asarray(Image.open(path).convert("RGB")).astype(np.float64)


def fit_joints(gray):
    """Sub-pixel fit of each depth joint as x = c + s*y. Returns fits, VP, rms."""
    h, w = gray.shape
    hp = gray - ndi.gaussian_filter(gray, 4)
    fits, rms = [], []
    for x0, x1 in ROUGH_JOINTS:
        ys, xs = [], []
        for y in range(2, h - 2):
            xp = x0 + (x1 - x0) * y / (h - 1)
            lo, hi = int(round(xp - 8)), int(round(xp + 8))
            if lo < 1 or hi > w - 2:
                continue
            prof = hp[y - 1:y + 2, lo:hi + 1].mean(0)
            i = int(np.argmin(prof))
            if prof[i] > -4:
                continue
            off = 0.0
            if 0 < i < len(prof) - 1:
                d = prof[i - 1] - 2 * prof[i] + prof[i + 1]
                off = 0.5 * (prof[i - 1] - prof[i + 1]) / d if d != 0 else 0.0
            ys.append(y)
            xs.append(lo + i + off)
        ys, xs = np.array(ys, float), np.array(xs, float)
        for _ in range(3):
            p = np.polyfit(ys, xs, 1)
            r = xs - np.polyval(p, ys)
            keep = np.abs(r) < max(2.5 * np.std(r), 0.6)
            ys, xs = ys[keep], xs[keep]
        p = np.polyfit(ys, xs, 1)
        fits.append(p)
        rms.append(float(np.std(xs - np.polyval(p, ys))))
    fits = np.array(fits)
    a = np.column_stack([np.ones(len(fits)), -fits[:, 0]])
    vp = np.linalg.lstsq(a, fits[:, 1], rcond=None)[0]
    return fits, vp, rms


class FloorGeom:
    def __init__(self, alpha=None):
        g = load_gray(FLOOR)
        self.fits, vp, self.joint_rms = fit_joints(g)
        self.x_vp, self.y_vp = float(vp[0]), float(vp[1])
        slopes = self.fits[:, 0]
        self.K = PITCH_IN / float(np.mean(np.diff(slopes)))
        self.joint_X = self.K * slopes          # joint centre lines, inches
        self.u_j = Y_CROSS_JOINT - self.y_vp
        if alpha is None and os.path.exists(CALIB):
            with open(CALIB) as f:
                alpha = json.load(f)["alpha"]
        self.alpha = alpha

    def plane_to_image(self, X, Z, alpha=None):
        al = self.alpha if alpha is None else alpha
        u = 1.0 / (Z / al + 1.0 / self.u_j)
        return self.x_vp + X * u / self.K, self.y_vp + u

    def image_to_plane(self, x, y, alpha=None):
        al = self.alpha if alpha is None else alpha
        u = y - self.y_vp
        return self.K * (x - self.x_vp) / u, al * (1.0 / u - 1.0 / self.u_j)

    def local_res(self, y, alpha=None):
        """Source pixels per inch (across, depth) at image row y."""
        al = self.alpha if alpha is None else alpha
        u = y - self.y_vp
        return u / self.K, u * u / al

    def rectify(self, img, r, X0, X1, Z0, Z1, alpha=None, order=3):
        """Resample img (H,W) or (H,W,C) onto the plane at r px/in.
        Rows run from far (Z1) at the top to near (Z0) at the bottom."""
        X = X0 + (np.arange(int(round((X1 - X0) * r))) + 0.5) / r
        Z = Z1 - (np.arange(int(round((Z1 - Z0) * r))) + 0.5) / r
        ZZ, XX = np.meshgrid(Z, X, indexing="ij")
        x, y = self.plane_to_image(XX, ZZ, alpha)
        chans = [img] if img.ndim == 2 else [img[..., c] for c in range(img.shape[2])]
        out = [ndi.map_coordinates(c, [y, x], order=order, mode="constant", cval=np.nan)
               for c in chans]
        out = out[0] if img.ndim == 2 else np.stack(out, -1)
        return out, XX, ZZ, x, y

    def valid_mask(self, XX, ZZ, x, y, joint_clear=0.6):
        """Stone pixels: inside the frame, off joints, clear of shadows and the far band."""
        ok = (x > 2) & (x < 1997) & (y > 8) & (y < 346)
        dj = np.min(np.abs(XX[..., None] - self.joint_X[None, None, :]), axis=2)
        ok &= dj > joint_clear
        ok &= np.abs(ZZ) > joint_clear
        # two cast shadows at the right edge of the photo (ellipses), with margin
        for cx, cy, ax, ay in [(2010.0, 58.0, 205.0, 45.0), (2040.0, 191.0, 140.0, 48.0)]:
            ok &= ((x - cx) / ax) ** 2 + ((y - cy) / ay) ** 2 > 1.0
        return ok
