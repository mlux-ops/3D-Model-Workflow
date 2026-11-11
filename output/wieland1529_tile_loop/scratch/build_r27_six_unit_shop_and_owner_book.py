"""Create actionable physical six-unit powder trades, 13-room owner brief; no site measurements invented."""
from pathlib import Path
import csv,json
from decimal import Decimal
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'deliverables/integrated-r27-powder-value-and-13room-procurement'
def read(n):
 with (OUT/n).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))
def write(n,rows):
 p=OUT/n;assert not p.exists()
 with p.open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n')
  w.writeheader();w.writerows(rows)
rs={r['id']:r for r in json.loads((ROOT/'state/ROOMS.json').read_text(encoding='utf-8'))['rooms']}
stages={
'PH-POWDER':{
 'units':['405A','405B'],'surface':'Earth Lines 2x10 8.6mm glossy relief and optional owner-selected DRY painted flat center',
 'fixture':'Selected Brizo T65722LF-GL Luxe Gold WALL, separately required R65700 rough; RP72414GL drain',
 'evidence':'Brizo exact 9-11/16in spout reach and factory rough/escutcheon bearing; selected basin/vanity splash projection; dry painted center owner optional, no AXOR substitution',
 'dim':'Source W1 50.688 x111in; 12/16/20in conditional painted centers with 20in nominal 10in module cut under3; actual 1529 W1/height/mirror/rough/counter and body height unknown',
 'section':'[TILE glossy raised Earth Lines] > actual owner chosen metal edge/movement joint > [PAINT dry FLAT finished bearing] > R65700 rough supported in proper wall backing > selected Brizo gasket and trim > countertop bowl/wood floor; never expose raw board',
 'sample':'Full-scale selected Brizo rough and Luxe Gold actual escutcheon under both flat paint and relief, 1x2/2x10 tile caliber, two end cut pieces >=3in, two metal trim lengths, painted field chip, grout, sink water landing check',
 'views':['Straight-on Brizo selected WALL faucet with proposed 12/16in center and equal relief flanks, actual 1529 datum missing','Oblique low vanity showing 8.6mm raised relief/flat painted transition and wood floor','Tight 1:1 Brizo Luxe Gold seal/rough and 9-11/16in projection over actual owner basin, no measured basin depicted'],
 'first':'Owner select uninterrupted Earth Lines vs a particular finished painted full-height center width and paint, not implicit approval',
 'second':'Architect certifies measured correct 1529 rough W1, vanity/face/paint and two exposed trim lengths',
 'third':'Plumber verifies R65700 depth/bracket, gaskets and actual spout water landing'},
'TX-POWDER':{
 'units':['102A','102B'],'surface':'Haze Camel/Wheat 1.6x5 matte 8mm in one dry wall; optional Earth Lines 2x10 relief separate scheme',
 'fixture':'TWO unselected separate WALL programs: AXOR One cross-handle Polished Gold Optic 48140991 OR hansgrohe Metropol Brushed Bronze single-lever 32526141 + now factory compatible 13622181 rough',
 'evidence':'AXOR exact matching rough NOT VERIFIED; Hansgrohe factory 13622181 lists 32526141 compatible; original source wrong 32526141 rough designation and showroom inventory unverified',
 'dim':'Source W1 35.880x111in; 70/30 band widths 25.116/10.764 before joints, field unknown and actual 1529 width/mirror/escutcheons unmeasured',
 'section':'One manufacturer selected WALL trim and its exact separate compatible factory rough/box only; finished flat sealed faucet bearing if maker demands; Haze dry tile field+grout or distinct Earth Lines dry relief option, mirror backing, wood floor; no wet-pan detail',
 'sample':'Two separately labeled AXOR CROSS and Metropol SINGLE fixture cardboard/metal mockup comparison, ACTUAL owner-chosen trim and factory rough only for approved 1:1, handle swing, escutcheon, real Haze 70:30 color cartons, flat bearing if needed',
 'views':['Head-on Haze 70:30 wall, one tile total and neutral blank faucet placeholder until owner selects','Close two mutually exclusive maker-hardware sketches, expressly not shown installed together','Oblique wood-floor/vanity and grout 1.6x5 color transition; signed exact rough front elevation pending'],
 'first':'Owner selects AXOR One 48140991 OR Metropol 32526141 and finish, with no assumption 32526141 is rough',
 'second':'Architect confirms selected trim handle swing, mirror, three vs single ESC bearing and wall relief/flat cut',
 'third':'Plumber checks actual pre-existing site/source/showroom inventory and obtains exact AXOR rough OR selected Metropol 13622181 assembly, pipe depth and drain topology'},
'TX-POWDER2':{
 'units':['009A','009B'],'surface':'Vera Forma Indigo Edge 6x6 glossy relief 8.6mm wall only; Earth Lines 2x10 a separate owner option',
 'fixture':'Selected hansgrohe Tecturis E 73072341 Brushed Black Chrome DECK faucet, basin UNSELECTED, separate project drain 50100341',
 'evidence':'Factory Tecturis DECK supplied mounting parts/hoses, not wall rough; selected basin rim/overflow plus 50100341 matching finish and actual faucet reach unknown',
 'dim':'Source W1 45.672x111in; six centered 6in full modules with 0.125in illustrative joints and two 4.3985in ends; source carton 30pieces/7.34SF inconsistent with nominal 30x6x6=7.5SF',
 'section':'Indigo wall [DRY tile] over backed mirror > planned actual backsplash/counter upstand > separate real DECK basin and Tecturis factory bore/reach, overflow/drain trap supported in vanity > wood floor; no wall faucet ESC or PAN',
 'sample':'3x3 actual Indigo tiles and grout under daylight/warm grazing light, exact selected Tecturis 73072341 on detachable countertop mockup but NO drilling before owner selected basin + manufacturer template, chosen basin overflow/drain selection',
 'views':['Frontal W1 Indigo 6x6 centered six full nominal columns, mirror datums hypothetical','Oblique relief tile and Brushed Black Chrome DECK faucet, countertop and wood finish, sink placeholder labeled unselected','Close DECK single faucet mounting template with blank owner basin and source 50100341 unconfirmed overflow, no wall rough'],
 'first':'Owner elects basin size/type and exact color/finish wall sample, not automatic Indigo purchase',
 'second':'Architect certifies 1529 counter, rear clearance and mirror to tile, wood/vanity upstand, true W1',
 'third':'Plumber checks selected Hansgrohe DECK reach/connection, sink bowl/overflow 50100341 drain, trap and countertop drilling only after signed plan'},
}
units=[]
for rid,x in stages.items():
 for i,unit in enumerate(x['units']):
  units.append(dict(room=rid,physical_room_number=unit,unit_independent_site_survey_required='TRUE',fixture_program=x['fixture'],dry_wall_material=x['surface'],manufacturer_source_verified_vs_unresolved=x['evidence'],
     schematic_wall_source_and_measurement_gate=x['dim'],full_section_substrate_rough_and_edge_control=x['section'],
     mockup_1to1_components_acceptance=x['sample'],render_view_1_source_true_not_produced=x['views'][0],render_view_2_source_true_not_produced=x['views'][1],render_view_3_source_true_not_produced=x['views'][2],
     owner_selection_required=x['first'],architect_survey_shop_required=x['second'],plumber_system_shop_required=x['third'],
     waterproofing_installer_scope='N/A DRY POWDER WALL/WOOD FLOOR (confirm countertop splash protection only)' ,
     tile_installer_hold='Real calibrated size, <= accepted lippage, no under-3in focal cuts, proper finished dry wall and edge/movement joints, executed 1:1 under selected light',
     supplier_hold='Exact ordered tile color/lot, factory case quantity, actual 1529 new measured net and agreed once-only cut allowance, written current Chicago ETA and installed material/paint/edge bid',
     ACTUAL_1529_W1_width_in='',ACTUAL_mirror_and_faucet_center_in='',ACTUAL_tile_caliper_joint_and_face_depth='',ACTUAL_net_tile_SF='',ACTUAL_paint_area_SF='',ACTUAL_trim_LF='',actual_waste_and_verified_case_qty='',factory_selected_rough_cut_sheet_signed='FALSE',
     physical_mockup_installed='FALSE',camera_render_created='FALSE',owner_approved='FALSE',architect_approved='FALSE',plumber_approved='FALSE',tile_installer_approved='FALSE',GC_approved='FALSE',purchaser_released='FALSE'))
