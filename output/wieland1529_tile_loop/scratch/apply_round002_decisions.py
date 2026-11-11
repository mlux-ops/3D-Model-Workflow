"""Apply completed four-critic TX Round002 board decisions, preserving v4 history."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / "state/ROOMS.json"
state = json.loads(path.read_text(encoding="utf-8"))
scored = json.loads((ROOT/"state/ROUND002_SCORING.json").read_text(encoding="utf-8"))["room_results"]
fixes = {
    "TX-BATH2": [
        "Obtain exact manufacturer wet DCOF >=0.42 for PF07 Cream 12x24 or select independently documented compliant floor.",
        "Verify actual room/tub/niche dimensions and deduct niche field once; review physical Copper/Sandstone/Cream sample and trim.",
        "Owner must choose TX Bath 2 basin; no assumed sink model.",
        "Project-specific PF07 cartons, Chicago stock, freight/lead and room budget allocation missing."
    ],
    "TX-BATH3": [
        "Owner/model must reconcile tub alcove against selected walk-in shower and Brizo BT062415-BNX point drain.",
        "Measure actual shower pan, wall heights, four-plane slope, curb and PF05 12x24-to-2x2 area split, no invented pan SF.",
        "Secure measured wet DCOF >=0.42 for both PF05 12x24 and PF05 2x2 (or documented compliant substitutions).",
        "Obtain 2x2 pan quote, actual Daltile Chicago inventory/ETA, full washout of historical tub takeoff and room budget."
    ],
    "TX-BATH4": [
        "Obtain exact tested wet DCOF >=0.42 for Cortar Bone 12x24 Soft or select documented qualified bath floor.",
        "Measure alcove/niche/flat field and confirm Charcoal/Soho cut and Matte White fixture transition; no wet Bone Ribbed use.",
        "Replace unapproved Clara Caviar wet niche with wet-listed Soho only after owner approval and quote.",
        "Resolve current Soho price, Cortar 300 SF historical minimum, lots/lead, trims, freight and room budget."
    ]
}
assert len(state["rooms"]) == 13
seen = set()
for room in state["rooms"]:
    rid = room["id"]
    if rid not in scored:
        continue
    assert room["status"] == "active" and room["last_round"] == 2 and room["champion_id"] == "v4-"+rid
    assert room["round_002_submission"]["status"] == "blind_review_pending"
    result = scored[rid]
    room["prior_champion_id"] = room["champion_id"]
    room["status"] = "blocked"
    room["champion_id"] = None
    room["champion_score"] = None
    room["last_round"] = 2
    room["provisional_preference_id"] = "round-002-" + result["provisional_design_preference"]
    room["board_round_002"] = result
    room["board_round_002"]["report"] = "board/round-002/ROUND_REPORT.md"
    room["round_002_submission"]["status"] = "review_complete_scored"
    room["round_002_submission"]["scores"] = {
        letter: candidate["weighted_score"] for letter,candidate in result["candidates"].items()
    }
    room["round_002_submission"]["owner_approved"] = False
    room["decision_blockers"] = fixes[rid]
    for fix in fixes[rid]:
        if fix not in room["open_gaps"]:
            room["open_gaps"].append(fix)
    seen.add(rid)
assert seen == set(scored), seen
path.write_text(json.dumps(state,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
print("UPDATED:",", ".join(sorted(seen)))
assert all(x["champion_id"] is None and x["status"] == "blocked" for x in state["rooms"] if x["id"] in seen)
