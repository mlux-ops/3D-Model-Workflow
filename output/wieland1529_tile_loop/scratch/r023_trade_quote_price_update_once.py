"""Additive 1529 trade-source cost updates after owner-supplied TRADE_QUOTES arrives."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1]
SOURCE=R/"inputs/TRADE_QUOTES.md"
assert SOURCE.exists()
orig=SOURCE.read_text(encoding="utf8")
for needle in ("2026-09-04","$8.14/SF","$6.95/SF","$8.20/SF","$11.93/SF","1a068e80c92c255f"):
 assert needle in orig,needle
OUT=R/"deliverables/r023-owner-13-trade-price-updated-NOT-APPROVED"
REC=R/"state/ROUND023_TRADE_PRICING_13_ROOM_ADDENDUM_SHA.json"
assert not OUT.exists() and not REC.exists()
rooms={x["id"]:x for x in json.loads((R/"state/ROOMS.json").read_text(encoding="utf8"))["rooms"]}
unit={
"PH-PRIMARY":("ELM Cortar Bone FLAT Soft 24x48",8.14,15.39,"Quoted same 1529 project 2026-09-04; 2 pcs per box, imported 10–12 weeks, 50% deposit; no guarantee today."),
"TX-PRIMARY":("ELM Cortar Clay FLAT Soft 24x48",8.14,15.39,"Quoted same 1529 project 2026-09-04; 2 pcs/box, import 10–12 weeks, 50% deposit."),
"PH-BATH2":("ELM Tones Sapphire Glossy 2x20",6.95,6.50,"Quoted same 1529 project 2026-09-04, maker five-color quote one material line; 24 pieces per 6.50SF box."),
"PH-BATH3":("ELM Tones Sapphire Glossy 2x20",6.95,6.50,"Quoted same 1529 project 2026-09-04; original Opal has a price but exact wet WALL gate unproven."),
"PH-BATH4":("ELM Cortar Bone FLAT Soft 24x48",8.14,15.39,"Flat Bone direct 1529 job quote 2026-09-04. Distinct original Reed/Ribbed quoted $7.37/SF is not wet-application approval."),
"TX-BATH2":("ELM Tones Copper Glossy 2x20",6.95,6.50,"Quoted same 1529 project 2026-09-04, 24 pcs/6.50SF box."),
"TX-BATH3":("ELM Tones Emerald Glossy 2x20",6.95,6.50,"Quoted same 1529 job; proposed different ELM SOHO Emerald has NO source quote; do not transfer price or manufacturer wet approval."),
"TX-BATH4":("ELM Cortar Charcoal FLAT Soft 24x48",8.14,15.39,"Quoted same 1529 job 2026-09-04; manufacturer wet listed FLAT, not unverified relief."),
"PH-POWDER":("ELM Vera Forma Earth Lines Glossy 2x10",8.20,6.22,"Quoted same 1529 job 2026-09-04; 44 pcs/box, 6.22SF/box, FOB TN."),
"TX-POWDER":("ELM Haze Camel/Wheat Matte 1.6x5 blend",11.93,6.14,"Quoted same 1529 job 2026-09-04; 114 pcs/6.14SF box; BOTH colors quoted per SF."),
"TX-POWDER2":("ELM Vera Forma Indigo Edge Glossy 6x6",8.20,7.34,"Quoted same 1529 job 2026-09-04; 30 pcs/7.34SF box, FOB TN.")
}
evidence=R/"research/products/R023_1529_JOB_ELM_TRADE_QUOTE_EVIDENCE_20260904.md"
assert not evidence.exists()
evidence.write_text("""# R023 newly available owner historical trade-pricing evidence, 1529 Wieland

Owner's new read-only export inputs/TRADE_QUOTES.md appeared during R023 validation (modified 2026-11-07 02:28 UTC). **This replaces the earlier "trade file absent" price assessment.** No email, vendor outreach, attachment downloads or account operations performed by this tile selection agent.

Highest-priority 1529 same-job Elm trade QUOTE dated **2026-09-04**, Gmail thread reference **1a068e80c92c255f** / message **1a06e29c0b2333f4** supplied in owner export. Exact line rates: Cortar Bone/Clay/Charcoal FLAT Soft 24x48 **$8.14/SF**, 15.39SF/2-pc box, imported 10–12 weeks, 50% deposit and 300SF minimum aggregated colors/sizes; Tones Sapphire/Opal/Copper/Emerald/Sandstone 2x20 Glossy **$6.95/SF**, 6.50SF/24-pc box; Earth Lines 2x10 Glossy **$8.20/SF**, 6.22SF box; Indigo Edge 6x6 Glossy **$8.20/SF**, 7.34SF box; Haze Camel+Wheat Matte blend 1.6x5 **$11.93/SF**, 6.14SF box. Original Bone Reed/Ribbed $7.37/SF quote **does NOT satisfy** original missing exact wet WALL product permission. Original Caviar NICHE $33.70/SF quote does not give wet use permission.

