"""Prepare R017 blind wet-bath source only. NO critic dispatch or weighted scores."""
from pathlib import Path
import hashlib,json,re

R=Path(__file__).resolve().parents[1]
base=R/'research/products/R17_FOUR_WET_ROOM_CONDITIONAL_ASSEMBLY_SOURCE_20261106.md'

research='''# R017 four wet-bath controlled technical source — 2026-11-06

This is **neutral manufacturer and construction evidence for individual room designs**, not a prior-round review, weighted score or owner package. Individual design candidates MUST be evaluated only against their specific disclosed physical system. Four current focus rooms: PH-BATH3, TX-BATH3, PH-BATH4, PH-PRIMARY. Two instances per room; true native 1529 model and all finish/rough locations unknown (open Revit title 1527). Source quoted material-only data is 2026-09-03 history, not current local supplier bid or an option price. Original gross includes 15% waste exactly once. All current 1529 net/case, Chicago availability, lead, installed GC bid and owner cap null.

## Official technical references, each distinct

- [ELM Tones Sapphire individual manufacturer page](https://www.elmsurfaces.com/product/sapphire-tones): 2x20 Glossy, individually Wet Areas listed for shower/tub WALL. It does not confer wet application on Tones Opal.
- [ELM Tones Emerald individual manufacturer page](https://www.elmsurfaces.com/product/emerald-tones): 2x20 Glossy, individually Wet Areas listed for TX shower/tub WALL.
- [ELM Tones Sandstone individual manufacturer page](https://www.elmsurfaces.com/product/sandstone-tones): 2x20 Glossy, separately individually Wet Areas listed, conditional wet NICHE back/returns/sill; actually measure opening field deduction once and niche faces separately.
- ELM Tones Opal 2x20 Glossy individual wet WALL authority **NOT available**; fail for wet walls, regardless of Sapphire approval.
- ELM Cortar Bone flat Soft 24x48 individual wet WALL maker listing supported by [source research](elm-cortar-bone-flat-24x48.md); ELM Cortar Bone Ribbed 24x48 relief individual wet WALL listing **NOT established** ([specific relief research](elm-cortar-bone-ribbed-24x48-relief.md)). No permission transfer between relief and flat. Clara Caviar individual NICHE wet listing absent; ELM [Soho Black 2x10](https://www.elmsurfaces.com/product/soho-black) individually Wet Areas listed (see [source](elm-soho-black-2x10.md)).
- [Daltile Prime RL21 Dynamic Beige](https://www.daltile.com/products/stone-look/prime/dynamic-beige): distinct LEVEL 12x24 Matte USA ~3/8in and separate conditional 1.5in hex Matte Mexico nominal 5/16in for SQUARE POINT or 48in LINEAR PAN if approved maker applications. Older nominal 1/4in hex and 1/8-vs-3/16 grout recommendation source conflict; distinguish per exact current order variant. Manufacturer `Target >=0.42` versus older brochure linear Target differences are **NOT measured raw numerical wet lab report**. No exact original raw wet lab on either size/finish.
- [Glazzio HNC6715 Harmonic Rondo 2x2 matte hex maker](https://glazziosurfaces.com/products/harmonic-rondo-2x2-matte-hex-mosaic): individual maker shower-floor suitability; maker DCOF `>0.50` is bound, NOT exact raw numeric measured lab result; reported 4.85 SF/carton is a research lead not a confirmed current Chicago lot/case. [HNC6615 12x24](https://www.glazziotiles.com/default.aspx?itemcode=HNC6615&page=item+detail) LEVEL `>0.50` similarly not raw individual lab.
- [Selected Delta DT062412 installation PDF 113919 Rev B](https://media.deltafaucet.com/MandI/113919%20Rev%20B.pdf): PH Bath3 Chrome 4in SQUARE POINT shower drain, conditional only if owner WALK-IN. A shower POINT drain is NOT tub waste.
- [Selected Brizo BT062415-BNX installation PDF 113920 Rev C](https://media.brizo.com/MandI/113920%20Rev%20C.pdf): PH Bath4 WALK-IN and conditional TX Bath3 WALK-IN each Black Onyx 4in SQUARE POINT. Factory traditional clamped-liner/preslope detail is not blanket bonded-membrane compatibility.
- [Brizo BT0734816-BNX](https://www.brizo.com/bath/product/BT0734816-BNX) selected PH Primary Black Onyx 48in reversible LINEAR, separate [BR73480 rough](https://www.brizo.com/bath/product/BR73480). Solid BNX vs tile-in grate are selected manufacturer's installation configuration studies; tile-in insert 7–18mm. No new Primary NICHE, shared PH WC LEVEL once. Solid grate does not establish whole membrane/liner/wet lab compliance.

## Frozen owner/plumbing interfaces, not board roles

PH Bath3 and TX Bath3 owner TUB versus WALK-IN UNSELECTED. In either TUB condition exact actual owner-selected bathtub, dedicated tub waste/overflow, tub flange/shop and revised approved plumbing are **NOT SELECTED**; shower PAN N/A. In WALK-IN use only each room's actual selected 4in square POINT drain, independent four-plane small-format PAN, manufacturer-approved exact rough/liner/membrane and raw numerical measured PAN wet DCOF. PH Bath3 basin owner UNSELECTED; do not import that into TX Bath3. PH Bath4 actual WALK-IN point with owner floor 35 SF vs old drawing 27 SF, historic Soft vs Anti-Slip source conflict and original 107.2 SF wall/copy x2 vendor total audit only. PH Primary always 48in BNX LINEAR with separate selected Duravit tub, no extra shower niche.

**Lab gate:** For bath LEVEL floor and each actual or conditional LINEAR/POINT PAN product obtain original manufacturer exact SKU/color/finish *raw measured numerical wet DCOF* with specimen, test method, date and wet use. No product passes by a Target, lower bound, public merchant numeric or application alone. Individual wet WALL/NICHE permissions separate; no approval transfer. All selected fixture and non-selected owner program flags unchanged. No 1527 model dimension certified as 1529, no new purchases.
'''

