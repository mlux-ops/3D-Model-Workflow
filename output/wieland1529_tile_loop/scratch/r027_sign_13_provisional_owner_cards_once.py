"""Sign additive thirteen-room provisional cards without modifying original cards."""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from decimal import Decimal
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
NEW=Path("deliverables/r027-13-owner-review-PROVISIONAL")
OLD=Path("state/ROUND025_13_OWNER_SELECTION_CARDS_SHA.json")
RECEIPT=Path("state/ROUND027_13_PROVISIONAL_OWNER_PREVIEWS_SIGNED.json")


def fp(path):
    raw=(ROOT/path).read_bytes()
    return {"sha256":hashlib.sha256(raw).hexdigest(),"bytes":len(raw)}


def main():
    if (ROOT/RECEIPT).exists():
        raise FileExistsError("R027 owner cards already signed")
    old=json.loads((ROOT/OLD).read_text(encoding="utf-8"))
    for path, sig in old["files"].items():
        if fp(Path(path))!=sig:
            raise RuntimeError("Historical R025 owner card modified: "+path)
    rows=json.loads((ROOT/"state/ROOMS.json").read_text(encoding="utf-8"))["rooms"]
    if len(rows)!=13 or sum(x["unit_count"] for x in rows)!=26 or sum(len(x["carried_tile_rows"]) for x in rows)!=27:
        raise RuntimeError("Original 13/26/27 baseline changed")
    total=sum(Decimal(str(x["carried_quote_material_subtotal_usd_per_unit"]))*x["unit_count"] for x in rows)
    if total!=Decimal("23572.44"):
        raise RuntimeError("Original $23572.44 material total changed")
    if dict(Counter(x["status"] for x in rows))!={"blocked":8,"active":3,"seeded":2}:
        raise RuntimeError("Unexpected status promotions")
    files={}
    for row in rows:
        path=NEW/(row["id"]+".md")
        full=ROOT/path
        if not full.is_file():
            raise FileNotFoundError("R027 preview not complete "+str(path))
        txt=full.read_text(encoding="utf-8")
        if row["id"] not in txt[:300] or len(txt)<400:
            raise RuntimeError("R027 card malformed "+str(path))
        if "PROVISIONAL" not in txt.upper() or "NOT" not in txt.upper():
            raise RuntimeError("Missing nonapproval label "+str(path))
        if "CHAMPION ACCEPTED" in txt.upper() or "PURCHASING APPROVED" in txt.upper():
            raise RuntimeError("Unsubstantiated owner/purchasing approval "+str(path))
        files[path.as_posix()]=fp(path)
    readme=NEW/"README.md"
    if readme.is_file() and "README.md" not in files:
        files[readme.as_posix()]=fp(readme)
    report={
        "round":27,"phase":"THIRTEEN_OWNER_PREVIEWS_PROVISIONAL_SOURCE_ONLY_NOT_APPROVED",
        "cards":files,
        "signed_R025_original_manifest":fp(OLD),
        "card_count":13,
        "original_R025_cards_unchanged":13,
        "historical_original_rooms":13,
        "historical_physical_instances":26,
        "historical_material_rows":27,
        "historical_four_unit_material_usd":23572.44,
        "original_waste_included_once_pct":15,
        "program_status_counts":{"blocked":8,"active":3,"seeded":2},
        "native_geometry":"UNKNOWN",
        "all_room_full_delivered_price_and_lot":"UNKNOWN",
        "owner_only_unselected_programs":"PH-BATH3 and TX-BATH3 TUB/WALK-IN; other existing owner basin/fixture choices retained",
        "cards_owner_approved":False,
        "champions_accepted_in_this_round":False,
        "procurement_release":False,
        "global_DONE":False
    }
    with (ROOT/RECEIPT).open("x", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(report,indent=2)+"\n")
    print("R027 owner preview cards 13/13 SOURCE SIGNED; historical R025 cards 13/13 preserved")
    print("SHA",fp(RECEIPT))


if __name__=="__main__":
    main()
