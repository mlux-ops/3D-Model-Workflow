"""Additive 13-room individual buyer/render/1:1 mockup construction-ready field briefs.
No owner selection, no actual render fabricated, no existing signed record edited.
"""
from pathlib import Path
import csv,hashlib,json
from decimal import Decimal

R=Path(__file__).resolve().parents[1]
S=R/"state";D=R/"deliverables/integrated-r18-owner-sample-visual-and-shop"
assert not D.exists()
assert not (S/"ROUND014_SCORING.json").exists()
assert not (S/"ROUND015_SCORING.json").exists()
def fp(path):
 b=path.read_bytes()
 return {"sha256":hashlib.sha256(b).hexdigest(),"bytes":len(b)}
signed_r17=R/"deliverables/integrated-r17/MANIFEST.json"
assert fp(signed_r17)["sha256"]=="78c0849c14a83dba65023d7ede812181d7360d2c7cd00eaa2f8cc0e33927aac1"
rooms=json.loads((S/"ROOMS.json").read_text(encoding="utf-8"))["rooms"]
assert len(rooms)==13
D.mkdir(parents=True)

scenes={
"PH-PRIMARY":("Brizo 48in Black Onyx LINEAR + BR73480; no new niche; separate selected Duravit tub; PH-WC floor within Primary",
 "flat wet-listed Bone field versus source relief wet authorization held; selected Black Onyx linear mosaic pan","full wet wall and 48in drain","independent LEVEL vs LINEAR pan threshold/fall","separate tub, black fittings, no added niche","maker flat-v-relief chips, separate LEVEL raw lab and mosaic LINEAR raw lab, 7-18mm frame section","48in rough and liner, hex 1/4 vs 5/16 version, grout 1/8 vs 3/16, shared WC cartons"),
"PH-BATH2":("Duravit selected TUB, Hansgrohe MATTE WHITE, Sandstone niche; no tiled PAN",
 "individually wet-listed Sapphire 2x20 Glossy against Matte White and warm LEVEL floor","frontal tub surround 2x20 stacks","Sapphire/Sandstone niche back/returns and positive sill","tub flange/finish LEVEL floor door threshold","Sapphire and Sandstone maker Wet Areas chips; Matte White escutcheon, tub flange, LEVEL raw lab","59in selected tub vs 59.496in nominal alcove leaves only 0.496in before rough/flange/backer"),
"PH-BATH3":("Delta DT062412 CHROME 4in square shower POINT; PH basin and owner TUB/WALK-IN both UNSELECTED",
 "equal-status tub and walk-in owner alternatives with independently wet-listed Sapphire vs unlisted Opal and existing Sandstone niche","TUB branch with no selected tub SKU, new tub waste required","WALK-IN branch with Delta 4-plane square POINT pan if owner signs","Chrome shower/vanity with basin placeholder UNSELECTED","Sapphire versus Opal individual wet evidence; Sandstone; LEVEL raw lab; distinct conditional POINT pan lab and Delta liner shop","No shower point drain as tub waste, no guessed shower center, no duplicate full floor/PAN gross"),
"PH-BATH4":("Selected Brizo BT062415-BNX 4in SQUARE POINT WALK-IN, never tub",
 "source Ribbed/Caviar wet-unlisted vs flat Bone/Soho Black individually wet-listed conditional fields","straight wall relief versus flat side-by-side not as approval","niche edge, Black Onyx trim and glass","four-plane POINT pan/LEVEL separation and drain elevation","flat Bone and Ribbed maker wet status distinct, Soho Black/Caviar distinct, raw LEVEL and POINT lab","Owner 35SF vs old 27SF, Soft/AntiSlip, Ribbed 107.2SF/unit potential 214.4SF source vendor total audit only"),
"PH-POWDER":("DRY Earth Lines vanity tile wall; wood floor, Brizo Luxe Gold wall faucet",
 "Earth Lines dry wall and verified flat faucet escutcheon support","front vanity/mirror and wall faucet","grazing side light showing tile gauge and joint","dry tile-to-wood base; no shower pan","Earth Lines 1:1 dry panel, grout, Luxe Gold and wall support, wood sample","No bath wet LEVEL tile or PAN; real basin/faucet backing and trim LF only"),
"PH-WC":("Inherited PH Primary LEVEL floor including WC source gross; no independent order or PAN",
 "floor/door threshold and matching Primary grout","Primary-to-WC threshold","toilet flange/perimeter soft joint","full WC LEVEL continuity, no shower floor","same Primary LEVEL raw wet lab and calibrated finish, no new SKU","No double cartons or independent WC pan; threshold field verification"),
"TX-PRIMARY":("Brizo 48in Black Onyx LINEAR + BR73480, no niche; shared TX WC LEVEL and separate tub",
 "wet-listed flat Clay vs unlisted Ribbed, separate LEVEL and LINEAR pan","flat Clay shower wall/ceiling with real openings","linear drain slope and grout/metal flush","Duravit separate tub and WC threshold matching LEVEL","flat Clay versus Ribbed Wet Areas evidence, raw LEVEL and LINEAR pan independently, BNX grate","7-18mm tile-in frame vs hex current 5/16 historical 1/4, grout conflict, BR73480 waterproof"),
"TX-BATH2":("Selected Duravit TUB Hansgrohe CHROME; sink/basin UNSELECTED; NO shower tiled PAN",
 "Copper/Sandstone individual maker wet PASS with Clay Soft historical versus conditional White Elect EL30 bath LEVEL","Copper vertical vs horizontal 2x20 module on W1","Sandstone niche and Chrome shower escutcheon on tub surround","White Elect/Clay bath LEVEL and door","Copper/Sandstone Wet Areas evidence; EL30 Mexico 12x24 LEVEL and raw lab, Chrome, tub flange","No basin selection, EL30 maker Target not raw DCOF, correct actual grout and vendor lot"),
"TX-BATH3":("Brizo Roccesco Black Onyx and BT062415-BNX 4in square POINT; owner TUB/WALK-IN UNSELECTED",
 "Emerald and Sandstone wet-listed wall/niche, split tub and walk-in narrative without choosing owner program","source tub alcove and owner TUB option UNSELECTED model/waste","if WALK-IN: Brizo 4-plane POINT slope/glass/membrane","Emerald/Sandstone/BNX and LEVEL boundary","Emerald/Sandstone Wet Areas chips, LEVEL raw lab, conditional separate 1.5 hex POINT raw lab, selected Brizo grate","Brizo shower POINT is not tub waste; avoid unselected BT062418/BR62400 rough and PH basin clause"),
"TX-BATH4":("Selected Duravit TUB Hansgrohe MATTE WHITE; no tiled PAN",
 "wet-listed flat Cortar Charcoal tub field, conditional Soho Ivory wet niche versus original Clara Caviar unlisted; Bone vs KC04 LEVEL","flat 24x48 Charcoal orthogonal with true tub opening","Soho Ivory/Caviar niche 2x10 vs 2x8 and Matte White trim","Bone/KC04 12x24 bath LEVEL floor, no shower PAN","flat Charcoal, Soho Ivory Wet Areas evidence, Caviar individual permission missing, KC04 USA/grout 3/16 and raw LEVEL lab","Do not copy TX2 Chrome/unselected basin; tub waste/flange, edges and net niche return"),
"TX-POWDER":("Dry Haze Camel/Wheat vanity tile wall 70:30 direction; WOOD FLOOR",
 "two 70:30 dry-wall arrangement studies against real mirror/basin","dry vanity orthographic full elevation","70:30 split/edge and mirror backing crop","wood-floor/dry-tile transition","Haze Camel and Wheat chips, calibrated grout, wood and actual faucet metal","No tiled wet floor or shower pan; owner palette still unsigned"),
"TX-POWDER2":("Dry Indigo Edge 6x6 vanity wall, owner BASIN UNSELECTED, Tecturis 73072341 DECK-mounted, WOOD FLOOR",
 "Indigo Edge 6x6 module against real deck faucet and basin placeholder, no fictitious wall faucet","front vanity with basin volume marked UNSELECTED","deck faucet/counter hole coordination from above","wall-to-wood toe/base joint","Indigo Edge 6x6 1:1, deck faucet actual finish, counter and basin candidates unsigned","Do not choose sink model or drill holes; no wall-mount faucet or tiled wet PAN"),
"TX-WC":("Inherited TX Primary LEVEL floor within original Primary gross; no separate order or PAN",
 "one continuous shared Primary finish","WC-to-Primary door threshold","flange/soft perimeter inspection","wide WC existing LEVEL only","same TX Primary tile/grout/raw LEVEL lab, soft joint and metal threshold","No separate WC cartons or PAN, no repeated 15 percent waste")
}
assert set(scenes)=={r["id"] for r in rooms}
matrix=[]
for room in rooms:
 rid=room["id"]
 fixed,design,c1,c2,c3,samples,hold=scenes[rid]
 geo=json.loads((R/"rooms"/rid/"geometry.json").read_text(encoding="utf-8"))
 original=sum((Decimal(str(x.get("extended_quote_cost_usd_per_unit") or 0)) for x in room.get("carried_tile_rows",[])),Decimal(0))
 widths="; ".join(x["id"]+" "+str(round(x["length"]["value"]*12,3))+"in W and "+str(round(x["tiled_height"]["value"]*12,3))+"in assumed tiled H" for x in geo.get("tiled_walls",[]))
 if not widths:widths="Source-only; no separate W tiles or verified model"
 b=[
 "# "+rid+" — R18 buyer 1:1 sample, three-view source-faithful render and GC field-shop brief","",
 "**NOT OWNER APPROVED, NOT A CERTIFIED 1529 DRAWING, NOT A PURCHASE/QUOTE OR A PHYSICAL SAMPLE ORDER.** This document is an independent supplementary instruction to signed R17, not a change to v4, plumbing, R014/R015 blind source or source pricing.","",
 "## Existing owner fixture/program controls","",fixed,"",
 "## Owner-facing conditional design language","",design,"",
 "## Three actual visualization camera briefs — NOT GENERATED RENDERS","",
 "1. Camera A — "+c1+". Use only true field-surveyed geometry, level, actual glass/valve and selected fixture form; no invented window or wall placement.",
 "2. Camera B — "+c2+". Include dimension legend only after correct 1529 model identity and real rough field measures; where source is unverified, label it explicitly PROVISIONAL.",
 "3. Camera C — "+c3+". Show material contrasts in both neutral daylight and warm architectural light without claiming physically accurate glazing or approved tile SKU.",
 "",
 "## Exact 1:1 sample and physical mockup components — not ordered","",samples,"",
 "Label every actual approved physical swatch with manufacturer name, SKU, color, size, finish and caliber. Place real selected plumbing/escutcheon beside tile, choose actual grout/soft joint and trims by approved maker, include wet/slope/tub flange section as appropriate. Order/sample authorization remains FALSE.",
 "",
 "## Provisional drawing geometry; field measurements not certified","",
 "Drawing source room plan "+str(geo["floor_area"]["value"])+" SF. Source W studies: "+widths+". Correct native open model is 1527, not authenticated 1529. Treat each source width and area as a preliminary planning dimension only.",
 "",
 "Field estimator: survey actual face width/height, tile joint/caliber, rough valve coordinates, door/window opening/jamb/sill, niche aperture (subtract displaced field once) and niche back/returns/sill (add once), finished exposed edge LF, movement/soft joints, tub rim or shower glass, threshold, drain center and wet pan/level boundary. Source gross SF ALREADY includes prior 15% cut allowance once; neither repeat source waste nor duplicate full LEVEL as shower PAN. Conditional full cases remain NULL until verified same-SKU case yield.",
 "",
 "## Room-specific design/manufacturer/installer holds","",hold,"",
 "Any WET wall or niche needs its OWN individual maker Wet Areas application on exact item/color/finish. LEVEL bath tile requires exact RAW NUMERIC measured wet DCOF laboratory record. An actual LINEAR or POINT shower PAN requires a separately measured exact small-format PAN raw lab and compatible slope/membrane/rough/flood section. Daltile Target, Emser >=0.60, Glazzio >0.50 are NOT individual raw lab results. No tiled PAN for the three selected Duravit TUB-only rooms; no shower floor in dry powders; WC floor inherited from Primary.",
 "",
 "## Separate owner, architect, GC and procurement signatures","",
 "| Checkpoint | Required signed evidence | Current |",
 "|---|---|---|",
 "| Owner design/program/finish and room cap | Signed color/size/joint, actual program choices and selected basin where held | **NULL — not approved** |",
 "| Architect/GC geometry and sample shop | Verified 1529 project identity, actual measured 1:1 W cuts/trim/niche and raw wet manufacturer files | **NULL — not accepted** |",
 "| GC installer/plumber | Selected tub or drain rough, manufacturer-matched waterproofing, flood/leak inspection, live lot/cartons and installed bid | **NULL — not accepted** |",
 "| Purchasing | Current dated actual Chicago exact-SKU vendor offer/ETA/stock, signed complete GC installed budget and owner PO | **FALSE — no release** |",
 "",
 "## Evidence pointers","",
 "- rooms/"+rid+"/geometry.json and plumbing.json, state/OWNER_FEEDBACK.md, historic v4 plus separate R17 13/27/65/25/lab outputs.",
 "- 14 listing entries = nine distinct buildings, 405 W Armitage entries ONE, Old Town preferred, adjacent Lincoln Park/Gold Coast secondary, PH $2.8M / TX $2.7M target, no authenticated competitor tile photos.",
 "- Historic tile material per copy "+str(original)+" USD from original source; two copies per room in four-unit $23,572.44 material total; does NOT equal owner room cap or installed offer.",
 "",
 "**No owner, manufacturer, field/GC or purchase release.**"
 ]
 fn=rid+"_OWNER_1TO1_SAMPLE_RENDER_SHOP_BRIEF.md"
 (D/fn).write_text("\n".join(b)+"\n",encoding="utf-8")
 matrix.append({"room":rid,"status":room["status"],"room_source_material_per_copy_usd":str(original),
   "two_copy_historic_material_usd":str(original*2),"brief_file":fn,
   "three_provisional_camera_views":"A "+c1+"; B "+c2+"; C "+c3,
   "owner_program_fixture_identity_preserved":fixed,"sample_kit_conditional":samples,
   "actual_1529_dimensions_verified":"FALSE","actual_raw_wet_lab_proof":"FALSE",
   "sample_order":"FALSE","owner_approval":"FALSE","architect_approval":"FALSE",
   "GC_shop_acceptance":"FALSE","installed_quote_id":"","owner_cost_cap":"",
   "procurement_release":"FALSE"})
