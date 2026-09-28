"""Rectify every flat front panel to the front plane at the delivery density (single resampling, bicubic, float64,
linear light). Doors are rotated 90 deg so every crop has horizontal grain. Crops sit INSET inches inside the
fitted reveal lines, clear of the reveal shadow and edge rounding.

Writes _work/crops/<name>.npy (linear RGB float64), _work/crops.json, and a contact sheet _VIEW_crops_raw.jpg."""
import json

import numpy as np

from common import load_rgb, srgb_to_lin, sample_cubic, lin_to_srgb, thumb
from guard import SOURCE_PHOTO, out_path

PPI = 32                      # delivered density, px/in (native front-plane density is 23-26 px/in)
INSET = {"default": 0.22, "apron": (0.22, 0.30, 0.22, 0.20), "bottom_rail": (0.22, 0.20, 0.22, 0.25)}
USE = ["drawer_L1", "drawer_L2", "drawer_L3", "drawer_R1", "drawer_R2", "drawer_R3", "door_L", "door_R", "apron",
       "bottom_rail"]
ROTATE = {"door_L", "door_R"}   # vertical grain in the photo


def main():
    m = json.load(open(out_path("_work/measure.json")))
    Hin = np.array(m["H_img_to_in"])
    Hi = np.linalg.inv(Hin)
    src = srgb_to_lin(load_rgb(SOURCE_PHOTO))
    meta = {}
    for name in USE:
        q = np.array(m["panels"][name]["quad_in"])   # TL, TR, BR, BL in front-plane inches
        ins = INSET.get(name, INSET["default"])
        l, t, r, b = ins if isinstance(ins, tuple) else (ins,) * 4
        u0, u1 = max(q[0, 0], q[3, 0]) + l, min(q[1, 0], q[2, 0]) - r
        v0, v1 = max(q[0, 1], q[1, 1]) + t, min(q[2, 1], q[3, 1]) - b
        W = int(np.floor((u1 - u0) * PPI))
        H = int(np.floor((v1 - v0) * PPI))
        uu = u0 + (np.arange(W) + 0.5) / PPI
        vv = v0 + (np.arange(H) + 0.5) / PPI
        U, V = np.meshgrid(uu, vv)
        P = np.stack([U, V, np.ones_like(U)], -1) @ Hi.T
        xs, ys = P[..., 0] / P[..., 2] - 0.5, P[..., 1] / P[..., 2] - 0.5   # pixel-centre convention
        crop = np.clip(sample_cubic(src, xs, ys), 0, 1)
        if name in ROTATE:
            crop = np.rot90(crop, 1)      # grain now runs along x
        np.save(out_path("_work/crops/%s.npy" % name), crop)
        meta[name] = {"u_in": [round(u0, 3), round(u1, 3)], "v_in": [round(v0, 3), round(v1, 3)],
                      "px": [crop.shape[1], crop.shape[0]],
                      "along_grain_in": round(crop.shape[1] / PPI, 3), "across_grain_in": round(crop.shape[0] / PPI, 3),
                      "rotated_90": name in ROTATE, "native_ppi": m["panels"][name]["px_per_in_h"],
                      "centre_in": [round((u0 + u1) / 2, 3), round((v0 + v1) / 2, 3)]}
        print(name, meta[name]["px"], meta[name]["along_grain_in"], meta[name]["across_grain_in"])
    json.dump({"ppi": PPI, "inset": INSET, "crops": meta}, open(out_path("_work/crops.json"), "w"), indent=1)
    # contact sheet: stack all crops with gaps
    crops = [np.load(out_path("_work/crops/%s.npy" % n)) for n in USE]
    Wmax = max(c.shape[1] for c in crops)
    rows = []
    x = 0
    line, lines = [], []
    for c in crops:
        if x + c.shape[1] > max(Wmax, 1400) and line:
            lines.append(line)
            line, x = [], 0
        line.append(c)
        x += c.shape[1] + 12
    lines.append(line)
    for ln in lines:
        h = max(c.shape[0] for c in ln)
        w = sum(c.shape[1] for c in ln) + 12 * (len(ln) - 1)
        row = np.ones((h, w, 3))
        x = 0
        for c in ln:
            row[:c.shape[0], x:x + c.shape[1]] = c
            x += c.shape[1] + 12
        rows.append(row)
    W = max(r.shape[1] for r in rows)
    sheet = np.ones((sum(r.shape[0] for r in rows) + 12 * len(rows), W, 3))
    y = 0
    for r in rows:
        sheet[y:y + r.shape[0], :r.shape[1]] = r
        y += r.shape[0] + 12
    thumb(lin_to_srgb(sheet), out_path("_PREVIEW_source_crops_raw.jpg"))


if __name__ == "__main__":
    main()
