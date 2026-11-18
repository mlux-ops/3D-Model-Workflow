"""Phase 5, step 5.1: one licence line for every file under the project's Content folder.

Usage:
    python -B phase5_licences.py <project Content folder> <asset_licences.csv> <asset_licence_groups.csv> [<downloads.csv>]

Every file is put in the most specific group below (the longest matching
folder, then a name test inside the Datasmith texture folders). The first
table has one row per file; the second has one row per group with the full
wording. Nothing is deleted or moved: a group without a licence record is
marked for the owner.

status is one of
    recorded          the source and its licence are written down somewhere
    owner's own       the owner's model or work made in this project
    NO RECORD         nothing in the project or the repository states a licence
"""

import csv
import os
import sys

REC, OWN, NONE = "recorded", "owner's own", "NO RECORD"
REPO = "E:\\Games\\Claude\\1527 Wieland\\fbx_walkthrough\\tools\\"

# (folder under Content, group, what it is, source, licence, status, evidence or note)
FOLDERS = (
    ("Wieland1529/Building/Datasmith", "Revit export, Phase 3",
     "Geometry and material settings exported from the owner's Revit model 25-006",
     "The owner's Revit model through Datasmith (Phase 3)",
     "Owner's property. The model contains manufacturers' Revit families (plumbing, appliances, windows, furniture, light fixtures); each manufacturer's download terms are not recorded.",
     OWN, "SOURCES.md line 32. Manufacturers' terms: no record; listed for the owner."),
    ("Wieland1529/Scratch", "Revit export, Phase 1 pilot copy",
     "The Phase 1 trial import of the same Revit model, with three small test materials made in Phase 1",
     "The owner's Revit model through Datasmith (Phase 1)",
     "Owner's property; same remark on manufacturers' families as the Phase 3 export.",
     OWN, "phase1_results.md."),
    ("Wieland1529/Surroundings", "Surroundings, Phase 4",
     "Massing of the neighbouring buildings and the level that holds them",
     "Built in Phase 4 from Cook County building footprints 2022 and the 2022 lidar of the Illinois State Geological Survey",
     "Lidar: \"No restrictions apply to these data.\" County footprints: provided \"as is\"; redistribution unclear.",
     REC, "SOURCES.md lines 42 and 44."),
    ("Wieland1529/Materials", "Phase 5 materials",
     "Parent materials, candidate instances, the swatch level and textures brought in during Phase 5",
     "Made in Phase 5; each downloaded texture set has its own line in the downloads table",
     "Own work; downloaded sets are CC0 (public-domain dedication) as recorded per set.",
     REC, "phase5_results.md; the downloads rows of this table."),
    ("Wieland1529", "Scene levels of this plan",
     "The site levels L_Site_M1 and L_Site_M2",
     "Made in Phases 3 and 4 of this plan", "Own work.", OWN, "phase3_results.md, phase4_results.md."),
    ("Wieland/Revit1527", "Revit export, earlier project",
     "The earlier project's import of the owner's Revit model",
     "The owner's Revit model", "Owner's property; same remark on manufacturers' families.",
     OWN, "SOURCES.md line 32."),
    ("Wieland/R15_Materials/PolyHaven", "Poly Haven texture sets",
     "13 surface texture sets", "Poly Haven, https://polyhaven.com",
     "CC0 (public-domain dedication), as the earlier project's records state; the licence page itself was not read then.",
     REC, "SOURCES.md line 98; SITE_MODEL_AUDIT.md line 65."),
    ("Wieland/R15_Materials/Glass", "ambientCG glass imperfection set",
     "Surface imperfection maps used on glass", "ambientCG SurfaceImperfections015, https://ambientcg.com",
     "CC0, as the earlier project's script states.", REC, REPO + "r15_finish_glass.py line 109."),
    ("Wieland/R15_Materials/Scans", "Megascans worn brick",
     "One scanned worn-brick surface", "Quixel Megascans (by its folder name)",
     "No licence record. Megascans items are tied to the Epic or Fab account that took them.",
     NONE, "SOURCES.md line 99: \"No licence record was kept with the project.\""),
    ("Wieland/R15_Materials/BrickWallWorn_sexkaitb", "Megascans worn brick",
     "One scanned worn-brick surface", "Quixel Megascans (by its folder name)",
     "No licence record. Megascans items are tied to the Epic or Fab account that took them.",
     NONE, "SOURCES.md line 99."),
    ("Wieland/R15_Materials/Production", "Earlier project's production materials",
     "Parent materials, instances and textures made by the earlier project's scripts",
     "Earlier project scripts; the scripts name TextureCan (Metal0010, Rooftop0010, Limestone1 by M. Tolga Arslan) and ambientCG (Grass004) as texture sources",
     "The scripts call these CC0. No licence file is kept, and another record (SOURCE_REPORT.md) says no outside maps were taken, which contradicts the scripts.",
     NONE, REPO + "r15_native_extras.py lines 13 to 16. Contradiction listed for the owner."),
    ("Wieland/R15_Materials", "Earlier project's materials, other",
     "Materials of the earlier project outside the named folders", "Earlier project", "No licence record.",
     NONE, "No record found."),
    ("Wieland/R15_Landscape", "Earlier project's landscape",
     "The earlier project's landscape level and its ground textures; the level L_R15_Production is never saved by this plan",
     "Earlier project scripts", "The grass texture's source is recorded three ways (ambientCG Grass004, Poly Haven grass_medium_02, a Fab grass folder).",
     NONE, "Contradiction listed for the owner."),
    ("Wieland/R15_Render", "Earlier project's render settings",
     "Render presets and sequences made in the earlier project", "Earlier project", "Own work of the earlier project; no licence file.",
     OWN, "By content: settings and sequences, no outside media seen in the names."),
    ("Wieland/R14", "Earlier project's site model",
     "Neighbour buildings of the earlier site model and their materials",
     "Earlier project, built on the City of Chicago building footprints",
     "City data: \"See Terms of Use\"; the terms page refused the request when Phase 0 tried to read it.",
     NONE, "SOURCES.md line 43."),
    ("Wieland", "Earlier project, other", "Other files of the earlier project", "Earlier project", "No licence record.",
     NONE, "No record found."),
    ("Fab", "Fab downloads",
     "Materials, textures and Megascans surfaces taken from Fab, Epic's asset store, including a grass material",
     "Fab (by its folder name)", "No licence record. Fab items carry the Fab licence of the account that took them.",
     NONE, "SOURCES.md line 99."),
    ("Megaplant_Library", "Megaplant tree library",
     "Tree and plant models with their textures", "Not recorded; an earlier note calls it \"UE-only or no-redistribution\"",
     "No licence record.", NONE, "SOURCES.md line 99."),
    ("HighPoly_Tree_Model", "High-poly tree model", "One tree model with demo level, materials and textures",
     "Not recorded", "No licence record.", NONE, "No record found."),
    ("MSPresets", "Megascans presets", "Preset materials installed by the Megascans (Quixel Bridge) plugin",
     "Quixel Megascans plugin (by its folder name)", "No licence record; comes with the plugin.", NONE, "No record found."),
    ("ProductAssets", "Product configurator template content", "Blueprints, levels and sequences of a product-configurator template",
     "Not recorded; the names match Epic's product-configurator template", "No licence record.", NONE, "No record found."),
    ("ProductConfig", "Product configurator template content", "Blueprints and interface widgets of a product-configurator template",
     "Not recorded; the names match Epic's product-configurator template", "No licence record.", NONE, "No record found."),
    ("Building", "Sample building content", "A sample building (beams, floor, roof, flowers, land) in a folder named Building",
     "Not recorded; the names match an Epic sample or template", "No licence record.", NONE, "No record found."),
    ("Python", "Project scripts", "Start-up script and the agent bridge", "Written for this project", "Own work.", OWN, "By content."),
    ("", "Other", "Files outside every named folder", "Not recorded", "No licence record.", NONE, "No record found."),
)

