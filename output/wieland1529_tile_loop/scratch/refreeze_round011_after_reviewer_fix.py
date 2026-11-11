"""One-time pre-dispatch correction of R011 PH3-A source-lineage mislabel."""
from pathlib import Path
import hashlib
import json

root = Path(__file__).resolve().parents[1]
receipt_path = root / "state/ROUND011_SUBMISSION.json"
receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
assert receipt["round"] == 11 and receipt["all_critic_scores"] is None
assert receipt["phase"] == "2-board"
assert receipt["independent_preflight_status"] == "pending independent non-Pro Reviewer"
assert receipt["new_board_dispatch_status"].startswith("NOT DISPATCHED")
assert "pre_dispatch_corrected_source_lineage" not in receipt
target = ("PH-BATH3", "A")
expected_old = "7715d2c39ed37a0ec4ffc85f6146b2ea5dcb0f718e05d00a2dfbcd3a76671479"
assert receipt["candidate_files"][target[0]][target[1]]["sha256"] == expected_old
for rid, candidates in receipt["candidate_files"].items():
    folder = root / "rooms" / rid / "board/round-011"
    assert (folder / "_key.json").exists()
    assert not list(folder.glob("critic-*.md"))
    for letter, recorded in candidates.items():
        f = folder / "candidates" / (letter + ".md")
        raw = f.read_bytes()
        sha = hashlib.sha256(raw).hexdigest()
        if (rid, letter) == target:
            body = raw.decode("utf-8")
            assert "Original **Opal wall 86.20 SF plus Sandstone niche 8.63 SF**" in body
            assert "The original Sandstone wall + niche" not in body
            assert sha != expected_old
            replacement = {"sha256": sha, "bytes": len(raw)}
        else:
            assert sha == recorded["sha256"] and len(raw) == recorded["bytes"]
receipt["candidate_files"][target[0]][target[1]] = replacement
receipt["pre_dispatch_corrected_source_lineage"] = {
    "room": "PH-BATH3",
    "letter": "A",
    "reviewer": "worker-8",
    "reason": "Correct original 86.20 SF wet wall as Opal (not Sandstone); 8.63 SF historical Sandstone niche separate",
    "prior_sha256": expected_old,
    "updated_sha256": replacement["sha256"],
    "critics_dispatched": False,
    "all_critic_scores": None,
}
receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
print("PASS R011 pre-dispatch targeted source correction PH3-A", replacement, "3 other source SHA unchanged, zero critic dispatch")
