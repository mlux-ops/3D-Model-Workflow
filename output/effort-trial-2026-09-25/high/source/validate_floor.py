"""Validate the floor-photo perspective correction and use it to cross-check the swatch scale.

1. Rectify the full floor strip (both sides of the horizontal joint, all columns) at 16 px/in.
2. Re-detect every vertical joint in bands of the rectified image: straight, vertical,
   24 in apart => the homography is right in the across direction.
3. Forward scale F: spectral isotropy of the stone (cross-cut has no direction).
4. Feature-scale cross-check: autocorrelation half-width of the rectified floor stone vs the
   swatch resampled with the brief's 41.67 px/in assumption.
Writes _work/floor_validation.json and _work/floor_rectified_check.jpg.
"""
import json, os
import numpy as np
from PIL import Image
from scipy.ndimage import map_coordinates, gaussian_filter
import prep_sources as ps

ppi = 16
a = np.asarray(Image.open(os.path.join(ps.INP, 'crosscut_floor_angled.jpg')).convert('RGB')).astype(np.float64)
g = a.mean(2)
u_j = ps.Y_JOINT - ps.Y_H


def rect_gray(F, x0, x1, z0, z1, img=g):
    Z = np.arange(z1, z0, -1.0 / ppi); X = np.arange(x0, x1, 1.0 / ppi)
    u = F / (Z + F / u_j); y = u + ps.Y_H
    xx = ps.X_V + X[None, :] * (u[:, None] / ps.H_ACROSS)
    yy = np.repeat(y[:, None], len(X), 1)
    return map_coordinates(img, [yy, xx], order=1, mode='constant', cval=np.nan), Z, X


F = ps.F_FWD
z_top = F / (14 - ps.Y_H) - F / u_j
z_bot = F / (346 - ps.Y_H) - F / u_j
r, Z, X = rect_gray(F, -60, 30, z_bot, z_top)
# joint re-detection per 4-in band
hp = r - gaussian_filter(np.nan_to_num(r, nan=np.nanmean(r)), 3)
bands = []
for zb in np.arange(z_bot + 1, z_top - 4, 4.0):
    rows = (Z <= zb + 4) & (Z > zb)
    prof = np.nanmean(hp[rows], 0)
    found = []
    for xj in [-49.78, -25.82, -1.76, 22.2]:
        win = (X > xj - 1.5) & (X < xj + 1.5)
        if np.isnan(prof[win]).any():
            continue
        found.append(round(float(X[win][np.argmin(prof[win])]), 3))
    bands.append({'Z_in': round(float(zb), 1), 'joint_X_in': found})
jx = {}
for b in bands:
    for k, v in enumerate(b['joint_X_in']):
        jx.setdefault(k, []).append(v)
straight = {f'joint{k}': {'mean_X': round(float(np.mean(v)), 3), 'std_X_in': round(float(np.std(v)), 3),
                          'max_dev_in': round(float(np.max(np.abs(np.array(v) - np.mean(v)))), 3), 'n_bands': len(v)}
            for k, v in jx.items()}
means = [straight[k]['mean_X'] for k in sorted(straight)]
spacings = np.round(np.diff(means), 3).tolist()


def aniso(img, lo=1 / 10, hi=1 / 1.5):
    img = img - img.mean()
    w = np.hanning(img.shape[0])[:, None] * np.hanning(img.shape[1])[None, :]
    P = np.abs(np.fft.fft2(img * w)) ** 2
    fy = np.fft.fftfreq(img.shape[0], 1 / ppi)[:, None]; fx = np.fft.fftfreq(img.shape[1], 1 / ppi)[None, :]
    m = (np.hypot(fx, fy) > lo) & (np.hypot(fx, fy) < hi)
    return float((P * fx ** 2)[m].sum() / (P * fy ** 2)[m].sum())


def acf_half(img):
    img = gaussian_filter(img, 0.5 * ppi); img = img - gaussian_filter(img, 4 * ppi); img = img - img.mean()
    f = np.fft.fft2(img, s=(img.shape[0] * 2, img.shape[1] * 2)); ac = np.fft.ifft2(np.abs(f) ** 2).real; ac /= ac[0, 0]
    return float(np.argmax(ac[0] < 0.5) / ppi), float(np.argmax(ac[:, 0] < 0.5) / ppi)


cols = [(-49.78, -25.82), (-25.82, -1.76), (-1.76, 22.2)]
iso = {}
for Ft in [100000, 120000, 140000, 160000, 180000, 200000]:
    zt = Ft / (14 - ps.Y_H) - Ft / u_j - 1
    iso[str(Ft)] = round(float(np.mean([aniso(rect_gray(Ft, x0 + 1, x1 - 1, 1.5, zt)[0]) for x0, x1 in cols])), 3)
fl_acf = np.mean([acf_half(rect_gray(F, x0 + 1, x1 - 1, 1.5, z_top - 1)[0]) for x0, x1 in cols], 0)
sw = np.asarray(Image.open(os.path.join(ps.INP, 'crosscut_swatch.webp')).convert('L')).astype(np.float64)
swr = np.asarray(Image.fromarray(sw.astype(np.float32), 'F').resize((round(2000 / ps.SWATCH_PPI * ppi), round(875 / ps.SWATCH_PPI * ppi)), Image.LANCZOS), np.float64)
sw_acf = acf_half(swr)
res = {'method': 'floor-plane homography from fitted joints: vanishing point of 5 vertical joints, horizon from '
                 'linear joint spacing, across scale from the 24 in tile width, forward scale F from stone isotropy',
       'joint_straightness_after_rectification': straight, 'joint_spacing_in': spacings,
       'depth_visible_above_joint_in': round(float(z_top), 1), 'depth_visible_below_joint_in': round(float(-z_bot), 1),
       'isotropy_Ex_over_Ey_vs_F': iso, 'F_chosen': F,
       'native_resolution_of_rectified_floor_px_per_in': {
           'across': [round((14 - ps.Y_H) / ps.H_ACROSS, 1), round((346 - ps.Y_H) / ps.H_ACROSS, 1)],
           'forward': [round((14 - ps.Y_H) ** 2 / F, 1), round((346 - ps.Y_H) ** 2 / F, 1)]},
       'feature_scale_check_acf_half_width_in': {'floor_rectified_XZ': np.round(fl_acf, 3).tolist(),
                                                 'swatch_at_41.67ppi_XY': np.round(sw_acf, 3).tolist()}}
json.dump(res, open(os.path.join(ps.WORK, 'floor_validation.json'), 'w'), indent=1)
rc, _, _ = rect_gray(F, -60, 30, z_bot, z_top, img=a[..., 0])
vis = np.stack([rect_gray(F, -60, 30, z_bot, z_top, img=a[..., c])[0] for c in range(3)], -1)
Image.fromarray(np.clip(np.nan_to_num(vis, nan=0), 0, 255).astype(np.uint8)).save(os.path.join(ps.WORK, 'floor_rectified_check.jpg'), quality=90)
print(json.dumps(res, indent=1))
