"""R027 Reviewer38 FIX: room-only, result-free research and controlled neutral refreeze.
Run once. Preserve frozen old signed receipt and all older source history.
"""
from pathlib import Path
import hashlib, json, re
ROOT=Path(__file__).resolve().parents[1]
OLD="state/ROUND027_FORMAL_THREE_TUB_ROOMS_SOURCE_FROZEN_PREDISPATCH.json"
NEW="state/ROUND027_PREDISPATCH_FIX2_ROOM_ONLY_RESEARCH_REFREEZE.json"
ROOMS=("PH-BATH2","TX-BATH2","TX-BATH4")
OLD_LINK="research/products/R027_TUB_THREE_ROOM_SOURCED_ALTERNATIVES.md"
PRODS={
 "PH-BATH2": {
  "program":"Duravit selected TUB, Hansgrohe Matte White; separate Ecostat/diverter tub-spout compatibility unresolved; no tiled shower PAN",
  "wall":["Elm Tones Sapphire 2x20 Glossy | $6.95/SF same-job 2026-09-04 | individually Wet Areas WALL | https://www.elmsurfaces.com/product/sapphire-tones",
          "Elm Tones Copper 2x20 Glossy | $6.95/SF same-job | individually Wet Areas WALL | https://www.elmsurfaces.com/product/copper-tones",
          "Floor & Decor La Belle Purity 3x12 Glossy SKU100507722 | $5.56/SF non-Chicago observed public | Shower Walls YES (ceramic, floor NO) | https://www.flooranddecor.com/ceramic-tile/la-belle-purity-high-gloss-ceramic-tile-100507722.html"],
  "niche":["Elm Tones Sandstone 2x20 Glossy | $6.95/SF same-job | individually Wet Areas WALL | https://www.elmsurfaces.com/product/sandstone-tones",
           "Elm Tones Copper 2x20 Glossy | $6.95/SF same-job | Wet Areas WALL | https://www.elmsurfaces.com/product/copper-tones",
           "Elm Soho Ivory 2x10 Glossy | price on request; no matching exact 1529 quote | individually Wet Areas WALL | https://www.elmsurfaces.com/product/soho-ivory"],
  "gross":"WALL 89.70 SF, NICHE 3.67 SF provisional, LEVEL 40.20 SF, original material $920.28 per room copy, 125%-of-original comparison $1150.35"
 },
 "TX-BATH2":{
  "program":"Duravit selected TUB, Hansgrohe Chrome, basin owner UNSELECTED, no tiled shower PAN",
  "wall":["Elm Tones Copper 2x20 Glossy | $6.95/SF same-job 2026-09-04 | individually Wet Areas WALL | https://www.elmsurfaces.com/product/copper-tones",
          "Elm Tones Sapphire 2x20 Glossy | $6.95/SF same-job | individually Wet Areas WALL | https://www.elmsurfaces.com/product/sapphire-tones",
          "Floor & Decor La Belle Purity 3x12 Glossy SKU100507722 | $5.56/SF non-Chicago public | Shower Walls YES, floors NO | https://www.flooranddecor.com/ceramic-tile/la-belle-purity-high-gloss-ceramic-tile-100507722.html"],
  "niche":["Elm Tones Sandstone 2x20 Glossy | $6.95/SF same-job | individually Wet Areas WALL | https://www.elmsurfaces.com/product/sandstone-tones",
           "Elm Tones Copper 2x20 Glossy | $6.95/SF same-job | individually Wet Areas WALL | https://www.elmsurfaces.com/product/copper-tones",
           "Elm Soho Ivory 2x10 Glossy | price on request; no exact-job quote | individually Wet Areas WALL | https://www.elmsurfaces.com/product/soho-ivory"],
  "gross":"WALL 92.80 SF, NICHE 8.63 SF provisional, LEVEL 43.70 SF, original material $999.92 per copy, 125%-of-original comparison $1249.90"
 },
 "TX-BATH4":{
  "program":"Duravit selected TUB, Hansgrohe Matte White, existing Ecostat/pressure-balance diverter spout/rough compatibility held, no tiled shower PAN",
  "wall":["Elm Cortar Charcoal FLAT Soft 24x48, 9mm | $8.14/SF 2026-09-04 same-job | exact FLAT Wet Areas WALL, NOT Ribbed/Reed | https://www.elmsurfaces.com/product/cortar-charcoal",
          "Elm Cortar Clay FLAT Soft 24x48, 9mm | $8.14/SF same-job | individually Wet Areas WALL | https://www.elmsurfaces.com/product/cortar-clay",
          "Floor & Decor La Belle Purity 3x12 Glossy SKU100507722 | $5.56/SF non-Chicago public | Shower Walls YES | https://www.flooranddecor.com/ceramic-tile/la-belle-purity-high-gloss-ceramic-tile-100507722.html"],
  "niche":["Elm Tones Sandstone 2x20 Glossy | $6.95/SF same-job | individually Wet Areas WALL | https://www.elmsurfaces.com/product/sandstone-tones",
           "Elm Tones Copper 2x20 Glossy | $6.95/SF same-job | individually Wet Areas WALL | https://www.elmsurfaces.com/product/copper-tones",
           "Elm Soho Ivory 2x10 Glossy | price on request, no 1529 quote | individually Wet Areas WALL | https://www.elmsurfaces.com/product/soho-ivory"],
  "gross":"WALL 89.80 SF, NICHE 8.63 SF provisional, LEVEL 44.30 SF, original material $1320.82 per copy, 125%-of-original comparison $1651.02"
 }
}
FLOORS=[
 "Floor & Decor Luxe Sand Matte porcelain SKU 101317949, 24x24 nominal, 8mm rectified | $3.49/SF non-Chicago public, 15.52 SF/box | individual Bathroom Floor YES, Shower Floors YES, published wet DCOF >=0.42 | https://www.flooranddecor.com/porcelain-tile/luxe-sand-matte-porcelain-tile-101317949.html",
 "Floor & Decor Riviera Oat Matte porcelain SKU 101487775, 24x48 nominal, 8mm rectified | $3.99-$4.39/SF non-Chicago public, 16.00 SF/box | individual Bathroom Floor YES, Shower Floors YES, published wet DCOF >=0.42 | https://www.flooranddecor.com/porcelain-tile/riviera-oat-matte-porcelain-tile-101487775.html",
 "MSI Murcia Dune Matte porcelain NMURDUN2448, 24x48 | price on request, Chicago lot UNKNOWN | maker item-family published wet DCOF >0.42, LEVEL product comparison pending exact format/finish tech sheet | https://www.msisurfaces.com/porcelain-murcia/dune/",
 "Porcelanosa Bottega Caliza 23x47 SKU100280172 | historically observed $5.98/SF public | exact wet-floor DCOF and technical sheet UNKNOWN, NOT QUALIFIED | https://store.porcelanosa.com/us/search/bottega"
]
def fp(path):
 b=(ROOT/path).read_bytes()
 return {"sha256":hashlib.sha256(b).hexdigest(),"bytes":len(b)}
