"""Controlled R027 tub source-neutralization / distinct formal freeze (run once).

Seven older signed sources are never modified. No private keys are exposed to
the four future critics. New neutral copies omit R024 outcome/role language.
"""
from pathlib import Path
import hashlib
import json
import re

ROOT=Path(__file__).resolve().parents[1]
PREP="state/ROUND027_THREE_DURAVIT_TUB_BATHS_PREPARED_NOT_SUBMITTED.json"
FIX="state/ROUND027_TUB_PREPARED_FIX1_SOURCE_SCOPE_SUPERSEDING_ONE_FILE.json"
OUT="state/ROUND027_FORMAL_THREE_TUB_ROOMS_SOURCE_FROZEN_PREDISPATCH.json"
DATA={
 "PH-BATH2":("89.70","3.67","40.20","920.28","1150.35","35","5.00","2.54",
    "Duravit Starck TUB and Hansgrohe Matte White; Ecostat/tub-spout compatibility held; no new basin decision; NO tiled shower PAN"),
 "TX-BATH2":("92.80","8.63","43.70","999.92","1249.90","38","5.207","2.60",
    "Duravit Starck TUB, Hansgrohe Chrome, basin owner UNSELECTED, NO tiled shower PAN"),
 "TX-BATH4":("89.80","8.63","44.30","1320.82","1651.02","38.5","5.00","2.54",
    "Duravit Starck TUB, Hansgrohe Matte White; Ecostat/pressure-balance diverter spout/rough compatibility held; NO tiled shower PAN")
}


def fingerprint(p):
    b=(ROOT/p).read_bytes()
    return {"sha256":hashlib.sha256(b).hexdigest(),"bytes":len(b)}


def new(p,text):
    path=ROOT/p
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("x",encoding="utf-8",newline="\n") as f:
        f.write(text)
    return fingerprint(p)


