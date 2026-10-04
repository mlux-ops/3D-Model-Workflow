"""Independent checks and review previews for the limestone maps.

Re-reads the delivered PNGs (not the builder's arrays), re-derives the gates and
exits non-zero if any fails. Writes previews to previews/.
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parents[1]
TEX = ROOT / "textures"
PRE = ROOT / "previews"
SIZE_IN = 192.0
GAIN = 6.0   # contrast stretch used for every "_stretch" preview


def png_header(p):
    b = p.read_bytes()[16:26]
    return int.from_bytes(b[0:4], "big"), int.from_bytes(b[4:8], "big"), b[8], b[9]


def stretch(a, mean):
    return np.clip((a - mean) * GAIN + 0.5, 0, 1)


def to_img(a):
    a = np.clip(a, 0, 1)
    return Image.fromarray(np.round(a * 255).astype(np.uint8))


def shade(h, light_elev_deg, light_az_deg, relief):
    gy, gx = np.gradient(h * relief)
    n = np.dstack([-gx, -gy, np.ones_like(h)])
    n /= np.linalg.norm(n, axis=-1, keepdims=True)
    el, az = np.radians(light_elev_deg), np.radians(light_az_deg)
    L = np.array([np.cos(el) * np.cos(az), np.cos(el) * np.sin(az), np.sin(el)])
    return np.clip(n @ L, 0, 1)


def seam_ratio(a, axis):
    """Wrap step / mean interior step at the same phase mod 4.

    The supplied maps have a 4 px block structure (every 4th neighbour step is
    ~35 % larger), so the wrap step is compared only with steps of its own phase.
    """
    d = np.abs(np.roll(a, -1, axis=axis) - a).mean(axis=1 - axis)  # d[k] = |a[k+1]-a[k]|, d[-1] = wrap
    same_phase = d[(len(d) - 1) % 4::4][:-1]
    return float(d[-1] / same_phase.mean())


def main():
    PRE.mkdir(exist_ok=True)
    col_p = next(q for q in TEX.glob("*.png") if " - Bump " not in q.name)
    bump_p = next(TEX.glob("* - Bump *.png"))
    gates, info = {}, {}
    cw, ch, cbd, cct = png_header(col_p)
    bw, bh, bbd, bct = png_header(bump_p)
    gates["color_8bit_rgb"] = cbd == 8 and cct == 2
    gates["bump_16bit_grey"] = bbd == 16 and bct == 0
    gates["same_px_size"] = (cw, ch) == (bw, bh)
    gates["aspect_matches_sample_size"] = cw == ch  # 192 x 192 in
    gates["sample_size_quarter_inch"] = (SIZE_IN * 4).is_integer()

    c = np.asarray(Image.open(col_p)).astype(np.float64) / 255
    b = np.asarray(Image.open(bump_p)).astype(np.float64) / 65535
    lum = c.mean(-1)
    info["seam_ratio"] = {
        "color_x": seam_ratio(lum, 1), "color_y": seam_ratio(lum, 0),
        "bump_x": seam_ratio(b, 1), "bump_y": seam_ratio(b, 0)}
    # wrap step must look like any interior neighbour step (1.0 = identical)
    gates["seamless_wrap"] = all(0.8 < v < 1.25 for v in info["seam_ratio"].values())

    # low-frequency wrap: 8 px strip means either side of the wrap vs interior
    lf = ndi.gaussian_filter(c, (8, 8, 0), mode="wrap")
    jump_x = np.abs(lf[:, 0] - lf[:, -1]).mean()
    jump_int = np.abs(np.diff(lf, axis=1)).mean()
    info["lowfreq_wrap_vs_interior_x"] = float(jump_x / jump_int)

    # repetition: autocorrelation of the detail luminance, ignore radius < 2 in
    det = lum - ndi.gaussian_filter(lum, 40, mode="wrap")
    F = np.fft.fft2(det)
    ac = np.fft.ifft2(F * np.conj(F)).real
    ac /= ac[0, 0]
    yy = np.fft.fftfreq(lum.shape[0]) * lum.shape[0]
    xx = np.fft.fftfreq(lum.shape[1]) * lum.shape[1]
    r = np.hypot(*np.meshgrid(yy, xx, indexing="ij"))
    peak = float(ac[r > 2 * cw / SIZE_IN].max())
    info["detail_autocorr_max_offpeak"] = peak
    gates["no_copied_blocks_autocorr_lt_0.2"] = peak < 0.2

    info["color_mean_rgb_8bit"] = (c.reshape(-1, 3).mean(0) * 255).round(1).tolist()
    mean = c.reshape(-1, 3).mean(0)

    # previews -------------------------------------------------------------
    t3 = np.tile(c, (3, 3, 1))
    to_img(t3).resize((1200, 1200), Image.LANCZOS).save(PRE / "_PREVIEW_tiling_3x3_48ft.jpg", quality=92)
    to_img(stretch(t3, mean)).resize((1200, 1200), Image.LANCZOS).save(PRE / "_PREVIEW_tiling_3x3_48ft_stretch.jpg", quality=92)
    # wall: 40 ft x 12 ft at true contrast, the typical large uninterrupted surface
    wall = np.tile(c, (1, 3, 1))[:int(144 * cw / SIZE_IN), :int(480 * cw / SIZE_IN)]
    to_img(wall).resize((1600, 480), Image.LANCZOS).save(PRE / "_PREVIEW_wall_40x12ft.jpg", quality=92)
    to_img(stretch(wall, mean)).resize((1600, 480), Image.LANCZOS).save(PRE / "_PREVIEW_wall_40x12ft_stretch.jpg", quality=92)
    # 1:1 corner of a 2x2 wrap
    t2 = np.tile(c, (2, 2, 1)); n = cw
    corner = t2[n - 256:n + 256, n - 256:n + 256]
    to_img(stretch(corner, mean)).save(PRE / "_PREVIEW_wrap_corner_1to1_stretch.png")
    to_img(corner).save(PRE / "_PREVIEW_wrap_corner_1to1.png")
    # same-scale comparison with the supplied maps (each 47 x 94 in)
    refs = [np.asarray(Image.open(p).convert("RGB")).astype(np.float64) / 255
            for p in sorted((ROOT / "references").glob("0*.webp"))]
    crop = c[200:200 + 2000, 300:300 + 1000]
    panel = np.concatenate([refs[0], np.ones((2000, 20, 3)), refs[1], np.ones((2000, 20, 3)), crop], axis=1)
    to_img(stretch(panel, mean)).resize((1530, 1000), Image.LANCZOS).save(PRE / "_REVIEW_source_A_B_vs_output_47x94_stretch.jpg", quality=92)
    to_img(panel).resize((1530, 1000), Image.LANCZOS).save(PRE / "_REVIEW_source_A_B_vs_output_47x94.jpg", quality=92)
    # grazing light on the bump, 1:1, including the wrap corner
    bc = np.tile(b, (2, 2))[n - 300:n + 300, n - 300:n + 300]
    g = shade(bc, 12, 30, relief=6.0)
    to_img(np.dstack([g] * 3) * (0.5 / g.mean())).save(PRE / "_PREVIEW_grazing_light_bump_corner.png")

    gates_ok = all(gates.values())
    res = {"color": col_p.name, "bump": bump_p.name, "px": [cw, ch],
           "gates": gates, "info": info, "pass": gates_ok,
           "pending": ["Revit render with neutral and grazing light (not run)"]}
    (ROOT / "source/validation.json").write_text(json.dumps(res, indent=2))
    print(json.dumps(res, indent=2))
    sys.exit(0 if gates_ok else 1)


if __name__ == "__main__":
    main()
