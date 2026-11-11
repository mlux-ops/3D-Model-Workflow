"""Add 27-row exact original product application-and-test matrix to R12 owner package."""
from pathlib import Path
import json,csv,hashlib
R=Path(__file__).resolve().parents[1];O=R/'deliverables/integrated-r12'
rooms=json.loads((R/'state/ROOMS.json').read_text(encoding='utf-8'))['rooms']
source={
 'PH-PRIMARY':('Flat Cortar Bone 24x48 Soft + Reed Relief; exact split null','https://www.elmsurfaces.com/product/cortar-bone','FLAT wall Wet Areas documented; Reed relief exact Wet Areas missing'),
 'PH-BATH2':('Tones Sapphire 2x20 Glossy','https://www.elmsurfaces.com/product/sapphire-tones','Individual maker Wet Areas wall PASS'),
 'PH-BATH3':('Tones Opal 2x20 Glossy','https://www.elmsurfaces.com/product/opal-tones','Individual Wet Areas not demonstrated; wet wall FAIL'),
 'PH-BATH4':('Cortar Bone Ribbed Relief 24x48','https://www.elmsurfaces.com/product/bone-ribbed-cortar','Individual wet shower use unlisted, FAIL'),
 'TX-PRIMARY':('Flat Cortar Clay Soft + Ribbed Relief; exact split null','https://www.elmsurfaces.com/product/cortar-clay','FLAT Wet Areas documented; Ribbed relief individual Wet Areas missing'),
 'TX-BATH2':('Tones Copper 2x20 Glossy','https://www.elmsurfaces.com/product/copper-tones','Individual maker Wet Areas wall PASS'),
 'TX-BATH3':('Tones Emerald 2x20 Glossy','https://www.elmsurfaces.com/product/emerald-tones','Individual maker Wet Areas wall PASS'),
 'TX-BATH4':('Cortar Charcoal 24x48 Soft FLAT','https://www.elmsurfaces.com/product/cortar-charcoal','Individual maker Wet Areas wet wall PASS')
}
niches={'PH-BATH2':'Tones Sandstone 2x20 Glossy','PH-BATH3':'Tones Sandstone 2x20 Glossy','PH-BATH4':'Clara Tierra Madre Caviar 2x8','TX-BATH2':'Tones Sandstone 2x20 Glossy','TX-BATH3':'Tones Sandstone 2x20 Glossy','TX-BATH4':'Clara Tierra Madre Caviar 2x8'}
rows=[]
for room in rooms:
 rid=room['id']
 for src in room['carried_tile_rows']:
  surf=src['surface']
  label=src['carried_description'];uri=None
  if surf=='floor':
   scope='BATH LEVEL / possible separate PAN where selected shower, only if sourced and owner program permits'
   rating='FAIL exact raw numeric measured manufacturer SKU wet DCOF missing; source Soft/AntiSlip not a certificate'
   if rid in ('PH-BATH2','TX-BATH2','TX-BATH4'):scope='LEVEL bath floor only; actual bathtub means NO tiled shower pan'
   if rid in ('PH-PRIMARY','TX-PRIMARY'):scope='LEVEL+shared WC and separate LINEAR pan blended in one original source gross, separate verified split NULL'
   if rid=='PH-BATH4':scope='LEVEL+square POINT shower pan originally blended gross; 35-vs-27SF and Soft/AntiSlip conflict'
   if rid in ('PH-BATH3','TX-BATH3'):scope='LEVEL only if TUB; level and measured POINT pan if owner selects WALK-IN (owner decision null)'
  elif rid in ('PH-PRIMARY','TX-PRIMARY') and surf=='accent':
   scope='HISTORIC unpriced PRIMARY NICHE row; explicitly out of scope, do not order'
   rating='N/A — excluded, no Primary niche'
  elif surf=='accent':
   scope='Existing quoted wet niche provisional gross; opening/face/backs/returns/sill unmeasured'
   if 'Caviar' in label:
    rating='FAIL exact Caviar product individual Wet Areas unverified; collection Walls not sufficient'
    uri='https://www.elmsurfaces.com/product-collection/clara-collection'
   else:
    rating='PASS individually maker Wet Areas-listed Tones Sandstone on wet walls only'
    uri='https://www.elmsurfaces.com/product/sandstone-tones'
  elif surf=='wall':
   scope='WET shower/tub surround wall and where specifically noted shower ceiling'
   name,uri,rating=source[rid]
  else:
   scope='DRY vanity feature wall only, NO shower/floor DCOF requirement'
   rating='WET floor test N/A to dry vanity; sample, exact trim and owner approval held'
  # Floor maker reported bound cannot be transported to old ELM source.
  rows.append({'room':rid,'source_row_id':src['smartsheet_row_id'],'original_surface':surf,'original_v4_quoted_product':label,'maker_product_web_evidence':uri,'intended_surface_and_program':scope,'exact_individual_maker_wet_or_raw_dcof_gate':rating,'manufacturer_exact_raw_wet_numeric_value':None,'source_gross_sf_includes_15pct_once':src['qty_sf_per_unit'],'source_2026_09_03_material_usd_per_copy':src['extended_quote_cost_usd_per_unit'],'actual_measured_level_sf':None,'actual_measured_pan_sf':None,'actual_measured_niche_face_and_returns':None,'exact_product_carton_order_quantity':None,'current_chicago_lot_quote_eta':None,'approved_installed_total':None,'owner_program_approval':False,'procurement_release':False})
assert len(rows)==27
name='R12_27_ROW_EXACT_WET_APPLICATION_AND_TEST_MATRIX.csv'
dst=O/name
assert not dst.exists()
with dst.open('w',newline='',encoding='utf-8-sig') as f:
 writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
manifest_path=O/'MANIFEST.json';manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
assert manifest['source_rows']==27 and manifest['rooms']==13 and len(manifest['outputs'])==4
for fn,meta in manifest['outputs'].items():
 b=(O/fn).read_bytes()
 assert len(b)==meta['bytes'] and hashlib.sha256(b).hexdigest()==meta['sha256'],('prior signed output changed',fn)
b=dst.read_bytes()
manifest['outputs'][name]={'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
manifest['individual_application_test_rows']=27
manifest['raw_numeric_floor_or_pan_wet_dcof_available']=False
manifest['owner_approved']=False
manifest['procurement_release']=False
manifest_path.write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print('PASS new R12 original 27-row wet application/test matrix signed as fifth file; four prior output SHA unchanged and all source/owner holds preserved')
