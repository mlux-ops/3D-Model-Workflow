"""Additive R023 3-room Duravit-tub cohort; selection only; no previous source edits."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
S={r["id"]:r for r in json.loads((ROOT/"state/ROOMS.json").read_text(encoding="utf8"))["rooms"]}
OFFERS={
"PH-BATH2":{
"A":("ELM Tones Sapphire 2x20 Glossy","https://www.elmsurfaces.com/product/sapphire-tones","ELM Sandstone 2x20 Glossy","https://www.elmsurfaces.com/product/sandstone-tones","Luxe Sand 24x24 Matte", "101317949","Color-rich sapphire surround, warm Sandstone niche and pale matte large-format floor."),
"B":("ELM Soho Ivory 2x10 Glossy","https://www.elmsurfaces.com/product/soho-ivory","ELM Sandstone 2x20 Glossy","https://www.elmsurfaces.com/product/sandstone-tones","Riviera Oat 24x48 Matte","101487775","Warm ivory tub walls with discrete Sandstone niche and quiet travertine-look 24x48 LEVEL floor.")},
"TX-BATH2":{
"A":("ELM Tones Copper 2x20 Glossy","https://www.elmsurfaces.com/product/copper-tones","ELM Sandstone 2x20 Glossy","https://www.elmsurfaces.com/product/sandstone-tones","Luxe Sand 24x24 Matte","101317949","Copper-colored wet wall picks up warmth against Chrome, pale 24x24 level tile keeps balanced lightness."),
"B":("ELM Noho Ivory 2x10 Matte","https://www.elmsurfaces.com/product/noho-ivory","ELM Sandstone 2x20 Glossy","https://www.elmsurfaces.com/product/sandstone-tones","Riviera Oat 24x48 Matte","101487775","Soft ivory matte wall and quieter Sandstone niche offset warm beige 24x48 LEVEL floor.")},
"TX-BATH4":{
"A":("ELM Cortar Charcoal FLAT 24x48 Soft","https://www.elmsurfaces.com/product/cortar-charcoal","ELM Soho Ivory 2x10 Glossy","https://www.elmsurfaces.com/product/soho-ivory","Luxe Sand 24x24 Matte","101317949","Charcoal flat wet wall contrasts a separate glossy pale niche and large ivory matte floor."),
"B":("ELM Cortar Charcoal FLAT 24x48 Soft","https://www.elmsurfaces.com/product/cortar-charcoal","ELM Soho Black 2x10 Glossy","https://www.elmsurfaces.com/product/soho-black","Riviera Oat 24x48 Matte","101487775","Quiet charcoal surround with deeper black glossy niche and warmer travertine-look level floor.")}}
FLOORS={
"101317949":{"url":"https://www.flooranddecor.com/porcelain-tile/luxe-sand-matte-porcelain-tile-101317949.html","size":"24x24","thickness":"8mm","finish":"matte rectified","wet":"DCOF >=0.42, Shower Floor YES and Bathroom Floor YES","low":3.49,"high":3.49},
"101487775":{"url":"https://www.flooranddecor.com/porcelain-tile/riviera-oat-matte-porcelain-tile-101487775.html","size":"24x48","thickness":"8mm","finish":"matte rectified","wet":"DCOF >=0.42, Shower Floor YES and Bathroom Floor YES","low":3.99,"high":4.39}}
FIX={
"PH-BATH2":"Selected Duravit tub, Hansgrohe MATTE WHITE; NO tiled PAN. No unselected basin added.",
"TX-BATH2":"Selected Duravit tub, Hansgrohe CHROME; basin UNSELECTED; NO tiled PAN.",
"TX-BATH4":"Selected Duravit tub, Hansgrohe MATTE WHITE; NO tiled PAN; Hansgrohe thermostat/diverter compatibility remains separately held."}
evidence=ROOT/"research/products/R023_PORCELANOSA_REPLACED_PLATFORM_AND_LFT_TUB_LEVEL_SOURCE.md"
receipt=ROOT/"state/ROUND023_THREE_DURAVIT_TUB_LFT_PRELIMINARY_NOT_SUBMITTED.json"
assert not evidence.exists() and not receipt.exists()
for rid in OFFERS: assert not (ROOT/"rooms"/rid/"board/round-023").exists()
evidence.write_text("""# R023 four permitted vendors, large LEVEL floor and Duravit tub selections

