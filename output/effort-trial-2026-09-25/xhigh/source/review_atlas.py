"""Measure the gates on textures/Color.png and write the review images + report.json."""
import json
import os
import struct
import zlib

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.signal import fftconvolve

from floor_geom import CALIB, RUN

TEX = os.path.join(RUN, "textures")
PNG = os.path.join(TEX, "Color.png")
PROV = os.path.join(TEX, "_provenance.json")
REPORT = os.path.join(TEX, "report.json")
EXPECT_W, EXPECT_H = 9228, 4620
CELL_W, CELL_H, FACE_W, FACE_H, JH = 3076, 1540, 3072, 1536, 2
JOINT = np.array([209, 209, 209])


def font(sz):
    for f in ("C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/arial.ttf"):
        if os.path.exists(f):
            return ImageFont.truetype(f, sz)
    return ImageFont.load_default()


def png_header(path):
    with open(path, "rb") as f:
        sig = f.read(8)
        ln, typ = struct.unpack(">I4s", f.read(8))
        data = f.read(ln)
        w, h, depth, ctype, comp, filt, inter = struct.unpack(">IIBBBBB", data)
        chunks = []
        f.seek(8)
        while True:
            hdr = f.read(8)
            if len(hdr) < 8:
                break
            ln, typ = struct.unpack(">I4s", hdr)
            chunks.append(typ.decode())
            f.seek(ln + 4, 1)
    return {"signature_ok": sig == b"\x89PNG\r\n\x1a\n", "width": w, "height": h, "bit_depth": depth,
            "color_type": ctype, "color_type_name": {2: "RGB", 6: "RGBA", 0: "gray"}.get(ctype, str(ctype)),
            "interlace": inter, "chunks": sorted(set(chunks))}


def ncc(a, b):
    a = a - a.mean()
    b = b - b.mean()
    return float((a * b).sum() / np.sqrt((a * a).sum() * (b * b).sum()))


