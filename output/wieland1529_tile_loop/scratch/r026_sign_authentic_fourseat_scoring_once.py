"""Immutable, new-only R026 signed score receipt and five-section reviewer report.

Calls strict read-only audit for all eight genuine TX critic files. It never
rewrites signed freezes, worker reports, keys or the 13-room state.
"""
from __future__ import annotations
import contextlib
import hashlib
import io
import json
from pathlib import Path

import r026_authentic_fourseat_readonly_audit as audit

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = "state/ROUND026_AUTHENTIC_FOUR_SEAT_COLLECTION_SCORED_NO_CHAMPIONS.json"
REPORT = "state/ROUND026_FOUR_SEAT_SCORING_FIVE_SECTION_REVIEWER_REPORT.md"


def sha(rel: str) -> dict:
    raw = (ROOT / rel).read_bytes()
    return {"sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)}


def run_audit() -> dict:
    captured = io.StringIO()
    audit.ERRORS.clear()
    with contextlib.redirect_stdout(captured):
        try:
            audit.main()
        except SystemExit as e:
            if e.code:
                raise RuntimeError("R026 audit has errors") from None
    data = json.loads(captured.getvalue())
    assert data["authentic_critic_files"] == 8
    assert data["criterion_values"] == 76 and data["candidate_seat_means"] == 16
    assert not data["errors"]
    return data


def exclusive(rel: str, s: str):
    path = ROOT / rel
    if path.exists():
        raise FileExistsError(rel + " already signed; do not regenerate")
    with path.open("x", encoding="utf-8", newline="\n") as f:
        f.write(s)
    return sha(rel)


def main():
    data = run_audit()
    selected = data["weighted"]
    assert selected["TX-PRIMARY"]["A"]["weighted"] == 3.62
    assert selected["TX-PRIMARY"]["B"]["weighted"] == 3.55
    assert selected["TX-BATH3"]["A"]["weighted"] == 3.11
    assert selected["TX-BATH3"]["B"]["weighted"] == 3.70
    assert not selected["TX-PRIMARY"]["A"]["four_seats_minimum_3"]
    assert not selected["TX-PRIMARY"]["B"]["four_seats_minimum_3"]
    assert not selected["TX-BATH3"]["A"]["four_seats_minimum_3"]
    assert selected["TX-BATH3"]["B"]["four_seats_minimum_3"]
    d = json.loads((ROOT/"state/ROUND026_FOUR_FRESH_AUTHENTIC_CRITIC_DISPATCH.json").read_text(encoding="utf-8"))
    if d["score_in_this_dispatch_phase"] is not False:
        raise RuntimeError("same-turn dispatch scoring not allowed")
    room_data = json.loads((ROOT/"state/ROOMS.json").read_text(encoding="utf-8"))["rooms"]
    for room in room_data:
        if room["id"] in selected and not (room["status"] == "blocked" and room["champion_id"] is None):
            raise RuntimeError("R026 existing incumbent changed")
    receipt = {
       "round":26,"phase":"DISTINCT_POSTDISPATCH_COLLECTED_FOUR_AUTHENTIC_SCORED_NO_CHAMPIONS",
       "reviewer_status":"PENDING_INDEPENDENT_POSTSCORE_REVIEW",
       "signed_predecessors":{
          rel:sha(rel) for rel in (
            "state/ROUND026_FORMAL_TWO_TX_ROOMS_SOURCE_FROZEN_PREDISPATCH.json",
            "state/ROUND026_INDEPENDENT_PREDISPATCH_REVIEWER27_CLEARANCE.json",
            "state/ROUND026_FOUR_FRESH_AUTHENTIC_CRITIC_DISPATCH.json",
            "state/ROUND026_TX_FOUR_SCHEMES_TWO_OWNER_CARDS_SIGNED.json",
            "state/ROUND025_SCOPEFIX1_INDEPENDENT_POSTSCORE_REVIEWER30_CLEARANCE.json")
       },
       "freeze_signed_checks":data["signed_counts"],
       "authentic_worker_ids":data["workers"],
       "original_critic_reports":{"room_count":2,"file_count":8,"candidate_seat_means":16,"criterion_values":76,
           "fingerprints_scores_local_links":data["critic_fingerprints_and_scores"]},
       "weights":data["weights"],
       "scoring_independently_recomputed":selected,
       "seat_minimum_ge_3_required":True,
       "TX_PRIMARY_both_A_B_COST_below_3":True,
       "TX_BATH3_A_COST_below_3":True,
       "TX_BATH3_B_every_seat_ge_3":True,
       "real_same_round_incumbent":False,
       "plus_0_25_rule":"N/A: both rooms BLOCKED no same-round incumbent, cannot manufacture weighted margin",
       "hard_gate_pass":False,
       "hard_gate_findings":{
          "exact_Elm_wet_WALL_NICHE":"PASS where applicable based on dated individual product evidence; primary has NO niche",
          "exact_FD_floor_PAN_item":"PASS for individual product use: Luxe 101317949 and Riviera 101487775 published wet DCOF >=0.42 and Bath/Shower Floor",
          "TX_PRIMARY_tiled_shower_ceiling":"UNKNOWN separate overhead application, wall permission cannot transfer",
          "native_room_drain_cut_geometry":"UNKNOWN, no verified receipts, visible <3in sliver and installer PAN cuts not proved",
          "TX_BATH3_TUB_vs_WALKIN":"OWNER UNSELECTED, selected square BNX POINT only WALK-IN, no tiled PAN if tub",
          "complete_carton_rounded_delivered_cost_vs_owner_allocated_budget":"UNKNOWN; original 125% material comparison provisional",
          "Chicago_exact_lot_quantity_inventory_ETA":"UNKNOWN; non-Chicago public prices not actual Chicago delivered offer",
          "owner_do_not_use":"PASS no forbidden new vendor",
          "no_new_champions":"BLOCKED on original minimum scores and mandatory unknown gates"
       },
       "historical_baseline":data["baseline"],
       "rooms_status_counts":data["status_counts"],
       "original_source_waste_included_once_pct":15,
       "R025_corrected_scopefix":"Independent Reviewer30 cleared corrected scoring for NONACCEPTANCE only; no champion",
       "R026_separate_program":"R026 four genuine specialist reports now collected in next turn; no score in R026 dispatch phase",
       "room_statuses_changed":False,"champions_changed":False,"owner_approval":False,
       "procurement_release":False,"global_DONE":False
    }
    report = """# R026 independent post-scoring five-section ROUND REPORT

## 1. Authority, history and accepted phase boundary
Owner latest four vendors Elm/MSI/Porcelanosa/Floor & Decor; 24in+ floor and installer-cut PAN preferred, exact wet WALL/NICHE and bath LEVEL/PAN published wet DCOF >=0.42, separated per product. R025 Reviewer30 independently cleared corrected scores for NONACCEPTANCE ONLY. Historic 13 rooms/26 physical instances/27 material rows/$23,572.44 four-unit material, original gross 15% waste once. Current statuses 8 blocked, 3 active, 2 seeded.

## 2. R026 formal provenance and genuine four-seat collection
R026 four neutral frozen TX-PRIMARY/TX-BATH3 A/B files, two segregated prime-only keys, four parent receipts SHA+bytes PASS. Prepared R026 7/7 files and 3/3 parents PASS. Independent Reviewer27 CONTINUE for blind DISPATCH ONLY; separate dispatch receipt worker31 MARKET(.30), worker32 DESIGN(.25), worker33 BUILD(.25), worker34 COST(.20). DISTINCT next prime turn collects eight genuine critics. Read-only audits verify all 8 files, 76 original criterion marks, 16 one-decimal half-up means and linked source isolation; no prior outcomes/private keys/other room files linked. Raw worker read histories not independently evidenced.

## 3. Original critic weighted arithmetic and no champion result
- TX-PRIMARY A: MARKET 4.0 DESIGN 4.0 BUILD 3.6 COST 2.6 = 3.62; min 2.6 FAIL.
- TX-PRIMARY B: MARKET 3.8 DESIGN 3.8 BUILD 3.6 COST 2.8 = 3.55; min 2.8 FAIL.
- TX-BATH3 A: MARKET 3.5 DESIGN 3.6 BUILD 3.2 COST 1.8 = 3.11; min 1.8 FAIL.
- TX-BATH3 B: MARKET 4.0 DESIGN 4.0 BUILD 3.6 COST 3.0 = 3.70; seat PASS, hard gates UNKNOWN.
Both rooms BLOCKED with NO same-round incumbent. +0.25 replacement rule N/A. No accepted champion, owner choice or procurement release.

## 4. Material selection improvements and unresolved hard gates
Correct Clay FLAT wet WALL, individually wet Copper, Soho Emerald and Sandstone NICHE; no TX Primary niche. F&D Riviera Oat 24x48 SKU101487775 and Luxe Sand 24x24 SKU101317949 publish wet DCOF >=0.42 and Shower Floors YES for separate LEVEL/PAN product-use checks; no invented raw lab value. TX Primary BNX 48in LINEAR+BR73480 solid grate/TX-WC inherits once, no niche. TX Bath3 owner TUB/WALK-IN UNSELECTED, Brizo BNX POINT only if WALK-IN (no PAN with tub), no false basin decision. Native door, niche, drain, visible cut/sliver and ceiling assembly receipts UNKNOWN. Chicago matching lot/ETA and full delivered carton-rounded budget UNKNOWN; Soho Emerald exact 1529 price UNKNOWN, 125% historic proxy not owner allocation. Product permission cannot confer full assembly PASS.

## 5. Reviewer decision and subsequent selection cohort
Independently review state/ROUND026_AUTHENTIC_FOUR_SEAT_COLLECTION_SCORED_NO_CHAMPIONS.json and original eight files; authenticate all sources/weights/76 marks/16 means, source privacy and no-promotions, return exact CONTINUE FOR R026 NONACCEPTANCE SCORING ONLY or PRECISE FIX with file/line. Do not imply GLOBAL DONE. Next prime focus: new evidence-backed PH-BATH2/TX-BATH2/TX-BATH4 tub selection alternatives after R024, preserving three Duravit tubs NO tiled PAN and owner fixture/basin holds. Final 13 owner cards remain PROVISIONAL pending genuine hard-gate champions.
"""
    if report.count("## ") != 5 or len(report) >= 4000:
        raise RuntimeError(f"Report must have five sections, <4k; got {len(report)} chars")
    if (ROOT / RECEIPT).exists() or (ROOT / REPORT).exists():
        raise FileExistsError("Score receipt/report already exist; no signed artifact regeneration")
    a=exclusive(RECEIPT, json.dumps(receipt, indent=2, ensure_ascii=False)+"\n")
    b=exclusive(REPORT,report)
    print("R026 POSTDISPATCH SCORED 8 reports 76 criteria 16 means; no champion; signed score",a["sha256"],a["bytes"])
    print("R026 FIVE_SECTION_REPORT",len(report),"chars SHA",b["sha256"])


if __name__=="__main__":
    main()
