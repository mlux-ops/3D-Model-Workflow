"""Add explicitly source-qualified COMPLETE room envelopes from A2.1/A2.2 floor plans.

This is a geometric DESIGN STUDY, not a native room solid, surveyed dimension,
or authorization to modify the frozen tile/fixture schedule. Dimension sets
combine visible architect floor-plan callouts and older unverified room areas.
Source-specific spatial outlines are intentionally approximate until original
Revit room boundary curves are available.
"""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PATH=ROOT/'deliverables/viewer3d/picks.json'
payload=json.loads(PATH.read_text(encoding='utf-8'))
SOURCE='25-006 1527 N Wieland fp.pdf, export 2026-11-07 6:49 PM, A2.1/A2.2 (OWNER UPLOAD, latest floor plans); supersedes 2026-11-05 set and 2026-10-28 FP export'
DETAIL='25-006 1527 N Wieland_bathrooms.pdf, 2026-08-22, sheets ID2.1-ID3.5 (Google Drive file 1CPjRDspmk2hfG0r-YNyvA74XOS5SNENN)'

# Architect-sheet plan geometry study widths and depths in feet. These describe
# the entire scheduled bathroom, NEVER only the wet/tub alcove. Values besides
# explicitly noted PH4/Bath3 dimension callouts are plan-scaled hypotheses,
# cross-referenced to the legacy area; they must not be used as takeoff values.
# No construction wall thickness, rough opening or floor finish area is inferred.
SOURCE_ENVELOPES={
 'PH-BATH4': (5+5/12,5.0,'LATEST A2.2 311A/B mirrored shower compartments: 5ft-5in width x 5ft-0in depth; 310A WIC4 and 310B BATH4 EACH show adjacent toilet and sink in the plan. Bath4 shower is OUTER side alcove, entry on INNER side. 27.08 SF vs frozen 35 SF remains unresolved.','dimensioned owner 2026-11-07 floor plan; room boundary is 311 only'),
 'PH-BATH3': (7.0,5.0,'A2.2 307A/B: 7ft-0in x 5ft-0in bath envelope','dimensioned drawing rectangle; VERIFY IN REVIT'),
 'PH-BATH2': (5.0,7.0,'A2.2 305A/B: bath compartment; 35 SF legacy area; both spans need room-boundary confirmation','PLAN-SCALED APPROXIMATION'),
 'PH-PRIMARY': (11+7/12,8.90,'A2.2 304A/B primary suite bath area; 11ft-7in plan width; approximate depth calibrated to former 103 SF area','PLAN-SCALED APPROXIMATION'),
 'PH-WC': (5+2/12,2+10/12,'A2.2 PRIMARY toilet enclosure 314A/B, 5ft-2in x 2ft-10in dimensioned; frozen legacy mislabeled 313A/B (corridor/door)','DIMENSIONED DRAWING, ROOM NUMBER CORRECTED IN VIEWER ONLY'),
 'PH-POWDER': (4+2/12,6+8.5/12,'A2.2 405A/B: 4ft-2in x 6ft-8 1/2in powder, toilet at outer wall and vanity near foyer; entries mirrored','DIMENSIONED DRAWING, NO NATIVE SOLID'),
 'TX-PRIMARY': (10.25,8.49,'A2.1 202A/B second-floor primary bath enclosure; legacy 87 SF','PLAN-SCALED APPROXIMATION'),
 'TX-BATH2': (5+2.75/12,7+4/12,'A2.1 205A/B: 5ft-2 3/4in x 7ft-4in, tub outer end, toilet middle, lav near door','DIMENSIONED DRAWING, NO NATIVE SOLID'),
 'TX-BATH3': (5.0,7+4.75/12,'A2.1 207A/B: 5ft-0in x 7ft-4 3/4in, shower/tub alcove, toilet and lav opposite; TUB/WALK-IN still UNSELECTED','DIMENSIONED DRAWING, NO NATIVE SOLID'),
 'TX-WC': (2+8/12,5+3/12,'A2.1 203A/B primary toilet compartment, approximately 2ft-8in x 5ft-3in','PLAN-SCALED APPROXIMATION'),
 'TX-BATH4': (8+4/12,4+8/12,'A2.1 007A/B lower-level Bath 4, 8ft-4in long sanitary fixture wall / approximately 4ft-8in clear depth','DRAWING DIMENSION AND APPROX. ENCLOSURE'),
 'TX-POWDER2': (3+9.75/12,7.0,'A2.1 010A/B powder 2, distinct from 009A/B MECH; about 3ft-9 3/4in by 7ft-0in','DRAWING DIMENSION AND APPROX. ENCLOSURE, ROOM NUMBER CORRECTED'),
 'TX-POWDER': (6+4/12,3+6/12,'A2.1 102A/B first-floor powder, approximately 6ft-4in x 3ft-6in, oriented along kitchen wall; previous 3ft x 7ft-6in aspect unsupported','PLAN-SCALED APPROXIMATION, REORIENTED')
}
# Published viewer identifiers follow the latest labeled architectural floor
# plan; legacy state/ROOMS.json and room champions remain immutable. These
# discrepancies affect SPATIAL ROOM IDENTIFICATION, not any tile pick.
DRAWING_ID_CORRECTIONS={'PH-WC':['314A','314B'],'TX-POWDER2':['010A','010B']}
# Normalized (x,z) locations traced from A2.1/A2.2 2026-11-07. The diagrams
# preserve relational fixture placement and door side, not shop coordinates.
# Conditional TUB/WALK-IN rooms retain the branch UNSELECTED regardless of
# what the architect's drawing depicts. Physical B is mirrored where the
# source floor plans depict A/B mirror pairs.
DRAWING_SYMBOLS={
 # Latest 2026-11-07 A2.2 high-resolution 3rd-floor 305A/B explicitly draws
 # both 59in built-in TUB outlines along the SOUTH/lobby-side wall, not the
 # north sink/entry wall previously implied by R042 normalized pictograms.
 # Countertop/lavatory at NORTH, wall-hung WC above south tub. Door enters
 # from EAST (A)/WEST (B) near the north/elevator side. These are RELATIVE
 # source-derived symbols, not surveyed fixture insertion coordinates.
 'PH-BATH2': dict(entry='rear-right',items=[('tub',.50,.80),('toilet',.25,.45),('lavatory',.18,.12)]),
 'PH-BATH3': dict(entry='rear-right',items=[('tub-reference',.17,.50),('toilet',.56,.64),('lavatory',.88,.83)]),
 'PH-PRIMARY': dict(entry=None,items=[('vanity',.72,.72),('shower-reference',.23,.36)]),
 'PH-WC': dict(entry='rear-left',items=[('toilet',.50,.50)]),
 'PH-POWDER': dict(entry='front-left',items=[('toilet',.55,.20),('lavatory',.50,.76)]),
 'TX-PRIMARY': dict(entry=None,items=[('vanity',.30,.73),('shower-reference',.82,.26)]),
 'TX-BATH2': dict(entry='front-right',items=[('tub',.50,.19),('toilet',.48,.59),('lavatory',.18,.83)]),
 'TX-BATH3': dict(entry='rear-left',items=[('lavatory',.80,.14),('toilet',.80,.45),('tub-reference',.51,.82)]),
 'TX-WC': dict(entry='front-left',items=[('toilet',.50,.52)]),
 # High-resolution latest 2026-11-07 A2.1 LOWER LEVEL redraw 007A/B:
 # UNIT A east: wet/tub compartment is EAST/right of the WC; the small sink
 # is WEST/left, not vice versa. B mirrors. Source toilet/countertop 270AA
 # insertion records corroborate the sink's WEST/left placement in A.
 # This depicts RELATIVE drawing handedness only; exact 59in Duravit physical
 # fit/rough-in is still gated against native room walls and source fixtures.
 'TX-BATH4': dict(entry=None,items=[('tub',.80,.50),('toilet',.55,.38),('lavatory',.15,.17)]),
 'TX-POWDER2': dict(entry='front-right',items=[('toilet',.55,.22),('lavatory',.50,.79)]),
 'TX-POWDER': dict(entry='front-left',items=[('toilet',.22,.50),('lavatory',.78,.50)])
}
assert len(DRAWING_SYMBOLS)==12
assert len(SOURCE_ENVELOPES)==13
for room in payload['rooms']:
 rid=room['id']
 width,depth,evidence,confidence=SOURCE_ENVELOPES[rid]
 assert width>0 and depth>0
 if rid in DRAWING_ID_CORRECTIONS:
  room['frozen_schedule_room_numbers']=list(room['numbers'])
  room['numbers']=DRAWING_ID_CORRECTIONS[rid]
 room['full_room_plan']={
  'shape':'RECTANGULAR ENVELOPE STUDY; actual native room polygon NOT EXTRACTED',
  'width_ft':width,'depth_ft':depth,
  'display_area_ft2':round(width*depth,2),
  'not_a_quantity_or_verified_floor_area':True,
  'source_floor_area_ft2':room['wet_zone_schematic']['floor_area']['value'] if room['wet_zone_schematic'].get('floor_area') else None,
  'confidence':confidence,
  'evidence':evidence,'plan_source':SOURCE,
  'interior_detail_source':DETAIL,
  'entry_side':'UNVERIFIED',
  'door_cutouts':None,'openings':None,
  'actual_wall_type_and_thickness':None,
  'fixtures_transform':None,
  'revit_room_boundary':None,
  'wet_zone_orientation':'UNVERIFIED',
  'model_scope':'Full compartment envelope for interactive planning, not a site coordination/fabrication model'
 }
 if rid in DRAWING_SYMBOLS:
  spec=DRAWING_SYMBOLS[rid]
  room['full_room_plan']['fixture_symbol_diagram']={
   'items':[dict(kind=k,x_fraction=x,z_fraction=z) for k,x,z in spec['items']],
   'entry_side':spec['entry'],
   'confidence':'PLAN-TRACED RELATIONAL POSITIONS ONLY; symbols not native family solids or scaled fixtures',
   'conditional_tub_reference_only':rid in ['PH-BATH3','TX-BATH3'],
   'source':SOURCE}
 if rid=='PH-BATH4':
  assert room['full_room_plan']['display_area_ft2']<30
  assert room['full_room_plan']['source_floor_area_ft2']==35
 assert len(room['physical_instances'])==2
 for inst in room['physical_instances']:
  if rid in DRAWING_ID_CORRECTIONS:
   original=inst['room_number']
   corrected=DRAWING_ID_CORRECTIONS[rid][0 if original.endswith('A') else 1]
   inst['frozen_schedule_room_number']=original
   inst['room_number']=corrected
   inst['room_number_correction']={
    'status':'DRAWING VERIFIED LABEL, SOURCE SCHEDULE DISCREPANCY',
    'original':original,'latest_drawing':corrected,
    'source':SOURCE,'owner_pick_status_unchanged':True
   }
   room['full_room_plan']['room_number_discrepancy']='Latest architectural room number corrected in viewer only; legacy schedule retained'
  inst['full_room_plan_evidence']=room['full_room_plan']['plan_source']
  inst['full_room_plan_spatial_status']='Drawing room name and compartment type known; exact A/B boundary placement in Revit NOT spatially verified'
  if rid in DRAWING_SYMBOLS:
   inst['plan_is_mirrored_B']=inst['room_number'].endswith('B')
  if rid=='PH-BATH4':
   side=inst['room_number'][-1]
   inst['plan_handedness']='LEFT ENTRY / SHOWER RIGHT' if side=='A' else 'RIGHT ENTRY / SHOWER LEFT'
   inst['plan_entry_side']='left' if side=='A' else 'right'
   inst['plan_shower_side']='right' if side=='A' else 'left'
   inst['plan_entry_type']='OPEN SIDE FROM BEDROOM; entrance is a gap in the short side partition, NOT a swinging door'
   inst['plan_entry_schematic']={
    'side':'left' if side=='A' else 'right',
    'open_front_fraction':0.5,
    'opening_width_ft':None,
    'status':'DRAWING-WALL-BREAK; opening length 1/2 of side depth illustrative, actual jamb length not dimensioned'
   }
   inst['adjacent_zone']={
    'number':'310A' if side=='A' else '310B',
    'label':'WIC 4' if side=='A' else 'BATH 4 — toilet and lavatory',
    'depth_ft':7+5/12,
    'width_ft':width,
    'status':'A2.2 overall 12ft-5in north-south span minus 311 shower depth 5ft-0in; plan-derived, subject to wall-finish offsets',
    'drawn_fixtures':['TOILET SYMBOL','LAVATORY SYMBOL'],
    'tile_scope':'ADJACENT ROOM ONLY; 311 shower room tile allowance NOT EXPANDED'
   }
  if rid=='PH-BATH3':
   inst['plan_fixture_diagram']={
    'sources':['A2.2 third-floor 307A/B; 7ft-0in x 5ft-0in compartment'],
    'symbols':['TUB left','TOILET center','LAVATORY right'],
    'qualifier':'Plan-diagram footprint positions and fixture identities only; not native family solids. Frozen TUB/WALK-IN decision remains UNSELECTED.'
   }
