"""Stage 1: prepare the two photographic sources at 64 px/in.

- Swatch: notch out the periodic horizontal scan-line artifact (period 3.77 px),
  resample 41.67 -> 64 px/in (Lanczos), remove a linear illumination plane.
- Floor photo: ground-plane rectification from the fitted tile joints, sampled
  directly at 64 px/in, per-tile illumination plane removal, tone match to swatch.
Outputs go to ../_work/ as float32 .npy (linear 0..255 sRGB code values).
"""
import json, os
import numpy as np
from PIL import Image
from scipy.ndimage import map_coordinates, gaussian_filter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
INP = os.path.join(ROOT, '..', 'inputs')
WORK = os.path.join(ROOT, '_work')
os.makedirs(WORK, exist_ok=True)
PPI = 64
SWATCH_PPI = 2000 / 48.0          # brief: swatch spans ~48 in -> 41.67 px/in

# ---- floor geometry (fitted in the floor photo, see README) ----
# Vertical joints, x at y=0 and x at y=348 (least-darkness line search)
JOINTS = {'A': (338.5, 39.0), 'B': (725.5, 570.0), 'C': (1114.0, 1103.5),
          'D': (1501.0, 1634.5), 'E': (1889.5, 2166.5)}
Y_H = -935.4        # horizon row: joint spacing s(y)=387.75+0.4145y reaches 0
X_V = 1142.5        # vanishing column (joint lines intersect here)
H_ACROSS = 24.0 / 0.4145   # px per inch across = (y - Y_H) / H_ACROSS  (24 in tile width)
Y_JOINT = 261.0     # horizontal joint row
F_FWD = 160000.0    # forward scale: Z = F/u - F/u_joint, chosen by texture isotropy


def plane_remove(img, mask=None):
    """Remove a least-squares linear plane per channel (keeps the mean)."""
    h, w = img.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    A = np.stack([np.ones(h * w), (xx.ravel() / w) - .5, (yy.ravel() / h) - .5], 1)
    m = np.ones(h * w, bool) if mask is None else mask.ravel()
    out = img.copy()
    for c in range(3):
        coef, *_ = np.linalg.lstsq(A[m], img[..., c].ravel()[m], rcond=None)
        out[..., c] = img[..., c] - (A[:, 1:] @ coef[1:]).reshape(h, w)
    return out


def destripe(a):
    """Notch filter for the horizontal line artifact at 0.2651 cycles/px (vertical)."""
    h, w = a.shape[:2]
    fy = np.fft.fftfreq(h)[:, None]
    fx = np.fft.fftfreq(w)[None, :]
    f0 = 0.2651
    notch = np.ones((h, w))
    for s in (1, -1):
        notch *= 1 - np.exp(-((fy - s * f0) ** 2) / (2 * 0.0035 ** 2) - (fx ** 2) / (2 * 0.02 ** 2))
    out = np.empty_like(a)
    for c in range(3):
        out[..., c] = np.fft.ifft2(np.fft.fft2(a[..., c]) * notch).real
    return out


def prep_swatch():
    a = np.asarray(Image.open(os.path.join(INP, 'crosscut_swatch.webp')).convert('RGB')).astype(np.float64)
    r0 = a.mean((1, 2)); r0 = np.std(r0 - gaussian_filter(r0, 3))
    a = destripe(a)
    r1 = a.mean((1, 2)); r1 = np.std(r1 - gaussian_filter(r1, 3))
    W, H = round(a.shape[1] * PPI / SWATCH_PPI), round(a.shape[0] * PPI / SWATCH_PPI)
    up = np.stack([np.asarray(Image.fromarray(a[..., c].astype(np.float32), 'F').resize((W, H), Image.LANCZOS))
                   for c in range(3)], -1).astype(np.float64)
    up = plane_remove(up)
    return up, {'native_px': [a.shape[1], a.shape[0]], 'native_ppi': SWATCH_PPI,
                'resampled_px': [W, H], 'scale_factor': PPI / SWATCH_PPI,
                'row_oscillation_std_before_after_destripe': [round(float(r0), 3), round(float(r1), 3)]}


