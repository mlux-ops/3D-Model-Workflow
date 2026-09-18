from __future__ import annotations

import hashlib
import json
import pathlib
import sys
import zipfile

import numpy as np
from PIL import Image


ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "daltile_remedy_hydro"
TEX = OUT / "textures"
GEN = ROOT / "output" / "model-transfer-tests" / "candidate-20260918-01" / "material" / "adsklib_generator"
MANIFEST = OUT / "manifest.json"
REPORT = OUT / "technical_validation.json"


def sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def edge_stats(arr: np.ndarray) -> dict:
    a = arr.astype(np.float64)
    if a.ndim == 2:
        lr = np.abs(a[:, 0] - a[:, -1])
        tb = np.abs(a[0, :] - a[-1, :])
    else:
        lr = np.abs(a[:, 0, :] - a[:, -1, :])
        tb = np.abs(a[0, :, :] - a[-1, :, :])
    return {
        "left_right_max": float(lr.max()),
        "left_right_mean": float(lr.mean()),
        "top_bottom_max": float(tb.max()),
        "top_bottom_mean": float(tb.mean()),
    }


def tile_crop_hashes(arr: np.ndarray, cols: int, rows: int, tile_w_px: int, tile_h_px: int, module_w_px: float, module_h_px: float, grout_px: int) -> tuple[list[str], list[list[float]]]:
    hashes = []
    means = []
    for row in range(rows):
        for col in range(cols):
            x0 = round(col * module_w_px) + grout_px // 2
            y0 = round(row * module_h_px) + grout_px // 2
            x1 = min(arr.shape[1], x0 + tile_w_px)
            y1 = min(arr.shape[0], y0 + tile_h_px)
            crop = np.ascontiguousarray(arr[y0:y1, x0:x1])
            hashes.append(hashlib.sha256(crop.tobytes()).hexdigest())
            if crop.ndim == 3:
                means.append([float(x) for x in crop.reshape(-1, crop.shape[2]).mean(axis=0)])
            else:
                means.append([float(crop.mean())])
    return hashes, means


