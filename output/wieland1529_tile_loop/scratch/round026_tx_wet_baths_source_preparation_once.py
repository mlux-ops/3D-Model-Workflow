"""Additive next TX wet-bath selection source; no R025 phase overlap."""
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP
import json,hashlib
R=Path(__file__).resolve().parents[1]
receipt=R/"state/ROUND026_TWO_TX_WET_BATHS_PREPARED_NOT_SUBMITTED.json"
assert not receipt.exists()
rooms={x["id"]:x for x in json.loads((R/"state/ROOMS.json").read_text(encoding="utf8"))["rooms"]}
spec={
 "TX-PRIMARY":{
  "A":("Elm Cortar Clay FLAT Soft 24x48","https://www.elmsurfaces.com/product/cortar-clay","FLAT Wet Areas WALL (not Ribbed)","Riviera Oat","quiet warm monochrome Clay + travertine-look 24x48 LINEAR floor"),
  "B":("Elm Cortar Clay FLAT Soft 24x48 with a LIMITED Elm Tones Copper 2x20 glossy wet WALL feature","https://www.elmsurfaces.com/product/cortar-clay","both Cortar Clay FLAT and Tones Copper individually Wet Areas WALL; feature NET allocation unknown","Luxe Sand","controlled warm Copper accent and matte 24x24 ivory concrete-look continuous LINEAR floor")},
 "TX-BATH3":{
  "A":("Elm Soho Emerald 2x10 Glossy","https://www.elmsurfaces.com/product/soho-emerald","exact Soho Emerald Wet Areas WALL, do not borrow Tones Emerald permission","Riviera Oat","jewel-tone wet wall and Sandstone niche grounded by warmer stone-look 24x48"),
  "B":("Elm Tones Copper 2x20 Glossy","https://www.elmsurfaces.com/product/copper-tones","exact Copper Tones individual Wet Areas WALL","Luxe Sand","warm artisan Copper wet field, Sandstone niche and bright 24x24 ivory floor")}
}
floors={
 "Luxe Sand":("101317949","24x24","23.70x23.70","8mm matte rectified","https://www.flooranddecor.com/porcelain-tile/luxe-sand-matte-porcelain-tile-101317949.html","3.49","15.52"),
 "Riviera Oat":("101487775","24x48","23.58x47.28","8mm matte rectified","https://www.flooranddecor.com/porcelain-tile/riviera-oat-matte-porcelain-tile-101487775.html","3.99–4.39","16.00")
}
files={}
for rid,options in spec.items():
 r=rooms[rid];assert r["status"]=="blocked" and r["champion_id"] is None
 base=R/"rooms"/rid/"board"/"round-026"/"prepared"/"candidates"
 assert not base.exists()
 rows={z["surface"]:z for z in r["carried_tile_rows"]}
 wall=rows["wall"];floor=rows["floor"];accent=rows["accent"]
 geometry=json.loads((R/"rooms"/rid/"geometry.json").read_text(encoding="utf8"))
 dims=", ".join(f'{z["id"]} {z["length"]["value"]:.3f}ft x {z["tiled_height"]["value"]:.2f}ft (drawing only)' for z in geometry.get("tiled_walls",[]))
 old=Decimal(str(r["carried_quote_material_subtotal_usd_per_unit"]))
 threshold=(old*Decimal("1.25")).quantize(Decimal("0.01"),rounding=ROUND_HALF_UP)
 for letter,(wallname,wurl,wgate,floor_key,design) in options.items():
  sku,fsize,actual,finish,furl,retail,box=floors[floor_key]
  if rid=="TX-PRIMARY":
   plumbing="Owner-selected Brizo Black Onyx BT0734816-BNX 48in LINEAR with separate BR73480 rough, factory SOLID BNX grate and NO niches; TX-WC inherits same bath LEVEL tile once."
   pan="SELECTED 48in LINEAR shower PAN, exact same SKU as LEVEL, independently Shower Floor YES and published wet DCOF >=0.42. Installer cuts/slopes large tile; neither 6mm mosaic nor unapproved tile-in insert is assumed."
   niche="NONE by explicit owner direction; original excluded and unpriced niche reference must not be added to cost or scope."
   if letter=="B":pricewall="Cortar Clay flat 24x48 and Tones Copper 2x20 are both in matching Elm 2026-09-04 job quote ($8.14/SF, $6.95/SF). Feature-wall net area is UNKNOWN and must be subtracted from full-flat allocation before pricing; never double count."
   else:pricewall="Exact Cortar Clay FLAT 24x48 in matching Elm 2026-09-04 job trade quote $8.14/SF."
   quantities="Compute actual LEVEL net x1.15 + independent LINEAR PAN net x1.25 + TX-WC inherited net x1.15 ONCE, replacing original combined floor gross, not compounded on original 15%."
  else:
   plumbing="Owner TUB vs WALK-IN remains UNSELECTED. Selected Brizo Roccesco Black Onyx wet fixtures and conditional BT062415-BNX 4in square POINT ONLY if owner chooses WALK-IN; not tub waste. Do not assert basin is unselected for TX-BATH3."
   pan="CONDITIONAL: If WALK-IN is selected, 4-plane POINT PAN uses exact same SKU as LEVEL, individually Shower Floor YES and wet DCOF >=0.42, cut by owner installer. If TUB: NO tiled shower PAN, conditional Brizo shower POINT N/A."
   niche="[Elm Tones Sandstone 2x20 Glossy](https://www.elmsurfaces.com/product/sandstone-tones), independent Wet Areas NICHE wall listing. Exact same-job 2026-09-04 Elm $6.95/SF; niche SF from source remains provisional."
   pricewall=("Soho Emerald 2x10 wall has NO matching quote; do not use Tones Emerald $6.95/SF for Soho." if letter=="A" else "Exact Tones Copper 2x20 Glossy is in Elm 2026-09-04 same-job quote $6.95/SF.")
   quantities="After owner selects TUB/WALK-IN and native receipt confirms areas, LEVEL net x1.15; add separate POINT PAN net x1.25 ONLY if WALK-IN. Original floor gross already contains 15%; avoid compounded waste."
  doc=f"""# {rid} — R026 neutral tile scheme {letter} | SOURCE PREPARED ONLY

**Actual program and owner holds:** {plumbing}

**Wet WALL:** [{wallname}]({wurl}). {wgate}. Wall approval not transferred to relief variant, niche, floor, ceiling or another color. Wet-wall substrate/grout/transition selection held to actual room geometry.

**NICHE:** {niche}

**LEVEL bath floor:** Floor & Decor [Vetta Elements {floor_key}, SKU {sku}]({furl}), nominal {fsize}, actual {actual}, {finish}; exact item Bathroom Floor YES, published wet DCOF >=0.42 (threshold only, not invented raw lab number).

**Separate PAN:** {pan} Actual slope, drain rough/waterproof assembly and visible cuts under 3in require native receipts and installer acceptance; do not disqualify the tile simply because it is large format.

**Design and Old Town comparison:** {design}. Actual selected Black Onyx metal is retained. Only OT01 has an attributable powder-like bath photo (dark vanity, white wainscot, patterned upper wall, contrasted floor); no photographed Old Town tub/shower specific tile/grout is authenticated. OT01–OT04 are one building, OT05 bath image unverified. Lincoln Park and Gold Coast secondary, no invented buyer premium.

**Actual 1529 job costs:** Original carried material ${old:.2f}/room copy, original 125%-of-quote *provisional* comparison ${threshold:.2f}, NOT owner-allocated budget (actual ROOMS room budget NULL). Source original gross, 15% waste already counted ONCE: WALL {wall['qty_sf_per_unit']:.2f} SF, FLOOR {floor['qty_sf_per_unit']:.2f} SF, ACCENT {accent['qty_sf_per_unit']:.2f} SF. Original finished quote row costs are NOT new substitution quotes. {pricewall} Floor & Decor {floor_key} public observed ${retail}/SF (non-Chicago storefront, current Chicago price/lot/ETA UNKNOWN), box {box}SF; actual room delivered subtotal UNKNOWN after freight/cartons/mortar/trim and true PAN/LEVEL area split. {quantities}

**Native geometry and manufacturer source:** 1527 and 1529 SAME building owner-confirmed; prior drawing-derived W lengths {dims}; no native individual element/room/drain receipt to certify layout or a focal-edge cut >=3in. Wet WALL, LEVEL, and independently conditional PAN applications must be checked at actual exact product/size/finish; F&D public seller catalog and original Elm Wet Areas research establish item-level published eligibility, NOT local physical stock. 24in+ FLOOR/PAN priority complied; potential unrectified edge/thickness alternatives not falsely substituted. Proposed floor grout 1/8in is only an owner/installer sample starting point.

**Selection and review:** Only approved vendor Elm/Floor & Decor products in this candidate; three-plus cross-vendor look/price comparison stays in rooms/{rid}/vendor_comparison_R023_current.md (Porcelanosa alternatives unqualified if exact wet DCOF missing). Preserves signed R019/R022 originals and R025 current active phase. This is a future DISTINCT R026 PREPARED source, not preflight-cleared, dispatched, scored, an accepted champion, owner-approved specification or order.
"""
  p=base/(letter+".md");p.parent.mkdir(parents=True,exist_ok=True);p.write_text(doc,encoding="utf8",newline="\n")
  b=p.read_bytes();files[str(p.relative_to(R)).replace("\\","/")]={"sha256":hashlib.sha256(b).hexdigest(),"bytes":len(b)}
parent={}
for rel in ("state/ROUND025_FORMAL_THREE_PH_ROOMS_SOURCE_FROZEN_PREDISPATCH.json","state/ROUND025_PH_THREE_ROOM_PREPARED_NOT_SUBMITTED.json","state/ROUND023_TRADE_PRICING_13_ROOM_ADDENDUM_SHA.json"):
 b=(R/rel).read_bytes();parent[rel]={"sha256":hashlib.sha256(b).hexdigest(),"bytes":len(b)}
receipt.write_text(json.dumps({"round":26,"phase":"ADDITIVE_SOURCE_PREPARED_ONLY_WAIT_R025_BOARD","focus":["TX-PRIMARY","TX-BATH3"],"neutral_options":files,"signed_parent_receipts":parent,"user_vendors":["Elm Surfaces","MSI Surfaces","Porcelanosa","Floor & Decor"],"historical_material_total_usd":23572.44,"owner_TX_BATH3_TUB_vs_WALKIN":"UNSELECTED","reviewer_preflight":None,"critic_dispatch":None,"weighted_score":None,"champions_changed":False,"global_DONE":False},indent=2)+"\n",encoding="utf8",newline="\n")
print("R026 future TX cohort prepared",len(files),"candidate A/B files; no R025 board overlap")
