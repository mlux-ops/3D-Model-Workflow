"""Additive all-room corrected Porcelanosa-policy comparison and provisional owner pages."""
from pathlib import Path
import json,hashlib,re
R=Path(__file__).resolve().parents[1]
S={x["id"]:x for x in json.loads((R/"state/ROOMS.json").read_text(encoding="utf8"))["rooms"]}
OUT=R/"deliverables/r023-owner-13-porcelanosa-policy-NOT-APPROVED"
REC=R/"state/ROUND023_13_OWNER_PORCELANOSA_POLICY_PREVIEW_MANIFEST.json"
assert not OUT.exists() and not REC.exists()
files={}
floor_options=[
("Floor & Decor","Luxe Sand","24x24","Matte rectified, 8mm","101317949","3.49 non-Chicago online","DCOF >=0.42; Bathroom Floor and Shower Floor YES","https://www.flooranddecor.com/porcelain-tile/luxe-sand-matte-porcelain-tile-101317949.html"),
("Floor & Decor","Riviera Oat","24x48","Matte rectified, 8mm","101487775","3.99–4.39 store-dependent","DCOF >=0.42; Bathroom Floor and Shower Floor YES","https://www.flooranddecor.com/porcelain-tile/riviera-oat-matte-porcelain-tile-101487775.html"),
("Porcelanosa","Bottega Caliza","23x47","Finish/technical sheet needs individual verification","100280172","5.98 published Porcelanosa US catalog","Exact wet DCOF and shower-floor technical application UNKNOWN: CONDITIONAL, cannot be champion","https://store.porcelanosa.com/us/search/bottega"),
]
wall_base={
"PH-PRIMARY":("Cortar Bone FLAT 24x48 Soft","https://www.elmsurfaces.com/product/cortar-bone"),
"TX-PRIMARY":("Cortar Clay FLAT 24x48 Soft","https://www.elmsurfaces.com/product/cortar-clay"),
"PH-BATH2":("Tones Sapphire 2x20 Glossy","https://www.elmsurfaces.com/product/sapphire-tones"),
"PH-BATH3":("Tones Sapphire 2x20 Glossy","https://www.elmsurfaces.com/product/sapphire-tones"),
"PH-BATH4":("Cortar Bone FLAT 24x48 Soft","https://www.elmsurfaces.com/product/cortar-bone"),
"TX-BATH2":("Tones Copper 2x20 Glossy","https://www.elmsurfaces.com/product/copper-tones"),
"TX-BATH3":("Soho Emerald 2x10 Glossy","https://www.elmsurfaces.com/product/soho-emerald"),
"TX-BATH4":("Cortar Charcoal FLAT 24x48 Soft","https://www.elmsurfaces.com/product/cortar-charcoal")}
powder={
"PH-POWDER":[("ELM Earth Lines 2x10 Glossy Relief","https://www.elmsurfaces.com/product/earth-lines-vera-forma",None),("ELM Soho Ivory 2x10 Glossy","https://www.elmsurfaces.com/product/soho-ivory",None),("F&D La Belle Purity 3x12 High Gloss 100507722","https://www.flooranddecor.com/ceramic-tile/la-belle-purity-high-gloss-ceramic-tile-100507722.html","5.56")],
"TX-POWDER":[("ELM Haze Camel/Wheat 70:30 1.6x5 Matte","https://www.elmsurfaces.com/product/haze-camel",None),("ELM Noho Taupe 2x10 Matte","https://www.elmsurfaces.com/product/noho-taupe",None),("F&D La Belle Purity 3x12 High Gloss 100507722","https://www.flooranddecor.com/ceramic-tile/la-belle-purity-high-gloss-ceramic-tile-100507722.html","5.56")],
"TX-POWDER2":[("ELM Indigo Edge 6x6 Glossy Relief","https://www.elmsurfaces.com/product/indigo-edge-vera-forma",None),("ELM Soho Blue 2x10 Glossy","https://www.elmsurfaces.com/product/soho-blue",None),("F&D La Belle Antique Blue 3x12 Glossy 100507706","https://www.flooranddecor.com/ceramic-tile/la-belle-antique-blue-high-gloss-ceramic-tile-100507706.html","5.56")]}
preserve={
"PH-PRIMARY":"BNX BT0734816-BNX LINEAR 48in, BR73480 separate rough, solid BNX grate, no niches; PH-WC inherits LEVEL.",
"TX-PRIMARY":"BNX BT0734816-BNX LINEAR 48in, BR73480 separate rough, solid BNX grate, no niches; TX-WC inherits LEVEL.",
"PH-BATH2":"Duravit tub, Hansgrohe Matte White, NO tiled PAN.",
"TX-BATH2":"Duravit tub, Hansgrohe Chrome, basin UNSELECTED, NO tiled PAN.",
"TX-BATH4":"Duravit tub, Hansgrohe Matte White, NO tiled PAN; rough/diverter control hold.",
"PH-BATH3":"Hansgrohe Chrome, Delta DT062412 POINT only if WALK-IN; TUB/WALK-IN and basin UNSELECTED.",
"TX-BATH3":"Brizo BNX BT062415-BNX POINT only if WALK-IN; TUB/WALK-IN UNSELECTED.",
"PH-BATH4":"WALK-IN selected, Brizo BT062415-BNX square POINT fixed.",
"PH-POWDER":"Brizo T65722LF-GL Luxe Gold WALL with R65700, WOOD floor.",
"TX-POWDER":"AXOR One 48140991 vs Hansgrohe Metropol 32526141 WALL faucet UNSELECTED, WOOD floor.",
"TX-POWDER2":"Hansgrohe 73072341 DECK Brushed Black Chrome, basin UNSELECTED, WOOD floor.",
"PH-WC":"inherits PH-PRIMARY LEVEL floor, no independent tile/PAN.",
"TX-WC":"inherits TX-PRIMARY LEVEL floor, no independent tile/PAN."}
for rid,r in S.items():
 original=R/"rooms"/rid/"vendor_comparison.md"
 assert original.exists()
 comparison=R/"rooms"/rid/"vendor_comparison_R023_current.md"
 assert not comparison.exists()
 lines=[f"# {rid} — current owner vendor policy, 2026-11-07 (SOURCE REVIEW ONLY)",
  "ONLY ELM / MSI / PORCELANOSA / FLOOR & DECOR. This ADDENDUM supersedes Platform and Emser entries in the signed historical vendor_comparison.md. Missing product prices and eligibility remain UNKNOWN; nothing is approved.",
  f"Historic room status {r['status']}; original material per copy USD {r.get('carried_quote_material_subtotal_usd_per_unit') or 0:.2f}, 2 room copies; 15% original waste once. Historic quote is NOT new material quote.",
  f"Plumbing invariant: {preserve[rid]}",
  ""]
 if rid in powder:
  lines+=["## DRY feature WALL (three independently named products)",
          "| Item | Public USD/SF | Individual page |", "|---|---:|---|"]
  for name,url,price in powder[rid]:
   lines.append(f"| {name} | {price or 'UNKNOWN (no quote)'} | {url} |")
  lines+=["**FLOOR:** WOOD; wet-floor DCOF and shower PAN N/A.", ""]
 elif rid.endswith("-WC"):
  lines+=["## Inherited LEVEL floor only; NO independent WC tile order."]
 else:
  w,wu=wall_base[rid]
  lines+=["## WET WALL (three manufacturer-specific comparison items)",
  "| Item | Public USD/SF | Exact application | Source |","|---|---:|---|---|",
  f"| Elm {w} | UNKNOWN | Individual Wet Areas WALL listing for exact flat/finish only | {wu} |",
  "| Elm Soho Ivory 2x10 Glossy | UNKNOWN | Individual Wet Areas WALL-listed; no floor inference | https://www.elmsurfaces.com/product/soho-ivory |",
  "| F&D La Belle Purity 3x12 Glossy SKU100507722 | 5.56 non-Chicago | Vendor Shower Walls YES, floors NO | https://www.flooranddecor.com/ceramic-tile/la-belle-purity-high-gloss-ceramic-tile-100507722.html |",
  ""]
  if not rid.endswith("-PRIMARY"):
   lines+=["## Separate NICHE face (three product options)",
   "| Item | Public USD/SF | Evidence |", "|---|---:|---|",
   "| Elm Tones Sandstone 2x20 Glossy | UNKNOWN | https://www.elmsurfaces.com/product/sandstone-tones individually Wet Areas listed |",
   "| Elm Soho Black 2x10 Glossy | UNKNOWN | https://www.elmsurfaces.com/product/soho-black individually Wet Areas listed |",
   "| Elm Soho Ivory 2x10 Glossy | UNKNOWN | https://www.elmsurfaces.com/product/soho-ivory individually Wet Areas listed |",""]
  else:lines+=["NO PRIMARY NICHE by owner instruction.",""]
 lines+=["## LEVEL floor options (three actual approved-vendor items)",
 "| Vendor | Product and size | USD/SF evidence | Wet gate and source |",
 "|---|---|---|---|"]
 for vendor,name,size,finish,sku,price,wet,url in floor_options:
  lines.append(f"| {vendor} | {name} {size} {finish}, SKU {sku} | {price} | {wet}; {url} |")
 if rid in powder:
  lines.append("DRY powder with WOOD floor: FLOOR alternatives above are NOT in room scope; listed solely to keep cross-room palette comparison consistent, no WC/POWDER flooring order.")
 elif rid in ["PH-BATH2","TX-BATH2","TX-BATH4"]:
  lines.append("Selected Duravit BATHTUB: LEVEL only; NO tiled shower PAN.")
 elif rid.endswith("-WC"):
  lines.append("Parent Primary tiles govern WC once; never double-count WC.")
 else:
  lines.append("If owner selects/retains WALK-IN, same exact manufacturer-wet-listed large tile may form installer-cut PAN subject to actual native drain/geometry; Porcelanosa wet DCOF still UNKNOWN, so not eligible for PAN.")
 lines+=["","Historic signed vendor_comparison.md remains authentic but superseded as to Platform/Emser. Trade quotes export absent; no inferred Elm/MSI/Porcelanosa trade rates. Public F&D default-store rates are not verified Chicago warehouse inventory. Owner price hierarchy: this project signed trade quote > prior-job dated trade quote > public retail. No vendor outreach. OT01 is a powder-type photographic comp only; OT05 bathroom interior remains unauthenticated; Lincoln Park/Gold Coast secondary."]
 comparison.write_text("\n".join(lines)+"\n",encoding="utf8",newline="\n")
 bb=comparison.read_bytes();files[str(comparison.relative_to(R)).replace("\\","/")]={"sha256":hashlib.sha256(bb).hexdigest(),"bytes":len(bb)}
 # Existing R022 preview copied and made explicitly subordinate to the newest policy.
 prior=R/"deliverables/r022-owner-13-updated-large-format-and-powder-NOT-APPROVED"/(rid+".md")
 old=prior.read_text(encoding="utf8")
 new=old.replace("— 2026-11-06 / NOT APPROVED","— 2026-11-07 R023 UPDATE / NOT APPROVED")
 new=new.replace("New R018–R022 alternatives are UNSCORED","New R018–R023 alternatives are UNSCORED")
 # Replace stale comparison link to new current vendor table; no signed file changed.
 new=new.replace(f"../../rooms/{rid}/vendor_comparison.md",f"../../rooms/{rid}/vendor_comparison_R023_current.md")
 new=new.replace("three-plus allowed-vendor options by exact tiled surface","three-plus updated allowed-vendor options per tiled surface")
 insertion=("\n**New vendor authority:** Porcelanosa REPLACES Platform, and historical trade price file inputs/TRADE_QUOTES.md is still absent. "
            "Porcelanosa Bottega Caliza 23x47 SKU100280172 posted $5.98/SF U.S. catalog is **conditional only**, "
            "because individual published wet DCOF >=0.42 is not verified; no wet-floor/PAN approval. "
            "Floor & Decor Luxe Sand/Riviera Oat exact 24+ products retain independently published >=0.42 wet rating. "
            "For Duravit tub rooms no tiled pan is permitted. Four original critics and independent Reviewer clearance remain unavailable.\n")
 new=new.replace("\n**Old Town property/photo comparison:**",insertion+"\n**Old Town property/photo comparison:**")
 pp=OUT/(rid+".md");pp.parent.mkdir(parents=True,exist_ok=True);pp.write_text(new,encoding="utf8",newline="\n")
 b=pp.read_bytes();files[str(pp.relative_to(R)).replace("\\","/")]={"sha256":hashlib.sha256(b).hexdigest(),"bytes":len(b)}
