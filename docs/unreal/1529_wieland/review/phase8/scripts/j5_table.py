"""Phase 8, step J5: write review/phase8/fixture_table.csv, one row per fixture kind of the Revit model.

Runs outside the editor:   python -I -B j5_table.py

Every number in a row is either read from the photometric file named in the row (by tools/ies_read.py)
or typed here from the source named in the row. The value the editor is given is worked out here:
a light with a photometric file is set in candela, and that value is
    the file's largest candela x the lumens wanted / the lumens the file's own table adds up to.
Words: a fixture is one Revit lighting-fixture element; a light is one light source inside it.
"""
import csv
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import ies_read  # noqa: E402

EXPORT = "D:/Unreal_Engine_Projects/Wieland1527 5.9/ImportStaging/2026-11-11_export_2/25-006_1527_N_Wieland-3DView-3D_View_188_r2_Assets/"
PHOTO = "E:/Wieland1529_site_data/photometry/"
ASSETS = "/Game/Wieland1529/Lighting/Photometric/"
BEFORE = os.path.join(ROOT, "review", "phase8", "fixture_lights_before.csv")
OUT = os.path.join(ROOT, "review", "phase8", "fixture_table.csv")

MAKER_FILE = "maker's photometric file"
GENERIC = "generic shape made here (tools/ies_generic.py); no file is published for this product"

# One entry per kind. lumens None means: the lumens the file's own table adds up to.
# on: "largest" = only the fixture's main light is lit; "all" = every light; "none" = off.
# per: "light" = the lumens are for each light; "fixture" = for the fixture, shared in the model's proportions.
KINDS = [
    dict(family="Recessed_Can_Light_18377 2", type="Recessed_Can_Light_18377",
         maker="none named", model="Revit family 'Recessed Can Light' (no product)", status="placeholder: generic",
         file=PHOTO + "_generic_made_here/GENERIC_downlight_60deg.ies", asset="IES_GENERIC_downlight_60deg", file_kind=GENERIC,
         lumens=1800.0, lumens_source="the Revit family's own value for its main light (1,800 lm); the family's second light (100 lm) is left off",
         kelvin=3000, kelvin_source="the Revit light's value", on="largest", per="light", aim="down", radius=3.0,
         waits_on="Owner: name the downlight product. 1,800 lm is high for a residential downlight (700 to 1,100 lm is usual)."),
    dict(family="Recessed_Can_Light_18377 2", type="Recessed_Can_Light_G1-1",
         maker="none named", model="Revit family 'Recessed Can Light', type G1-1 (no product)", status="placeholder: generic",
         file=PHOTO + "_generic_made_here/GENERIC_downlight_60deg.ies", asset="IES_GENERIC_downlight_60deg", file_kind=GENERIC,
         lumens=1800.0, lumens_source="the Revit family's own value for its main light (1,800 lm); the second light (100 lm) is left off",
         kelvin=3000, kelvin_source="the Revit light's value", on="largest", per="light", aim="down", radius=3.0,
         waits_on="Owner: name the downlight product (garage level)."),
]

FOCAL = dict(family="Lighting_Fixture-Focal_Point-ID-3.5_Adjustable_Accent",
             maker="Focal Point", model="ID+ 3.5 in Adjustable Accent, FLCS3-RO-1900L-835K-VWFL", status="data sheet and maker's file",
             file=PHOTO + "FocalPoint/ID35_AdjustableAccent/FLCS3-RO-1900L-835K-VWFL-LCS3-RDO-VWFL-SL-CD.ies",
             asset="IES_FocalPoint_FLCS3_RO_1900L_835K_VWFL", file_kind=MAKER_FILE + ", downloaded from focalpointlights.com",
             lumens=None, lumens_source="the maker's file (1,442.6 lm); the data sheet FLCS3_RO__W.pdf gives 1,810 lm x 0.76 for the very wide flood = 1,444 lm, 22.4 W",
             kelvin=3500, kelvin_source="the type name (835K) and the data sheet", on="largest", per="light", aim="down", radius=2.0,
             waits_on="The fixture can be tilted; every one is aimed straight down until the owner says which are aimed at a wall.")
