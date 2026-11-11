from pathlib import Path
import json,csv,hashlib,re
R=Path(__file__).resolve().parents[1]
O=R/"deliverables/integrated-r10"
reg=json.loads((R/"state/ROOMS.json").read_text(encoding="utf-8"))["rooms"]
sub=json.loads((R/"state/ROUND010_SUBMISSION.json").read_text(encoding="utf-8"))
assert len(reg)==13 and sub["all_critic_scores"] is None and sub["phase"]=="2-board"
scored=(R/"state/ROUND010_SCORING.json").exists()
with (O/"R10_13_ROOM_SOURCE_COST_AND_RELEASE_HOLDS.csv").open(encoding="utf-8-sig",newline="") as f: roomrows=list(csv.DictReader(f))
with (O/"R10_27_ROW_BID_COMPARISON_AND_NON_ORDERABLE_GAPS.csv").open(encoding="utf-8-sig",newline="") as f: quote=list(csv.DictReader(f))
with (O/"R10_65_WORK_ITEM_OWNER_GC_EVIDENCE_CLOSURE.csv").open(encoding="utf-8-sig",newline="") as f: actions=list(csv.DictReader(f))
with (O/"R10_SOURCE_WALL_CUT_AND_TRIM_CHECKS.csv").open(encoding="utf-8-sig",newline="") as f: walls=list(csv.DictReader(f))
ids={x["id"] for x in reg}
assert len(roomrows)==len(ids)==13 and {x["room"] for x in roomrows}==ids
assert len(quote)==27 and len(actions)==65 and len(walls)==25
old={(x["id"],z["smartsheet_row_id"]):z for x in reg for z in x["carried_tile_rows"]}
assert len(old)==27 and {(z["room"],z["source_row_id"]) for z in quote}==set(old)
for q in quote:
 z=old[(q["room"],q["source_row_id"])]
 assert abs(float(q["source_gross_sf_per_copy_includes_15pct"])-z["qty_sf_per_unit"])<.0001
 assert q["release_allowed"]=="False" and q["owner_approved"]=="False"
assert sum(q["original_source_scope"].startswith("EXCLUDED") for q in quote)==2
for w in walls:
 g=json.loads((R/"rooms"/w["room"]/"geometry.json").read_text(encoding="utf-8"))
 wall=next(z for z in g["tiled_walls"] if z["id"]==w["wall"])
 assert abs(float(w["source_width_in"])-wall["length"]["value"]*12)<.002
 assert abs(float(w["source_tiled_height_in"])-wall["tiled_height"]["value"]*12)<.002
 assert w["verified"]=="False" and w["trim_sticks_orderable"]==""
for x in actions:assert x["release_allowed"]=="False" and x["owner_approved"]=="False"
for x in roomrows:
 r=next(z for z in reg if z["id"]==x["room"])
 assert abs(float(x["two_copy_old_material_usd"])-r["carried_quote_material_subtotal_usd_per_unit"]*2)<.01
 assert x["release_allowed"]=="False" and x["owner_approved"]=="False"
assert round(sum(float(z["two_copy_old_material_usd"]) for z in roomrows),2)==23572.44
assert {(r["room"],r["gate_group"]) for r in actions}=={(rid,gate) for rid in ids for gate in ("manufacturer_spec","dimensions_and_edge","floor_pan_and_drain","owner_approval","vendor_quote_and_stock")}
for rid,files in sub["candidate_files"].items():
 assert rid in ("PH-PRIMARY","PH-BATH2","PH-BATH4") and len(files)==2
 for k,c in files.items():
  b=(R/"rooms"/rid/"board/round-010/candidates"/(k+".md")).read_bytes()
  assert len(b)==c["bytes"] and hashlib.sha256(b).hexdigest()==c["sha256"]
 room=next(z for z in reg if z["id"]==rid)
 assert room["status"]=="blocked" and room["champion_id"] is None and room["owner_status"] is None
 if scored:
  assert room["round_010_submission"]["status"]=="review_complete_scored"
  assert room["board_round_010"]["status"]=="blocked" and room["owner_status"] is None and room["champion_id"] is None
 else:
  assert room["round_010_submission"]["status"]=="blind_review_pending" and room["round_010_submission"]["scores"] is None