assert len(units)==6
write('R27_6_PHYSICAL_POWDER_UNIT_1TO1_MOCKUP_FAUCET_FIELD_SHOP_CLOSURES.csv',units)

release=read('R27_13_ROOM_SEQ_OWNER_ARCH_PLUMB_WP_TILE_SUPPLIER_RESERVATION_RELEASE.csv')
family=read('R27_7_SOURCE_SAME_MATERIAL_MULTI_ROOM_GROUPS_AND_EXCLUSIONS.csv')
opts=read('R27_9_THREE_POWDER_MANUFACTURER_PHYSICAL_GOOD_BETTER_BEST.csv')
ph=read('R27_PH_BRIZO_4_PAINT_RELIEF_WIDTH_TILE_EDGE_COST_SCENARIOS.csv')
tx=read('R27_TX_HAZE_3_SINGLE_WALL_COLOR_ALLOCATION_AND_CUT_STUDIES.csv')
indigo=read('R27_TX2_INDIGO_4_HISTORIC_CARTON_THRESHOLD_SENSITIVITIES.csv')
val=read('R27_3_ALTERNATE_POWDER_MATERIAL_REFERENCE_RATE_VALUE_SCENARIOS.csv')
assert len(release)==13 and len(opts)==9 and len(family)==7
sections=[
'# R27 | 1529 Wieland | New powder-room physical design and all-13-room controlled material release',
'',
'**WORKING, UNSCORED OWNER/ARCHITECT/GC DECISION EXHIBIT. NO owner or GC release.** R27 uses manufacturer public fixture evidence and prior source W1 geometry; no field visit, actual mockup, purchased sample, installed work, photos, rendering, issued shop, original measured raw wet DCOF or supplier outreach. Signed R12-R26 unchanged. Rooms and R014/R017 blind source governance remain OPEN.',
'',
'## High-value new design decisions, not R22 narrative repeats',
'',
'**PH Powder** retains actual selected Brizo WALL T65722LF-GL Luxe Gold / R65700 rough. Manufacturer public spout reach **9-11/16in** gives a real dimensional clearance check against owner-signed basin and true finished wall, not guaranteed water landing. The already-considered relief-to-flat idea has now been transformed into four full-height 0/12/16/20in painted-center cut/quantity/edge studies. A 20in proposed flat strip gives nominal raised 2x10 tiles with **sub-3in centered end cuts**, so not a defensible unchecked bond; 12 or16in candidates have viable nominal end cuts but require full-size calibrated 1:1, paint selection, trim cost and real Brizo gasket support. Actual two exposed center vertical edges yield **18.5 LF nominal** only, not orderable trim.',
'',
'**TX Powder** continues historical Haze Camel/Wheat 70/30 dry WALL, with 3 actual area-band/cut scenarios and no duplicate per-color wall quantity. Factory hansgrohe **13622181** is newly confirmed on official maker product page as matching Metropol wall TRIM 32526141, correcting wrong prior rough label. This is **one optional factory-compatible program only**, not selected or installed. Competing AXOR One cross-handle 48140991 is a DIFFERENT Polished Gold Optic trim and its exact required rough remains unknown. Owner must elect exactly one trim program before architecture/plumber can position a sealed wall bearing island. A conditional Earth Lines relief scheme is NOT priced to PH old rate as a new TX supplier offer. The alternative trim+rough manufacturer public MSRP cannot be compared to AXOR trim-only without the missing AXOR rough.',
'',
'**TX Powder2** retains selected DECK Tecturis E 73072341 Brushed Black Chrome, basin UNSELECTED. New calibrated cut model centers **six** nominal 6in columns across provisional 45.672in W1 with joint-inclusive ~4.3985in side cuts, not prior joint-free 4.836in, and 17 full modules over 111in height with ~3.375in top/bottom cuts. Dated 7.34 SF/30pcs carton conflicts with nominal 30 six-inch pieces 7.5 SF, hence supplier must confirm actual carton SF/usable pieces, lot and approved case split. Two copies source **81.0 SF GROSS** at historic carton 7.34 SF/box gives **12 hypothetical cases**; if independently verified revised NEW gross across both units were <=80.74 SF then 11 hypothetical case count, but is not a measured saving, current packaging or procurement authorization. No DECK hole or wall-escutcheon fabrication before selected basin/overflow.',
'',
'## Decision matrix for all three powder rooms',
'']
for rid in stages:
 x=stages[rid]
 sections.extend(['### '+rid+' — '+x['fixture'],'','**Baseline maker dry wall:** '+x['surface'],'','**Four controls:** '+x['first']+'; '+x['second']+'; '+x['third']+'; separately documented case/installed bid.','',
 '**GOOD / BETTER / BEST are unscored visual/construction options:**',''])
 for r in opts:
  if r['room']==rid:sections.append('- **'+r['tier']+':** '+r['new_distinct_material_and_install_design']+'; '+r['Old_Town_buyer_value_and_constructability'])
 sections.extend(['','**Source-faithful 3-camera instructions:** '+', '.join(x['views'])+'. No images or field photography were created.',''])
