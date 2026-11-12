"""Phase 5, step 5.0: score how faithfully each exported Revit material shows its finish.

Usage:
    python -B phase5_score.py <material_audit.csv> <material_params.json>

Reads the audit table and the parameters that wieland_materials.dump_params()
read from the editor, sorts every material into a family, and writes three
columns into the audit table: family, confidence (1 to 5) and
confidence_reason. The column decision is the owner's and is left alone.

The figure says how faithfully the exported material shows the finish its name
specifies, judged from what was exported (colour, gloss, images, their pixel
size and their size on the wall). No material was compared with a sample or a
photograph, so 5 is given only to objects that are not finishes at all.

    1  wrong or missing: Revit's default grey, a missing image, or an image of
       another finish
    2  the finish has a pattern or a sheen that the material does not show
    3  plausible, with a named weakness (repeat, coarse image, flat glass)
    4  plain finish with its colour and gloss stated, or a sharp image at scale
    5  not a finish (a marker object); nothing to judge
"""

import csv
import json
import sys

FOOT_M = 0.3048
LARGE = ("Walls", "Floors", "Ceilings", "Roofs", "Site", "Runs", "Landings")
PATTERNED = ("wood", "stone", "masonry", "concrete", "tile", "fabric")

# (family, keywords); the first family with a keyword in the name wins.
NAME_FAMILIES = (
    ("marker", ("generic_clearance", "generic_warning", "z_miele_connection", "air_-_clear", "cinemat")),
    ("placeholder", ("default", "rnt_material", "render_material", "01_cabinets")),
    ("siding", ("siding",)),
    # Names whose later words would send them to the wrong family: Ultrex is a
    # fibreglass frame ("Stonewhite" is its colour), a laminate named "Linen"
    # is still a laminate, and "textile" contains "tile".
    ("plastic", ("ultrex", "laminate")),
    ("fabric", ("textile",)),
    ("glass", ("glass", "glazing", "acrylic_lens", "opalwhite", "frosted", "study_pane")),
    ("masonry", ("brick", "cmu", "masonry_units", "barham")),
    ("stone", ("limestone", "quartzite", "calacatta", "larvikite", "travertine", "marble", "alabaster",
               "countertop", "counter_top", "stone", "terrazzo")),
    ("tile", ("tile", "kit_kat")),
    ("concrete", ("concrete", "microcement")),
    ("ceramic", ("vitreous", "china", "porcelain", "lithocast", "ceramic", "terracotta")),
    ("wood", ("wood", "oak", "teak", "birch", "cedar", "maple", "veneer", "douglas_fir", "carpentry", "mdf",
              "beechwood")),
    ("fabric", ("fabric", "textile", "linen", "upholstery", "rug_", "leather", "shoes")),
    ("metal", ("metal", "chrome", "steel", "alumin", "alminium", "brass", "nickel", "inox", "bronze", "cromo",
               "zinc", "stainless", "gold", "plating")),
    ("paint", ("gypsum", "paint", "drywall", "white_dove", "trim", "soffit", "ral", "parking_stripe")),
    ("plastic", ("plastic", "laminate", "vinyl", "acrylic", "rubber", "silicone", "epp_", "ultrex", "hewi")),
)

# The same for image names. Autodesk's library names every wood and laminate
# image "Woods___Plastics_Finish_Carpentry_...", so the word after
# "Carpentry" decides, and it is looked at first.
IMAGE_FAMILIES = (
    ("wood", ("carpentry_wood",)),
    ("plastic", ("carpentry_plas",)),
    ("asphalt", ("asphalt",)),
    ("stone", ("masonry_stone", "limestone", "quartzite", "calacatta", "larvikite", "travertine")),
    ("masonry", ("brick", "cmu")),
    ("concrete", ("concrete", "microcement")),
    ("paint", ("gypsum",)),
    ("glass", ("glass",)),
    ("fabric", ("fabric", "linen")),
    ("tile", ("tile", "kit_kat")),
    ("wood", ("wood", "oak", "teak", "veneer", "mdf")),
    ("metal", ("metal", "alumin")),
)

