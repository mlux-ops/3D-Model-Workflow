"""One-time append-only status narrative for R025 scoring and R026 source freeze.

Separate R025 score acceptance review and R026 pre-dispatch preflight are pending;
these lines never assert either independent decision already exists.
"""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "state/LEDGER.md"
SCORE_FILE = ROOT / "state/ROUND025_AUTHENTIC_FOUR_SEAT_COLLECTION_SCORED_NO_CHAMPIONS.json"
FROZEN_FILE = ROOT / "state/ROUND026_FORMAL_TWO_TX_ROOMS_SOURCE_FROZEN_PREDISPATCH.json"


def append(path, text, unique):
    existing = path.read_text(encoding="utf-8")
    if unique in existing:
        raise RuntimeError("Append already recorded: " + unique)
    with path.open("a", encoding="utf-8", newline="\n") as out:
        out.write(("" if existing.endswith("\n") else "\n") + text)


def main():
    s = json.loads(SCORE_FILE.read_text(encoding="utf-8"))
    f = json.loads(FROZEN_FILE.read_text(encoding="utf-8"))
    if len(s["original_critic_reports"]) != 3 or s["critic_count"] != 12 or s["individual_criterion_count"] != 114:
        raise RuntimeError("R025 score certificate incomplete")
    if s["independent_postscore_reviewer"] is not None or s["global_DONE"] is not False:
        raise RuntimeError("R025 clearance unexpectedly changed")
    if len(f["neutral_candidates"]) != 4 or len(f["prime_only_private_keys"]) != 2 or f["pre_dispatch_independent_verdict"] is not None:
        raise RuntimeError("R026 freeze/independent stage changed")
    scores = s["candidate_scores"]
    primary, bath3, bath4 = (scores[k] for k in ("PH-PRIMARY", "PH-BATH3", "PH-BATH4"))
    assert [primary["A"]["weighted"],primary["B"]["weighted"],bath3["A"]["weighted"],bath3["B"]["weighted"],bath4["A"]["weighted"],bath4["B"]["weighted"]] == [4.01,4.07,3.82,3.72,3.85,3.63]
    history = {
      "PH-PRIMARY": ("B 4.07, A 4.01", "B is provisionally higher by 0.06 but neither A nor B is a champion: full delivered cost, Chicago lot, native 48in LINEAR pan/door/glass cuts and separate shower ceiling permission not verified. Selected Brizo BT0734816-BNX/BR73480, solid BNX grate, no niches, inherited PH-WC retained."),
      "PH-BATH3": ("A 3.82, B 3.72", "A provisionally higher by 0.10; TUB/WALK-IN and basin owner UNSELECTED. Delta DT062412 Chrome POINT PAN only if WALK-IN, no tiled PAN with tub. Chicago lot, budget and native geometry unknown, so no champion."),
      "PH-BATH4": ("A 3.85, B 3.63", "A provisionally higher by 0.22; selected WALK-IN Brizo BT062415-BNX POINT retained, independent four-plane PAN. Owner 35 SF versus older 27 SF and true cut geometry, delivered pricing and lot unknown, so no champion.")
    }
    for room, (score, notes) in history.items():
        heading = "## R025 authentic four-seat collection and weighted NON-ACCEPTANCE — 2026-11-07"
        paragraph = (f"{heading}\n- MARKET worker23, DESIGN worker24, BUILD worker25, COST worker26; "
                     f"12 original critique reports/114 criteria/24 correct means; {score}, all seats >=3.0. "
                     "Receipt state/ROUND025_AUTHENTIC_FOUR_SEAT_COLLECTION_SCORED_NO_CHAMPIONS.json.\n"
                     f"- {notes}\n- All three PH rooms have no genuine existing incumbent: +0.25 comparison inapplicable. "
                     "No accepted candidate, owner approval, procurement or global DONE; independent post-scoring Reviewer22 requested, verdict pending.\n")
        append(ROOT / "rooms" / room / "history.md", paragraph, heading)
    title1 = "## R025 authentic four-seat collection scored with NO new champion — 2026-11-07"
    entry1 = "\n".join([
        title1,
        "- DISTINCT post-dispatch prime collection: genuine MARKET23/DESIGN24/BUILD25/COST26; 12/12 own-seat files inspected, 114 separate 1-5 criteria, 24 half-up means and evidence links independently verified; no private key/outcome leaks found in file contents.",
        "- Scores PH-PRIMARY A4.01/B4.07, PH-BATH3 A3.82/B3.72, PH-BATH4 A3.85/B3.63; all 24 specialist seat means >=3.0, but no valid existing incumbent for +0.25 replacement test.",
        "- Frozen source 6/6, prime-only keys 3/3, signed parents 4/4; score receipt state/ROUND025_AUTHENTIC_FOUR_SEAT_COLLECTION_SCORED_NO_CHAMPIONS.json (13,338 bytes) signed, independent Reviewer22 POST-SCORE verdict requested/pending.",
        "- None accepted: Chicago exact-lot/ETA and complete cartoned/delivered cost unverified, native openings/drain/pan cuts unknown, PH-BATH3 TUB/WALK-IN and basin undecided, PH-BATH4 35-vs-27 SF; all original room statuses/champions held.",
        "- 13 rooms/26 instances/27 historic rows/$23,572.44 four-unit material, old 15% waste once; selected fixtures and all previous signed receipts preserved, no owner/GC approval, Revit/Smartsheet write, supplier outreach or purchases."
    ]) + "\n"
    title2 = "## R026 TX wet-bath formal neutral source frozen, awaiting independent preflight — 2026-11-07"
    entry2 = "\n".join([
        title2,
        "- Distinct future cohort TX-PRIMARY/TX-BATH3: original signed four prepared A/B preserved; four new critic-neutral copies, two separate private _keys and four signed parents validated in state/ROUND026_FORMAL_TWO_TX_ROOMS_SOURCE_FROZEN_PREDISPATCH.json.",
        "- R026 preflight requested independently from Reviewer27; no clearance yet, critics not dispatched, no weighted score, no champion, not owner-approved. Source freeze is NOT a release.",
        "- Exact Elm wet WALL/NICHE variants and F&D SKU 101317949 Luxe 24x24 / 101487775 Riviera 24x48 have per-item published wet DCOF>=0.42 and separately shower-floor permissions; Porcelanosa third-option wet proof UNKNOWN.",
        "- TX Primary BNX 48in LINEAR/BR73480/no niche/TX-WC inherited once; TX3 owner TUB/WALK-IN UNSELECTED, BNX square POINT/PAN only if WALK-IN, no invented TX3 basin decision.",
        "- Same-job Elm rates, non-Chicago F&D retail and null Soho price remain distinct; native cut geometry, full delivered cost, project owner budget and Chicago matching lot unknown, 13/26/27/$23,572.44 and original waste once remain intact."
    ]) + "\n"
    if len(entry1.splitlines()) > 15 or len(entry2.splitlines()) > 15:
        raise RuntimeError("Ledger entry exceeds owner 15-line limit")
    append(LEDGER, entry1, title1)
    append(LEDGER, entry2, title2)
    print("R025 3 room histories and ledger entry",len(entry1.splitlines()),"lines;")
    print("R026 formal sourcefreeze ledger entry",len(entry2.splitlines()),"lines; no scored or owner release")


if __name__ == "__main__":
    main()