for type_name in ("FLCS3-RO-1900L-835K-VWFL-LCS3-RDO-VWFL-SL-D-2", "FLCS3-RO-1900L-835K-VWFL-LCS3-RDO-VWFL- C1-1",
                  "FLCS3-RO-1900L-835K-VWFL-LCS3-RDO-VWFL-SL-D-3"):
    KINDS.append(dict(FOCAL, type=type_name))

KOHLER_27263 = dict(family="Light_Fixture-Wall_Sconce-KOHLER-PURIST-K-27263",
                    maker="Kohler", model="Purist two-light sconce K-27263", status="placeholder: generic shape, assumed lamp",
                    file=PHOTO + "_generic_made_here/GENERIC_diffuse_globe.ies", asset="IES_GENERIC_diffuse_globe", file_kind=GENERIC,
                    lumens=800.0, lumens_source="assumed lamp: the data sheet K-27263-SC02 names two E26 sockets, 60 W maximum each, lamps not supplied and no lumens printed; 800 lm is a 60 W-equivalent LED lamp",
                    kelvin=3000, kelvin_source="the Revit light's value", on="all", per="light", aim="", radius=4.0,
                    waits_on="Owner: which lamps go in the sconces (lumens and colour temperature).")
KINDS.append(dict(KOHLER_27263, type="2GL-Brushed Modern Brass"))
KINDS.append(dict(KOHLER_27263, type="BNL-Brushed Nickel"))

KOHLER_32375 = dict(family="Light_Fixture-Wall_Sconce-KOHLER-PURIST-K-32375",
                    maker="Kohler", model="Purist one-light sconce K-32375", status="placeholder: generic shape, assumed lamp",
                    file=PHOTO + "_generic_made_here/GENERIC_diffuse_globe.ies", asset="IES_GENERIC_diffuse_globe", file_kind=GENERIC,
                    lumens=800.0, lumens_source="assumed lamp: the data sheet K-32375-SC01 names one E26 socket, 60 W maximum, lamp not supplied and no lumens printed; 800 lm is a 60 W-equivalent LED lamp",
                    kelvin=3000, kelvin_source="assumed with the lamp (the Revit light says 3,450 K, which no lamp is sold in)", on="all", per="light", aim="", radius=4.0,
                    waits_on="Owner: which lamp goes in the sconce.")
KINDS.append(dict(KOHLER_32375, type="Not a Type-See Type Catalog"))
KINDS.append(dict(KOHLER_32375, type="L1.1-1"))

