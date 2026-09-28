"""Build the two independent Soreno Ivory source faces (A, B) at the best available resolution.

Evidence (a05_dupes.py, _work/dupes.json): every tile face in every candidate swatch is a crop,
180-degree rotation or mirror of one of two printed faces:
  A = top-right tile of MSI soreno-ivory-porcelain-24x48.jpg (805 px swatch, ~11.25 px/in)
  B = middle tile of the same image
The MSI 24x24 swatch (soreno-ivory-porcelain.jpg) shows A's left half, A's right half and B's right
half (twice) at ~16.8 px/in. This script registers those hi-res crops onto 1.5x-upsampled A and B,
colour-matches them (per-channel gain/offset on low-passed overlap), feathers them in, and writes
  _work/master_A.npy, _work/master_B.npy  (float64 sRGB 0..255, 16.84 px/in scale)
  _work/master_hires_mask_A.npy / _B.npy  (1 = native hi-res pixel, 0 = upsampled 24x48 pixel)
  _work/master.json                        (scale, offsets, NCC, colour fits, gradient stats)
  _work/_VIEW_master_A.jpg / _B.jpg        (<= 800 px previews)
"""
import json

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, zoom, distance_transform_edt
from scipy.signal import fftconvolve

from guard import out_path, ref

SRC48 = "msi_porcelainceramic__soreno-ivory-porcelain-24x48.jpg"
SRC24 = "msi_porcelainceramic__soreno-ivory-porcelain.jpg"
# face boxes in SRC48 (x0, y0, x1, y1), joint centres from _work/grid.json, inset 5 px
INSET = 5
QUADS = {  # 24x24 image quadrant crops (y0, y1, x0, x1), inset 8 px from its joints/edges
    "A_left": (8, 394, 8, 397),
    "A_right": (408, 797, 411, 797),
    "B_right": (8, 394, 411, 797),
}
QUAD_FACE = {"A_left": "A", "A_right": "A", "B_right": "B"}
FEATHER = 10


def bp(im):
    return gaussian_filter(im, 1.5) - gaussian_filter(im, 8)


def ncc_map(img, t):
    t = t - t.mean()
    tn = np.sqrt((t * t).sum())
    num = fftconvolve(img, t[::-1, ::-1], "valid")
    o = np.ones_like(t)
    s1 = fftconvolve(img, o, "valid")
    s2 = fftconvolve(img * img, o, "valid")
    return num / (np.sqrt(np.maximum(s2 - s1 * s1 / t.size, 1e-9)) * tn)


def lum(a):
    return a @ np.array([0.2126, 0.7152, 0.0722])


def load_faces():
    grid = json.load(open(out_path("_work/grid.json")))
    g = [x for x in grid if x["image"] == SRC48][0]
    rgb = np.asarray(Image.open(ref(SRC48)).convert("RGB")).astype(np.float64)
    boxes = {}
    b0 = g["bands"][0]
    b1 = g["bands"][1]
    # A: top band, right of the joint; B: middle band between its two joints
    boxes["A"] = (b0["cols"][0], 0.0, float(rgb.shape[1]), b0["band"][1])
    boxes["B"] = (b1["cols"][0], b1["band"][0], b1["cols"][1], b1["band"][1])
    faces = {}
    for k, (x0, y0, x1, y1) in boxes.items():
        ya = 0 if y0 < 1 else int(np.ceil(y0)) + INSET
        yb = int(np.floor(y1)) - INSET
        xa = int(np.ceil(x0)) + INSET
        xb = rgb.shape[1] if x1 >= rgb.shape[1] - 1 else int(np.floor(x1)) - INSET
        faces[k] = rgb[ya:yb, xa:xb]
    return faces, boxes, g["pitch_px"]


