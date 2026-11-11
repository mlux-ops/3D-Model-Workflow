"""Clear reeded glass - procedural bump, normal and colour maps for Revit 2025.

No manufacturer product was specified. Every dimension below is a design default
chosen for this job, not manufacturer data. Change a constant and re-run.

Run:  C:/Python314/python.exe output/clear_reeded_glass/source/build_maps.py
Writes only inside output/clear_reeded_glass/ (out_path guard).
"""
import json
import math
import struct
import sys
import zlib
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

# ---------------------------------------------------------------- constants
PITCH_IN = 0.5            # reed pitch, centre to centre (design default)
REED_DEPTH_MM = 1.5       # crest above valley (design default)
GLASS_THICKNESS_MM = 6.0  # nominal 1/4 in pane (recorded only; not in the maps)
REEDS_ACROSS = 8          # whole number of reeds across the image
IMAGE_PX = 2048           # square image; must divide evenly by REEDS_ACROSS
SUPERSAMPLE = 16          # horizontal supersampling of the valley cusp
COLOR_SRGB = (250, 250, 250)  # neutral clear, no visible tint
NAME = "Clear_Reeded_Glass_0p5in"

# ---------------------------------------------------------------- paths
RUN_DIR = Path(__file__).resolve().parents[1]
TEX_DIR = RUN_DIR / "textures"
SRC_DIR = RUN_DIR / "source"


def out_path(*parts):
    p = RUN_DIR.joinpath(*parts).resolve()
    if RUN_DIR not in p.parents:
        raise RuntimeError("refusing to write outside run dir: %s" % p)
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


# ---------------------------------------------------------------- PNG io (stdlib)
def write_png(path, arr, bit_depth):
    """arr: (H, W) grey or (H, W, 3) RGB, unsigned ints already in range."""
    if arr.ndim == 2:
        color_type, channels = 0, 1
    else:
        color_type, channels = 2, 3
    h, w = arr.shape[:2]
    if bit_depth == 16:
        raw = arr.astype(">u2").reshape(h, w * channels).tobytes()
        stride = w * channels * 2
    else:
        raw = arr.astype(np.uint8).reshape(h, w * channels).tobytes()
        stride = w * channels
    rows = bytearray()
    for y in range(h):
        rows.append(0)
        rows.extend(raw[y * stride:(y + 1) * stride])

    def chunk(tag, data):
        return (struct.pack(">I", len(data)) + tag + data
                + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))

    sig = bytes([0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A])
    ihdr = struct.pack(">IIBBBBB", w, h, bit_depth, color_type, 0, 0, 0)
    with open(path, "wb") as f:
        f.write(sig)
        f.write(chunk(b"IHDR", ihdr))
        if bit_depth == 8 and channels == 3:
            f.write(chunk(b"sRGB", bytes([0])))
        f.write(chunk(b"IDAT", zlib.compress(bytes(rows), 9)))
        f.write(chunk(b"IEND", b""))


def read_png_header(path):
    with open(path, "rb") as f:
        head = f.read(33)
    w, h, depth, ctype = struct.unpack(">IIBB", head[16:26])
    return {"width": w, "height": h, "bit_depth": depth,
            "color_type": {0: "grey", 2: "rgb", 6: "rgba"}.get(ctype, ctype)}


