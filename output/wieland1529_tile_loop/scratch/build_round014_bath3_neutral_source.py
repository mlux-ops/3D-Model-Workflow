"""One-time genuinely new two-Bath3 R014 neutral design board; NO scoring or critic dispatch."""
from pathlib import Path
from decimal import Decimal
import hashlib,json,math,re
R=Path(__file__).resolve().parents[1]
submission=R/'state/ROUND014_SUBMISSION.json'
assert not submission.exists()
research=R/'research/products/R14_BATH3_MAKER_BRANCH_AND_POINT_PAN_20261106.md'
assert research.exists()
source={
 'PH-BATH3':{
  'letters':{'A':'revised','C':'historic'},
  'walls':'Tones Opal 2x20 Glossy',
  'wet_revised':'Tones Sapphire 2x20 Glossy',
  'level_source':'Cortar Bone 12x24 Soft',
  'niche':'Tones Sandstone 2x20 Glossy',
  'wallid':'4724833938636676','floorid':'2473034124951428','nicheid':'1589102831075204',
  'areas':[Decimal('86.2'),Decimal('40.2'),Decimal('8.63')],
  'costs':[Decimal('599.09'),Decimal('271.35'),Decimal('59.98')],
  'lengths':[Decimal('60'),Decimal('27.96'),Decimal('27.96')],
  'wetmaker':'Sapphire wet field individually maker Wet Areas PASS; historic Opal wet field NOT individually approved',
  'drain':'Delta DT062412 CHROME 4-inch SQUARE POINT drain, Hansgrohe Chrome shower set',
  'lav':'PH basin OWNER UNSELECTED',
  'tub':'5.00ft x 2.33ft drawn alcove',
  'wetlink':'elm-tones-sapphire-2x20-wet-approved.md',
  'unit':'Penthouse',
 },
 'TX-BATH3':{
  'letters':{'B':'historic','C':'revised'},
  'walls':'Tones Emerald 2x20 Glossy',
  'wet_revised':'Tones Emerald 2x20 Glossy',
  'level_source':'Cortar Grey 12x24 Soft',
  'niche':'Tones Sandstone 2x20 Glossy',
  'wallid':'6413683798900612','floorid':'4161883985215364','nicheid':'1026152877653892',
  'areas':[Decimal('91.8'),Decimal('42.5'),Decimal('4.89')],
  'costs':[Decimal('638.01'),Decimal('286.88'),Decimal('33.99')],
  'lengths':[Decimal('61.2'),Decimal('31.2'),Decimal('31.2')],
  'wetmaker':'Emerald wet field individually maker Wet Areas PASS for both schemes; no transfer from Opal',
  'drain':'Brizo BT062415-BNX Brilliance Black Onyx 4-inch SQUARE POINT drain and Roccesco shower system',
  'lav':'TX sink selection retained as plumbing specified; no owner tub program selection',
  'tub':'5.10ft x 2.60ft drawn alcove',
  'wetlink':'elm-tones-emerald-2x20.md',
  'unit':'Triplex',
 }
}
rooms={r['id']:r for r in json.loads((R/'state/ROOMS.json').read_text(encoding='utf-8'))['rooms']}
assert set(source)<=set(rooms)
def plain(x):return f'{x:.2f}'
def block(rid,letter,rec,scheme):
    hist=scheme=='historic'
    wall=rec['walls'] if hist else rec['wet_revised']
    level=rec['level_source'] if hist else 'Daltile Prime Dynamic Beige RL21 12x24 Matte LEVEL'
    pan='NONE SPECIFIED until owner walks-in' if hist else 'Daltile Prime Dynamic Beige RL21 1.5-in Hex Matte POINT PAN only if owner signs WALK-IN'
    wet=('FAIL: individual Opal wet-wall authorization absent' if rid=='PH-BATH3' and hist
         else 'PASS WET WALL ONLY: exact listed '+wall+'; no collection-wide permission transferred')
    if rid=='PH-BATH3' and not hist:
        wallfinish='Sapphire blue wet-listed alternate with Sandstone wet-listed niche, field-to-niche single aperture net and Chrome shower fittings'
    elif rid=='TX-BATH3' and not hist:
        wallfinish='Emerald 2x20 existing wet-listed visual palette retained but revised TRUE split LEVEL 12x24 plus separately approved 1.5-inch hex point pan, if WALK-IN'
    else:
        wallfinish=wall+' field with Sandstone niche, original Soft LEVEL and no assumed small format four-plane point-pan'
    floor_gate=('FAIL: original '+level+' has no exact raw numerical measured individual wet LEVEL DCOF'
                if hist else 'FAIL: maker RL21 LEVEL 12x24 Target >=0.42 is NOT exact raw numerical measured individual wet DCOF')
    pan_gate=('FAIL/HOLD if WALK-IN selected: source 12x24 large format unsuitable as unreviewed four-plane SQUARE POINT pan; actual small-format PAN SKU, test and physical section NULL'
              if hist else 'FAIL/HOLD if WALK-IN selected: maker RL21 1.5-in Hex 5/16-in Target >=0.42 is NOT exact raw individual measured wet DCOF; approved four-plane drain, membrane and rough section NULL')
    ah=rec['areas'];cost=rec['costs']
    assert sum(cost)==Decimal('930.42' if rid=='PH-BATH3' else '958.88')
    line3='This specification is a design option for independent evaluation; model geometry, manufacturer compliance, procurement terms and owner approval must be verified.'
    lines=[
      f'# {rid} — Candidate {letter} — complete tile design option','',line3,'',
      '## Current physical/program and source authority (identical review standard)','',
      f'**Unit:** {rec["unit"]}, two copies. **Program conflict:** {rec["tub"]} prior drawing-based alcove versus selected {rec["drain"]} shower drain/controls. Owner has NOT chosen TUB or WALK-IN. Neither alternative chooses one or supplies any bathtub SKU or waste/overflow. {rec["lav"]}. The live Revit process bears title 1527, NOT verified 1529; every wall length, niche location, level/pan area and outlet coordinate below is drawing-origin provisional, not approved geometry.',
      '',
      f'**Material specification:** {wallfinish}. Wet wall field: {wall}, nominal 2x20 Glossy, dry/corner transitions subject to actual 1:1 mock-up. Niche: {rec["niche"]} 2x20 Glossy, independently wet-listed; actual field aperture must be deducted once. LEVEL bath floor: {level}. Sloped four-plane POINT PAN: {pan}. No source pan SF is independently measured. All alternatives are provisional until exact product approved.',
      '',
      '## Source-faithful same-depth five-column, dated material/source/technical table','',
      '| Smartsheet surface ID and source | Maker/format/application and local product evidence | Original gross SF per copy, historical 15% INCLUDED | Original 2026-09-03 material-only quote vs proposed new price | Product-specific wet/physical hard gate |',
      '|---|---|---:|---|---|',
      f'| WALL {rec["wallid"]}: original {rec["walls"]} | {wall}, 2x20 Glossy WET field. [source maker research](../../../../../research/products/{rec["wetlink"]}), [Sandstone wet niche](../../../../../research/products/elm-tones-sandstone-2x20.md) | {plain(ah[0])} gross SF; mathematical /1.15={plain(ah[0]/Decimal("1.15"))} pre-waste estimate NOT measured | Original USD {plain(cost[0])} at 6.95/SF; candidate CURRENT installed/lot/bid NULL | {wet}; true wall plane/trim/valve geometry and actual maker written approval for field version required |',
      f'| LEVEL {rec["floorid"]}: original {rec["level_source"]} | {level}; [individual RL21 maker test/application](../../../../../research/products/R14_BATH3_MAKER_BRANCH_AND_POINT_PAN_20261106.md), distinct original finish | {plain(ah[1])} gross SF historical LEVEL plus possible owner-changed PAN, not two independent full gross floors; /1.15={plain(ah[1]/Decimal("1.15"))} arithmetic ONLY | Original USD {plain(cost[1])} at 6.75/SF; alternate current product quote/carton/installed USD NULL | {floor_gate}; separately approved conditional POINT PAN only if owner WALK-IN |',
      f'| NICHE {rec["nicheid"]}: original {rec["niche"]} | {rec["niche"]} wet listed original field/back/returns; [maker](../../../../../research/products/elm-tones-sandstone-2x20.md) | {plain(ah[2])} gross SF original niche allowance; /1.15={plain(ah[2]/Decimal("1.15"))} estimate only | Original USD {plain(cost[2])} at 6.95/SF; new/current price NULL | PASS individual wet niche listing; field opening deduction/back/returns/sill measurement and sloped waterproof niche sill HOLD |',
      '| Separate wet POINT PAN, rough, wall waterproofing, trims, samples | '+pan+'; [technical maker point/drain evidence](../../../../../research/products/R14_BATH3_MAKER_BRANCH_AND_POINT_PAN_20261106.md) | Actual LEVEL/PAN partition and net pan geometry NULL; do not add twice | Current pan/cartons/installed labor/trim LF/lot/ETA all NULL | '+pan_gate+'; source gross was already 15% loaded once |',
      '',
      '## Designed geometry, grout, edge and installation study (not field elevation)','',
      '| Drawn wall | Prior width × assumed tiled height | Balanced horizontal 2x20 nominal, before actual grout/caliber | Physical installation/coordination hold |',
      '|---|---:|---|---|']
    for i,w in enumerate(rec['lengths']):
        tiles=2 if i==0 else 1
        end=(w-Decimal(20)*tiles)/2
        lines.append(f'| W{i+1} | {plain(w)} × 93 in | {tiles} nominal 20-in full modules + two {plain(end)}-in symmetrical pieces; orient/stack after full 1:1 mock-up | No confirmed niche aperture, control trim or grout-center; field-cuts and Schluter/profile/movement LF unmeasured |')
    lines.extend(['',
      '### TUB branch — owner has NOT approved','',
      'If owner chooses TUB, source drawing alcove dimensions are only a starting geometry reference. Owner selects real bathtub and drain waste/overflow, and architect/GC updates Hansgrohe/Brizo shower rough/interface with the owner, plus flange/tub-wall/niche/threshold waterproof detail. The selected listed square shower drain cannot be a tub waste. LEVEL floor only and separate tiled PAN N/A; no tub/pan materials released and no fabricated tub SKU.',
      '',
      '### WALK-IN branch — owner has NOT approved','',
      f'If owner chooses WALK-IN, retain named {rec["drain"]}; no source tub alcove is certified shower geometry. Provide actual drain throat, center, edge slope, four-plane POINT PAN, liner/membrane, mortar bed/mesh/carrier, curb-glass, threshold and flood test with tile maker/GC written approval. {pan_gate}. Actual net PAN and LEVEL floor split is NULL and cannot be derived by treating all original gross as two distinct pools.',
      '',
      '## Installer top-fix actions, professional/commercial release gates','',
      f'- Wet walls: {wet}. Niche Sandstone maker Wet Areas PASS, not floor compliance; relief/Opal approvals are individual and non-transferable. Chrome/Black Onyx original plumbing schedule not changed.',
      f'- Flooring: {floor_gate}. {pan_gate}. Original v4 LEVEL Soft fails exact raw measured wet DCOF regardless of aesthetic or Target literature; proposed RL21 maker Target also fails exact raw test. No physical shower-pan approval.',
      '- Maker current RL21 1.5-in Hex thickness 5/16-in versus older 1/4-in brochure; manufacturer web grout 1/8-in recommendation. Chip/caliber/joint/mesh and selected 4-in SQUARE POINT throat/liner must be checked in actual sourced/approved assembly. Do not transfer Primary Brizo 48-in linear tile-in 7-18mm frame to this point-drain room.',
      '- Retain two copies and historical original 15% included once; this is source audit, not installed cost. Alternate new level, pan, niche and wall carton coverage, purchase cases, actual Chicago material lot, lead and complete installed bid all NULL. Never apply another 15%, duplicate niche face, treat old floor gross as both LEVEL and PAN, or invent supplier credit.',
      '- Source hierarchy: actual owner decision > individual approved plumbing > 2026-08-26 fixture v3.2 and v4 tile source > correct native 1529 geometry (not verified) > maker SKU/finish > 14 market listings/nine independent buildings. 405 W Armitage four listings = ONE precedent; Old Town first, LP/Gold Coast secondary. PH $2.8M, TX $2.7M, band $2.4M-$3.2M; no authenticated bathroom tile imagery.',
      '- Required signed releases: owner tub/walk-in and PH basin where applicable, architect/GC dimensioned wall/niche/edge shop, manufacturer exact maker wet-area letter and exact raw numerical LEVEL/PAN wet DCOF lab points, manufacturer approved drain/waterproof/flood detail, current independent Chicago SKU/cartons/lot/ETA/installed quote and owner room budget cap. Owner approval and procurement release FALSE.',
      '',
      '## Local maker, geometry, market, owner authority for every critic','',
      '- [Current exact R014 maker/drain and wall-cut analysis](../../../../../research/products/R14_BATH3_MAKER_BRANCH_AND_POINT_PAN_20261106.md); [Daltile RL21 maker](https://www.daltile.com/products/stone-look/prime/dynamic-beige); [Glazzio HNC6615 previous independent maker](https://www.glazziotiles.com/default.aspx?itemcode=HNC6615&page=item+detail); [Glazzio HNC6715 earlier 2x2](https://www.glazziotiles.com/default.aspx?itemcode=HNC6715&page=item+detail).',
      '- [Official comparables (14 entries, 9 buildings)](../../../../../research/comps/COMPS.md); [owner feedback](../../../../../state/OWNER_FEEDBACK.md). Relative links and 1529 source data are research/owner references, NOT permission to access score, mapping, prior rounds or another critic.',
    ])
    return '\n'.join(lines)+'\n'