Research observed November 6–7, 2026. Newest owner feedback authorizes Elm Surfaces, MSI Surfaces, Porcelanosa and Floor & Decor only. Platform, Daltile and Emser are NOT authorized future champions. Original prior signed alternatives remain historical, not dispatchable.

Floor & Decor **Luxe Sand SKU 101317949** https://www.flooranddecor.com/porcelain-tile/luxe-sand-matte-porcelain-tile-101317949.html : 24x24 nominal/23.70 actual, matte 8mm rectified, wet DCOF >=0.42, Shower Floor YES / Bathroom Floor YES, observed non-Chicago online $3.49/SF, 15.52SF/$54.08 carton.

Floor & Decor **Riviera Oat SKU 101487775** https://www.flooranddecor.com/porcelain-tile/riviera-oat-matte-porcelain-tile-101487775.html : 24x48 nominal/23.58x47.28 actual, matte 8mm rectified, wet DCOF >=0.42, Shower Floor YES / Bathroom Floor YES, public two storefront price observations $3.99–$4.39/SF, box 16SF/$63.84–$70.24. Neither guarantees Chicago dye lot, lead, stock or project price. Proposed 1/8-inch grout a design assumption until maker/sample verified.

**Porcelanosa official U.S. catalog** https://store.porcelanosa.com/us/search/bottega : Bottega Caliza 23x47 manufacturer item 100280172 $5.98/SF and 23x23 manufacturer item 100324943 $10.95/SF posted. This is a real allowable price/appearance comparison, NOT an approved bath LEVEL or PAN selection: exact per-SKU published wet DCOF >=0.42 and wet-floor application technical sheet still unavailable. Do not infer rating from the Ant. variant or 20mm paver.

**ELM individual wet WALL/NICHE product pages**: Tones Sapphire https://www.elmsurfaces.com/product/sapphire-tones; Copper https://www.elmsurfaces.com/product/copper-tones; Sandstone https://www.elmsurfaces.com/product/sandstone-tones; Soho Ivory https://www.elmsurfaces.com/product/soho-ivory; Soho Black https://www.elmsurfaces.com/product/soho-black; Noho Ivory https://www.elmsurfaces.com/product/noho-ivory; Cortar Charcoal FLAT https://www.elmsurfaces.com/product/cortar-charcoal. Use only individual Wet Areas listed finishes, never inherit from unlisted ribbed or Caviar colors. Elm replacement quote currently UNKNOWN.

inputs/TRADE_QUOTES.md was absent at live R023 inspection. Price hierarchy: job 25-006 trade quote, then dated earlier-job quote (older than 12 months indicative only), then current manufacturer/store retail. No Gmail/vendor outreach and no invented trade prices. Three chosen Duravit TUB rooms have no tiled shower PAN; preferred 24in+ floor is LEVEL only. Room geometry is prior drawing-derived and still requires native read-only Revit receipt/actual element corroboration. Historic original waste 15% once and total $23,572.44 unchanged.
""",encoding="utf8",newline="\n")
files={}
b=evidence.read_bytes();files[str(evidence.relative_to(ROOT)).replace("\\","/")]={"sha256":hashlib.sha256(b).hexdigest(),"bytes":len(b)}
for rid,opts in OFFERS.items():
 room=S[rid];assert room["status"]=="blocked"
 rows={x["surface"]:x for x in room["carried_tile_rows"]}
 for letter,(wall,wallurl,niche,nicheurl,floortitle,sku,design) in opts.items():
  d=FLOORS[sku];fl=rows["floor"];gross=fl["qty_sf_per_unit"]
  public=f"public online {d['low']:.2f}–{d['high']:.2f} USD/SF, indicative original gross floor spend {gross*d['low']:.2f}–{gross*d['high']:.2f} USD per copy"
  body=f"""# {rid} — neutral R023 option {letter} — eligible-vendor tile design only

This specification is a design option for independent evaluation; model geometry, manufacturer compliance, procurement terms and owner approval must be verified.

**Selected plumbing/program:** {FIX[rid]}

**WET TUB WALL:** [{wall}]({wallurl}), exact individual manufacturer Wet Areas WALL listing for this finish and color; no automatic approval transferred from related relief/tile format.

**Separate WET NICHE:** [{niche}]({nicheurl}), individual maker Wet Areas WALL listing; niche exact location/edge grout and matching finish remain conditional, owner program unchanged.

