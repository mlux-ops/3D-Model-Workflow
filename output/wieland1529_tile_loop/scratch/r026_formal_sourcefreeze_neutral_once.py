"""Create critic-safe R026 copies from immutable seven-item PREPARED receipt.

Intentional normalization: remove earlier-round pointers and PREPARED label from
critic-visible copies, and cite the Tones Copper exact maker page separately.
The seven signed originals are read-only and retain their original fingerprints.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FOCUS = ("TX-PRIMARY", "TX-BATH3")
OUT_RECEIPT = "state/ROUND026_FORMAL_TWO_TX_ROOMS_SOURCE_FROZEN_PREDISPATCH.json"


def fingerprint(rel):
    raw = (ROOT / rel).read_bytes()
    return {"sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)}


def write_exclusive(rel, contents):
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as out:
        out.write(contents)
    return fingerprint(rel)


def main():
    if (ROOT / OUT_RECEIPT).exists():
        raise FileExistsError("R026 formal freeze already present; never regenerate")
    prepared_rel = "state/ROUND026_TX_FOUR_SCHEMES_TWO_OWNER_CARDS_SIGNED.json"
    prepared = json.loads((ROOT / prepared_rel).read_text(encoding="utf-8"))
    if prepared["phase"] != "SOURCE_PREPARED_NOT_SUBMITTED_R025_ACTIVE":
        raise RuntimeError("R026 signed prepared state differs")
    if len(prepared["files"]) != 7 or len(prepared["parents"]) != 3:
        raise RuntimeError("R026 signed prepared files/parents not 7/3")
    for section in ("files", "parents"):
        for rel, expected in prepared[section].items():
            if fingerprint(rel) != expected:
                raise RuntimeError("R026 signed predecessor mismatched: " + rel)
    frozen = {}
    private = {}
    audit = {}
    for room in FOCUS:
        for letter in ("A", "B"):
            source_rel = f"rooms/{room}/board/round-026/prepared/candidates/{letter}.md"
            frozen_rel = f"rooms/{room}/board/round-026/candidates/{letter}.md"
            s = (ROOT / source_rel).read_text(encoding="utf-8")
            lines = s.splitlines()
            if len(lines) != 19 or not lines[0].startswith(f"# {room} — R026 neutral tile scheme {letter}"):
                raise RuntimeError("Unexpected signed source shape " + source_rel)
            lines[0] = f"# {room} — neutral candidate {letter}"
            if not lines[-1].startswith("**Selection and review:**"):
                raise RuntimeError("Source conclusion changed " + source_rel)
            lines[-1] = ("**Verification limits:** Manufacturer product applications, publicly quoted exact prices, "
                         "and unresolved owner choices are identified above. This neutral option is "
                         "not an approved specification: native opening/drain/cut dimensions, "
                         "complete delivered case-rounded costs, Chicago lot/ETA, and applicable "
                         "owner-only decisions still require evidence. No owner or procurement release.")
            if room == "TX-PRIMARY" and letter == "B":
                old = ("[Elm Cortar Clay FLAT Soft 24x48 with a LIMITED Elm Tones Copper 2x20 "
                       "glossy wet WALL feature](https://www.elmsurfaces.com/product/cortar-clay). "
                       "both Cortar Clay FLAT and Tones Copper individually Wet Areas WALL")
                new = ("[Elm Cortar Clay FLAT Soft 24x48](https://www.elmsurfaces.com/product/cortar-clay) "
                       "with a LIMITED [Elm Tones Copper 2x20 glossy wet WALL feature]"
                       "(https://www.elmsurfaces.com/product/copper-tones). "
                       "Both Cortar Clay FLAT and Tones Copper individually Wet Areas WALL")
                if old not in lines[4]:
                    raise RuntimeError("Separate Copper product citation unexpectedly missing")
                lines[4] = lines[4].replace(old, new)
            neutral = "\n".join(lines) + "\n"
            if re.search(r"(?i)R019|R022|R023|R024|R025|round-0\d\d|SOURCE PREPARED|"
                         r"prior.round|previous.outcome|_key\.json|champion\.md|/history\.md|"
                         r"/(?:ROOMS|LEDGER)\.(?:md|json)", neutral):
                raise RuntimeError("Confidential earlier-round marker in neutral " + frozen_rel)
            if room == "TX-PRIMARY":
                if "NO niches" not in neutral or "48in LINEAR" not in neutral or "TX-WC" not in neutral:
                    raise RuntimeError("Primary plumber/WC owner conditions lost")
            else:
                if "TUB vs WALK-IN remains UNSELECTED" not in neutral or "ONLY if owner chooses WALK-IN" not in neutral:
                    raise RuntimeError("Bath3 owner conditional branch lost")
            frozen[frozen_rel] = write_exclusive(frozen_rel, neutral)
            audit[frozen_rel] = {"from_signed_prepared": source_rel, "source": fingerprint(source_rel),
                                 "normalization": "heading/conclusion earlier-round redaction" +
                                 ("; separate Tones Copper maker link" if room == "TX-PRIMARY" and letter == "B" else "")}
        keyrel = f"rooms/{room}/board/round-026/_key.json"
        key = {"round": 26, "room": room, "prime_only": True,
               "existing_incumbent": None,
               "A": "new independent tile alternative; original signed prepared A",
               "B": "new independent tile alternative; original signed prepared B",
               "candidate_roles_not_for_critics": True,
               "source_prepared_manifest": prepared_rel}
        private[keyrel] = write_exclusive(keyrel, json.dumps(key, indent=2) + "\n")
    parents = {rel: fingerprint(rel) for rel in (
        prepared_rel,
        "state/ROUND026_TWO_TX_WET_BATHS_PREPARED_NOT_SUBMITTED.json",
        "state/ROUND025_FOUR_AUTHENTIC_CRITIC_DISPATCH.json",
        "state/ROUND024_AUTHENTIC_FOUR_SEAT_COLLECTION_SCORED_NO_CHAMPIONS.json")}
    receipt = {"round": 26, "phase": "1-SOURCE_FROZEN_PENDING_INDEPENDENT_PREDISPATCH_REVIEW",
               "focus_rooms": list(FOCUS), "neutral_candidates": frozen,
               "prime_only_private_keys": private, "signed_parents": parents,
               "source_preservation": "Four neutral copies normalized only; original seven signed prepared files unchanged",
               "neutralization_audit": audit,
               "allowed_vendors": ["Elm Surfaces", "MSI Surfaces", "Porcelanosa", "Floor & Decor"],
               "original_material_total_four_unit_usd": 23572.44,
               "source_gross_waste_included_once_pct": 15,
               "TX_BATH3_TUB_WALKIN_owner": "UNSELECTED",
               "TX_BATH3_basin_status": "NOT DECLARED UNSELECTED",
               "pre_dispatch_independent_verdict": None,
               "four_critic_reports": False, "formal_scores": None,
               "champions_changed": False, "owner_approval": False,
               "procurement_release": False, "global_DONE": False}
    sig = write_exclusive(OUT_RECEIPT, json.dumps(receipt, indent=2) + "\n")
    assert all(fingerprint(k) == v for k,v in frozen.items())
    assert all(fingerprint(k) == v for k,v in private.items())
    print("R026 FORMAL SOURCE FROZEN; 4/4 neutral A/B; 2/2 segregated private keys; 4/4 ancestors; prepared 7/7 + 3/3 unchanged")
    print("R026 SHA", sig["sha256"], "bytes", sig["bytes"])


if __name__ == "__main__":
    main()
