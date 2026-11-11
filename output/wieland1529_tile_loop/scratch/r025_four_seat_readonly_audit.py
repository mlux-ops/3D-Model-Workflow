"""Read-only audit of authentic R025 four-seat PH critiques and frozen source.

Do not replace, edit, or regenerate critic or signed-predecessor files.
"""
from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROOMS = ("PH-PRIMARY", "PH-BATH3", "PH-BATH4")
SEATS = {"market": ("worker-23", Decimal("0.30"), 4),
         "design": ("worker-24", Decimal("0.25"), 5),
         "build": ("worker-25", Decimal("0.25"), 5),
         "cost": ("worker-26", Decimal("0.20"), 5)}
ERRORS = []


def check(test, why):
    if not test:
        ERRORS.append(why)


def sha_file(relative, signature):
    path = ROOT / relative
    if not path.is_file():
        ERRORS.append("MISSING " + relative)
        return False
    raw = path.read_bytes()
    ok = hashlib.sha256(raw).hexdigest() == signature["sha256"] and len(raw) == signature["bytes"]
    check(ok, "SHA/BYTES " + relative)
    return ok


def audit_signed(file, sections):
    receipt = json.loads((ROOT / file).read_text(encoding="utf-8"))
    checked = 0
    for section in sections:
        block = receipt.get(section)
        check(isinstance(block, dict), "SIGNED BLOCK " + file + ":" + section)
        for rel, sig in (block or {}).items():
            if not isinstance(sig, dict) or "sha256" not in sig or "bytes" not in sig:
                ERRORS.append("MALFORMED ENTRY " + file + ":" + rel)
                continue
            sha_file(rel, sig)
            checked += 1
    return checked


def one_decimal(values):
    return (sum((Decimal(v) for v in values), Decimal(0)) / Decimal(len(values))).quantize(
        Decimal("0.1"), rounding=ROUND_HALF_UP)


def score_one(file, room, seat, expected_n):
    source = file.read_text(encoding="utf-8")
    sections = list(re.finditer(r"(?im)^##\s*(?:neutral\s+)?(?:candidate|option)\s+([AB])\b[^\n]*", source))
    check(len(sections) == 2 and {m.group(1).upper() for m in sections} == {"A", "B"},
          "CANDIDATE HEADINGS " + str(file))
    result = {}
    for index, match in enumerate(sections):
        letter = match.group(1).upper()
        end = sections[index + 1].start() if index + 1 < len(sections) else len(source)
        part = source[match.end():end]
        criterion = [int(n) for n in re.findall(
            r"(?m)^\|[^|\n]+\|\s*\*{0,2}([1-5])(?:/5)?\*{0,2}\s*\|", part)]
        check(len(criterion) == expected_n, "CRITERION COUNT " + str(file) + ":" + letter + " " + repr(criterion))
        if len(criterion) != expected_n:
            continue
        mean = one_decimal(criterion)
        report_lines = [ln for ln in part.splitlines() if not ln.startswith("|") and
                        re.search(r"(?i)(overall_seat_score|arithmetic mean|seat score|seat mean|mean|score\s+[AB])", ln)]
        documented = any(re.search(r"(?<!\d)" + re.escape(str(mean)) + r"(?:/5|\b)", ln)
                         for ln in report_lines)
        check(documented, "MEAN DOCUMENTATION " + str(file) + ":" + letter + " " + str(mean))
        check(bool(re.search(r"(?i)top_fix", part)), "TOP_FIX " + str(file) + ":" + letter)
        check(bool(re.search(r"(?i)confidence", part)) or seat == "cost",
              "CONFIDENCE " + str(file) + ":" + letter)
        result[letter] = {"criteria": criterion, "mean": float(mean)}
    # All source links in every original report must resolve; URLs are retained as written.
    urls = re.findall(r"\]\(([^)]+)\)", source)
    refs = 0
    for url in urls:
        if url.startswith(("https://", "http://", "mailto:", "#")):
            continue
        target = (file.parent / url.split("#", 1)[0].replace("%20", " ")).resolve()
        check(target.is_file(), "BROKEN LOCAL LINK " + str(file) + " => " + url)
        rel = target.relative_to(ROOT).as_posix() if target.is_relative_to(ROOT) else "OUTSIDE_ROOT"
        check(rel != "OUTSIDE_ROOT", "LINK OUTSIDE ROOT " + str(file) + " => " + url)
        if rel != "OUTSIDE_ROOT":
            check(not any(part in rel for part in ("/_key.json", "/champion.md", "/history.md",
                                               "state/ROOMS.json", "state/LEDGER.md")),
                  "PRIVATE LINK " + str(file) + " => " + rel)
            check(not ("/board/round-" in rel and "/board/round-025/" not in rel),
                  "OLDER BOARD LINK " + str(file) + " => " + rel)
            if rel.startswith("rooms/"):
                check(rel.split("/")[1] in ROOMS, "UNASSIGNED ROOM LINK " + str(file) + " => " + rel)
        refs += 1
    check(len(re.findall(r"(?i)gate_flags", source)) >= 1, "MISSING GATES " + str(file))
    for gate in ("WALL", "NICHE", "LEVEL", "PAN", "BUDGET", "GEOMETRY"):
        check(re.search(r"(?i)\b" + gate + r"\b", source) is not None,
              "MISSING GATE " + str(file) + " " + gate)
    check(not re.search(r"(?i)state/(?:ROOMS\.json|LEDGER\.md)|_key\.json|/champion\.md|/history\.md", source),
          "FORBIDDEN CONTENT REFERENCE " + str(file))
    return result, refs, hashlib.sha256(file.read_bytes()).hexdigest(), file.stat().st_size


