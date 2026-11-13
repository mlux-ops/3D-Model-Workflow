"""Phase 12, step 12.1: the work list and the recipe of every rebuilt material.

    python -P -B phase12_recipes.py <folder docs/unreal/1529_wieland>

Reads material_audit.csv (never writes it), review/phase5/material_params.json (what the Revit export
says), review/phase12/uses.json (where each material is shown), material_candidates.csv and
material_tests.csv (Phase 5). Makes the images of this phase (phase12_make_textures.py) and writes

    material_rebuild.csv             one row per work-list material
    review/phase12/recipes.json      the same recipes for the editor tool (wieland_rebuild.py)

When review/phase12/tests.json (phase12_material_tests.py) and review/phase12/state.json
(wieland_rebuild.py) are there, their results are merged into the rows.

A recipe is an instance of a parent material: which parent, which numbers, colours, images and
switches. Colours given as three whole numbers are sRGB 0 to 255; a roughness of 0 is a mirror and
1 is chalk. The reason for every value is in the row.
"""
import csv
import datetime
import fnmatch
import json
import math
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))   # -P leaves this folder out
import phase12_make_textures as mk

GAME = "/Game/Wieland1529/Materials"
TEX = GAME + "/Textures/"
PARENTS = {"Opaque": GAME + "/Parents/M_W1529_Opaque", "Metal": GAME + "/Parents/M_W1529_Metal",
           "Glass": GAME + "/Parents/M_W1529_Glass", "Emissive": GAME + "/Parents/M_W1529_Emissive",
           "StoneBlend": GAME + "/Parents/M_W1529_StoneBlend"}
REBUILT = GAME + "/Rebuilt/MI_W1529_R_"
FOOT_M = 0.3048
SITE = "E:/Wieland1529_site_data/textures_cc0"
BRAND = re.compile("brizo|hansgrohe|kohler", re.I)
READ = "read 2026-11-13"

OWN = "Made by tools/phase12_make_textures.py; this project's own work, no licence needed"
OWN5 = "Computed by tools/phase5_make_textures.py; this project's own work"
REVIT = "The Revit export's own image (see asset_licences.csv for its group)"
CC0_PH = "Poly Haven, Creative Commons CC0 1.0 (https://polyhaven.com/license, %s)" % READ
CC0_ACG = "ambientCG, Creative Commons CC0 1.0 Universal (https://docs.ambientcg.com/license/)"

MARKERS = {
    "Generic_Clearance_Area": "a clearance zone drawn in the Revit family, not a finish",
    "Generic_Warning": "a warning marker drawn in the Revit family, not a finish",
    "MI_CineMat_CamViewFinder": "part of the engine's camera object, not a Revit material; shown on no surface",
    "MI_CineMat_CameraBody": "part of the engine's camera object, not a Revit material; shown on no surface",
    "z_Miele_Connection_Water_IN": "a connection marker of the Miele family, not a finish",
    "z_Miele_Connection_Connection_Modul": "a connection marker of the Miele family, not a finish",
    "z_Miele_Connection_Connection_Water_IN": "a connection marker of the Miele family, not a finish",
}

URL_DOVE = ("https://paintdb.com/colors/benjamin-moore/bm-oc-17-white-dove ; "
            "https://plan-home.com/color/benjamin-moore-white-dove-oc-17 ; https://pontata.com/color/bm-white-dove-oc-17 ; "
            "https://compositepaint.com/colors/benjamin-moore/white-dove/ (all %s)" % READ)
URL_LIME = ("https://polycor.com/stones/indiana-limestone-full-color-blend/ ; "
            "https://www.polycor.com/wp-content/uploads/2023/04/indiana-limestone-full-color-blend.pdf ; "
            "https://iliai.com/?p=1571 (all %s)" % READ)
URL_TAJ = ("https://www.countryfloors.com/product/taj-mahal-honed-quartzite-slab-random/ ; "
           "https://www.msisurfaces.com/blogs/post/2025/05/28/the-ultimate-guide-to-taj-mahal-quartzite-finishes-sizes-&-design-ideas.aspx ; "
           "https://in2stone.co.uk/products/quartzite/taj-mahal-honed-quartzite (all %s)" % READ)
URL_BRIZO_BL = ("https://www.brizo.com/kitchen/product/69080-BL ; "
                "https://www.brizo.com/world-of-brizo/inspired-craftsmanship/matte-black-modern-classic-evolves (%s)" % READ)
URL_BRIZO_PVD = "https://www.brizo.com/innovation/innovations-for-the-bath/brilliance-finishes (%s)" % READ
URL_BRIZO_SS = "https://www.brizo.com/kitchen/product/61365LF-C-SS ; " + URL_BRIZO_PVD
URL_BRIZO_BNX = "https://www.brizo.com/bath/product/T70198-BNX ; " + URL_BRIZO_PVD
URL_BRIZO_PC = "https://www.brizo.com/bath/product/T65722LF-PC (%s)" % READ
URL_KOHLER_CP = ("https://techcomm.kohler.com/techcomm/pdf/K-7271_spec_US-CA_Kohler_en.pdf ; "
                 "https://techcomm.kohler.com/techcomm/pdf/K-7272_spec_US-CA_Kohler_en.pdf (%s)" % READ)
URL_KOHLER_27263 = "https://techcomm.kohler.com/techcomm/pdf/K-27263-SC02_spec_US-CA_Kohler_en.pdf (%s)" % READ
URL_KOHLER_32375 = "https://techcomm.kohler.com/techcomm/pdf/K-32375-SC01_spec_US-CA_Kohler_en.pdf (%s)" % READ
URL_KOHLER_77685 = "https://techcomm.kohler.com/techcomm/pdf/K-77685_spec_US-CA_Kohler_en.pdf (%s)" % READ
URL_HG_700 = ("https://assets.hansgrohe.com/celum/web/finishplus_brochure2020_us.pdf ; "
              "https://www.hansgrohe.com/bathroom/new-products/finishplus ; "
              "https://pro.hansgrohe-usa.com/service/finishsamples (all %s)" % READ)
URL_HG_990 = ("https://www.winnings.com.au/p/hansgrohe-addstoris-addstoris-bath-towel-rail-polished-gold-optic-41747990 ; "
              "https://www.victorianplumbing.co.uk/hansgrohe-addstoris-polished-gold-optic-single-towel-rail ; "
              "https://www.megabad.com/en/hansgrohe-bad-accessoires-addstoris-badetuchhalter-a-1246943.htm (all %s)" % READ)
REF = "E:/Wieland1529_site_data/manufacturer_reference/brizo/"


def slug(name):
    return re.sub(r"[^A-Za-z0-9_-]", "_", name)


def to_linear(value):
    return value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4


def to_srgb(value):
    value = min(1.0, max(0.0, value))
    return value * 12.92 if value <= 0.0031308 else 1.055 * value ** (1 / 2.4) - 0.055


def kelvin_linear(kelvin):
    """Colour of a glowing body at this temperature, in linear values with a brightness of 1
    (Tanner Helland's fit), so that multiplying by candela per square metre gives that luminance."""
    t = kelvin / 100.0
    red = 255.0 if t <= 66 else 329.698727446 * (t - 60) ** -0.1332047592
    green = 99.4708025861 * math.log(t) - 161.1195681661 if t <= 66 else 288.1221695283 * (t - 60) ** -0.0755148492
    blue = 255.0 if t >= 66 else (0.0 if t <= 19 else 138.5177312231 * math.log(t - 10) - 305.0447927307)
    linear = [to_linear(min(255.0, max(0.0, v)) / 255.0) for v in (red, green, blue)]
    brightness = 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]
    return [round(v / brightness, 4) for v in linear]


