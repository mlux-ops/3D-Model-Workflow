"""Mark submitted TX bath candidates active without scoring the new board."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / "state" / "ROOMS.json"
state = json.loads(path.read_text(encoding="utf-8"))
focus = {"TX-BATH2", "TX-BATH3", "TX-BATH4"}
assert len([r for r in state["rooms"] if r["id"] in focus]) == 3
for room in state["rooms"]:
    if room["id"] not in focus:
        continue
    assert room["status"] == "seeded" and room["last_round"] == 0, room["id"]
    assert room["champion_score"] is None
    room["status"] = "active"
    room["last_round"] = 2
    room["round_002_submission"] = {
        "status": "blind_review_pending",
        "candidate_count": 2,
        "critics_required": ["critic-market", "critic-design", "critic-build", "critic-cost"],
        "scores": None,
        "owner_approved": False,
        "source_geometry_verified": False,
        "exact_floor_wet_dcof_verified": False,
        "source_note": "Manufacturer target DCOF is not an exact measured finish-specific result."
    }
path.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print("room_count", len(state["rooms"]))
print("round2_active", [r["id"] for r in state["rooms"] if r.get("round_002_submission")])