def main():
    signed = {
        "r025_frozen": audit_signed("state/ROUND025_FORMAL_THREE_PH_ROOMS_SOURCE_FROZEN_PREDISPATCH.json",
                                    ("neutral_candidates", "prime_only_private_keys", "signed_parents")),
        "r025_prepared": audit_signed("state/ROUND025_PH_THREE_ROOM_PREPARED_NOT_SUBMITTED.json", ("files",)),
    }
    dispatch = json.loads((ROOT / "state/ROUND025_FOUR_AUTHENTIC_CRITIC_DISPATCH.json").read_text(encoding="utf-8"))
    check(dispatch["round"] == 25 and dispatch["focus_rooms"] == list(ROOMS), "DISPATCH ROUND/ROOMS")
    check(dispatch["score_in_this_dispatch_phase"] is False, "PREMATURE DISPATCH SCORING")
    for seat, (worker, weight, _) in SEATS.items():
        info = dispatch["seats"]["critic-" + seat]
        check(info["worker"] == worker and Decimal(str(info["weight"])) == weight,
              "SEAT DISPATCH " + seat)
    rootrooms = json.loads((ROOT / "state/ROOMS.json").read_text(encoding="utf-8"))
    rows = rootrooms["rooms"]
    statuses = dict(Counter(r["status"] for r in rows))
    original_count = sum(len(r["carried_tile_rows"]) for r in rows)
    physical = sum(r["unit_count"] for r in rows)
    total = sum((Decimal(str(r["carried_quote_material_subtotal_usd_per_unit"])) * r["unit_count"]
                 for r in rows), Decimal(0))
    check((len(rows), physical, original_count, total) == (13, 26, 27, Decimal("23572.44")),
          "HISTORIC BASELINE " + repr((len(rows), physical, original_count, str(total))))
    check(statuses == {"blocked": 8, "active": 3, "seeded": 2}, "ROOM STATUS " + repr(statuses))
    for r in rows:
        if r["id"] in ROOMS:
            check(r["status"] == "blocked" and r["champion_id"] is None and r["champion_score"] is None,
                  "PREMATURE CHAMPION " + r["id"])
    collected = {}
    for room in ROOMS:
        collected[room] = {}
        for seat, (worker, weight, count) in SEATS.items():
            rel = "rooms/" + room + "/board/round-025/critic-" + seat + ".md"
            file = ROOT / rel
            check(file.is_file(), "MISSING CRITIQUE " + rel)
            if not file.is_file():
                continue
            result, links, sha, size = score_one(file, room, seat, count)
            collected[room][seat] = {"worker": worker, "weight": float(weight), "candidates": result,
                                     "file": rel, "sha256": sha, "bytes": size, "local_links": links}
    weighted = {}
    for room in ROOMS:
        weighted[room] = {}
        for letter in ("A", "B"):
            if all(letter in collected[room].get(s, {}).get("candidates", {}) for s in SEATS):
                vals = {s: collected[room][s]["candidates"][letter]["mean"] for s in SEATS}
                raw = sum((Decimal(str(vals[s])) * SEATS[s][1] for s in SEATS), Decimal(0))
                weighted[room][letter] = {"seats": vals,
                                           "minimum": min(vals.values()),
                                           "all_four_minimum_3": min(vals.values()) >= 3,
                                           "weighted": float(raw.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
                                           "raw_weighted": str(raw),
                                           "hard_gates_all_pass": False,
                                           "decision": "BLOCKED_OPEN_MANDATORY_GATES_NOT_CHAMPION"}
    result = {"round": 25, "phase": "COLLECTION_AUDIT_READ_ONLY", "signed_checks": signed,
              "statuses": statuses, "baseline": {"rooms": len(rows), "instances": physical,
              "material_rows": original_count, "historic_four_unit_usd": str(total)},
              "weights": {s: float(w) for s, (_, w, _) in SEATS.items()},
              "critic_files": sum(len(v) for v in collected.values()),
              "criterion_values": sum(len(collected[r][s]["candidates"][letter]["criteria"])
                                      for r in collected for s in collected[r]
                                      for letter in collected[r][s]["candidates"]),
              "critics": collected, "scores": weighted, "errors": ERRORS,
              "source_access_note": "File contents/links audited; undisclosed browser reads cannot be independently proven",
              "acceptance_note": "No champion: native cut geometry, delivered/cartoned cost and Chicago lot/ETA unknown; PH-BATH3 owner program/basin unresolved; conditional PAN only if WALK-IN."}
    print(json.dumps(result, indent=2))
    raise SystemExit(1 if ERRORS else 0)


if __name__ == "__main__":
    main()
