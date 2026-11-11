"""Correct independent replacement Reviewer's specific R012 room/role blind-source issues."""
from pathlib import Path
R=Path(__file__).resolve().parents[1]
files=sorted((R/'rooms').glob('TX-*/board/round-012/candidates/*.md'))
assert len(files)==6
for f in files:
 rid=f.parents[3].name;letter=f.stem
 assert rid in ('TX-PRIMARY','TX-BATH2','TX-BATH4')
 a=f.read_text(encoding='utf-8').splitlines()
 assert a[2]=='This specification is a design option for independent evaluation; model geometry, manufacturer compliance, procurement terms and owner approval must be verified.'
 for idx,line in enumerate(a):
  if line.startswith('**Geometry classification:**'):
   if rid=='TX-PRIMARY':
    a[idx]='**Geometry classification:** Prior drawing W1/W2 module studies are NOT certified by 1529 native Revit; calibrate actual Cortar Clay 24x48 panel dimensions and joint widths with measured wet-wall/ceiling cuts, true Brizo 48-in LINEAR drain/rough location, shower pan pitch, valve and glass openings, actual threshold, movement/edge LF and approved waterproof construction. Focal 24x48 cuts under 3 in must be resolved with a revised grid; none assumed as built.'
   elif rid=='TX-BATH2':
    a[idx]='**Geometry classification:** W1–W3 are only old 1529 drawing/export dimensions, not certified as-built. Verify actual 2x20 Copper caliber and grout joint, 62.484-in W1 centered cut choice, tub rim/flange, selected Duravit waste/overflow/outlet, Chrome controls and actual niche/sill/corner/door/wood threshold elevations. All real trim LF, liner/membrane, movement sealant and fixture penetrations remain unmeasured; no shower floor drain center or tiled pan exists.'
   else:
    a[idx]='**Geometry classification:** All nominal W1–W3 values from previous 1529 drawing/export remain NOT native Revit 1529 verified. Calibrate true 24x48 Charcoal field dimensions, 60-in back and 30.48-in returns, minimum focal panel end cuts, actual niche opening/edge and tub rim, Duravit waste/overflow and Matte White valve/penetrations. Waterproof tub flange/threshold, soft movement joints and exposed edge LF require survey; NO tiled shower pan or shower drain-center study.'
  if rid!='TX-PRIMARY':
   a[idx]=a[idx].replace('introduce a primary niche','invent an extra niche')
   a[idx]=a[idx].replace('LEVEL floor/pan interpretation','LEVEL floor (tub-only program)')
   a[idx]=a[idx].replace('double-count shared WC, niche face/back/returns, trim or a new whole-area pan','double-count the quoted niche field face/back/returns or trim, or invent an extra full-area floor/pan')
   a[idx]=a[idx].replace('NO separately tiled shower pan or primary linear drain in this room','NO separately tiled shower pan; the tub waste/overflow is its own selected fixture assembly')
   a[idx]=a[idx].replace('NO Brizo primary linear drain','no added shower drain')
 for idx,line in enumerate(a):
  if line.startswith('**Sample/render brief,'):
   if rid=='TX-PRIMARY' and letter=='C':
    a[idx]=line.replace('source W1/W2 flat/relief wet-wall','source W1/W2 FLAT Cortar Clay-only wet-wall')
   elif rid=='TX-BATH2' and letter=='C':
    a[idx]=line.replace('draw centered source W1-W3 Copper wet tub elevation','draw the source stacked Copper W1-W3 wet tub elevation (no centered-grid design approval)')
   elif rid=='TX-BATH4' and letter=='A':
    a[idx]='**Sample/render brief, NOT ordered/rendered:** TX BATH4 only: draw flat Charcoal W1-W3 wet tub walls and the SPECIFIED Clara Tierra Madre Caviar 2x8 existing niche (**individual wet approval FAIL**), Hansgrohe MATTE WHITE and Duravit TUB rim/flange/positive niche sill/LEVEL threshold. NO additional tiled pan or drain. Actual niche back/returns, edge trim, floor raw DCOF, current bid and signed owner approval NULL.'
   elif rid=='TX-BATH4' and letter=='B':
    a[idx]='**Sample/render brief, NOT ordered/rendered:** TX BATH4 only: draw flat Charcoal W1-W3 wet tub walls with ONLY individually Wet Areas-listed Soho Ivory 2x10 Glossy in the existing niche, Hansgrohe MATTE WHITE / Duravit TUB rim/flange/positive Ivory sill/LEVEL threshold. NO tiled shower pan or added drain. Field-face subtraction/returns, exact current quote/cartons, level-floor raw wet DCOF and signed owner sample NULL.'
 t='\n'.join(a)+'\n'
 if rid=='TX-BATH4':
  if letter=='A':assert 'Soho Ivory' not in t and 'original scheduled Caviar or' not in t
  if letter=='B':assert 'Caviar or named individual Ivory' not in t and 'Only individually Wet Areas-listed Soho Ivory' in t.replace('ONLY individually','Only individually')
 if rid=='TX-BATH2' and letter=='C':assert 'draw centered source' not in t
 if rid=='TX-PRIMARY' and letter=='C':assert 'flat/relief wet-wall' not in t
 if rid!='TX-PRIMARY':
  assert 'introduce a primary niche' not in t and 'double-count shared WC' not in t and 'shower drain center' not in t and 'primary linear drain' not in t
 f.write_text(t,encoding='utf-8')
 print(rid,letter,len(f.read_bytes()))
print('PASS corrected six R012 packet-only precise room/option texts, no keys/source receipt written yet')
