"""Create thirteen new concise, provisional owner decision pages; signed R023 untouched."""
from pathlib import Path
import hashlib,json,re
R=Path(__file__).resolve().parents[1]
S={x["id"]:x for x in json.loads((R/"state/ROOMS.json").read_text(encoding="utf8"))["rooms"]}
score=json.loads((R/"state/ROUND024_AUTHENTIC_FOUR_SEAT_COLLECTION_SCORED_NO_CHAMPIONS.json").read_text(encoding="utf8"))
fresh={
"PH-PRIMARY":"R025 A Bone FLAT wet wall / Luxe Sand 24x24 LEVEL and LINEAR pan; B Bone FLAT / Riviera Oat 24x48 LEVEL and LINEAR pan. No niche; inherited PH-WC floor.",
"PH-BATH3":"R025 A wet-listed Sapphire wall/Sandstone niche/Luxe Sand 24x24 LEVEL; B Copper wall/Sandstone niche/Riviera Oat 24x48 LEVEL. POINT pan only under owner-selected WALK-IN, otherwise none.",
"PH-BATH4":"R025 A Bone FLAT wet wall/Sandstone niche/Luxe Sand 24x24 LEVEL and POINT pan; B Bone FLAT/Copper niche/Riviera Oat 24x48 LEVEL and POINT pan.",
}
nextaction={
"PH-PRIMARY":"Choose pale square vs warm travertine-look tile; verify Brizo BNX 48in LINEAR rough and solid grate, no niche, parent WC allocation and native drain/pan dimensions.",
"PH-BATH2":"R024 A ranks highest but remains blocked; validate 59in Duravit tub clear dimension, delivered $1,150.35/copy cap, Chicago lot and Hansgrohe valve/diverter compatibility.",
"PH-BATH3":"OWNER must choose TUB vs WALK-IN and basin; only WALK-IN includes Delta Chrome square POINT pan and separate 25% conditional cut-waste scenario.",
"PH-BATH4":"Preserve WALK-IN and Brizo BNX square POINT; select one wet-listed niche color, reconcile old floor 35 SF vs 27 SF and native four-plane cuts.",
"PH-POWDER":"Keep wall-mounted Luxe Gold Brizo FLW/R65700; compare relief Earth Lines against smooth Soho Ivory and F&D Purity, dry tile wall/WOOD floor only.",
"PH-WC":"Inherit eventual PH-PRIMARY LEVEL tile once; native WC room and copied floor area unverified, no independent tile spend.",
"TX-PRIMARY":"Keep Brizo BNX 48in LINEAR/rough and NO niche; compare flat Clay/large-format Riviera with possible controlled Emerald focal and Luxe floor/pan, inherit TX-WC once.",
"TX-BATH2":"R024 A ranks highest but remains blocked; owner basin UNSELECTED; verify actual Duravit tub geometry and 125% budget/Chicago lot.",
"TX-BATH3":"Owner TUB vs WALK-IN unresolved; Brizo Black Onyx square POINT only WALK-IN, no tub pan. Select Emerald vs neutral wet-wall scheme after program decision.",
"TX-BATH4":"R024 both A/B fail COST specialist minimum; preserve Matte White Hansgrohe Duravit tub, get exact Soho niche price and resolve valve/spout compatibility.",
"TX-POWDER":"Resolve selected AXOR One vs Hansgrohe Metropol WALL-mounted faucet and correct rough; then compare existing Haze Camel/Wheat to Noho Taupe and Purity; WOOD floor.",
"TX-POWDER2":"Choose basin, preserve Hansgrohe Tecturis E deck-mounted Brushed Black Chrome, compare Indigo Edge relief versus Soho Blue and Antique Blue; WOOD floor.",
"TX-WC":"Inherit TX-PRIMARY LEVEL once; confirm TX203A room placement before final quantities, no independent pan/order."
}
out=R/"deliverables/r025-13-owner-tiles-PROVISIONAL"
rec=R/"state/ROUND025_13_OWNER_SELECTION_CARDS_SHA.json"
assert not out.exists() and not rec.exists()
files={}
for rid,r in S.items():
 old=R/"deliverables/r023-owner-13-trade-price-updated-NOT-APPROVED"/(rid+".md")
 src=old.read_text(encoding="utf8")
 def get(label):
  m=re.search(r"(?m)^\*\*"+re.escape(label)+r":\*\*\s*(.*)$",src)
  assert m,(rid,label)
  return m.group(1)
 selected=fresh.get(rid,get("Surface-by-surface design direction"))
 rationale=get("Why this scheme")
 plumbing=get("Actual plumbing and owner decisions")
 if rid in fresh:
  plumbing=nextaction[rid]
 amounts=r.get("carried_quote_material_subtotal_usd_per_unit") or 0
 cap=round(amounts*1.25,2)
 decision=nextaction[rid]
 summary=""
 if rid in score["rooms"]:
  z=score["rooms"][rid]["candidates"]
  summary=(f"Four authentic blind R024 seat scores weighted: A {z['A']['weighted_arithmetic']:.2f} and B {z['B']['weighted_arithmetic']:.2f}; "
           f"A minimum-seat {z['A']['seat_minimum']:.1f}, B minimum-seat {z['B']['seat_minimum']:.1f}. "
           "No champion: full delivered budget and native cut-geometry gates UNKNOWN; do not treat ranking as acceptance.")
 elif r["status"]=="active":
  summary=f"Existing active incumbent {r['champion_id']} score {r.get('champion_score')} retained; no later four-seat compliant approval recorded."
 elif r["status"]=="seeded":
  summary=f"Source-seeded {r['champion_id']} unscored and not board-approved; parent Primary governs WC."
 else:summary="No accepted champion; latest alternatives PREPARED only and no formal critique or independent source clearance yet."
 orig=(f"Carried original ${amounts:.2f}/copy, two physical copies; 125% board cap ${cap:.2f}/copy."
       if not rid.endswith("-WC") else "Inherited WC floor, no independent purchase; original Primary source includes WC allocation.")
 text=f"""# {rid} — one-page owner decision | R025 | NOT APPROVED

**Formal status:** {r["status"].upper()}; {summary} No final owner, GC, or purchasing authorization.

**Tile scheme by surface:** {selected}

**Design logic:** {rationale} Coordinate the tile direction against actual selected fixture finish and retained room program. Manufacturer Wet Areas permission for WALL/NICHE is separate from exact FLOOR/PAN wet DCOF; wet FLOOR ratings are published thresholds >=0.42, not fabricated raw lab points.

**Plumbing and owner-only decisions:** {plumbing}

**Historic cost versus selection:** {orig} Owner's 2026-09-04 same-job Elm quote: Tones 2x20 Glossy $6.95/SF; Cortar flat Soft 24x48 $8.14/SF; Earth Lines / Indigo Edge $8.20/SF; Haze Camel/Wheat $11.93/SF where the exact product matches. F&D Luxe Sand 24x24 $3.49/SF and Riviera Oat 24x48 $3.99–$4.39/SF are online STORE-DEPENDENT observations, not Chicago quotes. Unquoted Soho/Noho rates, full cartons/freight, local stock and real cut waste remain UNKNOWN. Original source 15% waste included once; never multiply its gross again. Parent WC not billed twice.

**Old Town photo comparison:** Attributable OT01 405 W Armitage shows a powder-like room with white wainscot, patterned upper wall, dark vanity and contrasting floor, not a wet tub/pan SKU or exact grout. OT01–04 are ONE building; OT05 1849 N Mohawk has no authenticated bathroom interior photo, so tile/grout/metal claims are UNKNOWN. Use Old Town first; Lincoln Park/Gold Coast secondary.

**Next owner decision / release gates:** {decision} Actual 1527=1529 project identity is confirmed, but Revit room/door/drain element receipts and certified native cut dimensions remain outstanding. Separate LEVEL and PAN only where WALK-IN, retain selected drains, Duravit TUB rooms have NO tiled PAN. Chicago same-lot pricing and 125% complete material budget gates must be documented before approval.

**Audit references:** R024 four-seat collection and R025 preliminary PH source receipts; current per-room vendor comparison, original trade-quote export and research/comps. This sheet is **PROVISIONAL**, not a final specification or permission to order.
"""
 dest=out/(rid+".md");dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(text,encoding="utf8",newline="\n")
 b=dest.read_bytes();files[str(dest.relative_to(R)).replace("\\","/")]={"sha256":hashlib.sha256(b).hexdigest(),"bytes":len(b)}
parents={}
for rel in ("state/ROUND023_TRADE_PRICING_13_ROOM_ADDENDUM_SHA.json","state/ROUND024_AUTHENTIC_FOUR_SEAT_COLLECTION_SCORED_NO_CHAMPIONS.json","state/ROUND025_PH_THREE_ROOM_PREPARED_NOT_SUBMITTED.json"):
 b=(R/rel).read_bytes();parents[rel]={"sha256":hashlib.sha256(b).hexdigest(),"bytes":len(b)}
rec.write_text(json.dumps({"round":25,"status":"ALL_PROVISIONAL_NOT_APPROVED","files":files,"immutable_parents":parents,"rooms":13,"copies":26,"historical_rows":27,"historical_material_usd":23572.44,"champion_changes":False,"owner_approval":False,"purchase_release":False},indent=2)+"\n",encoding="utf8",newline="\n")
print("R025 owner one-page summaries",len(files),"signed, all provisional")