index=["# SHB | 1529 Wieland R10 owner design, independent board and procurement-preparation pack","",
"**Authority:** owner feedback and all prior scored rounds preserved. NO owner choices, contracts, install orders or approvals have been made. Work was executed only against sourced 13-room state, drawing-derived W geometry and original manufacturer research. The currently open native Revit file is **1527 N Wieland**, not verified as the 1529 project; no source wall dimensions are certified 1529.",
"","## New physical coordination documents","",
"| Owner / GC artifact | What the contractor can do immediately, without procurement |",
"|---|---|",
"| [Complete 13-room original surface and nominal field/trim book](R10_ROOM_BY_ROOM_CONSTRUCTION_AND_PROCUREMENT_BOOK.md) | Per room original Smartsheet source rows, GOOD/BETTER/BEST, actual plumbing/fixture category, W1-W3 widths and nominal symmetric end cuts, existing waste and dry/wet classification, actual membrane/edge/threshold and sample/render decision tasks |",
"| [Exact source-to-new bid comparison, 27 lines](R10_27_ROW_BID_COMPARISON_AND_NON_ORDERABLE_GAPS.csv) | Buyer/architect can isolate missing exact replacement SKUs, current prices, lot/lead, real carton yield and wet-test certificates for each original material row; two historical Primary niches excluded |",
"| [65-item owner, manufacturer, GC and procurement release closure](R10_65_WORK_ITEM_OWNER_GC_EVIDENCE_CLOSURE.csv) | Five coordinated prerequisite categories per 13 rooms, no owner approval or purchase inferred |",
"| [25-wall source cut, trim and calibration control](R10_SOURCE_WALL_CUT_AND_TRIM_CHECKS.csv) | Drawing-based dimensions, nominal/full module and paired end sliver assessment, exposed-edge theoretical upper study, actual surveyed/joint/trim quantities explicit null |",
"| [13-room historical-cost and release ledger](R10_13_ROOM_SOURCE_COST_AND_RELEASE_HOLDS.csv) | The complete original historical four-unit material value $23,572.44, separate two non-orderable niche rows and no WC double purchase |",
"| [13 compact owner decision and presentation cards](R10_13_OWNER_DECISIONS_AND_SAMPLE_PRESENTATION_CARDS.md) | One explicit unanswered owner question per room, specific sample/cut/fixture criteria, original quoted SF and dollars, no inferred approval or purchase |",
"| [PH Bath3 and TX Bath3 owner-only tub versus walk-in design branches](R10_PH3_TX3_OWNER_PROGRAM_AND_PAN_SCOPE_BRANCHES.md) | Source-based two-program plumbing/drain/waterproof and floor-versus-pan takeoff scopes without choosing a fixture, inventing a sink or transferring original prices |",
"| [Current manufacturer exact SKU & wet evidence comparison](../../research/products/R10_EXACT_SKU_WET_USAGE_AND_CARTON_DECISION_REGISTER.md) | Exact HNC6615/HNC6715 box coverage, product-specific wet use and source discrepancies vs measured-test release criterion; Brizo/Daltile application unresolved |",
"","## New Round010 focus: three Penthouse bathrooms (blind review pending)","",
"| Room | Historical concept | Substantive conditional new floor / wet envelope | Current acceptance status |",
"|---|---|---|---|",
"| **PH Primary** | Cortar Bone Soft 24x48 level / 12x24 Anti-Slip pan in ONE historic blended ELM floor row; unlisted Reed wet accent | Wet-approved flat Bone, maker-reported HNC6615 12x24 level/WC and Prime RL21 mosaic family around existing 48-in Brizo linear; NO NICHE, actual wet pan and measured lab test held | BLOCKED, candidate scores null |",
"| **PH Bath2** | Wet-approved Sapphire walls, historical Grey Soft level floor and actual Duravit tub | Preserve Sapphire and Matte White tub package; independently study HNC6615 level field; maker >0.50 claim is NOT accepted exact numeric test | BLOCKED, candidate scores null |",
"| **PH Bath4** | Unlisted Bone Ribbed/Clara wet zone, unresolved Soft/Anti-Slip floor | Actual walk-in shower geometry, Brizo square point drain, flat Bone/Soho wet walls, HNC6615 level and HNC6715 hex pan conditional, actual pan/level split and owner 35-versus-27 SF held | BLOCKED, candidate scores null |",
"","**Scoring cadence:** six neutral candidate SHA-256/byte receipts in [ROUND010_SUBMISSION.json](../../state/ROUND010_SUBMISSION.json) are frozen with all_critic_scores null. Private mapping stays in each room _key.json and MUST NOT be revealed to independent market/design/build/cost seats. Reuse existing four seats; score only in a subsequent independent scoring turn after 12 valid critiques, all original SHA checks and hard-gate review. No premature acceptance or owner signoff.",
"","## Unchanged established program choices and holds","",
"TX Primary R009 2.61/3.45 (+0.84) blocked; TX Bath2 3.41/3.55 (+0.14) blocked; TX Bath4 2.71/3.41 (+0.70) blocked; TX Bath3 tub/shower owner held. PH Bath3 tub versus point drain and owner basin unresolved. Active dry feature board directions remain PH Powder Earth Lines 3.69, TX Powder Haze Camel/Wheat 70:30 3.67, TX Powder2 Indigo 3.23; none owner-approved. PH and TX WC floors are covered inside their Primary level floor and inherit unresolved wet DCOF.",
"","Manufacturer raw measured wet DCOF points, proper installation drain/substrate/membrane, actual 1529 room survey, finish-specific manufacturer wet approval for Caviar/Opal/Bone Reed/Clay Ribbed, PH4 35/27 area and Soft/Anti-Slip old quote, accepted owner basins and room caps, current Chicago stock and price are all still **null/held**. A Daltile Target or a maker-reported Glazzio >0.50 bound is NOT the actual test report. Historical ELM material-only values include 15% source waste and no current landed cost."]
if scored:
 scores=json.loads((R/"state/ROUND010_SCORING.json").read_text(encoding="utf-8"))
 assert scores["verification"]["all_valid"] and scores["verification"]["criterion_checks"]==114
 index=[x.replace("(blind review pending)","(12 independent critics scored; all three BLOCKED)") for x in index]
 for i,line in enumerate(index):
  if "| **PH Primary**" in line:
   index[i]=line.replace("BLOCKED, candidate scores null","BLOCKED: original C 2.65 vs revised A 3.38 (+0.73), min cost 2.6; wet floor/pan gate FAIL")
  elif "| **PH Bath2**" in line:
   index[i]=line.replace("BLOCKED, candidate scores null","BLOCKED: original A 3.49 vs revised C 3.57 (+0.08), min cost 2.8; wet floor gate FAIL")
  elif "| **PH Bath4**" in line:
   index[i]=line.replace("BLOCKED, candidate scores null","BLOCKED: original C 2.52 vs revised B 3.35 (+0.83), min cost 2.2; wet floor/pan gate FAIL")
  elif line.startswith("**Scoring cadence:**"):
   index[i]="**Scored in subsequent independent turn:** 12 actual SHA-checked critics across four seats, 114 evidence-backed criterion scores, 6 frozen source candidate SHA unchanged; source ROUND010_SUBMISSION.json intentionally remains all_critic_scores:null while separately signed state/ROUND010_SCORING.json and three room registers carry completed blocked verdicts. No owner/purchase approval."
 index.insert(8,"| [R010 scored 13-room owner/GC addendum](R10_ROUND010_SCORED_13_ROOM_OWNER_ADDENDUM.md) | Actual 12-critic weighted/minimum/hard-gate comparison across PH Primary/Bath2/Bath4, all BLOCKED, plus full 13-room source/vendor/owner next fixes |")
