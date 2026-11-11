"""Read-only Round 002 preflight plus one auditable local JSON receipt.

Checks submission identity, six candidate heads, blind presentation, citations,
room state, and prior critic completeness. Does not calculate Round 002 scores.
"""
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]
FOCUS = {
    "TX-BATH2": ("B", "C"),
    "TX-BATH3": ("A", "B"),
    "TX-BATH4": ("A", "B"),
}
SEATS = ("market", "design", "build", "cost")
results = {
    "round": 2,
    "date": "2026-11-06",
    "phase": "2-board",
    "scoring_deferred_to_next_turn": True,
    "candidate_files": {},
    "round1_critics": {},
    "room_state": {},
    "broken_relative_links": [],
    "warnings": [],
}
state = json.loads((ROOT / "state" / "ROOMS.json").read_text(encoding="utf-8"))
assert len(state["rooms"]) == 13
indexed = {room["id"]: room for room in state["rooms"]}
assert len(indexed) == len(state["rooms"])
for room, letters in FOCUS.items():
    base = ROOT / "rooms" / room / "board" / "round-002"
    key = json.loads((base / "_key.json").read_text(encoding="utf-8"))
    assert key["room_id"] == room and key["blind_review"] is True
    assert {k for k in key if k in ("A", "B", "C")} == set(letters)
    files = sorted((base / "candidates").glob("*.md"))
    assert {p.stem for p in files} == set(letters)
    record = indexed[room]
    assert record["last_round"] == 2 and record["status"] == "active"
    assert record["champion_score"] is None
    assert record["round_002_submission"]["scores"] is None
    assert record["round_002_submission"]["status"] == "blind_review_pending"
    results["room_state"][room] = {
        "status": record["status"],
        "champion_id": record["champion_id"],
        "score": record["champion_score"],
    }
    for path in files:
        data = path.read_bytes()
        body = data.decode("utf-8")
        first = body.splitlines()[0]
        assert first.startswith("# ") and re.search(r"\bCandidate " + path.stem + r"\b", first)
        assert "**Round 002 / per Triplex unit; two units.**" in body
        assert "| Actual surface" in body or "| Surface" in body
        assert body.count("|---") >= 1
        role_terms = (
            "independent challenger", "v4 source scheme",
            "incumbent", "replacement test",
            "instead of the scheduled", "remove unapproved"
        )
        assert not any(term in body.casefold() for term in role_terms), str(path)
        links = []
        for match in re.finditer(r"\]\(([^)]+)\)", body):
            url = match.group(1).split("#", 1)[0]
            if not url or url.startswith(("https://", "http://", "mailto:")):
                continue
            target = (path.parent / url).resolve()
            links.append(url)
            if not target.exists():
                results["broken_relative_links"].append({"path": str(path.relative_to(ROOT)), "link": url})
        results["candidate_files"][str(path.relative_to(ROOT)).replace("\\", "/")] = {
            "letter": path.stem,
            "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
            "relative_links": len(links),
            "surface_rows": sum(1 for line in body.splitlines() if line.startswith("|")),
        }

for room in ("PH-BATH3", "PH-BATH4", "PH-POWDER"):
    base = ROOT / "rooms" / room / "board" / "round-001"
    completed = [seat for seat in SEATS if (base / ("critic-" + seat + ".md")).exists()]
    assert len(completed) == 4
    results["round1_critics"][room] = completed
assert not results["broken_relative_links"]
assert len(results["candidate_files"]) == 6
results["status"] = "PASS"
out = ROOT / "state" / "ROUND002_PREFLIGHT.json"
out.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
print("PASS six blind candidates; 3 active rooms, all Round001 critiques, relative links")
for name, item in results["candidate_files"].items():
    print(name, "bytes", item["bytes"], "sha256", item["sha256"][:12])
print("receipt", out.relative_to(ROOT))
