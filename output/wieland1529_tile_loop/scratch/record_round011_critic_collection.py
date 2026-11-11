"""Collect eight authentic R011 specialist files; do not score or open private keys."""
from pathlib import Path
import hashlib
import json
import re

root = Path(__file__).resolve().parents[1]
submission = root / "state/ROUND011_SUBMISSION.json"
dispatch = root / "state/ROUND011_CRITIC_DISPATCH.json"
source = json.loads(submission.read_text(encoding="utf-8"))
workers = json.loads(dispatch.read_text(encoding="utf-8"))
assert source["phase"] == workers["phase"] == "2-board"
assert source["all_critic_scores"] is workers["all_critic_scores"] is None
assert workers["scoring_deferred_to_next_distinct_turn"]
assert workers["source_submission_sha256"] == hashlib.sha256(submission.read_bytes()).hexdigest()
for room_id, letters in source["candidate_files"].items():
    for letter, record in letters.items():
        b = (root / "rooms" / room_id / "board/round-011/candidates" / f"{letter}.md").read_bytes()
        assert hashlib.sha256(b).hexdigest() == record["sha256"] and len(b) == record["bytes"]

out = {
    "round": 11,
    "phase": "2-board",
    "event": "eight original independent specialist critiques collected for subsequent distinct-turn scoring",
    "source_receipt": "state/ROUND011_SUBMISSION.json",
    "source_submission_sha256": hashlib.sha256(submission.read_bytes()).hexdigest(),
    "dispatch_receipt": "state/ROUND011_CRITIC_DISPATCH.json",
    "source_dispatch_sha256": hashlib.sha256(dispatch.read_bytes()).hexdigest(),
    "critic_seats": workers["critic_worker_seats"],
    "weighted_scoring_complete": False,
    "all_critic_scores": None,
    "report_files": {},
}
local_links = 0
for room_id, letters in source["candidate_files"].items():
    folder = root / "rooms" / room_id / "board/round-011"
    out["report_files"][room_id] = {}
    for seat in ("market", "design", "build", "cost"):
        filename = folder / f"critic-{seat}.md"
        assert filename.is_file() and filename.stat().st_size > 1500, (room_id, seat, "missing")
        raw = filename.read_bytes()
        body = raw.decode("utf-8")
        for letter in letters:
            assert re.search(r"(?im)^#{1,3}\s+candidate\s+" + letter + r"\b", body), (room_id, seat, letter, "missing letter section")
        assert "top_fix" in body.lower() and "gate_flags" in body.lower() and "confidence" in body.lower()
        assert not re.search(r"(?i)_key\.json|state/ROOMS\.json|state/LEDGER\.md|\bincumbent\b|\bchampion\b", body), (room_id, seat, "blind role")
        for link in re.findall(r"\]\(([^)]+)\)", body):
            if link.startswith(("https://", "http://", "#", "mailto:")):
                continue
            assert (folder / link.split("#")[0]).exists(), (room_id, seat, link)
            local_links += 1
        out["report_files"][room_id][seat] = {
            "file": str(filename.relative_to(root)).replace("\\", "/"),
            "worker": workers["critic_worker_seats"][f"critic-{seat}"],
            "sha256": hashlib.sha256(raw).hexdigest(),
            "bytes": len(raw),
        }
assert sum(map(len, out["report_files"].values())) == 8
out["resolved_local_links"] = local_links
dest = root / "state/ROUND011_CRITIC_COLLECTION.json"
assert not dest.exists(), "Collection receipt already exists"
dest.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
print(f"PASS R011 eight authentic critique file fingerprints, {local_links} local links; phase 2-board, weighted scoring deferred")
