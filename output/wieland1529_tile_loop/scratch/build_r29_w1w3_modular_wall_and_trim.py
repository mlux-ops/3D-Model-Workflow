"""R29 source W1/W2/W3 2x20 mathematical bond; owner/trade not signed."""
from pathlib import Path
import csv,json
from decimal import Decimal,ROUND_HALF_UP
R=Path(__file__).resolve().parents[1]
O=R/'deliverables/integrated-r29-sandstone-niche-shared-cutstock'
P=O/'R29_24_PROVISIONAL_FOUR_ROOM_W1_W3_2X20_WALL_EDGE_MODULE_AND_TRIM.csv'
assert not P.exists()
def d(x):return Decimal(str(x))
def n(x):return str(d(x).quantize(d('.0001'),rounding=ROUND_HALF_UP))
with (R/'deliverables/integrated-r17/R17_25_DIMENSIONAL_ELEVATION_SHOP_GATE.csv').open(encoding='utf-8-sig',newline='') as f:source=list(csv.DictReader(f))
rs=['PH-BATH2','PH-BATH3','TX-BATH2','TX-BATH3']
wallcolors={'PH-BATH2':'Sapphire maker individual wet PASS','PH-BATH3':'Opal wet FAIL, Sapphire owner-conditional individually wet PASS','TX-BATH2':'Copper maker individual wet PASS','TX-BATH3':'Emerald historical individual wet listing only current refresh required'}
out=[]
for room in rs:
 for wall in ('W1','W2','W3'):
  row=next(r for r in source if r['room']==room and r['wall']==wall)
  width=d(row['source_width_in_UNVERIFIED']);height=d(row['source_tiled_height_in_UNVERIFIED'])
  assert height==93
  for j in (d('.125'),d('.1875')):
   # Balanced ends, one to four full nominal horizontal 20in modules, reject negative/offcut over nominal tile length.
   valid=[]
   for full in range(5):
    cut=(width-full*d(20)-(full+1)*j)/2
    if 0<cut<=20:valid.append((full,cut))
   assert valid,(room,wall,width,j)
   maxfull=max(valid,key=lambda a:a[0])
   preferred=next(((full,cut) for full,cut in sorted(valid,reverse=True) if cut>=3),max(valid,key=lambda a:a[1]))
   face=width*height/d(144)
   courses=(height+j)/(d(2)+j)
   out.append(dict(room=room,source_wall=wall,original_wall_color_and_individual_wet_permission=wallcolors[room],
    original_source_W1W3_width_in_NOT_VERIFIED=n(width),original_source_tile_height_in_NOT_VERIFIED=n(height),
    source_full_nominal_wall_face_before_openings_SF=n(face),
    hypothetical_2x20_nominal_tile_length_in='20',hypothetical_2x20_nominal_tile_height_in='2',
    assumed_grout_joint_in=n(j),most_full_20in_tiles_between_edges=maxfull[0],most_full_edge_each_in=n(maxfull[1]),
    most_full_edge_under_3in='TRUE' if maxfull[1]<3 else 'FALSE',
    safer_full_tile_count=preferred[0],safer_edge_each_in=n(preferred[1]),
    safer_edge_under_3in='TRUE' if preferred[1]<3 else 'FALSE',
    nominal_courses_from_unverified_source_height_NOT_ACTUAL_TILE_COUNT=n(courses),
    illustrative_TWO_FULL_HEIGHT_EXPOSED_WALL_EDGE_LF_UPPER_BOUND=n(height*2/d(12)),
    actual_field_exposed_edges_LF='',actual_wet_WALL_valve_window_door_deduction_SF='',
    actual_one_NICHE_aperture_deducted_from_field_SF='',
    actual_field_Net_and_NICHE_independent_back_returns_sill='',
    confirmed_actual_field_width_and_height='',actual_selected_tile_calibrated_length_height_thickness='',
    true_1529_wall_orientation_and_selected_niche_location='',
    maker_approved_individual_wet_WALL='FALSE_IF_OPAL' if room=='PH-BATH3' else 'REVERIFY_CURRENT_INDIVIDUAL_FOR_EMERALD' if room=='TX-BATH3' else 'CURRENT_INDIVIDUAL_LISTING',
    actual_perimeter_movement_and_transition_SF='',original_tile_saw_kerf_and_pier_support='',
    owner_approved='FALSE',architect_signed='FALSE',tile_installer_signed='FALSE',purchase_released='FALSE'))
assert len(out)==24
with P.open('w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=out[0],lineterminator='\n');w.writeheader();w.writerows(out)
print('PASS R29 24 2x20 wall bond and edge/cut sensitivity scenarios with source W1-W3, no new selected finish')
