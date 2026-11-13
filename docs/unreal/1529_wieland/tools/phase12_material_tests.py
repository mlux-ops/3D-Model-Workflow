"""Phase 12, step 12.5: the tests of step 5.8 on the rebuilt materials.

    python -P -B phase12_material_tests.py <recipes.json> <uses.json> <rebuilt swatch folder>
                                           <wrap preview folder> <tests.json> [<relief.json>]

The measures and thresholds are those of Phase 5 (phase5_material_tests.py), so that the two tables
can be read side by side:

    seam figure            step across the wrapping edge over the strongest step between two neighbouring
                           lines of pixels inside the image; pass at 1.5 or less
    large-scale unevenness standard deviation of the brightness in an 8 by 8 grid over its mean; 0.05 or
                           less counts as even
    grazing light          fine detail on the wall piece lit at a grazing angle at least 0.010

For every image a recipe names it writes the wrap preview (the image laid 3 by 3 and the place where four
copies meet at full size). The result goes to tests.json as {material: {column: value}}, which
phase12_recipes.py merges into material_rebuild.csv. relief.json, when given, holds measured relief
depths in millimetres ({material: {"depth_mm": ..., "how": ...}}) for sculpted tile.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import phase5_material_tests as p5
from PIL import Image

# Relief made by this phase that is finer than one pixel of the swatch picture (about 2.5 mm on the wall
# piece): it shapes the highlight and does not show as a pattern, so the detail threshold does not apply.
FINE_RELIEF = {"T_W1529_P12_Eggshell_N": "roller stipple, bumps of about 3 mm",
               "T_W1529_P12_Brushed_N": "brushed scratches of about 0.3 mm",
               # Finishes that are smooth in reality. Their relief image is used at the strength it was
               # photographed or exported with; making it stronger until it passed would show a surface
               # the finish does not have.
               "T_W1529_P12_OakVeneer02_N": "the open pores of sanded, sealed oak veneer, well under 1 mm, as scanned by Poly Haven",
               "T_W1529_P12_AshVeneer_N": "the open pores of sanded, sealed ash veneer, well under 1 mm, as scanned by Poly Haven",
               "T_W1529_P12_WhiteMapleVeneer_N": "the pores of sanded, sealed maple veneer, well under 1 mm, as scanned by Poly Haven",
               "INDIANA-LIMESTONE-FULL-COLOR-BLENDtm-Tranche-1-001-BUMP-16K":
                   "the smooth machine finish of cut limestone, from the Revit export's own relief image at 0.3 strength"}
# Finishes whose joints repeat by design.
JOINTED_FAMILIES = ("tile", "masonry", "brick", "siding")
JOINTED_NAMES = ("Tile", "Kit_Kat", "Larvikite", "Siding", "CMU", "Brick", "Limestone", "Paver", "Plank", "Stack")


def main(recipes_json, uses_json, swatch_folder, preview_folder, out_json, relief_json=None):
    os.makedirs(preview_folder, exist_ok=True)
    with open(recipes_json, encoding="utf-8") as handle:
        recipes = json.load(handle)["rebuild"]
    with open(uses_json, encoding="utf-8") as handle:
        uses = json.load(handle)
    relief = {}
    if relief_json and os.path.exists(relief_json):
        with open(relief_json, encoding="utf-8") as handle:
            relief = json.load(handle)
    measured, result = {}, {}
    for recipe in recipes:
        name, textures, scalars, switches = recipe["material"], recipe["textures"], recipe["scalars"], recipe["switches"]
        parent = recipe["parent"].rsplit("_", 1)[-1]
        seams, uneven, pixels, previews = [], None, None, []
        for key in sorted(textures):
            asset, path = textures[key], recipe["files"].get(key, "")
            if asset not in measured:
                if not path or not os.path.exists(path):
                    measured[asset] = None
                else:
                    lum, image = p5.luminance(path)
                    preview = os.path.join(preview_folder, p5.slug(asset.rsplit("/", 1)[1])[:90] + ".jpg")
                    p5.wrap_preview(image, preview)
                    with Image.open(path) as original:
                        size = original.size
                    measured[asset] = {"seam": p5.seam_figure(lum), "uneven": p5.unevenness(lum), "size": size,
                                       "preview": os.path.basename(preview)}
            found = measured[asset]
            if found is None:
                seams.append(None)
                continue
            seams.append(found["seam"])
            previews.append(found["preview"])
            if key == "BaseColorMap":
                uneven, pixels = found["uneven"], found["size"]
        use = uses.get(name, {})
        largest = use.get("largest_m", [0.0, 0.0])
        size_u, size_v = scalars.get("SizeU_m"), scalars.get("SizeV_m")
        repeats, density = "", ""
        if textures and size_u and size_v:
            repeats = round(max(largest[0] / size_u, largest[1] / size_v), 1) if max(largest) > 0 else 0.0
            if pixels:
                density = round(pixels[0] / size_u)
        jointed = recipe["family"] in JOINTED_FAMILIES or any(tag in name for tag in JOINTED_NAMES)

        # tiling
        if not textures:
            tiling, tiling_pass = "No image: nothing to wrap or repeat.", True
        elif any(seam is None for seam in seams):
            tiling, tiling_pass = "An image file was not found for the test.", False
        else:
            worst = max(seams)
            seam_ok = worst <= 1.5
            if repeats != "" and repeats <= 1.0:
                repeat_ok, why = True, "the largest surface is no larger than one field"
            elif switches.get("AntiRepeat"):
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
        front, graze = p5.swatch_detail(os.path.join(swatch_folder, p5.slug(name) + ".png"))
        relief_image = textures.get("NormalMap", "").rsplit("/", 1)[-1]
        if graze is None:
            grazing, grazing_pass = "No swatch picture.", False
        elif parent == "Glass":
            grazing, grazing_pass = "Glass: judged by eye on the sheet (see-through, reflection).", True
        elif parent == "Emissive":
            grazing, grazing_pass = ("A surface that gives off light: on the swatch stage, whose exposure is fixed for "
                                     "unlit finishes, it shows white or near white; judged in the scene pictures."), True
        elif not relief_image:
            grazing, grazing_pass = "Flat by design (no relief image); detail %.3f." % graze, True
        elif relief_image in FINE_RELIEF:
            grazing, grazing_pass = ("Fine relief by design (%s), finer than one pixel of the swatch picture: it shapes "
                                     "the highlight and is judged by eye on the sheet; detail %.3f under grazing light, "
                                     "%.3f lit from the front." % (FINE_RELIEF[relief_image], graze, front)), True
        else:
            grazing_pass = graze >= 0.010
            grazing = "Relief detail %.3f under grazing light, %.3f lit from the front (%s)." % (
                graze, front, "reads" if grazing_pass else "does not read")
        if name in relief:
            grazing += " Relief depth %.1f mm (%s)." % (relief[name]["depth_mm"], relief[name]["how"])
        result[name] = {
            "image_pixels": "%d x %d" % pixels if pixels else "",
            "pixels_per_metre": density,
            "fields_across_the_largest_surface": repeats,
            "large_scale_unevenness": "" if uneven is None else round(uneven, 3),
            "tiling_result": tiling,
            "grazing_light_result": grazing,
            "passes": "yes" if (tiling_pass and grazing_pass) else "no",
            "wrap_previews": "; ".join(previews),
        }
    with open(out_json, "w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=1, sort_keys=True)
    failed = sorted(name for name, row in result.items() if row["passes"] == "no")
    print("%d materials, %d pass, %d do not: %s" % (len(result), len(result) - len(failed), len(failed), failed))


if __name__ == "__main__":
    main(*sys.argv[1:7])
