from __future__ import annotations

import hashlib
import json
import math
import os
import pathlib
import shutil
import sys
import zipfile

import numpy as np
from PIL import Image, ImageDraw, ImageFilter


ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "daltile_remedy_hydro"
TEX = OUT / "textures"
REF = ROOT / "references" / "daltile_remedy_hydro"
GEN = ROOT / "output" / "model-transfer-tests" / "candidate-20260918-01" / "material" / "adsklib_generator"
ADELLA = ROOT / "output" / "adella" / "MSI_Adella_Viso_White_R2025.adsklib"

MATERIAL_NAME = "Daltile Remedy Hydro - 2x10 Fluted Glossy"
SKU = "RD22RCT210FLUGL"
URL = "https://www.daltile.com/products/wall/remedy/hydro"

TILE_W_IN = 10.0
TILE_H_IN = 2.0
GROUT_IN = 1.0 / 16.0
COLS = 20
ROWS = 10
PX_PER_IN = 48
MODULE_W_IN = TILE_W_IN + GROUT_IN
MODULE_H_IN = TILE_H_IN + GROUT_IN
ATLAS_W_IN = COLS * MODULE_W_IN
ATLAS_H_IN = ROWS * MODULE_H_IN
W = round(ATLAS_W_IN * PX_PER_IN)
H = round(ATLAS_H_IN * PX_PER_IN)
SEED = 220210

# Relief values are explicit estimates because Daltile does not publish flute depth.
PATTERN_RELIEF_MM = 1.20
GROUT_STEP_MM = 2.20
CLEARANCE_MM = GROUT_STEP_MM - PATTERN_RELIEF_MM


def sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def save_png16(path: pathlib.Path, arr01: np.ndarray) -> None:
    a = np.clip(arr01, 0.0, 1.0)
    Image.fromarray(np.round(a * 65535.0).astype(np.uint16), mode="I;16").save(path)


def dominant_palette() -> np.ndarray:
    # Use manufacturer imagery itself as the palette source. The Silo/Grid images
    # isolate the product better than room scenes; quantization removes lighting noise.
    ims = []
    for name in ("Silo_01.jpg", "Grid.jpg", "Detail.jpg"):
        im = Image.open(REF / name).convert("RGB").resize((512, 512))
        ims.append(np.asarray(im, dtype=np.uint8).reshape(-1, 3))
    px = np.concatenate(ims, axis=0)
    # Keep the dark green/teal product population and reject near-white studio background.
    lum = px.mean(axis=1)
    sat = px.max(axis=1) - px.min(axis=1)
    keep = (lum < 185) & (sat > 5)
    sample = px[keep]
    if len(sample) < 1000:
        sample = px[lum < 185]
    im = Image.fromarray(sample[: min(len(sample), 240000)].reshape(-1, 1, 3), "RGB")
    q = im.quantize(colors=12, method=Image.Quantize.MAXCOVERAGE).convert("RGB")
    colors = sorted(q.getcolors(q.width * q.height), reverse=True)
    pal = np.array([c for _, c in colors[:10]], dtype=np.float32)
    return pal


