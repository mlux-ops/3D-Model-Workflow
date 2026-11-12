"""Phase 5: write the recipe of the native Unreal candidate for every material scored 3 or lower.

Usage:
    python -P -B phase5_candidates.py <material_audit.csv> <material_params.json> <folder of ambientCG sets> <material_candidates.csv>

Runs outside the editor. For each material with a confidence of 3 or lower it
chooses a parent material and the values an instance of that parent gets, and
writes one row. wieland_candidates.build_candidates() in the editor then
builds the instances from the table.

No photograph or sample exists, so every candidate is built from what the
Revit export says (name, colour, see-through, image, mapping size) and from
public-domain surface images. Each row says what it rests on and what the
owner should check. Revit's colours are stored as screen values (0 to 255
over 255); they are converted to the linear values Unreal materials use.
"""

import csv
import json
import os
import re
import sys

import numpy as np
from PIL import Image

GAME = "/Game/Wieland1529/Materials"
TEX = GAME + "/Textures/"
FOOT_M = 0.3048
CC0 = "ambientCG, CC0 1.0 (see asset_downloads.csv)"
OWN = "Computed by tools/phase5_make_textures.py; this project's own work"
REVIT = "The Revit export's own image (see asset_licences.csv for its group)"
NONE = "No image; values only"

# name of the set -> physical size of its field in metres (U, V)
SETS = {
    "Bricks086": (2.6, 1.3), "Carpet016": (1.7, 1.7), "Concrete046": (2.4, 2.4), "Fabric061": (0.4, 0.4),
    "Leather031": (0.45, 0.45), "Travertine009": (1.2, 1.2), "Wood049": (0.8, 0.8), "Wood090A": (1.4, 1.4),
    "WoodFloor051": (1.8, 1.8),
}


def slug(name):
    return re.sub(r"[^A-Za-z0-9_-]", "_", name)


def to_linear(value):
    return value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4


def mean_linear(path):
    """Mean colour of an image in linear values."""
    image = np.asarray(Image.open(path).convert("RGB").resize((256, 256)), dtype=np.float64) / 255.0
    linear = np.where(image <= 0.04045, image / 12.92, ((image + 0.055) / 1.055) ** 2.4)
    return [float(v) for v in linear.reshape(-1, 3).mean(axis=0)]


def rgb(values):
    return [round(float(v), 4) for v in values[:3]] + [1.0]


