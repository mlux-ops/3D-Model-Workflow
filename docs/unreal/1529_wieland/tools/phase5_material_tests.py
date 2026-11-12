"""Phase 5, step 5.8: the test table of the candidates.

    python -P -B phase5_material_tests.py <material_candidates.csv> <material_params.json> <ambientCG folder>
        <generated images folder> <candidate swatch folder> <largest_surfaces.json> <wrap preview folder>
        <material_tests.csv>

For every image a candidate uses it makes the repository's wrap preview: the
image laid 3 by 3, with the place where four copies meet cut out at full
size beside it. It measures the step across the wrapping edge against the
ordinary step between neighbouring pixels (the seam figure), and how uneven
the image is at large scale (the figure that makes a repeat easy to spot).
From the candidate's swatch picture it measures whether the relief shows on
the wall piece lit at a grazing angle. With the largest surface each
material covers in the model (measured in the editor) it then writes one
row per candidate. A finite image always repeats; the test is whether the
repeat is recognisable, not whether it exists.

Thresholds (this project's own, stated so that they can be argued with):
    seam figure      edge step / ordinary step, the worse of the two directions; pass at 2.0 or less
    large-scale      standard deviation of the image's brightness averaged in an 8 by 8 grid, over its mean;
    unevenness       0.05 or less counts as even
    grazing light    fine detail on the grazing-lit wall piece at least 0.010 (brightness 0 to 1)
"""

import csv
import json
import os
import re
import sys

import numpy as np
from PIL import Image

Image.MAX_IMAGE_PIXELS = None
SETS = ("Bricks086", "Carpet016", "Concrete046", "Fabric061", "Leather031", "Travertine009", "Wood049", "Wood090A",
        "WoodFloor051")
SUFFIX = {"C": "Color", "N": "NormalDX", "R": "Roughness"}
JOINTED = ("Bricks086", "WoodFloor051", "Tile24x12", "CMU", "Siding", "Reed", "CMU_Block", "Barham", "In_Situ",
           "Oak_Veneered", "Calacatta")


def slug(name):
    return re.sub(r"[^A-Za-z0-9_-]", "_", name)


def luminance(path, limit=2048):
    image = Image.open(path).convert("RGB")
    if max(image.size) > limit:
        scale = limit / float(max(image.size))
        image = image.resize((max(1, round(image.size[0] * scale)), max(1, round(image.size[1] * scale))), Image.BOX)
    data = np.asarray(image, dtype=np.float64) / 255.0
    return data @ np.array([0.2126, 0.7152, 0.0722]), image


def seam_figure(lum):
    figures = []
    for axis in (0, 1):
        moved = np.moveaxis(lum, axis, 0)
        inside = np.abs(np.diff(moved, axis=0)).mean()
        edge = np.abs(moved[0] - moved[-1]).mean()
        figures.append(edge / max(inside, 1e-4))
    return max(figures)


def unevenness(lum):
    rows = np.array_split(np.arange(lum.shape[0]), 8)
    cols = np.array_split(np.arange(lum.shape[1]), 8)
    cells = np.array([[lum[np.ix_(r, c)].mean() for c in cols] for r in rows])
    return float(cells.std() / max(cells.mean(), 1e-4))


def wrap_preview(image, out_path):
    """3 by 3 copies on the left, the four-way corner at full size on the right."""
    side = 300
    small = image.resize((side, max(1, round(side * image.size[1] / image.size[0]))), Image.LANCZOS)
    grid = Image.new("RGB", (small.size[0] * 3, small.size[1] * 3))
    for i in range(3):
        for j in range(3):
            grid.paste(small, (i * small.size[0], j * small.size[1]))
    crop = min(450, image.size[0], image.size[1])
    half = crop // 2
    corner = Image.new("RGB", (crop, crop))
    # the four quarters that meet where four copies touch
    w, h = image.size
    corner.paste(image.crop((w - half, h - half, w, h)), (0, 0))
    corner.paste(image.crop((0, h - half, crop - half, h)), (half, 0))
    corner.paste(image.crop((w - half, 0, w, crop - half)), (0, half))
    corner.paste(image.crop((0, 0, crop - half, crop - half)), (half, half))
    height = max(grid.size[1], 450)
    corner = corner.resize((450, 450), Image.NEAREST if crop < 200 else Image.LANCZOS)
    sheet = Image.new("RGB", (grid.size[0] + 450 + 30, height + 20), (24, 24, 24))
    sheet.paste(grid, (10, 10))
    sheet.paste(corner, (grid.size[0] + 20, 10))
    sheet.save(out_path, quality=85)


