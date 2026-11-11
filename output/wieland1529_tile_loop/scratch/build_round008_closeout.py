from pathlib import Path
import csv,json,hashlib
R=Path(__file__).resolve().parents[1];O=R/'deliverables/integrated-r05';O.mkdir(parents=True,exist_ok=True)
rooms=json.loads((R/'state/ROOMS.json').read_text(encoding='utf-8'))['rooms']
needed={
'PH-PRIMARY':{'owner':'approve wall/field/pan palette only after testing; no niche','maker_wall':'flat Cortar Bone manufacturer Wet Areas PASS; Bone Reed unlisted','floor':'PF07 12x24 Target only, exact test null','pan':'PF07 2x2 Target only; linear-drain approval blank in Portfolio maker sheet','drain':'Brizo 48-inch linear; position/slope null','other':'No niche. WT area/ceiling, WC share, PF07 or Prime RL option independent'},
'PH-BATH2':{'owner':'sample Sapphire vs Copper option (no required wet-fix)','maker_wall':'Tones Sapphire 2x20 Glossy Wet Areas PASS; Sandstone maker Wet Areas PASS','floor':'Cortar Grey Soft/PF05 exact wet DCOF null','pan':'N/A retained Duravit tub','drain':'Duravit tub, Matte White Hansgrohe; tub flange coordinates null','other':'Niche back/returns overlap to be netted; wall finish itself compliant'},
'PH-BATH3':{'owner':'select basin and resolve tub versus selected Delta square point drain','maker_wall':'Tones Opal wet listing absent; proposed Sandstone Wet Areas PASS','floor':'Bone Soft/PF07 floor exact wet DCOF null','pan':'null unless shower elected; tub source is NOT pan evidence','drain':'Delta DT062412 point drain versus source tub conflict','other':'Niche field face and returns unknown'},
'PH-BATH4':{'owner':'resolve 35 vs 27 SF and Soft vs Anti-Slip owner/source interpretation','maker_wall':'Bone Ribbed and Clara Caviar wet listing absent; flat Bone/Soho Wet Areas PASS','floor':'Charcoal Soft quote vs Anti-Slip spec; PF09 field DCOF null','pan':'PF09 2x2 point-drain DCOF null, provisional 14.6 gross SF not approved','drain':'Brizo BT062415-BNX 4-in square; four-plane slope unknown','other':'Original 214.4 SF two-unit Ribbed vendor-total omission must reconcile'},
'PH-POWDER':{'owner':'confirm Earth Lines dry feature/metal grout/mirror','maker_wall':'Earth Lines dry-wall finish, wet-area approval not applicable','floor':'N/A historic wood floor','pan':'N/A','drain':'N/A','other':'Board Earth Lines 3.69 active, not stable'},
'PH-WC':{'owner':'confirm threshold and adopt qualified Primary level finish only','maker_wall':'N/A separate tile wall','floor':'Included in PH Primary quoted floor; inherits level DCOF clearance','pan':'N/A','drain':'N/A','other':'NO separate purchase SF or carton'},
'TX-PRIMARY':{'owner':'approve flat Clay field and alternate pan palette only after tested acceptance','maker_wall':'flat Cortar Clay Wet Areas PASS; Clay Ribbed wet listing absent','floor':'Original mixed Soft/Anti-Slip; PF07 12x24 exact wet test null','pan':'PF07 2x2 exact DCOF null AND Portfolio linear drain suitability blank; Prime RL alternative only research','drain':'Brizo 48-inch linear; actual slope/position null','other':'No primary niche; WC included in original blended floor'},
'TX-BATH2':{'owner':'select basin and approve wet wall palette','maker_wall':'Tones Copper/Sandstone maker wet wall listings in project audit','floor':'Cortar Clay Soft/PF07 exact DCOF null','pan':'N/A retained tub','drain':'Tub flange/return dimensions null','other':'Niche field/back deductions unknown'},
'TX-BATH3':{'owner':'DECIDE tub versus walk-in with Brizo point drain','maker_wall':'Emerald/Sandstone source, exact proposed wall use must be reconfirmed','floor':'Grey Soft/PF05 exact DCOF null','pan':'null, DO NOT infer pan SF from tub alcove','drain':'Brizo BT062415-BNX square point versus tub source','other':'Program must settle before any floor/pan package'},
'TX-BATH4':{'owner':'approve exact Charcoal/Soho wet wall/niche arrangement after samples','maker_wall':'Clara Caviar wet approval absent; flat Charcoal/Soho maker Wet Areas reported','floor':'Cortar Bone Soft exact wet DCOF null','pan':'N/A retained tub source','drain':'Tub details and walls provisional','other':'Caviar niche and relief source quantities/returns unmeasured'},
'TX-POWDER':{'owner':'accept/revise board-selected 70% Camel/30% Wheat Haze','maker_wall':'Dry Haze vanity wall; floor DCOF N/A','floor':'N/A wood floor','pan':'N/A','drain':'N/A','other':'48140991 wall faucet/32526141 rough, mirrored cuts; color-specific quote null'},
'TX-POWDER2':{'owner':'select basin and verify deck-faucet landing','maker_wall':'Dry Indigo Edge v4 retained','floor':'N/A wood floor','pan':'N/A','drain':'N/A','other':'Hansgrohe 73072341 DECK mounted, smooth insert unpriced/unselected'},
'TX-WC':{'owner':'approve primary-level threshold/finish only','maker_wall':'N/A','floor':'Included in TX Primary floor line; numeric DCOF follows Primary','pan':'N/A','drain':'N/A','other':'No separate tile SF or carton'}
}
assert len(needed)==len(rooms)==13
result=[]
for x in rooms:
 rid=x['id'];z=needed[rid]; wc=rid.endswith('-WC');dry=rid in ('PH-POWDER','TX-POWDER','TX-POWDER2')
 row={'room_id':rid,'unit_type':x['unit_type'],'copies':x['unit_count'],'board_status':x['status'],'champion_id':x['champion_id'] or 'null',
 'historic_tile_cost_usd_per_unit':f"{x['carried_quote_material_subtotal_usd_per_unit']:.2f}",
 'source_gross_sf_includes_15pct_waste':'true','quote_source_rows':len(x['carried_tile_rows']),
 'owner_selection_approved':'false','owner_decision_needed':z['owner'],
 'manufacturer_wet_wall_evidence':z['maker_wall'],
 'wet_level_floor_evidence':z['floor'],'wet_shower_pan_evidence':z['pan'],'drain_and_assembly_evidence':z['drain'],
 'correct_project_1529_native_identity':'false','actual_survey_verified':'false','exact_wet_dcof_certificate':'HOLD inherited Primary level floor DCOF test null/FAIL' if wc else 'N/A dry powder wood floor' if dry else 'null / FAIL',
 'maker_linear_drain_application':'HOLD if PF07 linear' if rid in ('PH-PRIMARY','TX-PRIMARY') else 'N/A',
 'exposed_trim_lf':'null','current_chicago_lot_stock':'null','current_supplier_lead':'null','current_revised_material_price':'null','owner_room_material_cap':'null','installed_cost_quote':'null','orderable_cartons':'null','owner_signed_finish':'null',
 'release_allowed':'false','highest_priority_dependency':z['other']}
 result.append(row)
