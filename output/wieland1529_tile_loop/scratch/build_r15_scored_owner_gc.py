"""Additive four-file R15 signed scored all-13-room owner/GC release bridge."""
from pathlib import Path
import csv,hashlib,json
from decimal import Decimal

R=Path(__file__).resolve().parents[1]
OUT=R/'deliverables/integrated-r15'
assert not OUT.exists()
rooms=json.loads((R/'state/ROOMS.json').read_text(encoding='utf-8'))['rooms']
scored=json.loads((R/'state/ROUND013_SCORING.json').read_text(encoding='utf-8'))
assert len(rooms)==13 and len(scored['room_results'])==3
with (R/'deliverables/integrated-r14/R14_13_ROOM_EXACT_SOURCE_AND_OWNER_GC_RELEASE_BRIDGE.csv').open(encoding='utf-8-sig',newline='') as f:
    r14=list(csv.DictReader(f))
with (R/'deliverables/integrated-r13/R13_65_TRADE_OWNED_EVIDENCE_AND_RELEASE_ACTIONS.csv').open(encoding='utf-8-sig',newline='') as f:
    original=list(csv.DictReader(f))
assert len(r14)==13 and len(original)==65
authority={x['room']:x for x in r14}
assert set(authority)=={x['id'] for x in rooms}
assert sum(Decimal(str(x['carried_quote_material_subtotal_usd_per_unit']))*x['unit_count'] for x in rooms)==Decimal('23572.44')

def fsha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
def next_gap(rid):
    if rid in ('PH-PRIMARY','TX-PRIMARY'):
        return 'Exact raw tested LEVEL/WC and LINEAR PAN wet DCOF per SKU; selected Brizo 48-in Black Onyx LINEAR and BR73480 manufacturer-approved rough/liner/slope/flood section; no Primary niche; measured shared WC not double ordered'
    if rid=='PH-BATH2':
        return 'Source nominal W1 59.496 in minus selected Duravit 59-in tub = only 0.496 in TOTAL nominal difference before tile/backer/flange; actual 1529 rough fit and LEVEL raw DCOF missing; Sapphire/Sandstone wet PASS; tub, NO PAN'
    if rid=='TX-BATH2':
        return 'Basin owner unselected; selected Duravit TUB/Hansgrohe Chrome, NO PAN; manufacturer exact raw LEVEL DCOF and tub flange, niche and vendor quote unknown'
    if rid=='PH-BATH3':
        return 'Owner decides source tub alcove vs selected Delta DT062412 Chrome SQUARE POINT shower drain; basin unselected; exact Tones Opal Wet Areas listing/LEVEL raw DCOF and geometry held'
    if rid=='TX-BATH3':
        return 'Owner decides source tub alcove vs Brizo Black Onyx BT062415-BNX SQUARE POINT shower rough/controls; never substitute shower drain as tub waste; raw LEVEL/PAN tests depend on signed program'
    if rid=='PH-BATH4':
        return 'Actual WALK-IN Brizo BT062415-BNX Black Onyx 4-in SQUARE POINT not tub; 35/27-SF dispute and Soft/Anti-Slip; source 107.2-SF/unit full Ribbed wall, Caviar niche individually wet unlisted; exact LEVEL and POINT PAN raw DCOF'
    if rid=='TX-BATH4':
        return 'Original Cortar Bone Soft LEVEL vs proposed Emser Capisco Trosa F08CAPITR1224M LEVEL exact raw wet DCOF; selected Duravit/Matte White TUB NO PAN; Soho Ivory wet niche PASS vs original unlisted Caviar'
    if rid in ('PH-WC','TX-WC'):
        return 'Shared Primary LEVEL floor original 15%-loaded quantity already carries WC; measure partition and do NOT purchase separate WC floor, preserve individual LEVEL exact wet DCOF hold'
    if rid=='PH-POWDER':
        return 'Earth Lines 3.69 conditional board direction, not signed; Brizo Luxe Gold, confirm dry vanity wall cut/edge/mirror/escutcheon and real bid; shower PAN N/A'
    if rid=='TX-POWDER':
        return '70:30 Haze Camel/Wheat conditional board direction 3.67, not owner signed; verify measured actual area split, grout/edge and complete installed cost, dry vanity PAN N/A'
    if rid=='TX-POWDER2':
        return 'Retain conditional Indigo Edge 6x6 design 3.23; owner basin unselected; confirm deck spout, tile/mirror backing, elevation and Chicago exact quote'
    raise ValueError(rid)

