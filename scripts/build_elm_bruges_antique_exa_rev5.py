from __future__ import annotations

import hashlib
import json
import math
import pathlib
import shutil
import sys
import zipfile

import numpy as np
from PIL import Image, ImageDraw, ImageFilter


ROOT = pathlib.Path(__file__).resolve().parents[1]
REF = ROOT / "references" / "elm_bruges_antique_exa"
OUT = ROOT / "output" / "elm_bruges_antique_exa"
TEX = OUT / "textures"
GEN = ROOT / "output" / "model-transfer-tests" / "candidate-20260918-01" / "material" / "adsklib_generator"
TEMPLATE = ROOT / "output" / "adella" / "MSI_Adella_Viso_White_R2025.adsklib"

NAME = "ELM Colorado Bruges Antique - Exa Mosaic"
COLS, ROWS = 64, 72
PITCH_X, PITCH_Y = 112, 97
HALF_W, RADIUS = 56, 65
W, H = COLS * PITCH_X, ROWS * PITCH_Y
SHEET_W_IN, SHEET_H_IN = 29.5 / 2.54, 25.5 / 2.54
ATLAS_IN = (16 * SHEET_W_IN, 18 * SHEET_H_IN)
GROUT_STEP_MM = 0.50
PATTERN_RELIEF_MM = 0.30
MICRO_RELIEF_MM = 0.020
SEED = 85212026