f=O/'R08_ROOM_EVIDENCE_CLOSEOUT_TRACKER.csv'
with f.open('w',encoding='utf-8-sig',newline='') as h:
 w=csv.DictWriter(h,fieldnames=result[0]);w.writeheader();w.writerows(result)
assert sum(float(r['historic_tile_cost_usd_per_unit'])*int(r['copies']) for r in result)==23572.44
assert sum(int(r['quote_source_rows']) for r in result)==27
assert all(r['release_allowed']=='false' and r['owner_selection_approved']=='false' for r in result)
head=['# R08 | 13-room owner / GC evidence closeout and release-dependency register','',
'**This is an operational checklist, not an approval or permit document.** Built from actual 13-room scored register, 27 historical ELM quote rows and manufacturer R05–R07 evidence. No available owner signatures, exact wet DCOF values, real Chicago inventory or native 1529 model measurements were invented. The companion machine-readable file is `R08_ROOM_EVIDENCE_CLOSEOUT_TRACKER.csv`.','',
'## Required decision route by room','',
'| Room | Historical tile-only $/unit | Board status | First non-inferable decision | Mandatory technical evidence before release |',
'|---|---:|---|---|---|']
for x,r in zip(rooms,result):
 rid=x['id']; z=needed[rid];head.append('| %s | $%.2f | %s | %s | %s; %s; verified 1529 dimensions; actual supplier/budget signoff |'%(rid,x['carried_quote_material_subtotal_usd_per_unit'],x['status'],z['owner'],z['floor'],z['pan']))