allfiles={}
for rid,rec in source.items():
    r=rooms[rid]
    assert r['status']=='blocked' and r['champion_id'] is None and r['owner_status'] is None
    assert r['last_round']==11 and not (R/'rooms'/rid/'board/round-014').exists()
    basedir=R/'rooms'/rid/'board/round-014'
    (basedir/'candidates').mkdir(parents=True,exist_ok=False)
    for letter,scheme in rec['letters'].items():
        (basedir/'candidates'/f'{letter}.md').write_text(block(rid,letter,rec,scheme),encoding='utf-8')
    (basedir/'_key.json').write_text(json.dumps({letter:('historic v4 source' if kind=='historic' else 'revised individual maker Sapphire/Emerald wall and Prime RL21 distinct point system') for letter,kind in rec['letters'].items()},indent=2)+'\n',encoding='utf-8')
    allfiles[rid]={}
    for letter in rec['letters']:
        p=basedir/'candidates'/f'{letter}.md'
        b=p.read_bytes()
        allfiles[rid][letter]={'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b),'file':str(p.relative_to(R)).replace('\\','/')}
assert len(allfiles)==2 and sum(len(v) for v in allfiles.values())==4
payload={
 'round':14,'as_of':'2026-11-06','phase':'2-board',
 'rooms':['PH-BATH3','TX-BATH3'],
 'source_authority':'2026-09-03 original 6 Smartsheet tile rows and owner selected square shower drain vs tub conflict, maker individual sources, provisional geometry',
 'freeze_purpose':'Only source-neutral R014 PH/TX Bath3 candidates frozen; reviewer pre-dispatch requested, no critic dispatch, no weighted scoring, no champion',
 'candidate_files':allfiles,'private_key_paths':['rooms/PH-BATH3/board/round-014/_key.json','rooms/TX-BATH3/board/round-014/_key.json'],
 'critic_seats':{'market':0.30,'design':0.25,'build':0.25,'cost':0.20},
 'critic_dispatch':'NOT DISPATCHED',
 'all_critic_scores':None,'weighted_scoring':None,'reviewer_preflight_verdict':None,
 'owner_tub_vs_walkin':None,'ph_sink_owner_selected':False,'owner_approved':False,'procurement_release':False,
 'original_gross_15pct_waste_included_once':True,
 'original_per_copy_usd':{'PH-BATH3':930.42,'TX-BATH3':958.88},
 'correct_native_1529_verified':False
}
submission.write_text(json.dumps(payload,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print('PASS 4 equal-depth R014 Bath3 frozen neutral source candidates + private mappings, SHA/bytes, original material rows, scores NULL; awaiting independent Reviewer')
print('R014_SUBMISSION_SHA',hashlib.sha256(submission.read_bytes()).hexdigest())
