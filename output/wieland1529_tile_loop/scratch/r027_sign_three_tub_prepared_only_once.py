"""One-time receipt for the independently prepared R027 tub-bath source cohort.

This tool refuses incomplete inputs; never regenerates a prepared candidate,
old signed manifests, owner cards or other previously accepted work.
"""
from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROOMS = ("PH-BATH2","TX-BATH2","TX-BATH4")
RECEIPT = "state/ROUND027_THREE_DURAVIT_TUB_BATHS_PREPARED_NOT_SUBMITTED.json"
EXPECTED = [
    *(f"rooms/{room}/board/round-027/prepared/candidates/{letter}.md"
      for room in ROOMS for letter in ("A","B")),
    "research/products/R027_TUB_THREE_ROOM_SOURCED_ALTERNATIVES.md",
    *(f"rooms/{room}/vendor_comparison_R027_current.md" for room in ROOMS),
]
PARENTS = [
    "state/ROUND024_AUTHENTIC_FOUR_SEAT_COLLECTION_SCORED_NO_CHAMPIONS.json",
    "state/ROUND026_FORMAL_TWO_TX_ROOMS_SOURCE_FROZEN_PREDISPATCH.json",
    "state/ROUND026_INDEPENDENT_PREDISPATCH_REVIEWER27_CLEARANCE.json",
    "state/ROUND026_AUTHENTIC_FOUR_SEAT_COLLECTION_SCORED_NO_CHAMPIONS.json",
    "state/ROUND025_SCOPEFIX1_INDEPENDENT_POSTSCORE_REVIEWER30_CLEARANCE.json",
]


def fp(rel: str) -> dict:
    raw=(ROOT/rel).read_bytes()
    return {"sha256":hashlib.sha256(raw).hexdigest(),"bytes":len(raw)}


def main():
    if (ROOT/RECEIPT).exists():
        raise FileExistsError(RECEIPT+" previously signed, no reruns")
    missing = [r for r in EXPECTED+PARENTS if not (ROOT/r).is_file()]
    if missing:
        raise RuntimeError("Prepared cohort incomplete, not signed: "+repr(missing))
    for room in ROOMS:
        for letter in ("A","B"):
            rel=f"rooms/{room}/board/round-027/prepared/candidates/{letter}.md"
            doc=(ROOT/rel).read_text(encoding="utf-8")
            low=doc.lower()
            if room not in doc[:200] or len(doc)<500:
                raise RuntimeError("Room identity/length missing "+rel)
            for word in ("duravit","tub","no tiled","wall","niche","level","dcof","quote","unknown"):
                if word not in low:
                    raise RuntimeError("Missing expected explicit qualification "+word+" in "+rel)
            for forbidden in ("daltile", "platform surfaces", "emser"):
                if forbidden in low:
                    raise RuntimeError("Earlier excluded vendor appears in NEW neutral source "+rel)
            if "owner approved" in low and "not owner approved" not in low:
                raise RuntimeError("Potential false owner approval "+rel)
        comp=(ROOT/f"rooms/{room}/vendor_comparison_R027_current.md").read_text(encoding="utf-8")
        if "101317949" not in comp or "101487775" not in comp:
            raise RuntimeError("Missing both known independent exact F&D alternatives in "+room)
    rows=json.loads((ROOT/"state/ROOMS.json").read_text(encoding="utf-8"))["rooms"]
    material=sum(Decimal(str(r["carried_quote_material_subtotal_usd_per_unit"])) * r["unit_count"] for r in rows)
    counts={"rooms":len(rows),"copies":sum(r["unit_count"] for r in rows),
            "rows":sum(len(r["carried_tile_rows"]) for r in rows),"usd":str(material)}
    if counts!={"rooms":13,"copies":26,"rows":27,"usd":"23572.44"}:
        raise RuntimeError("Historical baseline changed: "+repr(counts))
    status=dict(Counter(r["status"] for r in rows))
    if status!={"blocked":8,"active":3,"seeded":2}:
        raise RuntimeError("Unexpected room promotion: "+repr(status))
    for room in ROOMS:
        matching=next(x for x in rows if x["id"]==room)
        if matching["champion_id"] is not None or matching["status"]!="blocked":
            raise RuntimeError(room+" no longer blocked/no incumbent")
    receipt={
        "round":27,"phase":"ADDITIVE_SOURCE_PREPARED_ONLY_NOT_FORMALLY_FROZEN",
        "focus_rooms":list(ROOMS),
        "neutral_prepared_candidates":{
            r:fp(r) for r in EXPECTED if "/prepared/candidates/" in r},
        "source_research_and_comparisons":{
            r:fp(r) for r in EXPECTED if "/prepared/candidates/" not in r},
        "signed_ancestors":{r:fp(r) for r in PARENTS},
        "source_author":"new R027 three-Duravit-tub product research; no authenticated specialist critique",
        "allowed_vendors":["Elm Surfaces","MSI Surfaces","Porcelanosa","Floor & Decor"],
        "all_three_tubs_NO_TILED_PAN":True,
        "native_cut_geometry":"UNKNOWN; existing read-only job queued, no invented dimensions",
        "project_Chicago_lot_and_landed_cost":"UNKNOWN",
        "provisional_125pct_not_owner_approved_budget":True,
        "historical_total":counts,"original_gross_waste_included_once_pct":15,
        "status_counts":status,
        "pre_dispatch_reviewer":None,
        "formal_source_frozen":False,
        "critic_dispatch":None,"scoring":None,
        "champions_changed":False,"owner_approval":False,
        "procurement_release":False,"global_DONE":False,
    }
    with (ROOT/RECEIPT).open("x",encoding="utf-8",newline="\n") as f:
        f.write(json.dumps(receipt,indent=2)+"\n")
    print("R027 PREPARED ONLY: 6/6 candidates,4/4 research/comparisons,5/5 parents signed")
    print("SHA",fp(RECEIPT))


if __name__=="__main__":
    main()