class Maker:
    def __init__(self, params, sets_folder):
        self.params = params
        self.means = {}
        for name in SETS:
            self.means[name] = mean_linear(os.path.join(sets_folder, name, name + "_2K-JPG_Color.jpg"))

    # --- what Revit says -------------------------------------------------
    def colour(self, material):
        """Revit's colour in linear values."""
        return [to_linear(v) for v in self.params[material]["vectors"]["DiffuseColor"][:3]]

    def see_through(self, material):
        return float(self.params[material]["scalars"].get("Transparency", 0.0))

    def revit_image(self, material, which="DiffuseMap"):
        texture = self.params[material]["textures"].get(which, {})
        path = texture.get("path", "")
        if not path.startswith("/Game/"):
            return None
        if which == "BumpMap" and "TC_NORMALMAP" not in texture.get("compression_settings", ""):
            return None
        return path.split(".")[0]

    def revit_field(self, material):
        scalars = self.params[material]["scalars"]
        return (FOOT_M / float(scalars["DiffuseMap_UVScaleX"]), FOOT_M / float(scalars["DiffuseMap_UVScaleY"]))

    # --- the kinds of candidate -------------------------------------------
    def plain(self, colour, rough, basis, note, parent="Opaque", metallic=None, extra=None, macro=0.0):
        scalars = {"RoughnessScale": rough}
        if parent != "Metal":
            # no real coating reflects more than about 85 percent or less than about half a percent
            colour = [min(0.85, max(0.005, v)) for v in colour[:3]]
        if metallic is not None:
            scalars["Metallic"] = metallic
        if macro:
            scalars["MacroVariation"] = macro
        scalars.update(extra or {})
        return {"parent": parent, "scalars": scalars, "vectors": {"Tint": rgb(colour)}, "textures": {},
                "switches": {}, "field": "none (no image)", "source": NONE, "basis": basis, "note": note}

    def from_set(self, name, basis, note, target=None, parent="Opaque", mesh=False, anti=False, macro=0.06,
                 rough=1.0, extra=None, size=None, turn=False):
        """A candidate from an ambientCG set; target is a linear colour to tint towards, or None."""
        size_u, size_v = size or SETS[name]
        tint = [1.0, 1.0, 1.0]
        if target is not None:
            tint = [target[i] / max(self.means[name][i], 0.004) for i in range(3)]
            if max(tint) > 3.0:  # keep the hue when the image is too dark to reach the colour
                tint = [v * 3.0 / max(tint) for v in tint]
            tint = [max(0.02, v) for v in tint]
        scalars = {"SizeU_m": size_u, "SizeV_m": size_v, "RoughnessScale": rough, "MacroVariation": macro}
        if turn:
            scalars["TurnQuarter"] = 1.0
        scalars.update(extra or {})
        return {"parent": parent, "scalars": scalars, "vectors": {"Tint": rgb(tint)},
                "textures": {"BaseColorMap": TEX + "T_W1529_%s_C" % name, "NormalMap": TEX + "T_W1529_%s_N" % name,
                             "RoughnessMap": TEX + "T_W1529_%s_R" % name},
                "switches": {"UseMeshUV": mesh, "AntiRepeat": anti},
                "field": "%.3f by %.3f m" % (size_u, size_v), "source": CC0 + ", set " + name, "basis": basis,
                "note": note}

    def from_revit(self, material, rough, basis, note, image_of=None, macro=0.08):
        """The Revit export's own image in the new parent, at Revit's size and mapping."""
        source = image_of or material
        size_u, size_v = self.revit_field(source)
        textures = {"BaseColorMap": self.revit_image(source)}
        # Revit's relief image is far stronger in the new parent than Revit shows it, so it is used at a
        # quarter strength; the limestone's relief image tilts the whole surface and is left out.
        relief = None if source.startswith("Indiana") else self.revit_image(source, "BumpMap")
        scalars = {"SizeU_m": size_u, "SizeV_m": size_v, "RoughnessScale": rough, "MacroVariation": macro,
                   "VariationSize_m": 6.0}
        if relief:
            textures["NormalMap"] = relief
            scalars["NormalStrength"] = 0.25
        return {"parent": "Opaque", "scalars": scalars,
                "vectors": {}, "textures": textures, "switches": {"UseMeshUV": True, "AntiRepeat": False},
                "field": "%.3f by %.3f m" % (size_u, size_v), "source": REVIT, "basis": basis, "note": note}

    def glass(self, tint, opacity, grazing, rough, basis, note, reeded=False):
        row = {"parent": "Glass", "scalars": {"Opacity": opacity, "OpacityGrazing": grazing, "Roughness": rough},
               "vectors": {"Tint": rgb(tint)}, "textures": {}, "switches": {}, "field": "none (no image)",
               "source": NONE, "basis": basis, "note": note}
        if reeded:
            row["scalars"].update({"SizeU_m": 0.0127, "SizeV_m": 0.1, "NormalStrength": 1.0})
            row["textures"]["NormalMap"] = TEX + "T_W1529_Reed_N"
            row["field"] = "0.0127 m (0.5 in) by any height"
            row["source"] = OWN
        return row

    def metal(self, material, rough, basis, note, brushed=False, floor=0.0, colour=None):
        colour = colour or [max(v, floor) for v in self.colour(material)]
        extra = {"Anisotropy": 0.5} if brushed else {}
        return self.plain(colour, rough, basis, note, parent="Metal", metallic=1.0, extra=extra)

    # --- one material ------------------------------------------------------
    def recipe(self, name, family):
        low = name.lower()
        colour = self.colour(name)
        unknown = "The finish was never set in Revit; this is a guess from the object's name. Owner to specify."

        if family == "placeholder":
            if name == "Wood":
                return self.from_set("Wood049", "Name only (Revit's default grey).", unknown, mesh=True)
            if name.startswith("Rug_Dots"):
                return self.from_set("Carpet016", "Name only: a rug.", unknown, parent="Fabric")
            if name.startswith("ETH_Fabric"):
                target = [to_linear(v) for v in ((0.80, 0.70, 0.56) if "Almond" in name else (0.66, 0.38, 0.20))]
                return self.from_set("Fabric061", "Name only: a fabric called %s." % name.split("_")[-1], unknown,
                                     target=target, parent="Fabric", mesh=True)
            if name == "PL113S_-_PL113S_-_Leg":
                return self.metal(name, 0.3, "Name only: a chair leg, taken as brushed steel.", unknown, brushed=True,
                                  colour=[0.55, 0.55, 0.55])
            if name == "PL113S_-_PL113S_-_Seat":
                return self.from_set("Fabric061", "Name only: a chair seat, taken as grey fabric.", unknown,
                                     target=[0.12, 0.12, 0.12], parent="Fabric", mesh=True)
            if name == "PL113S_-_PL113S_-_Black":
                return self.plain([0.015, 0.015, 0.015], 0.4, "Name only: black, taken as a black coating.", unknown)
            if name in ("Sink", "700342-Starck_rectangular_bathtub_-_starck-rectangular-bathtub-700342_-_"):
                return self.plain([0.85, 0.85, 0.84], 0.12, "Name only: a sink or bathtub, taken as white glazed.",
                                  unknown)
            if name == "01_CABINETS":
                return self.plain([0.80, 0.80, 0.78], 0.35, "Name only: cabinets, taken as painted white.", unknown)
            if name == "Default_New_Material_2_":
                return self.from_set("Bricks086", "The missing image is named 'Endicott SN-8 Black Glazed Thinbrick "
                                     "Modular Stack'; a running-bond brick tinted black stands in.",
                                     "The specified brick is a stack bond; no public-domain stack-bond set with a "
                                     "stated size was found. Owner to supply the maker's image.",
                                     target=[0.02, 0.02, 0.02], rough=0.45, macro=0.03)
            if name.startswith("Render_Material"):
                return self.plain(colour, 0.6, "Revit's stand-in colour, kept; matte.", unknown)
            if name == "EAE_Logo":
                return self.plain([0.03, 0.03, 0.03], 0.5, "Name only: a logo, taken as dark and matte.", unknown)
            if name.startswith("RNT_Material"):
                return self.plain(colour, 0.6, "Revit's default colour, kept; matte.", unknown)
            return self.plain([0.78, 0.77, 0.74], 0.6, "Revit's default material; taken as off-white paint.", unknown)

        if family == "glass":
            see = self.see_through(name)
            if name == "Betafence_LeafMaterial":
                return self.plain(colour, 0.5, "The image is missing; a fence leaf, taken as coated steel in Revit's "
                                  "colour.", "Owner to confirm the fence finish.")
            if "reeded" in low:
                return self.glass([0.95, 0.97, 0.96], 0.18, 0.6, 0.04,
                                  "Name: reeded glass, 0.5 in vertical reed; relief computed at that size.",
                                  "Reed depth (2 mm) is assumed.", reeded=True)
            if name in ("Opalwhite", "FILAMENT_INNER_MATERIAL", "LIGHT_BULB_FROST", "Difused_glass"):
                # the see-through parent shows a milky glass dark when lit from the front, so the
                # opal glass of a light fitting is built as an opaque, smooth white surface
                tint = [0.8, 0.8, 0.8] if name == "Opalwhite" else [max(v, 0.6) for v in colour]
                return self.plain(tint, 0.3, "Name: the opal or frosted glass of a light fitting; taken as an "
                                  "opaque, smooth, milky white surface.",
                                  "It does not let light through; once lighting is set up (Phase 8) it may need "
                                  "to glow. Owner to confirm.")
            if "frost" in low:
                return self.glass([max(v, 0.6) for v in colour], 0.75, 0.95, 0.6,
                                  "Name: a frosted glass; rough, mostly opaque.",
                                  "On the swatch it reads darker lit from the front than at a grazing angle; a "
                                  "limit of see-through materials in this engine. Owner to confirm.")
            if "solarbronze" in low:
                return self.glass(colour, 0.4, 0.75, 0.02, "Name: Solarban R100 on Solarbronze; Revit's bronze tint, "
                                  "see-through %d percent in Revit." % round(see * 100),
                                  "The maker's reflectance and tint were not looked up; owner to confirm.")
            if all(abs(a - b) < 0.02 for a, b in zip(self.params[name]["vectors"]["DiffuseColor"][:3],
                                                     (0.0, 0.50196, 0.75294))):
                return self.glass([0.90, 0.95, 0.93], 0.10, 0.55, 0.02,
                                  "Revit's default blue replaced by a near-colourless glass with a faint green.",
                                  "Tint and reflectance of the real glazing are not specified in the export.")
            opacity = min(0.3, max(0.08, 1.0 - see))
            return self.glass([max(v, 0.75) for v in colour], opacity, 0.55, 0.02,
                              "Revit's tint lightened to a clear glass; see-through %d percent in Revit." % round(
                                  see * 100), "Owner to confirm.")

        if family == "metal":
            if name in ("Hansgrohe_-_Metal_-_700_Matte_White", "White_Aluminum",
                        "Pablo_Sky_Dome_18_Pendant_Black_Aluminum_R2025_Opal", "ETH_Metal_Black"):
                tint = [0.015, 0.015, 0.015] if name == "ETH_Metal_Black" else colour
                return self.plain(tint, 0.5, "Name: a coated metal; the coating, not bare metal, is what shows.",
                                  "Gloss of the coating is assumed (matte).")
            if "brushed" in low:
                return self.metal(name, 0.3, "Name: brushed; a stretched highlight across the grain.",
                                  "Grain direction follows the mesh and is not checked per object.", brushed=True,
                                  floor=0.3)
            if "chrome" in low or "polished" in low:
                return self.metal(name, 0.06, "Name: polished chrome; a bright mirror-like metal.", "None.",
                                  colour=[0.75, 0.75, 0.77])
            if "galvanized" in low:
                return self.metal(name, 0.4, "Name: galvanized steel.", "None.", floor=0.3)
            if "matte" in low:
                return self.metal(name, 0.5, "Name: a matte metal in Revit's colour.", "None.")
            if "metal_finish" in low:
                return self.metal(name, 0.2, "Name says metal; exported as a non-metal. Taken as a bright metal.",
                                  "The actual finish (chrome, nickel, steel) is not named; owner to specify.",
                                  floor=0.45)
            return self.metal(name, 0.3, "Name: a metal in Revit's colour, satin.", "Gloss is assumed (satin).",
                              floor=0.2)

        if family == "wood":
            if name == "Finishes_-_Flooring__Oak":
                return self.from_set("WoodFloor051", "Name: oak flooring; Revit's image is coarse (373 pixels per "
                                     "metre).", "Board width and colour are the set's own; owner to confirm.",
                                     rough=1.0, macro=0.05)
            if name.startswith("Oak_Veneered_MDF"):
                return self.from_revit(name, 0.45, "Revit's own sharp image at Revit's size, with a slow change of "
                                       "brightness so that the repeat is less even.", "None.")
            target = None if all(abs(v - colour[0]) < 0.01 for v in colour) and name != "Cabinet_Light_Wood" else colour
            if name == "Cabinet_Light_Wood":
                target = [0.55, 0.42, 0.27]
            if name == "ETH_Teak_NaturalOutdoor":
                target = [0.30, 0.22, 0.15]
            return self.from_set("Wood049", "Name: a wood finish; a straight-grained wood set, tinted.",
                                 "Species and stain are not matched to a sample; grain direction follows the mesh.",
                                 target=target, mesh=True, rough=1.0)

        if family == "stone":
            if name == "Counter_Top":
                return self.from_set("Wood090A", "Revit's image shows cherry wood, so a wood counter is taken.",
                                     "The name says counter top, the image says wood; owner to say which.", mesh=True)
            if name.startswith("Indiana_Limestone") or name.startswith("Calacatta"):
                rough = 0.25 if name.startswith("Calacatta") else 0.75
                return self.from_revit(name, rough, "Revit's own sharp image at Revit's size, with a slow change of "
                                       "brightness so that the repeat is less even.", "None.")
            if name.startswith("Countertop"):
                return self.plain(colour, 0.15, "Revit's alabaster image is moderate (420 pixels per metre); a "
                                  "polished stone in Revit's colour with a slow change of brightness.",
                                  "The slab is not specified; owner to supply the maker's image.", macro=0.10)
            target = colour if name.startswith("TF27") else None
            return self.from_set("Travertine009", "Name: %s; a travertine set." % (
                "honed ivory limestone" if target else "travertine"),
                "Stone and colour are not matched to a sample.", target=target, anti=True, rough=1.0)

        if family == "masonry":
            if name.startswith("Brick"):
                return self.from_set("Bricks086", "Name: brick; Revit's image is coarse (252 pixels per metre).",
                                     "Brick colour, size and bond are the set's own; owner to confirm.", macro=0.05)
            if name == "Concrete_Masonry_Units":
                row = self.plain(colour, 1.0, "Name: concrete block; Revit's image is coarse. Colour, relief and "
                                 "roughness of the nominal 16 by 8 in block in running bond computed at that size.",
                                 "Block size, bond and joint (10 mm) are assumed; the colour is Revit's.", macro=0.08)
                row["scalars"].update({"SizeU_m": 0.4064, "SizeV_m": 0.4064})
                row["textures"] = {"BaseColorMap": TEX + "T_W1529_CMU_C", "NormalMap": TEX + "T_W1529_CMU_N",
                                   "RoughnessMap": TEX + "T_W1529_CMU_R"}
                row["field"] = "0.4064 by 0.4064 m (two courses)"
                row["source"] = OWN
                return row
            return self.from_revit(name, 0.85, "Revit's own sharp image at Revit's size, with a slow change of "
                                   "brightness so that the repeat is less even.", "None.")

        if family == "concrete":
            if name.startswith("In_Situ"):
                return self.from_revit(name, 0.8, "Revit's own sharp image at Revit's size, with a slow change of "
                                       "brightness so that the repeat is less even.", "None.")
            return self.from_set("Concrete046", "Name: concrete; Revit's image is coarse (465 pixels per metre).",
                                 "Formwork pattern and colour are the set's own.", anti=True, macro=0.08)

        if family == "fabric":
            if "leather" in low or "shoes" in low:
                return self.from_set("Leather031", "Name: leather; a leather set tinted to the name's colour.",
                                     "Not matched to a sample.",
                                     target=[0.012, 0.012, 0.012] if "black" in low else colour, mesh=True, rough=1.0)
            return self.from_set("Fabric061", "Name: a woven fabric; a weave set tinted to Revit's colour.",
                                 "Weave and colour are not matched to a sample.", target=colour, parent="Fabric",
                                 mesh=True)

        if family == "siding":
            exposure = 0.1778 if "LAP" in name else 0.1143
            tint = colour
            row = self.plain(tint, 0.6, "Name: %s; relief of one course computed at an exposure of %.0f mm." % (
                "fibre-cement lap siding" if "LAP" in name else "vinyl siding", exposure * 1000),
                "The exposure is assumed; the colour is Revit's. Owner to confirm both.")
            row["scalars"].update({"SizeU_m": 1.0, "SizeV_m": exposure})
            row["textures"]["NormalMap"] = TEX + "T_W1529_Siding_N"
            row["field"] = "any width by %.4f m" % exposure
            row["source"] = OWN
            return row

        if family == "tile":
            row = self.plain(colour, 1.0, "Name: porcelain tile 24 by 12 in; colour, relief and roughness of one "
                             "tile with its joint computed at that size.",
                             "Joint width (3 mm) and stacked bond are assumed.")
            row["scalars"].update({"SizeU_m": 0.6096, "SizeV_m": 0.3048})
            row["textures"] = {"BaseColorMap": TEX + "T_W1529_Tile24x12_C", "NormalMap": TEX + "T_W1529_Tile24x12_N",
                               "RoughnessMap": TEX + "T_W1529_Tile24x12_R"}
            row["field"] = "0.6096 by 0.3048 m"
            row["source"] = OWN
            return row

        # plastics and everything else: a plain colour with a gloss chosen from the name
        if name == "Difused_glass":
            return self.glass([0.9, 0.9, 0.9], 0.8, 0.95, 0.6, "Name: a diffusing glass; Revit's image is a stray "
                              "wood.", "Owner to confirm.")
        if name.startswith("Laminate__Linen"):
            return self.from_revit(name, 0.15, "Revit's own sharp image at Revit's size, with the gloss the name "
                                   "states.", "None.", macro=0.0)
        if name.startswith("KM3054") or name == "Betafence_HingeMaterial":
            return self.metal(name, 0.35, "A hardware part in a grey colour; taken as satin metal.",
                              "Whether it is metal is not stated; owner to confirm.", floor=0.2)
        gloss = 0.5
        why = "gloss assumed (satin)"
        for key, value, text in (("glossy", 0.15, "glossy by name"), ("glass_black", 0.05, "black glass by name"),
                                 ("rubber", 0.85, "rubber by name"), ("epp", 0.75, "foam by name"),
                                 ("laminate", 0.35, "laminate, satin"), ("hewi", 0.3, "polyamide, satin"),
                                 ("plastic", 0.3, "plastic, satin"), ("finish", 0.45, "a black coating"),
                                 ("black", 0.45, "a black coating")):
            if key in low:
                gloss, why = value, text
                break
        return self.plain(colour, gloss, "Revit's colour; %s." % why,
                          "Revit left the gloss at its default; the value here is from the name only.")