assert len(files)==26
receipt=R/"state/ROUND023_ALLROOM_UPDATED_VENDOR_OWNER_PREVIEWS_SHA.json"
assert not receipt.exists()
parents={}
for n in ["state/ROUND021_BLIND_ROLE_NEUTRAL_FIX1_SOURCE_PREPARED_NOT_SUBMITTED.json","state/ROUND022_13_OWNER_UPDATED_NOT_APPROVED_SHA_MANIFEST.json","state/ROUND023_THREE_DURAVIT_TUB_LFT_PRELIMINARY_NOT_SUBMITTED.json"]:
 b=(R/n).read_bytes();parents[n]={"sha256":hashlib.sha256(b).hexdigest(),"bytes":len(b)}
receipt.write_text(json.dumps({"round":23,"files":files,"immutable_parents":parents,"status":"13_CURRENT_VENDOR_COMPARISONS_AND_13_PROVISIONAL_OWNER_PAGES_NOT_APPROVED","historical_total":23572.44,"room_count":13,"physical_instances":26,"source_material_rows":27,"trade_quote_export_present":False,"new_champion_changes":False,"approval":False,"purchase":False},indent=2)+"\n",encoding="utf8",newline="\n")
print("R023 OWNER/VENDOR",len(files),"SHA items: 13 comparison updates and 13 provisional single-room owner sheets")