def digest(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def antique_faces() -> list[Image.Image]:
    im = Image.open(REF / "grid_bruges_antique.jpg").convert("RGB")
    if im.size != (900, 900):
        raise ValueError("unexpected manufacturer Antique grid size")
    # Every crop stays inside one pictured stone face; none crosses a baked joint.
    return [im.crop((x * 225 + 18, y * 225 + 18, (x + 1) * 225 - 18, (y + 1) * 225 - 18))
            for y in range(4) for x in range(4)]


def new_face(faces: list[Image.Image], rng: np.random.Generator, index: int) -> Image.Image:
    face = faces[index]
    side = int(rng.integers(110, 179))
    x = int(rng.integers(0, face.width - side + 1))
    y = int(rng.integers(0, face.height - side + 1))
    crop = face.crop((x, y, x + side, y + side))
    if rng.integers(0, 2):
        crop = crop.transpose(Image.Transpose.ROTATE_180)
    return crop.resize((PITCH_X + 2, 2 * RADIUS + 2), Image.Resampling.LANCZOS)


def mask_and_height(kind: str, phase: float, face: Image.Image) -> tuple[Image.Image, Image.Image, Image.Image]:
    pw, ph = face.size
    cx, cy = pw // 2, ph // 2
    # One-pixel inset leaves a narrow, continuous grout channel. The same
    # polygon is reused for every hex; only the face and accent vary.
    polygon = [(cx, cy - RADIUS + 2), (cx + HALF_W - 2, cy - RADIUS / 2 + 1),
               (cx + HALF_W - 2, cy + RADIUS / 2 - 1), (cx, cy + RADIUS - 2),
               (cx - HALF_W + 2, cy + RADIUS / 2 - 1),
               (cx - HALF_W + 2, cy - RADIUS / 2 + 1)]
    mask = Image.new("L", (pw, ph), 0)
    ImageDraw.Draw(mask).polygon(polygon, fill=255)
    feather = mask.filter(ImageFilter.GaussianBlur(0.65))
    rgb = np.asarray(face, dtype=np.float32).copy()
    yy, xx = np.mgrid[0:ph, 0:pw]
    # Antique stone retains subtle actual photographic tone and grain.
    gray = rgb.mean(2)
    low = np.asarray(Image.fromarray(gray.astype("uint8")).filter(ImageFilter.GaussianBlur(6)), dtype=np.float32)
    micro = np.clip((gray - low) / 100.0, -1, 1) * MICRO_RELIEF_MM
    recess = np.zeros((ph, pw), dtype=np.float32)
    if kind == "grooved":
        # Same descending diagonal orientation shown in Kronos SKU 8521.
        d = (xx + 0.70 * yy + phase) % 14.0
        groove = np.maximum(0.0, 1.0 - np.minimum(d, 14.0 - d) / 1.8)
        recess = groove.astype(np.float32) * PATTERN_RELIEF_MM
        rgb -= groove[:, :, None] * 13.0
    elif kind == "worn":
        # Keep pitting smaller than the deliberate grout recess.
        pits = np.clip((low - gray - 7.0) / 45.0, 0.0, 1.0)
        recess = pits * 0.16
        rgb -= pits[:, :, None] * 5.0
    height = np.clip(GROUT_STEP_MM - recess + micro, 0.0, GROUT_STEP_MM + MICRO_RELIEF_MM)
    height *= np.asarray(feather, dtype=np.float32) / 255.0
    h16 = Image.fromarray(np.round(height / (GROUT_STEP_MM + MICRO_RELIEF_MM) * 65535).astype("uint16"))
    return Image.fromarray(np.clip(rgb, 0, 255).astype("uint8"), "RGB"), h16, mask


def paste_wrapped(canvas: Image.Image, patch: Image.Image, mask: Image.Image, x: int, y: int) -> None:
    cw, ch = canvas.size
    pw, ph = patch.size
    for dx in (-cw, 0, cw):
        px = x + dx
        if px >= cw or px + pw <= 0:
            continue
        for dy in (-ch, 0, ch):
            py = y + dy
            if py >= ch or py + ph <= 0:
                continue
            canvas.paste(patch, (px, py), mask)


def make_maps() -> dict:
    TEX.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)
    faces = antique_faces()
    color = Image.new("RGB", (W, H), (139, 134, 126))
    # Pillow's masked paste into I;16 silently stops painting after half the
    # pixel width. Compose as 32-bit integer and quantize only when saving.
    bump = Image.new("I", (W, H), 0)
    counts = {"plain": 0, "worn": 0, "grooved": 0}
    signatures: set[bytes] = set()
    choices: dict[tuple[int, int], int] = {}
    for row in range(ROWS):
        for col in range(COLS):
            neighbors = {choices.get((row, col - 1)), choices.get((row - 1, col))}
            candidates = [i for i in range(16) if i not in neighbors]
            fi = int(rng.choice(candidates))
            choices[(row, col)] = fi
            k = rng.random()
            kind = "grooved" if k < 0.13 else "worn" if k < 0.29 else "plain"
            counts[kind] += 1
            for _ in range(100):
                patch = new_face(faces, rng, fi)
                signature = hashlib.sha256(patch.tobytes()).digest()
                if signature not in signatures:
                    signatures.add(signature)
                    break
            else:
                raise RuntimeError("could not select a unique photographed face crop")
            face, height, mask = mask_and_height(kind, float(rng.uniform(0, 14)), patch)
            cx = col * PITCH_X + (HALF_W if row % 2 else 0)
            cy = row * PITCH_Y
            x = cx - face.width // 2
            y = cy - face.height // 2
            paste_wrapped(color, face, mask, x, y)
            paste_wrapped(bump, height.convert("I"), mask, x, y)
    # Exact last/first texels make both bitmap boundaries periodic.
    ca = np.asarray(color).copy()
    ba = np.asarray(bump, dtype=np.uint16).copy()
    ca[-1, :, :] = ca[0, :, :]
    ca[:, -1, :] = ca[:, 0, :]
    ba[-1, :] = ba[0, :]
    ba[:, -1] = ba[:, 0]
    color = Image.fromarray(ca)
    bump = Image.fromarray(ba)
    cp = TEX / "ELM_Bruges_Antique_Exa_Rev5_Color.png"
    bp = TEX / "ELM_Bruges_Antique_Exa_Rev5_Bump16.png"
    color.save(cp, optimize=True)
    bump.save(bp)
    sample = color.crop((0, 0, PITCH_X * 8, PITCH_Y * 8))
    sample.save(TEX / "_REVIEW_eight_by_eight_hexes.png")
    wrap = Image.new("RGB", (sample.width * 3, sample.height * 3))
    for yy in range(3):
        for xx in range(3):
            wrap.paste(sample, (xx * sample.width, yy * sample.height))
    wrap.thumbnail((1800, 1800), Image.Resampling.LANCZOS)
    wrap.save(TEX / "_REVIEW_three_by_three_wrap.jpg", quality=92)
    atlas_room = color.copy()
    atlas_room.thumbnail((1600, 1600), Image.Resampling.LANCZOS)
    atlas_room.save(TEX / "_REVIEW_full_atlas_room.jpg", quality=92)
    repeated = Image.new("RGB", (atlas_room.width * 3, atlas_room.height * 3))
    for yy in range(3):
        for xx in range(3):
            repeated.paste(atlas_room, (xx * atlas_room.width, yy * atlas_room.height))
    repeated.thumbnail((2400, 2400), Image.Resampling.LANCZOS)
    repeated.save(TEX / "_REVIEW_full_atlas_three_by_three.jpg", quality=91)
    # Grazing-light diagnostic from physical bump height; grout and diagonal
    # motif must read separately. This is an inspection image, not an asset.
    crop16 = np.asarray(bump.crop((0, 0, sample.width, sample.height)), dtype=np.uint16)
    # Pillow's blur does not accept I;16; 8-bit is sufficient for this preview.
    sh = np.asarray(Image.fromarray((crop16 >> 8).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.9)), dtype=np.float32)
    gx = np.gradient(sh, axis=1) / 255 * (GROUT_STEP_MM + MICRO_RELIEF_MM)
    gy = np.gradient(sh, axis=0) / 255 * (GROUT_STEP_MM + MICRO_RELIEF_MM)
    light = np.clip(0.76 - gx * 1.7 - gy * 0.4, 0.25, 1.0)
    lit = np.clip(np.asarray(sample, dtype=np.float32) * light[:, :, None], 0, 255)
    Image.fromarray(lit.astype("uint8"), "RGB").save(TEX / "_REVIEW_grazing.jpg", quality=94)
    return {"color": cp, "bump": bp, "counts": counts, "unique_patch_count": len(signatures),
            "edge_color_equal": bool(np.array_equal(ca[0], ca[-1]) and np.array_equal(ca[:, 0], ca[:, -1])),
            "edge_bump_equal": bool(np.array_equal(ba[0], ba[-1]) and np.array_equal(ba[:, 0], ba[:, -1]))}