KINDS += [
    dict(family="DWL 017A 40OD00 1K4 65 05 V.2 FLP", type="DWL 017A 40OD00 1K4 65 05 V.2 FLP",
         maker="EAE", model="DOWNLED V.2 downlight, DWL 017A 40OD00 1K4", status="maker's file from the Revit family",
         file=EXPORT + "LDT File - DOWNLED 20W V.2 FLP.IES", asset="IES_EAE_DOWNLED_20W_V2_FLP", file_kind=MAKER_FILE + ", delivered inside the Revit family",
         lumens=None, lumens_source="the file delivered in the Revit family (2,231 lm, 20.5 W). The type name reads 17 W and '1K4'; the family carries the 20 W file",
         kelvin=4000, kelvin_source="the type name (40) and the Revit light's value", on="all", per="light", aim="", radius=3.0,
         waits_on="Owner: the family mixes a 17 W type name with a 20 W file; confirm the product."),
    dict(family="MP75127-Motif", type="MP75127-BK",
         maker="Kuzco", model="Motif multi-pendant MP75127, 13 heads", status="data sheet and maker's file for one head",
         file=EXPORT + "PD75027-CH_SAMPLE.IES", asset="IES_Kuzco_PD75027", file_kind=MAKER_FILE + " of the single pendant PD75027, delivered inside the Revit family",
         lumens=900.0, lumens_source="data sheet MP75127: 11,710 delivered lm for 13 heads = 901 lm a head; data sheet PD75027: 900 lm. The file itself adds up to 784 lm and is scaled",
         kelvin=2700, kelvin_source="the data sheet (2,700 K; the Revit light says 3,000 K)", on="all", per="light", aim="", radius=3.0, waits_on=""),
    dict(family="Alcon-12303-P-Revit-Family", type="Alcon-12303-P-Revit-Family",
         maker="Alcon Lighting", model="12303-P pendant", status="data sheet and maker's file",
         file=EXPORT + "12303-PC-30K-25-BK.ies", asset="IES_Alcon_12303_PC_30K_25", file_kind=MAKER_FILE + ", delivered inside the Revit family",
         lumens=None, lumens_source="the maker's file (1,667.9 lm, 23.2 W); the data sheet 12303-Specification-Sheet.pdf gives 1,500 lm nominal",
         kelvin=3000, kelvin_source="the file name (30K); the data sheet offers 2,700, 3,000, 3,500 and 4,000 K", on="all", per="light", aim="", radius=3.0,
         waits_on="Owner: colour temperature option (the Revit light says 3,200 K, which is not an option)."),
    dict(family="EAE_KANOLED_V3_133W_5700K", type="Standart",
         maker="EAE", model="KANOLED V3 133 W 5,700 K (an industrial high-bay fixture)", status="placeholder: stand-in value",
         file=PHOTO + "_generic_made_here/GENERIC_downlight_60deg.ies", asset="IES_GENERIC_downlight_60deg", file_kind=GENERIC,
         lumens=1000.0, lumens_source="stand-in. The named product is a 133 W industrial high-bay fixture (about 18,000 lm, 5,700 K); eleven of them hang in rooms of the residences, which cannot be the design intent. 1,000 lm is an ordinary ceiling light",
         kelvin=3000, kelvin_source="stand-in, to match the downlights (the product is 5,700 K)", on="all", per="light", aim="", radius=3.0,
         waits_on="Owner: which fixture these eleven stand for."),
    dict(family="Simes_Walker_Wall recessed", type="*USE TYPE CATALOGUE*",
         maker="Simes", model="Walker wall-recessed step light S.6320W", status="data sheet and maker's file",
         file=EXPORT + "S6320W.ies", asset="IES_Simes_S6320W", file_kind=MAKER_FILE + ", delivered inside the Revit family",
         lumens=None, lumens_source="the maker's file (411.6 lm, 9.3 W); the catalogue gives 433 lm, 8.8 W",
         kelvin=3000, kelvin_source="the catalogue (3,000 K; the Revit light says 4,000 K)", on="all", per="light", aim="", radius=1.0,
         waits_on="The file is not the same in every direction; which way its front faces was not checked against each wall."),
    dict(family="Compound Ceiling", type="GWB",
         maker="EAE", model="ORN 018U 40OD00 2K10 downlight (five lights that Datasmith attached to a ceiling instead of a fixture)", status="maker's file from the Revit family",
         file=EXPORT + "3293297 - ORN 018U 40OD00 2K10 35 66 ELP.IES", asset="IES_EAE_ORN_018U_2K10", file_kind=MAKER_FILE + ", delivered inside the Revit family",
         lumens=None, lumens_source="the file delivered in the Revit family (2,036.5 lm, 17.7 W); the type name reads 18 W and '2K10'",
         kelvin=4000, kelvin_source="the type name (40) and the Revit light's value", on="all", per="light", aim="", radius=3.0, waits_on=""),
    dict(family="ORN 018U 40OD00 2K10 35 66 V6", type="STANDARD",
         maker="EAE", model="ORN 018U 40OD00 2K10 downlight", status="maker's file from the Revit family",
         file=EXPORT + "3293297 - ORN 018U 40OD00 2K10 35 66 ELP.IES", asset="IES_EAE_ORN_018U_2K10", file_kind=MAKER_FILE + ", delivered inside the Revit family",
         lumens=None, lumens_source="the file delivered in the Revit family (2,036.5 lm, 17.7 W); the type name reads 18 W and '2K10'",
         kelvin=4000, kelvin_source="the type name (40) and the Revit light's value", on="all", per="light", aim="", radius=3.0, waits_on=""),
    dict(family="Lighting-Wall_Mount-Visual_Comfort_&_Co-Stagger_X-Large_Wall_Sconce", type="700WSSTG63B-LED927-277",
         maker="Visual Comfort (Tech Lighting)", model="Stagger X-Large wall sconce 700WSSTG63B-LED927", status="data sheet; generic shape",
         file=PHOTO + "_generic_made_here/GENERIC_diffuse_globe.ies", asset="IES_GENERIC_diffuse_globe", file_kind=GENERIC,
         lumens=1000.0, lumens_source="the spec guide Tech-Lighting_Stagger-XL_700WSSTG63_spec-guide_2019.pdf: 1,000 delivered lm, 19.8 W (the Revit light says 2,000)",
         kelvin=2700, kelvin_source="the type name (LED927) and the spec guide", on="all", per="light", aim="", radius=4.0, waits_on=""),
    dict(family="INO TRIPLE circle suspended", type="INO TRIPLE circle suspended, white, 2700 K, 034-3845437H",
         maker="XAL", model="INO Triple circle suspended, 034-3845437H, three rings", status="maker's Revit family values; generic shape",
         file=PHOTO + "_generic_made_here/GENERIC_diffuse_down.ies", asset="IES_GENERIC_diffuse_down", file_kind=GENERIC,
         lumens=16490.0, lumens_source="the maker's Revit family: 6,870 + 5,500 + 4,120 lm for the three rings",
         kelvin=2700, kelvin_source="the type name (2700 K)", on="all", per="fixture", aim="", radius=5.0,
         waits_on="A ring of light is drawn as one point at the ring's centre."),
    dict(family="Emergency Wall Pack EM (Floor hosted)", type="EM2 - Emergency Unit - 2 Lamp Heads",
         maker="none named", model="emergency unit with two lamp heads", status="off: lit only when the power fails",
         file="", asset="", file_kind="", lumens=0.0, lumens_source="not lit in normal use", kelvin=3200, kelvin_source="the Revit light's value",
         on="none", per="light", aim="", radius=0.0, waits_on=""),
    dict(family="Lighting-Surface-Lumenwerx-Aera_5-Cylinder", type="AE4CYS-D-12IN-PHL-SW-15DEG-90CRI-35K-14W",
         maker="Lumenwerx", model="Aera 4 Cylinder Surface, AE4CYS pinhole 15 degrees 3,500 K 14 W", status="data sheet and maker's file",
         file=PHOTO + "Lumenwerx/Aera_Cylinder_Surface/AE4CYS-PHL-SW-15-90-35-SDL-14W.ies", asset="IES_Lumenwerx_AE4CYS_PHL_15_35_14W",
         file_kind=MAKER_FILE + ", downloaded from lumenwerx.com (the family carries the Aera 5 file; the type name says Aera 4)",
         lumens=None, lumens_source="the maker's file for the type named (1,345 lm, 14 W); the data sheet gives 1,399 lm x 0.92 for the pinhole",
         kelvin=3500, kelvin_source="the type name (35K)", on="all", per="light", aim="", radius=2.0, waits_on=""),
    dict(family="Lighting-Recessed-Vertical-Lumenwerx-Via_1_5", type="VIA1.5RV-D-HLO-1.5D-SW-90CRI-350LMF-35K",
         maker="Lumenwerx", model="Via 1.5 Recessed Vertical, 350 lm per foot, 3,500 K", status="data sheet; maker's file of a sister product",
         file=EXPORT + "VIA1.5PD-HLO-1.5D-SW-90-200-35-4FT.ies", asset="IES_Lumenwerx_VIA15_HLO_4FT",
         file_kind=MAKER_FILE + " of the pendant version, 4 ft, delivered inside the Revit family (none is published for the recessed vertical version)",
         lumens=353.0, lumens_source="the Revit family (353 lm for this length); the data sheet gives 350 lm per foot, 4.0 W per foot",
         kelvin=3500, kelvin_source="the type name (35K)", on="all", per="light", aim="", radius=2.0,
         waits_on="A line of light is drawn as one point; the file is for the hanging version."),
    dict(family="Lighting_Pendants_Zero_Mist_Pendant", type="Mist pendant 250 LED 880LM/9W Opal",
         maker="Zero", model="Mist pendant 250, opal, 880 lm 9 W", status="data sheet and maker's file",
         file=EXPORT + "Mist83651.IES", asset="IES_Zero_Mist83651", file_kind=MAKER_FILE + ", delivered inside the Revit family",
         lumens=None, lumens_source="the maker's file (834.6 lm, 9 W); the data sheet and the type name give 880 lm",
         kelvin=3000, kelvin_source="the data sheet (3,000 K; the Revit light says 4,000 K)", on="all", per="light", aim="", radius=5.0, waits_on=""),
]

