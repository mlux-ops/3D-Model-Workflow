"""Build Color.png, Bump16.png, face_ids.png from the layout and per-face generators. Re-running reproduces the maps."""
import json
import sys
import time
from facegen import *
import facegen
import layout

SEED = 20260929
A_CORE = 320.0                       # apothem of the tile face: 10.000 in / 2 at 64 px/in
A_MOD = 324.0                        # module apothem (10.125 in / 2)
PITCH_X = W / 8.0                    # 561.125 px column pitch (8 columns wrap in 4489 px)
PITCH_Y = 648.0                      # module across flats, 10.125 in
XQ = (1.5 * PITCH_Y / np.sqrt(3.0)) / PITCH_X     # stretch x so the lattice is exactly regular
R_PX = W / 12.0
JOINT_RGB = np.array([208.0, 200.0, 186.0])       # p10 of the joint line centre measured in the render
H_LO, H_HI = -JOINT_DEPTH_MM, 0.8                 # 16-bit height range (mm)


def centre(i, j):
    cx = R_PX * (1 + 1.5 * i)
    cy = 324.0 + 648.0 * j + (324.0 if i % 2 else 0.0)
    return cx, cy


def main():
    faces = json.load(open(RUN + "/work/layout.json"))
    facegen.reset_usage()
    col = np.zeros((H, W, 3), np.float32)
    hgt = np.zeros((H, W), np.float32)
    best = np.full((H, W), -1e9, np.float32)
    ids = np.zeros((H, W), np.uint16)
    meta = []
    t0 = time.time()
    for f in faces:
        i, j, idx = f["col"], f["row"], f["index"]
        rng = np.random.default_rng([SEED, idx])
        if f["type"] == "matte":
            c, h, prov = gen_matte(rng)
            rot, mir = 0, False
        elif f["type"] == "raw":
            c, h, prov = gen_raw(rng)
            rot, mir = 0, False
        else:
            c, h, prov = gen_chis(rng, float(f["groove_dir"]))
            rot, mir = int(f["groove_dir"]), False
        cx, cy = centre(i, j)
        ic, jc = int(round(cx)), int(round(cy))
        ix = (ic - WT // 2 + np.arange(WT)) % W
        iy = (jc - HT // 2 + np.arange(HT)) % H
        dx = (ic - WT // 2 + np.arange(WT) + 0.5) - cx
        dy = (jc - HT // 2 + np.arange(HT) + 0.5) - cy
        DX, DY = np.meshgrid(dx * XQ, dy)
        s = (A_CORE - np.maximum(np.abs(DY), 0.8660254 * np.abs(DX) + 0.5 * np.abs(DY))).astype(np.float32)
        sub = best[np.ix_(iy, ix)]
        upd = s > sub
        for arr, val in ((col, c), (hgt, h)):
            cur = arr[np.ix_(iy, ix)]
            cur = np.where(upd[..., None], val, cur) if arr.ndim == 3 else np.where(upd, val, cur)
            arr[np.ix_(iy, ix)] = cur
        cur_i = ids[np.ix_(iy, ix)]
        ids[np.ix_(iy, ix)] = np.where(upd, idx, cur_i).astype(np.uint16)
        best[np.ix_(iy, ix)] = np.where(upd, s, sub)
        meta.append(dict(index=idx, col=i, row=j, type=f["type"], rotation_deg=f["groove_dir"], mirrored=False,
                         source_patches=prov, cx=cx, cy=cy))
        print("face %2d %-8s done  (%.0fs)" % (idx, f["type"], time.time() - t0)); sys.stdout.flush()

    # joints
    s = best
    x = np.clip((1.5 - s) / 3.0, 0, 1)
    fh = x * x * (3 - 2 * x)
    xc = np.clip((0.75 - s) / 1.5, 0, 1)
    fc = xc * xc * (3 - 2 * xc)
    hgt = hgt * (1 - fh) + (-JOINT_DEPTH_MM) * fh
    col = col * (1 - fc[..., None]) + JOINT_RGB[None, None, :] * fc[..., None]
    ids = np.where(s > 0, ids, 0).astype(np.uint16)
    np.clip(col, 0, 255, out=col)
    save_img(Image.fromarray(np.rint(col).astype(np.uint8), "RGB"), RUN + "/textures/Color.png", compress_level=3)
    v16 = np.rint((hgt - H_LO) / (H_HI - H_LO) * 65535.0)
    v16 = np.clip(v16, 0, 65535).astype(np.uint16)
    save_img(Image.fromarray(v16), RUN + "/textures/Bump16.png", compress_level=3)
    save_img(Image.fromarray(ids), RUN + "/textures/face_ids.png", compress_level=3)
    json.dump(meta, open(guard(RUN + "/work/build_meta.json"), "w"), indent=1, default=str)
    np.save(guard(RUN + "/work/height_mm.npy"), hgt.astype(np.float32))
    print("wrote maps in %.0fs" % (time.time() - t0))


if __name__ == "__main__":
    main()