fields=['room','unit_copies','latest_round','room_status','champion_id','current_champion_weighted',
        'r013_historic_letter','r013_revised_letter','r013_historic_weighted',
        'r013_revised_weighted','r013_margin','r013_min_revised_specialist',
        'r013_margin_at_least_025','r013_all_specialists_at_least_3','r013_all_hard_gates_pass','r013_challenger_accepted',
        'historical_source_usd_per_unit','historical_source_usd_two_units',
        'selected_program_and_fixture','specific_owner_gc_next_evidence',
        'exact_numeric_measured_level_wet_dcof','exact_numeric_measured_pan_wet_dcof',
        'verified_1529_model','current_chicago_lot_and_installed_quote','measured_level_sf','measured_pan_sf',
        'owner_approved','gc_procurement_release']
register=[]
for r in rooms:
    rid=r['id']
    q=scored['room_results'].get(rid)
    x={k:'' for k in fields}
    x.update({'room':rid,'unit_copies':'2','latest_round':str(r['last_round']),
      'room_status':r['status'],'champion_id':r.get('champion_id') or '',
      'current_champion_weighted':r.get('champion_score') or '',
      'historical_source_usd_per_unit':f"{Decimal(str(r['carried_quote_material_subtotal_usd_per_unit'])):.2f}",
      'historical_source_usd_two_units':f"{Decimal(str(r['carried_quote_material_subtotal_usd_per_unit']))*2:.2f}",
      'selected_program_and_fixture':authority[rid]['selected_plumbing_program_or_board_direction'],
      'specific_owner_gc_next_evidence':next_gap(rid),
      'verified_1529_model':'FALSE','owner_approved':'FALSE','gc_procurement_release':'FALSE'})
    if q:
        h=q['candidates'][q['historical_letter']]
        b=q['candidates'][q['revised_letter']]
        assert r['status']=='blocked' and r['champion_id'] is None and r['champion_score'] is None
        x.update({'r013_historic_letter':q['historical_letter'],
         'r013_revised_letter':q['revised_letter'],
         'r013_historic_weighted':f"{h['weighted_score']:.2f}",
         'r013_revised_weighted':f"{b['weighted_score']:.2f}",
         'r013_margin':f"{q['challenger_margin']:+.2f}",
         'r013_min_revised_specialist':f"{b['minimum_critic_score']:.1f}",
         'r013_margin_at_least_025':str(q['challenger_margin_at_least_025']).upper(),
         'r013_all_specialists_at_least_3':str(b['all_critics_at_least_3']).upper(),
         'r013_all_hard_gates_pass':'FALSE','r013_challenger_accepted':'FALSE'})
    register.append(x)
assert len(register)==13
assert sum(Decimal(r['historical_source_usd_two_units']) for r in register)==Decimal('23572.44')

action_fields=list(original[0])+['current_round','current_status','r013_conditional_score',
                                    'latest_specific_evidence','current_owner_release_gate']
actions=[]
by={r['id']:r for r in rooms}
for action in original:
    rid=action['room']
    r=by[rid];q=scored['room_results'].get(rid)
    x={**action,'current_round':r['last_round'],'current_status':r['status'],
       'r013_conditional_score':f"{q['candidates'][q['revised_letter']]['weighted_score']:.2f}" if q else '',
       'latest_specific_evidence':next_gap(rid),
       'current_owner_release_gate':'BLOCKED - NO RELEASE' if q else 'NO OWNER SIGNATURE - NO RELEASE',
       'exact_gc_approval':'False','owner_approval':'False','purchase_release':'False'}
    assert not any(x[k] for k in ('verified_1529_session_title_path','manufacturer_raw_lab_certificate_ref',
       'installed_quote_id','owner_rejected_or_approved'))
    actions.append(x)
assert len(actions)==65

OUT.mkdir(parents=True,exist_ok=False)
def csv_write(name,cols,rows):
    with (OUT/name).open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=cols);writer.writeheader();writer.writerows(rows)
csv_write('R15_13_ROOM_SCORED_OWNER_RELEASE_REGISTER.csv',fields,register)
csv_write('R15_65_TRADE_ACTIONS_LATEST_SCORES.csv',action_fields,actions)