# Name tests inside a Datasmith "Textures" folder: (group, test, what, source, licence, status, note)
AUTODESK = ("finishes_", "woods___plastics", "masonry_", "metals_", "concrete_", "sitework_", "furnishings_",
            "doors_-_windows_", "brick_non_uniform", "cmu_running", "tilesquarebump", "plastic_smooth_bump",
            "brush_short_bump", "thermal_", "roofing_")


def _texture_group(name):
    low = name.lower()
    if low.endswith("_ies"):
        return ("Revit export: light distribution files",
                "Light distribution (photometric) file carried in a light fixture family",
                "A lighting manufacturer, through the Revit family", "The manufacturer's download terms; not recorded.",
                NONE, "SOURCES.md line 100: to be read per file in Phase 8.")
    if low.startswith(AUTODESK):
        return ("Revit export: Autodesk library images",
                "Image from the material library that ships with Revit (judged by its name)",
                "Autodesk material library, through the Revit model",
                "Autodesk's terms for its material library; whether they allow use outside Autodesk's programs is not recorded.",
                NONE, "No record found; listed for the owner.")
    if low.startswith(("diffuse_", "bump_")) and low.rstrip("_").rsplit("__", 1)[-1].strip("_0123456789").isalnum():
        return ("Revit export: generated surface images",
                "Colour or relief image whose name carries a pattern, a size in inches and a six-letter code, the way an online texture editor names its output (judged by its name)",
                "Not recorded; brought into the Revit model by the owner",
                "Depends on the editor's terms and the plan of the account that made it; not recorded.",
                NONE, "No record found; listed for the owner.")
    if low.startswith(("indiana-limestone", "indiana_limestone")):
        return ("Revit export: Indiana limestone images",
                "Large colour and relief images of Indiana limestone",
                "Not recorded; brought into the Revit model by the owner (name suggests a stone supplier's or a generated image)",
                "Not recorded.", NONE, "No record found; listed for the owner.")
    return ("Revit export: other images in the model",
            "Image carried in a Revit family or a project material",
            "The Revit model; the origin of the single image is not recorded",
            "Not recorded per image.", NONE, "No record found; listed for the owner.")