def smooth_noise(rng: np.random.Generator, h: int, w: int, radius: float) -> np.ndarray:
    small_h = max(4, h // 20)
    small_w = max(4, w // 40)
    a = rng.normal(0.0, 1.0, (small_h, small_w)).astype(np.float32)
    a = (a - a.min()) / max(1e-6, a.max() - a.min())
    im = Image.fromarray(np.round(a * 255).astype(np.uint8), "L").resize((w, h), Image.Resampling.BICUBIC)
    im = im.filter(ImageFilter.GaussianBlur(radius))
    b = np.asarray(im, dtype=np.float32) / 255.0
    return b - b.mean()


def build_maps() -> dict:
    TEX.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)
    palette = dominant_palette()
    color = np.zeros((H, W, 3), dtype=np.float32)
    height_mm = np.zeros((H, W), dtype=np.float32)
    rough = np.zeros((H, W), dtype=np.float32)

    grout_rgb = np.array([111, 119, 115], dtype=np.float32)
    color[:] = grout_rgb
    height_mm[:] = 0.0
    rough[:] = 0.62

    gx = max(1, round(GROUT_IN * PX_PER_IN))
    gy = gx
    tw = max(8, round(TILE_W_IN * PX_PER_IN))
    th = max(8, round(TILE_H_IN * PX_PER_IN))

    assignments = []
    last_choices = {}
    for row in range(ROWS):
        for col in range(COLS):
            x0 = round(col * MODULE_W_IN * PX_PER_IN) + gx // 2
            y0 = round(row * MODULE_H_IN * PX_PER_IN) + gy // 2
            x1 = min(W, x0 + tw)
            y1 = min(H, y0 + th)
            hh, ww = y1 - y0, x1 - x0
            if hh <= 0 or ww <= 0:
                continue

            # V4 variation: select from manufacturer-derived palette while avoiding
            # identical immediate neighbors. Add low-frequency glaze shifts only.
            choices = list(range(len(palette)))
            for neighbor in ((row, col - 1), (row - 1, col)):
                if neighbor in last_choices and last_choices[neighbor] in choices and len(choices) > 2:
                    choices.remove(last_choices[neighbor])
            idx = int(rng.choice(choices))
            last_choices[(row, col)] = idx
            base = palette[idx].copy()
            base += rng.normal(0.0, 5.5, 3)
            n = smooth_noise(rng, hh, ww, 8.0)
            tile = base[None, None, :] + n[:, :, None] * rng.uniform(9.0, 18.0)
            tile = np.clip(tile, 0, 255)

            # Flutes run along the 10-inch length; profile varies across the 2-inch
            # width. Six soft ribs give a readable sculpted response without baking
            # photographic highlights into color.
            yy = (np.arange(hh, dtype=np.float32) + 0.5) / hh
            ribs = 0.5 + 0.5 * np.cos(2.0 * math.pi * 6.0 * yy)
            ribs = np.power(np.clip(ribs, 0.0, 1.0), 0.72)
            relief = (1.0 - ribs) * PATTERN_RELIEF_MM
            relief2 = np.repeat(relief[:, None], ww, axis=1)
            # Subtle handmade longitudinal irregularity, spatially smooth and
            # independent for each tile, stays well below the main relief amplitude.
            relief2 += smooth_noise(rng, hh, ww, 6.0) * 0.10
            relief2 = np.clip(relief2, 0.0, PATTERN_RELIEF_MM)

            color[y0:y1, x0:x1] = tile
            height_mm[y0:y1, x0:x1] = GROUT_STEP_MM - relief2
            rr = 0.18 + smooth_noise(rng, hh, ww, 10.0) * 0.025
            rough[y0:y1, x0:x1] = np.clip(rr, 0.12, 0.25)
            assignments.append({"row": row, "col": col, "palette_index": idx, "rgb": [int(v) for v in np.clip(base, 0, 255)]})

    # Normalize height to 0..1 where grout is the low floor and tile crests are high.
    h01 = height_mm / GROUT_STEP_MM

    # Compute tangent-space OpenGL normal from physical height gradients.
    mm_per_px_x = 25.4 / PX_PER_IN
    mm_per_px_y = 25.4 / PX_PER_IN
    # Periodic centered derivatives prevent the tangent-space normal map from
    # introducing a false seam at an atlas boundary whose height already wraps.
    gx_mm = (np.roll(height_mm, -1, axis=1) - np.roll(height_mm, 1, axis=1)) / (2.0 * mm_per_px_x)
    gy_mm = (np.roll(height_mm, -1, axis=0) - np.roll(height_mm, 1, axis=0)) / (2.0 * mm_per_px_y)
    strength = 1.0
    nx = -gx_mm * strength
    ny = -gy_mm * strength
    nz = np.ones_like(nx)
    norm = np.sqrt(nx * nx + ny * ny + nz * nz)
    normal = np.dstack(((nx / norm + 1) * 0.5, (ny / norm + 1) * 0.5, nz / norm))
    # The atlas perimeter is half-grout and should be optically flat. Preserve
    # a neutral tangent normal there so the first/last texels are identical.
    normal[0, :, :] = (0.5, 0.5, 1.0)
    normal[-1, :, :] = (0.5, 0.5, 1.0)
    normal[:, 0, :] = (0.5, 0.5, 1.0)
    normal[:, -1, :] = (0.5, 0.5, 1.0)

    color_path = TEX / "Daltile_Remedy_Hydro_Fluted_BaseColor.png"
    bump_path = TEX / "Daltile_Remedy_Hydro_Fluted_Bump16.png"
    normal_path = TEX / "Daltile_Remedy_Hydro_Fluted_Normal.png"
    rough_path = TEX / "Daltile_Remedy_Hydro_Fluted_Roughness.png"
    Image.fromarray(np.round(color).astype(np.uint8), "RGB").save(color_path, optimize=True)
    save_png16(bump_path, h01)
    Image.fromarray(np.round(np.clip(normal, 0, 1) * 255).astype(np.uint8), "RGB").save(normal_path, optimize=True)
    Image.fromarray(np.round(np.clip(rough, 0, 1) * 255).astype(np.uint8), "L").save(rough_path, optimize=True)

    # 3x3 wrapped preview and a neutral thumbnail.
    thumb = Image.open(color_path).crop((0, 0, min(W, round(4 * MODULE_W_IN * PX_PER_IN)), min(H, round(4 * MODULE_H_IN * PX_PER_IN))))
    thumb.thumbnail((512, 512), Image.Resampling.LANCZOS)
    thumb_path = OUT / "thumbnail.png"
    canvas = Image.new("RGB", (512, 512), tuple(grout_rgb.astype(int)))
    canvas.paste(thumb, ((512 - thumb.width) // 2, (512 - thumb.height) // 2))
    canvas.save(thumb_path)

    p = Image.open(color_path)
    preview = Image.new("RGB", (p.width * 3, p.height * 3))
    for yy in range(3):
        for xx in range(3):
            preview.paste(p, (xx * p.width, yy * p.height))
    preview.thumbnail((3600, 1200), Image.Resampling.LANCZOS)
    preview_path = OUT / "qa_wrap_3x3.jpg"
    preview.save(preview_path, quality=90)

    return {
        "palette": palette.astype(int).tolist(),
        "assignments": assignments,
        "paths": {"color": str(color_path), "bump": str(bump_path), "normal": str(normal_path), "roughness": str(rough_path), "thumbnail": str(thumb_path), "wrap_preview": str(preview_path)},
    }


def build_adsklib(maps: dict) -> dict:
    sys.path.insert(0, str(GEN))
    import adsklib_gen as g

    ref = g.extract_params(str(ADELLA))
    candidate = OUT / "Daltile_Remedy_Hydro_2x10_Fluted_Glossy_R2025_candidate.adsklib"
    final = OUT / "Daltile_Remedy_Hydro_2x10_Fluted_Glossy_R2025.adsklib"
    thumb_bytes = pathlib.Path(maps["paths"]["thumbnail"]).read_bytes()
    desc = "Daltile Remedy Hydro 2x10 fluted glossy ceramic wall tile; V4 random shade variation; estimated flute relief; 1/16 inch grout"
    kwargs = dict(ref)
    for k in ("package_guid", "creator_guid", "created", "modified", "material_name", "description", "diffuse_path", "bump_path", "real_world_scale_in", "thumbnail_png_bytes", "_thumb_suffix_override"):
        kwargs.pop(k, None)
    kwargs.update(
        material_name=MATERIAL_NAME,
        description=desc,
        diffuse_path=str(pathlib.Path(maps["paths"]["color"]).resolve()),
        bump_path=str(pathlib.Path(maps["paths"]["bump"]).resolve()),
        real_world_scale_in=(ATLAS_W_IN, ATLAS_H_IN),
        thumbnail_png_bytes=thumb_bytes,
        _template_path=str(ADELLA),
    )
    g.build_library(str(candidate), **kwargs)
    with zipfile.ZipFile(candidate) as zf:
        bad = zf.testzip()
        if bad:
            raise RuntimeError("candidate ADSKLIB corrupt entry: %s" % bad)
    readback = g.extract_params(str(candidate))
    if readback["material_name"] != MATERIAL_NAME:
        raise RuntimeError("ADSKLIB readback material name mismatch")
    if tuple(round(x, 5) for x in readback["real_world_scale_in"]) != tuple(round(x, 5) for x in (ATLAS_W_IN, ATLAS_H_IN)):
        raise RuntimeError("ADSKLIB readback scale mismatch")
    if final.exists():
        final = OUT / "Daltile_Remedy_Hydro_2x10_Fluted_Glossy_R2025_Rev2.adsklib"
    shutil.copy2(candidate, final)
    return {"candidate": str(candidate), "final": str(final), "sha256": sha256(final), "readback": {k: readback[k] for k in ("material_name", "description", "diffuse_path", "bump_path", "real_world_scale_in")}}


def write_docs(maps: dict, adsk: dict) -> None:
    refs = []
    for f in sorted(REF.glob("*.jpg")):
        refs.append({"file": f.name, "sha256": sha256(f), "bytes": f.stat().st_size})
    manifest = {
        "material": MATERIAL_NAME,
        "manufacturer": "Daltile",
        "series": "Remedy",
        "color": "Hydro",
        "sku": SKU,
        "finish": "Glossy",
        "style": "Fluted",
        "nominal_size_in": [10.0, 2.0],
        "nominal_thickness_in": 0.5,
        "shade_variation": "V4: Random",
        "url": URL,
        "grout_assumption_in": GROUT_IN,
        "atlas_size_in": [ATLAS_W_IN, ATLAS_H_IN],
        "atlas_pixels": [W, H],
        "seed": SEED,
        "relief": {"pattern_relief_mm": PATTERN_RELIEF_MM, "grout_step_mm": GROUT_STEP_MM, "clearance_mm": CLEARANCE_MM, "status": "estimated from product character; manufacturer depth not published"},
        "maps": {k: {"path": os.path.relpath(v, OUT), "sha256": sha256(pathlib.Path(v))} for k, v in maps["paths"].items()},
        "adsklib": {"path": os.path.relpath(adsk["final"], OUT), "sha256": adsk["sha256"], "readback": adsk["readback"]},
        "sources": refs,
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    readme = f"""# Daltile Remedy Hydro — 2x10 Fluted Glossy

Revit 2025 material library for Daltile Remedy Hydro, Fluted, Glossy, SKU `{SKU}`.

Manufacturer facts used: nominal 2 x 10 in, nominal 1/2 in thickness, glossy finish, V4 Random shade variation. The color atlas is derived from official Daltile Hydro imagery. The flute height is recreated as geometry in the bump/normal maps rather than copied from photographed lighting.

## Load in Revit

1. Keep the `.adsklib` and `textures` folder together.
2. Revit > Manage > Materials > Material Browser > Open Existing Library and select `{pathlib.Path(adsk['final']).name}`.
3. Add the material to the project. If Revit reports missing texture paths after moving the package, repath the Base Color and Bump maps to the supplied `textures` folder.

The ADSKLIB binds the BaseColor and 16-bit Bump maps. A registered tangent-space OpenGL Normal map and Roughness map are included as companion assets for renderers that support them.

Physical atlas: {ATLAS_W_IN:.4f} x {ATLAS_H_IN:.4f} in ({COLS} x {ROWS} tile modules) with assumed 1/16 in grout. The finite bitmap repeats mathematically, but the atlas deliberately uses broad V4 per-tile variation and avoids immediate duplicate palette assignments.

Relief estimate: pattern {PATTERN_RELIEF_MM:.2f} mm; grout step {GROUT_STEP_MM:.2f} mm; remaining clearance {CLEARANCE_MM:.2f} mm. Daltile does not publish flute depth, so these are visual/rendering estimates, not measured product geometry.
"""
    (OUT / "README.md").write_text(readme, encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    maps = build_maps()
    adsk = build_adsklib(maps)
    write_docs(maps, adsk)
    print(json.dumps({"output": str(OUT), "adsklib": adsk, "atlas_pixels": [W, H], "atlas_in": [ATLAS_W_IN, ATLAS_H_IN], "relief_mm": [PATTERN_RELIEF_MM, GROUT_STEP_MM, CLEARANCE_MM]}, indent=2))


if __name__ == "__main__":
    main()
