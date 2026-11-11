"""Guarded R033 inheritance-only state update; retains all earlier room history."""
from pathlib import Path
import subprocess
import sys
import json
from decimal import Decimal

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / "state" / "ROOMS.json"
d = json.loads(path.read_text(encoding="utf-8-sig"))
assert len(d["rooms"]) == 13
assert sum(r.get("unit_count") == 2 for r in d["rooms"]) == 13
assert {r["id"] for r in d["rooms"]} == {
    "PH-PRIMARY","PH-BATH2","PH-BATH3","PH-BATH4","PH-POWDER","PH-WC",
    "TX-PRIMARY","TX-BATH2","TX-BATH3","TX-BATH4","TX-POWDER","TX-POWDER2","TX-WC"
}
run = subprocess.run([sys.executable, "-B", str(ROOT / "scratch" / "r033_board_arithmetic.py")],
                     capture_output=True, text=True, check=True)
board = json.loads(run.stdout)
assert board["criterion_count"] == 76
plans = {
    "PH-WC": {"parent": "PH-PRIMARY", "former": "v4-PH-WC", "sku": "101317949",
              "name": "Floor & Decor Luxe Sand Matte Porcelain 24x24",
              "labels": ["313A", "313B"], "candidate_labels": ["304A", "304B"]},
    "TX-WC": {"parent": "TX-PRIMARY", "former": "v4-TX-WC", "sku": "101487775",
              "name": "Floor & Decor Riviera Oat Matte Porcelain 24x48",
              "labels": ["203A", "203B"], "candidate_labels": ["202A", "202B"]},
}
for id, p in plans.items():
    wc = next(r for r in d["rooms"] if r["id"] == id)
    parent = next(r for r in d["rooms"] if r["id"] == p["parent"])
    assert wc["status"] == "seeded" and wc["champion_id"] == p["former"], id
    assert wc["champion_score"] is None and wc["owner_status"] is None and wc["last_round"] == 0, id
    assert wc["revit_room_numbers"] == p["labels"], id
    assert wc["carried_quote_material_subtotal_usd_per_unit"] == 0, id
    assert parent["status"] == "blocked" and parent["champion_id"] is None and parent["owner_status"] is None, id
    score = board["data"][id]
    assert all(score[c]["seat_gate_pass"] for c in ("A","B"))
    assert Decimal(score["A"]["weighted"]) > Decimal(score["B"]["weighted"])
    wc["prior_champion_id"] = p["former"]
    wc["status"] = "blocked"
    wc["champion_id"] = None
    wc["champion_score"] = None
    wc["last_round"] = 33
    wc["provisional_preference_id"] = "round-033-A"
    wc["board_round_033"] = {
        "status": "authentic_strict_blind_scored_parent_inheritance_only_NOT_accepted",
        "source": "state/ROUND033_TWO_INHERITED_WC_FOUR_SEAT_DECISIONS.md",
        "workers": {"market":63, "design":64, "build":68, "cost":66},
        "weights": {"market":0.30,"design":0.25,"build":0.25,"cost":0.20},
        "original_criterion_ratings": 76,
        "candidates": {
            c: {
                "seat_scores": {seat: float(score[c][seat]["mean"]) for seat in ("market","design","build","cost")},
                "weighted_score": float(score[c]["weighted"]),
                "seat_minimum_pass": score[c]["seat_gate_pass"],
                "floor_product_gate_pass": True,
                "full_room_accepted": False,
                "owner_approved": False
            } for c in ("A","B")
        },
        "board_preference": "A",
        "conditional_inherited_floor_sku": p["sku"],
        "conditional_inherited_floor_product": p["name"],
        "no_genuine_accepted_independent_wc_incumbent": True,
        "displacement_margin_rule": "inapplicable to seeded v4 selection; WC cannot independently displace parent choice",
        "required_parent_room": p["parent"],
        "parent_shower_ceiling_technical_gate": "BLOCKED: no independently manufacturer-qualified tiled wet CEILING and compatible overhead assembly",
        "wc_tiled_surfaces": ["dry floor LEVEL inherited from parent"],
        "not_wc_tiled": ["WALL","NICHE","CEILING","PAN"],
        "separate_wc_purchase_sf": 0,
        "separate_wc_purchase_usd": 0,
        "waste": "original parent gross pool already includes WC; 15% applied once, never again",
        "candidate_copy_labels": p["candidate_labels"],
        "source_geometry_copy_labels": p["labels"],
        "room_number_discrepancy": "must reconcile; do not relabel source geometry silently",
        "other_open_items": ["actual doorway/threshold and visible >=3-in tile cut proof",
                             "Chicago same-lot availability and delivered cost",
                             "owner room tile budget FILL IN", "final owner approval"]
    }
    assert wc["owner_status"] is None and wc["champion_id"] is None
assert sum(r["status"] == "provisional champion" for r in d["rooms"]) == 9
assert sum(r["status"] == "blocked" for r in d["rooms"]) == 4
assert sum(r["status"] == "seeded" for r in d["rooms"]) == 0
assert sum(r["owner_status"] is not None for r in d["rooms"]) == 0
path.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print("PASS: R033 integrated 9 provisional + 4 blocked (2 Primary, 2 inherited WC), 0 final; no duplicate WC quantities, 13 rooms/26 copies preserved.")
