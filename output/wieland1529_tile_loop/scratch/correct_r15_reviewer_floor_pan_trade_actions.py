"""One-time R15 source-specific floor/PAN trade action FIX, signed SHA audit."""
from pathlib import Path
import csv,hashlib,json
R=Path(__file__).resolve().parents[1]
D=R/'deliverables/integrated-r15'
name='R15_65_TRADE_ACTIONS_LATEST_SCORES.csv'
target=D/name
manifest=D/'MANIFEST.json'
audit=R/'state/ROUND013_R15_REVIEWER_FLOOR_PAN_SOURCE_FIX.json'
assert target.exists() and manifest.exists() and not audit.exists()
def fp(p):
    b=p.read_bytes()
    return {'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}

before=json.loads(manifest.read_text(encoding='utf-8'))
assert fp(target)==before['outputs'][name]
old_manifest=fp(manifest)
unchanged={n:v for n,v in before['outputs'].items() if n!=name}
assert all(fp(D/n)==v for n,v in unchanged.items())

room_detail={
 'PH-PRIMARY':'Selected Brizo BT0734816-BNX Black Onyx 48-in LINEAR/mandatory BR73480, separate LEVEL bath/shared PH WC and sloped LINEAR PAN. Candidate Prime RL21 12x24 LEVEL (3/8-in) and 1.5-in hex Matte PAN (current maker 5/16-in, old brochure 1/4-in conflict): separately obtain exact raw measured wet DCOF, actual pan/level area, tile+carrier+setting thickness and manufacturer written waterproof membrane/rough/slope/flood section. Factory solid grate study bypasses decorative tile-in insert ONLY; no assumed shim or certified assembly. NO Primary niche.',
 'PH-BATH2':'Selected Duravit 700332000000090 59-in actual TUB with Hansgrohe Matte White; NO tiled shower PAN and no linear/square point shower drain study. Verify manufacturer tub flange/wall waterproof sill, true W1 59.496-in versus nominal tub 59-in TOTAL 0.496-in rough-fit HOLD and exact raw numerical wet DCOF for bath LEVEL floor alone.',
 'PH-BATH3':'Owner tub-versus-WALK-IN program UNSELECTED: source tub alcove conflicts with selected Delta DT062412 Chrome SQUARE POINT shower drain. Do not approve, order or assign point shower drain as bathtub waste. First obtain owner program, correct 1529 geometry and actual plumbing/drain rough; then require LEVEL raw DCOF and, only if walk-in selected, separately sized/tested POINT PAN and written membrane/flood section.',
 'PH-BATH4':'Actual selected WALK-IN Brizo BT062415-BNX Black Onyx 4-in SQUARE POINT (NOT tub or primary linear). Proposed Prime RL21 12x24 LEVEL and 1.5-in Hex Matte (current maker 5/16-in) four-plane POINT PAN are distinct raw wet numerical DCOF test and shop section gates; NO generic 2x2 claim. Resolve owner 35-SF vs old 27-SF source, Soft vs AntiSlip floor finish and source 40.2 gross pooled LEVEL+PAN; exact square throat/membrane/slope/flood test.',
 'PH-POWDER':'Scheduled DRY relief vanity tile and WOOD floor; NO tiled shower PAN, no Brizo shower drain. Verify Brizo Luxe Gold wall-faucet escutcheon on flat approved mounting plane over Earth Lines relief, measured edge/cut and joint. Tile LEVEL wet DCOF not applicable to this dry feature wall; grout/paint/water splash protection remain GC holds.',
 'PH-WC':'Shared PH WC floor derives from PH-PRIMARY LEVEL source gross. No independent PAN or separately ordered WC tile. Verify true WC/Primary LEVEL split without duplicate original 15% waste, level waterproof/threshold transition and same selected raw numerical LEVEL wet DCOF test.',
 'TX-PRIMARY':'Selected Brizo BT0734816-BNX Black Onyx 48-in LINEAR with separately required BR73480 rough; NO Primary niche. Source Cortar Clay Soft LEVEL/shared TX WC and AntiSlip LINEAR PAN; revised Emser Trosa LEVEL and distinct Prime RL21 1.5-in hex LINEAR PAN are option-specific. Maker hex current 5/16-in versus old 1/4-in brochure: neither implies approved tile-in/rough fit. Require exact tested raw wet LEVEL and PAN DCOF, actual footprint, compatible written rough/membrane/channel/slope/flood section.',
 'TX-BATH2':'Selected Duravit actual TUB with Hansgrohe CHROME, basin owner UNSELECTED; NO tiled shower PAN. Do not transfer Brizo 48-in linear or Prime mosaic into this room. Verify tub flange/waterproof niche, raw measured wet DCOF for LEVEL Cortar Clay Soft or revised Emser Trosa and true 1529 dimensions.',
 'TX-BATH3':'Owner tub versus WALK-IN UNSELECTED: source tub alcove conflicts with selected Brizo BT062415-BNX Black Onyx SQUARE POINT shower drain/controls. Do not use point shower drain as tub waste. Owner must first choose program, then remeasure tub/point rough and require exact raw numerical LEVEL test and separately raw POINT PAN if actual walk-in approved, plus membrane/flood section.',
 'TX-BATH4':'Selected Duravit TUB and Hansgrohe MATTE WHITE; NO tiled shower PAN, no Brizo point/linear shower rough. Source Cortar Bone Soft LEVEL versus revised Emser Capisco Trosa F08CAPITR1224M LEVEL, each needs exact raw numeric wet DCOF certificate; verify tub flange, niche edge/back/returns and measured current trade quote.',
 'TX-POWDER':'Scheduled DRY Haze Camel/Wheat 70:30 vanity wall with WOOD floor; NO tiled shower PAN and no shower drain. Verify 70:30 actual wall area and per-color carton/lot/grout/current installed bid; retain selected Hansgrohe wall faucet/rough. No false generic Brizo linear or 2x2 point mosaic requirement.',
 'TX-POWDER2':'Scheduled DRY Indigo Edge 6x6 vanity wall with WOOD floor; basin remains owner UNSELECTED, selected Hansgrohe Tecturis E 73072341 Brushed Black Chrome is DECK-mounted. NO tiled shower PAN or point/linear shower drain. Obtain basin/vanity coordinates then dry relief cut/mirror/edge and signed mockup; no assumed basin.',
 'TX-WC':'Shared TX WC inherits TX-PRIMARY LEVEL floor, no separately ordered WC tile and no independent shower PAN. Confirm physical shared WC floor area, original 15%-loaded source quantity only once and exact manufacturer raw wet numerical LEVEL test; Brizo LINEAR PAN belongs to Primary shower, not WC.',
}
with target.open('r',encoding='utf-8-sig',newline='') as f:
    reader=csv.DictReader(f)
    fields=reader.fieldnames
    rows=list(reader)
assert len(rows)==65 and len(room_detail)==13
affected=[]
for row in rows:
    if row['group']!='floor_pan_and_drain':
        continue
    rid=row['room']
    assert rid in room_detail
    assert 'Brizo LINEAR primaries require BR73480' in row['measurable_next_closure']
    row['measurable_next_closure']=room_detail[rid]
    affected.append(rid)
assert len(affected)==13 and set(affected)==set(room_detail)

prior=fp(target)
with target.open('w',encoding='utf-8-sig',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=fields)
    writer.writeheader();writer.writerows(rows)
assert fp(target)!=prior
assert sum(x['group']=='floor_pan_and_drain' for x in rows)==13
assert all(x['purchase_release']=='False' and x['owner_approval']=='False' and x['exact_gc_approval']=='False' for x in rows)
before['outputs'][name]=fp(target)
manifest.write_text(json.dumps(before,indent=2)+'\n',encoding='utf-8')
assert all(fp(D/n)==v for n,v in before['outputs'].items())
audit_data={
 'as_of':'2026-11-06','round':13,'reviewer':'worker-14',
 'precise_fix':'13 originally copied R13 generic floor_pan_and_drain closure strings in new R15 CURRENT trade register replaced by exact individual room program, manufacturer, LINEAR/POINT/TUB/DRY/WC distinctions; original R13 remains signed and untouched',
 'affected_rooms':affected,
 'old_action_file':prior,'new_action_file':fp(target),
 'unchanged_three_other_outputs':unchanged,
 'old_manifest':old_manifest,'new_manifest':fp(manifest),
 'old_r013_candidate_and_critic_sha_unchanged':True,
 'r013_scoring_receipt_unchanged':True,
 'owner_approval':False,'procurement_release':False
}
audit.write_text(json.dumps(audit_data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print('PASS precise reviewer R15 13 room floor/PAN group action FIX, other 3 signed outputs unchanged')
print('R15 manifest new sha',fp(manifest)['sha256'])