class Book:
    """Holds what the export says and collects recipes, the images they need and the files behind them."""

    def __init__(self, root):
        self.root = root
        self.generated = os.path.join(root, "review", "phase12", "generated_textures")
        os.makedirs(self.generated, exist_ok=True)
        with open(os.path.join(root, "review", "phase5", "material_params.json"), encoding="utf-8") as handle:
            self.params = json.load(handle)["materials"]
        with open(os.path.join(root, "review", "phase12", "uses.json"), encoding="utf-8") as handle:
            self.uses = json.load(handle)
        self.imports = {}     # asset path -> [file, kind]
        self.files = {}       # asset path -> file (every image a recipe uses, for the tests)
        self.made = []        # rows of generated_textures.csv
        self.recipes = {}     # material -> recipe
        self.means = {}

    # --- what Revit says ---------------------------------------------------
    def revit_rgb(self, material):
        return [round(v * 255) for v in self.params[material]["vectors"]["DiffuseColor"][:3]]

    def gloss(self, material):
        return float(self.params[material]["scalars"].get("Glossiness", 0.5))

    def revit_texture(self, material, which="DiffuseMap"):
        texture = self.params[material]["textures"].get(which) or {}
        path = texture.get("path", "")
        if not path.startswith("/Game/"):
            return None
        asset = path.split(".")[0]
        self.files[asset] = (texture.get("source_file") or "").replace("\\", "/")
        return asset

    def revit_field(self, material):
        scalars = self.params[material]["scalars"]
        return (FOOT_M / float(scalars["DiffuseMap_UVScaleX"]), FOOT_M / float(scalars["DiffuseMap_UVScaleY"]))

    # --- images --------------------------------------------------------------
    def _own(self, item):
        path, name, kind, field, note = item
        asset = TEX + name
        if asset not in self.imports:
            self.imports[asset] = [path.replace("\\", "/"), kind]
            self.files[asset] = path.replace("\\", "/")
            self.made.append([name + ".png", kind, "" if field is None else "%.3f by %.3f m" % field, note])
        return asset

    def flat(self, rgb):
        return self._own(mk.flat_colour(tuple(rgb), self.generated))

    def veneer(self, set_id, resolution, short, gain=None):
        """The three images of a Poly Haven set: colour, relief, roughness. With gain, the colour
        image is a copy whose grain is that many times stronger (the set's own is too faint to read)."""
        result = {}
        for key, part, kind in (("BaseColorMap", "diff", "colour"), ("NormalMap", "nor_dx", "normal"),
                                ("RoughnessMap", "rough", "mask")):
            path = "%s/PolyHaven/%s/%s_%s_%s.jpg" % (SITE, set_id, set_id, part, resolution)
            asset = TEX + "T_W1529_P12_%s_%s" % (short, {"diff": "C", "nor_dx": "N", "rough": "R"}[part])
            self.imports[asset] = [path, kind]
            self.files[asset] = path
            result[key] = asset
        if gain:
            source = self.files[result["BaseColorMap"]]
            del self.imports[result["BaseColorMap"]]
            item = mk.contrast(source, self.generated, "T_W1529_P12_%s_Strong_C" % short, gain)
            item[3] = (1.0, 1.0)
            item[4] = "Poly Haven %s (CC0), %s" % (set_id, item[4])
            result["BaseColorMap"] = self._own(item)
        return result

    def ambient(self, name):
        result = {}
        for key, letter, part in (("BaseColorMap", "C", "Color"), ("NormalMap", "N", "NormalDX"),
                                  ("RoughnessMap", "R", "Roughness")):
            asset = TEX + "T_W1529_%s_%s" % (name, letter)
            self.files[asset] = "%s/ambientCG/%s/%s_2K-JPG_%s.jpg" % (SITE, name, name, part)
            result[key] = asset
        return result

    def mean(self, path):
        if path not in self.means:
            self.means[path] = mk.mean_linear(path)
        return self.means[path]

    def tint_towards(self, colour_asset, target_rgb, limit=3.0):
        mean = self.mean(self.files[colour_asset])
        tint = [to_linear(target_rgb[i] / 255.0) / max(mean[i], 0.004) for i in range(3)]
        if max(tint) > limit:
            tint = [v * limit / max(tint) for v in tint]
        return [round(max(0.02, v), 4) for v in tint] + [1.0]

    # --- the kinds of recipe ---------------------------------------------------
    def coat(self, rgb, rough, relief=None, relief_size=None, strength=1.0, extra=None):
        """Paint, powder coat, plastic, glaze: a plain colour image on the Opaque parent."""
        rgb = [round(to_srgb(min(0.85, max(0.015, to_linear(v / 255.0)))) * 255) for v in rgb]
        textures = {"BaseColorMap": self.flat(rgb)}
        scalars = {"RoughnessScale": rough, "SizeU_m": 1.0, "SizeV_m": 1.0}
        field = "1.000 by 1.000 m (plain colour image)"
        source = OWN
        if relief:
            textures["NormalMap"] = relief
            scalars.update({"SizeU_m": relief_size[0], "SizeV_m": relief_size[1], "NormalStrength": strength})
            field = "%.3f by %.3f m" % tuple(relief_size)
        scalars.update(extra or {})
        return {"parent": "Opaque", "scalars": scalars, "vectors": {"Tint": [1.0, 1.0, 1.0, 1.0]},
                "textures": textures, "switches": {}, "field": field, "source": source, "rgb": rgb}

    def metal(self, rgb, rough, brushed=False, anisotropy=0.0):
        """Bare, plated or vapour-coated metal on the Metal parent. Brushed: scratches along the
        mesh's U direction, and the highlight stretched across them (negative Anisotropy)."""
        textures = {"BaseColorMap": self.flat(rgb)}
        scalars = {"RoughnessScale": rough, "Metallic": 1.0, "SizeU_m": 1.0, "SizeV_m": 1.0}
        switches = {}
        field = "1.000 by 1.000 m (plain colour image)"
        if brushed:
            relief, roughness = mk.brushed(self.generated)
            textures["NormalMap"] = self._own(relief)
            textures["RoughnessMap"] = self._own(roughness)
            scalars.update({"SizeU_m": 0.25, "SizeV_m": 0.25, "Anisotropy": anisotropy, "NormalStrength": 1.0})
            switches["UseMeshUV"] = True
            field = "0.250 by 0.250 m (brushed relief and roughness)"
        return {"parent": "Metal", "scalars": scalars, "vectors": {"Tint": [1.0, 1.0, 1.0, 1.0]},
                "textures": textures, "switches": switches, "field": field, "source": OWN, "rgb": list(rgb)}

    def chrome(self, rough=0.05):
        return self.metal((196, 197, 197), rough)

    def glass(self, tint_rgb, opacity, grazing, rough):
        tint = [round(to_linear(v / 255.0), 4) for v in tint_rgb] + [1.0]
        return {"parent": "Glass", "scalars": {"Opacity": opacity, "OpacityGrazing": grazing, "Roughness": rough},
                "vectors": {"Tint": tint}, "textures": {}, "switches": {},
                "field": "none (the Glass parent takes a tint, not a colour image)",
                "source": "No image; values only", "rgb": list(tint_rgb)}

    def light(self, rgb, luminance, kelvin, rough=0.3):
        """A glowing face: its own colour when off, and light of the Revit luminance (candela per
        square metre) and colour temperature. The project's fixed exposure is in physical units, so
        the number is used as it stands."""
        recipe = self.coat(rgb, rough)
        recipe["parent"] = "Emissive"
        recipe["scalars"]["Luminance_cd_m2"] = float(luminance)
        recipe["vectors"]["EmissiveColor"] = kelvin_linear(kelvin) + [1.0]
        return recipe

    def wood(self, images, size, target_rgb, turn=False, anti=True, rough=1.0, mesh=False, macro=0.04, strength=1.0,
             source=CC0_PH):
        scalars = {"SizeU_m": size[0], "SizeV_m": size[1], "RoughnessScale": rough, "MacroVariation": macro,
                   "NormalStrength": strength}
        if turn:
            scalars["TurnQuarter"] = 1.0
        tint = [1.0, 1.0, 1.0, 1.0] if target_rgb is None else self.tint_towards(images["BaseColorMap"], target_rgb)
        return {"parent": "Opaque", "scalars": scalars, "vectors": {"Tint": tint}, "textures": dict(images),
                "switches": {"UseMeshUV": mesh, "AntiRepeat": anti}, "field": "%.3f by %.3f m" % tuple(size),
                "source": source, "rgb": target_rgb}

    def add(self, pattern, recipe, rests, confidence, reason, assumption="", owner="", urls=""):
        names = [n for n in self.worklist if fnmatch.fnmatchcase(n, pattern)]
        if len(names) != 1:
            raise SystemExit("recipe key %r matches %d work-list materials" % (pattern, len(names)))
        if names[0] in self.recipes:
            raise SystemExit("two recipes for " + names[0])
        recipe = dict(recipe)
        recipe.update({"rests": rests, "confidence": confidence, "reason": reason, "assumption": assumption,
                       "owner": owner, "urls": urls})
        self.recipes[names[0]] = recipe

    def by_revit(self, name, kind, rough=None, colour=None, brushed=False):
        """A plain finish whose colour is the Revit family's colour; roughness from the family's
        glossiness (1 - glossiness, kept between 0.08 and 0.7) unless given."""
        rgb = colour or self.revit_rgb(name)
        if rough is None:
            rough = round(min(0.7, max(0.08, 1.0 - self.gloss(name))), 2)
        if kind == "metal":
            return self.metal(rgb, rough, brushed=brushed, anisotropy=-0.5 if brushed else 0.0)
        return self.coat(rgb, rough)


def describe_use(use):
    labels = sorted(use.get("labels", {}).items(), key=lambda kv: -kv[1])[:3]
    return "; ".join("%s (%d)" % (k, v) for k, v in labels)