**These rates match specific same-job product/color/finish only.** New Elm Soho Ivory, Soho Black, Soho Emerald, Noho Taupe, Noho Ivory, Soho Blue have NO matching quote in owner export; do not assign the Tones or Haze rate to them. The manufacturer's product application evidence must remain distinct from the price evidence.

Other vendor historical quote lines in the export: MSI one 513 Fullerton Arabescato Venato slat 4x12 text $8.62 versus quoted $9.069/SF, NOT applicable to another tile SKU. Porcelanosa past project invoices/quotes were attached PDFs, exact per-SF UNREAD; no Porcelanosa 1529 quote. Floor & Decor historic small mosaic order has no SF yield, not a transferable LFT price. For these tiles use current actual manufacturer/store public prices when available. Porcelanosa official Bottega Caliza SKU100280172 23x47 online **$5.98/SF**, but wet DCOF for exact SKU still not authenticated, so NOT selection-qualified.

**Price hierarchy:** documented 2026-09-04 1529 Elm quote > earlier job trades (a quote older than 12 months indicative only) > public catalog price. Quote date is recent, but no current buyer-specific validity date, Chicago same-lot availability or delivered total guaranteed. F&D Luxe Sand SKU101317949 current non-Chicago public **$3.49/SF** and Riviera Oat SKU101487775 **$3.99–$4.39/SF store-dependent**; owner has no trade F&D price for these. Shipping, freight, taxes, current stock, installer and selected grout/edge unknown.

