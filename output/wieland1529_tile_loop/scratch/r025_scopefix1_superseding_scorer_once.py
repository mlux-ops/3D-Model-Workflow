"""One-time R025 corrective scorer, retaining immutable first-pass originals.

Requires six fresh independent room-only MARKET/DESIGN critiques in scopefix1
files; combines original BUILD25/COST26, validates independent evidence/links,
signs an additive superseding NON-CHAMPION receipt and 5-section review report.
"""
from __future__ import annotations

import contextlib
import hashlib
import io
import json
import re
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

import r025_four_seat_readonly_audit as baseline

ROOT = Path(__file__).resolve().parents[1]
ROOMS = ("PH-PRIMARY", "PH-BATH3", "PH-BATH4")
ROLE = {
    "market": ("worker-28", Decimal("0.30"), 4, "critic-market-scopefix1.md"),
    "design": ("worker-29", Decimal("0.25"), 5, "critic-design-scopefix1.md"),
    "build": ("worker-25", Decimal("0.25"), 5, "critic-build.md"),
    "cost": ("worker-26", Decimal("0.20"), 5, "critic-cost.md"),
}
RECEIPT = "state/ROUND025_SCOPEFIX1_AUTHENTIC_FOUR_SEAT_SCORED_NO_CHAMPIONS.json"
REPORT = "state/ROUND025_SCOPEFIX1_FIVE_SECTION_INDEPENDENT_REVIEWER_REPORT.md"