COATED = ("matte", "black", "white", "powder", "paint", "anthracite", "pebblegray", "stonewhite")


def _family(text, table):
    text = text.lower()
    for family, words in table:
        if any(word in text for word in words):
            return family
    return None


def _ash(name):
    return name.lower() == "ash"


def _real_image(texture):
    """True for an image that is more than a plain colour chip."""
    if not texture:
        return False
    path = texture["path"]
    if "/Engine/" in path:
        return False
    return max(texture.get("x") or 0, texture.get("y") or 0) > 32


def classify(name, params, row):
    scalars = params["scalars"]
    family = _family(name, NAME_FAMILIES)
    if _ash(name):
        family = "wood"
    if family == "marker" or row["categories"].startswith("Views"):
        return "marker"
    if scalars.get("SelfIlluminationLuminance", 0) > 0:
        return "light source"
    translucent = "OPAQUE" not in (params.get("blend_mode") or "OPAQUE")
    if family == "placeholder":
        return family
    colour = params["vectors"].get("DiffuseColor")
    grey80 = colour is not None and all(abs(c - 80 / 255.0) < 0.004 for c in colour[:3])
    if grey80 and not _real_image(params["textures"].get("DiffuseMap")) and "Glossiness" not in params.get(
            "overridden_scalars", []):
        return "placeholder"
    if translucent and family in (None, "plastic", "glass"):
        return "glass"
    if family == "glass" and not translucent:
        return "mirror" if params["switches"].get("IsMetal") else "plastic"
    if family is None and params["switches"].get("IsMetal"):
        return "metal"
    return family or "other"


