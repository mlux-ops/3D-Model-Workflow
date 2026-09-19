"""Build deterministic, source-derived ELM Almond PBR texture atlases.

This is numerical material construction, not a native renderer.  The default
source face is the supplied flat official face.  The supplied lifestyle images
are inventory-only references and are never sampled.  A user-supplied
generated continuous albedo may be added explicitly with --generated-source.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
from PIL import Image, ImageFilter, ImageOps


SEED = 20260918
INCHES_PER_FOOT = 12.0
MM_PER_INCH = 25.4


@dataclass(frozen=True)
class MaterialSpec:
    material_id: str
    label: str
    tile_w_in: float
    tile_h_in: float
    grout_in: float
    tile_count_x: int
    tile_count_y: int
    pattern: str

    @property
    def pitch_w_in(self) -> float:
        return self.tile_w_in + self.grout_in

    @property
    def pitch_h_in(self) -> float:
        return self.tile_h_in + self.grout_in

    @property
    def extent_in(self) -> tuple[float, float]:
        return (self.tile_count_x * self.pitch_w_in, self.tile_count_y * self.pitch_h_in)


SPECS = (
    MaterialSpec("elm_almond_mosaic_2x2", "2 x 2 inch mosaic", 2.0, 2.0, 1.0 / 16.0, 96, 96, "mosaic"),
    MaterialSpec("elm_almond_flat_12x24", "12 x 24 inch flat", 24.0, 12.0, 1.0 / 16.0, 8, 16, "flat"),
    MaterialSpec("elm_almond_fluted_12x24", "12 x 24 inch fluted", 24.0, 12.0, 1.0 / 16.0, 8, 16, "fluted"),
)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def relpath(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def load_rgb(path: Path) -> np.ndarray:
    return np.asarray(Image.open(path).convert("RGB"), dtype=np.float32) / 255.0


def save_rgb(path: Path, image: np.ndarray) -> None:
    Image.fromarray(np.clip(image * 255.0 + 0.5, 0, 255).astype(np.uint8), "RGB").save(path, optimize=False)


def save_gray8(path: Path, image: np.ndarray) -> None:
    Image.fromarray(np.clip(image * 255.0 + 0.5, 0, 255).astype(np.uint8), "L").save(path, optimize=False)


def save_height16(path: Path, height_mm: np.ndarray, low_mm: float, high_mm: float) -> None:
    encoded = np.clip((height_mm - low_mm) / (high_mm - low_mm), 0.0, 1.0)
    Image.fromarray(np.round(encoded * 65535.0).astype(np.uint16), "I;16").save(path, optimize=False)


def resize_array(image: np.ndarray, size: tuple[int, int]) -> np.ndarray:
    pil = Image.fromarray(np.clip(image * 255.0 + 0.5, 0, 255).astype(np.uint8), "RGB")
    return np.asarray(pil.resize(size, Image.Resampling.LANCZOS), dtype=np.float32) / 255.0


def source_inventory(ref_dir: Path) -> list[dict]:
    rows: list[dict] = []
    for path in sorted(ref_dir.iterdir()):
        if path.suffix.lower() not in {".jpg", ".jpeg", ".webp", ".png"}:
            continue
        with Image.open(path) as im:
            size = list(im.size)
        name = path.name.lower()
        if path.name == "almond_main.jpg":
            role, included, reason = "official_flat_face", True, "official flat face source"
        elif path.name == "generated_continuous_albedo.png":
            role, included, reason = "user_supplied_generated_albedo", False, "optional only; excluded from default matching"
        elif path.name == "683124287cce7c270f37b4c2_almond main.jpg":
            role, included, reason = "official_flat_face_duplicate", False, "duplicate of almond_main.jpg; not sampled twice"
        elif "flute" in name:
            role, included, reason = "official_flute_lifestyle_reference", False, "scene reference; orientation and relief only"
        elif "palace" in name:
            role, included, reason = "other_product_lifestyle_reference", False, "Palace Royale scene; not ELM Almond"
        elif "almond" in name and path.suffix.lower() == ".webp":
            role, included, reason = "official_lifestyle_reference", False, "lifestyle scene; not a face crop"
        else:
            role, included, reason = "unclassified", False, "not selected by the default source policy"
        rows.append({"path": relpath(path, ref_dir.parent.parent), "filename": path.name, "size_px": size,
                     "role": role, "included_by_default": included, "reason": reason})
    return rows


def crop_pool(source: np.ndarray, aspect: float, count: int, seed: int) -> list[np.ndarray]:
    """Make genuinely different spatial crops; no rotations, mirrors, or tint-only variants."""
    h, w = source.shape[:2]
    margin_x, margin_y = max(2, int(w * 0.035)), max(2, int(h * 0.035))
    usable_w, usable_h = w - 2 * margin_x, h - 2 * margin_y
    if usable_w / usable_h >= aspect:
        crop_h = usable_h
        crop_w = max(8, int(round(crop_h * aspect)))
    else:
        crop_w = usable_w
        crop_h = max(8, int(round(crop_w / aspect)))
    xs = np.linspace(margin_x, w - margin_x - crop_w, 8).round().astype(int)
    ys = np.linspace(margin_y, h - margin_y - crop_h, 8).round().astype(int)
    candidates = [(int(x), int(y)) for y in ys for x in xs]
    order = sorted(range(len(candidates)), key=lambda i: ((i * 2654435761 + seed) & 0xFFFFFFFF))
    selected = [candidates[i] for i in order[: min(count, len(order))]]
    out: list[np.ndarray] = []
    for x, y in selected:
        out.append(source[y:y + crop_h, x:x + crop_w].copy())
    return out


def patch_height(patch: np.ndarray, size: tuple[int, int], amplitude_mm: float) -> np.ndarray:
    gray = np.asarray(Image.fromarray(np.clip(patch * 255 + 0.5, 0, 255).astype(np.uint8), "RGB").convert("L"), dtype=np.float32) / 255.0
    base = Image.fromarray(np.clip(gray * 255 + 0.5, 0, 255).astype(np.uint8), "L")
    blur = np.asarray(base.filter(ImageFilter.GaussianBlur(radius=max(1.0, min(gray.shape) / 22.0))), dtype=np.float32) / 255.0
    detail = gray - blur
    detail -= float(np.mean(detail))
    scale = float(np.max(np.abs(detail))) or 1.0
    detail = detail / scale
    detail = np.asarray(Image.fromarray(np.clip((detail * 0.5 + 0.5) * 255, 0, 255).astype(np.uint8), "L").resize(size, Image.Resampling.LANCZOS), dtype=np.float32) / 255.0
    detail = (detail - 0.5) * 2.0
    return detail * amplitude_mm


def make_rib_height(size: tuple[int, int], seed: int) -> np.ndarray:
    w, h = size
    yy = (np.arange(h, dtype=np.float32) + 0.5) / h
    xx = (np.arange(w, dtype=np.float32) + 0.5) / w
    rng = np.random.default_rng(seed)
    centers = (np.arange(12, dtype=np.float32) + 0.5) / 12.0
    centers += rng.uniform(-0.017, 0.017, size=12).astype(np.float32)
    widths = rng.uniform(0.025, 0.043, size=12).astype(np.float32)
    profile = np.zeros(h, dtype=np.float32)
    for center, width in zip(centers, widths):
        d = (yy - center + 0.5) % 1.0 - 0.5
        profile = np.maximum(profile, np.exp(-0.5 * (d / width) ** 2))
    # Very low-frequency along-rib variation keeps the pattern irregular without
    # breaking the intended long-axis direction.
    along = 0.96 + 0.04 * np.sin(xx * math.tau * 1.7 + seed * 0.013)
    pattern = profile[:, None] * along[None, :]
    pattern = (pattern - float(pattern.min())) / max(float(pattern.max() - pattern.min()), 1e-6)
    return pattern.astype(np.float32)


def normal_from_height(height_mm: np.ndarray, extent_in: tuple[float, float]) -> np.ndarray:
    px_mm_x = extent_in[0] * MM_PER_INCH / height_mm.shape[1]
    px_mm_y = extent_in[1] * MM_PER_INCH / height_mm.shape[0]
    dx = (np.roll(height_mm, -1, axis=1) - np.roll(height_mm, 1, axis=1)) / (2.0 * px_mm_x)
    dy = (np.roll(height_mm, -1, axis=0) - np.roll(height_mm, 1, axis=0)) / (2.0 * px_mm_y)
    nx, ny, nz = -dx, -dy, np.ones_like(height_mm)
    norm = np.sqrt(nx * nx + ny * ny + nz * nz)
    nx, ny, nz = nx / norm, ny / norm, nz / norm
    return np.stack((nx * 0.5 + 0.5, ny * 0.5 + 0.5, nz * 0.5 + 0.5), axis=2).astype(np.float32)


def render_grazing(diffuse: np.ndarray, normal: np.ndarray) -> np.ndarray:
    n = normal * 2.0 - 1.0
    light = np.array([0.72, -0.58, 0.42], dtype=np.float32)
    light /= np.linalg.norm(light)
    lambert = np.maximum(np.sum(n * light[None, None, :], axis=2), 0.0)
    shade = 0.20 + 0.80 * lambert
    return np.clip(diffuse * shade[:, :, None], 0.0, 1.0)


def preview_3x3(image: np.ndarray, out_path: Path, size: int = 1024) -> None:
    thumb = resize_array(image, (size // 3, size // 3))
    tiled = np.tile(thumb, (3, 3, 1))
    save_rgb(out_path, tiled)


def edge_stats(array: np.ndarray) -> dict:
    if array.ndim == 3:
        a = np.mean(array, axis=2)
    else:
        a = array
    return {
        "left_right_mean_abs_delta": float(np.mean(np.abs(a[:, 0] - a[:, -1]))),
        "top_bottom_mean_abs_delta": float(np.mean(np.abs(a[0, :] - a[-1, :]))),
        "corner_values": [float(a[0, 0]), float(a[0, -1]), float(a[-1, 0]), float(a[-1, -1])],
        "note": "edge differences include intentional grout at the atlas perimeter; periodic derivatives use np.roll",
    }


def tile_hashes(diffuse: np.ndarray, spec: MaterialSpec, extent_in: tuple[float, float]) -> dict:
    px_per_in_x = diffuse.shape[1] / extent_in[0]
    px_per_in_y = diffuse.shape[0] / extent_in[1]
    hashes: list[str] = []
    for row in range(spec.tile_count_y):
        y0 = round(row * spec.pitch_h_in * px_per_in_y)
        y1 = round((row * spec.pitch_h_in + spec.tile_h_in) * px_per_in_y)
        for col in range(spec.tile_count_x):
            x0 = round(col * spec.pitch_w_in * px_per_in_x)
            x1 = round((col * spec.pitch_w_in + spec.tile_w_in) * px_per_in_x)
            crop = Image.fromarray(np.clip(diffuse[y0:y1, x0:x1] * 255 + 0.5, 0, 255).astype(np.uint8), "RGB").resize((16, 16), Image.Resampling.BILINEAR)
            hashes.append(hashlib.sha256(crop.tobytes()).hexdigest()[:16])
    adjacent = sum(hashes[i] == hashes[i + 1] for i in range(len(hashes) - 1))
    return {"tile_instances": len(hashes), "unique_interior_tile_hashes": len(set(hashes)), "adjacent_duplicate_pairs": adjacent}


def build_material(spec: MaterialSpec, out_dir: Path, sources: list[np.ndarray], source_labels: list[str], pixels: int, seed: int) -> dict:
    extent_in = spec.extent_in
    px_per_in_x, px_per_in_y = pixels / extent_in[0], pixels / extent_in[1]
    diffuse = np.zeros((pixels, pixels, 3), dtype=np.float32)
    roughness = np.full((pixels, pixels), 0.72, dtype=np.float32)
    height = np.full((pixels, pixels), -1.0, dtype=np.float32)
    source_pools = [crop_pool(src, spec.tile_w_in / spec.tile_h_in, 32, seed + i * 101) for i, src in enumerate(sources)]
    all_patches: list[np.ndarray] = [patch for pool in source_pools for patch in pool]
    patch_labels: list[str] = [label for label, pool in zip(source_labels, source_pools) for _ in pool]
    if not all_patches:
        raise RuntimeError("No usable source face crops were produced")
    patch_cache: dict[tuple[int, int, int], np.ndarray] = {}
    patch_height_cache: dict[tuple[int, int, int], np.ndarray] = {}
    used_indices: list[int] = []

    for row in range(spec.tile_count_y):
        y0 = round(row * spec.pitch_h_in * px_per_in_y)
        y1 = round((row * spec.pitch_h_in + spec.tile_h_in) * px_per_in_y)
        for col in range(spec.tile_count_x):
            x0 = round(col * spec.pitch_w_in * px_per_in_x)
            x1 = round((col * spec.pitch_w_in + spec.tile_w_in) * px_per_in_x)
            tw, th = max(1, x1 - x0), max(1, y1 - y0)
            index = (row * 37 + col * 61 + (0 if spec.pattern == "mosaic" else 17)) % len(all_patches)
            used_indices.append(index)
            key = (index, tw, th)
            if key not in patch_cache:
                patch_cache[key] = resize_array(all_patches[index], (tw, th))
                amp = 0.12 if spec.pattern != "fluted" else 0.04
                patch_height_cache[key] = patch_height(all_patches[index], (tw, th), amp)
            diffuse[y0:y1, x0:x1] = patch_cache[key]
            if spec.pattern == "fluted":
                rib = make_rib_height((tw, th), seed + row * 131 + col * 977)
                # Peak is 1.2 mm. The grout floor is 1.0 mm below the tile base,
                # so the 2.2 mm peak-to-grout step leaves 1.0 mm clearance.
                height[y0:y1, x0:x1] = rib * 1.2
                roughness[y0:y1, x0:x1] = 0.58 + 0.05 * (1.0 - rib)
            else:
                height[y0:y1, x0:x1] = patch_height_cache[key]
                roughness[y0:y1, x0:x1] = 0.62 + 0.06 * (0.5 - np.mean(patch_cache[key], axis=2))

    # Encode intentional grout only after all tile faces are filled, preserving
    # exact registered maps and a common physical coordinate system.
    normal = normal_from_height(height, extent_in)
    safe = spec.material_id
    paths = {
        "diffuse": out_dir / f"{safe}_diffuse.png",
        "height16": out_dir / f"{safe}_height16.png",
        "bump16": out_dir / f"{safe}_bump16.png",
        "normal_opengl": out_dir / f"{safe}_normal_opengl.png",
        "roughness": out_dir / f"{safe}_roughness.png",
        "preview_3x3": out_dir / f"{safe}_preview_3x3.png",
        "grazing_diagnostic": out_dir / f"{safe}_grazing_lambertian_diagnostic.png",
    }
    save_rgb(paths["diffuse"], diffuse)
    save_height16(paths["height16"], height, -1.0, 1.2)
    save_height16(paths["bump16"], height, -1.0, 1.2)
    save_rgb(paths["normal_opengl"], normal)
    save_gray8(paths["roughness"], roughness)
    preview_3x3(diffuse, paths["preview_3x3"])
    preview_3x3(render_grazing(diffuse, normal), paths["grazing_diagnostic"])

    unique = tile_hashes(diffuse, spec, extent_in)
    file_records = {}
    for key, path in paths.items():
        file_records[key] = {"path": path.name, "sha256": sha256(path), "bytes": path.stat().st_size}
    return {
        "id": spec.material_id,
        "label": spec.label,
        "tile_size_in": [spec.tile_w_in, spec.tile_h_in],
        "orientation": "landscape_24x12" if spec.tile_w_in > spec.tile_h_in else "square",
        "layout": "stacked_aligned",
        "pattern": spec.pattern,
        "grout_width_in": spec.grout_in,
        "grout_width_mm": spec.grout_in * MM_PER_INCH,
        "tile_count": [spec.tile_count_x, spec.tile_count_y],
        "physical_extent_in": list(extent_in),
        "physical_extent_ft": [extent_in[0] / 12.0, extent_in[1] / 12.0],
        "map_resolution_px": [pixels, pixels],
        "pixels_per_inch": [px_per_in_x, px_per_in_y],
        "registered_map_scale_in_per_px": [1.0 / px_per_in_x, 1.0 / px_per_in_y],
        "source_face_count": len(sources),
        "source_crop_count": len(all_patches),
        "source_crop_labels": sorted(set(patch_labels)),
        "variation_method": "deterministic_spatial_crops; no rotations, mirrors, or tint-only variants",
        "maps": file_records,
        "validation": {
            "unique_interiors": unique,
            "wrapped_boundary_statistics": {
                "diffuse": edge_stats(diffuse),
                "height_mm": edge_stats(height),
                "normal_opengl": edge_stats(normal),
                "roughness": edge_stats(roughness),
            },
            "periodic_derivatives": True,
            "visual_3x3_preview": "generated; illustrative bitmap inspection only",
            "grazing_lambertian_diagnostic": "generated; not a native render",
            "native_render": "pending",
            "native_application_binding": "pending",
            "seamless_visual_gate": "pending",
            "non_repetition_visual_gate": "pending",
        },
    }


def write_readme(path: Path, manifest: dict) -> None:
    lines = [
        "# ELM Almond texture set",
        "",
        "Deterministic source-derived PBR atlases for the authorized 2 x 2 inch mosaic, 12 x 24 inch flat, and 12 x 24 inch fluted materials.",
        "",
        "## Contents",
        "",
        "- Each material has registered diffuse, 16-bit height, 16-bit bump, OpenGL normal, and roughness maps.",
        "- Each atlas is at least 16 x 16 ft physically and uses exact tile-plus-grout dimensions recorded in `manifest.json`.",
        "- `*_preview_3x3.png` and `*_grazing_lambertian_diagnostic.png` are illustrative numerical diagnostics, not native Revit or renderer output.",
        "",
        "## Source policy",
        "",
        "The default face source is the official `references/elm_almond/almond_main.jpg`. The eight numbered Almond WEBPs were inspected as lifestyle scenes and are excluded from sampling; Palace is a different product scene; Flute is used only as a dimensional/orientation reference. The default build therefore has one genuine official face and many deterministic spatial crops, which is a documented source limitation rather than a claim of multiple product faces.",
        "",
        "Pass `--generated-source references/elm_almond/generated_continuous_albedo.png` to add the user-supplied continuous albedo as an explicit secondary color/crop source. It is excluded from the default source-face matching.",
        "",
        "## Fluted relief",
        "",
        "The fluted map uses twelve irregular horizontal rib bands across the 12 inch short axis of each landscape 24 x 12 inch tile. Pattern relief is 1.2 mm. The encoded grout floor is 1.0 mm below the tile base, making the peak-to-grout step 2.2 mm and leaving 1.0 mm clearance above the grout floor. Relief must still be reviewed under grazing light in the native application.",
        "",
        "## Acceptance status",
        "",
        "Hash, source registration, unique-interior, and wrapped-boundary statistics are recorded in `manifest.json`. Native Revit binding, native render, seamless visual review, and non-repetition visual review are pending. No ADSKLIB is included or claimed.",
        "",
        f"Build seed: `{manifest['build']['seed']}`; map axis: `{manifest['build']['pixels']} px`; build source mode: `{manifest['build']['source_mode']}`.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--generated-source", type=Path, default=None, help="Optional user-supplied continuous albedo source")
    parser.add_argument("--pixels", type=int, default=4096, help="Map axis resolution; default 4096")
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()
    if args.pixels < 2048 or args.pixels > 6144:
        parser.error("--pixels must be between 2048 and 6144")

    root = Path(__file__).resolve().parents[1]
    ref_dir = root / "references" / "elm_almond"
    out_dir = args.output.resolve() if args.output else root / "output" / "elm_almond_textures"
    out_dir.mkdir(parents=True, exist_ok=True)
    for child in list(out_dir.iterdir()):
        if child.is_file():
            child.unlink()
        elif child.is_dir():
            shutil.rmtree(child)

    official = ref_dir / "almond_main.jpg"
    if not official.exists():
        raise FileNotFoundError(f"Required official face source not found: {official}")
    sources = [load_rgb(official)]
    source_labels = [relpath(official, root)]
    generated_info = {"path": relpath(ref_dir / "generated_continuous_albedo.png", root), "included_by_default": False,
                      "included_this_build": False, "reason": "optional explicit source; excluded from default source-face matching"}
    if args.generated_source is not None:
        generated = args.generated_source if args.generated_source.is_absolute() else (root / args.generated_source)
        if not generated.exists():
            raise FileNotFoundError(f"Generated source does not exist: {generated}")
        sources.append(load_rgb(generated))
        source_labels.append(relpath(generated, root))
        generated_info.update({"path": relpath(generated, root), "included_this_build": True})

    manifest = {
        "schema_version": "1.0",
        "material_id": "ELM_Almond",
        "build": {"script": relpath(Path(__file__).resolve(), root), "seed": args.seed, "pixels": args.pixels,
                  "source_mode": "official_face_only" if len(sources) == 1 else "official_face_plus_explicit_generated_albedo",
                  "coordinate_convention": "u=map x/right, v=map y/down; registered map scale is per-axis"},
        "source_set": {"official_faces": source_inventory(ref_dir), "generated_source": generated_info,
                       "sampled_source_labels": source_labels},
        "materials": [],
        "limitations": [
            "Only one genuine official flat face was suitable for sampling; the other numbered Almond WEBPs are lifestyle scenes.",
            "Spatial crops are source-derived but do not constitute multiple independent product faces; non-repetition visual acceptance is pending.",
            "No native Revit or renderer validation was performed by this script.",
            "No ADSKLIB was created.",
        ],
    }
    for spec in SPECS:
        manifest["materials"].append(build_material(spec, out_dir, sources, source_labels, args.pixels, args.seed))

    for material in manifest["materials"]:
        for rec in material["maps"].values():
            rec["path"] = relpath(out_dir / rec["path"], out_dir)
    manifest_path = out_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    write_readme(out_dir / "README.md", manifest)
    print(json.dumps({"output": str(out_dir), "manifest": str(manifest_path), "materials": [m["id"] for m in manifest["materials"]]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
