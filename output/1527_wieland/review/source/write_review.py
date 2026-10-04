import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "output" / "1527_wieland"
REV = OUT / "review"
ledger = json.loads((REV / "grade_ledger.json").read_text(encoding="utf-8"))
delivery_path = REV / "delivery.json"
delivery = json.loads(delivery_path.read_text(encoding="utf-8-sig")) if delivery_path.exists() else None
bt = chr(96)

def esc(value):
    if value is None:
        return ""
    return str(value).replace("|", "\\|").replace("\n", " ").strip()

def q(value):
    return bt + esc(value) + bt

def row_link(row):
    if row.get("product_url"):
        return "[product](" + row["product_url"] + ")"
    notes = row.get("notes_path")
    if not notes:
        return ""
    folder = {
        "Appliances": "appliances",
        "Plumbing Fixtures": "plumbing_fixtures",
        "Electrical Fixtures": "electrical_fixtures",
    }[row["section"]]
    return "[NOTES](./" + folder + "/" + notes.replace("\\", "/") + ")"

lines = [
    "# 1527 Wieland - Revit 2025 Family Orchestrator Review",
    "",
    "Final independent review for the Appliances, Plumbing Fixtures, and Electrical Fixtures inventories extracted from the live FINISH DATABASE - 1527 Wieland Smartsheet (sheet ID 8569278453206916). No Smartsheet edits were made.",
    "",
    "## Executive result",
    "",
]

for section in ("Appliances", "Plumbing Fixtures", "Electrical Fixtures"):
    total = ledger["totals"][section]
    worker = ", ".join(k + " " + str(v) for k, v in sorted(total["worker_status"].items()))
    grades = ", ".join(k + " " + str(v) for k, v in sorted(total["grade"].items()))
    lines.append("- **" + section + ":** " + str(total["rows"]) + " rows. Worker statuses: " + worker + ". Orchestrator grades: " + grades + ".")

overall = ledger["totals"]["Overall"]
overall_grades = ", ".join(k + " " + str(v) for k, v in sorted(overall["grade"].items()))
lines += [
    "- **Overall:** " + str(overall["rows"]) + " rows. " + overall_grades + ".",
    "",
    "Only PASS families are eligible for final package delivery. NEEDS_USER rows are intentionally withheld. Any remaining FAIL row is also withheld.",
    "",
    "## Independent QA evidence",
    "",
    "- Row coverage: Appliances 27/27, Plumbing 178/178, Electrical 120/120; zero missing row IDs.",
    "- Plumbing/Electrical native orchestrator review: 112 distinct final RFAs reopened in Revit 2025 through the serialized shared runner; 112 measured, zero open errors, zero category mismatches.",
    "- The lightweight reviewer was used for the final saved-RFA health/category pass because a generic geometry union can include template/control geometry. Authoritative dimension grades therefore use the workers' native measured gate receipts rather than raw family bounding boxes.",
    "- Plumbing visual review: all seven final contact sheets were inspected by the orchestrator.",
    "- Electrical visual review: all eleven final review sheets were inspected by the orchestrator; the worker-native maximum checked-dimension error is 0.685197 mm.",
    "- Appliances: the prior independent pass covered more than 30 percent of rows and every BUILT_WITH_LIMITATIONS target. Any later reworked appliance family is independently reopened and visually inspected before final PASS.",
    "",
    "## Review-tool stalls and blockers",
    "",
    "- The initial all-family generic review dispatch returned upstream UNAVAILABLE: Connection failed even though the first job had dispatched; the retry waited behind revit.lock for **336 seconds**. This was an orchestrator-QA dispatch artifact, not a production family failure.",
    "- A generic image/mesh batch later timed out after **240 seconds** on Panasonic RG-C811A. The lightweight Revit reviewer subsequently reopened the RFA successfully with correct category, zero warnings, and the expected physical envelope.",
    "- No family-production lock stall exceeded 15 minutes. Production remained serialized through the shared revit.lock.",
    "- Review-tool events are recorded in /3d-model-workflow/PROJECT_MEMORY.md. No production RFA was modified by those failed review attempts.",
    "",
    "## NEEDS_USER decisions",
    "",
]

if ledger["needs_user"]:
    lines += [
        "| Section | Row ID | Item / model | Link | Decision required | Hold code |",
        "|---|---:|---|---|---|---|",
    ]
    for row in ledger["needs_user"]:
        item = row.get("tag") or row.get("model_number") or row.get("description")
        lines.append("| " + " | ".join([
            esc(row["section"]), esc(row["row_id"]), esc(item), row_link(row),
            esc(row["reason"]), esc(row.get("needs_user_code")),
        ]) + " |")
else:
    lines.append("None.")

lines += [
    "",
    "## Every inventory row",
    "",
    "| Section | Row ID | Tag / code | Manufacturer | Model | Worker status | Grade | RFA | Reason |",
    "|---|---:|---|---|---|---|---|---|---|",
]

for row in ledger["rows"]:
    rfas = "<br>".join(q(x) for x in row.get("rfa_paths", []))
    lines.append("| " + " | ".join([
        esc(row["section"]), esc(row["row_id"]), esc(row.get("tag")), esc(row.get("manufacturer")),
        esc(row.get("model_number")), esc(row.get("worker_status")), esc(row.get("grade")),
        rfas, esc(row.get("reason")),
    ]) + " |")

lines += ["", "## Delivery", ""]
if delivery:
    lines += [
        "- Package: " + q(delivery.get("package_name", "")),
        "- Local SHA-256: " + q(delivery.get("sha256", "")),
        "- PASS rows represented: " + str(delivery.get("pass_rows", "")),
        "- Included canonical families: " + str(delivery.get("canonical_families", "")),
    ]
    if delivery.get("drive_status") == "uploaded":
        lines += [
            "- Google Drive: [verified upload](" + delivery.get("drive_url", "") + ")",
            "- Drive file ID: " + q(delivery.get("drive_file_id", "")),
            "- Verified Drive size: " + str(delivery.get("drive_size", "")) + " bytes",
        ]
        if delivery.get("drive_md5"):
            lines.append("- Verified Drive MD5: " + q(delivery["drive_md5"]))
    else:
        lines.append("- Google Drive status: **" + delivery.get("drive_status", "pending") + "**")
        if delivery.get("detail"):
            lines.append("- Delivery note: " + delivery["detail"])
else:
    lines.append("Final PASS-only package assembly and Drive verification are pending.")

lines += [
    "",
    "## Release scope",
    "",
    "A PASS grade means the Revit 2025 family package passed the documented model/category/dimensional or authoritative-scope review required for this task. It is not fabrication, installation-clearance, procurement, photometric, hydraulic, or code approval. Documented visual/material simplifications remain as stated in the row and canonical notes.",
    "",
]

(OUT / "REVIEW.md").write_text("\n".join(lines), encoding="utf-8")
print(str(OUT / "REVIEW.md"))
print("rows", len(ledger["rows"]), "needs_user", len(ledger["needs_user"]), "failures", len(ledger["failures"]))
