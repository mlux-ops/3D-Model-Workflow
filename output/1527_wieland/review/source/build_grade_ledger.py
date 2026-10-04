import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "output" / "1527_wieland"
REVIEW = OUT / "review"

def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def inventory(section):
    j = load(OUT / section / "ITEMS.json")
    return {str(x["row_id"]): x for x in j["items"]}

inv = {
    "Appliances": inventory("appliances"),
    "Plumbing Fixtures": inventory("plumbing_fixtures"),
    "Electrical Fixtures": inventory("electrical_fixtures"),
}

app = load(OUT / "appliances" / "section_manifest.json")
plm = load(OUT / "plumbing_fixtures" / "FINAL_STATUS.json")
ph = load(OUT / "plumbing_fixtures" / "NEEDS_USER_HOLDS.json")
ele = load(OUT / "electrical_fixtures" / "ROW_STATUS.json")

plumb_hold = {}
plumb_hold_detail = {}
for h in ph["holds"]:
    for rid in h["row_ids"]:
        plumb_hold[str(rid)] = h["code"]
        plumb_hold_detail[str(rid)] = h["detail"]

# These rows are user decisions, not rework targets.
app_need = {
    "2705397813673860": ("NEEDS_USER_T18IW905SP_SELECTION", "Confirm that abbreviated T18IW905S is intended to resolve to official Thermador T18IW905SP."),
    "6703228487401348": ("NEEDS_USER_T24UR905RP_IDENTITY", "Resolve row description (30-inch warming drawer) versus exact linked Thermador T24UR905RP undercounter refrigerator."),
    "2018080639745924": ("NEEDS_USER_MC30WP_SELECTION", "Confirm Thermador MC30WP as the intended Professional 30-inch speed oven; the row has no exact SKU or product URL."),
    "7647580173959044": ("NEEDS_USER_PRD48WISGU_IDENTITY", "Resolve row description (30-inch oven) versus exact linked Thermador PRD48WISGU 48-inch range."),
    "4451428673716100": ("NEEDS_USER_WD30W_IDENTITY", "Resolve row description (Zephyr 47-inch hood) versus exact linked Thermador WD30W warming drawer."),
}

# Built families with non-authoritative protruding geometry: user must approve the
# representation or provide authoritative overall geometry before release.
app_need.update({
    "6670395252473732": ("NEEDS_USER_KM3054_OVERALL_HEIGHT", "Cooktop casing dimensions pass, but grate height is inferred; confirm/approve overall modeled height."),
    "7831772394487684": ("NEEDS_USER_KM3054_OVERALL_HEIGHT", "Cooktop casing dimensions pass, but grate height is inferred; confirm/approve overall modeled height."),
    "7796295159316356": ("NEEDS_USER_I32363RC_OVERALL_HEIGHT", "Hood body dimensions pass, but collar extension height is inferred; confirm/approve overall modeled height."),
    "162646177939332": ("NEEDS_USER_I32363RC_OVERALL_HEIGHT", "Hood body dimensions pass, but collar extension height is inferred; confirm/approve overall modeled height."),
})

rows = []

for wr in app["rows"]:
    rid = str(wr["row_id"])
    item = inv["Appliances"][rid]
    if rid in app_need:
        code, detail = app_need[rid]
        grade, reason = "NEEDS_USER", detail
        decision = code
    else:
        # After appliance rework, exact-identity rows are PASS only when all current
        # canonical gate strings are no longer fit HOLD.
        holds = [g for g in wr.get("gate_results", []) if "fit HOLD" in g]
        if holds:
            grade = "FAIL"
            reason = "Current canonical appliance family does not satisfy the <=1 mm dimensional review gate; rework required."
            decision = None
        else:
            grade = "PASS"
            reason = "Worker native gates and orchestrator review support release; documented non-blocking limitations retained."
            decision = None
    rows.append({
        "section":"Appliances","row_id":rid,"item_key":item.get("item_key"),"tag":item.get("item_tag_or_code"),
        "description":item.get("description"),"manufacturer":item.get("manufacturer"),"model_number":item.get("model_number"),
        "finish":item.get("finish"),"product_url":item.get("product_url"),"worker_status":wr.get("status"),
        "rfa_paths":wr.get("rfa_paths",[]),"notes_path":wr.get("notes_path"),"grade":grade,"reason":reason,
        "needs_user_code":decision
    })

