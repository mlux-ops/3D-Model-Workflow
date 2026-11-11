"""Strict R026 collection audit. Never changes signed source or original critiques."""
from __future__ import annotations

import hashlib
import json
import re
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROOMS = ("TX-PRIMARY", "TX-BATH3")
SEATS = {
    "market": ("worker-31", Decimal("0.30"), 4),
    "design": ("worker-32", Decimal("0.25"), 5),
    "build": ("worker-33", Decimal("0.25"), 5),
    "cost": ("worker-34", Decimal("0.20"), 5),
}
ERRORS: list[str] = []


def check(value: bool, reason: str) -> None:
    if not value:
        ERRORS.append(reason)


def fp(path: Path) -> dict[str, object]:
    raw = path.read_bytes()
    return {"sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)}


def signed_block(receipt: dict, name: str) -> int:
    block = receipt.get(name)
    check(isinstance(block, dict), "missing signed block " + name)
    count = 0
    for rel, sig in (block or {}).items():
        path = ROOT / rel
        check(path.is_file(), "missing signed file " + rel)
        if path.is_file():
            check(fp(path) == sig, "SHA/BYTES mismatch " + rel)
            count += 1
    return count


def verify_links(source: str, file: Path, room: str) -> int:
    count = 0
    for match in re.finditer(r"\]\(([^)]+)\)", source):
        raw = match.group(1)
        if raw.startswith(("http://", "https://", "#", "mailto:")):
            continue
        target = (file.parent / raw.split("#", 1)[0]).resolve()
        if not target.is_file():
            ERRORS.append(f"Broken linked file {file}: {raw}")
            continue
        if not target.is_relative_to(ROOT):
            ERRORS.append(f"Out of project {file}: {raw}")
            continue
        rel = target.relative_to(ROOT).as_posix()
        if rel.startswith("rooms/"):
            check(rel.split("/")[1] == room, f"Cross-room source {file}: {rel}")
            if rel.split("/")[1] == room:
                check(rel in (
                    f"rooms/{room}/geometry.json",
                    f"rooms/{room}/plumbing.json",
                    f"rooms/{room}/board/round-026/candidates/A.md",
                    f"rooms/{room}/board/round-026/candidates/B.md",
                ), f"Forbidden room source {file}: {rel}")
        else:
            check(rel in ("board/BOARD.md", "state/OWNER_FEEDBACK.md")
                  or rel.startswith(("research/products/", "research/comps/", "inputs/")),
                  f"Forbidden global source {file}: {rel}")
        count += 1
    check(not re.search(r"(?i)_key\.json|/champion\.md|/history\.md|state/ROOMS\.json|state/LEDGER\.md", source),
          f"Forbidden text token in critic {file}")
    return count


def one_decimal(nums: list[int]) -> Decimal:
    return (sum(map(Decimal, nums)) / Decimal(len(nums))).quantize(
        Decimal(".1"), rounding=ROUND_HALF_UP)


def parse_critic(path: Path, room: str, seat: str, n: int) -> dict:
    source = path.read_text(encoding="utf-8")
    headings = list(re.finditer(
        r"(?im)^##\s*(?:(?:neutral\s+)?(?:candidate|option)\s+)?([AB])(?:\b|\s*[-–—])[^\n]*",
        source))
    check(len(headings) == 2 and {x.group(1).upper() for x in headings} == {"A", "B"},
          "A/B headings " + str(path) + " " + repr([m.group(0) for m in headings]))
    res: dict[str, dict] = {}
    for i, heading in enumerate(headings):
        letter = heading.group(1).upper()
        rest = source[heading.end(): (headings[i+1].start() if i+1 < len(headings) else len(source))]
        # Scores only from first Markdown criterion table in this candidate section.
        tables = re.findall(r"(?ms)(?:^\|[^\n]*\|\n){2,}", rest)
        scorelists = []
        for table in tables:
            rows = [int(x) for x in re.findall(
                r"(?m)^\|[^|\n]+\|\s*\*{0,2}([1-5])(?:/5)?\*{0,2}\s*\|", table)]
            if rows:
                scorelists.append(rows)
        vals = scorelists[0] if scorelists else []
        check(len(vals) == n and len(scorelists) == 1, f"criterion count/extra tables {path} {letter} {scorelists}")
        if len(vals) != n:
            continue
        calc = one_decimal(vals)
        all_lines = [ln for ln in rest.splitlines() if not ln.lstrip().startswith("|")]
        score_lines = [ln for ln in all_lines
                       if re.search(r"(?i)seat[_ ]?mean|seat[_ ]?score|arithmetic mean|overall[_ ]?seat|score(?:\s+of)?\s*[AB]?", ln)]
        check(any(re.search(r"(?<!\d)" + re.escape(str(calc)) + r"\s*(?:/|\b)", ln) for ln in score_lines),
              f"reported mean mismatch {path} {letter}: {calc}")
        check(re.search(r"(?i)top_fix", rest) is not None, f"top_fix missing {path} {letter}")
        check(re.search(r"(?i)confidence", rest) is not None
              or re.search(r"(?i)confidence", source) is not None, f"confidence missing {path} {letter}")
        res[letter] = {"criteria": vals, "mean": float(calc)}
    check("gate_flags" in source.lower() or "hard-gate flags" in source.lower(), "No gate flags " + str(path))
    for gate in ("WALL", "NICHE", "LEVEL", "PAN", "BUDGET", "GEOMETRY"):
        check(re.search(r"\b" + gate + r"\b", source, re.I) is not None, f"missing gate {gate} {path}")
    if room == "TX-PRIMARY":
        check("BR73480" in source and "LINEAR" in source and "NICHE" in source, "Primary fixture missing " + str(path))
    else:
        check("TUB" in source and "WALK-IN" in source and "POINT" in source, "Bath3 branch missing " + str(path))
    return {"file": path.relative_to(ROOT).as_posix(), "fingerprint": fp(path),
            "local_links": verify_links(source, path, room), "candidates": res}


def main() -> None:
    frozen = json.loads((ROOT/"state/ROUND026_FORMAL_TWO_TX_ROOMS_SOURCE_FROZEN_PREDISPATCH.json").read_text(encoding="utf-8"))
    prepared = json.loads((ROOT/"state/ROUND026_TX_FOUR_SCHEMES_TWO_OWNER_CARDS_SIGNED.json").read_text(encoding="utf-8"))
    cleared = json.loads((ROOT/"state/ROUND026_INDEPENDENT_PREDISPATCH_REVIEWER27_CLEARANCE.json").read_text(encoding="utf-8"))
    dispatch = json.loads((ROOT/"state/ROUND026_FOUR_FRESH_AUTHENTIC_CRITIC_DISPATCH.json").read_text(encoding="utf-8"))
    check(cleared["authentic_verdict"] == "CONTINUE FOR R026 BLIND CRITIC DISPATCH ONLY", "Not preflight-cleared")
    check(dispatch["round"] == 26 and dispatch["focus_rooms"] == list(ROOMS), "Dispatch identity")
    check(dispatch["score_in_this_dispatch_phase"] is False, "Dispatch prematurely scored")
    counts = {x: signed_block(frozen, x) for x in
              ("neutral_candidates", "prime_only_private_keys", "signed_parents")}
    counts["prepared_files"] = signed_block(prepared, "files")
    counts["prepared_parents"] = signed_block(prepared, "parents")
    check(counts == {"neutral_candidates":4, "prime_only_private_keys":2, "signed_parents":4,
                     "prepared_files":7,"prepared_parents":3}, "Source/parent count incorrect " + str(counts))
    for seat, (worker, weight, _) in SEATS.items():
        sd = dispatch["seats"]["critic-" + seat]
        check(sd["worker"] == worker and Decimal(str(sd["weight"])) == weight,
              "Worker provenance " + seat)
    state = json.loads((ROOT/"state/ROOMS.json").read_text(encoding="utf-8"))
    rows = state["rooms"]
    material = sum((Decimal(str(r["carried_quote_material_subtotal_usd_per_unit"])) * r["unit_count"]
                    for r in rows), Decimal(0))
    baseline = {"room_count":len(rows), "physical_instances":sum(r["unit_count"] for r in rows),
                "original_material_rows":sum(len(r["carried_tile_rows"]) for r in rows),
                "material_usd":str(material)}
    check(baseline == {"room_count":13,"physical_instances":26,"original_material_rows":27,
                       "material_usd":"23572.44"}, "Historic accounting changed " + str(baseline))
    from collections import Counter
    statuses = dict(Counter(r["status"] for r in rows))
    check(statuses == {"blocked":8,"active":3,"seeded":2}, "Room state changed "+str(statuses))
    for row in rows:
        if row["id"] in ROOMS:
            check(row["status"] == "blocked" and row["champion_id"] is None, "Premature champion "+row["id"])
    reports = {}
    totals = {}
    count_crit = 0
    for room in ROOMS:
        reports[room] = {}
        for seat, (_, _, expected) in SEATS.items():
            path = ROOT / f"rooms/{room}/board/round-026/critic-{seat}.md"
            check(path.is_file(), "Missing critic " + str(path))
            if path.is_file():
                reports[room][seat] = parse_critic(path, room, seat, expected)
                count_crit += len(reports[room][seat]["candidates"])
        totals[room] = {}
        for letter in ("A", "B"):
            if all(letter in reports[room].get(seat, {}).get("candidates", {}) for seat in SEATS):
                vals = {seat:Decimal(str(reports[room][seat]["candidates"][letter]["mean"])) for seat in SEATS}
                w = sum((vals[seat]*SEATS[seat][1] for seat in SEATS), Decimal(0))
                totals[room][letter] = {"seat_means":{seat:float(x) for seat,x in vals.items()},
                                        "weighted":float(w.quantize(Decimal(".01"),rounding=ROUND_HALF_UP)),
                                        "raw_weighted":str(w),"minimum":float(min(vals.values())),
                                        "four_seats_minimum_3":min(vals.values()) >= 3,
                                        "all_hard_gates_pass":False,
                                        "champion_accepted":False}
    criteria = sum(len(rpt["candidates"][letter]["criteria"]) for rs in reports.values() for rpt in rs.values()
                   for letter in rpt["candidates"])
    check(criteria == 76 and count_crit == 16, "Expected 76/16 scored values: "+repr((criteria,count_crit)))
    result={"round":26,"phase":"DISTINCT_POSTDISPATCH_COLLECTION_AUDIT_READ_ONLY","signed_counts":counts,
            "baseline":baseline,"status_counts":statuses,"authentic_critic_files":8,
            "candidate_seat_means":count_crit,"criterion_values":criteria,
            "workers":{seat:worker for seat,(worker,_,_) in SEATS.items()},
            "weights":{seat:float(weight) for seat,(_,weight,_) in SEATS.items()},
            "critic_fingerprints_and_scores":reports,"weighted":totals,"errors":ERRORS,
            "gate_explanation":"No champion regardless of weighted score; both TX Primary COST means <3, TX Bath3 A COST <3, all native geometry/cost/Chicago exact lot unresolved; TX3 owner tub vs walk-in unselected.",
            "owner_release":False,"global_DONE":False}
    print(json.dumps(result, indent=2))
    raise SystemExit(1 if ERRORS else 0)


if __name__ == "__main__":
    main()