LIBRARY = ("Repository package: Daltile Remedy Hydro tile",
           "Colour, relief and roughness images of this repository's package of the Daltile Remedy Hydro 2 by 10 inch "
           "fluted tile, and the library instance built from them in Phase 5 (assigned to no surface)",
           "This repository's package under output\\; its colour image is derived from the manufacturer's product "
           "pictures",
           "Relief and roughness: this repository's own work. Colour: the manufacturer's terms for its product pictures "
           "are not recorded.",
           NONE, "material_library.csv; the package's manifest and README. Listed for the owner; nothing deleted.")


def classify(relative):
    path = relative.replace("\\", "/")
    if path.startswith("Wieland1529/Materials/Library/") or "/T_W1529_Daltile_" in path:
        return LIBRARY
    for folder, group, what, source, licence, status, note in FOLDERS:
        if folder == "" or path == folder or path.startswith(folder + "/"):
            if "/Textures/" in path and ("Datasmith" in path or "Revit1527" in path or "/Scratch/" in path):
                name = os.path.splitext(os.path.basename(path))[0]
                return _texture_group(name)
            return (group, what, source, licence, status, note)
    raise AssertionError(path)


def main(content, files_csv, groups_csv, downloads_csv=None):
    groups = {}
    rows = []
    for folder, _dirs, names in os.walk(content):
        if "__pycache__" in folder:
            continue
        for name in sorted(names):
            full = os.path.join(folder, name)
            relative = os.path.relpath(full, content).replace("\\", "/")
            group, what, source, licence, status, note = classify(relative)
            size = os.path.getsize(full)
            rows.append({"file": "Content/" + relative, "size_mb": "%.3f" % (size / 1048576.0), "group": group,
                         "licence": licence, "status": status})
            entry = groups.setdefault(group, {"group": group, "files": 0, "size_mb": 0.0, "what_it_is": what,
                                              "source": source, "licence": licence, "status": status,
                                              "evidence_or_note": note, "example": "Content/" + relative})
            entry["files"] += 1
            entry["size_mb"] += size / 1048576.0
    downloads = []
    if downloads_csv and os.path.exists(downloads_csv):
        with open(downloads_csv, encoding="utf-8", newline="") as handle:
            downloads = list(csv.DictReader(handle))
    for item in downloads:
        group = "Phase 5 download: " + item["name"]
        groups[group] = {"group": group, "files": item.get("files", ""), "size_mb": float(item.get("size_mb") or 0),
                         "what_it_is": item["what_it_is"], "source": item["source"], "licence": item["licence"],
                         "status": REC, "evidence_or_note": item["evidence_or_note"], "example": item.get("kept_at", "")}
    rows.sort(key=lambda row: row["file"].lower())
    with open(files_csv, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["file", "size_mb", "group", "licence", "status"])
        writer.writeheader()
        writer.writerows(rows)
    ordered = sorted(groups.values(), key=lambda entry: (entry["status"] != NONE, entry["group"].lower()))
    with open(groups_csv, "w", encoding="utf-8", newline="") as handle:
        fields = ["group", "status", "files", "size_mb", "what_it_is", "source", "licence", "evidence_or_note", "example"]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for entry in ordered:
            entry = dict(entry)
            entry["size_mb"] = "%.1f" % entry["size_mb"]
            writer.writerow(entry)
    totals = {}
    for entry in groups.values():
        files = int(entry["files"] or 0)
        count, size = totals.get(entry["status"], (0, 0.0))
        totals[entry["status"]] = (count + files, size + float(entry["size_mb"]))
    print("%d files in %d groups" % (len(rows), len(groups)))
    for status, (count, size) in sorted(totals.items()):
        print("  %-12s %5d files %8.1f MB" % (status, count, size))
    for entry in ordered:
        print("  %-10s %5s files %8.1f MB  %s" % (entry["status"], entry["files"], float(entry["size_mb"]), entry["group"]))


if __name__ == "__main__":
    main(*sys.argv[1:])