data={
 'PH-BATH3':dict(letters=['A','C'],key={'A':'maker-wet-Sapphire-RL21-two-branch','C':'source-Opal-Bone-Soft-two-branch'},basis='One copy original 86.2 SF wall Opal $599.09; 40.2 SF combined source floor Bone Soft $271.35; Sandstone niche 8.63 SF $59.98; room material-only $930.42. All original 15% gross already once.',options={
  'A':dict(wall='ELM Tones Sapphire 2x20 Glossy wet WALL + Tones Sandstone 2x20 niche; individual maker Wet Areas YES for each exact color/finish; source Opal approval cannot transfer.',level='Daltile Prime RL21 12x24 Matte as conditional LEVEL, 3/8in USA; maker Target wet rating, exact raw measured test null/FAIL.',pan='Daltile Prime RL21 1.5in hex Matte 5/16in Mexico as conditional four-plane POINT PAN if WALK-IN; maker Target not actual raw lab; 1/4-vs-5/16 thickness and grout revisions need physical order/version check.',detail='Stacked or centered Sapphire 20in modules around actual Chrome thermostatic trim; Sandstone recess must be individually waterproofed and one niche opening deducted; separate calibrated grout and tile edge mockup.'),
  'C':dict(wall='ELM Tones Opal 2x20 Glossy wet WALL permission UNESTABLISHED/FAIL, Tones Sandstone wet NICHE YES; do not transfer Sapphire source to Opal.',level='ELM Cortar Bone Soft source LEVEL conditional; individual raw numeric wet lab NULL/FAIL despite dated price.',pan='No exact physical POINT shower PAN SKU specified for any WALK-IN branch; PAN maker wet app and raw numeric test FAIL/HOLD; no fictitious mosaic authorized.',detail='Opal horizontal or vertically oriented 20in WALL tile must undergo exact individual maker wet proof, full cut/grout/Chrome valve/edge mockup before entering shower; niche independently wet-listed only.')}),
 'TX-BATH3':dict(letters=['B','C'],key={'B':'source-Emerald-Grey-Soft-two-branch','C':'Emerald-RL21-point-two-branch'},basis='Original one copy Emerald 91.8 gross SF $638.01; Cortar Grey Soft floor 42.5 SF $286.88; Sandstone niche 4.89 SF $33.99; room $958.88/copy; original 15% gross once.',options={
  'B':dict(wall='ELM Tones Emerald 2x20 Glossy WALL maker individual wet YES, Tones Sandstone 2x20 NICHE maker wet YES.',level='ELM Cortar Grey Soft source LEVEL; exact individual raw numerical wet DCOF absent/FAIL.',pan='No specifically factory-verified small-format POINT PAN tile or raw numerical wet DCOF exists for WALK-IN branch; separate 4-plane PAN FAIL/HOLD.',detail='Black Onyx selected Brizo Roccesco fixtures and 4in square shower drain when WALK-IN, emerald wet walls with Sandstone niche; full 20in module/factory-approved grout, cuts and trim still held.'),
  'C':dict(wall='ELM Tones Emerald 2x20 Glossy wet WALL maker YES plus individually wet-listed Sandstone niche; no inferred approval for other colors.',level='Daltile Prime Dynamic Beige RL21 12x24 Matte conditional LEVEL product, original raw numerical wet DCOF absent despite maker Target.',pan='Daltile Prime RL21 1.5in hex Matte conditional 4-plane POINT PAN only if owner WALK-IN; maker shower-floor application Target is not raw measured wet DCOF, thickness/joints exact variant hold.',detail='Contrast BNX Roccesco with Emerald/Sandstone and matte RL21 individually separated floor planes; detail selected Brizo BT062415-BNX 4in point factory liner and correct drain center, not tub waste.')}),
 'PH-BATH4':dict(letters=['A','C'],key={'A':'wet-listed-flat-Bone-Soho-Glazzio-point','C':'source-full-Ribbed-Caviar-source-floor'},basis='Historic per copy full Bone Ribbed 107.2 gross SF $790.06; floor 40.2 gross SF $271.35 (original Soft vs AntiSlip conflict); Clara Caviar niche 8.63 gross SF $290.83; total $1352.24. Original two-copy wall 214.4 SF vendor-total audit not payable shortage. Owner floor 35 SF versus source drawing 27 SF.',options={
  'A':dict(wall='Individually maker Wet Areas-listed flat Cortar Bone Soft WALL and individually wet Soho Black 2x10 NICHE; does NOT inherit approval for full Bone Ribbed/Caviar.',level='Glazzio HNC6615 12x24 DCOF Matte conditional LEVEL; maker >0.50 reported lower bound NOT individual raw wet lab result.',pan='Glazzio HNC6715 2x2 matte hex maker shower-floor listed, conditional four-plane POINT PAN with selected BNX square; >0.50 bound NOT raw lab, exact wet test FAIL.',detail='Full-height light flat Bone wet wall + bounded dark Soho wet niche; physical BNX 4in square POINT and 1:1 four-plane PAN/curb/glass, 35/27 actual survey before finish cuts.'),
  'C':dict(wall='Full wet wall ELM Cortar Bone Ribbed 24x48 relief individual maker wet authorization NOT shown/FAIL; historical Clara Caviar wet NICHE permission NOT shown/FAIL.',level='Historical Cortar Charcoal Soft vs AntiSlip floor source mismatch unresolved, exact manufacturer raw measured LEVEL wet DCOF absent/FAIL.',pan='No separately specified original small-format POINT shower PAN floor tile with exact raw wet DCOF; large format 12x24 source floor cannot simply be carried into four-plane point without maker-approved shop. FAIL.',detail='Full 107.2 SF/copy relief source field and 8.63 SF/copy Caviar source niche are historical design study only; relief/niche wet authorization, drain/slope, owner 35/27 and grand-total audit all unresolved.')}),
 'PH-PRIMARY':dict(letters=['B','C'],key={'B':'wet-listed-flat-Bone-RL21-linear-solid-BNX-grate','C':'source-Reed-Bone-Soft-AntiSlip-linear'},basis='Original one copy Bone Soft with Reed shower/ceiling wall total 143.0 gross SF $1164.02; shared PH-WC included LEVEL plus pan source 135.6 gross SF $1060.39, $2224.41/copy. Unpriced Primary niche history excluded NO SCOPE/NO ORDER.',options={
  'B':dict(wall='Individually maker wet-listed flat ELM Cortar Bone Soft WALL conditional, no Reed relief wet approval transferred; separate correct wet-ceiling installation holds.',level='Daltile Prime RL21 12x24 matte LEVEL including PH-WC once, maker Target not individual raw wet lab, FAIL.',pan='Distinct RL21 1.5in hex matte LINEAR shower PAN conditional, maker Target/brochure application not individual raw test FAIL; 1/4-vs-5/16, 1/8-vs-3/16 version conflicts. Selected BNX solid grate rather than tile-in insert CONFIGURATION STUDY using same 48in BT0734816-BNX/BR73480.',detail='Quiet flat Bone wall for warm Black Onyx Roccesco, dry area separate Duravit tub. Exact BR73480 secondary drain, slab-to-linear edge/membrane, movement joint, low point and flush solid BNX 48in grate section to be designed; no Primary niche.'),
  'C':dict(wall='Source Cortar Bone Soft flat + Bone Reed relief full wet design; Reed individual maker wet authorization ABSENT/FAIL; no wet ceiling assumptions certified.',level='Source Cortar Bone Soft LEVEL shared PH-WC once; precise SKU raw wet test absent/FAIL.',pan='Source Cortar Bone AntiSlip 12x24 sloped linear shower PAN description, selected BNX 48in LINEAR/BR73480; individual raw measured wet lab absent/FAIL, exact slope/format physical system unapproved.',detail='Source relief feature and 12x24 linear pan require exact wall wet permissions, physical slope/grout/cut, selected BR73480/48in BNX, wet ceiling and no niche. No implicit waterproof or pan release.')})
}