def main() -> None:
    m = json.loads(MANIFEST.read_text(encoding="utf-8"))
    paths = {k: OUT / v["path"] for k, v in m["maps"].items() if k in ("color", "bump", "normal", "roughness")}
    for p in paths.values():
        if not p.exists():
            raise FileNotFoundError(str(p))

    color_im = Image.open(paths["color"])
    bump_im = Image.open(paths["bump"])
    normal_im = Image.open(paths["normal"])
    rough_im = Image.open(paths["roughness"])
    color = np.asarray(color_im)
    bump = np.asarray(bump_im)
    normal = np.asarray(normal_im)
    rough = np.asarray(rough_im)

    expected_size = tuple(m["atlas_pixels"])
    decoded_sizes = {
        "color": list(color_im.size),
        "bump": list(bump_im.size),
        "normal": list(normal_im.size),
        "roughness": list(rough_im.size),
    }
    modes = {"color": color_im.mode, "bump": bump_im.mode, "normal": normal_im.mode, "roughness": rough_im.mode}
    size_pass = all(tuple(v) == expected_size for v in decoded_sizes.values())
    mode_pass = modes["color"] == "RGB" and modes["normal"] == "RGB" and modes["roughness"] == "L" and bump.dtype == np.uint16

    edge = {"color": edge_stats(color), "bump": edge_stats(bump), "normal": edge_stats(normal), "roughness": edge_stats(rough)}
    # The atlas intentionally carries half-grout at every outer edge. Exact matching
    # outermost pixels therefore verifies that periodic wrap does not introduce a seam.
    seam_pass = all(v["left_right_max"] == 0.0 and v["top_bottom_max"] == 0.0 for v in edge.values())

    ppi = expected_size[0] / m["atlas_size_in"][0]
    tile_w_px = round(m["nominal_size_in"][0] * ppi)
    tile_h_px = round(m["nominal_size_in"][1] * ppi)
    grout_px = max(1, round(m["grout_assumption_in"] * ppi))
    module_w_px = (m["nominal_size_in"][0] + m["grout_assumption_in"]) * ppi
    module_h_px = (m["nominal_size_in"][1] + m["grout_assumption_in"]) * ppi
    cols = round(m["atlas_size_in"][0] / (m["nominal_size_in"][0] + m["grout_assumption_in"]))
    rows = round(m["atlas_size_in"][1] / (m["nominal_size_in"][1] + m["grout_assumption_in"]))
    hashes, means = tile_crop_hashes(color, cols, rows, tile_w_px, tile_h_px, module_w_px, module_h_px, grout_px)
    unique_tiles = len(set(hashes))
    duplicate_count = len(hashes) - unique_tiles

    adjacent_exact_mean_matches = 0
    means_arr = np.asarray(means)
    for row in range(rows):
        for col in range(cols):
            i = row * cols + col
            if col + 1 < cols and np.allclose(means_arr[i], means_arr[i + 1], atol=1e-9):
                adjacent_exact_mean_matches += 1
            if row + 1 < rows and np.allclose(means_arr[i], means_arr[i + cols], atol=1e-9):
                adjacent_exact_mean_matches += 1
    variation_pass = duplicate_count == 0 and adjacent_exact_mean_matches == 0

    relief = m["relief"]
    expected_clearance = relief["grout_step_mm"] - relief["pattern_relief_mm"]
    relief_math_pass = abs(expected_clearance - relief["clearance_mm"]) < 1e-6 and relief["clearance_mm"] > 0.0
    bump_min = int(bump.min())
    bump_max = int(bump.max())
    bump_range_pass = bump_min == 0 and bump_max == 65535

    sys.path.insert(0, str(GEN))
    import adsklib_gen as g

    adsk_path = OUT / m["adsklib"]["path"]
    with zipfile.ZipFile(adsk_path) as zf:
        corrupt = zf.testzip()
        zip_entries = len(zf.namelist())
    readback = g.extract_params(str(adsk_path))
    diffuse_path = pathlib.Path(readback["diffuse_path"])
    bump_path = pathlib.Path(readback["bump_path"])
    adsk_pass = (
        corrupt is None
        and readback["material_name"] == m["material"]
        and tuple(round(x, 5) for x in readback["real_world_scale_in"]) == tuple(round(x, 5) for x in m["atlas_size_in"])
        and diffuse_path.exists()
        and bump_path.exists()
        and sha256(adsk_path) == m["adsklib"]["sha256"]
    )

    report = {
        "success": bool(size_pass and mode_pass and seam_pass and variation_pass and relief_math_pass and bump_range_pass and adsk_pass),
        "material": m["material"],
        "sku": m["sku"],
        "map_dimensions": decoded_sizes,
        "map_modes": modes,
        "map_registration_pass": bool(size_pass),
        "bit_depth_pass": bool(mode_pass),
        "edge_wrap": edge,
        "seam_pass": bool(seam_pass),
        "tile_modules": {"columns": cols, "rows": rows, "count": len(hashes), "unique_full_tile_crops": unique_tiles, "duplicate_full_tile_crops": duplicate_count, "adjacent_exact_mean_matches": adjacent_exact_mean_matches},
        "variation_pass": bool(variation_pass),
        "relief": {**relief, "computed_clearance_mm": expected_clearance, "bump_u16_min": bump_min, "bump_u16_max": bump_max, "pass": bool(relief_math_pass and bump_range_pass)},
        "adsklib": {
            "path": str(adsk_path),
            "sha256": sha256(adsk_path),
            "zip_entries": zip_entries,
            "zip_corrupt_entry": corrupt,
            "readback": {k: readback[k] for k in ("material_name", "description", "diffuse_path", "bump_path", "real_world_scale_in")},
            "bound_diffuse_exists": diffuse_path.exists(),
            "bound_bump_exists": bump_path.exists(),
            "pass": bool(adsk_pass),
        },
        "tested_surface": {
            "quantitative_wrap_test": "2 atlas repeats in each axis are implied by exact opposing-edge equality; visual multi-repeat review remains separate",
            "single_atlas_in": m["atlas_size_in"],
            "two_repeat_extent_in": [2 * m["atlas_size_in"][0], 2 * m["atlas_size_in"][1]],
        },
        "visual_gates": {
            "grazing_light_relief": "pending - no image/desktop review tool is available in this Zero Risk retry",
            "room_view_repetition": "pending - no image/desktop review tool is available in this Zero Risk retry",
            "revit_material_browser_library_open": "pending native UI check; archive/readback and Revit-bound maps are validated separately",
        },
    }
    REPORT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    if not report["success"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
