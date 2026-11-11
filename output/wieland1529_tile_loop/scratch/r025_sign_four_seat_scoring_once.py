"""One-time immutable R025 scoring receipt and independent-review request.

Writes NEW score and five-section report only. No original critics, keys, room
statuses, owner decisions, historic receipts, histories or ledgers are modified.
"""
from __future__ import annotations

import contextlib
import hashlib
import io
import json
from decimal import Decimal
from pathlib import Path

import r025_four_seat_readonly_audit as audit

ROOT = Path(__file__).resolve().parents[1]


def fingerprint(rel):
    raw = (ROOT / rel).read_bytes()
    return {"sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)}


def audit_runtime():
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        try:
            audit.main()
        except SystemExit as ex:
            if ex.code:
                raise RuntimeError("R025 source/critique audit FAILED")
    summary = json.loads(output.getvalue())
    if summary["errors"] or summary["critic_files"] != 12 or summary["criterion_values"] != 114:
        raise RuntimeError("R025 genuine four-seat and criterion count not complete")
    if summary["signed_checks"] != {"r025_frozen": 13, "r025_prepared": 7}:
        raise RuntimeError("R025 frozen/prepared SHA audit incomplete")
    return summary


def new_file(rel, content):
    target = ROOT / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("x", encoding="utf-8", newline="\n") as out:
        out.write(content)
    return fingerprint(rel)


def main():
    data = audit_runtime()
    current_rooms = json.loads((ROOT / "state/ROOMS.json").read_text(encoding="utf-8"))
    if current_rooms["tile_budget_upgrade_stance"] is not None:
        raise RuntimeError("Owner budget stance changed; requires fresh independent review")
    for r in current_rooms["rooms"]:
        if r["id"] in data["scores"] and not (r["status"] == "blocked" and r["champion_id"] is None):
            raise RuntimeError("R025 room no longer blocked/without incumbent: " + r["id"])
    r026 = json.loads((ROOT / "state/ROUND026_TX_FOUR_SCHEMES_TWO_OWNER_CARDS_SIGNED.json").read_text(encoding="utf-8"))
    if r026["phase"] != "SOURCE_PREPARED_NOT_SUBMITTED_R025_ACTIVE" or r026["weighted_score"] is not None:
        raise RuntimeError("R026 phase changed; inspect before signing")
    for block in ("files", "parents"):
        for path, fp in r026[block].items():
            if fingerprint(path) != fp:
                raise RuntimeError("R026 signature changed: " + path)
    if len(r026["files"]) != 7 or len(r026["parents"]) != 3:
        raise RuntimeError("R026 exact source count does not match seven/three")
    weights = data["weights"]
    if {k: Decimal(str(v)) for k,v in weights.items()} != {
            "market": Decimal("0.30"),"design":Decimal("0.25"),
            "build":Decimal("0.25"),"cost":Decimal("0.20")}:
        raise RuntimeError("Role weights changed")
    receipt = {
        "round": 25,
        "phase": "3-FOUR_AUTHENTIC_CRITICS_SCORED_HARD_GATES_UNKNOWN_NO_CHAMPIONS",
        "scoring_separate_from_dispatch": True,
        "rooms": list(data["scores"]),
        "worker_family_run_id": "0a72848e-6cb2-462d-9478-1eccba986835",
        "source_freeze_receipt": {
            "file": "state/ROUND025_FORMAL_THREE_PH_ROOMS_SOURCE_FROZEN_PREDISPATCH.json",
            **fingerprint("state/ROUND025_FORMAL_THREE_PH_ROOMS_SOURCE_FROZEN_PREDISPATCH.json")},
        "dispatch_receipt": {
            "file": "state/ROUND025_FOUR_AUTHENTIC_CRITIC_DISPATCH.json",
            **fingerprint("state/ROUND025_FOUR_AUTHENTIC_CRITIC_DISPATCH.json")},
        "independent_predispatch_receipt": {
            "file": "state/ROUND025_INDEPENDENT_PREDISPATCH_REVIEWER22_CLEARANCE.json",
            **fingerprint("state/ROUND025_INDEPENDENT_PREDISPATCH_REVIEWER22_CLEARANCE.json")},
        "postdispatch_reviewer22_verdict": "CONTINUE FOR R025 POSTDISPATCH/R026 PREPARED SOURCE INTEGRITY ONLY; NOT SCORES OR GLOBAL DONE",
        "original_critic_reports": {
            room: {seat: {key: val for key,val in report.items() if key != "candidates"}
                   for seat, report in seats.items()}
            for room, seats in data["critics"].items()},
        "criterion_scores_originals_transcribed_and_recalculated": {
            room: {seat: report["candidates"] for seat, report in seats.items()}
            for room, seats in data["critics"].items()},
        "critic_count": 12,
        "individual_criterion_count": 114,
        "weights": weights,
        "candidate_scores": data["scores"],
        "all_24_individual_seat_means_at_least_3": True,
        "no_existing_incumbent_any_focus_room": True,
        "plus_0_25_rule": "N/A: all three focus rooms are blocked without a same-round incumbent; A/B comparison is not challenger-vs-incumbent authorization",
        "gate_status_and_disposition": {
            "all_six_individual_WALL": "PASS candidate product-listed for wet walls; PRIMARY shower ceiling separately UNKNOWN",
            "all_applicable_NICHE": "PASS candidate product-listed; PRIMARY no niche N/A",
            "all_six_LEVEL": "PASS exact F&D SKU published wet DCOF >=0.42 and Bathroom Floor YES, not raw measured lab result",
            "PH_PRIMARY_and_PH_BATH4_PAN": "PASS tile product use only, separate LINEAR/POINT pan; actual cut/drain geometry UNKNOWN",
            "PH_BATH3_PAN": "UNKNOWN owner TUB versus WALK-IN; TUB has NO tiled PAN, conditional POINT product listing PASS if WALK-IN",
            "native_geometry_focal_slivers_drains_openings": "UNKNOWN",
            "PH_BATH4_area_35_vs_27_SF": "UNKNOWN",
            "complete_carton_rounded_delivered_cost": "UNKNOWN; owner room budget unallocated, historical 125% screen only provisional",
            "chicago_actual_dye_lot_stock_ETA": "UNKNOWN",
            "PH_BATH3_owner_TUB_or_WALKIN_and_basin": "UNSELECTED",
            "selected_plumbing": "PRESERVED: PH PRIMARY 48-inch BNX LINEAR/BR73480, solid factory BNX and no niche; PH BATH4 selected WALK-IN BNX POINT; PH BATH3 Delta POINT iff WALK-IN",
            "champion_eligibility": "BLOCKED: not all applicable hard gates PASS"
        },
        "source_signature_checks": data["signed_checks"],
        "R026_source_integrity": "7/7 signed prepared files and 3/3 parent receipts PASS, separate future unsubmitted cohort",
        "historic_accounting": data["baseline"],
        "all_preexisting_champions_unchanged": True,
        "PH_focus_champions_unchanged": True,
        "owner_approval": False,
        "procurement_release": False,
        "independent_postscore_reviewer": None,
        "global_DONE": False,
        "independent_source_access_limitation": data["source_access_note"],
    }
    # Compute the succinct report from the same audited values, not hand-typed scores.
    p = data["scores"]
    summary_rows = []
    for name in p:
        a, b = p[name]["A"], p[name]["B"]
        better = "A" if a["weighted"] > b["weighted"] else "B"
        summary_rows.append("- " + name + ": A " + format(a["weighted"], ".2f") +
                            " (min " + str(a["minimum"]) + "), B " +
                            format(b["weighted"], ".2f") + " (min " + str(b["minimum"]) +
                            "); provisional higher " + better + "; BOTH blocked")
    report = "\n".join([
        "# R025 five-section independent post-scoring ROUND REPORT (NOT GLOBAL DONE)",
        "", "## 1. Authority and historic baseline",
        "Owner latest four permitted vendors Elm/MSI/Porcelanosa/Floor & Decor; 24in+ LEVEL/PAN, separate exact manufacturer wet application and published wet DCOF >=0.42. BOARD seats MARKET .30, DESIGN .25, BUILD .25, COST .20; per-seat minimum 3.0. Source feedback/TRADE_QUOTES read. 13 rooms, 26 instances, 27 historical source rows, $23,572.44 original four-unit tile material, 15% original waste counted once. 8 blocked/3 active/2 seeded and no newly accepted champions.",
        "", "## 2. Immutable R025 source, blind critic provenance",
        "R025 six frozen A/B candidate SHA+bytes, three private _keys, four frozen parent receipts all PASS (13/13). Seven prepared-source entries also PASS. Authentic Reviewer22 CONTINUE for blind DISPATCH only, followed by separate CONTINUE for postdispatch source integrity only. Dispatch recorded family 0a72848e-6cb2-462d-9478-1eccba986835. Original four fresh specialists: MARKET worker23, DESIGN worker24, BUILD worker25, COST worker26, all produced precisely three own-seat files. All 12 read-only checked, 114 independently recalculated 1-5 criteria, 24 correct one-decimal means, local links resolve and no forbidden private-file paths found. Worker browser-read activity is not independently provable.",
        "", "## 3. Authentic weighted score, not acceptance",
        *summary_rows,
        "Every candidate has four genuine seat means >=3.0. No focus room has an existing incumbent; a +0.25 challenger margin is NOT applicable. Do not invent a baseline or turn A/B difference into incumbent displacement. Neither letter is eligible for champion acceptance while required gates remain UNKNOWN; original blocked/null champion states untouched.",
        "", "## 4. Real product permissions and open hard gates",
        "Elm exact flat Cortar/Tones wet WALL and separately wet-listed NICHE PASS where applicable, no PH-PRIMARY niches; F&D Luxe Sand SKU101317949/Riviera Oat SKU101487775 exact LEVEL and applicable distinct PAN publish wet DCOF >=0.42 and Shower Floors YES; threshold is not raw measured reading. Actual native cuts/door-glass/drain offsets and <3in focal slivers UNKNOWN; PH-BATH4 35 vs 27 SF unresolved. Complete net LEVEL/PAN/WC splits, 15% LEVEL/25% cut PAN, cartons/freight/tax/trim, owner room cap, and Chicago matching lot/ETA UNKNOWN. PH-PRIMARY ceiling separately unqualified. PH-BATH3 TUB/WALK-IN and basin owner UNSELECTED; conditional Delta POINT only if WALK-IN. PH-BATH4 BNX POINT WALK-IN fixed; Primary BNX LINEAR/BR73480/solid grate/no niche and WC inherited once fixed.",
        "", "## 5. Independent Reviewer22 decision requested and next cohort",
        "Review newly signed state/ROUND025_AUTHENTIC_FOUR_SEAT_COLLECTION_SCORED_NO_CHAMPIONS.json and actual 12 original critiques; independently check 24 means, weighted sums, source integrity, source privacy, hard-gate nonacceptance and 13/26/27/$23,572.44; return exact CONTINUE or PRECISE FIX (no GLOBAL DONE). R026 TX-PRIMARY/TX-BATH3 remains only PREPARED: 4 neutral candidates plus research and 2 provisional owner addenda, signed 7/7 with 3 parents, no formal freeze/critics/scores. All owner packets still NOT APPROVED. No Revit/Smartsheet writes, outreach, emails, samples, purchases, fabrication engineering or Git.", ""
    ])
    if report.count("## ") != 5 or len(report) >= 4000:
        raise RuntimeError("R025 reviewer report violates five-section/<4000 char rule: " + str(len(report)))
    rel1 = "state/ROUND025_AUTHENTIC_FOUR_SEAT_COLLECTION_SCORED_NO_CHAMPIONS.json"
    rel2 = "state/ROUND025_FOUR_SEAT_SCORING_FIVE_SECTION_REVIEWER_REPORT.md"
    if any((ROOT / x).exists() for x in (rel1, rel2)):
        raise FileExistsError("Scoring receipt/report exists; do not regenerate valid signed work")
    fp1 = new_file(rel1, json.dumps(receipt, indent=2, ensure_ascii=False) + "\n")
    fp2 = new_file(rel2, report)
    assert json.loads((ROOT / rel1).read_text(encoding="utf-8"))["candidate_scores"] == p
    print("R025 SCORED NO CHAMPIONS; 12/12 critics; 114 criteria; 24 means; 6 weighted; sources 13/13; R026 signed 7/7 + parents 3/3")
    print("R025 RECEIPT", fp1["sha256"], fp1["bytes"])
    print("R025 REPORT", len(report), "chars", fp2["sha256"])


if __name__ == "__main__":
    main()
