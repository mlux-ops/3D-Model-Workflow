import hashlib
import json
import shutil
import zipfile
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "output" / "1527_wieland"
REV = OUT / "review"
DELIVERY = OUT / "delivery"
PACKAGE_NAME = "1527_Wieland_Revit_2025_PASS_Families_2026-10-02"
STAGE = DELIVERY / PACKAGE_NAME
ZIP = DELIVERY / (PACKAGE_NAME + ".zip")

def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

ledger = load(REV / "grade_ledger.json")
app = load(OUT / "appliances" / "section_manifest.json")
plm = load(OUT / "plumbing_fixtures" / "FINAL_STATUS.json")
ele = load(OUT / "electrical_fixtures" / "ROW_STATUS.json")

grades = {(r["section"], str(r["row_id"])): r["grade"] for r in ledger["rows"]}
family_rows = defaultdict(lambda: {"pass": [], "nonpass": []})

for row in app["rows"]:
    rid = str(row["row_id"])
    for rel in row.get("rfa_paths", []):
        key = ("appliances", rel)
        family_rows[key]["pass" if grades[("Appliances", rid)] == "PASS" else "nonpass"].append(rid)

for row in plm["rows"]:
    rid = str(row["row_id"])
    rel = row.get("rfa_path")
    if not rel:
        continue
    key = ("plumbing_fixtures", rel)
    family_rows[key]["pass" if grades[("Plumbing Fixtures", rid)] == "PASS" else "nonpass"].append(rid)

for row in ele["rows"]:
    rid = str(row["row_id"])
    rel = row.get("canonical_rfa_path") or row.get("rfa_path")
    if not rel:
        continue
    key = ("electrical_fixtures", rel)
    family_rows[key]["pass" if grades[("Electrical Fixtures", rid)] == "PASS" else "nonpass"].append(rid)

included = {}
excluded_shared = {}
for key, refs in sorted(family_rows.items()):
    if refs["pass"] and not refs["nonpass"]:
        included[key] = refs
    elif refs["pass"] and refs["nonpass"]:
        excluded_shared[key] = refs

if excluded_shared:
    # A family serving an unresolved row is never silently released just because
    # another duplicate row passed.
    print("withheld shared families", len(excluded_shared))

assert STAGE.parent.resolve() == DELIVERY.resolve()
assert STAGE.name == PACKAGE_NAME
if STAGE.exists():
    shutil.rmtree(STAGE)
STAGE.mkdir(parents=True)

allowed_suffixes = {
    ".rfa", ".md", ".json", ".txt", ".py", ".png", ".jpg", ".jpeg",
    ".bmp", ".tif", ".tiff", ".pat", ".xml", ".csv"
}

manifest = {
    "schema": "1527_wieland_pass_delivery_v1",
    "package_name": PACKAGE_NAME,
    "pass_rows": sum(1 for r in ledger["rows"] if r["grade"] == "PASS"),
    "needs_user_rows": sum(1 for r in ledger["rows"] if r["grade"] == "NEEDS_USER"),
    "fail_rows": sum(1 for r in ledger["rows"] if r["grade"] == "FAIL"),
    "canonical_families": len(included),
    "families": [],
    "withheld_shared_families": [],
}

for (section, rel_rfa), refs in sorted(included.items()):
    section_root = OUT / section
    rfa = section_root / rel_rfa
    if not rfa.exists():
        raise FileNotFoundError(rfa)
    family_dir = rfa.parent
    dest = STAGE / section / family_dir.name
    dest.mkdir(parents=True, exist_ok=True)

    copied = []
    for src in sorted(family_dir.rglob("*")):
        if not src.is_file():
            continue
        # Package the native family, setup/validation records, scripts, companion
        # bitmaps and previews. Large retained source PDFs/CAD/ZIP/RFAs used only
        # as research/original evidence remain preserved in the local archive.
        if src.suffix.lower() not in allowed_suffixes:
            continue
        # Never copy an alternate/original research RFA; only the selected working
        # RFA for this canonical family is released.
        if src.suffix.lower() == ".rfa" and src.resolve() != rfa.resolve():
            continue
        target = dest / src.relative_to(family_dir)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, target)
        copied.append(str(target.relative_to(STAGE)).replace("\\", "/"))

    sha = hashlib.sha256(rfa.read_bytes()).hexdigest()
    manifest["families"].append({
        "section": section,
        "source_rfa": str(rfa.relative_to(OUT)).replace("\\", "/"),
        "rfa_sha256": sha,
        "pass_row_ids": refs["pass"],
        "files": copied,
    })

for (section, rel_rfa), refs in sorted(excluded_shared.items()):
    manifest["withheld_shared_families"].append({
        "section": section,
        "source_rfa": rel_rfa.replace("\\", "/"),
        "pass_row_ids": refs["pass"],
        "nonpass_row_ids": refs["nonpass"],
        "reason": "Withheld because one canonical family is referenced by at least one unresolved/non-PASS row.",
    })

shutil.copy2(OUT / "REVIEW.md", STAGE / "REVIEW.md")
shutil.copy2(REV / "grade_ledger.json", STAGE / "grade_ledger.json")
(STAGE / "PACKAGE_MANIFEST.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
(STAGE / "README.md").write_text(
    "# 1527 Wieland Revit 2025 PASS family package\n\n"
    "This package contains only canonical families whose mapped inventory rows are all graded PASS. "
    "Any canonical family referenced by a NEEDS_USER or FAIL row is withheld.\n\n"
    "Each included family carries its selected Revit 2025 RFA plus available setup/validation records, "
    "scripts, companion bitmap textures, and preview images. Full retained manufacturer originals, PDFs, "
    "CAD research files, and worker evidence remain preserved in the local 3d-model-workflow archive and "
    "are intentionally not duplicated into this delivery ZIP. See REVIEW.md and PACKAGE_MANIFEST.json.\n",
    encoding="utf-8",
)

if ZIP.exists():
    ZIP.unlink()
with zipfile.ZipFile(ZIP, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    for src in sorted(STAGE.rglob("*")):
        if src.is_file():
            z.write(src, src.relative_to(STAGE))

sha256 = hashlib.sha256()
with ZIP.open("rb") as f:
    for chunk in iter(lambda: f.read(4 * 1024 * 1024), b""):
        sha256.update(chunk)

delivery = {
    "package_name": ZIP.name,
    "local_path": str(ZIP),
    "sha256": sha256.hexdigest(),
    "size": ZIP.stat().st_size,
    "pass_rows": manifest["pass_rows"],
    "needs_user_rows": manifest["needs_user_rows"],
    "fail_rows": manifest["fail_rows"],
    "canonical_families": manifest["canonical_families"],
    "withheld_shared_families": len(manifest["withheld_shared_families"]),
    "drive_status": "pending",
}
(REV / "delivery.json").write_text(json.dumps(delivery, indent=2), encoding="utf-8")
print(json.dumps(delivery, indent=2))