def main():
    faces, boxes, pitch48 = load_faces()
    im24 = np.asarray(Image.open(ref(SRC24)).convert("RGB")).astype(np.float64)
    ppi48 = pitch48[0] / (47.2441 + 0.125)
    ppi24 = 400.0 / (23.622 + 0.125)
    rep = {"ppi_24x48_swatch": ppi48, "ppi_24x24_swatch": ppi24, "faces": {}, "quads": {}}
    # refine the scale between the swatches by NCC over candidate factors
    f0 = ppi24 / ppi48
    best = (-1, None)
    qA = im24[slice(*QUADS["A_left"][:2]), slice(*QUADS["A_left"][2:])]
    tpl = bp(lum(qA))
    tpl = tpl[60:-60, 60:-60]
    for f in np.linspace(f0 * 0.97, f0 * 1.03, 25):
        up = bp(lum(zoom(faces["A"], (f, f, 1), order=3)))
        if up.shape[0] < tpl.shape[0] or up.shape[1] < tpl.shape[1]:
            continue
        m = ncc_map(up, tpl).max()
        if m > best[0]:
            best = (m, f)
    f = best[1]
    rep["scale_24_over_48"] = f
    rep["scale_ncc"] = best[0]
    masters, masks = {}, {}
    for k in ("A", "B"):
        up = zoom(faces[k], (f, f, 1), order=3)
        masters[k] = up.copy()
        masks[k] = np.zeros(up.shape[:2])
        L = lum(up)
        # lighting / gradient stats on the native face (planar + quadratic fit of low-passed luminance)
        Ln = gaussian_filter(lum(faces[k]), 12)
        yy, xx = np.mgrid[0:Ln.shape[0], 0:Ln.shape[1]]
        xn, yn = xx / Ln.shape[1] - 0.5, yy / Ln.shape[0] - 0.5
        Aq = np.stack([np.ones_like(xn), xn, yn, xn * xn, yn * yn, xn * yn], -1).reshape(-1, 6)
        c, *_ = np.linalg.lstsq(Aq, Ln.ravel(), rcond=None)
        fit = (Aq @ c).reshape(Ln.shape)
        rep["faces"][k] = {"native_px": [int(faces[k].shape[1]), int(faces[k].shape[0])],
                           "box_in_24x48_swatch": boxes[k],
                           "mean_srgb": [float(v) for v in faces[k].reshape(-1, 3).mean(0)],
                           "lum_mean": float(lum(faces[k]).mean()),
                           "lowpass_fit_peak_to_trough_rel": float(fit.max() / fit.min() - 1),
                           "planar_x_rel": float(c[1] / c[0]), "planar_y_rel": float(c[2] / c[0]),
                           "hi_px": [int(up.shape[1]), int(up.shape[0])]}
    for q, (y0, y1, x0, x1) in QUADS.items():
        k = QUAD_FACE[q]
        crop = im24[y0:y1, x0:x1]
        up = masters[k]
        t = bp(lum(crop))
        m = ncc_map(bp(lum(faces[k] if False else zoom(faces[k], (f, f, 1), order=3))), t[20:-20, 20:-20])
        iy, ix = np.unravel_index(int(m.argmax()), m.shape)
        oy, ox = iy - 20, ix - 20                      # crop origin in the upsampled face
        # overlap region
        ya, yb = max(0, oy), min(up.shape[0], oy + crop.shape[0])
        xa, xb = max(0, ox), min(up.shape[1], ox + crop.shape[1])
        c_sub = crop[ya - oy:yb - oy, xa - ox:xb - ox]
        u_sub = zoom(faces[k], (f, f, 1), order=3)[ya:yb, xa:xb]
        fits = []
        matched = np.empty_like(c_sub)
        for ch in range(3):
            a = gaussian_filter(c_sub[..., ch], 3).ravel()
            b = gaussian_filter(u_sub[..., ch], 3).ravel()
            G = np.stack([a, np.ones_like(a)], 1)
            (g_, o_), *_ = np.linalg.lstsq(G, b, rcond=None)
            fits.append([float(g_), float(o_)])
            matched[..., ch] = c_sub[..., ch] * g_ + o_
        # feathered paste: weight rises from 0 at the crop border to 1 FEATHER px inside
        w = np.ones(c_sub.shape[:2])
        w[0, :] = w[-1, :] = w[:, 0] = w[:, -1] = 0
        w = np.clip(distance_transform_edt(w) / FEATHER, 0, 1)
        masters[k][ya:yb, xa:xb] = w[..., None] * matched + (1 - w[..., None]) * masters[k][ya:yb, xa:xb]
        masks[k][ya:yb, xa:xb] = np.maximum(masks[k][ya:yb, xa:xb], w)
        resid = float(np.abs(gaussian_filter(lum(matched), 3) - gaussian_filter(lum(u_sub), 3)).mean())
        rep["quads"][q] = {"face": k, "ncc": float(m.max()), "origin_in_upsampled_face": [int(ox), int(oy)],
                           "crop_px": [int(crop.shape[1]), int(crop.shape[0])], "colour_fit_gain_offset": fits,
                           "lowpass_abs_resid_after_fit": resid}
    for k in ("A", "B"):
        np.save(out_path("_work/master_%s.npy" % k), masters[k])
        np.save(out_path("_work/master_hires_mask_%s.npy" % k), masks[k])
        rep["faces"][k]["hires_fraction"] = float((masks[k] > 0.5).mean())
        v = Image.fromarray(np.clip(np.round(masters[k]), 0, 255).astype(np.uint8))
        v.thumbnail((800, 800), Image.LANCZOS)
        v.save(out_path("_work/_VIEW_master_%s.jpg" % k), quality=92)
    rep["master_ppi"] = ppi48 * f
    json.dump(rep, open(out_path("_work/master.json"), "w"), indent=1)
    print(json.dumps(rep, indent=1))


if __name__ == "__main__":
    main()