def write_recipes(b):
    """Every rebuilt material. The order follows the work list: brand names, the owner's rebuild rows,
    the keep row with a note, then the blank rows."""
    add, coat, metal, chrome, glass, light, by = b.add, b.coat, b.metal, b.chrome, b.glass, b.light, b.by_revit
    dove = (239, 238, 229)
    eggshell = b._own(mk.eggshell_normal(b.generated))
    photo = "Manufacturer pictures are kept as reference only (%s, listed in asset_downloads.csv); none is used as an image of the material."

    # ---- names with Brizo, Hansgrohe or Kohler --------------------------------
    add("Hansgrohe_-_Metal_-_700_Matte_White", coat((240, 240, 237), 0.55),
        "Hansgrohe finish 700/701 'Matte White' (FinishPlus brochure: 'Matte White (-70X)'; Hansgrohe: 'Matt White has a light, "
        "pure, harmonious, and natural look'; the matte finishes are lacquered). A lacquer, so the coating shows and not bare "
        "metal: Opaque parent, white just under paper white, matte.", 4,
        "Finish name, sheen (matte) and kind (lacquer) are stated by the manufacturer; the exact white is not published and is "
        "taken as a neutral white.",
        owner="This Hansgrohe-named material is on 697 handrail surfaces (Railings, Handrail - Rectangular), which is not a "
              "Hansgrohe product: the Revit handrail type borrows the material. It is rebuilt as the Hansgrohe matte white lacquer; "
              "say if the handrails are to be another finish.", urls=URL_HG_700)
    add("Kohler-Light_Source-Incandescent", light((248, 239, 209), 2000, 2700, rough=0.1),
        "Owner's note: 'emissive glass material'. Kohler Purist sconces K-27263-SC02 and K-32375-SC01 take E26 lamps sold "
        "separately; Kohler states no colour temperature, so the Revit family's values are used: 2,000 candela per square metre "
        "at 2,700 K. Smooth like glass (roughness 0.1).", 4,
        "The owner named the finish; luminance and colour temperature are the Revit family's own numbers.",
        owner="Kohler does not state a lamp colour temperature (lamps are sold separately); 2,700 K is the Revit family's value.",
        urls=URL_KOHLER_27263 + " ; " + URL_KOHLER_32375)
    add("Kohler-Glass-L-Crystal_Clear", glass((236, 240, 239), 0.10, 0.55, 0.02),
        "Kohler K-27263-SC02 spec: 'Rounded glass shades connect with tube attachments'; the Revit family names the glass Crystal "
        "Clear and shows it 85 % clear. Clear glass: Glass parent, nearly colourless tint, 10 % opacity face-on.", 4,
        "Clear glass is a plain finish; the family's name and transparency agree. Kohler's sheet does not say clear or frosted.",
        owner="Kohler's spec sheet does not say whether the K-27263 shade is clear or frosted; clear is the Revit family's word.",
        urls=URL_KOHLER_27263)
    add("Kohler-Frosted_Glass", glass((230, 234, 232), 0.55, 0.85, 0.55),
        "Kohler K-32375-SC01 spec: 'frosted-glass shade'. Glass parent with a rough surface (0.55) and 55 % opacity so that the "
        "lamp behind it reads as a soft glow.", 4, "The manufacturer states frosted glass.", urls=URL_KOHLER_32375)
    kohler_cp = ("Kohler finish CP 'Polished Chrome' (listed on Kohler's spec sheets for the Clearflo drains K-7271 and K-7272). "
                 "Chrome plate: Metal parent, chrome's own reflectance (sRGB 196,197,197), near-mirror roughness 0.05.")
    for key in ("Kohler-Metal-CP-Polished_Chrome", "Metal_-_Kohler_-_CP_-_Polished_Chrome", "Metal-Kohler-CP-Polished_Chrome"):
        add(key, chrome(), kohler_cp, 4, "Finish code and name are the manufacturer's; polished chrome is a plain, known finish.",
            urls=URL_KOHLER_CP)
    black_note = ("Brizo finish BL 'Matte Black' (product page 69080-BL). Brizo: 'Its striking dark tones bring a dramatic edge', "
                  "with a 'gentle sheen'. Brizo's finish swatch reads sRGB 72,72,70 under studio light; the product picture shows a "
                  "dark matte coat. A coating: Opaque parent, sRGB 40,40,39, roughness 0.5. ")
    add("Metal_-_Brizo_-_Matte_Black", coat((40, 40, 39), 0.5), black_note + photo % (REF + "BL_swatch_Matte_Black_2024.jpg"), 4,
        "Finish name and sheen are the manufacturer's; colour from its swatch and product picture.", urls=URL_BRIZO_BL)
    add("Brizo_69080-BL_R2025_Finish", coat((40, 40, 39), 0.5),
        "Brizo 69080-BL 'Air Switch with Dual Outlet', finish Matte Black (BL). " + black_note +
        photo % (REF + "69080-BL_product_photo.png"), 4, "Product and finish are named on Brizo's page.", urls=URL_BRIZO_BL)
    add("Brizo_69080-BL_R2025_Detail", coat((24, 25, 26), 0.2),
        "Brizo 69080-BL air switch. The product picture shows a glossier black button inside the matte flange; the Revit family "
        "gives this part sRGB 24,25,26. Opaque parent, roughness 0.2. " + photo % (REF + "69080-BL_product_photo.png"), 4,
        "Colour from the family, sheen from the manufacturer's picture.",
        assumption="That 'Detail' is the glossy inner button is read from the product picture, not stated by Brizo.",
        urls=URL_BRIZO_BL)
    add("Kohler-Vitreous_China-0-White", coat((236, 235, 236), 0.08),
        "Kohler Verticyl K-8189: vitreous china, colour 0 White (Kohler spec sheet). Fired glaze: Opaque parent, white, roughness "
        "0.08.", 4, "Material and colour are stated by the manufacturer; a glaze is a plain, glossy finish.",
        urls="https://techcomm.kohler.com/techcomm/pdf/K-8189_spec_US-CA_Kohler_en.pdf (%s)" % READ)
    add("KOHLER-Acrylic-0-White", coat((236, 235, 236), 0.15),
        "Kohler Underscore K-1130: acrylic, colour 0 White (Kohler spec sheet). Glossy sanitary acrylic: Opaque parent, white, "
        "roughness 0.15.", 4, "Material and colour are stated by the manufacturer.",
        urls="https://techcomm.kohler.com/techcomm/pdf/K-1130_spec_US-CA_Kohler_en.pdf (%s)" % READ)
    add("Kohler-Lithocast-0-White", coat((236, 235, 236), 0.12),
        "Kohler Ceric K-8335: 'KOHLER Lithocast Gloss cast resin', colour 0 White (Kohler spec sheet). Opaque parent, white, "
        "roughness 0.12.", 4, "Material, gloss and colour are stated by the manufacturer.",
        urls="https://techcomm.kohler.com/techcomm/pdf/K-8335_spec_US-CA_Kohler_en.pdf (%s)" % READ)
    add("Kohler_K-77685-NA_R2025_Finish", coat((242, 243, 240), 0.4),
        "Kohler K-77685-NA Aquifer water filtration system: high-impact plastic; 'NA' means no finish applies (Kohler spec "
        "sheet). White moulded plastic in the family's colour, roughness 0.4.", 4,
        "Material is stated by the manufacturer; colour is the family's.", urls=URL_KOHLER_77685)
    add("Kohler_K-77685-NA_R2025_Gray", coat((131, 132, 130), 0.45),
        "Kohler K-77685-NA Aquifer filter: high-impact plastic (Kohler spec sheet); the family's grey part, roughness 0.45.", 4,
        "Material is stated by the manufacturer; colour is the family's.", urls=URL_KOHLER_77685)
    add("KOHLER-Metal-2GL-Brushed_Modern_Brass", metal((214, 178, 122), 0.32, brushed=True, anisotropy=-0.5),
        "Kohler finish 2GL 'Brushed Moderne Brass' on the Purist sconce K-27263-SC02 (Kohler spec sheet). Brushed warm brass: "
        "Metal parent, colour from Kohler's Revit family (sRGB 252,208,156) taken down to what brass reflects, brushed relief "
        "and roughness 0.32, highlight stretched across the brushing.", 4,
        "Finish code and name are the manufacturer's; the colour rests on Kohler's family, no swatch could be read (kohler.com "
        "refuses automated reading).", urls=URL_KOHLER_27263)
    add("KOHLER-Metal-BNL-Brushed_Nickel", metal((192, 186, 174), 0.34, brushed=True, anisotropy=-0.5),
        "Kohler finish BNL 'Brushed Nickel' on the Purist sconce (Kohler spec sheet K-27263-SC02). Nickel's warm grey, brushed "
        "relief, roughness 0.34.", 4,
        "Finish code and name are the manufacturer's; nickel's colour is known; no swatch could be read.", urls=URL_KOHLER_27263)
    stainless = ("Brizo finish SS 'Brilliance Stainless', a vapour-deposited (PVD) finish. Brizo's swatch reads sRGB 209,199,187 "
                 "and the product picture of 61365LF-C-SS shows a brushed, warm silver surface. Metal parent, that colour, brushed "
                 "relief and roughness 0.34, highlight stretched across the brushing. ")
    add("Metal_-_Brizo_-_Brilliance?_Stainless", metal((209, 199, 187), 0.34, brushed=True, anisotropy=-0.5),
        stainless + photo % (REF + "SS_swatch_Brilliance_Stainless_2024.jpg and 61365LF-C-SS_product_photo.png"), 4,
        "Finish name is the manufacturer's; colour and brushing are read from its swatch and product picture.", urls=URL_BRIZO_SS)
    add("Plumbing_-_Brizo_-_Pipes", metal((209, 199, 187), 0.34, brushed=True, anisotropy=-0.5),
        "The visible pipes of the Brizo Levoir tub filler and Frank Lloyd Wright faucet families; the family gives them the same "
        "colour as Brilliance Stainless (sRGB 207,201,194). " + stainless, 3,
        "Evidence missing: Brizo does not publish a finish for these family parts.",
        assumption="Taken as the same Brilliance Stainless as the family's matching colour.", urls=URL_BRIZO_SS)
    add("Metal_-_Brizo_-_Polished_Chrome", chrome(),
        "Brizo finish PC 'Polished Chrome' (product page T65722LF-PC); the product picture shows a mirror finish. Metal parent, "
        "chrome's reflectance, roughness 0.05. " + photo % (REF + "PC_swatch_Polished_Chrome_2024.jpg and T65722LF-PC_product_photo.png"),
        4, "Finish name is the manufacturer's; polished chrome is a plain, known finish.", urls=URL_BRIZO_PC)
    add("Metal_-_Brizo_-_Brilliance?_Black_Onyx", metal((84, 82, 73), 0.10),
        "Brizo finish BNX 'Brilliance Black Onyx', a vapour-deposited (PVD) finish. Brizo's swatch reads sRGB 81,80,70 and the "
        "product picture of T70198-BNX shows a polished dark warm metal with sharp reflections. Metal parent, roughness 0.10. " +
        photo % (REF + "BNX_swatch_Brilliance_Black_Onyx_2024.jpg and T70198-BNX_product_photo.png"), 4,
        "Finish name is the manufacturer's; colour and polish are read from its swatch and product picture.", urls=URL_BRIZO_BNX)
    add("Metal_-_Brizo_-_Internal_Pipe", metal((200, 160, 96), 0.4),
        "One hidden part inside a Brizo shower trim family; the family colours it signal orange (sRGB 255,128,0) to mark it. A "
        "waterway is brass: Metal parent, raw brass, roughness 0.4.", 3,
        "Evidence missing: the part is internal and Brizo publishes no finish for it.",
        assumption="Taken as raw brass because faucet waterways are brass.", urls=URL_BRIZO_PVD)

    # ---- the owner's rebuild rows ------------------------------------------------
    gypsum = ("Owner's note: all gypsum board is painted Benjamin Moore White Dove, eggshell. White Dove OC-17 is sRGB "
              "239,238,229 (light reflectance 83). Opaque parent: that colour, roughness 0.45 for eggshell, and the fine stipple a "
              "roller leaves (bumps of about 3 mm).")
    for key in ("09_23_00_Gypsum_Wall_Board", "Gypsum_Wall_Board"):
        add(key, coat(dove, 0.45, relief=eggshell, relief_size=(0.5, 0.5), strength=0.6), gypsum, 4,
            "Paint colour and sheen are named by the owner; the colour value is published.", urls=URL_DOVE)
    add("Door_-_Panel", coat(dove, 0.45),
        "Owner's note: all door panels are White Dove, eggshell. Same colour and roughness as the walls, sprayed smooth (no "
        "roller stipple).", 4, "Paint colour and sheen are named by the owner.", urls=URL_DOVE)
    add("Door_-_Frame", coat(dove, 0.45),
        "Owner's note on a keep row: 'same white dove paint as door panel'. Identical to Door_-_Panel.", 4,
        "Paint colour and sheen are named by the owner.", urls=URL_DOVE)
    oak = b.veneer("oak_veneer_02", "4k", "OakVeneer02", gain=2.5)
    add("Cabinet_Wood_Veneer", b.wood(oak, (1.0, 1.0), (201, 172, 137), turn=True, anti=True, rough=0.85),
        "Owner's note: 'seamless, non repeating texture of a rift cut white oak'. Poly Haven 'Oak Veneer 02' (straight, tight "
        "grain as rift cutting gives; 4,096 pixels over 1 m; its grain made 2.5 times stronger so that it reads at room distance), tinted to the pale neutral of unstained white oak, grain turned "
        "upright, and a second, shifted reading mixed in through a cloud pattern so that no repeat shows.", 4,
        "The owner named the finish; a sharp image at 4,096 pixels per metre.",
        assumption="Grain runs upright on every face (world mapping); the Revit model does not record grain direction per panel.",
        owner="Grain direction is upright on all cabinet faces, drawer fronts included; say if drawer fronts should run "
              "horizontally.", urls="https://polyhaven.com/a/oak_veneer_02 ; https://api.polyhaven.com/info/oak_veneer_02 (%s)" % READ)
    limestone_image = b.revit_texture("Indiana_Limestone_-_Full_Color_Blend")
    limestone_relief = b.revit_texture("Indiana_Limestone_-_Full_Color_Blend", "BumpMap")
    blend = b._own(mk.limestone_blend(b.generated))
    size = b.revit_field("Indiana_Limestone_-_Full_Color_Blend")

    def limestone():
        return {"parent": "StoneBlend",
                "scalars": {"SizeU_m": round(size[0], 4), "SizeV_m": round(size[1], 4), "RoughnessScale": 0.75,
                            "MacroSize_m": 24.4, "MacroColorAmount": 1.0, "MacroVariation": 0.03, "NormalStrength": 0.3},
                "vectors": {"Tint": [1.0, 1.0, 1.0, 1.0]},
                "textures": {"BaseColorMap": limestone_image, "NormalMap": limestone_relief, "MacroColorMap": blend},
                "switches": {"AntiRepeat": True, "UseMeshUV": False},
                "field": "%.3f by %.3f m fine image, under a 24.4 by 24.4 m zone image" % size,
                "source": REVIT + "; zone image: " + OWN, "rgb": None}
    lime_text = ("Polycor describes Indiana Limestone Full Color Blend as 'a natural, full range compilation of warm buff colors "
                 "and medium gray tones'. The Revit export's own 16K image (8,192 by 16,384 pixels over %.2f by %.2f m, an even tan) "
                 "gives the grain; a second, shifted reading mixed through a cloud pattern hides its repeat; and a zone image of "
                 "24.4 m, larger than any wall of the building, shifts it between buff and grey in long flat beds, so that no "
                 "part of a wall repeats another." % size)
    add("Indiana_Limestone_-_Full_Color_Blend", limestone(), "Owner's note: 'research full color blend limestone and create a "
        "material that doesn't repeat over large distances'. " + lime_text, 4,
        "The owner named the stone; the grain is a sharp image at 6,861 pixels per metre and the colour range is the quarry's "
        "published description.",
        assumption="Stone joints are not drawn: the Revit image has none and the model does not give a coursing.",
        owner="No stone joints are drawn (the export has no coursing). Give the panel size and joint width if joints are to "
              "show. Indiana_Limestone_-_Full_Color_Blend_2 (5 surfaces) is marked 'candidate', so it shows the Phase 5 "
              "candidate and will not match these walls exactly; say if it should be rebuilt the same way.", urls=URL_LIME)
    add("Indiana_Limestone_-_Full_Color_Blend_Seamless", limestone(), "No owner's note; same stone as "
        "Indiana_Limestone_-_Full_Color_Blend by its Revit name, so it is rebuilt identically. " + lime_text, 4,
        "Same named stone as the row the owner asked to rebuild.", urls=URL_LIME)
    taj_source = (b.params["Taj_Mahal_Polished_-_Quartzite__UF4F70_"]["textures"]["DiffuseMap"].get("source_file") or "").replace("\\", "/")
    taj = b._own(mk.seamless_crop(taj_source, b.generated, "T_W1529_P12_TajMahal_C", band=0.12))
    taj_field = tuple(v * 0.88 for v in b.revit_field("Taj_Mahal_Polished_-_Quartzite__UF4F70_"))
    b.made[-1][2] = "%.3f by %.3f m" % taj_field

    def taj_recipe(rough):
        return {"parent": "Opaque", "scalars": {"SizeU_m": round(taj_field[0], 4), "SizeV_m": round(taj_field[1], 4),
                                                "RoughnessScale": rough, "MacroVariation": 0.03},
                "vectors": {"Tint": [1.0, 1.0, 1.0, 1.0]}, "textures": {"BaseColorMap": taj},
                "switches": {"AntiRepeat": True, "UseMeshUV": False}, "field": "%.3f by %.3f m" % taj_field,
                "source": REVIT + ", made seamless by tools/phase12_make_textures.py", "rgb": None}
    add("Taj_Mahal_Polished_-_Quartzite__UF4F70_", taj_recipe(0.08),
        "Decision rebuild, no note; the Revit name gives the stone and the finish: Taj Mahal quartzite, polished. The export's "
        "own slab image (1,383 by 1,800 pixels over 1.00 by 1.30 m) had a visible seam; its edges are faded into each other "
        "(12 % band) and a second, shifted reading is mixed in so that the 0.88 by 1.14 m field does not show on a 5 m top. "
        "Polished: roughness 0.08, no relief.", 4,
        "Stone and finish are named in the Revit material; the image is the export's own at 1,383 pixels per metre.",
        owner="Counter_Top is honed by your note while this material stays polished by its name; say if every Taj Mahal top "
              "should be honed.", urls=URL_TAJ)
    add("Counter_Top", taj_recipe(0.40),
        "Owner's note: 'make a taj mahal quartzite material, honed finish'. The same seamless Taj Mahal image as "
        "Taj_Mahal_Polished_-_Quartzite; honed is a smooth matte surface with low sheen: roughness 0.40, no relief.", 4,
        "The owner named stone and finish.", urls=URL_TAJ)
    add("07_46_00_JH_LAP_SIDING", coat((45, 46, 48), 0.75, relief=TEX + "T_W1529_Siding_N", relief_size=(1.0, 0.1778)),
        "Owner's note: 'lap siding in a dark charcoal almost black matte painted finish'. James Hardie lap siding by the Revit "
        "name: plain charcoal sRGB 45,46,48, roughness 0.75, and the Phase 5 lap relief at a 7 inch (178 mm) exposure.", 4,
        "The owner named colour and sheen; lap siding is a plain painted board.",
        assumption="Board exposure of 7 inches (the common HardiePlank 8.25 inch board); the Revit material does not give it.",
        owner="The siding exposure is assumed 7 inches; give the board size if different.")
    b.files[TEX + "T_W1529_Siding_N"] = os.path.join(b.root, "review", "phase5", "generated_textures", "T_W1529_Siding_N.png").replace("\\", "/")
    add("Aluminum_-_Milgard_-_Bronze_Anodized", coat((43, 32, 23), 0.6),
        "Owner's note: 'should be a matte finish, same color as revit material'. Revit colour sRGB 43,32,23 kept; matte: "
        "roughness 0.6. Dark anodising reads as a coloured coat, so the Opaque parent.", 4,
        "The owner named colour and sheen.")
    add("z_Miele_Design_OBSW", metal((54, 54, 56), 0.08),
        "Owner's note: 'dark black polished metal'. Miele 'Obsidian Black' by the family's name (OBSW). Metal parent, very dark "
        "(sRGB 54,54,56 as a mirror colour), roughness 0.08.", 4, "The owner named the finish.")
    add("z_Miele_Design_Glass_Black", glass((28, 28, 30), 0.78, 0.95, 0.03),
        "Owner's note: 'black look of candidate is good but needs to be transparent glass'. Glass parent, near-black tint, 78 % "
        "opacity face-on so that it reads black yet shows what is behind it, mirror-smooth.", 4,
        "The owner named the finish.",
        owner="The oven glass is 78 % opaque face-on (dark tinted glass); say if more should be seen through it.")
    add("z_Miele_Design_Zinc_Steel", metal((206, 208, 210), 0.28),
        "Owner's note: 'should be a brighter lighter metal'. Metal parent, bright steel sRGB 206,208,210 (Revit had 150), "
        "roughness 0.28.", 4, "The owner named the direction; a plain bright metal.")
    add("Betafence_LeafMaterial", coat((30, 30, 30), 0.5),
        "Owner's note: 'fences are a painted black steel'. Opaque parent, black paint sRGB 30,30,30, roughness 0.5. Revit showed "
        "this leaf as 55 % clear glass.", 4, "The owner named the finish.",
        owner="The gate leaf is one flat sheet in the model; painted black it reads as a solid black panel, not as a mesh of "
              "wires. A wire-mesh look would need a cut-out image or new geometry.")
    add("Alminium_White", coat((238, 238, 236), 0.4),
        "No note. On the housings of 18 ORN recessed downlights (Lighting Fixtures). Revit: white, full gloss. A white powder "
        "coat on aluminium is what such trims carry: Opaque parent, white, roughness 0.4.", 3,
        "Evidence missing: the luminaire maker's finish sheet.", assumption="White powder coat, satin, inferred from the fixture type.")
    add("vluchtweg_wit", light((240, 240, 240), 50, 6500, rough=0.4),
        "No note. The lit face of the same 18 ORN downlights; Revit gives it 50 candela per square metre at 6,500 K. Emissive "
        "parent with those numbers.", 4, "Luminance and colour temperature are the Revit family's own numbers.")
    add("Cedar", b.wood(b.ambient("Wood049"), (0.8, 0.8), (168, 112, 78), turn=True, anti=True, rough=0.9, source=CC0_ACG + ", set Wood049"),
        "No note. On 6x6 timber columns (Structural Columns). ambientCG Wood049 tinted to the red-brown of western red cedar, "
        "grain along the column, second reading mixed in against repeats.", 3,
        "Evidence missing: a cedar image; a general softwood image is tinted, which gives the colour but not cedar's own figure.",
        assumption="Species colour of western red cedar, clear finish; grain upright.")
    add("Gola_-_Black_Plastic_Mounting_Clips", by("Gola_-_Black_Plastic_Mounting_Clips", "coat", rough=0.45),
        "No note. Mounting clips of the Richelieu Gola handle channel; the name says black plastic. Revit colour kept, "
        "roughness 0.45.", 4, "The name states material and colour.")
    add("Black_-_Metal_Finish", coat((28, 28, 28), 0.35),
        "No note. Frames of JELD-WEN awning windows; Revit: black, gloss 0.75. Factory black coat on metal: Opaque parent, "
        "roughness 0.35.", 4, "The name states the finish; gloss from the family.")
    add("Trinity_-_Black_Metal_Finish", by("Trinity_-_Black_Metal_Finish", "coat", rough=0.55),
        "No note. Kuzco Trinity pendant; the family gives black with gloss 0.45. Black coat, roughness 0.55.", 4,
        "The name states the finish; gloss from the family.")
    brushed_steel = ("Brushed stainless steel: Metal parent, sRGB 202,200,196, brushed relief and roughness 0.35, highlight "
                     "stretched across the brushing.")
    add("Metal_-_Stainless_Steel", metal((202, 200, 196), 0.35, brushed=True, anisotropy=-0.5),
        "No note. Miele PW 6080 washer housing; the name says stainless steel. " + brushed_steel, 4,
        "The name states the metal; appliance stainless is brushed.")
    add("Metal_-_Stainless", metal((202, 200, 196), 0.35, brushed=True, anisotropy=-0.5),
        "No note. Lift doors (side-opening elevator door family); the name says stainless. " + brushed_steel, 4,
        "The name states the metal; lift doors are brushed stainless as a rule.",
        assumption="Brushed (No. 4) rather than mirror stainless.")
    add("Chrome_Plating", chrome(0.06),
        "No note. Trim of the same lift doors; the name says chrome plating. Metal parent, chrome, roughness 0.06.", 4,
        "The name states the finish.")
    add("Steel_-_DELTA_-_Brilliance_Stainless", metal((209, 199, 187), 0.34, brushed=True, anisotropy=-0.5),
        "No note. Shower family parts named for Delta's Brilliance Stainless, the same finish family as Brizo's (Brizo is "
        "Delta's brand). " + stainless, 4, "The name states the finish; colour and brushing from the Brizo swatch and picture.",
        urls=URL_BRIZO_SS)
    add("Aluminium_Chalk__721", coat((232, 229, 222), 0.55),
        "No note. Kettal Park Life centre tables; Kettal's aluminium colour 721 'Chalk' by the name. A warm off-white powder "
        "coat: sRGB 232,229,222, roughness 0.55.", 3,
        "Evidence missing: Kettal's colour chip for 721 Chalk was not read.",
        assumption="Chalk taken as a warm off-white, matte powder coat.")

    # ---- blank rows -----------------------------------------------------------------
    def plain(key, kind, text, rough=None, colour=None, confidence=4, reason=None, assumption="", owner="", brushed=False):
        name = [n for n in b.worklist if fnmatch.fnmatchcase(n, key)][0]
        rgb, gloss = b.revit_rgb(name), b.gloss(name)
        recipe = by(name, kind, rough=rough, colour=colour, brushed=brushed)
        basis = "No note. %s Revit family values: sRGB %d,%d,%d, glossiness %.2f. %s parent, roughness %.2f." % (
            text, rgb[0], rgb[1], rgb[2], gloss, recipe["parent"], recipe["scalars"]["RoughnessScale"])
        if reason is None:
            reason = ("A plain finish; colour and gloss are stated by the Revit family." if confidence >= 4 else
                      "Evidence missing: a maker's finish sheet; the values are the Revit family's.")
        add(key, recipe, basis, confidence, reason, assumption=assumption, owner=owner)

    def lamp(key, text, rough=0.3):
        name = [n for n in b.worklist if fnmatch.fnmatchcase(n, key)][0]
        scalars = b.params[name]["scalars"]
        cd, kelvin = scalars["SelfIlluminationLuminance"], scalars.get("SelfIlluminationColorTemperature", 6500.0) or 6500.0
        add(key, light(b.revit_rgb(name), cd, kelvin, rough),
            "No note. %s Revit gives it a luminance of %d candela per square metre at %d K; Emissive parent with those numbers." % (
                text, cd, kelvin), 4, "Luminance and colour temperature are the Revit family's own numbers.")

    lamp("EAE_LED", "LED face of 22 EAE Kanoled luminaires.")
    lamp("Glass_-_Visual_Comfort___Co__-_LED_Lens", "LED lens of the Visual Comfort wall lights.", rough=0.2)
    lamp("Acrylic_-_Lumenwerx_-_White", "Acrylic diffuser of the Lumenwerx surface light.", rough=0.4)
    lamp("Acrylic_-_Lumenwerx_-_Frosted", "Frosted acrylic diffuser of the Lumenwerx recessed light.", rough=0.5)
    lamp("Courcelette_-_Bulb_Finish", "Lamps of the DVI Courcelette chandelier.", rough=0.15)
    lamp("Focus_4_Clear_Acrylic_Lens", "Lens of the DCW Focus 4 light.", rough=0.15)
    lamp("Focus_4_LED_Emitter_2700K", "LED emitter of the DCW Focus 4 light.")
    plain("FARO_Black", "coat", "Faro Punt socket parts; black.", rough=0.45)
    plain("FARO_Black_Matt", "coat", "Faro Punt socket parts; the name says matt black.", rough=0.6)
    add("FARO_Cromo_C", chrome(), "No note. Faro Punt socket trim; 'Cromo' is chrome. Metal parent, chrome, roughness 0.05.", 4,
        "The name states the finish.")
    plain("Fixture_80019-ISE_R2025_Detail", "coat", "Dark plastic detail of the under-sink fixture family 80019-ISE.", rough=0.5)
    plain("Fixture_80019-ISE_R2025_Gray", "coat", "Grey plastic body of the under-sink fixture family 80019-ISE.", rough=0.5)
    plain("G_5051_SCVi_ADA_Black_Finish", "coat", "Black plastic of the Miele G 5051 SCVi dishwasher.", rough=0.5)
    plain("G_5051_SCVi_ADA_Display_Finish", "coat", "Display strip of the Miele G 5051 SCVi dishwasher; a glossy dark window.",
          rough=0.15)
    plain("G_5051_SCVi_ADA_Panel_Finish", "metal", "Control panel of the Miele G 5051 SCVi dishwasher; Miele panels are brushed "
          "stainless steel.", rough=0.35, colour=(202, 200, 196), brushed=True, confidence=3,
          assumption="Brushed stainless steel, from the appliance type; the family only gives a grey.")
    plain("KM3054_Burner_Finish", "coat", "Burner caps of the Miele KM 3054-1 gas cooktop; matt enamel.", rough=0.6)
    plain("KM3054_Burner_Ring_Finish", "metal", "Burner rings of the Miele gas cooktop; bare aluminium alloy.", rough=0.4)
    plain("KM3054_Grate_Finish", "coat", "Pan supports of the Miele gas cooktop; matt enamelled cast iron.", rough=0.7)
    plain("KM3054_Housing_Finish", "metal", "Housing of the Miele gas cooktop; stainless steel.", rough=0.35,
          colour=(202, 200, 196), brushed=True)
    plain("KM3054_Top_Finish", "coat", "Top of the Miele KM 3054-1 cooktop; black, full gloss in the family: black ceramic glass.",
          rough=0.06, colour=(20, 20, 20))
    plain("Porcelain__Ivory", "coat", "Glazed ivory porcelain of the shower family.", rough=0.1)
    plain("00_Trim_2_Color_White", "coat", "White trim paint on casework and pocket doors.", rough=0.5)
    plain("00_Trim_2_Color_White_1_", "coat", "White paint named as trim colour, on three generic floor slabs of the shell.",
          rough=0.5, owner="This white trim paint is on three 10 inch floor slabs of the shell (up to 21.5 by 12.9 m); check that "
                           "a painted white floor is intended.")
    plain("00_Soffit_2_Color_White", "coat", "White soffit paint; on one surrounding-building stand-in.", rough=0.6)
    plain("Betafence_AnthraciteRAL7016", "coat", "Betafence gate parts in RAL 7016 anthracite grey (the Revit colour 56,62,66 is "
          "RAL 7016).", rough=0.5)
    plain("Metal_-_LG_Electronics_-_Black", "coat", "Painted black metal back of the LG display.", rough=0.5)
    plain("Plastic_-_LG_Electronics_-_Black", "coat", "Glossy black plastic and screen face of the LG display.", rough=0.2)
    add("Metal_-_Waterworks_-_Chrome", chrome(), "No note. Waterworks bath and shower fittings; the name says chrome.", 4,
        "The name states the finish.")
    plain("White_RAL_9010", "coat", "Bandalux drapery track in RAL 9010 pure white (the Revit colour 241,236,225 is RAL 9010).",
          rough=0.4)
    add("41747XXX_AddStoris_Bath_towel_rail*", metal((224, 190, 120), 0.07),
        "No note. Hansgrohe AddStoris bath towel rail 41747, finish 990 = 'Polished Gold Optic' (648 mm long, as the model's "
        "part). A polished gold-coloured vapour-deposited finish: Metal parent, gold sRGB 224,190,120, roughness 0.07.", 4,
        "Article and finish code are named in the Revit material and confirmed on dealers' pages; a polished plain metal.",
        owner="hansgrohe.com refuses automated reading, so the finish name rests on three dealers' pages for article 41747990.",
        urls=URL_HG_990)
    plain("ARCAT_-_Finish_-_Interior_Paint", "coat", "Interior paint on two generic models.", rough=0.5)
    plain("Aluminum-PlyGem-White", "coat", "White factory coat on the Ply Gem bypass door frames.", rough=0.35)
    plain("Aluminum_-_Matte_Black_Powdercoat", "coat", "Matte black powder coat on the front facade metalwork and a floor edge.",
          rough=0.6)
    add("Ash", b.wood(b.veneer("ash_veneer", "2k", "AshVeneer"), (1.0, 1.0), (214, 190, 156), turn=False, anti=True, rough=0.9),
        "No note. Fronts of the primary bath vanities; the Revit name says ash. Poly Haven 'Ash Veneer' (2,048 pixels over 1 m) "
        "tinted to pale natural ash, second reading mixed in against repeats.", 4,
        "The name states the species; a sharp image at 2,048 pixels per metre.",
        assumption="Natural pale ash with a clear finish; grain horizontal.",
        urls="https://polyhaven.com/a/ash_veneer ; https://api.polyhaven.com/info/ash_veneer (%s)" % READ)
    plain("BNQ26_Satin_Warm_Bronze", "metal", "Legs of the custom BNQ26 table; the name says satin warm bronze.", rough=0.38,
          brushed=True)
    plain("Courcelette_-_Graphite_Finish", "coat", "Frame of the DVI Courcelette chandelier in the maker's Graphite finish.",
          rough=0.5)
    add("ETH_Concrete_LightGreyVarnished", b.wood(b.ambient("Concrete046"), (2.4, 2.4), (192, 192, 192), anti=False, rough=0.55,
                                                  macro=0.05, strength=2.0, source=CC0_ACG + ", set Concrete046"),
        "No note. Top of the Ethnicraft outdoor dining table; the name says light grey varnished concrete. ambientCG Concrete046 "
        "tinted to the Revit grey (sRGB 192,192,192), roughness lowered for the varnish.", 4,
        "The name states material, colour and coating; a sharp image.")
    add("ETH_Oak_Natural", b.wood(oak, (1.0, 1.0), (205, 172, 130), turn=False, anti=True, rough=0.85),
        "No note. Ethnicraft RollerMax tables; the name says natural oak. Poly Haven 'Oak Veneer 02' tinted to natural oiled oak, "
        "second reading mixed in against repeats.", 4, "The name states species and finish; a sharp image.",
        urls="https://polyhaven.com/a/oak_veneer_02 (%s)" % READ)
    plain("Focus_4_White_Aluminium", "coat", "White-coated aluminium body of the DCW Focus 4 light.", rough=0.6)
    plain("Herman_Miller_-_Finish_91_White", "coat", "Herman Miller finish 91 white on the Eames pieces.", rough=0.3)
    plain("Herman_Miller_-_Finish_BK_Black", "coat", "Herman Miller finish BK black on the Eames pieces.", rough=0.3,
          colour=(22, 22, 22))
    add("Herman_Miller_-_Finish_PA_Polished_Aluminum", metal((232, 234, 235), 0.10),
        "No note. Herman Miller finish PA 'polished aluminum' on the Eames pieces. Metal parent, aluminium's reflectance, "
        "roughness 0.10.", 4, "The name states the finish.")
    plain("Hot_Tub", "coat", "Shell of the hot tub (two casework parts); glossy white sanitary acrylic.", rough=0.2, confidence=3,
          assumption="White acrylic shell, from the object and its colour.")
    plain("Metal_-_Lumenwerx_-_Matte_Black", "coat", "Lumenwerx luminaire housing; the name says matte black (the family's gloss "
          "of 0.90 contradicts the name; the name is followed).", rough=0.6, colour=(34, 34, 34))
    plain("Metal_-_Lumenwerx_-_Matte_White", "coat", "Lumenwerx luminaire housing; the name says matte white (the family's gloss "
          "of 0.90 contradicts the name; the name is followed).", rough=0.6)
    plain("Metal_-_Lumenwerx_-_Black", "coat", "Lumenwerx recessed luminaire trim; black coat.", rough=0.5, colour=(34, 34, 34))
    add("Oak_Veneered_MDF__1Z2XY2_", b.wood(oak, (1.0, 1.0), (196, 160, 118), turn=False, anti=True, rough=0.85),
        "No note. Two oak canopies of 5.5 by 2.8 m (LR26 Oak Canopy). The export's own image covers 0.40 by 0.55 m and would "
        "repeat about 14 times across; it is replaced by Poly Haven 'Oak Veneer 02' over 1 m with a second reading mixed in, "
        "tinted to the mean colour of the export's image.", 4,
        "The name states the finish; a sharp image at 4,096 pixels per metre.",
        assumption="The plank joints of the export's image are not kept; the canopy reads as continuous veneer.",
        urls="https://polyhaven.com/a/oak_veneer_02 (%s)" % READ)
    plain("Parking_Stripe", "coat", "Painted parking stripe, traffic yellow.", rough=0.7)
    plain("Steel_ASTM_A992", "metal", "Two W12 steel beams (Structural Framing). Bare rolled steel as the Revit colour shows it.",
          rough=0.55, colour=(150, 152, 155), confidence=3,
          reason="Evidence missing: whether the beams are left bare, primed or painted.",
          assumption="Bare rolled steel, mid grey.", owner="Two exposed W12 beams are shown as bare grey steel; say if they are "
                                                             "painted.")
    plain("TF27_Recess_Bed", "coat", "Bed of the TF27 recessed firebox; matt dark.", rough=0.7)
    plain("TF27_Recess_Graphite", "coat", "Graphite parts of the TF27 recessed firebox; matt.", rough=0.7)
    plain("TF27_Recess_Liner", "coat", "Liner of the TF27 recessed firebox; matt dark.", rough=0.7)
    plain("Talis_N_-_Aerator_Dark", "coat", "Dark plastic aerator insert of the Talis N faucet.", rough=0.5)
    plain("Talis_N_Aerator_Finish", "coat", "Aerator of the Talis N faucet.", rough=0.5)
    add("Talis_N_Faucet_Finish", chrome(),
        "No note. Body of the Talis N bath faucet family (2 surfaces). The same family carries 'Talis_N_-_Polished_Chrome'; the "
        "body is taken as polished chrome: Metal parent, chrome, roughness 0.05.", 3,
        "Evidence missing: the article number, which would fix the finish.",
        assumption="Polished chrome, the standard finish of the range.")
    plain("Talis_N_Mounting_Hardware_Finish", "metal", "Hidden mounting hardware of the Talis N faucet; plain steel.", rough=0.45)
    maple = b.veneer("white_maple_veneer", "2k", "WhiteMapleVeneer")
    add("ViewRail_-_Wood_-_Birch", b.wood(maple, (1.0, 1.0), (222, 196, 160), turn=False, anti=True, rough=0.85),
        "No note. Treads of the ViewRail stair (Specialty Equipment, 4.3 by 3.7 m part); the name says birch. No public-domain "
        "birch set was found; Poly Haven 'White Maple Veneer', a close pale, fine-grained wood, is tinted to natural birch.", 3,
        "Evidence missing: a birch image; maple stands in for it.", assumption="Maple image tinted to birch; clear finish.",
        urls="https://polyhaven.com/a/white_maple_veneer ; https://api.polyhaven.com/info/white_maple_veneer (%s)" % READ)
    add("Wood_-_Bernhardt_Design_-_Maple", b.wood(maple, (1.0, 1.0), (196, 166, 130), turn=False, anti=True, rough=0.8),
        "No note. Frames of the Bernhardt Design lounge chairs; the name says maple. Poly Haven 'White Maple Veneer' tinted "
        "towards the family's colour (sRGB 157,134,109 lightened to a natural maple).", 4,
        "The name states the species; a sharp image at 2,048 pixels per metre.",
        urls="https://polyhaven.com/a/white_maple_veneer (%s)" % READ)
    plain("ARCAT_-_Ceramic_-_Porcelain_-_White_Glaze", "coat", "White glazed porcelain on one partition face.", rough=0.1)
    add("ARCAT_-_Glass_-_Mirror", metal((235, 237, 236), 0.02),
        "No note. A mirror on one partition (3.3 by 1.7 m). Metal parent at 92 % reflectance, roughness 0.02: a mirror is a "
        "silvered face behind glass.", 4, "The name states the finish.")
    add("ARCAT_-_Wood_-_Douglas_Fir", b.wood(b.ambient("Wood049"), (0.8, 0.8), (212, 179, 113), turn=True, anti=True, rough=0.9,
                                             source=CC0_ACG + ", set Wood049"),
        "No note. One foyer cabinet part; the name says Douglas fir. ambientCG Wood049 tinted to the family's colour (sRGB "
        "212,179,113), grain upright.", 3, "Evidence missing: a Douglas fir image; a general softwood image is tinted.",
        assumption="General softwood grain tinted to the family's colour.")
    plain("Aluminium_-_black", "coat", "Black-coated aluminium on one floor edge part of the shell.", rough=0.4, confidence=3,
          assumption="Black coat with a satin sheen; the family says full gloss, which no architectural aluminium coat has.")
    plain("Beverage_Faucet_-_Seam_Finish", "coat", "Dark seam line of the beverage faucet family.", rough=0.6)
    tpo = ("On one roof part named 'Basic Roof Generic 8in w TPO': a white TPO roofing membrane, matt.")
    plain("EPP_White_Plastic", "coat", tpo, rough=0.6, confidence=3, assumption="White TPO membrane, from the roof type's name.")
    plain("white_plastic", "coat", tpo, rough=0.6, confidence=3, assumption="White TPO membrane, from the roof type's name.")
    kitkat = "Kit_Kat_Speckle__Stack__HE8CGJ_"
    kit_size = b.revit_field(kitkat)
    add(kitkat, {"parent": "Opaque",
                 "scalars": {"SizeU_m": round(kit_size[0], 4), "SizeV_m": round(kit_size[1], 4), "RoughnessScale": 0.25,
                             "NormalStrength": 1.0},
                 "vectors": {"Tint": [1.0, 1.0, 1.0, 1.0]},
                 "textures": {"BaseColorMap": b.revit_texture(kitkat), "NormalMap": b.revit_texture(kitkat, "BumpMap")},
                 "switches": {"UseMeshUV": True, "AntiRepeat": False}, "field": "%.3f by %.3f m" % kit_size, "source": REVIT,
                 "rgb": None},
        "No note. One casework face of 1.9 by 1.5 m. 'Kit Kat' finger mosaic, stacked; the export's own image (2,048 by 4,028 "
        "pixels over %.2f by %.2f m, 13 by 4 tiles) and its relief image are kept at Revit's size on the mesh's own mapping so "
        "that tiles stay whole at the edges. Glazed: roughness 0.25. Relief: joints about 1.5 mm deep." % kit_size, 4,
        "A sharp image of a named tile at 6,800 pixels per metre.",
        assumption="Glazed surface (the family's glossiness of 0 would make a chalk-dry tile).")
    larv = "Larvikite_Stack_192_8_x_145_2_inches__M2MLUQ_"
    larv_source = (b.params[larv]["textures"]["DiffuseMap"].get("source_file") or "").replace("\\", "/")
    larv_image = b._own(mk.resample(larv_source, b.generated, "T_W1529_P12_Larvikite_C", (8192, 4096)))
    larv_size = b.revit_field(larv)
    b.made[-1][2] = "%.3f by %.3f m" % larv_size
    add(larv, {"parent": "Opaque",
               "scalars": {"SizeU_m": round(larv_size[0], 4), "SizeV_m": round(larv_size[1], 4), "RoughnessScale": 0.3,
                           "NormalStrength": 0.5},
               "vectors": {"Tint": [1.0, 1.0, 1.0, 1.0]},
               "textures": {"BaseColorMap": larv_image, "NormalMap": b.revit_texture(larv, "BumpMap")},
               "switches": {"UseMeshUV": True, "AntiRepeat": False}, "field": "%.3f by %.3f m" % larv_size, "source": REVIT,
               "rgb": None},
        "No note. One floor of 11.1 by 2.6 m. Larvikite slabs, stacked; the export's own image of %.2f by %.2f m. Datasmith had "
        "reduced it to 4,096 by 4,096 pixels (839 pixels per metre across); the original 6,000 by 4,519 pixel file is brought "
        "in again at 8,192 by 4,096, which keeps its full 1,230 pixels per metre. Polished-to-honed stone: roughness 0.3." % larv_size,
        4, "A sharp image of a named stone at 1,230 pixels per metre.")
    plain("Matte_Black", "coat", "One casework part; the name says matte black (the family's full gloss contradicts the name; "
          "the name is followed).", rough=0.6, colour=(34, 34, 34))
    plain("Metal_-_Moen_-_Black", "coat", "Moen shower parts in black; Moen's black is a matte coat.", rough=0.5, colour=(34, 34, 34))
    add("Metal_-_Moen_-_Chrome", chrome(), "No note. Moen shower parts; the name says chrome.", 4, "The name states the finish.")
    plain("Pablo_Sky_Dome_18_Pendant_Black_Aluminum_R2025_Alumi*", "metal", "Inner aluminium face of the Pablo Sky Dome pendant; "
          "spun aluminium.", rough=0.22)
    plain("Pablo_Sky_Dome_18_Pendant_Black_Aluminum_R2025_Black*", "coat", "Black outer coat of the Pablo Sky Dome pendant.",
          rough=0.6)
    plain("XAL_DIFFUSE", "coat", "Diffuser of the XAL Ino circle luminaire; the family gives it no luminance, so it is an unlit "
          "white opal sheet.", rough=0.5, owner="XAL_DIFFUSE has no luminance in the Revit family, so the diffuser does not glow; "
                                                 "give a value if it should.")
    plain("XAL_PURE_WHITE", "coat", "Body of the XAL Ino circle luminaire in the maker's 'pure white' coat.", rough=0.5)