head+=['','## Evidence owner vs technical reviewer (roles, not invented named people)','',
'**OWNER ONLY:** approves/rejects proposed finishes and exact sinks; TX Bath3 tub vs walk-in; PH Bath4 35 vs 27 area interpretation, per-room material allowances and any upgrades. No assistant selects these.',
'**ARCHITECT/DESIGNER:** verifies an actual 1529-model document title/path/session plus field survey, selected actual drain/fixture locations, shower area and pan/level boundaries, niche face deduction and 24x48 or 2x20 cut plans, glass/curb/threshold/finish decisions, owner palette signoff. Current 1527 Revit session is not 1529 proof.',
'**GC/TILE INSTALLER:** validates compatible specified membrane/backer/drain flange and warranty, actual substrate flatness, point/linear pitch plane feasibility, finished field/pan elevations (Portfolio 2x2 glazed ceramic 1/4in vs 12x24 porcelain 5/16in), grout/movement, exposed trim LF and stick dimensions, physical mock-up. Approval cannot come from conceptual W1–W3 sizes.',
'**MANUFACTURER / TECHNICAL REPORT (future authorized channel only):** full product code/color/size/finish wet wall approval, each floor and pan measured test result with actual test method/date/certificate. PF07 linear drain maker sheet has no suitable mark; Prime RL20/21/23 maker brochure does mark mosaic linear use but has conflicting old/new targets ≥0.60/≥0.42 and no exact measured point.',
'**PROCUREMENT / ESTIMATOR (future authorized channel only):** dated exact-SKU Chicago stock/lot and delivery, cartons/shade/freight/trim/setting/labor current quotation, comparative historic vs new scope, owner cap and 125% check. Historical ELM four-dwelling tile-only source $23,572.44 cannot serve as current installed budget. No vendor contact performed.',
'', '## Priority closeout sequence (no implied approvals)','',
'1. **Owner geometry/program:** actual project identity; PH Bath3 tub/Delta point-drain plus unselected basin; TX Bath3 tub vs walk-in; PH Bath4 35/27-SF and quoted Soft vs intended Anti-Slip, plus three basins (PH3, TX2, TX Powder2).',
'2. **Technical wet listing:** Clara Caviar 2x8 niche, Tones Opal, Bone/Clay relief finishes product-specific wet use; maintain Sapphire 2x20 Glossy confirmed wet tub wall PASS. Flat alternate approval never transfers to relief.',
'3. **Exact wet-floor and pan reports:** original ELM floors, PF07/PF05/PF09 12x24 fields and 2x2 pans, conditional maker listed RL20/21/23 linear options and Glazzio inequality/version research. Manufacturer Target is not measured exact result.',
'4. **Measured shop details and quantities:** preserve single original source 15% waste, share WC with Primary floor, no primary shower niches, avoid duplicate niche back/face. Determine field/pan split and then profile LF and per-SKU cartons.',
'5. **Source pricing and release:** separate 2026-09-03 original ELM amounts, online retail examples, qualified exact-SKU dated supplier bids, current Chicago availability, room material cap and signed owner schedule. `release_allowed=false` for every room until verifiable specific evidence and decisions exist.',
'', '## Validation and archive rules','',
'The CSV is a status control and never substitutes for a signed product submittal. Every unresolved item intentionally remains `null`, FALSE, HOLD or N/A rather than an invented count, cost, test or decision. Full source trace: `state/ROOMS.json`, `state/ROUND004_SCORING.json`, R05/R06/R07 manufacturer research, original v4 source and `SURFACE_TAKEOFF_13_ROOMS.csv`. Updating any release_allowed flag requires a new document receipt, corresponding review and owner/technical authorization.']
(O/'R08_OWNER_GC_CLOSEOUT_ACTION_SHEETS.md').write_text('\n'.join(head)+'\n',encoding='utf-8')
print('PASS R08 release controls 13 rooms, 27 source rows, $23572.44 historic, ZERO false approvals, 13 individual decisions')