(O/"START_HERE_R10_OWNER_AND_GC.md").write_text("\n".join(index)+"\n",encoding="utf-8")
for file in O.glob("*.md"):
 for l in re.findall(r"\]\(([^)]+)\)",file.read_text(encoding="utf-8")):
  if not l.startswith(("http://","https://","#","mailto:")):
   assert (file.parent/l.split("#")[0]).exists(),(file,l)
man={"round":10,"owner_approved":False,"procurement_release":False,"native_1529_geometry_verified":False,"rooms":13,"original_source_quote_rows":27,"release_closure_actions":65,"nominal_wall_cut_studies":25,"original_historic_2PH_2TX_material_only_usd":23572.44,"original_15pct_waste_embedded":True,"source_receipt":"state/ROUND010_SUBMISSION.json","all_critic_scores":None,"weighted_scoring_complete":scored,"scored_record":"state/ROUND010_SCORING.json" if scored else None,"files":[]}
for f in sorted(O.glob("*")):
 if f.name!="MANIFEST.json" and f.is_file():man["files"].append({"file":f.name,"bytes":f.stat().st_size,"sha256":hashlib.sha256(f.read_bytes()).hexdigest()})
(O/"MANIFEST.json").write_text(json.dumps(man,indent=2)+"\n",encoding="utf-8")
print("PASS R010 13 room/27 exact original material rows/65 coordinated action holders/25 wall cuts/6 frozen candidate SHA/$23572.44; index and",len(man["files"]),"SHA-signed deliverables")