def tune(name, recipe):
    """Corrections the test table (phase5_material_tests.py) asked for; one change per finding."""
    images = " ".join(recipe["textures"].values())
    # the relief of these three sets did not show on the wall piece lit at a grazing angle
    if any(key in images for key in ("Fabric061", "Concrete046", "Travertine009")):
        recipe["scalars"]["NormalStrength"] = 2.0
    # the leather image is uneven at large scale, so its repeat could be recognised when laid plainly
    if "Leather031" in images:
        recipe["switches"]["AntiRepeat"] = True
    # Revit's relief image of this block does not wrap (a visible seam); the colour image does
    if name.startswith("CMU_Block"):
        recipe["textures"].pop("NormalMap", None)
        recipe["scalars"].pop("NormalStrength", None)
        recipe["note"] += " Revit's relief image is left out because it shows a seam where it wraps."
    return recipe


def main(audit_csv, params_json, sets_folder, out_csv):
    with open(audit_csv, encoding="utf-8", newline="") as handle:
        audit = list(csv.DictReader(handle))
    with open(params_json, encoding="utf-8") as handle:
        params = json.load(handle)["materials"]
    maker = Maker(params, sets_folder)
    rows = []
    for item in audit:
        if int(item["confidence"]) > 3:
            continue
        name = item["material"]
        recipe = tune(name, maker.recipe(name, item["family"]))
        rows.append({
            "material": name,
            "family": item["family"],
            "confidence": item["confidence"],
            "revit_asset": item["asset_path"],
            "candidate_asset": "%s/Candidates/MI_W1529_C_%s" % (GAME, slug(name)),
            "parent": "%s/Parents/M_W1529_%s" % (GAME, recipe["parent"]),
            "scalars": json.dumps(recipe["scalars"], sort_keys=True),
            "vectors": json.dumps(recipe["vectors"], sort_keys=True),
            "textures": json.dumps(recipe["textures"], sort_keys=True),
            "switches": json.dumps(recipe["switches"], sort_keys=True),
            "physical_field_size": recipe["field"],
            "source_and_licence": recipe["source"],
            "what_it_rests_on": recipe["basis"],
            "for_the_owner": recipe["note"],
        })
    with open(out_csv, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    by_parent = {}
    for row in rows:
        key = row["parent"].rsplit("_", 1)[-1]
        by_parent[key] = by_parent.get(key, 0) + 1
    print("%d candidates written to %s: %s" % (len(rows), out_csv, by_parent))


if __name__ == "__main__":
    main(*sys.argv[1:5])
