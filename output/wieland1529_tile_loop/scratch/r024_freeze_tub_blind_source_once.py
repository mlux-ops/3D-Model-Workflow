"""R024 source-frozen neutral board copies; additive only, no predecessor edits."""
from pathlib import Path
import hashlib,json,re
P=Path(__file__).resolve().parents[1]
ROOM={x["id"]:x for x in json.loads((P/"state/ROOMS.json").read_text(encoding="utf8"))["rooms"]}
focus=("PH-BATH2","TX-BATH2","TX-BATH4")
receipt=P/"state/ROUND024_FROZEN_THREE_DURAVIT_TUB_BLIND_SOURCE.json"
assert not receipt.exists()
floorprices={"A":(3.49,3.49),"B":(3.99,4.39)}
for rid in focus:assert not (P/"rooms"/rid/"board/round-024").exists()
parents={}
for name in ("state/ROUND023_THREE_DURAVIT_TUB_LFT_PRELIMINARY_NOT_SUBMITTED.json",
             "state/ROUND023_TRADE_PRICING_13_ROOM_ADDENDUM_SHA.json"):
 b=(P/name).read_bytes()
 parents[name]={"sha256":hashlib.sha256(b).hexdigest(),"bytes":len(b)}
manifest={}
private={}
for rid in focus:
 r=ROOM[rid]
 assert r["status"]=="blocked" and r["champion_id"] is None and r["unit_count"]==2
 price_limit=round(1.25*r["carried_quote_material_subtotal_usd_per_unit"],2)
 private[rid]={"A":"R023 A revised tile option; no incumbent exists","B":"R023 B revised tile option; no incumbent exists"}
 rows={x["surface"]:x for x in r["carried_tile_rows"]}
 w,a,f=(rows[k] for k in ("wall","accent","floor"))
 for letter in ("A","B"):
  base=P/"rooms"/rid/"board/round-023/candidates"/(letter+".md")
  assert base.is_file()
  src=base.read_text(encoding="utf8")
  assert "NO tiled PAN" in src and "Duravit" in src
  if letter=="A":wprice=6.95 if rid!="TX-BATH4" else 8.14; aprice=6.95 if rid!="TX-BATH4" else None
  else:wprice=8.14 if rid=="TX-BATH4" else None;aprice=6.95 if rid!="TX-BATH4" else None
  low,high=floorprices[letter]
  known=round(w["qty_sf_per_unit"]*wprice,2) if wprice is not None else None
  niche=round(a["qty_sf_per_unit"]*aprice,2) if aprice is not None else None
  floorlo=round(f["qty_sf_per_unit"]*low,2)
  floorhi=round(f["qty_sf_per_unit"]*high,2)
  fulllo=round(known+niche+floorlo,2) if known is not None and niche is not None else None
  fullhi=round(known+niche+floorhi,2) if known is not None and niche is not None else None
  cost=(f"Screened complete SF-extended material ${fulllo:.2f}-${fullhi:.2f}/copy <= ${price_limit:.2f} gate ceiling, "
         "but this is not box-rounded, trim/grout-inclusive, delivered, or current Chicago inventory."
         if fulllo is not None else
         f"Full substituted-room cost UNKNOWN (at least one exact ELM alternative has no quote). Known FLOOR screening ${floorlo:.2f}-${floorhi:.2f}/copy; "
         f"room cap ${price_limit:.2f}/copy. Budget gate NOT YET DEMONSTRATED.")
  insert=f"""**R024 SAME-JOB SOURCE PRICING, provenance and budget gate (2026-11-07):** Original 1529 Elm quote dated 2026-09-04, Gmail thread 1a068e80c92c255f (owner-provided read-only inputs/TRADE_QUOTES.md). Exact substitute WALL quoted unit rate {f'${wprice:.2f}/SF' if wprice is not None else 'NULL / NOT QUOTED for this exact new Elm SKU'}, NICHE {f'${aprice:.2f}/SF' if aprice is not None else 'NULL / NOT QUOTED for this exact new Elm SKU'}. Floor item has publicly observed non-Chicago rates ${low:.2f}-${high:.2f}/SF; original gross {f['qty_sf_per_unit']:.2f}SF incl 15% waste once, no second markup. {cost} Historical carried room material ${r['carried_quote_material_subtotal_usd_per_unit']:.2f}/copy; 125% board ceiling ${price_limit:.2f}/copy. Original exact product Elm Tones and flat Cortar quotes outrank generic public pricing ONLY where the color/size/finish matches; unquoted Soho/Noho cannot borrow an Elm Tones quote.

**Formal hard-gate evidence:** Manufacturer individual product WALL and NICHE use must be independently checked; name and wet status in this source are claims with cited vendor product links, not independent Reviewer clearance. F&D FLOOR exact SKU individual published wet DCOF >=0.42, Bathroom Floor YES (and Shower Floor YES although this is TUB). Current US distribution evident from live retail item listing; current Chicago SKU/lot/ETA not independently established. Actual native Revit dimensions/door openings/cut layouts have no element-specific receipt IDs, so formal geometry and full delivered-budget PASS are withheld. 1/8-inch grout is proposed, not maker-approved construction instruction. No tiled shower PAN.

"""
  src=src.replace("**Historical original gross and price per room copy",insert+"**Historical original gross and price per room copy")
  src=src.replace(f"— neutral R023 option {letter} —",f"— neutral R024 option {letter} —")
  src=src.replace("ELM wall and niche price/Chicago availability UNKNOWN;", "Exact substitute Elm wall or niche pricing is documented above when available, otherwise NULL; Chicago on-hand remains UNKNOWN;")
  src=src.replace("No four original critics, no independent Reviewer clearance, weighted score or procurement release; SOURCE ONLY.", "R024 frozen source ONLY, no independent Reviewer clearance or four specialist reports, weighted score or owner release.")
  assert "incumbent" not in src.lower() and "champion" not in src.lower()
  out=P/"rooms"/rid/"board/round-024/candidates"/(letter+".md")
  out.parent.mkdir(parents=True,exist_ok=True)
  out.write_text(src,encoding="utf8",newline="\n")
  b=out.read_bytes()
  manifest[str(out.relative_to(P)).replace("\\","/")]={"sha256":hashlib.sha256(b).hexdigest(),"bytes":len(b)}
 key=P/"rooms"/rid/"board/round-024/_key.json"
 key.write_text(json.dumps({"room":rid,"round":24,"private_critic_forbidden":True,"role_mapping":private[rid],"existing_champion":None},indent=2)+"\n",encoding="utf8",newline="\n")
assert len(manifest)==6
receipt.write_text(json.dumps({
 "round":24,"phase":"SOURCE_FROZEN_PRE_DISPATCH_REVIEWER_REQUIRED",
 "focus_rooms":list(focus),"neutral_candidates":manifest,"private_keys_not_for_critics":
 [f"rooms/{rid}/board/round-024/_key.json" for rid in focus],
 "immutable_parent_receipts":parents,"same_job_elm_trade_quote":"2026-09-04 1a068e80c92c255f",
 "wet_floor_gate":"F&D exact item published >=.42 and Bathroom Floor YES",
 "all_three_programs":"SELECTED_DURAVIT_TUB_NO_TILED_PAN",
 "independent_reviewer_clearance":None,"critic_dispatch":None,"four_authentic_reports":False,
 "formal_scores":None,"champions_changed":False,"owner_approval":False,"purchase_release":False
},indent=2)+"\n",encoding="utf8",newline="\n")
print("R024 SOURCE FROZEN",len(manifest),"neutral candidates / 3 rooms; R023 source SHA unchanged; reviewer required")