Original $23,572.44 four-unit materials 27 source rows and already included 15% gross waste ONCE. This evidence updates **the certainty of same-job ORIGINAL material rates and exact ELM selected-wall substitute**; it is not new or incremental quote charges, and no order/box requisition is authorized. Native Revit 1527=1529 identity confirmed; room-measured net area and actual waste/installed total remain unverified.
""",encoding="utf8",newline="\n")
files={}
b=evidence.read_bytes();files[str(evidence.relative_to(R)).replace("\\","/")]={"sha256":hashlib.sha256(b).hexdigest(),"bytes":len(b)}
for rid,r in rooms.items():
 quote=unit.get(rid)
 cmp=R/"rooms"/rid/"vendor_comparison_R023_trade_price_addendum.md"
 assert not cmp.exists()
 old=r.get("carried_quote_material_subtotal_usd_per_unit") or 0
 oldlines=[f"# {rid} — R023 new same-job trade-pricing addendum, 2026-11-07","",
 "**Owner quote source:** inputs/TRADE_QUOTES.md; same-job Elm quote 2026-09-04, thread 1a068e80c92c255f. Historical source cost is already included in $23,572.44; no double charge.",
 f"Historical room source **USD {old:.2f}/copy** x two identical instances; original waste 15% once."]
 if quote:
  product,price,box,note=quote
  oldlines += [f"**Exact project-priced Elm source:** {product}; **USD {price:.2f}/SF**, {box:.2f}SF/box. {note}"]
  if rid in {"PH-BATH2","TX-BATH2","TX-BATH4","PH-PRIMARY","TX-PRIMARY","PH-BATH4","PH-BATH3","TX-BATH3"}:
   oldlines += ["**Separate current allowed-vendor floor comparisons:** F&D Luxe Sand 24x24 SKU101317949 online USD 3.49/SF, published wet DCOF >=0.42; F&D Riviera Oat 24x48 SKU101487775 online USD 3.99–4.39/SF by storefront, published wet >=0.42; Porcelanosa Bottega Caliza 23x47 SKU100280172 USD 5.98/SF catalog but wet DCOF UNKNOWN, so NOT gate-qualified. NO Platform, Daltile or Emser champion."]
  if rid.startswith("TX-POWDER") or rid=="PH-POWDER":
   oldlines += ["**Proposed DRY-wall F&D alternative** La Belle Purity or Antique Blue public USD 5.56/SF only; original Elm job-rate is not transferable to new Elm Soho/Noho product. WOOD floor; wet-floor/pan gates N/A."]
 else:
  parent="PH-PRIMARY" if rid=="PH-WC" else "TX-PRIMARY"
  oldlines += [f"**Inherited WC:** zero independent tile purchase; entire LEVEL allocation included in {parent}. Parent flat Cortar wall rate is NOT a WC floor price. Owner final floor yet unselected."]
 oldlines += ["**Constraints:** Actual current vendor stock/ETA/lot and all alternate full-room pricing remain UNKNOWN; original 15% waste already in historical gross. Porcelanosa previous Fullerton invoice PDFs are unread, so no transferable $/SF quote; no false discount. Only Elm original exact products have actual job rates. Original no-outreach rule enforced.",
 "Evidence: research/products/R023_1529_JOB_ELM_TRADE_QUOTE_EVIDENCE_20260904.md. This addendum is source-only, does not modify signed older vendor comparisons, accepted champion or procurement approvals."]
 cmp.write_text("\n".join(oldlines)+"\n",encoding="utf8",newline="\n")
 bb=cmp.read_bytes();files[str(cmp.relative_to(R)).replace("\\","/")]={"sha256":hashlib.sha256(bb).hexdigest(),"bytes":len(bb)}
 prior=R/"deliverables/r023-owner-13-porcelanosa-policy-NOT-APPROVED"/(rid+".md")
 oldbody=prior.read_text(encoding="utf8")
 latest=oldbody.replace("— 2026-11-07 R023 UPDATE / NOT APPROVED","— 2026-11-07 R023 TRADE-PRICED REVIEW / NOT APPROVED")
 prior_bad="Porcelanosa REPLACES Platform, and historical trade price file inputs/TRADE_QUOTES.md is still absent."
 prior_good="Porcelanosa REPLACES Platform. inputs/TRADE_QUOTES.md is now available with 2026-09-04 same-job Elm trade prices; original source economics are confirmed where product matches."
 latest=latest.replace(prior_bad,prior_good)
 note=(f"**Trade-price priority (same-job owner export):** {quote[0]} **USD {quote[1]:.2f}/SF** from 2026-09-04 Elm job quote, 1529 thread 1a068e80c92c255f; exact quoted product only, not a new purchase rate for Soho/Noho." if quote else "**Trade price:** WC not independently bought; inherit Primary LEVEL floor exactly once, no standalone source rate.")
 latest=latest.replace("**Old Town property/photo comparison:**",note+"\n\n**Old Town property/photo comparison:**")
 latest += f"\n**Current item-specific trade appendix:** [R023 new quote comparison](../../rooms/{rid}/vendor_comparison_R023_trade_price_addendum.md). Current substitute costs, owner approvals, native areas and Chicago lots remain NULL; no final champion is asserted.\n"
 owner=OUT/(rid+".md");owner.parent.mkdir(parents=True,exist_ok=True)
 owner.write_text(latest,encoding="utf8",newline="\n")
 by=owner.read_bytes();files[str(owner.relative_to(R)).replace("\\","/")]={"sha256":hashlib.sha256(by).hexdigest(),"bytes":len(by)}
assert len(files)==27
parents={}
for name in ("state/ROUND021_BLIND_ROLE_NEUTRAL_FIX1_SOURCE_PREPARED_NOT_SUBMITTED.json","state/ROUND023_THREE_DURAVIT_TUB_LFT_PRELIMINARY_NOT_SUBMITTED.json","state/ROUND023_ALLROOM_UPDATED_VENDOR_OWNER_PREVIEWS_SHA.json"):
 by=(R/name).read_bytes();parents[name]={"sha256":hashlib.sha256(by).hexdigest(),"bytes":len(by)}
sourcebytes=SOURCE.read_bytes()
REC.write_text(json.dumps({"round":23,"type":"ADDITIVE_NEWLY_RECEIVED_1529_TRADE_QUOTES_COST_REVALIDATION","price_file":{"path":"inputs/TRADE_QUOTES.md","sha256":hashlib.sha256(sourcebytes).hexdigest(),"bytes":len(sourcebytes)},"files":files,"immutable_parents":parents,"provisional_13_owner_sheets":True,"champions_changed":False,"owner_approved":False,"procurement_release":False,"four_original_specialist_critiques":False},indent=2)+"\n",encoding="utf8",newline="\n")
print("R023 TRADE SOURCES",len(files),"new signed items; project Elm quote 2026-09-04; originals unchanged")