lines=['# R15 — Round013 formally scored all-13-room owner/architect/GC release bridge','',
 '**NOT OWNER APPROVED. NOT A PURCHASE ORDER. NOT RELEASED FOR INSTALLATION.** Dated November 6, 2026. This is additive to SHA-signed R12/R13/R14 packages, not a replacement of dated original supplier quotes.','',
 '## Formal distinct-turn R013 Penthouse weighted results','',
 '| Room | Historical source | Revised design study | Improvement | Revised minimum critic | +0.25 gate | Every critic >=3 | All technical gates | Status |',
 '|---|---:|---:|---:|---:|---|---|---|---|']
for rid in ('PH-PRIMARY','PH-BATH2','PH-BATH4'):
    q=scored['room_results'][rid];a=q['candidates'][q['historical_letter']];b=q['candidates'][q['revised_letter']]
    lines.append(f"| {rid} | {a['weighted_score']:.2f} | {b['weighted_score']:.2f} | {q['challenger_margin']:+.2f} | {b['minimum_critic_score']:.1f} | {'PASS' if q['challenger_margin_at_least_025'] else 'FAIL'} | FAIL | FAIL | BLOCKED |")
lines.extend(['','A revised tile proposal requires +0.25 weighted improvement, no individual specialist below 3.0, and EVERY wet-wall, exact raw numerical tested wet LEVEL/PAN DCOF, geometry, availability, selected plumbing, budget (only if approved room cap exists) and owner veto hard gate. No higher average can override a FAIL. Four original R013 specialists independently authored the scored evidence.','',
 '## Penthouse technical findings and release prerequisites','',
 '### PH-PRIMARY','',
 'Selected Brizo Black Onyx BT0734816-BNX 48-in LINEAR with separately required BR73480 rough, separate Duravit tub and NO Primary shower niche. Revised manufacturer-wet-listed flat Cortar Bone 24x48 WALL and Daltile RL21 12x24 LEVEL/shared PH WC plus separately RL21 1.5-in hex LINEAR PAN are conditional only. Maker Target is not raw measured DCOF; both LEVEL/WC and PAN FAIL strict exact numerical lab tests. Manufacturer factory solid grate is a valid study to avoid tile-in insert thickness, but not approved rough/membrane/pan/flood construction. Older 1/4-in brochure vs current maker 5/16-in hex and 1/8-vs-3/16 grout snapshots remain HOLD. Original 143 gross wall/ceiling and 135.6 gross LEVEL/WC/PAN per unit include original 15% waste once; shared PH WC not another purchase.','',
 '### PH-BATH2','',
 'Retain selected Duravit 700332000000090 actual 59-in TUB and Hansgrohe MATTE WHITE, Tones Sapphire 2x20 Glossy and Sandstone 2x20 niche individually Wet Areas approved; NO tiled shower PAN. Proposed RL21 12x24 LEVEL is missing exact numeric measured raw wet DCOF. Historical Cortar Grey Soft LEVEL also missing raw report. Nominal tub W1 59.496 in minus nominal tub 59 in gives only 0.496-in TOTAL difference BEFORE framing, backer/tile/flange and tolerances; actual 1529 rough fit is neither certified nor disproven. Source 3.67 SF niche gross requires one field-opening deduction and measured recess back/returns/sill.','',
 '### PH-BATH4','',
 'Actual WALK-IN with selected Brizo Black Onyx BT062415-BNX 4-in SQUARE POINT drain, NOT tub/48-in linear. Revised flat Bone wet field and Soho Black wet niche individually Wet Areas supported, but proposed RL21 12x24 LEVEL and distinct hex four-plane POINT PAN raw measured numerical DCOF BOTH missing, Brizo compatible waterproof/rough/flood section absent. Historical FULL 107.2 gross SF/unit Ribbed Bone wet wall and Clara Caviar niche individually unlisted in Wet Areas. Owner floor 35 SF vs prior drawing 27 SF and quote Soft vs design AntiSlip finish remain unresolved. Original 214.4 SF across 2 units possible supplier grand-total omission is source audit ONLY, never a payable shortage. Single 40.2 gross SF/unit LEVEL+PAN source is not two independent orders.','',
 '## All thirteen rooms: contractor-owned next evidence and exact owner choices',''])
