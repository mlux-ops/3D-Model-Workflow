from pathlib import Path
import json,csv,math
R=Path(__file__).resolve().parents[1]
O=R/'deliverables/integrated-r09'
O.mkdir(exist_ok=True,parents=True)
rooms=json.loads((R/'state/ROOMS.json').read_text(encoding='utf-8'))['rooms']
pal={
'PH-PRIMARY':('Flat Bone; PF07 field/2x2 pan held',24,'Brizo 48-in linear; NO NICHE'),
'PH-BATH2':('Sapphire 2x20 wet walls; Grey Soft floor held',20,'Duravit tub; Matte White Hansgrohe'),
'PH-BATH3':('Sandstone 2x20 conditional wet walls',20,'Tub versus Delta square drain; sink UNSELECTED'),
'PH-BATH4':('Flat Bone and Soho niche conditional',24,'Brizo 4-in point; 35/27-SF discrepancy'),
'PH-POWDER':('Earth Lines dry feature',None,'Dry powder; existing wood floor'),
'PH-WC':('Shared Primary level tile',None,'No independent tile area or order'),
'TX-PRIMARY':('Flat Clay wet walls and Prime mosaic research',24,'Brizo 48-in linear; NO NICHE'),
'TX-BATH2':('Copper/Sandstone 2x20 wet tub surround',20,'Tub retained; sink UNSELECTED'),
'TX-BATH3':('Historic Emerald wet wall',20,'OWNER tub versus point-drain shower decision'),
'TX-BATH4':('Flat Charcoal/Soho wet niche concept',24,'Duravit tub; Matte White Hansgrohe'),
'TX-POWDER':('70:30 Haze Camel/Wheat board direction',5,'Dry wall, wood floor; NOT owner approved'),
'TX-POWDER2':('Indigo Edge dry wall retained',6,'DECK faucet; sink UNSELECTED'),
'TX-WC':('Shared TX Primary level tile',None,'No independent tile area or order')}
assert len(pal)==len(rooms)==13
md=['# R09 | 13-room architect cut, sample and rendering instruction set','',
'PROVISIONAL SOURCE STUDIES ONLY. Live native Revit is titled 1527, not confirmed 1529. All wall dimensions derive from source geometry.json, not a new field survey; no openings, valves or niches measured. No checked construction/shop drawing, owner approval, measured wet DCOF or order implied.','',
'CUT METHOD: nominal centered width. Choose max whole horizontal modules leaving >=3-inch nominal end cuts if possible. Ignore joint and actual tile calibers because unknown. A favorable study cannot pass site cuts; field measurement and trim/movement/penetrations remain null.','',
'SOURCE ACCOUNTING: historical 27 ELM rows include 15% waste ONCE. Implied net = gross/1.15 is an audit ratio, not verified area. WC is within Primary gross; historical Primary niche accent is excluded. Every separate floor/pan split and niche displacement requires verified geometry before carton orders.',
'']
cut=[]
for x in rooms:
 rid=x['id'];g=json.loads((R/'rooms'/rid/'geometry.json').read_text(encoding='utf-8'))
 palette,mod,interface=pal[rid]
 md+=['','## '+rid+' | '+x['status'].upper(),'',
 'GOOD: historical v4/old material retained solely as reference. BETTER: '+palette+'. BEST: independent exact SKU wet-use and floor/pan numeric test, verified 1529 cut geometry, current Chicago offer and signed owner decision; no BEST selection approved.',
 'Plumbing/program and owner note: '+interface+'. Current board champion '+str(x['champion_id'])+', score '+str(x['champion_score'])+'; signed owner approval null.','',
 '| Source wall | Drawing length | Drawing tiled height | Nominal width grid | Risk / missing controls |',
 '|---|---:|---:|---|---|']
 for w in g['tiled_walls']:
  width=w['length']['value']*12;height=w['tiled_height']['value']*12
  if mod:
   n=max(0,int(math.floor((width-6)/mod)))
   edge=(width-mod*n)/2
   grid=str(n)+' full '+str(mod)+'-in nominal horizontal modules + two '+format(edge,'.2f')+'-in ends'
   risk='possible focal sliver, redesign after survey' if edge<3 else 'nominal >=3-inch edge, not as-built'
  else:
   n=None;edge=None;grid='unknown product module / not tiled';risk='actual module or wall scope null'
  md.append('| '+w['id']+' | '+format(width,'.2f')+' in | '+format(height,'.2f')+' in | '+grid+' | '+risk+'; openings/valves/niche/trim null |')
  cut.append({'room':rid,'wall':w['id'],'drawing_width_in':round(width,3),'drawing_tiled_height_in':round(height,3),'module_nominal_in':mod,'full_modules':n,'balanced_nominal_end_cut_in':round(edge,3) if edge is not None else None,'verified_actual_opening':None,'verified_actual_tile_caliber':None,'approved_exposed_trim_lf':None,'release':False})
 md+=['','### Historic material trace (per unit, 15% gross waste already included)','']
 for row in x['carried_tile_rows']:
  is_excluded=rid.endswith('PRIMARY') and row['surface']=='accent'
  md+=['- '+row['surface']+' row '+row['smartsheet_row_id']+': '+format(row['qty_sf_per_unit'],'.2f')+' gross SF; implied net '+format(row['qty_sf_per_unit']/1.15,'.2f')+' SF; historical extension USD '+str(row['extended_quote_cost_usd_per_unit'])+('; EXCLUDED historic Primary niche (not a buy)' if is_excluded else '; no extra waste or re-priced substitution')]
 if not x['carried_tile_rows']:md+=['- No independent tile quantity or cost; inherit Primary level wet DCOF gate.']
 md+=['','### Conditional owner sample kit / rendering direction','',
 'Samples: 1 full-scale wall field sample in proposed palette, 1 floor field tile sample and separately 1 shower-pan mosaic sample ONLY if an actual tiled shower exists; 1 selected faucet/drain metal reference, grout and compatible movement-joint samples; 1 niche prototype only if a niche actually occurs. Actual manufacturer order SKU, swatch lot, case and DCOF report null unless independently documented. NOT ORDERED.',
 'Rendering brief: one eye-height perspective and W1/W2/W3 annotated orthogonal elevations faithful to drawing wall relationships and known plumbing, preserve '+interface+'. Show uncertain floor/pan tiles and niche returns as hatched placeholders. Do not fabricate doors/windows/vanity size, sink selections, drain positions, shower glass, owner approval or a photograph of a particular comp bath. Compare historical vs conditional scheme without claiming any new selected finish.',
 'Detail hold: real substrate, waterproof membrane and drain flange compatibility; shower linear/point geometry and positive fall; actual floor-to-pan thickness, curb, threshold to wood, water-resisting assembly; tub flange, real niche back/returns and occupied field-face subtraction; vertical trims/movement and grout-lot calibration all require field survey.',
 'Market basis: 14 listings / nine distinct buildings, Old Town first and within prior 24 months; four sales at 405 W Armitage count as one design. Lincoln Park and Gold Coast are secondary. PH $2.8M, TX $2.7M; $2.4M-$3.2M band. No inferred tile photos.']
md+=['','## Procurement release-control interpretation','',
 'No actual current supplier quote, signed owner cap, case count, delivery or labor/installed budget exists. ELM historic quote is not a target bid; Glazzio retailer asking prices are not SHB quote. Manufacturer Portfolio PF07 targets are not SKU measured DCOF, and Prime brochure linear drain targets conflict by version. Only once actual product proof, measured geometry, case yield, edge LF and source quotes exist may a purchasable list be prepared.']
(O/'R09_DIMENSIONED_ROOM_LAYOUT_AND_RENDER_BRIEFS.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
with (O/'R09_NOMINAL_WALL_CUT_REGISTER.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(cut[0]));w.writeheader();w.writerows(cut)
assert len(cut)==sum(len(json.loads((R/'rooms'/r['id']/'geometry.json').read_text(encoding='utf-8'))['tiled_walls']) for r in rooms)
assert round(sum(r['carried_quote_material_subtotal_usd_per_unit']*r['unit_count'] for r in rooms),2)==23572.44
print('PASS 13 room-specific specs/render briefs,',len(cut),'wall cuts; historic 2PH+2TX $23572.44')