def main():
    if (ROOT/OUT).exists():
        raise FileExistsError("R027 formal freeze exists, do not rerun")
    initial=json.loads((ROOT/PREP).read_text(encoding="utf-8"))
    fix=json.loads((ROOT/FIX).read_text(encoding="utf-8"))
    if fix["before_sha256"]!=initial["neutral_prepared_candidates"][fix["corrected_file"]]["sha256"]:
        raise ValueError("FIX1 not linked to original R027 preparation")
    for section in ("neutral_prepared_candidates","source_research_and_comparisons","signed_ancestors"):
        for path,sha in initial[section].items():
            expected={"sha256":fix["after_sha256"],"bytes":fix["after_bytes"]} if path==fix["corrected_file"] else sha
            if fingerprint(path)!=expected:
                raise ValueError("Predecessor SHA mismatch "+path)
    rooms=json.loads((ROOT/"state/ROOMS.json").read_text(encoding="utf-8"))["rooms"]
    for room in DATA:
        r=next(x for x in rooms if x["id"]==room)
        if r["status"]!="blocked" or r["champion_id"] is not None:
            raise ValueError("Room already promoted "+room)
    neutral={}
    private={}
    transformations={}
    for room,values in DATA.items():
        wall,niche,level,original,provisional,area,back,returns,fixture=values
        for letter in ("A","B"):
            old="rooms/"+room+"/board/round-027/prepared/candidates/"+letter+".md"
            source=(ROOT/old).read_text(encoding="utf-8")
            lines=source.splitlines()
            chosen=[]
            for label in ("| Wet tub WALL |","| Wet NICHE |","| Bath LEVEL |"):
                found=[x for x in lines if x.startswith(label)]
                if len(found)!=1:
                    raise RuntimeError("Expected exactly one "+label+" for "+old)
                chosen.append(found[0])
            if "no tiled shower pan" not in source.lower():
                raise RuntimeError("Wrong wet program "+old)
            if room=="TX-BATH2" and "basin UNSELECTED" not in source:
                raise RuntimeError("TX2 basin owner choice altered "+old)
            document="\n".join([
                "# "+room+" — neutral A/B tile candidate "+letter,
                "",
                "**Selected program:** "+fixture+".",
                "| Tiled surface | Exact proposed product | Manufacturer application and source price | Intent |",
                "|---|---|---|---|",
                *chosen,
                "",
                "**Separate application:** WALL wet-listed only for the exact maker/finish/color; NICHE independently wet-listed where existing actual niche is verified. Bath LEVEL exact proposed F&D item must list Bathroom Floor YES and product-specific published wet DCOF >=0.42; published inequality is not raw lab measurement. This is a TUB bathroom; LINEAR PAN and POINT PAN N/A. No shower PAN may be introduced.",
                "**Source economics:** Sep 04 2026 ELM exact matching 1529 trade quote supersedes older unrelated quotations. F&D rates on listed pages are observed non-Chicago public prices, not current Chicago PO prices. MSI 24x48 Murcia alternatives publish >0.42 but numerical price on request and Chicago lot unknown; Porcelanosa Bottega item technical wet rating UNKNOWN and not a qualified floor. See permitted research/products/R027_TUB_THREE_ROOM_SOURCED_ALTERNATIVES.md for >=3 real product comparisons per surface.",
                "**Original source gross per physical copy includes original 15% waste ONCE:** Wet WALL "+wall+" SF, NICHE "+niche+" SF provisional, LEVEL "+level+" SF. Original carried material USD "+original+"/copy; 125%-of-original USD "+provisional+"/copy is only a PROVISIONAL comparison, no owner-allocated budget. New actual floor/field/niche areas, replacement waste, whole cartons and complete delivered freight/tax/grout/trim/setting cost require real receipts; budget gate UNKNOWN.",
                "**Geometry:** earlier drawing-derived floor "+area+" SF, tub back wall W1 "+back+" ft, returns "+returns+" ft each, tiled height 7.75 ft. Actual native Revit element and field openings/drain/niche/tub rough dimensions, wall plumbness, 24in+ tile focal cuts under 3in and niche dimensions UNKNOWN, not measured approvals.",
                "**Design:** Independent reviewer to judge tile material, size, actual Hansgrohe finish and restrained niche wall hierarchy. Proposed 1/8-inch grout and edge profile remain owner/installer design decisions, not construction-release details. In a 24x48 floor actual cuts must be checked before any claim of a clean layout.",
                "**Old Town photo:** One attributable OT01 at 405 W Armitage DRY powder-like bathroom demonstrates layered visual contrast, not competitor wet tile SKU; OT01–OT04 share one building. OT05 bathroom imagery unverified.",
                "**Availability and approval:** Chicago exact shade lot, cartons, ETA, freight and current trade offer UNKNOWN. No native dimension, owner sign-off, bath fixture change, procurement, sample, installation, or owner-approved tile champion claimed.",
                ""])
            if re.search(r"(?i)r024|r025|r026|_key\.json|history\.md|champion\.md|critic-|state/ROOMS\.json|state/LEDGER\.md",document):
                raise RuntimeError("Blind role/predecessor leak "+old)
            out="rooms/"+room+"/board/round-027/candidates/"+letter+".md"
            neutral[out]=new(out,document)
            transformations[out]={"source_prepared":old,"prepared_fingerprint_after_fix1":fingerprint(old),
                                  "neutralization":"Exact item schedule and all owner/price/geometry knowns retained without prior scores/outcomes"}
        key="rooms/"+room+"/board/round-027/_key.json"
        private[key]=new(key,json.dumps({"room":room,"round":27,"prime_only":True,"incumbent":None,
                     "A":"fresh neutral design","B":"fresh neutral design","do_not_disclose_to_critics":True},indent=2)+"\n")
    parent_names=(PREP,FIX,
        "state/ROUND024_AUTHENTIC_FOUR_SEAT_COLLECTION_SCORED_NO_CHAMPIONS.json",
        "state/ROUND026_AUTHENTIC_FOUR_SEAT_COLLECTION_SCORED_NO_CHAMPIONS.json",
        "state/ROUND025_SCOPEFIX1_INDEPENDENT_POSTSCORE_REVIEWER30_CLEARANCE.json")
    parents={p:fingerprint(p) for p in parent_names}
    receipt={"round":27,"phase":"1-SOURCE_FROZEN_PENDING_INDEPENDENT_PREDISPATCH_REVIEW",
      "focus_rooms":list(DATA),"neutral_candidates":neutral,"prime_only_private_keys":private,
      "signed_parents":parents,"neutralization_audit":transformations,
      "vendors":["Elm Surfaces","MSI Surfaces","Porcelanosa","Floor & Decor"],
      "all_three_Duravit_TUB_no_tiled_PAN":True,"original_four_unit_material":23572.44,
      "original_gross_waste_once_pct":15,
      "native_room_geometry_and_Chicago_delivery":"UNKNOWN",
      "owner_budget_125_percent":"PROVISIONAL",
      "independent_reviewer":None,"critic_dispatch":None,"weighted_scores":None,
      "champions_changed":False,"owner_approval":False,"global_DONE":False}
    sign=new(OUT,json.dumps(receipt,indent=2)+"\n")
    print("R027 FORMAL FROZEN 6/6 neutral, 3/3 private keys, 5/5 parents, SHA",sign["sha256"])


if __name__=="__main__":
    main()