def block_mean(a, n):
    h, w = a.shape[0] // n * n, a.shape[1] // n * n
    return a[:h, :w].reshape(h // n, n, w // n, n).mean(axis=(1, 3))


def window_sd(img, n):
    """sqrt of the centred sum of squares of every n x n window of img"""
    ones = np.ones((n, n))
    s1 = fftconvolve(img, ones, mode="valid")
    s2 = fftconvolve(img * img, ones, mode="valid")
    return np.sqrt(np.maximum(s2 - s1 * s1 / (n * n), 1e-9))


def local_ncc_max(win, img, sd):
    """max normalized cross-correlation of the square window win over img"""
    t = win - win.mean()
    num = fftconvolve(img, t[::-1, ::-1], mode="valid")
    return float((num / (np.sqrt((t * t).sum()) * sd)).max())


def main():
    rep = {}
    hdr = png_header(PNG)
    im = Image.open(PNG)
    a = np.asarray(im.convert("RGB")).astype(np.int16)
    H, W = a.shape[:2]
    rep["format"] = {**hdr, "pil_mode": im.mode, "icc_profile_embedded": "icc_profile" in im.info,
                     "size_ok": (W, H) == (EXPECT_W, EXPECT_H),
                     "pass": hdr["signature_ok"] and (W, H) == (EXPECT_W, EXPECT_H) and hdr["bit_depth"] == 8
                     and hdr["color_type"] == 2 and im.mode == "RGB"}

    # ---------------- joints ----------------
    jcols = np.zeros(W, bool)
    jrows = np.zeros(H, bool)
    for k in range(4):
        for d in range(-JH, JH):
            x = (k * CELL_W + d) % W
            y = (k * CELL_H + d) % H
            if k < 4:
                jcols[x] = True
            if k < 4:
                jrows[y] = True
    jmask = jcols[None, :] | jrows[:, None]
    jpix = a[jmask]
    joint_exact = bool((jpix == JOINT).all())
    stone = ~jmask
    stone_is_joint = int((a[stone] == JOINT).all(1).sum())

    def runs(v):
        out, n = [], 0
        for x in v:
            if x:
                n += 1
            elif n:
                out.append(n)
                n = 0
        if n:
            out.append(n)
        return out
    # widths measured on a 2 x 2 tiling so the wrap joint is seen whole
    rowmid = a[CELL_H // 2]
    colmid = a[:, CELL_W // 2]
    tiled_row = np.concatenate([rowmid, rowmid])
    tiled_col = np.concatenate([colmid, colmid])
    wr = runs((tiled_row == JOINT).all(1))
    wc = runs((tiled_col == JOINT).all(1))
    rep["joint"] = {"rgb": JOINT.tolist(), "all_joint_pixels_exact": joint_exact,
                    "joint_pixel_count": int(jmask.sum()),
                    "stone_pixels_equal_to_joint_rgb": stone_is_joint,
                    "vertical_joint_widths_px_in_2x_tiling": wr, "horizontal_joint_widths_px_in_2x_tiling": wc,
                    "width_px_expected": 4, "width_in": 4 / 64.0,
                    "pass": joint_exact and all(v == 4 for v in wr[1:-1]) and all(v == 4 for v in wc[1:-1])}

    # ---------------- wrap steps ----------------
    af = a.astype(np.float64)
    lr = float(np.abs(af[:, 0] - af[:, -1]).mean())
    tb = float(np.abs(af[0] - af[-1]).mean())
    # interior stone neighbour steps (column pairs / row pairs fully inside stone)
    sc = [x for x in range(W - 1) if not jcols[x] and not jcols[x + 1]]
    sr = [y for y in range(H - 1) if not jrows[y] and not jrows[y + 1]]
    rows_stone = ~jrows
    cols_stone = ~jcols
    dx = np.abs(np.diff(af, axis=1))[rows_stone][:, sc].mean(axis=(0, 2))
    dy = np.abs(np.diff(af, axis=0))[:, cols_stone][sr].mean(axis=(1, 2))
    # stone-to-stone across a joint: wrap joint vs the interior joints
    wrap_lr_stone = float(np.abs(af[rows_stone][:, JH] - af[rows_stone][:, W - 1 - JH]).mean())
    wrap_tb_stone = float(np.abs(af[JH][cols_stone] - af[H - 1 - JH][cols_stone]).mean())
    int_lr_stone = [float(np.abs(af[rows_stone][:, k * CELL_W - JH - 1] - af[rows_stone][:, k * CELL_W + JH]).mean())
                    for k in (1, 2)]
    int_tb_stone = [float(np.abs(af[k * CELL_H - JH - 1][cols_stone] - af[k * CELL_H + JH][cols_stone]).mean())
                    for k in (1, 2)]
    # joint-edge contrast: wrap vs interior joints
    edge_lr = float(np.abs(af[rows_stone][:, JH] - af[rows_stone][:, JH - 1]).mean())
    edge_int = float(np.abs(af[rows_stone][:, CELL_W + JH] - af[rows_stone][:, CELL_W + JH - 1]).mean())
    rep["wrap"] = {
        "LR_step_col0_vs_colLast_mean_abs_rgb": lr, "TB_step_row0_vs_rowLast_mean_abs_rgb": tb,
        "interior_neighbour_step_x": {"mean": float(dx.mean()), "median": float(np.median(dx)),
                                      "p99": float(np.percentile(dx, 99))},
        "interior_neighbour_step_y": {"mean": float(dy.mean()), "median": float(np.median(dy)),
                                      "p99": float(np.percentile(dy, 99))},
        "LR_ratio_to_interior_median": lr / float(np.median(dx)),
        "TB_ratio_to_interior_median": tb / float(np.median(dy)),
        "note": "Both wrap edges fall on the centre line of a 1/16 in joint (2 px each side), so the edge "
                "columns/rows are joint on both sides of the wrap.",
        "stone_across_wrap_joint_LR": wrap_lr_stone, "stone_across_interior_joints_LR": int_lr_stone,
        "stone_across_wrap_joint_TB": wrap_tb_stone, "stone_across_interior_joints_TB": int_tb_stone,
        "stone_to_joint_edge_step_wrap": edge_lr, "stone_to_joint_edge_step_interior": edge_int,
        "pass": lr <= float(np.median(dx)) and tb <= float(np.median(dy)),
    }

    # ---------------- seam excess inside faces ----------------
    prov = json.load(open(PROV))
    bw, bh = prov["block_px"]
    ox, oy = prov["overlap_px"]
    stepx, stepy = bw - ox, bh - oy
    gray = af.mean(2)
    faces = []
    for f in prov["faces"]:
        x0, y0 = f["stone_origin_px"]
        faces.append(gray[y0:y0 + FACE_H, x0:x0 + FACE_W])
    band_x = np.zeros(FACE_W, bool)
    for c in range(1, 5):
        band_x[c * stepx:c * stepx + ox] = True
    band_y = np.zeros(FACE_H, bool)
    for r in range(1, 3):
        band_y[r * stepy:r * stepy + oy] = True
    gxs = [np.abs(np.diff(fc, axis=1)) for fc in faces]
    gys = [np.abs(np.diff(fc, axis=0)) for fc in faces]
    in_x = np.mean([g[:, band_x[:-1]].mean() for g in gxs])
    out_x = np.mean([g[:, ~band_x[:-1]].mean() for g in gxs])
    in_y = np.mean([g[band_y[:-1]].mean() for g in gys])
    out_y = np.mean([g[~band_y[:-1]].mean() for g in gys])
    # low-frequency step across seam bands (8 px/in means), to catch tone seams
    lf = [block_mean(fc, 8) for fc in faces]
    lfx_in = np.mean([np.abs(np.diff(l, axis=1))[:, band_x[::8][:-1]].mean() for l in lf])
    lfx_out = np.mean([np.abs(np.diff(l, axis=1))[:, ~band_x[::8][:-1]].mean() for l in lf])
    lfy_in = np.mean([np.abs(np.diff(l, axis=0))[band_y[::8][:-1]].mean() for l in lf])
    lfy_out = np.mean([np.abs(np.diff(l, axis=0))[~band_y[::8][:-1]].mean() for l in lf])
    rep["internal_seams"] = {
        "fullres_step_in_seam_bands_vs_elsewhere_x": [float(in_x), float(out_x), float(in_x / out_x)],
        "fullres_step_in_seam_bands_vs_elsewhere_y": [float(in_y), float(out_y), float(in_y / out_y)],
        "8ppi_step_in_seam_bands_vs_elsewhere_x": [float(lfx_in), float(lfx_out), float(lfx_in / lfx_out)],
        "8ppi_step_in_seam_bands_vs_elsewhere_y": [float(lfy_in), float(lfy_out), float(lfy_in / lfy_out)],
        "note": "ratio ~1 means the overlap bands where DP seams run carry no extra step energy"}

    # ---------------- cross-cell similarity ----------------
    flips = {"none": lambda x: x, "flipH": lambda x: x[:, ::-1], "flipV": lambda x: x[::-1],
             "rot180": lambda x: x[::-1, ::-1]}
    cells_full = [gray[(i // 3) * CELL_H:(i // 3 + 1) * CELL_H, (i % 3) * CELL_W:(i % 3 + 1) * CELL_W]
                  for i in range(9)]

    def ncc_table(imgs):
        best, rows = (-2, None), []
        for i in range(9):
            for j in range(i + 1, 9):
                for fn, f in flips.items():
                    v = ncc(imgs[i], f(imgs[j]))
                    rows.append(v)
                    if v > best[0]:
                        best = (v, [i, j, fn])
        return {"max": best[0], "argmax_pair_flip": best[1], "mean_abs": float(np.mean(np.abs(rows)))}
    faces8 = [block_mean(fc, 8) for fc in faces]
    # measurement-only copy with the swatch striation (a fixed horizontal grating every cell carries)
    # projected out, to separate stone-content similarity from the shared grating
    P = prov["swatch"]["stripe_period_px64"]
    yy = np.arange(FACE_H)
    destriped = []
    for fc in faces:
        prof = fc.mean(1) - fc.mean()
        z = (prof * np.exp(-2j * np.pi * yy / P)).sum() * 2 / FACE_H
        destriped.append(fc - np.real(z * np.exp(2j * np.pi * yy / P))[:, None])
    rep["cross_cell_similarity"] = {
        "faces_fullres_gray": ncc_table(faces),
        "cells_with_joints_fullres_gray": ncc_table(cells_full),
        "faces_fullres_gray_striation_removed_for_measurement": ncc_table(destriped),
        "faces_4x_downsampled_gray": ncc_table([block_mean(fc, 4) for fc in faces]),
        "faces_8ppi_gray": ncc_table(faces8),
        "note": "Pearson correlation of cell i against cell j and its flipH/flipV/rot180, all 36 pairs. "
                "The joint frame is identical in every cell, so the with-joints figure has a floor from it.",
    }

    # ---------------- repetition: shared source area and local NCC ----------------
    blocks = prov["blocks"]
    fp = {}   # footprints at 8 px/in in source coordinates
    for b in blocks:
        if b["source"] == "swatch":
            x, y, w, h = b["src_rect_64ppi_xywh"]
            key = ("swatch", x // 8, y // 8, w // 8, h // 8)
        else:
            r = b["src_plane_rect_in"]
            key = ("floor", int(round((r["X0"] + 72) * 8)), int(round((36.5 - r["Z1"]) * 8)),
                   int(round((r["X1"] - r["X0"]) * 8)), int(round((r["Z1"] - r["Z0"]) * 8)))
        fp.setdefault(b["face"], []).append(key)
    shape = {"swatch": (168, 384), "floor": (369, 1008)}

    def cover(face):
        m = {k: np.zeros(v, bool) for k, v in shape.items()}
        for s, x, y, w, h in fp[face]:
            m[s][y:y + h, x:x + w] = True
        return m
    covers = [cover(f) for f in range(9)]
    shared = np.zeros((9, 9))
    for i in range(9):
        for j in range(9):
            if i != j:
                shared[i, j] = sum((covers[i][s] & covers[j][s]).sum() for s in shape) / 64.0
    total_cov = {s: np.sum([c[s] for c in covers], axis=0) for s in shape}
    uses = np.concatenate([total_cov[s][total_cov[s] > 0].ravel() for s in shape])
    # local NCC: 6 in windows of each face against every other face in 8 orientations (8 px/in)
    win = 48
    orients = [lambda x: x, lambda x: x[:, ::-1], lambda x: x[::-1], lambda x: x[::-1, ::-1],
               lambda x: x.T, lambda x: x.T[:, ::-1], lambda x: x.T[::-1], lambda x: x.T[::-1, ::-1]]
    lmax = np.zeros((9, 9))
    sds = [window_sd(f8, win) for f8 in faces8]
    hits = []
    for i in range(9):
        for yy in range(0, 192 - win + 1, 24):
            for xx in range(0, 384 - win + 1, 24):
                w_ = faces8[i][yy:yy + win, xx:xx + win]
                for j in range(9):
                    if j == i:
                        continue
                    v = max(local_ncc_max(np.ascontiguousarray(o(w_)), faces8[j], sds[j]) for o in orients)
                    lmax[i, j] = max(lmax[i, j], v)
                    hits.append(v)
    hits = np.array(hits)
    rep["repetition"] = {
        "source_reuse_per_used_source_pixel": {"mean": float(uses.mean()), "max": int(uses.max())},
        "source_area_used_once_fraction": float((uses == 1).mean()),
        "max_shared_source_area_between_two_faces_in2": float(shared.max()),
        "max_shared_fraction_of_face": float(shared.max() / 1152.0),
        "shared_source_area_matrix_in2": np.round(shared, 1).tolist(),
        "local_6in_window_ncc_8ppi": {"max": float(hits.max()), "p99": float(np.percentile(hits, 99)),
                                      "median": float(np.median(hits)),
                                      "fraction_over_0.9": float((hits > 0.9).mean()),
                                      "fraction_over_0.8": float((hits > 0.8).mean()),
                                      "per_pair_max": np.round(lmax, 3).tolist()},
        "note": "Blocks reuse source areas (the pool holds ~4.6 faces of real stone for 9 faces); the "
                "local NCC shows where a 6 in window of one face reappears, in any of 8 orientations, "
                "in another face.",
    }

    # ---------------- per-cell provenance summary ----------------
    cells = []
    for f in prov["faces"]:
        bl = [b for b in blocks if b["face"] == f["face"]]
        cells.append({"cell": f["face"], "atlas_row": f["atlas_row"], "atlas_col": f["atlas_col"],
                      "stone_origin_px": f["stone_origin_px"], "swatch_blocks": f["swatch_blocks"],
                      "floor_blocks": f["floor_blocks"],
                      "blocks": [{k: b[k] for k in b if k not in ("face",)} for b in bl]})
    rep["cells"] = cells
    rep["build"] = {k: prov[k] for k in prov if k not in ("blocks", "faces")}
    rep["floor_calibration"] = {k: v for k, v in json.load(open(CALIB)).items() if k != "measurements"}
    fv = os.path.join(TEX, "_floor_validation.json")
    rep["perspective_validation"] = json.load(open(fv)) if os.path.exists(fv) else "run validate_floor.py"
    cs = rep["cross_cell_similarity"]
    rep["gates"] = {
        "1_photographic_only": "every stone pixel is resampled/flipped/rotated photo content or a feathered "
                               "blend of photo content; no synthetic noise or pattern generators are used "
                               "(see README method)",
        "2_perspective": {"pass": bool(isinstance(rep["perspective_validation"], dict)
                                       and rep["perspective_validation"]["pass"]),
                          "joint_spacing_error_in": rep["perspective_validation"].get(
                              "rectified_joint_spacing_error_in") if isinstance(rep["perspective_validation"], dict)
                          else None},
        "3_seamless": {"pass": rep["wrap"]["pass"], "LR_step": rep["wrap"]["LR_step_col0_vs_colLast_mean_abs_rgb"],
                       "TB_step": rep["wrap"]["TB_step_row0_vs_rowLast_mean_abs_rgb"],
                       "interior_median_step_x": rep["wrap"]["interior_neighbour_step_x"]["median"],
                       "interior_median_step_y": rep["wrap"]["interior_neighbour_step_y"]["median"],
                       "internal_seam_band_ratio_x": rep["internal_seams"]["fullres_step_in_seam_bands_vs_elsewhere_x"][2],
                       "internal_seam_band_ratio_y": rep["internal_seams"]["fullres_step_in_seam_bands_vs_elsewhere_y"][2]},
        "4_non_repeating": {"max_cell_ncc_fullres": cs["faces_fullres_gray"]["max"],
                            "max_cell_ncc_with_joints": cs["cells_with_joints_fullres_gray"]["max"],
                            "max_cell_ncc_8ppi": cs["faces_8ppi_gray"]["max"],
                            "max_local_6in_ncc": rep["repetition"]["local_6in_window_ncc_8ppi"]["max"],
                            "mean_source_reuse": rep["repetition"]["source_reuse_per_used_source_pixel"]["mean"],
                            "visual_review": "see README"},
        "5_scale": {"atlas_ppi": 64, "swatch_resample": 64 / (2000 / 48.0),
                    "floor_resample": "single-step plane resampling at 64 px/in from the photo"},
        "6_format": {"pass": rep["format"]["pass"] and rep["joint"]["pass"]},
    }
    with open(REPORT, "w") as f:
        json.dump(rep, f, indent=1)

    # ---------------- review images ----------------
    img = Image.open(PNG).convert("RGB")
    img.resize((W // 3, H // 3), Image.LANCZOS).save(os.path.join(TEX, "_PREVIEW_atlas_full.jpg"), quality=92)
    tile = Image.new("RGB", (2 * W, 2 * H))
    for dy in (0, H):
        for dx in (0, W):
            tile.paste(img, (dx, dy))
    tile.resize((2 * W // 6, 2 * H // 6), Image.LANCZOS).save(os.path.join(TEX, "_PREVIEW_wrap_2x2.jpg"), quality=92)
    # four-way wrap corner: 1:1 context and 4x magnified centre
    ctx = tile.crop((W - 384, H - 384, W + 384, H + 384))
    mag = tile.crop((W - 48, H - 48, W + 48, H + 48)).resize((768, 768), Image.NEAREST)
    board = Image.new("RGB", (768 * 2 + 30, 768 + 70), (255, 255, 255))
    board.paste(ctx, (0, 70))
    board.paste(mag, (798, 70))
    d = ImageDraw.Draw(board)
    d.text((6, 8), "Four-way wrap corner of a 2x2 repeat. Left: 1:1 at 64 px/in (12 x 12 in).", fill=(0, 0, 0),
           font=font(22))
    d.text((6, 38), "Right: centre 1.5 x 1.5 in magnified 8x (nearest). Joint 4 px = 1/16 in, RGB 209.",
           fill=(0, 0, 0), font=font(22))
    board.save(os.path.join(TEX, "_REVIEW_wrap_seam.jpg"), quality=95)
    # cell grid
    cw, ch, gap, lab = 1024, 512, 28, 44
    grid = Image.new("RGB", (3 * cw + 4 * gap, 3 * (ch + lab) + 4 * gap), (40, 40, 40))
    d = ImageDraw.Draw(grid)
    for f in prov["faces"]:
        x0, y0 = f["stone_origin_px"]
        c = img.crop((x0, y0, x0 + FACE_W, y0 + FACE_H)).resize((cw, ch), Image.LANCZOS)
        gx = gap + f["atlas_col"] * (cw + gap)
        gy = gap + f["atlas_row"] * (ch + lab + gap)
        grid.paste(c, (gx, gy + lab))
        d.text((gx + 4, gy + 6), "Cell %d  (row %d, col %d)   swatch blocks %d / floor blocks %d"
               % (f["face"], f["atlas_row"], f["atlas_col"], f["swatch_blocks"], f["floor_blocks"]),
               fill=(255, 255, 255), font=font(24))
    grid.save(os.path.join(TEX, "_REVIEW_cell_grid.jpg"), quality=92)
    summary = {k: rep[k]["pass"] for k in ("format", "joint", "wrap")}
    print(json.dumps(summary))
    print("cross-cell:", json.dumps(rep["cross_cell_similarity"]))
    print("seams:", json.dumps(rep["internal_seams"]))
    print("repetition:", json.dumps({k: v for k, v in rep["repetition"].items()
                                     if k not in ("shared_source_area_matrix_in2",)}, default=str)[:1500])
    print("wrap:", json.dumps({k: v for k, v in rep["wrap"].items() if k != "note"}))


if __name__ == "__main__":
    main()