assert len(matrix)==13
assert sum(Decimal(x["two_copy_historic_material_usd"]) for x in matrix)==Decimal("23572.44")
with (D/"R18_13_ROOM_SAMPLE_RENDER_OWNER_GC_SIGNATURE_MATRIX.csv").open("w",encoding="utf-8",newline="") as f:
 w=csv.DictWriter(f,fieldnames=list(matrix[0]));w.writeheader();w.writerows(matrix)
(D/"START_HERE_R18.md").write_text("# R18 owner 1:1 sample, rendering truth and GC shop review\n\nIndividual 13-room briefs each provide three camera narratives and 1:1 sample kit requirements without fabricating as-built room geometry, raw lab or selected owner approvals. The matrix has 13 separate owner, architect, GC and purchasing gates; all remain FALSE. Prior R12-R17 signature chain and R014/R015 authentic blind board are immutable. No actual samples or rendered images were created.\n",encoding="utf-8")
files=sorted(p for p in D.iterdir() if p.is_file())
assert len(files)==15
manifest={"as_of":"2026-11-06","kind":"independent additive 13-room 1to1 sample, 39 camera brief and shop/owner signature kit",
"rooms":13,"camera_briefs":39,"signature_rows":13,
"historical_four_unit_material_usd":"23572.44","original_15pct_waste_embedded_once":True,
"previous_R17_manifest_sha256":fp(signed_r17)["sha256"],
"R014_source_sha256_unchanged":fp(S/"ROUND014_SUBMISSION.json")["sha256"],
"R015_source_sha256_unchanged":fp(S/"ROUND015_SUBMISSION.json")["sha256"],
"actual_render_images":False,"actual_samples_ordered":False,"actual_1529_model_verified":False,
"owner_approval":False,"GC_release":False,"procurement_release":False,
"R014_scoring":None,"R015_scoring":None,
"outputs":{p.name:fp(p) for p in files}}
(D/"MANIFEST.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
assert all(fp(D/n)==sig for n,sig in manifest["outputs"].items())
print("PASS R18 13 individualized buyer mockup/render/shop briefs (39 source-truth views), 13 owner+architect+GC+purchase gates, original $23572.44 once waste, 15 outputs signed, no owner/lab/quote/release")
print("R18_MANIFEST_SHA",fp(D/"MANIFEST.json")["sha256"])
