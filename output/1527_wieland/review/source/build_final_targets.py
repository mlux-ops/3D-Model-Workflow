import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
REVIEW = os.path.join(ROOT, "review")
PLUMB = os.path.join(ROOT, "plumbing_fixtures")
ELEC = os.path.join(ROOT, "electrical_fixtures")


def load(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def abs_rfa(section_root, rel_or_abs):
    if not rel_or_abs:
        return None
    if os.path.isabs(rel_or_abs):
        return rel_or_abs
    return os.path.abspath(os.path.join(section_root, rel_or_abs))


targets = []

# Plumbing: one target per product group / final RFA.
pstatus = load(os.path.join(PLUMB, "FINAL_STATUS.json"))
groups = {}
for row in pstatus["rows"]:
    key = row.get("group_key")
    rfa = row.get("rfa_path")
    if not key or not rfa:
        continue
    rec = groups.setdefault(key, {
        "row_ids": [],
        "statuses": set(),
        "rfa": abs_rfa(PLUMB, rfa),
        "items": [],
    })
    rec["row_ids"].append(str(row["row_id"]))
    rec["statuses"].add(row.get("status"))
    if row.get("description"):
        rec["items"].append(row["description"])

for key, rec in sorted(groups.items()):
    validation_path = os.path.join(PLUMB, key, "validation.json")
    v = load(validation_path)
    expected_mm = v.get("expected_dimensions_mm")
    if expected_mm is None and v.get("expected_dimensions_in") is not None:
        expected_mm = [None if x is None else float(x) * 25.4 for x in v["expected_dimensions_in"]]
    sources = []
    for field in ("source_url", "spec_url"):
        if v.get(field):
            sources.append(v[field])
    for ref in v.get("source_references", []) or []:
        if isinstance(ref, dict) and ref.get("url"):
            sources.append(ref["url"])
    targets.append({
        "row_id": rec["row_ids"][0],
        "row_ids": rec["row_ids"],
        "section": "plumbing_fixtures",
        "group_key": key,
        "status": sorted(x for x in rec["statuses"] if x),
        "item": v.get("model") or key,
        "manufacturer": v.get("manufacturer"),
        "rfa": rec["rfa"],
        "validation_path": validation_path,
        "expected_category": v.get("category") or "Plumbing Fixtures",
        "expected_dimensions_mm": expected_mm,
        "worker_native_pass": v.get("native_gates_pass"),
        "source_urls": sorted(set(sources)),
    })

# Electrical: one target per distinct canonical saved family.
estatus = load(os.path.join(ELEC, "ROW_STATUS.json"))
efamily_index = load(os.path.join(ELEC, "FINAL_FAMILY_INDEX.json"))
category_by_rfa = {}
for fam in efamily_index.get("families", []):
    rp = fam.get("rfa_path")
    if rp:
        category_by_rfa[rp.replace("\\", "/").lower()] = fam.get("category")
egroups = {}
for row in estatus["rows"]:
    rfa = row.get("canonical_rfa_path") or row.get("rfa_path")
    if not rfa:
        continue
    product_key = row.get("group_key") or row.get("source_model") or rfa
    unique_key = (product_key, rfa)
    rec = egroups.setdefault(unique_key, {
        "row_ids": [],
        "statuses": set(),
        "rfa": abs_rfa(ELEC, rfa),
        "group_key": product_key,
        "expected_dimensions_in": row.get("expected_dimensions_in"),
        "manufacturer": row.get("delivered_manufacturer"),
        "model": row.get("delivered_model"),
        "source_urls": set(),
        "validation_path": row.get("validation_path"),
        "relative_rfa": rfa,
    })
    rec["row_ids"].append(str(row["row_id"]))
    rec["statuses"].add(row.get("status"))
    for u in row.get("source_urls", []) or []:
        rec["source_urls"].add(u)

for unique_key, rec in sorted(egroups.items(), key=lambda kv: (str(kv[0][0]), str(kv[0][1]))):
    expected_mm = None
    if rec["expected_dimensions_in"] is not None:
        expected_mm = [None if x is None else float(x) * 25.4 for x in rec["expected_dimensions_in"]]
    targets.append({
        "row_id": rec["row_ids"][0],
        "row_ids": rec["row_ids"],
        "section": "electrical_fixtures",
        "group_key": rec["group_key"],
        "status": sorted(x for x in rec["statuses"] if x),
        "item": rec["model"] or key,
        "manufacturer": rec["manufacturer"],
        "rfa": rec["rfa"],
        "validation_path": os.path.join(ELEC, rec["validation_path"]) if rec["validation_path"] else None,
        "expected_category": category_by_rfa.get(
            rec["relative_rfa"].replace("\\", "/").lower(),
            "Lighting Fixtures"
        ),
        "expected_dimensions_mm": expected_mm,
        "worker_native_pass": True,
        "source_urls": sorted(rec["source_urls"]),
    })

out = os.path.join(REVIEW, "review_targets.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(targets, f, indent=2)

summary = {
    "plumbing_unique_families": sum(1 for x in targets if x["section"] == "plumbing_fixtures"),
    "electrical_unique_families": sum(1 for x in targets if x["section"] == "electrical_fixtures"),
    "total_unique_families": len(targets),
    "plumbing_rows_covered": len({rid for x in targets if x["section"] == "plumbing_fixtures" for rid in x["row_ids"]}),
    "electrical_rows_covered": len({rid for x in targets if x["section"] == "electrical_fixtures" for rid in x["row_ids"]}),
}
with open(os.path.join(REVIEW, "target_summary.json"), "w", encoding="utf-8") as f:
    json.dump(summary, f, indent=2)
print(json.dumps(summary, indent=2))