def make_library(maps: dict) -> dict:
    sys.path.insert(0, str(GEN))
    import adsklib_gen as g
    reference = g.extract_params(str(TEMPLATE))
    kwargs = {k: v for k, v in reference.items() if k not in {
        "package_guid", "creator_guid", "created", "modified", "material_name", "description",
        "diffuse_path", "bump_path", "real_world_scale_in", "thumbnail_png_bytes", "_thumb_suffix_override"}}
    thumb = Image.open(TEX / "_REVIEW_eight_by_eight_hexes.png")
    thumb.thumbnail((512, 512), Image.Resampling.LANCZOS)
    import io
    s = io.BytesIO()
    thumb.save(s, format="PNG")
    kwargs.update(material_name=NAME, description="ELM Colorado Bruges Antique Exa stone-look hex mosaic; large seamless atlas; estimated grout and groove relief",
                  diffuse_path=str(maps["color"].resolve()), bump_path=str(maps["bump"].resolve()),
                  real_world_scale_in=ATLAS_IN, thumbnail_png_bytes=s.getvalue(), _template_path=str(TEMPLATE))
    candidate = OUT / "ELM_Bruges_Antique_Exa_R2025_candidate.adsklib"
    final = OUT / "ELM_Bruges_Antique_Exa_R2025_Rev4.adsklib"
    g.build_library(str(candidate), **kwargs)
    with zipfile.ZipFile(candidate) as z:
        if z.testzip():
            raise RuntimeError("candidate ADSKLIB ZIP integrity failed")
    readback = g.extract_params(str(candidate))
    if readback["material_name"] != NAME or any(abs(a - b) > .001 for a, b in zip(readback["real_world_scale_in"], ATLAS_IN)):
        raise RuntimeError("candidate ADSKLIB readback mismatch")
    if final.exists():
        raise RuntimeError("revision already exists; choose a new revision filename")
    shutil.copy2(candidate, final)
    return {"path": final, "sha256": digest(final), "readback": {k: readback[k] for k in ("material_name", "diffuse_path", "bump_path", "real_world_scale_in")}}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    maps = make_maps()
    if not maps["edge_color_equal"] or not maps["edge_bump_equal"]:
        raise RuntimeError("map boundary equality failed")
    lib = make_library(maps)
    report = {"material": NAME, "seed": SEED, "source_faces": 16, "atlas_pixels": [W, H],
              "atlas_inches": ATLAS_IN, "sheet_inches_landscape": [SHEET_W_IN, SHEET_H_IN],
              "hex_counts": maps["counts"], "unique_face_patches": maps["unique_patch_count"], "grout_step_mm_estimated": GROUT_STEP_MM,
              "groove_relief_mm_estimated": PATTERN_RELIEF_MM,
              "clearance_mm": GROUT_STEP_MM - PATTERN_RELIEF_MM - MICRO_RELIEF_MM,
              "map_edges_equal": {"color": maps["edge_color_equal"], "bump": maps["edge_bump_equal"]},
              "maps": {k: {"path": str(maps[k].relative_to(OUT)), "sha256": digest(maps[k])} for k in ("color", "bump")},
              "adsklib": {"path": lib["path"].name, "sha256": lib["sha256"], "readback": lib["readback"]}}
    (OUT / "technical_validation.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"atlas_pixels": [W, H], "hex_counts": maps["counts"], "library": str(lib["path"])}))


if __name__ == "__main__":
    main()