def sha(path):
 b=path.read_bytes();return {'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
assert not base.exists(),'Do not regenerate frozen common R017 maker study'
base.write_text(research,encoding='utf-8')

common='This option is submitted for independent blind technical review ONLY; no historical/challenger status, prior results, owner approval, original source price substitution or authorization to order may be inferred.'
files={};keys={}
for room,meta in data.items():
 ge=json.loads((R/'rooms'/room/'geometry.json').read_text(encoding='utf-8'))
 a=R/'rooms'/room/'board/round-017'; candidate=a/'candidates';candidate.mkdir(parents=True,exist_ok=True)
 wall_lines=[]
 for w in ge['tiled_walls']:
  wid=w['id'];width=w['length']['value']*12;height=w['tiled_height']['value']*12
  wall_lines.append(f'{wid}: drawing-only {width:.3f} in W × {height:.2f} in tile height, original opening/niche location, edge trim and true 1529 geometry UNKNOWN; measured NET = actual field face - actual openings - single niche aperture + independently tiled returns/back/sill once')
 files[room]={}
 for letter in meta['letters']:
  opt=meta['options'][letter]
  content=[f'# {room} — Candidate {letter} — complete independent wet design option','',common,'',
   '## 1. Individually named tile, source and technical permission',
   '', '**WET WALL / NICHE:** '+opt['wall'],
   '', '**Bath LEVEL floor:** '+opt['level'],
   '', '**Independent sloped POINT/LINEAR PAN:** '+opt['pan'],
   '', '## 2. Actual owner fixture and program compatibility',
   '', 'Current selected fixture numbers, finish and distinct owner decisions: [room plumbing](../../../plumbing.json). Real 1529 source geometry: [room geometry](../../../geometry.json). Shared [neutral manufacturer evidence](../../../../../research/products/R17_FOUR_WET_ROOM_CONDITIONAL_ASSEMBLY_SOURCE_20261106.md).',
   '', '**Non-transferable program:** PH/TX BATH3 owner TUB-vs-WALK-IN UNSELECTED. TUB requires newly owner-selected tub and dedicated tub waste/overflow with no tiled shower PAN; selected Delta/Brizo square shower drain MUST NOT be called tub waste. WALK-IN only retains owner-selected SQUARE POINT and independently approved 4-plane PAN. PH-BATH4 remains actual WALK-IN 4-in SQUARE POINT; PH-PRIMARY remains selected Brizo BNX 48-in LINEAR + BR73480 with separate Duravit tub, NO added niche, PH WC LEVEL included once. Room-specific rule applies, no unrelated fixture substitution.',
   '', '## 3. Physical wall tile, glass, drain and waterproofing execution',
   '', opt['detail'],
   '', '**Original source drawing W1–W3 only (NOT current certified model):** '+ '; '.join(wall_lines)+'.',
   '', '**Field shop section:** require architect-plumber-tile installer/GC signed actual wall dimensions, drain location and clearances, calibrated tile width/joint, actual finish-to-substrate thickness, selected factory rough/membrane/liner/clamp or linear channel system, preslope and pan build-up, waterproof wall-to-floor/curb/tub flange, all mirror/valve/glass anchors, sloped niche sill/returns, changes-of-plane movement seals, perimeter terminations and full-size drain/grout mockup. The open 1527 model CANNOT certify actual 1529. No real field inspection/flood test performed.',
   '', '## 4. Exact SKU wet gate / separate math and historical source cost',
   '', '**Raw exact wet DCOF:** Each physically applicable LEVEL tile AND each separate conditional/actual POINT or LINEAR PAN tile requires original manufacturer individual exact numeric measured wet test with specimen, method, date and color/format. Manufacturer Target/lower bound is NOT raw measurement. Unknown numeric = HARD FAIL. Bath3 TUB PAN N/A, Bath3 WALK-IN PAN conditional FAIL until maker report, PH4 point/PH Primary linear PAN required FAIL. WALL/NICHE individual Wet Areas application cannot be inferred from a collection/flat tile or alternate color.',
   '', '**Historical source comparator applicable to BOTH neutral design options:** '+meta['basis'],
   '', '**New actual material/case/price:** measured wall NET from each specific cut/opening + niche deducted/backs once, separately measured LEVEL floor vs real PAN net once, individual one-time new cut allowance only on newly surveyed NET, same exact SKU/color/lot supplier verified carton SF, `ceil(approved need / exact verified case SF)`, current Chicago shade-stock/ETA, freight/tax/setting/waterproof labor and complete GC bid all `null`. Historical source 15% gross waste is already counted ONCE. No existing quoted SF multiplied again by 1.15 or applied twice to LEVEL and PAN. No owner budget cap, current local bid or actual factory lot asserted.',
   '', '## 5. Old Town buyer / 1:1 mockup and unresolved hard gates',
   '', '**Buyer study:** owner PH $2.8M / TX $2.7M; price comparison $2.4M–$3.2M; 14 listings represent 9 distinct buildings (405 W Armitage OT01–OT04 one precedent), Old Town primary, Lincoln Park/Gold Coast labeled adjacent. No authenticated competitor-tile photographs. Require independently witnessed full wet wall/niche/metal/grout/finish sample, true wall calibration and owner-signed day/night look before design change.',
   '', '**top_fix:** obtain true owner tub/walk-in branch where required, individual maker exact wet WALL/NICHE proof, raw measured LEVEL/PAN DCOF, manufacturer-approved drain/rough waterproof assembly, correct verified 1529 dimensions and Chicago installed bid before any board champion can pass.',
   '', '**gate_flags:** wet areas as individually listed above; every applicable LEVEL and PAN raw numeric wet DCOF FAIL; manufacturer wet WALL/NICHE unlisted if specifically named above FAIL; floor format/drain/rough/geometry/shop HOLD; owner Bath3 program unknown, owner cap NULL, Chicago local stock/installed bid NULL. Source historic rates dated only; every owner/architect/GC/purchaser release FALSE. **No critic score or weighted score is claimed.**',
  ]
  path=candidate/f'{letter}.md'
  assert not path.exists(),'R017 source already prepared; do not overwrite'
  path.write_text('\n'.join(content)+'\n',encoding='utf-8')
  files[room][letter]={'path':str(path.relative_to(R)).replace('\\','/'),**sha(path)}
 key=a/'_key.json';assert not key.exists()
 key_data={'round':17,'room':room,'restricted_to':'prime and independent standing non-Pro Reviewer, NEVER critic','mappings':meta['key'],'owner_approved':False,'weighted_scoring':None}
 key.write_text(json.dumps(key_data,indent=2)+'\n',encoding='utf-8')
 keys[room]={'path':str(key.relative_to(R)).replace('\\','/'),**sha(key)}

submit={
 'round':17,'as_of':'2026-11-06','phase':'1-comps SOURCE_PREPARED_AWAIT_INDEPENDENT_PREDISPATCH',
 'focus_rooms':list(data),'blind_source_candidates':files,
 'confidential_prime_only_mappings':keys,
 'shared_maker_research':{'path':str(base.relative_to(R)).replace('\\','/'),**sha(base)},
 'owner_approved':False,'verified_native_1529':False,
 'all_critic_scores':None,'R017_weighted_scoring':None,'predispatch_reviewer_verdict':None,
 'critic_dispatch':'NOT_DISPATCHED','four_authentic_original_seat_dispatch_authorized':False,
 'R014_critic_files':6,'R014_required':8,'original_design_worker9':'FAILED',
 'R014_scoring':None,'R015_dispatch':'HOLD','R015_scoring':None,'R016_dispatch':'NOT_DISPATCHED','R016_scoring':None,
 'R016_source_sha256':'dcc6e38897a0f92f65c372c2bc9526b54ddb139e9bdfff1788522e3007599d6a',
 'R022_manifest_sha256':'32e5ceb807e33e642680dec47aa378d21d5ba9f7b05462214277cb89e7d76df1',
 'R023_manifest_sha256':'2eec511f9b6920fd7553e634a1178b85f43f72bf4abb26a832114bc8d7a80ee5',
 'historical_four_unit_material_only_usd':'23572.44','original_15pct_waste_once':True,
 'owner_release':False,'GC_release':False,'purchase_release':False,
 'new_materials_are_conditional':True,'reviewer_source_preflight_pending':True,
}
path=R/'state/ROUND017_SUBMISSION.json';assert not path.exists()
path.write_text(json.dumps(submit,indent=2)+'\n',encoding='utf-8')
assert len(files)==4 and sum(len(x) for x in files.values())==8 and len(keys)==4
assert all((R/f['path']).exists() for xs in files.values() for f in xs.values())
print('PASS R017 8 neutral wet-bath packets / four private mappings and common maker source PREPARED ONLY. No critic dispatch, scores, owner program or PO.')
print('R017_SOURCE_SHA',sha(path)['sha256'])