COLUMNS = ["family", "type", "lights_in_model", "fixtures_in_model", "maker", "model", "status",
           "lumens_per_light_lit", "lumens_per_fixture", "lumens_source", "kelvin", "kelvin_source",
           "photometric_file", "photometric_file_kind", "file_lumens", "file_peak_candela", "file_watts",
           "profile_asset", "lights_on", "set_units", "set_value", "value_is", "reach_cm", "source_radius_cm", "aim", "waits_on"]


def main():
    with open(BEFORE, "r", newline="", encoding="utf-8") as handle:
        model = list(csv.DictReader(handle))
    rows, missing = [], []
    covered = set()
    for kind in KINDS:
        key = (kind["family"], kind["type"])
        covered.add(key)
        lights = [r for r in model if (r["fixture_family"], r["fixture_type"]) == key]
        fixtures = set((r["level"], r["fixture_label"]) for r in lights)
        if not lights:
            missing.append(key)
        facts = {"lumens_from_table": "", "peak_candela": "", "input_watts": ""}
        if kind["file"]:
            facts = ies_read.read(kind["file"])
            if "error" in facts:
                raise SystemExit("cannot read %s: %s" % (kind["file"], facts["error"]))
        on = kind["on"]
        lit_per_fixture = 0.0
        if lights and fixtures:
            lit_per_fixture = {"all": len(lights) / len(fixtures), "largest": 1.0, "none": 0.0}[on]
        if on == "none":
            lumens_light = lumens_fixture = set_value = 0.0
            units, value_is = "", "off"
        else:
            wanted = kind["lumens"] if kind["lumens"] is not None else facts["lumens_from_table"]
            candela = facts["peak_candela"] * wanted / facts["lumens_from_table"]
            units, set_value = "candela", round(candela, 1)
            if kind["per"] == "fixture":
                value_is = "per fixture, shared by the model's values"
                lumens_fixture, lumens_light = wanted, ""
            else:
                value_is = "per light"
                lumens_light, lumens_fixture = wanted, round(wanted * lit_per_fixture, 1)
        rows.append({
            "family": kind["family"], "type": kind["type"], "lights_in_model": len(lights), "fixtures_in_model": len(fixtures),
            "maker": kind["maker"], "model": kind["model"], "status": kind["status"],
            "lumens_per_light_lit": lumens_light, "lumens_per_fixture": lumens_fixture, "lumens_source": kind["lumens_source"],
            "kelvin": kind["kelvin"], "kelvin_source": kind["kelvin_source"],
            "photometric_file": kind["file"], "photometric_file_kind": kind["file_kind"],
            "file_lumens": facts["lumens_from_table"], "file_peak_candela": facts["peak_candela"], "file_watts": facts["input_watts"],
            "profile_asset": (ASSETS + kind["asset"]) if kind["asset"] else "", "lights_on": on, "set_units": units,
            "set_value": set_value, "value_is": value_is, "reach_cm": 1000 if on != "none" else "",
            "source_radius_cm": kind["radius"], "aim": kind["aim"], "waits_on": kind["waits_on"],
        })
    not_covered = sorted(set((r["fixture_family"], r["fixture_type"]) for r in model) - covered)
    with open(OUT, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    print("kinds %d, lights covered %d of %d, kinds of the model not in the table %s, table kinds not in the model %s"
          % (len(rows), sum(r["lights_in_model"] for r in rows), len(model), not_covered, missing))
    for row in rows:
        print("%-40s %-28s on=%-7s %8s cd  %s lm/fixture  %s K" % (row["family"][:40], row["type"][:28], row["lights_on"],
                                                                 row["set_value"], row["lumens_per_fixture"], row["kelvin"]))


if __name__ == "__main__":
    main()
