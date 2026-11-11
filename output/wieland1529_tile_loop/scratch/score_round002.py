"""Audit Round002 four-seat critiques, compute weighted gates, no assumptions."""
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]
ROOMS = ("TX-BATH2", "TX-BATH3", "TX-BATH4")
SEATS = {"market": .30, "design": .25, "build": .25, "cost": .20}
state = json.loads((ROOT / "state/ROOMS.json").read_text(encoding="utf-8"))
previous = json.loads((ROOT / "state/ROUND002_PREFLIGHT.json").read_text(encoding="utf-8"))
results = {}
for room in ROOMS:
    folder = ROOT / "rooms" / room / "board/round-002"
    key = json.loads((folder / "_key.json").read_text(encoding="utf-8"))
    letters = [x for x in key if x in ("A", "B", "C")]
    assert len(letters) == 2 and set(letters) == set(x.stem for x in (folder / "candidates").glob("*.md"))
    seatdata = {}
    for seat in SEATS:
        source = folder / ("critic-" + seat + ".md")
        text = source.read_text(encoding="utf-8")
        assert "top_fix" in text and "gate_flags" in text and "confidence" in text.lower(), (room, seat)
        split = re.split(r"(?m)^## Candidate ([ABC])\b", text)
        assert len(split) == 5, (room, seat, len(split))
        byletter = {}
        for letter, part in zip(split[1::2], split[2::2]):
            if seat == "market":
                matches = re.findall(r"(?i)Overall market seat score:\s*([1-5]\.[0-9])", part)
            elif seat == "design":
                matches = re.findall(r"(?i)overall_score:\s*([1-5]\.[0-9])", part)
            else:
                matches = re.findall(r"(?i)seat_score:\s*([1-5]\.[0-9])|seat score:\s*\*\*([1-5]\.[0-9])", part)
                matches = [a or b for a, b in matches]
                if not matches and seat == "build":
                    matches = re.findall(r"(?i)seat score:\s*\*\*([1-5]\.[0-9])", text.split("## Candidate "+letter, 1)[1].split("## Candidate ",1)[0])
            assert len(matches) == 1, (room, seat, letter, matches)
            assert "FAIL" in part and "DCOF" in part, (room, seat, letter)
            byletter[letter] = float(matches[0])
        assert set(byletter) == set(letters)
        seatdata[seat] = byletter
    perletter = {}
    for letter in letters:
        cand = folder / "candidates" / (letter + ".md")
        rel = str(cand.relative_to(ROOT)).replace("\\", "/")
        assert hashlib.sha256(cand.read_bytes()).hexdigest() == previous["candidate_files"][rel]["sha256"]
        votes = {seat: seatdata[seat][letter] for seat in SEATS}
        total = round(sum(votes[s] * w for s, w in SEATS.items()), 3)
        reasons = ["Exact measured wet DCOF >=0.42 absent for bathroom floor"]
        if room == "TX-BATH3":
            reasons.append("Tub/walk-in shower scope unresolved; pan area and drain geometry missing")
        if room == "TX-BATH4" and key[letter] == "governing v4 incumbent":
            reasons.append("Clara Caviar tub niche lacks manufacturer Wet Areas listing")
            reasons.append("Bone Ribbed relief not approved for wet tub walls")
        perletter[letter] = {
            "role": key[letter],
            "seat_scores": votes,
            "weighted_score": total,
            "minimum_critic_score": min(votes.values()),
            "passes_all_gates": False,
            "reasons": reasons,
        }
    incumbent_letter = next(k for k in letters if "incumbent" in key[k])
    challenger_letter = next(k for k in letters if k != incumbent_letter)
    margin = round(perletter[challenger_letter]["weighted_score"] - perletter[incumbent_letter]["weighted_score"], 3)
    results[room] = {
        "round": 2,
        "review_complete": True,
        "seat_weights": SEATS,
        "candidates": perletter,
        "incumbent_letter": incumbent_letter,
        "challenger_letter": challenger_letter,
        "challenger_margin": margin,
        "accepted": False,
        "decision": "both_failed_hard_floor_gate_no_champion",
        "provisional_design_preference": max(letters, key=lambda x: perletter[x]["weighted_score"]),
        "score_gate_failure": (perletter[challenger_letter]["minimum_critic_score"] < 3),
    }
    print(room, "incumbent",incumbent_letter,perletter[incumbent_letter]["weighted_score"],
          "challenger",challenger_letter,perletter[challenger_letter]["weighted_score"],
          "margin",margin,"candidate_min",perletter[challenger_letter]["minimum_critic_score"])
out = ROOT / "state/ROUND002_SCORING.json"
out.write_text(json.dumps({"schema":1,"as_of":"2026-11-06","room_results":results}, indent=2) + "\n", encoding="utf-8")
print("PASS", out)