def kind_of(row):
    name, decision, note = row["material"], row["decision"].strip(), row["owner_note"].strip()
    if BRAND.search(name):
        return "brand name"
    if decision == "rebuild":
        return "rebuild"
    if decision == "":
        return "blank"
    if decision == "keep" and note:
        return "keep with a note"
    return decision


COLUMNS = ["material", "group", "decision_read", "owner_note_read", "read_at", "family", "action", "revit_asset",
           "active_asset", "parent", "scalars", "vectors", "textures", "switches", "physical_field_size",
           "source_and_licence", "what_the_finish_rests_on", "sources_read", "assumption", "confidence",
           "confidence_reason", "for_the_owner", "image_pixels", "pixels_per_metre", "largest_surface_in_the_model_m",
           "surfaces_using_it", "fields_across_the_largest_surface", "large_scale_unevenness", "tiling_result",
           "grazing_light_result", "passes", "wrap_previews", "swatch_sheet", "state"]


def main(root):
    root = os.path.abspath(root).replace("\\", "/")   # the editor reads these paths from another folder
    b = Book(root)
    with open(os.path.join(root, "material_audit.csv"), encoding="utf-8-sig", newline="") as handle:
        audit = list(csv.DictReader(handle))
    with open(os.path.join(root, "material_candidates.csv"), encoding="utf-8", newline="") as handle:
        candidates = {row["material"]: row for row in csv.DictReader(handle)}
    with open(os.path.join(root, "material_tests.csv"), encoding="utf-8", newline="") as handle:
        tests5 = {row["material"]: row for row in csv.DictReader(handle)}
    tests, state = {}, {}
    for name, target in (("tests.json", tests), ("state.json", state)):
        path = os.path.join(root, "review", "phase12", name)
        if os.path.exists(path):
            with open(path, encoding="utf-8") as handle:
                target.update(json.load(handle))
    groups = {row["material"]: kind_of(row) for row in audit}
    b.worklist = [row["material"] for row in audit
                  if groups[row["material"]] in ("brand name", "rebuild", "blank", "keep with a note")
                  and row["material"] not in MARKERS and row["material"] != "EAE_Logo"]
    write_recipes(b)
    missing = [n for n in b.worklist if n not in b.recipes]
    if missing:
        raise SystemExit("no recipe for: " + ", ".join(missing))
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    rows, editor = [], {"rebuild": [], "candidates": [], "imports": [], "left": []}
    for row in audit:
        name, group = row["material"], groups[row["material"]]
        if group == "keep":
            continue
        use = b.uses.get(name, {})
        used_on = describe_use(use)
        largest = use.get("largest_m", [0, 0])
        out = dict.fromkeys(COLUMNS, "")
        out.update({"material": name, "group": group, "decision_read": row["decision"].strip(),
                    "owner_note_read": row["owner_note"].strip(), "read_at": now, "family": row["family"],
                    "revit_asset": row["asset_path"], "surfaces_using_it": use.get("slots_mesh", 0),
                    "largest_surface_in_the_model_m": "%.2f x %.2f" % tuple(largest) if use else ""})
        if name in MARKERS or name == "EAE_Logo":
            reason = MARKERS.get(name, "Revit shows this logo plate 99 % transparent and the export has no artwork for it; "
                                       "any opaque finish would put dark plates on 46 luminaire faces that Revit shows clear")
            out.update({"action": "left as exported", "active_asset": row["asset_path"],
                        "what_the_finish_rests_on": "Not rebuilt: " + reason + ". Used on: " + (used_on or "no surface") + ".",
                        "confidence": row["confidence"], "confidence_reason": "Not a finish to rebuild." if name in MARKERS
                        else "Evidence missing: the logo artwork.",
                        "for_the_owner": "" if name in MARKERS else "EAE_Logo is left as exported (99 % clear); supply the logo "
                        "artwork if it is to show.", "passes": "not applicable", "tiling_result": "not applicable",
                        "grazing_light_result": "not applicable", "state": "left as exported"})
            editor["left"].append(name)
        elif group == "candidate":
            cand, test = candidates[name], tests5.get(name, {})
            out.update({"action": "Phase 5 candidate made active", "active_asset": cand["candidate_asset"],
                        "parent": cand["parent"], "scalars": cand["scalars"], "vectors": cand["vectors"],
                        "textures": cand["textures"], "switches": cand["switches"],
                        "physical_field_size": cand["physical_field_size"], "source_and_licence": cand["source_and_licence"],
                        "what_the_finish_rests_on": "Owner's decision 'candidate'. " + cand["what_it_rests_on"],
                        "confidence": cand["confidence"],
                        "confidence_reason": "Phase 5 score of the candidate; not rebuilt in this phase.",
                        "for_the_owner": cand["for_the_owner"], "image_pixels": test.get("image_pixels", ""),
                        "pixels_per_metre": test.get("pixels_per_metre", ""),
                        "fields_across_the_largest_surface": test.get("fields_across_the_largest_surface", ""),
                        "large_scale_unevenness": test.get("large_scale_unevenness", ""),
                        "tiling_result": test.get("tiling_result", ""),
                        "grazing_light_result": test.get("grazing_light_result", ""),
                        "passes": (test.get("passes", "") + " (Phase 5 test of the candidate)").strip(),
                        "wrap_previews": test.get("wrap_previews", "")})
            editor["candidates"].append({"material": name, "revit": row["asset_path"].split(".")[0],
                                         "asset": cand["candidate_asset"]})
        else:
            recipe = b.recipes[name]
            asset = REBUILT + slug(name)
            rests = recipe["rests"] + " Used on: " + used_on + "."
            out.update({"action": "rebuilt", "active_asset": asset, "parent": PARENTS[recipe["parent"]],
                        "scalars": json.dumps(recipe["scalars"], sort_keys=True),
                        "vectors": json.dumps(recipe["vectors"], sort_keys=True),
                        "textures": json.dumps(recipe["textures"], sort_keys=True),
                        "switches": json.dumps(recipe["switches"], sort_keys=True),
                        "physical_field_size": recipe["field"], "source_and_licence": recipe["source"],
                        "what_the_finish_rests_on": rests, "sources_read": recipe["urls"],
                        "assumption": recipe["assumption"], "confidence": recipe["confidence"],
                        "confidence_reason": recipe["reason"], "for_the_owner": recipe["owner"]})
            out.update(tests.get(name, {}))
            out["swatch_sheet"] = "review/phase12/swatches/sheets/%s.jpg" % slug(name)
            editor["rebuild"].append({"material": name, "revit": row["asset_path"].split(".")[0], "asset": asset,
                                      "parent": PARENTS[recipe["parent"]], "scalars": recipe["scalars"],
                                      "vectors": recipe["vectors"], "textures": recipe["textures"],
                                      "switches": recipe["switches"], "field": recipe["field"],
                                      "files": {k: b.files.get(v, "") for k, v in recipe["textures"].items()},
                                      "decision": row["decision"].strip(), "owner_note": row["owner_note"].strip(),
                                      "family": row["family"], "group": group, "rests": rests,
                                      "assumption": recipe["assumption"], "confidence": recipe["confidence"],
                                      "reason": recipe["reason"], "source": recipe["source"]})
        out["state"] = state.get(name, out["state"])
        rows.append(out)
    editor["imports"] = [[v[0], TEX.rstrip("/"), k.rsplit("/", 1)[-1], v[1]] for k, v in sorted(b.imports.items())]
    with open(os.path.join(root, "material_rebuild.csv"), "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    with open(os.path.join(root, "review", "phase12", "recipes.json"), "w", encoding="utf-8", newline="\n") as handle:
        json.dump(editor, handle, indent=1, sort_keys=True)
    with open(os.path.join(b.generated, "generated_textures.csv"), "w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["file", "kind", "physical_field_size", "what_it_is"])
        writer.writerows(sorted(b.made))
    counts = {}
    for out in rows:
        counts[out["action"]] = counts.get(out["action"], 0) + 1
    print(json.dumps({"rows": len(rows), "by_action": counts, "images_to_import": len(editor["imports"]),
                      "images_made": len(b.made)}))


if __name__ == "__main__":
    main(sys.argv[1])