sections.extend(['## Specific quantified decision gates','',
 'PH four flat landing widths: source full wall 50.688x111in, historical quote 44.9 SF gross/copy, $368.18/copy. Source-rate theoretical tile reductions use a NEW physically different measured tile-face quantity; they are an old-rate comparison only. Two new transitions, owner-selected paint, metal profile/grout/wood/basin and actual labor remain unpriced. 12/16in center modules are schematic; no automatic owner-painted center approval.',
 '',
 'TX one wall source 35.88x111in, 31.8 SF historic GROSS once, $379.37/copy. 70/30 equals 22.26 SF Camel +9.54 SF Wheat source gross allocation per copy, not separately payable two 31.8 SF walls. Actual factory color-specific case size, lot and full cost unknown.',
 '',
 'TX2 wall source 45.672x111in, original 40.5 SF gross/copy / $332.10, 30pc/7.34SF historical carton. 6x6 nominal 30pc geometric coverage 7.5 SF shows manufacturer carton discrepancies; only true current same SKU box label resolves real order and shared case usage.',
 '',
 'Potential cross-room same product groups: exact historical Tones Sandstone 2x20 Glossy NICHE appears in four bathrooms, but physical wet area and owner branch/lot must match and source niches must net subtract the field aperture; two copies of each source group produce 51.64 SF original gross, **NOT a new net or order**. Original Clara Caviar 2x8 in PH4/TX4 has NO individual wet NICHE permission and must NOT be pooled for reservation. Cortar Bone Soft 12x24 source PH3/TX4 and Cortar Grey Soft PH2/TX3 require original exact raw wet LEVEL lab and same lot before any consolidated delivery. Primary mixed Soft/AntiSlip floor may not be pooled as one SKU. PH/TX shared WCs have NO extra material row.',
 '',
 'The three powders originally total $2,159.30 historic tile-only for two copies each, already included in the original $23,572.44 four-unit total. A **reference-only** PH old Earth Lines rate of $8.20 x TX Powder historic 31.8 SF = $260.76/copy vs original Haze blended $379.37/copy, hypothetical **-$118.61/copy** or **-$237.22 for two** before new trim, paint, grout, labor and actual TX quote. This is NOT a supplier offer, owner saving or lower installed price. If all three dry powders used the same Earth Lines product, cross-unit material commonality is conditional on owner signoff, verified identical factory SKU/color/caliber and shade/lot, staged delivery and independent each-room counted-once case allocation. No blanket common order has been authorized.',
 '',
 '## Sequential no-shortcut reservation / ordering gates',
 '',
 '1. **OWNER** signs program, per-room palette, the AXOR-vs-Metropol trim choice, PH paint and color, TX2 basin selection, room upgrade cap. Owner chooses no PH/TX Bath3 tub or basins by proxy.',
 '2. **ARCHITECT** authenticates correct 1529 model and actual each room/unit width/height/rough plane/counter/mirror, revised colored W1 elevations and focal cuts >=3in or individually approved correction; floor/WC/wet book remains separate.',
 '3. **PLUMBER** signs factory exact Brizo T65722LF-GL/R65700 and basin reach, AXOR genuine trim plus rough OR Metropol 32526141+maker 13622181, TX2 73072341 DECK and owner-approved sink overflow/drain, 1:1 support and as-found inventory.',
 '4. **WATERPROOFER** marks dry decorative powder wall and WOOD floor wet shower membrane/PAN/NICHE/LEVEL gates N/A, ensures real backsplash/counter splash and movement interfaces; wet bathrooms individually require signed wall/niche/LEVEL and PAN original exact numeric wet lab and original drain/membrane/shop.',
 '5. **TILE INSTALLER** performs actual 1:1 relief-to-paint metal, grout/band/edge/cut tests in six units, calibrated tile module, wood floor/base and mirror/door trim; no samples or mockups performed yet.',
 '6. **SUPPLIER/ESTIMATOR** proves exact manufacturer material/color/size/finish/lot and actual 30pc /7.34SF contradiction resolution, each owner material selection, current Chicago dedicated availability, same-lot case quantity/staged split, landed material, paint/trim/setting/movement and installed GC bid. Attic stock and any cross-room volume rebate must have written terms, not be inferred.',
 '7. **ARCHITECT + GC + OWNER + PURCHASER** separately sign each scope and revised current price after other gates, NO procurement order before every release flag is TRUE.',
 '',
 '## All 13 source programs remain protected',
 ''])