def fp(path):
    raw = path.read_bytes()
    return {"sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)}


def one_decimal(vals):
    return (sum((Decimal(str(v)) for v in vals), Decimal(0)) / Decimal(len(vals))).quantize(Decimal(".1"), rounding=ROUND_HALF_UP)


def check_room_scope(path, room):
    content = path.read_text(encoding="utf-8")
    # Strictly prohibit other room candidate or plumbing links and any known
    # confidential room or state files in corrected critiques.
    errors = []
    refs = re.findall(r"\]\(([^)]+)\)", content)
    for url in refs:
        if url.startswith(("http://", "https://", "#")):
            continue
        file = (path.parent / url.split("#")[0]).resolve()
        if not file.is_file():
            errors.append("BROKEN " + url)
            continue
        if not file.is_relative_to(ROOT):
            errors.append("OUTSIDE ROOT " + url)
            continue
        rel = file.relative_to(ROOT).as_posix()
        if rel.startswith("rooms/"):
            parts = rel.split("/")
            if parts[1] != room:
                errors.append("CROSS ROOM " + rel)
            elif parts[2] == "board" and rel not in (
                 f"rooms/{room}/board/round-025/candidates/A.md",
                 f"rooms/{room}/board/round-025/candidates/B.md"):
                errors.append("BOARD PRIVATE/OLD/CRITIC " + rel)
            elif parts[2] not in ("geometry.json", "plumbing.json", "board"):
                errors.append("OUT OF ROOM ALLOWLIST " + rel)
        elif not (rel == "board/BOARD.md" or rel == "state/OWNER_FEEDBACK.md" or
                  rel.startswith("research/products/") or rel.startswith("research/comps/") or
                  rel.startswith("inputs/")):
            errors.append("OUT OF GLOBAL ALLOWLIST " + rel)
    for forbidden in ("_key.json", "champion.md", "history.md", "state/ROOMS.json", "state/LEDGER.md"):
        if forbidden in content:
            errors.append("FORBIDDEN TEXT " + forbidden)
    if re.search(r"(?i)previous critic|previous round score|worker-2[2345]|reviewer22", content):
        errors.append("PRIOR-OUTCOME / SPECIALIST LEAK")
    if errors:
        raise RuntimeError(f"{path}: " + "; ".join(errors))
    return len(refs)


def main():
    if any((ROOT / r).exists() for r in (RECEIPT, REPORT)):
        raise FileExistsError("Superseding scorer already executed; do not overwrite")
    for required in (
        "state/ROUND025_AUTHENTIC_FOUR_SEAT_COLLECTION_SCORED_NO_CHAMPIONS.json",
        "state/ROUND025_POSTSCORE_REVIEWER22_PRECISE_FIX_SOURCE_SCOPE.md",
        "state/ROUND025_FORMAL_THREE_PH_ROOMS_SOURCE_FROZEN_PREDISPATCH.json",
        "state/ROUND025_FOUR_AUTHENTIC_CRITIC_DISPATCH.json"):
        if not (ROOT / required).is_file():
            raise FileNotFoundError(required)
    original = json.loads((ROOT / "state/ROUND025_AUTHENTIC_FOUR_SEAT_COLLECTION_SCORED_NO_CHAMPIONS.json").read_text(encoding="utf-8"))
    assert original["critic_count"] == 12 and original["individual_criterion_count"] == 114
    # Re-verify all source parent, key and frozen candidate hashes before signing.
    source = json.loads((ROOT / "state/ROUND025_FORMAL_THREE_PH_ROOMS_SOURCE_FROZEN_PREDISPATCH.json").read_text(encoding="utf-8"))
    for section in ("neutral_candidates", "prime_only_private_keys", "signed_parents"):
        for rel, expected in source[section].items():
            if fp(ROOT / rel) != expected:
                raise RuntimeError("Frozen source changed: " + rel)
    # Independent original receipts are not changed; source / worker provenance is explicit.
    data = {}
    criterion_count = 0
    local_refs = 0
    for room in ROOMS:
        data[room] = {}
        for seat, (worker, weight, number, filename) in ROLE.items():
            rel = f"rooms/{room}/board/round-025/{filename}"
            file = ROOT / rel
            if not file.is_file():
                raise FileNotFoundError(rel)
            local_refs += check_room_scope(file, room) if seat in ("market", "design") else 0
            baseline.ERRORS.clear()
            scores, _, sha, size = baseline.score_one(file, room, seat, number)
            if baseline.ERRORS:
                raise RuntimeError("Critique arithmetic/source failure " + rel + ": " + repr(baseline.ERRORS))
            if set(scores) != {"A", "B"}:
                raise RuntimeError("Missing one neutral candidate score " + rel)
            criterion_count += sum(len(x["criteria"]) for x in scores.values())
            data[room][seat] = {"worker": worker, "weight": str(weight), "file": rel,
                                "sha256": sha, "bytes": size, "candidate_scores": scores}
    if criterion_count != 114:
        raise RuntimeError("114 original criterion slots must be replaced by 114 audited slots: " + str(criterion_count))
    sums = {}
    for room in ROOMS:
        sums[room] = {}
        for letter in ("A", "B"):
            seats = {seat: Decimal(str(data[room][seat]["candidate_scores"][letter]["mean"])) for seat in ROLE}
            total = sum((seats[seat] * ROLE[seat][1] for seat in ROLE), Decimal(0))
            sums[room][letter] = {"individual": {s: float(v) for s,v in seats.items()},
                                  "minimum": float(min(seats.values())),
                                  "all_seats_at_least_3": all(x >= 3 for x in seats.values()),
                                  "raw_weighted": str(total),
                                  "weighted": float(total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
                                  "hard_gates_all_pass": False,
                                  "champion_accepted": False}
    rooms_file = json.loads((ROOT / "state/ROOMS.json").read_text(encoding="utf-8"))
    for r in rooms_file["rooms"]:
        if r["id"] in ROOMS and not (r["status"] == "blocked" and r["champion_id"] is None):
            raise RuntimeError("R025 room was promoted without independent signoff")
    receipt = {
        "round": 25,
        "phase": "CORRECTIVE_CLEAN_ROOM_FOUR_SEAT_SCORED_NO_CHAMPIONS_INDEPENDENT_REVIEW_PENDING",
        "supersedes_first_pass_scope_violation_only": "state/ROUND025_AUTHENTIC_FOUR_SEAT_COLLECTION_SCORED_NO_CHAMPIONS.json",
        "first_pass_originals_unchanged": True,
        "precise_fix": "state/ROUND025_POSTSCORE_REVIEWER22_PRECISE_FIX_SOURCE_SCOPE.md",
        "source_freeze_sha": fp(ROOT / "state/ROUND025_FORMAL_THREE_PH_ROOMS_SOURCE_FROZEN_PREDISPATCH.json"),
        "original_dispatch": fp(ROOT / "state/ROUND025_FOUR_AUTHENTIC_CRITIC_DISPATCH.json"),
        "market_design_replacements": ["worker-28", "worker-29"],
        "authentic_original_build_cost": ["worker-25", "worker-26"],
        "four_seat_weights": {s: str(row[1]) for s,row in ROLE.items()},
        "source_scope": "STRICT: corrected MARKET/DESIGN reviewed only same-room geometry/plumbing/current candidate plus permitted global research/inputs/BOARD/OWNER; no other room links",
        "new_reports": data,
        "critic_files_count": 12,
        "criterion_scores_count": criterion_count,
        "weighted_results": sums,
        "native_cut_slivers_and_drain": "UNKNOWN",
        "delivered_carton_material_cost_and_room_budget": "UNKNOWN",
        "chicago_exact_lot_stock_ETA": "UNKNOWN",
        "PH_BATH3_TUB_WALKIN_and_basin": "UNSELECTED",
        "PH_BATH4_35_vs_27_SF": "UNKNOWN",
        "published_product_dcof": ">=0.42 on exact F&D LEVEL and applicable selected/conditional PAN tiles; not raw lab number",
        "no_incumbent_all_three_blocked": True,
        "plus_0_25": "N/A; no existing same-round incumbent",
        "revit_identity_1527_equals_1529": True,
        "original_historic_13_rooms_26_instances_27_rows_usd": 23572.44,
        "original_waste_once_pct": 15,
        "r026_phase": "separate frozen future TX source pending Reviewer27 pre-dispatch; no R026 critic score",
        "champion_changes": False,
        "owner_approval": False,
        "procurement_release": False,
        "independent_post_correction_reviewer": None,
        "global_DONE": False,
    }
    report_lines = [
        "# R025 source-scope FIX1 corrective scoring — independent Reviewer ROUND REPORT",
        "", "## 1. Authority and original defect",
        "Board applies four authentic blind specialists, MARKET .30/DESIGN .25/BUILD .25/COST .20; per seat >=3.0 and all hard gates PASS for champion. Reviewer22 PRECISE FIX found 21 cross-room links in original MARKET23/DESIGN24 files. Signed first-pass scores remain historical, not accepted source-compliant board verdict. Historical accounting 13 rooms, 26 units, 27 material rows, $23,572.44, original 15% waste counted once.",
        "", "## 2. Corrective independent critic provenance and hashes",
        "Fresh worker28 MARKET and worker29 DESIGN wrote six NEW source-scope-clean critiques only; original worker25 BUILD and worker26 COST remain unmodified and valid. Each of 12 active-seat reports has a distinct original SHA-256 and byte count in the additive receipt. All 114 criterion scores and 24 arithmetic half-up means rechecked, relevant evidence links resolve. The six frozen A/B files, three private mappings and four parents reverified unchanged. No other room candidate/plumbing/historical source in clean-room files.",
        "", "## 3. Reweighted results, all champion hard gates still unresolved",
    ]
    for room in ROOMS:
        a,b=sums[room]["A"],sums[room]["B"]
        report_lines.append(f"- {room}: A {a['weighted']:.2f} (min {a['minimum']:.1f}), B {b['weighted']:.2f} (min {b['minimum']:.1f}); neither accepted")
    report_lines.extend([
        "No existing incumbents in these blocked rooms; +0.25 challenger-vs-incumbent comparison is not applicable. Even if every seat >=3.0, incomplete hard gates prohibit champion promotion.",
        "", "## 4. Product, owner and hard-gate disposition",
        "Exact Elm FLAT Cortar and Tones wet WALL/NICHE (where applicable), F&D Luxe Sand 101317949/Riviera Oat 101487775 published wet >=0.42 LEVEL/PAN product listings distinguish genuine tile-use evidence from unverified native drain/door/glass/visible <3in cuts. PH-PRIMARY 48in BNX LINEAR/BR73480/solid grate/no niche/PH-WC once; ceiling separately UNKNOWN. PH-BATH4 selected BNX POINT WALK-IN, 35-vs-27 SF open. PH-BATH3 TUB vs WALK-IN and basin unselected; Delta Chrome POINT only WALK-IN. Chicago lot/ETA and complete case-rounded landed costs against owner budget remain UNKNOWN.",
        "", "## 5. Requested independent decision and next phase",
        "Inspect state/ROUND025_SCOPEFIX1_AUTHENTIC_FOUR_SEAT_SCORED_NO_CHAMPIONS.json, the six scopefix1 reports plus six valid BUILD/COST originals, Reviewer22 PRECISE FIX and immutable frozen sources; provide CONTINUE FOR R025 CORRECTIVE SCORING NONACCEPTANCE ONLY or exact PRECISE FIX. No owner approval, champion, procurement, fabricated sources or GLOBAL DONE. R026 separately frozen TX source awaits Reviewer27 preflight; no critic dispatch/score unless independently cleared."
    ])
    report = "\n".join(report_lines) + "\n"
    if report.count("## ") != 5 or len(report) >= 4000:
        raise RuntimeError("Report five-section/4k limit: " + str(len(report)))
    with (ROOT / RECEIPT).open("x", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(receipt, indent=2) + "\n")
    with (ROOT / REPORT).open("x", encoding="utf-8", newline="\n") as f:
        f.write(report)
    print("R025 FIX1 12/12 eligible reports 114 criteria; 24 means; corrected 6 weighted A/B; NO CHAMPIONS")
    print("R025 FIX1 SCORE", fp(ROOT/RECEIPT), "REPORT", len(report), "chars")
    print(json.dumps(sums, indent=2))


if __name__ == "__main__":
    main()
