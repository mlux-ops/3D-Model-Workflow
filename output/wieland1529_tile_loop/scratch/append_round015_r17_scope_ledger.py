"""One-time auditable R015 pre-dispatch/R17 package progress log; R014 still unscored."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1]
S=R/"state"
LEDGER=S/"LEDGER.md"
HEADER="## Round015 substantive Triplex TUB pre-dispatch source and R17 entire 13-room owner/GC evidence-to-shop package — 2026-11-06"
assert HEADER not in LEDGER.read_text(encoding="utf-8")
def fp(p):
 b=p.read_bytes()
 return {"sha256":hashlib.sha256(b).hexdigest(),"bytes":len(b)}
src=S/"ROUND015_SUBMISSION.json"
r17=R/"deliverables/integrated-r17/MANIFEST.json"
assert fp(src)["sha256"]=="ff0339025e5302b101958ff08da8f2b538bc11c4b77d204b6fc7db031c75e835"
assert fp(r17)["sha256"]=="a34a381bcc9072836130e17141851c80b8215e15d464fd7b8406bdb0b8711f41"
d=json.loads(src.read_text(encoding="utf-8"))
m=json.loads(r17.read_text(encoding="utf-8"))
assert d["critic_dispatch"]=="NOT_DISPATCHED" and d["weighted_scoring"] is None
assert m["room_count"]==13 and m["source_material_rows"]==27 and m["source_trade_actions"]==65
assert m["source_wall_elevations"]==25 and m["original_historic_material_usd_four_unit"]=="23572.44"
assert not m["owner_approval"] and not m["procurement_release"]
assert not (S/"ROUND014_SCORING.json").exists()
assert not (S/"ROUND014_CRITIC_COLLECTION.json").exists()
assert not (S/"ROUND015_CRITIC_DISPATCH.json").exists()
assert not (S/"ROUND015_SCORING.json").exists()
body=chr(10)+HEADER+chr(10)+chr(10)
body+="- **R014 original independent worker-9 DESIGN failure:** agents status reported worker-9 FAILED after two browser revival attempts were not claimed. Six authentic independent MARKET/BUILD/COST reports (56 criteria, 12 means, 191 local evidence links) exist; two original DESIGN reports absent. No replacement worker, fabricated opinions or weighted scoring. Original R014 source and R16 independent FIX3/addendum CONTINUE receipts untouched; must recover original seat or obtain explicit governance resolution before a full collection. Owner PH/TX Bath3 program and PH basin remain UNSELECTED."+chr(10)
body+="- **13-room reassessment and R015 coherent focus:** TX-BATH2 + TX-BATH4 actual Duravit tub programs (no shower PAN), R012 blocked and maker/installation/procurement deficits independently closable without guessing Bath3 owner decisions. TX Bath2 preserve Copper/Sandstone wet maker and Hansgrohe CHROME, owner basin unselected; new White Elect EL30 12x24 LEVEL vs original Clay Soft. TX Bath4 retain flat Charcoal, Hansgrohe MATTE WHITE, owner selected tub; new Grey Koncrete KC04 LEVEL and wet-listed Soho Ivory niche vs original Bone Soft/Caviar wet-unlisted. Neither floor maker Target is actual SKU raw wet DCOF; no owner approval or live Chicago quote. Four balanced neutral packets and two PRIME/Reviewer-only _key maps frozen; R015 source SHA "+fp(src)["sha256"]+", shared research "+d["shared_neutral_maker_research_sha256"]+". No critics dispatched or scores; pre-dispatch Reviewer verdict pending."+chr(10)
body+="- **Predispatch fixes BEFORE any reviewer or worker:** candidate relative-path level and malformed newline from initial author corrected with state/ROUND015_PREDISPATCH_SOURCE_LINK_FIX.json; two private key JSON terminal newlines corrected and signed with ROUND015_PRIVATE_KEY_JSON_FIX.json; candidate-readable common maker research role disclaimer removed and source re-signed via ROUND015_SHARED_RESEARCH_ROLE_NEUTRALITY_FIX.json. Post-repair source and six/owner package verifier PASS four candidate frozen SHA, 32 local relative links, source role neutrality and private keys parseability. No earlier scored candidate changed."+chr(10)
body+="- **R17 substantive NEW full-program package:** signed manifest "+fp(r17)["sha256"]+"; seven outputs including 13 owner/GC release gates, 27 original quote/conditional carton evidence rows, 65 original trade-owned closure evidence requests, 25 provisional elevation field-measured opening/niche/cut/trim/movement controls, 13 program-dependent wet WALL/NICHE vs LEVEL/PAN exact measured raw lab gates, and a new full 13-room GOOD/BETTER/BEST / sample/render/shop/pricing decision book. R17 is ADDITIVE to immutable R12-R16 and unscored R014, not a new release. Independent exact 27 material row source sum $23,572.44 (two PH/two TX) and historic gross includes 15% waste ONCE. Two excluded/unpriced Primary niche source references NO ORDER; shared WC no duplicate floor; wood powder floors no imaginary shower tests, actual Duravit tubs no tiled PAN, Bath3 owner branch conditional."+chr(10)
body+="- **Gates/procurement controls:** precise manufacturer SKU/finish Wet Areas permissions distinct from targets/bounds; original Opal, relief Reed/Ribbed, Clara Caviar unlisted remain holds; Daltile EL30/KC04 Target ≥0.42 is NOT raw measured lab. Need correct native 1529 (open 1527), physical W/valve/edge/niche/POINT/LINEAR drain sections and material sample, actual Chicago lot/carton/ETA, verified current landed + installed GC quote, signed owner caps and owner/GC releases; all new R17 release fields FALSE. Original PH/TX Primary Brizo 48in LINEAR + BR73480/no extra niches, PH4 4in Brizo POINT walk-in, PH2/TX2/TX4 Duravit tubs, PH3/TX3 unresolved TUB/WALK-IN held. No vendor, emails, Revit/Smartsheet writes or orders."+chr(10)
with LEDGER.open("a",encoding="utf-8",newline="") as h:h.write(body)
print("PASS R015 neutral source and R17 13-room new SHA signed evidence package logged; R014 6/8 with worker-9 failed and no scoring")
print("R015_SHA",fp(src)["sha256"])
print("R17_SHA",fp(r17)["sha256"])
