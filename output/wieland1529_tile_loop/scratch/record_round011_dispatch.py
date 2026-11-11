"""Record authorized R011 blind critic assignments without scoring or changing frozen candidates."""
from pathlib import Path
import hashlib
import json

root = Path(__file__).resolve().parents[1]
receipt = json.loads((root / "state/ROUND011_SUBMISSION.json").read_text(encoding="utf-8"))
dest = root / "state/ROUND011_CRITIC_DISPATCH.json"
assert not dest.exists(), "Dispatch is a one-time historical receipt"
assert receipt["phase"] == "2-board" and receipt["all_critic_scores"] is None
assert receipt["pre_dispatch_corrected_source_lineage"]["updated_sha256"] == receipt["candidate_files"]["PH-BATH3"]["A"]["sha256"]
for room_id, candidates in receipt["candidate_files"].items():
    for letter, meta in candidates.items():
        raw = (root / "rooms" / room_id / "board/round-011/candidates" / f"{letter}.md").read_bytes()
        assert hashlib.sha256(raw).hexdigest() == meta["sha256"] and len(raw) == meta["bytes"]
current = root / "state/ROOMS.json"
state = json.loads(current.read_text(encoding="utf-8"))
for room in state["rooms"]:
    if room["id"] not in receipt["candidate_files"]:
        continue
    assert room["status"] == "blocked" and room["champion_id"] is None
    assert room["round_011_submission"]["scores"] is None
    assert not room["round_011_submission"]["preflight_completed"]
    room["round_011_submission"]["preflight_completed"] = True
    room["round_011_submission"]["status"] = "independent_reviewer_cleared_critics_dispatched_pending_scores"
    room["round_011_submission"]["reviewer_clearance"] = "worker-8 DONE FOR R011 FOUR-SEAT DISPATCH after targeted source-lineage FIX"
dispatch = {
    "round": 11,
    "as_of": "2026-11-06",
    "phase": "2-board",
    "all_critic_scores": None,
    "scoring_deferred_to_next_distinct_turn": True,
    "source_submission": "state/ROUND011_SUBMISSION.json",
    "source_submission_sha256": hashlib.sha256((root / "state/ROUND011_SUBMISSION.json").read_bytes()).hexdigest(),
    "candidate_sha256": receipt["candidate_files"],
    "independent_reviewer": "worker-8",
    "reviewer_verdict": "DONE FOR R011 FOUR-SEAT DISPATCH",
    "critic_worker_seats": {
        "critic-market": "worker-3",
        "critic-design": "worker-9",
        "critic-build": "worker-10",
        "critic-cost": "worker-6"
    },
    "source_roles_unavailable_to_specialists": True,
    "owner_approvals": False,
    "procurement_released": False
}
dest.write_text(json.dumps(dispatch, indent=2) + "\n", encoding="utf-8")
current.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print("PASS R011 4 independent blind specialist seats dispatched after reviewer clearance; 4 candidate SHA intact, scores null, owner/release false")
