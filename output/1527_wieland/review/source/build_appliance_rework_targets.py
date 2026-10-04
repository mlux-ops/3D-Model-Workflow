import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "output" / "1527_wieland"
APP = OUT / "appliances"
REV = OUT / "review"
SLUGS = [
    "miele_h7280bp",
    "miele_h7270bm",
    "miele_g5051scvi",
    "miele_kwt6722is",
    "miele_kwtus7172f",
    "miele_kfmc3858fd",
    "thermador_t42it100np",
    "thermador_podmc301w",
    "thermador_pcg486wd",
]

manifest = json.loads((APP / "section_manifest.json").read_text(encoding="utf-8"))
rows_by_slug = {}
for row in manifest["rows"]:
    slugs = row.get("model_slugs") or ([row.get("canonical_slug")] if row.get("canonical_slug") else [])
    for slug in slugs:
        if slug:
            rows_by_slug.setdefault(slug, []).append(str(row["row_id"]))

targets = []
for slug in SLUGS:
    validation = json.loads((APP / slug / "validation.json").read_text(encoding="utf-8"))
    saved = validation.get("saved_rfa")
    if not saved:
        rfas = list((APP / slug).glob("*.rfa"))
        if len(rfas) != 1:
            raise RuntimeError("Cannot resolve selected RFA for " + slug)
        saved = str(rfas[0])
    expected = validation.get("target_xyz_mm")
    targets.append({
        "row_id": (rows_by_slug.get(slug) or [""])[0],
        "row_ids": rows_by_slug.get(slug, []),
        "section": "appliances",
        "group_key": slug,
        "rfa": saved,
        "validation_path": str(APP / slug / "validation.json"),
        "expected_category": "Specialty Equipment",
        "expected_dimensions_mm": expected,
        "worker_native_pass": bool(validation.get("dimension_gate")),
    })

(REV / "appliance_rework_targets.json").write_text(json.dumps(targets, indent=2), encoding="utf-8")
print(json.dumps({"targets": len(targets), "rows": sum(len(t["row_ids"]) for t in targets)}, indent=2))