for n,x in enumerate(register,1):
    lines.extend([f"### {n}. {x['room']} — {x['room_status']} / board R{int(x['latest_round']):03d}",
       '**Retained source/program:** '+x['selected_program_and_fixture'],
       '**Specific physical and procurement hold:** '+x['specific_owner_gc_next_evidence'],
       '**Original tile material-only quote:** $'+x['historical_source_usd_per_unit']+' per copy, 2 copies = $'+x['historical_source_usd_two_units']+'; source 15% gross waste already included. Owner/GC signatures, current Chicago bid and release FALSE.',''])
lines.extend(['## Release order and original evidence controls','',
 '1. Owner alone confirms PH/TX Bath3 tub-versus-walk-in and unselected PH Bath3/TX Bath2/TX Powder2 basins. No substituted selected fixture or new Primary niche.',
 '2. Architect/GC obtain identity-confirmed native 1529 model, measured wall/valve/niche/threshold/tub/pan geometry, physical cut elevations. Current open native model says 1527, not certified 1529.',
 '3. Manufacturer exact SKU/finish written wet-area listing for WALL and NICHE, separate exact RAW NUMERICAL measured wet DCOF certificates for each LEVEL and PAN. Generic Glazzio >0.50, Emser >=0.60 and Daltile TARGET are insufficient under project release standard.',
 '4. GC written approved selected Brizo point/linear rough/liner/membrane/slope/grate, four-plane pitch, water/flood testing, correct tub flange and large-format overhead settings. Dry powder walls and wood floors have PAN N/A.',
 '5. GC matches physical net wall/LEVEL/PAN/niche field-face/back/returns/sill and true 15%-inclusive source gross against actual carton yield, trim LF, exact Chicago in-stock lot/ETA and current complete installed quote. No second PH/TX WC tile row or double waste.',
 '6. Owner reviews 1:1 physical finish/grout/metal samples and signs actual room cost caps; GC release only after all documentation and contracts are satisfied. No current approved selections/purchase orders.',
 '',
 'Evidence references: R013 frozen submission, dispatch and independent collection retain all_critic_scores null; formal weight in separate state/ROUND013_SCORING.json. Previous 13-room R13 construction book has 25 provisional wall studies and 27 original supplier rows; R14 carries exact manufacturer identity correction. This R15 bridge updates decisions for all rooms, not historical original signed reports.',''])
book=OUT/'R15_OWNER_GC_13_ROOM_SCORE_AND_EVIDENCE_BOOK.md'
book.write_text('\n'.join(lines)+'\n',encoding='utf-8')
start=OUT/'START_HERE_R15.md'
start.write_text('# R15 source-linked scored 13-room GC owner release handoff\n\nStart with R15_OWNER_GC_13_ROOM_SCORE_AND_EVIDENCE_BOOK.md. Assign evidence with R15_65_TRADE_ACTIONS_LATEST_SCORES.csv and collect decisions in R15_13_ROOM_SCORED_OWNER_RELEASE_REGISTER.csv. All 3 new PH scored options remain BLOCKED with no champion; earlier signed R12-R14 artifacts remain intact. This package is NOT owner-approved or released for purchasing.\n',encoding='utf-8')
files=[book,OUT/'R15_13_ROOM_SCORED_OWNER_RELEASE_REGISTER.csv',
       OUT/'R15_65_TRADE_ACTIONS_LATEST_SCORES.csv',start]
manifest={
 'date':'2026-11-06','type':'additive_scored_R013_13_room_owner_gc_bridge',
 'room_count':13,'trade_actions':65,'original_supplier_rows':27,
 'original_four_unit_material_only_usd':23572.44,'original_gross_waste_included_pct':15,
 'r013_scoring_sha256':fsha(R/'state/ROUND013_SCORING.json'),
 'r013_submission_sha256':fsha(R/'state/ROUND013_SUBMISSION.json'),
 'r013_collection_sha256':fsha(R/'state/ROUND013_CRITIC_COLLECTION.json'),
 'r14_corrected_manifest_sha256':fsha(R/'deliverables/integrated-r14/MANIFEST.json'),
 'owner_approval':False,'procurement_release':False,'verified_native_1529':False,
 'outputs':{p.name:{'bytes':p.stat().st_size,'sha256':fsha(p)} for p in files}}
(OUT/'MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
print('PASS R15 new 4 signed outputs + manifest, all 13 rooms, 65 trade actions, original 27 rows and $23572.44, all owner/GC release false')