def rectify(a, x0, x1, z0, z1):
    """Ground-plane rectification at 64 px/in. X across (in, 0 at vanishing column),
    Z forward in inches from the horizontal joint (positive = farther away)."""
    Z = np.arange(z1, z0, -1.0 / PPI)
    X = np.arange(x0, x1, 1.0 / PPI)
    u_j = Y_JOINT - Y_H
    u = F_FWD / (Z + F_FWD / u_j)
    y = u + Y_H
    xx = X_V + X[None, :] * (u[:, None] / H_ACROSS)
    yy = np.repeat(y[:, None], len(X), 1)
    return np.stack([map_coordinates(a[..., c], [yy, xx], order=3, mode='nearest') for c in range(3)], -1)


def joint_X(name, y):
    xa, xb = JOINTS[name]
    x = xa + (xb - xa) * y / 348.0
    return (x - X_V) * H_ACROSS / (y - Y_H)


def prep_floor(sw_mean, sw_std):
    a = np.asarray(Image.open(os.path.join(INP, 'crosscut_floor_angled.jpg')).convert('RGB')).astype(np.float64)
    u_j = Y_JOINT - Y_H
    z_top = F_FWD / (14 - Y_H) - F_FWD / u_j        # skip glare/blur band above y=14
    z_bot = F_FWD / (346 - Y_H) - F_FWD / u_j
    tiles, meta = [], []
    names = ['A', 'B', 'C', 'D']
    margin = 0.6   # inches kept clear of each joint
    for i in range(3):
        xl = joint_X(names[i], Y_JOINT) + margin
        xr = joint_X(names[i + 1], Y_JOINT) - margin
        for (z0, z1, tag) in [(margin, z_top, 'far'), (z_bot, -margin, 'near')]:
            t = rectify(a, xl, xr, z0, z1)
            t = plane_remove(t)
            # per-channel tone match (white balance + contrast) to the swatch statistics
            m, s = t.reshape(-1, 3).mean(0), t.reshape(-1, 3).std(0)
            gain = np.clip(sw_std / s, 0.6, 1.6)
            t = (t - m) * gain + sw_mean
            tiles.append(t)
            meta.append({'tile_column': names[i] + names[i + 1], 'part': tag,
                         'X_in': [round(xl, 2), round(xr, 2)], 'Z_in': [round(z0, 2), round(z1, 2)],
                         'px': [t.shape[1], t.shape[0]], 'orig_mean_rgb': m.round(1).tolist(),
                         'gain_rgb': gain.round(3).tolist()})
    return tiles, meta


def geometry_checks():
    """Validation: joint widths at several rows (should all be 24 in)."""
    out = {}
    for y in [20, 100, 180, 261, 340]:
        xs = [joint_X(n, y) for n in 'ABCDE' if not (n == 'E' and y > 130)]
        out[str(y)] = np.round(np.diff(xs), 3).tolist()
    return out


if __name__ == '__main__':
    sw, sw_meta = prep_swatch()
    sw_mean, sw_std = sw.reshape(-1, 3).mean(0), sw.reshape(-1, 3).std(0)
    np.save(os.path.join(WORK, 'src_swatch.npy'), sw.astype(np.float32))
    tiles, fl_meta = prep_floor(sw_mean, sw_std)
    for k, t in enumerate(tiles):
        np.save(os.path.join(WORK, f'src_floor{k}.npy'), t.astype(np.float32))
    meta = {'swatch': sw_meta, 'swatch_mean_rgb': sw_mean.round(2).tolist(), 'swatch_std_rgb': sw_std.round(2).tolist(),
            'floor_tiles': fl_meta, 'floor_model': {'Y_H': Y_H, 'X_V': X_V, 'H_ACROSS': H_ACROSS,
                                                    'Y_JOINT': Y_JOINT, 'F_FWD': F_FWD},
            'floor_tile_widths_in_by_row': geometry_checks()}
    json.dump(meta, open(os.path.join(WORK, 'sources_meta.json'), 'w'), indent=1)
    print(json.dumps(meta, indent=1))