for r in release:
 sections.extend(['### '+r['room'],'', '**Retain:** '+r['selected_hardware_program_and_selection_hold']+'.','',
 '**First witness to close:** '+r['reason_this_room_must_not_pooled_blindly']+'.','',
 '**Wet evidence applicability:** '+r['wet_LEVEL_and_PAN_applicability']+'.','',
 '**Physical sample / correct 1529 camera or drawing:** '+r['sample_and_camera_acceptance']+'.',''])
sections += [
'## Historical and resale controls',
'','Exactly 13 source room IDs, 27 tile material records (two extra unpriced Primary niche history references NO SCOPE/NO ORDER), 25 provisional original wall keys, 65 original trade closures. The original $23,572.44 four-unit tile-only cost includes original 15% waste ONCE. No extra WC, LEVEL/PAN overlap, niche field/back/returns duplicate, opening or trim counted. Current Chicago lot/ETA/bid/physical mockups and full 13-room independent original raw wet floor certificates not received.',
'','Fourteen listing entries represent NINE buildings. 405 W Armitage OT01-OT04 is ONE Old Town building; prioritize verified recent Old Town while Lincoln Park and Gold Coast remain secondary. PH approximate $2.8M, TX $2.7M in $2.4M-$3.2M comparable band. No competitor bathroom-tile identities inferred from unverified photographs.',
'','**Governance:** R014 original DESIGN worker-9 FAILED, only 6/8 authentic specialist files. R015 partial original critic dispatch HOLD. R016 sources independently source-cleared as of R22 but NOT DISPATCHED; R017 eight frozen neutral source packets and four private keys await separate independent preflight, no critics or weighting. Sole non-Pro Reviewer worker-15 finished/nonrevivable with independent R23 FIX, corrected R23 local only and R24/R25/R26 independent acceptance absent. This R27 package is not a new scoring submission or authorized owner approval.',
'','**ENTIRE 13-ROOM PROJECT OPEN. ALL owner, architect, plumber, GC, supplier and purchaser approval/release flags FALSE. No native Revit or Smartsheet modifications, vendor communications, forms, purchases or sample orders.**']
p=OUT/'R27_THREE_POWDER_AND_13_ROOM_OWNER_ARCHITECT_GC_DECISION_BOOK.md'
assert not p.exists()
p.write_text('\n'.join(sections)+'\n',encoding='utf-8')
print('PASS R27 new six unique physical unit fixture mockups and source-faithful three-view briefs plus all-13-room technical, source/cost, staged vendor release owner book')
