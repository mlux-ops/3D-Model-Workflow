"""Print a compact view of source/revit_probe.json (read-only helper)."""
import json
from pathlib import Path

p = Path(__file__).resolve().parent / "revit_probe.json"
d = json.loads(p.read_text())
print("stage:", d.get("stage"), "| revit", d.get("revit_version"), d.get("revit_build"))
if "error" in d:
    print(d["error"])
print("schema counts:", d.get("schema_counts"))
SKIP = ("UIName", "thumbnail", "keyword", "category", "description", "ExchangeGUID",
        "AssetLibID", "assetlib", "Hidden", "VersionGUID", "localname", "localtype",
        "swatch", "SchemaVersion", "revision", "ImplementationGeometry", "ImplementationOGS",
        "ImplementationMentalRay", "ImplementationPreview", "PatternOffset", "mode")
for key, val in d["schemas"].items():
    print("\n==", key, "==")
    if not val:
        print("  NOT PRESENT")
        continue
    print("  library asset:", val["library_asset_name"])
    for row in val["properties"]:
        if any(s.lower() in row[0].lower() for s in SKIP):
            continue
        print("  ", row[0], "|", row[1], "|", row[2], *row[3:])
    print("  -- connect tests --")
    for name, slot in d["connect_tests"].get(key, {}).items():
        print("  ", name, slot)
for tex in ("UnifiedBitmap", "BumpMap"):
    rows = d.get("texprops_" + tex)
    print("\n== connected texture schema", tex, "==")
    if not rows:
        print("  none captured")
        continue
    for row in rows:
        if any(s.lower() in row[0].lower() for s in SKIP):
            continue
        print("  ", row[0], "|", row[1], "|", row[2])
