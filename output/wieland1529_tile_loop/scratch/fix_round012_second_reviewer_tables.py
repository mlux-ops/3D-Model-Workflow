"""Second precise predispatch reviewer FIX: room+candidate+surface gates and sample briefs."""
from pathlib import Path
R=Path(__file__).resolve().parents[1]
gates={
 ('TX-PRIMARY','B'):{
 'wall':'Cortar Clay flat Soft individual Wet Areas PASS only for flat portions; source Clay Ribbed Relief Walls/Back Splashes only and its individual wet-shower authorization FAIL; actual relief area and ceiling structural fixings unmeasured.',
 'floor':'Original Cortar Clay Soft LEVEL and Anti-Slip selected linear PAN lack their own exact raw numeric wet DCOF certificates: both FAIL. Actual 48in Brizo BNX linear slope, membrane/liner, shared WC field split, actual tile size and drain center HOLD.',
 'accent':'NO PRIMARY NICHE: historical unpriced row is archive-only, zero specified product/quantity/order.'},
 ('TX-PRIMARY','C'):{
 'wall':'Individual ELM Cortar Clay flat Soft Wet Areas PASS. Clay Ribbed Relief individually NOT wet-authorized and is excluded from wet field/ceiling; overhead substrate/retention engineering HOLD.',
 'floor':'Emser Capisco Trosa F08CAPITR1224M LEVEL maker wet DCOF >=0.60 BOUND, exact raw measured test FAIL; separate Prime RL21 LINEAR mosaic PAN only family-level target, exact individual test FAIL; measured pan/level/WC split, liner/Brizo rough compatibility HOLD.',
 'accent':'NO PRIMARY NICHE: historical unpriced row excluded, zero new niche order.'},
 ('TX-BATH2','C'):{
 'wall':'ELM Tones Copper 2x20 Glossy individual Wet Areas PASS for tub walls; selected Duravit tub/Chrome Hansgrohe and measured waterproof flange/penetrations required.',
 'floor':'Original Cortar Clay Soft 12x24 LEVEL bathroom floor exact raw numeric wet DCOF certificate NULL/FAIL; this actual Duravit TUB room has NO tiled shower pan (N/A), no linear drain or second floor.',
 'accent':'Individual Tones Sandstone wet niche PASS; opening/back/return/sill net area and field-face deduction unmeasured, historical 8.63 SF gross only.'},
 ('TX-BATH2','A'):{
 'wall':'ELM Tones Copper 2x20 Glossy individual Wet Areas PASS. Centered horizontal cut rhythm subject to calibrated tile, joint, niche/valve and selected Chrome fixtures.',
 'floor':'Emser Capisco Trosa F08CAPITR1224M proposed LEVEL bath floor maker wet >=0.60 BOUND is NOT accepted exact raw numeric test: FAIL. Actual Duravit tub room has NO tiled shower PAN (N/A); current alternate SKU carton/price/lot NULL.',
 'accent':'Existing Tones Sandstone 2x20 Glossy individual Wet Areas PASS; exact niche field subtraction/back/sill/returns and current order gross NULL.'},
 ('TX-BATH4','A'):{
 'wall':'Original flat Cortar Charcoal Soft individual Wet Areas PASS for TUB surround, with true wall/niche cuts and waterproof tub flange still unverified.',
 'floor':'Original Cortar Bone Soft 12x24 LEVEL floor exact raw wet DCOF laboratory value NULL/FAIL; actual Duravit tub has NO tiled PAN, no added linear/square drain.',
 'accent':'Original Clara Tierra Madre Caviar 2x8 wet niche individual manufacturer Wet Areas NOT established: FAIL. Historical 8.63 SF gross is a provisional quoted allowance, not measured return area.'},
 ('TX-BATH4','B'):{
 'wall':'Flat Cortar Charcoal Soft individual Wet Areas PASS for retained tub wet wall, actual tub flange and substrate flatness/movement still unverified.',
 'floor':'Emser Capisco Trosa F08CAPITR1224M on LEVEL only reports DCOF >=0.60 BOUND, exact raw numeric laboratory certificate NULL/FAIL; no shower pan in actual Duravit tub room.',
 'accent':'ELM Soho Ivory 2x10 Glossy individual Wet Areas PASS for EXISTING niche, replaces unavailable individual Clara wet approval only as unapproved alternate; new price/pack/returns and owner sample NULL.'}
}
for (rid,letter),mapped in gates.items():
 f=R/'rooms'/rid/'board/round-012/candidates'/f'{letter}.md'
 lines=f.read_text(encoding='utf-8').splitlines()
 seen=set()
 for ix,line in enumerate(lines):
  if line.startswith('| wall /') or line.startswith('| floor /') or line.startswith('| accent /'):
   cells=line.strip('|').split('|')
   assert len(cells)==5,(rid,letter,line)
   surface=cells[0].strip().split(' / ')[0]
   assert surface in mapped
   cells[4]=' '+mapped[surface]+' '
   lines[ix]='| '+' | '.join(x.strip() for x in cells)+' |'
   seen.add(surface)
 assert seen=={'wall','floor','accent'},(rid,letter,seen)
 if rid=='TX-PRIMARY':
  sample='**Sample/render brief, NOT ordered/rendered:** TX PRIMARY only: draw source W1/W2 flat/relief wet-wall and ceiling cut calibration with Brizo Black Onyx 48-in LINEAR drain, actual separate level/WC/pan slope/membrane rough section, selected tub in separate location, grout/edge/movement samples. NO PRIMARY NICHE or descoped sprays. Actual owner cap, current tile price, model identity and test certificates NULL.'
 elif rid=='TX-BATH2':
  sample='**Sample/render brief, NOT ordered/rendered:** TX BATH2 only: draw centered source W1-W3 Copper wet tub elevation, actual Hansgrohe CHROME and Duravit built-in TUB flange/backsplash transition, the existing Sandstone niche sill/returns and level bath floor/wood threshold; do not show shower pan or linear drain. Basin OWNER-UNSELECTED, actual grout, finish sample, current bid and owner signoff NULL.'
 else:
  sample='**Sample/render brief, NOT ordered/rendered:** TX BATH4 only: draw Charcoal flat wet tub walls W1-W3, the original scheduled Caviar or named individual Ivory niche per this specific candidate, Hansgrohe MATTE WHITE and Duravit TUB flange/positive niche sill/level threshold section; NO tiled shower pan or new drain. Measure niche opening and trim before quote. Current cost, signed sample and DCOF raw result NULL.'
 ix=next(i for i,x in enumerate(lines) if x.startswith('**Sample/render brief,'))
 lines[ix]=sample
 if rid=='TX-PRIMARY' and letter=='B':
  lines=[x.replace('no new Prime RL21 mosaic or Emser level-floor item is selected by this option','no added alternative floor or pan SKU is authorized by this option') for x in lines]
 # Historic source packets must not name exact alternate SKU/other option in cost/gates/brief anywhere.
 text='\n'.join(lines)+'\n'
 if (rid,letter) in (('TX-PRIMARY','B'),('TX-BATH2','C'),('TX-BATH4','A')):
  assert 'F08CAPITR1224M' not in text and 'Soho Ivory candidate' not in text and 'Prime RL21' not in text
 f.write_text(text,encoding='utf-8')
 print(rid,letter,len(f.read_bytes()))
print('PASS 6 R012 candidate-specific table rows and single-room sample/render brief FIX, source receipts not yet changed')
