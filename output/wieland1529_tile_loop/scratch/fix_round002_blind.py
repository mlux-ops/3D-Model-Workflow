"""Neutralize and relabel round 002 candidates after randomizing their roles."""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
spec = {
    "TX-BATH2": {"C": "incumbent", "B": "challenger"},
    "TX-BATH3": {"A": "incumbent", "B": "challenger"},
    "TX-BATH4": {"B": "incumbent", "A": "challenger"},
}
for room, mapping in spec.items():
    d = ROOT / "rooms" / room / "board" / "round-002"
    assert set(p.stem for p in (d / "candidates").glob("*.md")) == set(mapping), room
    for letter, role in mapping.items():
        path = d / "candidates" / (letter + ".md")
        body = path.read_text(encoding="utf-8")
        body = re.sub(r"(?m)^# (.*?Candidate )([ABC])(?=\b)", lambda m: m.group(1) + letter, body, count=1)
        body = body.replace("## Full tile specification (v4 source scheme)", "## Tile specification")
        body = body.replace("Round 002 / independent challenger / per Triplex unit", "Round 002 / per Triplex unit")
        body = body.replace("manufacturer Wet Areas listing reported yes in project audit. Existing recessed niche", "manufacturer Wet Areas listing reported yes in project audit. Recessed niche")
        body = body.replace("Existing bath fixture list", "Bath fixture list")
        body = body.replace("while v4 calls a tub alcove", "while the tile takeoff calls a tub alcove")
        body = body.replace("Existing bid quantities", "Carried quantities")
        body = body.replace("Prior verified owner correction:", "Owner-confirmed scope:")
        body = body.replace("originally quoted Copper tub surround", "quoted Copper tub surround")
        body = body.replace("different* 12x24", "12x24")
        path.write_text(body, encoding="utf-8")
    key = {"round": 2, "room_id": room, "blind_review": True,
           "not_for_critics": True,
           **{k: ("governing v4 incumbent" if v == "incumbent" else "revised candidate") for k, v in mapping.items()}}
    (d / "_key.json").write_text(json.dumps(key, indent=2) + "\n", encoding="utf-8")
    for letter in mapping:
        first = (d / "candidates" / (letter + ".md")).read_text(encoding="utf-8").splitlines()[0]
        assert re.search(r"Candidate\s+" + letter + r"\b", first), (room, letter, first)
        print(room, letter, "header_pass")
