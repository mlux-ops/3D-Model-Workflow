"""Read-only candidate freeze QA; does not open private role keys."""
from pathlib import Path
import hashlib
import json
import re

root = Path(__file__).resolve().parents[1]
receipt = json.loads((root / "state/ROUND011_SUBMISSION.json").read_text(encoding="utf-8"))
rooms = json.loads((root / "state/ROOMS.json").read_text(encoding="utf-8"))["rooms"]
intro = "This specification is a design option for independent evaluation; model geometry, manufacturer compliance, procurement terms and owner approval must be verified."
assert receipt["phase"] == "2-board" and receipt["all_critic_scores"] is None
assert receipt["new_board_dispatch_status"].startswith("NOT DISPATCHED")
assert set(receipt["candidate_files"]) == {"PH-BATH3", "TX-BATH3"}
count = 0
links = 0
for rid, specs in receipt["candidate_files"].items():
    room = next(x for x in rooms if x["id"] == rid)
    assert room["status"] == "blocked" and room["champion_id"] is None
    assert room["round_011_submission"]["scores"] is None
    folder = root / "rooms" / rid / "board/round-011"
    assert not list(folder.glob("critic-*.md"))
    assert len(list(folder.glob("_key.json"))) == 1
    assert {x.stem for x in (folder / "candidates").glob("*.md")} == set(specs)
    for letter, data in specs.items():
        f = folder / "candidates" / (letter + ".md")
        raw = f.read_bytes()
        doc = raw.decode("utf-8")
        lines = doc.splitlines()
        assert data["bytes"] == len(raw) and data["sha256"] == hashlib.sha256(raw).hexdigest()
        assert lines[0] == f"# {rid} — Candidate {letter} — complete tile design option"
        assert lines[1] == "" and lines[2] == intro
        assert not re.search(r"(?i)\bincumbent\b|\bchallenger\b|\bchampion\b|_key\.json|state/ROOMS\.json|state/LEDGER\.md|\bsteam\b|Round00[124] lessons", doc)
        assert "15%" in doc and "DCOF" in doc and "WALK-IN" in doc and "TUB" in doc
        assert sum(len(x.strip("|").split("|")) == 5 for x in lines if x.startswith("|")) >= 5
        for row in room["carried_tile_rows"]:
            assert row["smartsheet_row_id"] in doc
        for link in re.findall(r"\]\(([^)]+)\)", doc):
            if link.startswith(("https://", "http://", "#", "mailto:")):
                continue
            assert (f.parent / link.split("#")[0]).exists(), (rid, letter, link)
            links += 1
        if rid == "PH-BATH3":
            assert "DT062412" in doc and "UNSELECTED" in doc
        else:
            assert "BT062415-BNX" in doc and "Black Onyx" in doc
        count += 1
print(f"PASS R011 {count} SHA/byte frozen neutral packets, {links} resolved local links, 2 blocked rooms, scores null; reviewer preflight pending, no specialist dispatch")