def score(name, params, row, family):
    scalars, vectors, textures = params["scalars"], params["vectors"], params["textures"]
    overridden = params.get("overridden_scalars", [])
    gloss_set = "Glossiness" in overridden
    diffuse = textures.get("DiffuseMap")
    bump = textures.get("BumpMap")
    has_image = _real_image(diffuse)
    large = any(word in row["categories"] for word in LARGE)
    colour = vectors.get("DiffuseColor") or [0, 0, 0]
    rgb = tuple(int(round(c * 255)) for c in colour[:3])

    if family == "marker":
        return 5, "Not a finish: a marker object (clearance zone, connection point or camera symbol); nothing to judge."
    if row["image_missing_from_the_export"]:
        return 1, "The image the material names is missing from the export (%s); what is left is one flat colour." % (
            row["image_missing_from_the_export"])
    if family == "placeholder":
        if name.lower().startswith("render_material"):
            if has_image:
                return 1, "A colour-only stand-in from Revit with a stray wood image on it; no finish is specified."
            return 2, "A colour-only stand-in from Revit (colour %d, %d, %d); no finish is specified." % rgb
        if has_image:
            return 1, "Revit's default material with a stray image (%s); no finish was ever set." % (
                diffuse["path"].rsplit(".", 1)[-1])
        return 1, "Revit's default material (flat grey %d, %d, %d); no finish was ever set." % rgb
    if has_image:
        image_family = _family(diffuse["path"].rsplit(".", 1)[-1], IMAGE_FAMILIES)
        if image_family and family not in ("other",) and image_family != family and not (
                image_family == "masonry" and family == "tile"):
            return (1 if family in ("metal", "fabric", "glass") else 2), (
                "The image shows %s (%s) but the name says %s." % (
                    image_family, diffuse["path"].rsplit(".", 1)[-1], family))
    if family == "siding":
        return 2, "Siding has boards with shadow lines; the material is flat, with no board profile."
    if family == "light source":
        return 4, "A light source: colour and brightness are exported (%.0f candela per square metre); the lighting itself is Phase 8's." % (
            scalars.get("SelfIlluminationLuminance", 0))
    if family == "glass":
        if rgb == (0, 128, 192):
            return 2, "Revit's default blue glass (colour 0, 128, 192), see-through %.0f percent; real glazing is nearly colourless and reflects." % (
                100 * scalars.get("Transparency", 0))
        if has_image:
            return 3, "See-through %.0f percent with its own colour and relief images; no proper reflection or bending of light." % (
                100 * scalars.get("Transparency", 0))
        return 3, "See-through %.0f percent with a plausible tint; flat, with no proper reflection or bending of light." % (
            100 * scalars.get("Transparency", 0))
    if family == "mirror":
        return 4, "A mirror: exported as a polished metal, which is what a mirror is to the renderer."
    if family == "metal":
        lower = name.lower()
        if params["switches"].get("IsMetal"):
            if "brush" in lower:
                return 3, "A metal with its colour; the brushed grain is a relief image only, without the stretched highlight of brushed metal."
            if gloss_set:
                return 4, "A metal with its colour and gloss (%.2f) stated." % scalars["Glossiness"]
            return 3, "A metal with its colour, but the gloss was left at Revit's default (0.50)."
        if any(word in lower for word in COATED):
            if gloss_set:
                return 4, "A coated metal: a plain colour with its gloss (%.2f) stated." % scalars["Glossiness"]
            return 3, "A coated metal: a plain colour, but the gloss was left at Revit's default (0.50)."
        return 2, "Named a metal but exported as a non-metal, so it reads as grey plastic."
    if has_image:
        scale_x = scalars.get("DiffuseMap_UVScaleX", 1.0) or 1.0
        scale_y = scalars.get("DiffuseMap_UVScaleY", 1.0) or 1.0
        field_x, field_y = FOOT_M / scale_x, FOOT_M / scale_y
        density = diffuse["x"] / field_x
        size = "image of %d by %d pixels over %.2f by %.2f m (%.0f pixels per metre)" % (
            diffuse["x"], diffuse["y"], field_x, field_y, density)
        if family == "paint":
            return 4, "A painted surface with a fine, even %s." % size
        if family in PATTERNED or family == "other":
            if large:
                if density < 512:
                    return 2, "Coarse on a large surface: %s; the plan asks for 1,024 near a station." % size
                if max(field_x, field_y) < 4.0:
                    return 3, "Sharp %s, but the same field repeats across walls and floors wider than it." % size
                return 4, "Sharp %s; the field is wider than most surfaces it covers." % size
            if density < 256:
                return 2, "Coarse: %s." % size
            if density < 512:
                return 3, "Moderate: %s." % size
            return 4, "Sharp %s on small surfaces." % size
        return 3, "A plain finish with an %s." % size
    if family in PATTERNED:
        if _real_image(bump):
            return 3, "The joints are a relief image only (%s); the colour is flat." % bump["path"].rsplit(".", 1)[-1]
        return 2, "A %s finish has a visible pattern; the material is one flat colour (%d, %d, %d)." % ((family,) + rgb)
    if family == "paint":
        return 4, "A painted surface: a plain colour (%d, %d, %d) is what paint is." % rgb
    if gloss_set:
        return 4, "A plain finish with its colour (%d, %d, %d) and gloss (%.2f) stated." % (rgb + (scalars["Glossiness"],))
    return 3, "A plain colour (%d, %d, %d), but the gloss was left at Revit's default (0.50)." % rgb


def main(audit_csv, params_json):
    with open(params_json, encoding="utf-8") as handle:
        params = json.load(handle)["materials"]
    with open(audit_csv, encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = list(reader.fieldnames)
        rows = list(reader)
    for column in ("family", "confidence_reason"):
        if column not in fields:
            fields.insert(fields.index("confidence") + (0 if column == "family" else 1), column)
    counts = {}
    for row in rows:
        entry = params[row["material"]]
        family = classify(row["material"], entry, row)
        figure, reason = score(row["material"], entry, row, family)
        row["family"], row["confidence"], row["confidence_reason"] = family, str(figure), reason
        counts[figure] = counts.get(figure, 0) + 1
    with open(audit_csv, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print("scored %d materials: %s" % (len(rows), ", ".join("%d x %d" % (counts[k], k) for k in sorted(counts))))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