**BATH LEVEL only:** [Floor & Decor {floortitle} exact SKU {sku}]({d['url']}), {d['size']} {d['thickness']} {d['finish']}, published {d['wet']}. NO tiled PAN because the selected fixture is a Duravit tub; no POINT/LINEAR drain substitution. Grout 1/8-inch is an owner review starting point, not a manufactured requirement.

**Design direction:** {design}

**Historical original gross and price per room copy (15% waste included ONCE):** wet WALL {rows['wall']['qty_sf_per_unit']:.2f}SF @ {rows['wall']['quoted_rate_usd_per_sf']:.2f} USD/SF; NICHE {rows['accent']['qty_sf_per_unit']:.2f}SF @ {rows['accent']['quoted_rate_usd_per_sf']:.2f} USD/SF; bath LEVEL {gross:.2f}SF @ {fl['quoted_rate_usd_per_sf']:.2f} USD/SF. Carried original room material {room['carried_quote_material_subtotal_usd_per_unit']:.2f} USD/copy, two copies. New FLOOR screen **{public}**: original gross x variable public store rate only, NOT a new box-rounded/installed quote or assured saving. ELM wall and niche price/Chicago availability UNKNOWN; original carried $/SF is not the substitute's price. No owner tile budget upgrade authorized.

**Actual project geometry:** Revit native title 25-006 1527 N Wieland equals 1529 building, owner-confirmed. Element IDs and current niche/tub/floor lengths require separate successful read-only receipts; prior source dimensions cannot be certified solely by the name match. Plan cut checks and grout samples remain design decisions, not fabricated engineering.

**Old Town comp:** OT01–OT04 share one building at 405 W Armitage; OT01 dry powder-like photo confirms layered walls/contrast but NOT competing wet tub tile SKU. OT05 1849 Mohawk PH bathroom interior remains unauthenticated; actual wet tile/grout visual information UNKNOWN. Lincoln Park/Gold Coast secondary.

**Eligibility and review:** Elm specific wet WALL/NICHE and Floor & Decor exact LEVEL published wet DCOF support an application path, but current local inventory, owner selections, wall costs, tub cut layout and full 125%-budget gate remain open. Porcelanosa priced Bottega comparison has no confirmed wet DCOF, so is NOT used as qualified LEVEL. No four original critics, no independent Reviewer clearance, weighted score or procurement release; SOURCE ONLY.
"""
  pp=ROOT/"rooms"/rid/"board/round-023/candidates"/(letter+".md")
  pp.parent.mkdir(parents=True,exist_ok=True);pp.write_text(body,encoding="utf8",newline="\n")
  bb=pp.read_bytes();files[str(pp.relative_to(ROOT)).replace("\\","/")]={"sha256":hashlib.sha256(bb).hexdigest(),"bytes":len(bb)}
parents={}
for rel in ("state/ROUND018_TUB_TILE_SOURCE_PREPARED_AWAIT_BLIND_PREFLIGHT.json","state/ROUND019_TILE_ONLY_NEXT_COHORT_SOURCE_AWAIT_R018_FORMAL_CLEARANCE.json","state/ROUND021_BLIND_ROLE_NEUTRAL_FIX1_SOURCE_PREPARED_NOT_SUBMITTED.json","state/ROUND022_LARGE_FORMAT_PRIMARY_PH4_SOURCE_PRELIMINARY_NOT_SUBMITTED.json"):
 bb=(ROOT/rel).read_bytes();parents[rel]={"sha256":hashlib.sha256(bb).hexdigest(),"bytes":len(bb)}
receipt.write_text(json.dumps({"round":23,"phase":"PRELIMINARY_NOT_SUBMITTED","rooms":list(OFFERS),"source_files":files,"immutable_parents":parents,"vendor_policy":["Elm Surfaces","MSI Surfaces","Porcelanosa","Floor & Decor"],"trade_quotes_export_present":False,"owner_selected_tubs_no_tiled_pan":True,"porcelanosa_wet_dcof":None,"critic_reports":False,"independent_clearance":None,"weighted_scores":None,"champion_changes":False,"owner_approval":False,"purchase_release":False},indent=2)+"\n",encoding="utf8",newline="\n")
print("R023 THREE TUB ROOMS",len(files),"signed files, SIX neutral options; original signed R018–R022 unaffected")
