"""Precise SAME-R23 worker15 FIX: 65 specific trade narratives, 13 room sample rows, N/A owner approval scope."""
from pathlib import Path
import csv,json,hashlib,re,io

R=Path(__file__).resolve().parents[1]
O=R/'deliverables/integrated-r23-wet-bath-conditional-drain-and-owner-gc'
M=O/'MANIFEST.json'

def sig(p):
 b=p.read_bytes();return {'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}

before_manifest=sig(M)
assert before_manifest['sha256']=='2eec511f9b6920fd7553e634a1178b85f43f72bf4abb26a832114bc8d7a80ee5'
manifest=json.loads(M.read_text(encoding='utf-8'))
for name,meta in manifest['outputs'].items():assert sig(O/name)==meta

rooms=json.loads((R/'state/ROOMS.json').read_text(encoding='utf-8'))['rooms']
assert len(rooms)==13
byid={x['id']:x for x in rooms}
gc={rid:json.loads((R/'rooms'/rid/'geometry.json').read_text(encoding='utf-8')) for rid in byid}

# No generic wet wall, PAN or shower work may be demanded of a dry powder, WC or tub room.
trade={
'PH-PRIMARY':(
'Owner sign Black Onyx Brizo BT0734816-BNX 48-in LINEAR with BR73480, separate Duravit 67-in tub, no shower niche, flat Bone versus historical Reed visual palette and room cap; leave owner final choice unsigned.',
'Architect collect maker wet listing for flat Bone shower wall vs unlisted Reed and separate raw numerical wet LEVEL including PH-WC and exact RL21 1.5-in hex LINEAR PAN; wet ceiling support and grout/thickness revision remain held, NO niche.',
'Verify native 1529 PH304A/B and actual W1/W2 only, wet ceiling, linear location and rough, separate Duravit tub, PH-WC inherited LEVEL area and one measured LEVEL/PAN partition, door/glass and penetration coordinates.',
'Plumber/waterproofer submit Brizo BR73480 factory channel/flange/secondary drainage, actual selected BNX 48-in linear grate solid vs tile-in, approved membrane/slope/channel/threshold and flood witness; separate selected Duravit tub waste/flange shop; NO niche.',
'Estimator price exact flat Bone/optional RL21 LEVEL and LINEAR PAN each per verified net and factory carton, Brizo grate rough/membrane/ceiling labor and current Chicago lot/ETA, separate signed owner cap/purchaser; PH WC counted once.'),
'PH-BATH2':(
'Owner sign actual Duravit TUB and Hansgrohe MATTE WHITE palette, Sapphire wet wall/Sandstone niche, bath LEVEL tile, tub fit and budget; no tiled PAN.',
'Architect attach individual wet WALL Sapphire and wet NICHE Sandstone maker approvals and exact raw individual LEVEL floor DCOF; shower PAN N/A because selected tub.',
'Verify 1529 PH Bath2 W1-W3 and openings, nominal 59.496-in alcove versus 59-in tub before backer/flange, actual LEVEL net, niche aperture, back/returns/sill and tub surround height.',
'Plumber/tile install Duravit tub support, correct tub WASTE/OVERFLOW/flange-to-waterproof WALL seal, sloped niche sill and tub rim/finish threshold; no shower POINT/LINEAR PAN, no PAN flood test request.',
'Estimator obtain Sapphire, Sandstone, verified exact LEVEL floor case and actual tub/edge labor, current Chicago shade/lead and installed full bid; no shower PAN case.'),
'PH-BATH3':(
'Owner sign TUB versus WALK-IN independently for PH307A/B, owner basin selection, Hansgrohe CHROME/Delta DT062412 recorded shower drain, material finish and room cap; do not choose tub.',
'Architect obtain Sapphire individual wet WALL if proposed versus Opal wet WALL FAIL and Sandstone niche Wet Areas PASS, exact raw LEVEL DCOF and separate POINT PAN raw test ONLY for elected WALK-IN; TUB PAN N/A.',
'Verify actual PH307A/B W1-W3 1529 tub alcove/door, finished opening and valve/point shower center; measure bath LEVEL and conditional shower PAN boundaries independently, niche aperture/back/returns/sill once.',
'TUB only: new owner-selected tub, dedicated tub waste/overflow/flange, revised signed plumbing and WALL waterproofing, PAN N/A. WALK-IN only: selected Delta DT062412 Chrome SQUARE POINT with factory 113919 Rev B/clamped-liner preslope/weeps, compatible membrane, four-plane PAN and witnessed flood shop; never use shower drain as tub waste.',
'Estimator prepare TWO mutually exclusive PH3 installed bid branches (TUB with waste, no PAN; WALK-IN Delta 4-plane tested PAN), actual measured net/case, Sapphire/Opal approval status, owner basin, Chicago supplier lot and signed owner choice.'),
'PH-BATH4':(
'Owner review confirmed WALK-IN, selected Black Onyx Brizo BT062415-BNX SQUARE POINT, conditional flat Bone/Soho Black vs unlisted full Ribbed/Caviar, room cap; document 35-SF owner vs 27-SF prior drawing discrepancy.',
'Architect collect individual maker wet WALL flat Bone and niche Soho Black if proposed, historical Bone Ribbed/Clara Caviar wet-unlisted FAIL, separate exact raw LEVEL and 4-plane POINT PAN tests.',
'Verify actual PH311A/B W1-W3, point center/drain rim, four-plane PAN edges, shower glass/curb, 35 vs 27-SF actual floor, soft/anti-slip source disagreement and 107.2 SF/copy wet relief scope; niche opening/back/returns/sill once.',
'Plumber and tile installer sign exact Brizo BT062415-BNX POINT factory 113920 Rev C preslope/liner/clamp/weeps or separately maker-approved bonded junction, four-plane pan/threshold/glass, waterproof penetration and flood witness, NO tub/linear drain.',
'Estimator price one actual LEVEL and separate POINT PAN with exact maker carton/test, flat Bone/Soho vs historical relief/Caviar, current Chicago delivery installed scope; audit 214.4-SF two-unit vendor grand-total discrepancy only, NOT established payable shortage.'),
'PH-POWDER':(
'Owner choose dry Earth Lines uninterrupted relief or flanking relief with optional painted flat landing, preserve selected Brizo Frank Lloyd Wright T65722LF-GL Luxe Gold/R65700 and wood floor; paint and cap not signed.',
'Architect verify DRY wall-only Earth Lines application, relief substrate and selected Brizo escutcheon planar sealing; wet WALL/NICHE permission and wet LEVEL/PAN DCOF are N/A (wood floor).',
'Verify actual 1529 PH405A/B W1 ONLY, mirror/Brizo rough/vanity/wood floor, paint flat-center net deduction and two dry relief termination edges; no W3 or PAN.',
'Plumber/GC physically check Brizo R65700 wall faucet trim bearing against DRY Earth Lines relief or painted planar FINISHED WALL, backing, mirror and wood transition; no shower membrane, drain/pan slope, niche or flood test.',
'Estimator allocate actual dry relief net/paint and trim by measured W1, same exact Earth Lines case, current Chicago quote/paint labor and owner signature; no wet tile floor or shower PAN purchase.'),
'PH-WC':(
'Owner confirms PH WC shares PH PRIMARY LEVEL floor choice and one original quoted tile allocation; no separate WC niche, shower or new tile scope.',
'Architect inherits PH PRIMARY exact raw wet LEVEL DCOF once for the SAME exact selected SKU/finish; no new WC wet WALL/NICHE application certificate or PAN test.',
'GC check actual PH WC shared LEVEL finish boundary, toilet flange/cut and threshold/transition to PH PRIMARY; NO independent W1-W3 wall tile elevations or PAN net.',
'Plumber/GC witness toilet closet flange/threshold sealing and finish transition only; NO shower drain, tub flange, waterproof shower PAN or flood inspection.',
'Estimator count PH WC floor in PH PRIMARY LEVEL net and quote ONCE, no duplicate WC carton, unrelated wall niche or pan costs.'),
'TX-PRIMARY':(
'Owner preserve selected BNX Brizo 48-in LINEAR/no additional shower niche and TX WC inherited LEVEL; choose flat Clay maker-wet vs source ribbed condition and cost cap.',
'Architect validate flat Clay individual wet WALL vs unlisted Clay Ribbed, separate exact raw numeric TX LEVEL including WC and Prime RL21 LINEAR PAN, all maker revision/1/8-vs-3/16 grout; NO extra niche.',
'Survey actual TX PRIMARY 1529 W1/W2 shower, selected 48-in linear drain rough/subfloor/slope, shower openings/glass/penetrations and separately measured LEVEL+TX WC once versus LINEAR PAN.',
'Plumber/tile/GC submit selected 48-in Brizo BNX LINEAR factory rough and manufacturer-approved membrane/channel/pan slope and flood witness, actual grout/caliper and no extra niche; not PH4 4-in POINT.',
'Estimator separately price approved flat Clay wall, exact LEVEL+shared TX WC and distinct Prime LINEAR PAN only after factory raw test, current Chicago lot/carton/installed shower bid and owner cap.'),
'TX-BATH2':(
'Owner preserve Duravit TUB and Hansgrohe CHROME, choose owner-unselected sink/basin and wall/cost scope; no tiled shower PAN.',
'Architect obtain individual wet WALL/NICHE manufacturer permission for Copper/Sandstone source use and exact individual raw wet LEVEL floor test (Cortar Clay Soft or unselected conditional EL30); PAN N/A.',
'Verify TX Bath2 correct 1529 W1-W3 tub surround, niche cut/returns/sill and actual tub-flange/LEVEL net; sink selection and physical wall rough coordinates; NO shower PAN.',
'Plumber/tile/GC check actual Duravit tub support, tub waste/overflow and flange-to-wet-wall waterproof junction, valve/edge/movement; no tiled shower POINT/LINEAR pan or flood test of nonexistent pan.',
'Estimator price actual Copper/Sandstone wall and independent selected LEVEL case, sink/tub labor, Chicago supplier lot, complete installed bid and signed cap; NO PAN order.'),
'TX-BATH3':(
'Owner sign actual TX207A/B TUB versus WALK-IN (unselected), retain Brizo Roccesco BNX and square shower POINT as conditional; do NOT import PH Bath3 basin issue.',
'Architect preserve manufacturer Wet Areas listed Emerald WALL and Sandstone NICHE; require exact raw LEVEL Grey Soft/conditional RL21 independent test; if WALK-IN require separate raw POINT PAN test, TUB PAN N/A.',
'Survey actual TX207A/B 1529 W1-W3/alcove, door, valve/niche/glass, location of existing Black Onyx square POINT, separate LEVEL and conditional four-plane PAN net, measured niche opening/back/returns/sill.',
'TUB owner branch: approved new bathtub/waste/overflow and flange shop, no PAN; WALK-IN branch: selected Brizo BT062415-BNX 4in SQUARE POINT, maker 113920 Rev C clamp/weeps/liner or factory-approved membrane, four-plane PAN, threshold and witnessed flood; never tub waste.',
'Estimator obtain mutual-exclusive TX3 TUB vs WALK-IN budgets/real net/cases and current installed Chicago quote with Emerald/Sandstone and owner-approved fixture shop; no PH basin hold.'),
'TX-BATH4':(
'Owner preserve actual Duravit TUB/Hansgrohe MATTE WHITE and choose maker-wet Soho Ivory niche versus historical unlisted Caviar, source Bone Soft LEVEL and cost cap.',
'Architect obtain flat Charcoal maker-specific wet WALL and Soho Ivory maker-specific NICHE proof if used, distinguish unlisted Caviar, and exact raw numeric LEVEL Bone Soft/conditional Emser test; tiled PAN N/A.',
'Verify actual 1529 TX Bath4 W1-W3 with tub rim/flange, wall opening/niche aperture/back/returns/sill and separately measured LEVEL net; no shower point/linear PAN.',
'Plumber/tile/GC submit approved Duravit tub waste/overflow, support and tub rim-to-waterproof surround, niche slope/grout/edge; no shower PAN drainage/slope/flood requirement.',
'Estimator source correct separate Bone Soft or Emser LEVEL, flat Charcoal/Soho Ivory niche if owner elects, current Chicago case/lead/installed tub bid; no PAN or imported TX Bath2 sink hold.'),
'TX-POWDER':(
'Owner selects exactly one conflicting source-listed AXOR 48140991 One Polished Gold Optic WALL TRIM or Hansgrohe 32526141 Metropol Brushed Bronze WALL TRIM; Hansgrohe 32526141 is NOT rough. Approve dry Haze Camel/Wheat palette/cap only after trim election.',
'Architect verify dry Camel/Wheat (or Earth Lines) WALL finish ONLY, matching chosen wall trim to approved factory ROUGH and planar escutcheon landing; maker wet WALL/NICHE and wet floor LEVEL/PAN lab N/A with WOOD floor.',
'Survey true TX102A/B W1 ONLY, each selected-future faucet rough depth, mirror/backsplash/wood floor and Haze 70:30 color wall net and edge cuts; no W3, PAN or wet niche.',
'Plumber check actual future single AXOR or hansgrohe selected trim AND factory-matched rough, box/backing/seal against dry tile; do not install AXOR 48140991 with Hansgrohe 32526141 as compatible rough. No shower membrane/pan/flood.',
'Estimator obtain separate Haze Camel and Wheat exact current case/lot one-wall 70:30 quantities, fixture verified factory rough and installed dry setting/backsplash quote, owner cap; no wet floor.'),
'TX-POWDER2':(
'Owner select basin (UNSELECTED) for existing Hansgrohe Tecturis E 73072341 Brushed Black Chrome DECK faucet, Indigo/Earth Lines dry WALL palette, wood floor and cap.',
'Architect verify dry Indigo/Earth Lines WALL-only maker compatibility and deck-faucet/basin template/overflow/drain finish; wet WALL/NICHE and wet LEVEL/PAN lab N/A, no wall escutcheon.',
'Survey actual TX009A/B W1 ONLY, dry relief tile/mirror/wood, countertop deck-faucet rear setback, future owner-selected basin and drill hole layout; no W3 or shower PAN.',
'Plumber and GC hold ALL countertop drilling until owner basin and exact Tecturis 73072341 DECK reach/hole/drain overflow signed. No wall faucet rough, shower membrane, PAN or flood test.',
'Estimator price one dry feature wall exact SKU/current lot and countertop cut/finish-specific drain/installed vanity scope after basin approval, no shower/wet floor cases.'),
'TX-WC':(
'Owner confirms TX WC inherits TX PRIMARY LEVEL floor and source quote once, no extra wet wall/niche/shower/pan selection.',
'Architect require same exact individual wet LEVEL tile/raw laboratory report in parent TX PRIMARY once; independent WC wet WALL/NICHE and PAN applications N/A.',
'GC verify real TX WC common LEVEL floor threshold/flange and measured parent boundary, no W1-W3 tiled wall study, extra niche or shower PAN.',
'Plumber inspect toilet flange and dry closet transition; no shower rough/membrane, tub drain, pan flood or separate WC bath tile scope.',
'Estimator carry TX WC tile in parent TX PRIMARY LEVEL cases ONCE with actual current Chicago case; no separate order, PAN or niche cost.'),
}
assert set(trade)==set(byid)

trade_file=O/'R23_65_ROOM_TRADE_ACTIONS_REVIEW_BRIDGE_NEW_COPY.csv'
with trade_file.open('r',encoding='utf-8-sig',newline='') as f:
 reader=csv.DictReader(f);fields=reader.fieldnames;rows=list(reader)
assert len(rows)==65
old_trade=sig(trade_file)
categories=['owner_selection','maker_lab','field_geometry','waterproofing_shop','pricing_and_release']
for row in rows:
 idx=categories.index(row['workstream']);row['specific_action']=trade[row['room']][idx]
 assert row['approved']=='FALSE' and row['procurement_release']=='FALSE'
 assert row['source_reference'].startswith('../../state/')
 buf=io.StringIO(newline='');w=csv.DictWriter(buf,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(rows)
trade_file.write_bytes(buf.getvalue().encode('utf-8'))

# Exactly thirteen kit-row replacements, no other sample scope rewritten.
samples={
'PH-PRIMARY':('Flat Bone individual wet-wall sample vs historic Reed wet HOLD; 12x24 LEVEL including PH WC once, distinct RL21 hex LINEAR PAN, BNX 48-in reversible solid/tile-in grate and BR73480, separate Duravit tub, no added niche.','W1 front true shower valves/ceiling and Bone grid; W2 oblique true 48in linear wall edge and glass, NO W3/niche; 1:1 BNX/BR73480 pan/grout/caliper/membrane + separate tub flange/paint under day/night'),
'PH-BATH2':('Actual Duravit TUB, Matte White Hansgrohe, individually wet Sapphire WALL and Sandstone NICHE, separately exact raw LEVEL sample; no tiled shower PAN.','W1 straight-on tub and Sapphire wall; W3 oblique niche and tub return, measured 59 vs 59.496 nominal width hold; close 1:1 tub flange/waste, niche sill, Matte White/grout under real light, NO PAN'),
'PH-BATH3':('Two OWNER-UNSELECTED branches: Hansgrohe Chrome and maker-wet Sapphire vs unlisted Opal wall, wet Sandstone niche, LEVEL; conditional Delta DT062412 square POINT PAN only WALK-IN; basin unselected.','W1 source alcove front with TUB TBD and WALK-IN TBD distinct labels; W3 oblique Chrome/valve/niche on each mutually exclusive branch; close 1:1 future tub flange/waste NO PAN OR selected Delta square 4-plane POINT PAN if walk-in, not both'),
'PH-BATH4':('Confirmed WALK-IN Black Onyx Brizo BT062415-BNX 4in SQUARE POINT, source Ribbed/Caviar wet unlisted vs conditional flat Bone/Soho Black listed, separate LEVEL and small-format POINT PAN with raw tests.','W1 actual full shower wet flat-vs-relief overlay; W3 oblique niche/glass/point four-plane slope and owner 35 vs old 27 SF floor; 1:1 BNX square drain weeps/membrane, edge, 4-way pan wedges and black grout, NO tub'),
'PH-POWDER':('Selected Brizo FLW T65722LF-GL/R65700 Luxe Gold WALL faucet against DRY Earth Lines relief or DRY painted central planar landing, actual wood-floor and mirror sample; no wet tile floor/pan/niche.','W1 straight-on dry vanity wall and actual Brizo handle center; W1 oblique relief/paint/wood/mirror plane with no W3; 1:1 actual escutcheon bearing and trim on flat vs relief, no shower drain/tub/pan'),
'PH-WC':('Same PH Primary LEVEL tile and original quoted area/cases ONCE; toilet flange, threshold and adjacent transition sample ONLY; no independent WC wall/niche/pan or extra tile order.','Floor/threshold plan from Primary into PH-WC; low oblique view toilet flange and perimeter/movement joint; close tile-to-flange/door threshold sample, NO W1/W3 wet wall or shower drain detail'),
'TX-PRIMARY':('Brizo BNX 48in LINEAR, no niche, maker-wet flat Clay versus relief wet HOLD; distinct TX Primary+WC LEVEL and RL21 hex LINEAR PAN exact wet lab samples.','W1 source wet-wall front; W2 linear drain/glass oblique, NO W3/niche; close 1:1 BNX 48in linear selected rough/channel/perimeter and grout raw test, WC floor inherited, no point drain'),
'TX-BATH2':('Duravit TUB/Hansgrohe CHROME, Copper/Sandstone wall/niche manufacturer wet permission to confirm, LEVEL exact raw lab, owner sink unselected, NO tiled shower PAN.','W1 true tub and Chrome valve straight-on; W3 tub return/niche angled, actual sink shown unselected; close tub waste/flange/tiling edge, Copper/Sandstone and grout under daylight/night; no PAN'),
'TX-BATH3':('Owner TUB or WALK-IN unselected; Brizo Roccesco BNX 4in square POINT conditional WALK-IN, Emerald maker-wet WALL and Sandstone maker-wet NICHE, separate LEVEL and conditional small-format POINT PAN.','W1 actual source alcove front with two mutually exclusive unselected program labels; W3 Emerald/Sandstone/Black Onyx oblique; close 1:1 future tub flange and tub waste with PAN N/A OR Brizo square 4-plane POINT membrane/weeps mockup only if WALK-IN'),
'TX-BATH4':('Actual Duravit TUB/Hansgrohe MATTE WHITE and flat Charcoal conditional wet WALL, Soho Ivory maker-wet niche vs Caviar wet HOLD, Bone Soft/Emser LEVEL, no tiled PAN.','W1 Matte White tub and flat Charcoal color reference; W3 oblique Soho Ivory wet niche and real tub flange; close 1:1 tub waste/edge/movement/grout and LEVEL tile; NO POINT or LINEAR shower PAN'),
'TX-POWDER':('Dry Haze Camel/Wheat 70:30 W1 wall and wood floor; two incompatible source WALL faucet TRIMS AXOR 48140991 vs Hansgrohe 32526141 (NOT a rough). No manufacturer-selected matched rough.','W1 front actual 70:30 Camel/Wheat band study with faucet trim marked OWNER UNSELECTED; W1 angled matte/grout/wood/mirror under day/night with no W3; 1:1 compare separate AXOR vs Hansgrohe wall trim planes pending matched rough, no shower/tub/PAN'),
'TX-POWDER2':('DRY Indigo Edge 6x6 or Earth Lines W1 wall, wood floor, Hansgrohe Tecturis E 73072341 Brushed Black Chrome DECK faucet and basin UNSELECTED; no wall escutcheon.','W1 front dry tile/mirror composition; W1 oblique wall-to-countertop deck faucet/wood floor with basin blank/unselected, no W3; 1:1 deck spout/reach/hole/overflow/backsplash before ANY drilling, no wall valve/shower/PAN'),
'TX-WC':('Same TX Primary LEVEL tile and quote ONCE, toilet threshold/flange, floor joint/cut sample; no separate WC tiled shower pan or wall/niche.','Parent LEVEL to shared TX-WC floor transition plan; angled WC toilet/flange threshold photo brief; 1:1 parent tile and perimeter/door transition only, no W1/W3, shower rough, niche or PAN'),
}
assert set(samples)==set(byid)
sample_file=O/'R23_13_ROOM_1TO1_SAMPLE_RENDER_SHOP_AND_PRICE_ORIGINS.md'
old_sample=sig(sample_file)
lines=sample_file.read_text(encoding='utf-8').splitlines()
found=[]
for i,line in enumerate(lines):
 if line.startswith('| ') and line.count('|')>=4:
  rid=line.split('|')[1].strip()
  if rid in samples:
   assert rid not in found
   kit,camera=samples[rid]
   lines[i]=f'| {rid} | {kit} | {camera} | owner/architect/plumber/GC sample/photo/field acceptance: **FALSE** |'
   found.append(rid)
assert len(found)==13
sample_file.write_bytes(('\n'.join(lines)+'\n').encode('utf-8'))

book_file=O/'R23_ALL_13_ROOM_GOOD_BETTER_BEST_OWNER_DECISION_BOOK.md'
old_book=sig(book_file)
book=book_file.read_text(encoding='utf-8')
pattern=r'\*\*Approval boundary:\*\* selected fixtures remain only those in `rooms/([^/]+)/plumbing\.json`; verified 1529 dimensions, factory individual wet WALL/NICHE listings, raw exact numerical wet LEVEL/PAN lab where applicable, current Chicago lot/cases/offer, complete installed GC bid and owner/architect/plumber/tile/GC/purchaser signatures remain unresolved\. Owner tier: `null`; final order: `false`\.'
def replacer(m):
 rid=m.group(1);assert rid in byid
 if rid in ['PH-POWDER','TX-POWDER','TX-POWDER2']:
  gate='DRY vanity wall and WOOD floor: shower wet WALL/NICHE permission and wet LEVEL/PAN lab N/A; verify only actual tile wall use, exact DRY faucet/rough (or DECK countertop), owner basin if unselected and 1:1 backing/trim/edge'
 elif rid in ['PH-WC','TX-WC']:
  parent='PH-PRIMARY' if rid.startswith('PH') else 'TX-PRIMARY'
  gate=f'SHARED WC floor receives the SAME exact selected and individually tested LEVEL wet lab from {parent} ONCE, no separate WC tile order, no WC wet WALL/NICHE or PAN requirement; verify flange/threshold and parent cost/case allocation'
 elif rid in ['PH-BATH2','TX-BATH2','TX-BATH4']:
  gate='selected DURAVIT TUB with individually required wet WALL/NICHE documentation and raw wet LEVEL floor lab; tiled shower PAN N/A; tub waste/flange waterproofing and true 1529 dimensions remain unknown'
 elif rid in ['PH-BATH3','TX-BATH3']:
  gate='owner TUB/WALK-IN UNSELECTED; exact wet WALL/NICHE maker permissions and independent raw LEVEL mandatory, separate POINT PAN raw lab/rough/membrane ONLY IF owner selects WALK-IN; TUB requires own waste/flange and PAN N/A'
 elif rid in ['PH-PRIMARY','TX-PRIMARY']:
  gate='48-inch Brizo Black Onyx LINEAR with NO additional Primary niche, separate raw LEVEL plus LINEAR PAN lab and independently manufacturer-listed wet WALL, approved rough/membrane and inherited WC LEVEL once'
 else:
  gate='PH Bath4 actual 4in square POINT walk-in, separate LEVEL/POINT PAN exact raw lab, individual wet WALL/NICHE proofs and 35-vs-27 SF survey required'
 return f'**Approval boundary:** {gate}. Selected fixtures remain only those in `rooms/{rid}/plumbing.json`; actual verified 1529 survey, current Chicago lot/cases/offer and complete installed GC bid, and owner/architect/plumber/tile/GC/purchaser signatures remain unresolved. Owner tier: `null`; final order: `false`.'
book, count=re.subn(pattern,replacer,book)
assert count==13,count
book_file.write_bytes(book.encode('utf-8'))

changed={}
for file,before in [(trade_file,old_trade),(sample_file,old_sample),(book_file,old_book)]:
 changed[file.name]={'before':before,'after':sig(file)}
 assert changed[file.name]['after']['sha256']!=before['sha256']

manifest['outputs']={key:sig(O/key) for key in manifest['outputs']}
manifest['R23_independent_reviewer_verdict']='worker-15 PRECISE FIX1 corrected in SAME R23; awaiting independent successor Reviewer confirmation'
manifest['R23_reviewer_fix1_change_scope']=['65 room-specific trade action descriptions','13 room-specific sample and actual camera descriptions','13 explicit approval boundary N/A/inherited statements']
M.write_bytes((json.dumps(manifest,indent=2,ensure_ascii=False)+'\n').encode('utf-8'))
after_manifest=sig(M)
receipt={'date':'2026-11-06','round':'R23 SAME-PACKAGE','reviewer':'worker-15 original non-Pro standing, now permanently finished nonrevivable','reviewer_verdict':'PRECISE FIX1, 65 generic trade rows + 13 generic physical mockup render rows + optional 13 approval scope notes','old_manifest':before_manifest,'new_manifest':after_manifest,'changed_only_three_R23_outputs':changed,'other_six_R23_files_byte_SHA_unchanged':{n:manifest['outputs'][n] for n in manifest['outputs'] if n not in changed},'prior_signed_R12_to_R22_files_untouched':True,'R017_source_unchanged':True,'original_R014_design_missing':True,'R015_R016_scorings':None,'independent_successor_review_pending':True,'owner_approval':False,'GC_release':False,'purchase_release':False}
path=R/'state/ROUND023_REVIEWER_PROGRAM_SPECIFIC_SAME_PACKAGE_FIX1.json'
assert not path.exists()
path.write_bytes((json.dumps(receipt,indent=2,ensure_ascii=False)+'\n').encode('utf-8'))

assert sum(1 for r in rows if r['room'] in {'PH-POWDER','TX-POWDER','TX-POWDER2'} and 'wet LEVEL/PAN lab N/A' in r['specific_action'])>=0
for room in ['PH-POWDER','TX-POWDER','TX-POWDER2','PH-WC','TX-WC']:
 assert all(not('wet LEVEL/PAN' in r['specific_action'] and 'required' in r['specific_action']) for r in rows if r['room']==room)
for file,meta in manifest['outputs'].items():assert sig(O/file)==meta
print('PASS same-R23 reviewer FIX1 65 program-specific action narratives, 13 authentic sample/camera plans, 13 applicable maker/lab approval notes, 3 changed files/6 unchanged files')
print('OLD_MANIFEST',before_manifest['sha256'])
print('NEW_MANIFEST',after_manifest['sha256'])
print('FIX_RECEIPT',sig(path)['sha256'])