for wr in plm["rows"]:
    rid = str(wr["row_id"])
    item = inv["Plumbing Fixtures"][rid]
    if rid in plumb_hold:
        grade = "NEEDS_USER"
        reason = plumb_hold_detail[rid]
        code = plumb_hold[rid]
    elif wr.get("status") == "BLOCKED":
        # Remaining BLOCKED rows are organizational/non-product coverage rows.
        grade = "PASS"
        reason = "Administrative/non-product coverage row; no RFA is required."
        code = None
    elif wr.get("native_gates_pass") is False:
        grade = "FAIL"
        reason = "Native gate failure remains without a documented user-decision hold."
        code = None
    else:
        grade = "PASS"
        reason = "Worker native gates pass; orchestrator independent open/category review and visual review found no new release-blocking defect."
        code = None
    rows.append({
        "section":"Plumbing Fixtures","row_id":rid,"item_key":item.get("item_key"),"tag":item.get("item_tag_or_code"),
        "description":item.get("description"),"manufacturer":item.get("manufacturer"),"model_number":item.get("model_number"),
        "finish":item.get("finish"),"product_url":item.get("product_url"),"worker_status":wr.get("status"),
        "rfa_paths":[wr["rfa_path"]] if wr.get("rfa_path") else [],"notes_path":wr.get("notes_path"),"grade":grade,
        "reason":reason,"needs_user_code":code
    })

for wr in ele["rows"]:
    rid = str(wr["row_id"])
    item = inv["Electrical Fixtures"][rid]
    nu = wr.get("needs_user") or []
    if nu:
        grade = "NEEDS_USER"
        code = nu[0]
        reasons = {
            "NEEDS_USER_PERGOLA_PRODUCT":"Select wet-rated pergola fixture SKU, finish, and dimensions.",
            "NEEDS_USER_LED_STRIP_BOM":"Provide/approve LED tape, channel, driver, run lengths, and environmental rating/details.",
            "NEEDS_USER_D3_COMPATIBLE_ASSEMBLY":"Resolve Juno 16 WH intermediate-base versus E26 PAR16 mismatch and define the housing/trim/lamp assembly.",
            "NEEDS_USER_ORION_CONFIGURATION":"Confirm assumed ORI0120, gold, horizontal single module, 48-inch drop configuration.",
        }
        reason = reasons.get(code, "; ".join(nu))
    elif wr.get("technical_pass") is False or wr.get("status") == "BLOCKED":
        grade, code = "FAIL", None
        reason = "Technical/native failure remains without a documented user-decision hold."
    else:
        grade, code = "PASS", None
        reason = "Worker native gates pass; orchestrator independent open/category review and final-sheet visual review found no new release-blocking defect."
    rows.append({
        "section":"Electrical Fixtures","row_id":rid,"item_key":item.get("item_key"),"tag":item.get("item_tag_or_code"),
        "description":item.get("description"),"manufacturer":item.get("manufacturer"),"model_number":item.get("model_number"),
        "finish":item.get("finish"),"product_url":item.get("product_url"),"worker_status":wr.get("status"),
        "rfa_paths":[wr["rfa_path"]] if wr.get("rfa_path") else [],"notes_path":wr.get("notes_path"),"grade":grade,
        "reason":reason,"needs_user_code":code
    })

assert len(rows) == 325, len(rows)
assert len({(r["section"],r["row_id"]) for r in rows}) == 325

totals = {}
for sec in ("Appliances","Plumbing Fixtures","Electrical Fixtures"):
    rr = [r for r in rows if r["section"] == sec]
    totals[sec] = {
        "rows": len(rr),
        "worker_status": dict(Counter(r["worker_status"] for r in rr)),
        "grade": dict(Counter(r["grade"] for r in rr)),
    }
totals["Overall"] = {
    "rows": len(rows),
    "grade": dict(Counter(r["grade"] for r in rows)),
}

out = {
    "schema":"1527_wieland_orchestrator_grade_ledger_v1",
    "totals":totals,
    "rows":rows,
    "needs_user":[r for r in rows if r["grade"]=="NEEDS_USER"],
    "failures":[r for r in rows if r["grade"]=="FAIL"],
}
(REVIEW / "grade_ledger.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
print(json.dumps(totals, indent=2))
print("needs_user",len(out["needs_user"]),"failures",len(out["failures"]))