def detail(panel):
    """Fine detail: what is left after the slow change of light across the panel is taken out."""
    image = Image.fromarray(np.uint8(np.clip(panel, 0, 1) * 255))
    blurred = np.asarray(image.resize((max(1, image.size[0] // 16), max(1, image.size[1] // 16)), Image.BOX).resize(
        image.size, Image.BILINEAR), dtype=np.float64) / 255.0
    return float((panel - blurred).std())


def swatch_detail(path):
    if not os.path.exists(path):
        return None, None
    lum, _ = luminance(path, 4096)
    h, w = lum.shape
    front = lum[int(0.06 * h):int(0.60 * h), int(0.08 * w):int(0.42 * w)]
    graze = lum[int(0.06 * h):int(0.60 * h), int(0.58 * w):int(0.92 * w)]
    return detail(front), detail(graze)


def main(candidates_csv, params_json, sets_folder, generated_folder, swatch_folder, surfaces_json, preview_folder,
         out_csv):
    os.makedirs(preview_folder, exist_ok=True)
    with open(candidates_csv, encoding="utf-8", newline="") as handle:
        candidates = list(csv.DictReader(handle))
    with open(params_json, encoding="utf-8") as handle:
        params = json.load(handle)["materials"]
    with open(surfaces_json, encoding="utf-8") as handle:
        surfaces = json.load(handle)
    revit_files = {}
    for material in params.values():
        for texture in material["textures"].values():
            if texture and texture.get("source_file"):
                revit_files[texture["path"].split(".")[0]] = texture["source_file"]

    def file_of(asset):
        name = asset.rsplit("/", 1)[1]
        match = re.match(r"T_W1529_(.+)_([CNR])$", name)
        if match and match.group(1) in SETS:
            return os.path.join(sets_folder, match.group(1), "%s_2K-JPG_%s.jpg" % (match.group(1), SUFFIX[match.group(2)]))
        if name.startswith("T_W1529_"):
            return os.path.join(generated_folder, name + ".png")
        return revit_files.get(asset)

    measured = {}
    rows = []
    for row in candidates:
        textures = json.loads(row["textures"])
        scalars = json.loads(row["scalars"])
        switches = json.loads(row["switches"])
        seams, uneven, pixels, previews = [], None, None, []
        for key in sorted(textures):
            asset = textures[key]
            if asset not in measured:
                path = file_of(asset)
                if not path or not os.path.exists(path):
                    measured[asset] = None
                else:
                    lum, image = luminance(path)
                    preview = os.path.join(preview_folder, slug(asset.rsplit("/", 1)[1])[:90] + ".jpg")
                    wrap_preview(image, preview)
                    with Image.open(path) as original:
                        size = original.size
                    measured[asset] = {"seam": seam_figure(lum), "uneven": unevenness(lum), "size": size,
                                       "preview": os.path.basename(preview)}
            result = measured[asset]
            if result is None:
                seams.append(None)
                continue
            seams.append(result["seam"])
            previews.append(result["preview"])
            if key == "BaseColorMap":
                uneven, pixels = result["uneven"], result["size"]
            elif pixels is None:
                pixels = result["size"]
        surface = surfaces.get(row["material"], {})
        largest = surface.get("largest_m", [0.0, 0.0])
        size_u, size_v = scalars.get("SizeU_m"), scalars.get("SizeV_m")
        repeats = ""
        density = ""
        if textures and size_u and size_v:
            repeats = round(max(largest[0] / size_u, largest[1] / size_v), 1) if max(largest) > 0 else 0.0
            if pixels and "any" not in row["physical_field_size"]:
                density = round(pixels[0] / size_u)
        jointed = any(tag in " ".join(textures.values()) for tag in JOINTED)

        # tiling
        if not textures:
            tiling, tiling_pass = "No image: nothing to wrap or repeat.", True
        elif any(s is None for s in seams):
            tiling, tiling_pass = "An image file was not found for the test.", False
        else:
            worst = max(seams)
            seam_ok = worst <= 2.0
            anti = bool(switches.get("AntiRepeat"))
            if repeats != "" and repeats <= 1.0:
                repeat_ok, why = True, "the largest surface is no larger than one field"
            elif anti:
                repeat_ok, why = True, "the parent lays the image three ways and blends them, so no copy lines up"
            elif jointed and (uneven is None or uneven <= 0.05):
                repeat_ok, why = True, "joints repeat by design; the image is even at large scale"
            elif uneven is None or uneven <= 0.05:
                repeat_ok, why = True, "the image is even at large scale"
            else:
                repeat_ok, why = False, ("the image is uneven at large scale (%.3f) and is laid plainly, so the "
                                         "repeat can be recognised on a surface of %s fields" % (uneven, repeats))
            tiling_pass = seam_ok and repeat_ok
            tiling = "Seam figure %.2f (%s). Repeat: %s." % (worst, "passes" if seam_ok else "a visible seam", why)

        # grazing light
        front, graze = swatch_detail(os.path.join(swatch_folder, slug(row["material"]) + ".png"))
        has_relief = "NormalMap" in textures
        if row["parent"].endswith("Glass"):
            grazing, grazing_pass = "Glass: judged by eye on the sheet (see-through, reflection).", True
        elif graze is None:
            grazing, grazing_pass = "No swatch picture.", False
        elif not has_relief:
            grazing, grazing_pass = "Flat by design (no relief image); detail %.3f." % graze, True
        else:
            grazing_pass = graze >= 0.010
            grazing = "Relief detail %.3f under grazing light, %.3f lit from the front (%s)." % (
                graze, front, "reads" if grazing_pass else "does not read")
        rows.append({
            "material": row["material"],
            "candidate_asset": row["candidate_asset"],
            "source_and_licence": row["source_and_licence"],
            "physical_field_size": row["physical_field_size"],
            "image_pixels": "%d x %d" % pixels if pixels else "",
            "pixels_per_metre": density,
            "largest_surface_in_the_model_m": "%.2f x %.2f" % tuple(largest) if max(largest) > 0 else "not placed",
            "placed_objects_using_it": surface.get("objects", 0),
            "fields_across_the_largest_surface": repeats,
            "large_scale_unevenness": "" if uneven is None else round(uneven, 3),
            "tiling_result": tiling,
            "grazing_light_result": grazing,
            "passes": "yes" if (tiling_pass and grazing_pass) else "no",
            "wrap_previews": "; ".join(previews),
        })
    with open(out_csv, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    failed = [r["material"] for r in rows if r["passes"] == "no"]
    print("%d rows, %d pass, %d do not: %s" % (len(rows), len(rows) - len(failed), len(failed), failed))


if __name__ == "__main__":
    main(*sys.argv[1:9])