def create(path,content):
 p=ROOT/path
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open("x",encoding="utf-8",newline="\n") as f:f.write(content)
 return fp(path)
def main():
 if (ROOT/NEW).exists():raise FileExistsError("FIX2 receipt already exists")
 old=json.loads((ROOT/OLD).read_text(encoding="utf-8"))
 for block in ("neutral_candidates","prime_only_private_keys","signed_parents"):
  for path,sig in old[block].items():
   if fp(path)!=sig:raise RuntimeError("Frozen source mutated unexpectedly "+path)
 expected_card_count=6
 safe={}
 for room in ROOMS:
  p=PRODS[room]
  lines=["# "+room+" | independent maker evidence for neutral current tile comparison",
   "Observation date 2026-11-06/07. Strict room-local manufacturer product research only.",
   "**Actual selected program:** "+p["program"]+".",
   "**Wet WALL: three distinct real current-vendor options**"]
  lines+=["- "+s for s in p["wall"]]
  lines+=["**Separate wet NICHE: three distinct real current-vendor options, existing niche only; opening not yet measured**"]
  lines+=["- "+s for s in p["niche"]]
  lines+=["**Bath LEVEL: at least three real 24in-plus alternatives, item-specific qualification required**"]
  lines+=["- "+s for s in FLOORS]
  lines+=["**Price provenance:** Elm Tones $6.95/SF 2x20 8.5mm, 6.50 SF per carton. Elm flat Cortar 24x48 9mm $8.14/SF, 15.39 SF/carton, historical 10-12 weeks imported terms with 300-SF aggregate minimum. Matching Sep 04 2026 job 25-006 trade quote in inputs/TRADE_QUOTES.md. F&D publicly observed NON-CHICAGO retail rate only, not local reserved lot; MSI exact price UNKNOWN. Do not extrapolate other tiles' price.",
    "**Original material quantities gross including original 15% waste ONCE:** "+p["gross"]+". Do not multiply original gross by a further 15%. 125% comparison is strictly PROVISIONAL and not owner budget.",
    "**Applicability:** exact vendor Wet Areas listing for WALL, independent NICHE; product-specific published wet LEVEL floor DCOF >=0.42 is a threshold not a raw test number. Selected TUB has NO tiled LINEAR/POINT PAN. Grout and tile cut details need owner/installer selection.",
    "**Unresolved:** Chicago matching dye lot, carton count and ETA, delivered freight/trim/grout/mortar/tax, actual native room openings/tub rough/niche and visible <3in tile cut checks UNKNOWN. Confirmed 1527=1529 building identity does not prove geometry. No owner or procurement approval.",
    "**Market photo:** OT01 at 405 W Armitage shows only dry powder-like layered contrast; OT01-04 same building, OT05 wet bathroom photo not verified. No competitor wet tile model, grout or metal attributed.",
    "**Sources:** individual manufacturer URLs on this page, same-job inputs/TRADE_QUOTES.md, manufacturer product specifications, owner rule state/OWNER_FEEDBACK.md. Do not infer an exact inventory or price on request as a confirmed quote.",""]
  content="\n".join(lines)
  if re.search(r"(?i)R02[0-7]|ROUND0|worker-|critic-|_key\.json|champion|prior.round|previous.outcome|PH-BATH2|TX-BATH2|TX-BATH4",content.replace(room,"")):
   raise RuntimeError("Forbidden leak in "+room)
  rel="research/products/R027_"+room.replace("-","_")+"_BLIND_PRODUCT_EVIDENCE.md"
  safe[rel]=create(rel,content)
 prior="See permitted "+OLD_LINK+" for >=3 real product comparisons per surface."
 replacement="See permitted "+rel+" for three-plus room-specific product comparisons per surface."
 for letter in ("A","B"):
  path="rooms/"+room+"/board/round-027/candidates/"+letter+".md"
  text=(ROOT/path).read_text(encoding="utf-8")
  if text.count(prior)!=1:raise RuntimeError("Could not locate exact old citation "+path)
  text=text.replace(prior,replacement)
  # Preserve identical newline policy when changing the only research reference.
  with (ROOT/path).open("w",encoding="utf-8",newline="\n") as f:f.write(text)
 assert len(safe)==3
 changed={p:{"old":old["neutral_candidates"][p],"new":fp(p)} for p in old["neutral_candidates"]}
 assert len(changed)==expected_card_count
 for rel,sig in old["prime_only_private_keys"].items():
  if fp(rel)!=sig:raise RuntimeError("Key mutated "+rel)
 for rel,sig in old["signed_parents"].items():
  if fp(rel)!=sig:raise RuntimeError("Signed predecessor mutated "+rel)
 report={"round":27,"phase":"CONTROLLED_R027_PREDISPATCH_FIX2_SOURCE_REFROZEN_PENDING_FRESH_REVIEWER",
  "reason":"Independent Reviewer38 PRECISE FIX removed historical R024 outcome and other-room A/B source mapping from permitted product research access",
  "historical_formal_freeze_receipt":{"file":OLD,**fp(OLD)},
  "original_prepared_source_unchanged":True,
  "corrected_neutral_candidates_before_after":changed,
  "three_critic_safe_room_specific_research":safe,
  "prime_only_private_keys_unchanged":old["prime_only_private_keys"],
  "five_original_signed_parents_unchanged":old["signed_parents"],
  "source_access":"Blind critics may read only same-room neutral candidates/geometry/plumbing, corresponding room-safe research, other cleared global manufacturer/products/inputs/BOARD/OWNER, not multi-room outcome research",
  "independent_post_FIX_reviewer":None,"critic_dispatch":None,"weighted_score":None,"champion_changes":False,"owner_approval":False,"procurement_release":False,"global_DONE":False}
 print("FIX2 receipt",create(NEW,json.dumps(report,indent=2)+"\n"))
 print("3 room-only research, six candidate text links SHA resigned, three keys and five parents untouched")
if __name__=="__main__":main()
