"""Independent check of the delivered PNGs: decodes them from bytes (PIL reduces RGB16 to 8-bit),
re-derives bit depth, size, sign convention, wrap and relief, and writes native-resolution crops.
Exits non-zero on any failed gate."""
import json
import os
import struct
import sys
import zlib

import numpy as np
from PIL import Image

RUN_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEX = os.path.join(RUN_DIR, "textures")
NAME = "Riad_Turron_Honed_24x24"


def read_png16(path):
    with open(path, "rb") as f:
        data = f.read()
    assert data[:8] == b"\x89PNG\r\n\x1a\n"
    pos, idat, hdr = 8, b"", None
    while pos < len(data):
        ln = struct.unpack(">I", data[pos:pos + 4])[0]
        tag = data[pos + 4:pos + 8]
        body = data[pos + 8:pos + 8 + ln]
        if tag == b"IHDR":
            hdr = struct.unpack(">IIBBBBB", body)
        elif tag == b"IDAT":
            idat += body
        pos += 12 + ln
    w, h, depth, ctype = hdr[:4]
    assert depth == 16, depth
    ch = {0: 1, 2: 3}[ctype]
    raw = zlib.decompress(idat)
    stride = w * ch * 2 + 1
    rows = np.frombuffer(raw, np.uint8).reshape(h, stride)
    assert np.all(rows[:, 0] == 0), "unexpected PNG row filter"
    a = rows[:, 1:].copy().view(">u2").reshape(h, w, ch).astype(np.float64) / 65535.0
    return a[..., 0] if ch == 1 else a, (w, h, depth, ctype)


def main():
    out = {}
    bump, hb = read_png16(os.path.join(TEX, NAME + "_Bump16.png"))
    nrm, hn = read_png16(os.path.join(TEX, NAME + "_Normal16_OpenGL.png"))
    col = Image.open(os.path.join(TEX, NAME + "_Color.png"))
    out["headers"] = {"bump": hb, "normal": hn, "color": [col.size[0], col.size[1], col.mode]}
    g = {}
    g["sizes_match_6144x3072"] = hb[:2] == hn[:2] == (6144, 3072) and col.size == (6144, 3072)
    g["bump_distinct_levels_gt_1000"] = int(np.unique(np.round(bump * 65535)).size) > 1000
    out["bump_distinct_levels"] = int(np.unique(np.round(bump * 65535)).size)
    n = nrm * 2 - 1
    ln = np.sqrt((n ** 2).sum(-1))
    g["normal_unit_length"] = bool(np.abs(ln - 1).max() < 1e-3)
    # sign: just right of the joint at x = 1536 the face rises to the right -> red below mid (OpenGL/DX same for X)
    r_left_edge = float(nrm[400:1100, 1539:1542, 0].mean())
    r_right_edge = float(nrm[400:1100, 1530:1533, 0].mean())
    g_top_edge = float(nrm[1539:1542, 400:1100, 1].mean())   # below a horizontal joint face rises downward
    out["sign"] = {"red_east_of_joint": r_left_edge, "red_west_of_joint": r_right_edge, "green_south_of_joint": g_top_edge}
    g["red_sign"] = r_left_edge < 0.5 < r_right_edge
    g["green_sign_opengl"] = g_top_edge > 0.5        # OpenGL: surface facing up the image (+Y) -> green > mid
    for k, a in {"bump": bump, "normal": nrm}.items():
        typ = float(np.abs(np.diff(a, axis=1)).mean())
        wx = float(np.abs(a[:, 0] - a[:, -1]).mean())
        wy = float(np.abs(a[0] - a[-1]).mean())
        out["wrap_" + k] = [typ, wx, wy]
        g["wrap_" + k] = wx <= 2 * typ and wy <= 2 * typ
    out["gates"] = g
    out["pass"] = all(g.values())

    # native-res crops for review: 4 x 4 in around a four-way corner (256 px) upscaled x3
    cy, cx, hw = 1536, 3072, 128
    crop = nrm[cy - hw:cy + hw, cx - hw:cx + hw]
    Image.fromarray((crop * 255).astype(np.uint8)).resize((768, 768), Image.NEAREST).save(
        os.path.join(RUN_DIR, "source", "_PREVIEW_normal_native_corner.jpg"), quality=92)
    L = np.array([-np.cos(np.radians(8)), 0.25, np.sin(np.radians(8))])
    L /= np.linalg.norm(L)
    sh = np.clip((n * L).sum(-1), 0, None)
    big = sh[cy - 768:cy + 768, cx - 768:cx + 768]           # 24 x 24 in around the corner
    big = np.clip(big / np.percentile(big, 99.5), 0, 1)
    Image.fromarray((big * 255).astype(np.uint8)).resize((1024, 1024), Image.LANCZOS).save(
        os.path.join(RUN_DIR, "source", "_PREVIEW_grazing_native_24in.jpg"), quality=92)
    with open(os.path.join(RUN_DIR, "source", "map_validation.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, indent=2)
    print(json.dumps(out, indent=1))
    if not out["pass"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