def read_png_pixels(path):
    """Independent readback of what was written (first row only is enough: rows repeat)."""
    with open(path, "rb") as f:
        data = f.read()
    pos, idat, w, h, depth, ctype = 8, b"", 0, 0, 0, 0
    while pos < len(data):
        n = struct.unpack(">I", data[pos:pos + 4])[0]
        tag = data[pos + 4:pos + 8]
        body = data[pos + 8:pos + 8 + n]
        if tag == b"IHDR":
            w, h, depth, ctype = struct.unpack(">IIBB", body[:10])
        elif tag == b"IDAT":
            idat += body
        pos += 12 + n
    raw = zlib.decompress(idat)
    ch = 1 if ctype == 0 else 3
    stride = w * ch * (depth // 8)
    out = []
    for y in range(h):
        line = raw[y * (stride + 1):(y + 1) * (stride + 1)]
        if line[0] != 0:
            raise RuntimeError("unexpected PNG filter in %s" % path)
        dt = ">u2" if depth == 16 else "u1"
        out.append(np.frombuffer(line[1:], dtype=dt).reshape(w, ch))
    return np.stack(out)  # (H, W, ch)


# ---------------------------------------------------------------- geometry
def reed_profile():
    """One reed, analytic, float64. Returns per-pixel mean height (mm) and mean normal."""
    px_per_reed = IMAGE_PX // REEDS_ACROSS
    if px_per_reed * REEDS_ACROSS != IMAGE_PX:
        raise RuntimeError("IMAGE_PX must be a multiple of REEDS_ACROSS")
    pitch_mm = PITCH_IN * 25.4
    half = pitch_mm / 2.0
    radius = (half * half + REED_DEPTH_MM ** 2) / (2.0 * REED_DEPTH_MM)
    n_sub = px_per_reed * SUPERSAMPLE
    # sub-sample centres across one reed, x measured from the crest
    x = (np.arange(n_sub, dtype=np.float64) + 0.5) / n_sub * pitch_mm - half
    root = np.sqrt(radius * radius - x * x)
    height = root - (radius - REED_DEPTH_MM)          # 0 at valley, DEPTH at crest
    slope = -x / root                                  # dh/dx, analytic
    inv = 1.0 / np.sqrt(slope * slope + 1.0)
    nx, nz = -slope * inv, inv                         # unit normal (ny = 0)
    height_px = height.reshape(px_per_reed, SUPERSAMPLE).mean(axis=1)
    nx_px = nx.reshape(px_per_reed, SUPERSAMPLE).mean(axis=1)
    nz_px = nz.reshape(px_per_reed, SUPERSAMPLE).mean(axis=1)
    norm = np.sqrt(nx_px ** 2 + nz_px ** 2)
    nx_px, nz_px = nx_px / norm, nz_px / norm
    geo = {
        "pitch_mm": pitch_mm,
        "arc_radius_mm": radius,
        "edge_slope_deg": math.degrees(math.atan(half / math.sqrt(radius ** 2 - half ** 2))),
        "px_per_reed": px_per_reed,
        "mm_per_px": pitch_mm / px_per_reed,
    }
    return height_px, nx_px, nz_px, geo


def build():
    height_px, nx_px, nz_px, geo = reed_profile()
    row_h = np.tile(height_px, REEDS_ACROSS)           # (W,)
    row_nx = np.tile(nx_px, REEDS_ACROSS)
    row_nz = np.tile(nz_px, REEDS_ACROSS)

    # 16-bit height: 0 = valley floor, 65535 = REED_DEPTH_MM
    bump_row = np.rint(row_h / REED_DEPTH_MM * 65535.0).clip(0, 65535).astype(np.uint16)
    bump = np.tile(bump_row, (IMAGE_PX, 1))

    # RGB16 tangent-space normal: R = +X (right), G = Y (flat, mid value), B = +Z (out)
    nrm_row = np.stack([
        np.rint((row_nx * 0.5 + 0.5) * 65535.0),
        np.full_like(row_nx, 32768.0),
        np.rint((row_nz * 0.5 + 0.5) * 65535.0),
    ], axis=1).clip(0, 65535).astype(np.uint16)
    normal = np.tile(nrm_row[None, :, :], (IMAGE_PX, 1, 1))

    color = np.empty((IMAGE_PX, IMAGE_PX, 3), dtype=np.uint8)
    color[:, :] = COLOR_SRGB

    files = {
        "bump": out_path("textures", NAME + "_Bump_16bit.png"),
        "normal": out_path("textures", NAME + "_Normal_16bit.png"),
        "color": out_path("textures", NAME + "_Color.png"),
    }
    write_png(files["bump"], bump, 16)
    write_png(files["normal"], normal, 16)
    write_png(files["color"], color, 8)
    return files, geo, row_h, row_nx, row_nz


# ---------------------------------------------------------------- checks
def verify(files, geo):
    report = {"files": {}, "checks": {}}
    expect = {"bump": (16, "grey"), "normal": (16, "rgb"), "color": (8, "rgb")}
    ok = True
    for key, path in files.items():
        head = read_png_header(path)
        head["bytes"] = path.stat().st_size
        head["path"] = str(path).replace("\\", "/")
        report["files"][key] = head
        good = (head["bit_depth"], head["color_type"]) == expect[key] \
            and head["width"] == IMAGE_PX and head["height"] == IMAGE_PX
        report["checks"]["header_" + key] = good
        ok &= good

    ppr = geo["px_per_reed"]
    for key in ("bump", "normal"):
        px = read_png_pixels(files[key]).astype(np.int64)
        periodic = bool(np.array_equal(px, np.roll(px, ppr, axis=1)))
        rows_same = bool(np.array_equal(px, np.roll(px, 1, axis=0)))
        mirror = bool(np.array_equal(px[:, :, 0 if key == "bump" else 2],
                                     px[:, ::-1, 0 if key == "bump" else 2]))
        report["checks"][key + "_periodic_by_one_reed"] = periodic
        report["checks"][key + "_uniform_along_length"] = rows_same
        report["checks"][key + "_left_right_mirror"] = mirror
        ok &= periodic and rows_same and mirror
        if key == "bump":
            # wrap step: last column -> first column, against the largest interior step
            row = px[0, :, 0]
            wrap_step = abs(int(row[0]) - int(row[-1]))
            interior = int(np.abs(np.diff(row)).max())
            report["checks"]["bump_wrap_step_dn"] = wrap_step
            report["checks"]["bump_max_interior_step_dn"] = interior
            report["checks"]["bump_wrap_not_worse_than_interior"] = wrap_step <= interior
            report["checks"]["bump_range_dn"] = [int(row.min()), int(row.max())]
            ok &= wrap_step <= interior
        else:
            g = px[:, :, 1]
            report["checks"]["normal_green_flat"] = bool(g.min() == g.max() == 32768)
            r = px[0, :ppr, 0]
            report["checks"]["normal_red_left_flank_below_mid"] = bool(r[: ppr // 2].max() < 32768)
            report["checks"]["normal_red_right_flank_above_mid"] = bool(r[ppr // 2:].min() > 32767)
            ok &= report["checks"]["normal_green_flat"]
            ok &= report["checks"]["normal_red_left_flank_below_mid"]
            ok &= report["checks"]["normal_red_right_flank_above_mid"]
    cpx = read_png_pixels(files["color"])
    uniform = bool((cpx == np.array(COLOR_SRGB, dtype=np.uint8)).all())
    report["checks"]["color_spatially_uniform"] = uniform
    ok &= uniform

    width_in = PITCH_IN * REEDS_ACROSS
    report["sample_size"] = {
        "width_in": width_in, "height_in": width_in,
        "revit": "0'-%g\" x 0'-%g\"" % (width_in, width_in),
        "pixel_aspect": 1.0, "physical_aspect": 1.0,
    }
    report["relief"] = {
        "reed_depth_mm": REED_DEPTH_MM,
        "bump_full_range_mm": REED_DEPTH_MM,
        "pitch_in": PITCH_IN, "pitch_mm": geo["pitch_mm"],
        "arc_radius_mm": round(geo["arc_radius_mm"], 4),
        "flank_angle_at_valley_deg": round(geo["edge_slope_deg"], 2),
        "grout_joint_mm": "not applicable (no joint in glass)",
        "clearance_mm": "not applicable (no joint in glass)",
        "glass_thickness_mm_nominal": GLASS_THICKNESS_MM,
    }
    report["geometry"] = {k: (round(v, 6) if isinstance(v, float) else v) for k, v in geo.items()}
    report["all_checks_pass"] = bool(ok)
    return report


# ---------------------------------------------------------------- previews
def previews(row_h, row_nx, row_nz, geo):
    w = 800
    scale = IMAGE_PX // w if IMAGE_PX % w == 0 else None
    # resample one atlas row to 800 px by area mean over the supersampled idea: simple interp
    xs = (np.arange(w) + 0.5) / w * IMAGE_PX - 0.5
    nx = np.interp(xs, np.arange(IMAGE_PX), row_nx)
    nz = np.interp(xs, np.arange(IMAGE_PX), row_nz)

    def shade(nx_row, nz_row, elev_deg, from_left=True):
        el = math.radians(elev_deg)
        lx = -math.cos(el) if from_left else math.cos(el)
        lz = math.sin(el)
        lam = np.clip(nx_row * lx + nz_row * lz, 0.0, None)
        return lam

    # 1. grazing light, light from the LEFT at 12 degrees above the surface
    lam = shade(nx, nz, 12.0, True)
    img = np.tile((np.clip(0.06 + 0.94 * lam / lam.max(), 0, 1) ** (1 / 2.2) * 255).astype(np.uint8), (500, 1))
    Image.fromarray(img, "L").save(out_path("source", "_PREVIEW_grazing_light_from_left.png"))

    # 2. frontal light for comparison (shows why frontal review is not enough)
    lam = shade(nx, nz, 80.0, True)
    img = np.tile((np.clip(lam, 0, 1) ** (1 / 2.2) * 255).astype(np.uint8), (500, 1))
    Image.fromarray(img, "L").save(out_path("source", "_PREVIEW_frontal_light.png"))

    # 3. 3x3 wrap of the bump map with the tile boundaries marked only in the margin
    tile = 256
    xs2 = (np.arange(tile) + 0.5) / tile * IMAGE_PX - 0.5
    h_small = np.interp(xs2, np.arange(IMAGE_PX), row_h) / REED_DEPTH_MM
    strip = np.tile(h_small, 3)
    body = np.tile((strip * 255).astype(np.uint8), (tile * 3, 1))
    canvas = Image.new("L", (tile * 3, tile * 3 + 16), 255)
    canvas.paste(Image.fromarray(body, "L"), (0, 16))
    d = ImageDraw.Draw(canvas)
    for k in range(4):
        xk = min(k * tile, tile * 3 - 1)
        d.line([(xk, 0), (xk, 14)], fill=0, width=2)
    canvas.save(out_path("source", "_PREVIEW_bump_wrap_3x3.png"))

    # 4. profile section, true proportions (2 reeds), exaggeration stated
    pw, ph = 800, 260
    sec = Image.new("RGB", (pw, ph), (255, 255, 255))
    d = ImageDraw.Draw(sec)
    ppr = geo["px_per_reed"]
    two = np.tile(row_h[:ppr], 2)
    mm_w = 2 * geo["pitch_mm"]
    s = (pw - 40) / mm_w                               # px per mm, same on both axes
    base_y = ph - 40
    pts = [(20 + (i + 0.5) / len(two) * mm_w * s, base_y - two[i] * s) for i in range(len(two))]
    glass_bottom = base_y + (GLASS_THICKNESS_MM - REED_DEPTH_MM) * s
    poly = pts + [(pw - 20, min(glass_bottom, ph - 2)), (20, min(glass_bottom, ph - 2))]
    d.polygon(poly, fill=(205, 228, 232))
    d.line(pts, fill=(20, 60, 80), width=2)
    d.text((22, 6), "Section through two reeds, true proportions (1:1 on both axes). "
                    "Pitch %.1f mm, depth %.1f mm." % (geo["pitch_mm"], REED_DEPTH_MM), fill=(0, 0, 0))
    sec.save(out_path("source", "_PREVIEW_profile_section.png"))

    # 5. normal map thumbnail
    r = (nx * 0.5 + 0.5) * 255
    b = (nz * 0.5 + 0.5) * 255
    thumb = np.stack([r, np.full_like(r, 128.0), b], axis=1).astype(np.uint8)
    Image.fromarray(np.tile(thumb[None], (300, 1, 1)), "RGB").save(
        out_path("source", "_PREVIEW_normal_thumb.png"))


def main():
    files, geo, row_h, row_nx, row_nz = build()
    report = verify(files, geo)
    with open(out_path("source", "map_validation.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    previews(row_h, row_nx, row_nz, geo)
    print(json.dumps(report["checks"], indent=1))
    print("sample size:", report["sample_size"]["revit"])
    print("ALL CHECKS PASS" if report["all_checks_pass"] else "CHECKS FAILED")
    if not report["all_checks_pass"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