payload['phase']='v3_full_room_drawing_envelope_study'
payload['full_room_geometry_verified']=False
PATH.write_text(json.dumps(payload,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
acc=ROOT/'deliverables/viewer3d/ACCURACY.md'
# v2 native-context matrix is regenerated before this v3 plan overlay.
# Amend its PRIMARY room ID column using the latest plan, not merely an
# appended caveat that leaves contradictory original room numbers on page one.
original_accuracy=acc.read_text(encoding='utf-8')
for legacy,corrected in (
 ('| PH-WC (313A/313B) |','| PH-WC (314A/314B; frozen legacy 313A/313B) |'),
 ('| TX-POWDER2 (009A/009B) |','| TX-POWDER2 (010A/010B; frozen legacy 009A/009B) |')
):
 assert original_accuracy.count(legacy)==1,(legacy,'missing or duplicate matrix entry')
 original_accuracy=original_accuracy.replace(legacy,corrected)
acc.write_text(original_accuracy,encoding='utf-8')
with acc.open('a',encoding='utf-8') as f:
 f.write('\n## Full bathroom plan envelope study (R042)\n')
 f.write('- Source architectural floor-plan PDFs: '+SOURCE+'; bathroom interiors: '+DETAIL+'. All room types now have complete **compartment envelope studies**, separate from measured wet alcoves. These are approximate, not Revit room solids or fixture position evidence.\n')
 f.write('- PH-BATH4: LATEST OWNER-UPLOADED 2026-11-07 A2.2 confirms 311A and 311B MIRRORED 5ft-5in x 5ft-0in shower compartments (27.08 SF DISPLAY ONLY), with bedroom-facing side openings and an OUTER-SIDE shower, not a rear full-width shower. Both adjoining 310A (WIC4) and 310B (BATH4) show toilet and lavatory plan symbols, even though 310A is named WIC4. These are separate compartments and NOT part of the 311 material takeoff. Original 40.2 SF gross LEVEL/POINT PAN pool unchanged. 35 SF owner override conflicts.\n')
 f.write('- CRITICAL DRAWING ROOM NUMBER MISMATCHES: frozen PH-WC 313A/B is actually labeled PRIMARY WC 314A/B in November A2.2; frozen TX-POWDER2 009A/B is labeled MECH, and lower-level POWDER 2 is 010A/B in A2.1. Viewer physical instances show 314A/B and 010A/B, retaining original labels in metadata for reconciliation. DO NOT ALTER frozen champion or approval files.\n')
 f.write('- Other room-envelope rectangle dimensions remain plan-scaled approximations using historical stated area, NOT certified dimension strings, wall thickness or opening positions. Geometry deliberately omits invented door cuts and family fixtures.\n')
 for room in payload['rooms']:
  p=room['full_room_plan']
  f.write(f"- {room['id']} {'/'.join(room['numbers'])}: {p['width_ft']:.3f} x {p['depth_ft']:.3f} ft display envelope; {p['confidence']}; reference {p['evidence']}; original floor source {p['source_floor_area_ft2']} SF; no quantity change.\n")
 f.write('- These drawing-derived full-room enclosures are a meaningful visual improvement but do NOT meet exact-Revit photorealistic BIM release. Room actual polygon, hosted openings, floor slab thickness, ceiling slope, tested pan/drain and fixture transforms still require native geometry or explicit measured dimensions.\n')
print('PASS 13 full compartment envelope studies; 26 physical instance identities, PH-BATH4 27.08 display SF versus 35 SF source conflict preserved')
