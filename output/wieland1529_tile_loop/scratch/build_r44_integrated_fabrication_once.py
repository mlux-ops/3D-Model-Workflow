"""Additive R44 fabrication, architecture and GC package. Immutable predecessors."""
from pathlib import Path
from decimal import Decimal
import csv,io,json,hashlib,math
B=Path(__file__).resolve().parents[1]
D=B/"deliverables/integrated-r44-field-jig-wet-architecture-and-13room-procurement"
assert not D.exists()
PRE={
 "R43_FULL":("deliverables/integrated-r43-four-wet-bath-niche-focal-wall-fabrication-and-13room-GC/MANIFEST.json","71921913b2f8efb733a40d1ca87154c8d816af1519e1a59e5f7dc03943a5d6b0"),
 "R44_SOURCE":("state/ROUND044_NEXT_SOURCE_ONLY_CONTINUOUS_W3_FINISHED_PIER_CAPACITY_PREPARED_NOT_REVIEWED.json","b354b6fffe308bc204c68ee7a56559a6ed3c7dab6ae3dcaea8621f1d43e5c0f5"),
 "R42_FULL":("deliverables/integrated-r42-matte-white-thermostat-diverter-tub-spout-field-rough-wet-wall-GC/MANIFEST.json","1659fb4bb1bb57b1a26e8ab17ad36ce40ed49ba41ebd33b6fb45807e21c94712"),
 "R41_FULL":("deliverables/integrated-r41-four-wet-bath-architectural-composition-and-field-shop-13room/MANIFEST.json","7d14ca7d0acd29b6c85ffcaa90a4d6beecb20928fe1fd200073f67966a9fd3f0")
}
for k,(p,sha) in PRE.items():assert hashlib.sha256((B/p).read_bytes()).hexdigest()==sha,k
def rc(p):
 with (B/p).open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
OLD=rc("deliverables/integrated-r17/R17_27_LINE_EVIDENCE_TO_ORDER_CONTROL.csv")
WALL=rc("deliverables/integrated-r17/R17_25_DIMENSIONAL_ELEVATION_SHOP_GATE.csv")
TRADES=rc("deliverables/integrated-r24-room-branch-shop-quantity-and-owner-decisions/R24_65_ROOM_SPECIFIC_ACCEPTANCE_RFI_AND_RELEASE_GATES.csv")
LAB=rc("research/products/R31_20261106_13_SEPARATE_LEVEL_LINEAR_POINT_LAB_SPECIMEN_RECEIVERS.csv")
W50=rc("research/products/R31_20261106_50_TWO_COPY_W1W2W3_FIELD_OPENING_NICHE_VALVE_SURVEY.csv")
U26=rc("research/products/R31_20261106_26_UNIT_ROOM_PROGRAM_AND_BOUNDARY_RECEIVING_WITNESS.csv")
ROOMS=json.loads((B/"state/ROOMS.json").read_text(encoding="utf-8"))["rooms"]
assert (len(OLD),len(WALL),len(TRADES),len(LAB),len(W50),len(U26),len(ROOMS))==(27,25,65,13,50,26,13)
assert sum(Decimal(x["historic_usd_two_copies"] or 0) for x in OLD)==Decimal("23572.44")
F=("PH-BATH3","PH-BATH4","TX-BATH3","TX-BATH4")
W={(x["room"],x["wall"]):x for x in WALL}
O={(x["room"],x["source_surface"]):x for x in OLD}
G={r:json.loads((B/"rooms"/r/"geometry.json").read_text(encoding="utf-8")) for r in F}
assert all(len(G[r]["revit_room_numbers"])==2 for r in F)
PAY={}
def csvout(name,rows):
 assert rows and len({tuple(x) for x in rows})==1
 s=io.StringIO(newline="");writer=csv.DictWriter(s,fieldnames=list(rows[0]),lineterminator="\n");writer.writeheader();writer.writerows(rows)
 PAY[name]=s.getvalue().encode("utf-8-sig")
def md(name,s):PAY[name]=(s.strip()+"\n").encode("utf-8")
def fmt(x):return f"{x:.4f}"
OPTIONS={
"PH-BATH3":[("BETTER","Soho Blue 2x10 Glossy","https://www.elmsurfaces.com/product/soho-blue","Horizontal blue W1 hero with continuous waterproofed W2/W3 returns; Sandstone niche independent wet approval","16in preferred provisional W3; PH3 basin/TUB-WALKIN owner unselected"),
("BEST","Noho Ivory 2x10 Matte","https://www.elmsurfaces.com/product/noho-ivory","Matte vertical wet hero and staggered return, original Opal limited to proven dry wall","W3 niche align to calibrated course datum, no fictional dry boundary")],
"PH-BATH4":[("BETTER","Soho Ivory 2x10 Glossy","https://www.elmsurfaces.com/product/soho-ivory","Gloss vertical continuous three-wall shower with Black Onyx POINT drain focal","Select narrow/centered W3 niche rather than raw marginal 24in"),
("BEST","Noho Ivory 2x10 Matte","https://www.elmsurfaces.com/product/noho-ivory","Full matte wet enclosure with intentional tile joint and return-niche alignment","Preserve Brizo BNX 4in square POINT four-plane PAN vs independent LEVEL")],
"TX-BATH3":[("BETTER","Soho Emerald 2x10 Glossy","https://www.elmsurfaces.com/product/soho-emerald","Green glazed W1 focal, return W2/W3, original Sandstone niche separate","Brizo BNX POINT applies owner WALKIN only"),
("BEST","Noho Emerald 2x10 Matte","https://www.elmsurfaces.com/product/noho-emerald","Matte emerald focal W1 with quieter returns and calibrated offset niche","Archived Emerald needs exact current wet item, no owner TUB/WALKIN decision")],
"TX-BATH4":[("BETTER","Original Cortar Charcoal flat + Soho Ivory 2x10 Glossy niche","https://www.elmsurfaces.com/product/cortar-charcoal","Preserve exact original Charcoal wet wall only if selected size/finish Wet Areas approval; contrast light niche","Original Caviar no individual NICHE proof; actual Duravit tub and Matte White fixtures"),
("BEST","Noho Ivory 2x10 Matte","https://www.elmsurfaces.com/product/noho-ivory","Full light matte three-wall tub wet replacement with distinct flush niche and corner wrap","Higher tile+waterproof labor, R42 thermostatic/diverter spout held; no tiled PAN")]}
assert all(len(OPTIONS[r])==2 for r in F)

SURVEY=[]
for r in F:
 for u in G[r]["revit_room_numbers"]:
  SURVEY.append(dict(room=r,physical_copy=u,source_W3_width_in_UNVERIFIED=W[r,"W3"]["source_width_in_UNVERIFIED"],
   source_W3_height_in_UNVERIFIED=W[r,"W3"]["source_tiled_height_in_UNVERIFIED"],
   datum="W3 left finished edge X0; floor finished level Z0",
   actual_W3_FINISHED_width_in="",actual_W3_FINISHED_height_in="",
   existing_or_owner_authorized_NICHE="",
   niche_actual_center_X_in="",niche_authorized_opening_width_in="",niche_authorized_opening_height_in="",
   niche_actual_sill_bottom_Z_in="",niche_depth_actual_pipe_free_in="",
   actual_tile_calibrated_LONG_in="",actual_tile_calibrated_SHORT_in="",approved_grout_joint_in="",
   actual_LEFT_profile_projection_in="",actual_RIGHT_profile_projection_in="",
   installer_each_side_execution_tolerance_in="",actual_W3_service_glass_pipe_exclusion_X_intervals="",
   actual_valve_to_FINISHED_wall_depth_in="",actual_backer_membrane_compressed_mortar_tile_THICKNESS_mm="",
   site_1529_measured="FALSE",architect_1529_signed="FALSE",plumber_obstruction_signed="FALSE",
   WP_niche_system_signed="FALSE",tiler_profile_caliber_signed="FALSE",
   actual_physical_1TO1_witness="FALSE",owner_approved="FALSE",GC_approved="FALSE",
   purchase_authorized="FALSE"))
assert len(SURVEY)==8
csvout("R44_8_PHYSICAL_SOURCE_ONLY_BLANK_FIELD_SURVEY_INPUT_TEMPLATE.csv",SURVEY)

JIG=r'''#!/usr/bin/env python3
"""Offline measured W3 niche shop geometry check. Prints JSON; NEVER purchase release.
Usage: python R44_FIELD_FINISHED_PIER_OBSTRUCTION_JIG.py field_filled_copy.csv
"""
import sys,csv,json
REQUIRED=("actual_W3_FINISHED_width_in","actual_W3_FINISHED_height_in",
"niche_actual_center_X_in","niche_authorized_opening_width_in","niche_authorized_opening_height_in",
"niche_actual_sill_bottom_Z_in","niche_depth_actual_pipe_free_in",
"actual_tile_calibrated_LONG_in","actual_tile_calibrated_SHORT_in","approved_grout_joint_in",
"actual_LEFT_profile_projection_in","actual_RIGHT_profile_projection_in",
"installer_each_side_execution_tolerance_in","actual_valve_to_FINISHED_wall_depth_in",
"actual_backer_membrane_compressed_mortar_tile_THICKNESS_mm")
SIGNS=("site_1529_measured","architect_1529_signed","plumber_obstruction_signed",
"WP_niche_system_signed","tiler_profile_caliber_signed","actual_physical_1TO1_witness",
"owner_approved","GC_approved")
def check(row):
 ident=str(row.get("room"))+"/"+str(row.get("physical_copy"))
 missing=[k for k in REQUIRED if not str(row.get(k,"")).strip()]
 if missing:return dict(unit=ident,status="HOLD_MISSING_ACTUAL_SURVEY",missing=missing,purchase_authorized=False)
 try:
  v={k:float(row[k]) for k in REQUIRED}
 except (ValueError,TypeError):
  return dict(unit=ident,status="REJECT_INVALID_ACTUAL_SURVEY_NUMERIC",purchase_authorized=False)
 W=v["actual_W3_FINISHED_width_in"];H=v["actual_W3_FINISHED_height_in"]
 N=v["niche_authorized_opening_width_in"];NH=v["niche_authorized_opening_height_in"]
 C=v["niche_actual_center_X_in"];Z=v["niche_actual_sill_bottom_Z_in"]
 left=C-N/2;right=W-C-N/2
 tL=v["actual_LEFT_profile_projection_in"];tR=v["actual_RIGHT_profile_projection_in"]
 tol=v["installer_each_side_execution_tolerance_in"]
 if min(W,H,N,NH,v["actual_tile_calibrated_LONG_in"],v["actual_tile_calibrated_SHORT_in"],v["niche_depth_actual_pipe_free_in"])<=0 or min(tL,tR,tol,v["approved_grout_joint_in"])<0:
  return dict(unit=ident,status="REJECT_NONPHYSICAL_DIMENSION",purchase_authorized=False)
 L=left-tL-tol;R=right-tR-tol
 maxwidth=min(2*(C-3-tL-tol),2*(W-C-3-tR-tol))
 obstruction=str(row.get("actual_W3_service_glass_pipe_exclusion_X_intervals","")).strip()
 if not obstruction:
  return dict(unit=ident,status="HOLD_MISSING_PHYSICAL_OBSTRUCTION_SURVEY",
              finished_left_pier=round(L,4),finished_right_pier=round(R,4),purchase_authorized=False)
 if obstruction.upper()=="NONE":blocked=False
 else:
  try:
   intervals=[]
   for entry in obstruction.split(";"):
    nums=entry.split(":")
    if len(nums)!=2:raise ValueError
    lo,hi=map(float,nums)
    if not (0<=lo<hi<=W):raise ValueError
    intervals.append((lo,hi))
   blocked=any(max(left,lo)<min(left+N,hi) for lo,hi in intervals)
  except ValueError:
   return dict(unit=ident,status="REJECT_INVALID_OBSTRUCTION_INTERVAL",purchase_authorized=False)
 if L<3 or R<3 or Z<0 or Z+NH>H or blocked:
  return dict(unit=ident,status="REJECT_FINISHED_PIER_HEIGHT_OR_OBSTRUCTION",
              finished_left_pier=round(L,4),finished_right_pier=round(R,4),
              maximum_width_at_actual_center=round(maxwidth,4),blocked_by_real_pipe_glass=blocked,
              purchase_authorized=False)
 missing_signoffs=[k for k in SIGNS if row.get(k)!="TRUE"]
 if row.get("existing_or_owner_authorized_NICHE")!="TRUE":
  missing_signoffs.append("owner_authorized_existing_niche_geometry")
 return dict(unit=ident,status="GEOMETRY_PASS_ONLY_NOT_SHOP_RELEASE" if missing_signoffs else "SIGNED_GEOMETRY_ONLY_FURTHER_LAB_AND_GC_GATES",
             finished_left_pier=round(L,4),finished_right_pier=round(R,4),
             maximum_width_at_actual_center=round(maxwidth,4),missing_signatures=missing_signoffs,
             original_raw_numeric_LEVEL_and_independent_PAN_lab="NOT_VERIFIED",
             complete_factory_wet_WALL_NICHE_approval="NOT_VERIFIED",
             current_factory_lot_GC_installed_bid="NOT_VERIFIED",purchase_authorized=False)
def main():
 if len(sys.argv)!=2:raise SystemExit("usage: python R44_FIELD_FINISHED_PIER_OBSTRUCTION_JIG.py field_filled_copy.csv")
 with open(sys.argv[1],encoding="utf-8-sig",newline="") as f:
  for r in csv.DictReader(f):print(json.dumps(check(r),sort_keys=True))
if __name__=="__main__":main()
'''
PAY["R44_FIELD_FINISHED_PIER_OBSTRUCTION_JIG.py"]=JIG.encode("utf-8")
md("R44_FIELD_SURVEY_AND_JIG_OPERATOR_MANUAL.md","""
# R44 field survey and executable fabricator jig

Only true 1529 site-measured FINISHED W3 width, height, X and Z dimensions can clear geometric release; source measurements are labeled UNVERIFIED. Use X=0 at the left finished W3 return, X increases to the right; finish-floor top is Z=0 upward. Record site photos/tape and architect project/address identity. Existing niche count/owner authorization is required. The source CSV intentionally leaves every field measurement empty.

To run, COPY the signed R44_8_PHYSICAL_SOURCE_ONLY_BLANK_FIELD_SURVEY_INPUT_TEMPLATE.csv into an unrelated working scratch copy, enter measured information, then execute the delivered Python R44_FIELD_FINISHED_PIER_OBSTRUCTION_JIG.py followed by the copied CSV path. It only prints JSON. Do not edit or overwrite any signed deliverable.

Actual obstruction syntax: start:end;start:end, where starts/ends are measured finished W3 X inches. Entry NONE is permitted ONLY if the actual plumber/architect affirm no valve, glass, door sweep, pipe, structural or service conflict; empty triggers HOLD. Left and right actual finished tile piers are respectively (center - opening/2 - LEFT profile projection - execution tolerance) and (W - center - opening/2 - RIGHT profile projection - execution tolerance). Both must be at least 3in, with niche SILL and HEAD within measured finished height. Maximum allowable opening at a measured centerline is min(2*(center-3-left profile-tolerance),2*(W-center-3-right profile-tolerance)). The jig independently checks actual exclusion intervals. It does not certify missing Z-depth pipe clashes or any factory system.

After a FAIL, architect may propose a narrower centered/repositioned opening; any valve shift requires signed plumber and owner change; eliminating the niche requires owner/program approval. No new niche is approved just because a mathematical position is available. All 1:1 mockups, manufacturer-specific wet WALL versus NICHE permissions, membrane and drain/tub flange continuity, selected plumbing, numerical raw wet LEVEL/PAN lab, current supplier item/lot/case, paid material credit and installed GC bid remain separate release gates. The script always outputs purchase_authorized false even if all geometry signatures are TRUE.
""")

def jig_input(r,u):
 # Raw source isn't substituted for actual measured information.
 return next(x for x in SURVEY if x["room"]==r and x["physical_copy"]==u)

# Fully deterministic OFFLINE unit test logic. Test synthetic values only,
# no site claim or signed mockup. Output is a signed test expectation.
md("R44_JIG_SYNTHETIC_PASS_FAIL_VERIFICATION_CASES.md","""
# R44 executable jig synthetic tests (not actual 1529 conditions)

Create a scratch copy of any one blank unit input, set hypothetical W3=30.48in, H=93in, N=24in, NH=12in, C=15.24in, Z=40in, tile long=10in, short=2in, grout=.125in, niche depth=4in, actual valve rough finished depth=2.5in, backer+membrane+mortar+tile=22mm and all signed flags FALSE, obstruction NONE.

Case 1: left/right projection=0 and execution tolerance=0. Computed finished piers=3.24/3.24in. Jig returns GEOMETRY_PASS_ONLY_NOT_SHOP_RELEASE; purchase_authorized false.

Case 2: left/right projection=.25in, tolerance=0. Finished piers=2.99/2.99in. REJECT_FINISHED_PIER_HEIGHT_OR_OBSTRUCTION; purchase_authorized false.

Case 3: use 16in centered aperture and projections .25. Finished piers=6.99/6.99in. GEOMETRY_PASS_ONLY_NOT_SHOP_RELEASE; purchase_authorized false.

Case 4: same as case 3 but obstruction 10:20 means niche overlaps an actual *synthetic* pipe/service exclusion. REJECT_FINISHED_PIER_HEIGHT_OR_OBSTRUCTION regardless of pier size.

Case 5: leave obstruction field empty. HOLD_MISSING_PHYSICAL_OBSTRUCTION_SURVEY even if piers pass.

These are deliberately mathematical tests; actual 1529 measurements, manufacturer approvals and owner releases remain absent.
""")

# Physically coordinated focal/W1-W2-W3 WRAP: not merely repeating prior
# generic width-based row arithmetic. Uses ONE actual grid origin per concept
# propagated around each inside corner; the start datum remains provisional.
DATUM=[]
for r in F:
  a=float(W[r,"W1"]["source_width_in_UNVERIFIED"])
  b=float(W[r,"W2"]["source_width_in_UNVERIFIED"])
  c=float(W[r,"W3"]["source_width_in_UNVERIFIED"])
  for tier,item,url,composition,decision in OPTIONS[r]:
   for j in (.125,.1875):
    # Long-axis-on-horizontal vs narrow-axis-on-horizontal actually produces
    # differentiated material/appearance. Factory calibrated dimension null.
    face=10 if "Horizontal" in composition or "horizontal" in composition else 2
    pitch=face+j
    # Datum starts a symmetric W1 axis; turn two corners by carrying running
    # module phase, not resetting centered pattern independently at W2/W3.
    corner1=(a/2)%pitch;corner2=(a/2+b)%pitch;corner3=(a/2+b+c)%pitch
    leftcut=(c-(math.floor(c/pitch)*pitch))/2
    DATUM.append(dict(room=r,tier=tier,material=item,source_W1_width_in_UNVERIFIED=fmt(a),
      source_W2_width_in_UNVERIFIED=fmt(b),source_W3_width_in_UNVERIFIED=fmt(c),
      manufacturer_nominal_horizontal_face_in=fmt(face),
      source_joint_ILLUSTRATIVE_in=fmt(j),nominal_pitch_in=fmt(pitch),
      W1_center_to_INSIDE_corner_running_phase_in=fmt(corner1),
      W2_return_to_W3_running_phase_in=fmt(corner2),
      W3_end_running_phase_in=fmt(corner3),
      naive_independently_centered_W3_cut_in=fmt(leftcut),
      actual_W3_course_align_to_niche_jamb="RECALCULATE_AFTER_FACTORY_CALIBER_AND_TRUE1529_SURVEY",
      source_study_not_authorized_maker_joint="TRUE",true_1529_corner_squareness="UNKNOWN",
      tile_cuts_actual_piece_reuse_verified="FALSE",
      owner_approved="FALSE",architect_approved="FALSE",fabrication_authorized="FALSE"))
assert len(DATUM)==16
csvout("R44_16_COHERENT_W1_W2_W3_CORNER_WRAPPED_FOCAL_MODULE_DATUM_SOURCES.csv",DATUM)

# One controlled measured shop workflow per actual physical unit, not
# hypothetical 108-case table. The blank fields are to be jointly signed.
SHOP=[]
for r in F:
 for u in G[r]["revit_room_numbers"]:
  for stage,tech,accept in (
   ("01_BOUNDARY_AND_PROGRAM","Verify native TRUE 1529 wall faces, finish width, glass centerline, selected fixture program, original niche authority, coordinate datum","Signed architect + owner dimensions; no 1527 transfer"),
   ("02_PIPE_AND_GLASS_EXCLUSION","Survey actual selected valve/service clearance, pipe/structure, door swing, glass/curb footprint and tub rim; record real X intervals","Plumber and glazier sign exclusions; jig fails on overlap"),
   ("03_MAKER_WALL_AND_NICHE","Confirm exact item/color/size/finish individual Wet WALL, independent NICHE and complete substrate/membrane/adhesive system and warranty","Factory written authority for same material and specific assembly"),
   ("04_W1W2W3_MODULE","Transfer one actual tile-grid origin around two corners, trim within calibrated size and approved grout, check all focal/micro-cuts and edge exposures","Architect/tiler sign physical 1:1 W3/valve/niche finish"),
   ("05_WET_JUNCTION_AND_MORTAR","Actual backer/membrane/lap, substrate, compressed mortar, tile body, niche waterproof head/sill/returns and penetration sealing","Waterproofer signs signed detail before closing wall"),
   ("06_TUB_OR_SQUARE_POINT","PH4 selected Brizo BNX square POINT four-plane PAN/LEVEL; PH3/TX3 conditional TUB or WALKIN only; TX4 selected Duravit TUB NO PAN, R42 factory control hold","Plumber/architect selected rough and drain flange/tub flange plus true Z elevations"),
   ("07_FLOOR_AND_THRESHOLD","If shower confirm actual four plane point PAN polygon and slope/threshold/glass, raw exact numeric wet LEVEL + distinct PAN; if tub PAN N/A","Manufacturer original lab + trades sign flood/water test when applicable"),
   ("08_PHYSICAL_1TO1_REJECTION","Sample exact factory lot, calibrated face, tile cut/edge trim movement and waterproof return; photograph after dry fit and water verification","Architect/owner/GC reject sub3in finished piers or unapproved wet"),
   ("09_QUOTE_AND_PAID_SCOPE","Invoice original full wall vs openings once, old niche return material, PAN included/excluded mutually exclusive, supplier exact lot and real GC labor separately","Signed old paid/received credits and current bid, no theoretical saving"),
   ("10_RELEASE","All factory lab/site/owner/architect/plumber/WP/tile/supplier/GC approvals and four original critiques + reviewer","Only purchasing after all external approvals, currently FALSE")
  ):
   SHOP.append(dict(room=r,physical_copy=u,step=stage,contractor_task=tech,measurable_acceptance=accept,
     source_original_owner_program="PH3/TX3 owner TUB WALKIN unselected" if r in ("PH-BATH3","TX-BATH3") else "PH4 fixed WALKIN Brizo BNX POINT" if r=="PH-BATH4" else "TX4 fixed Duravit tub Matte White no PAN",
     actual_TRUE1529_field_or_real_factory_receipt="MISSING",
     actual_physical_1to1_completed="FALSE",owner_approved="FALSE",architect_approved="FALSE",
     plumber_approved="FALSE",waterproofer_approved="FALSE",tiler_approved="FALSE",
     supplier_approved="FALSE",GC_approved="FALSE",purchaser_approved="FALSE",
     purchase_authorized="FALSE"))
assert len(SHOP)==80
csvout("R44_80_EIGHT_PHYSICAL_INSTANCE_TEN_HOLD_POINT_MAKER_FIELD_FABRICATION_INSPECTION.csv",SHOP)

# Four project-specific section diagrams per focus room: actual source W
# sizes drawn, neither real niche nor valve position invented.
def svg(r):
 w=float(W[r,"W3"]["source_width_in_UNVERIFIED"]);h=float(W[r,"W3"]["source_tiled_height_in_UNVERIFIED"])
 a=(w-16)/2
 s=9
 body=f'''<svg xmlns="http://www.w3.org/2000/svg" width="1050" height="590" viewBox="0 0 1050 590">
<rect width="1050" height="590" fill="#faf9f5"/>
<text x="24" y="35" font-family="Arial" font-size="24" fill="#25323c">R44 {r} | Fabricator's true-field W3 survey sheet</text>
<text x="24" y="59" font-family="Arial" font-size="14" fill="#a04940">SOURCE-PROVISIONAL only. NOT certified native 1529 elevation, existing opening or valve placement.</text>
<g stroke="#455b66" stroke-width="2"><rect x="40" y="105" width="{w*s:.1f}" height="285" fill="#e3e8e6"/></g>
<rect x="{40+a*s:.1f}" y="172" width="144" height="110" fill="#fffaf2" stroke="#b0864c" stroke-dasharray="7,4" stroke-width="3"/>
<text x="40" y="410" font-family="Arial" font-size="15">W3 nominal {w:.2f}in / H {h:.2f}in; 16in aperture ONLY schematic</text>
<text x="40" y="435" font-family="Arial" font-size="15">Nominal equal side pier {a:.2f}in (no trim/tolerance)</text>
<text x="40" y="460" font-family="Arial" font-size="14">REAL jig: finish W3, center X, profile L/R, per-side tolerance, obstruction intervals</text>
<g font-family="Arial" font-size="16" fill="#243847">
<text x="520" y="135">W1/W2/W3 actual continuous datum</text>
<text x="520" y="172">1. Select exact wet WALL versus NICHE factory item</text>
<text x="520" y="209">2. Physically locate pipe, glass, valve exclusion</text>
<text x="520" y="246">3. Place flush sill / head / two jambs / backing</text>
<text x="520" y="283">4. Test actual tile + backer + membrane + mortar</text>
<text x="520" y="320">5. Check 3in FINISHED left and right focal piers</text>
<text x="520" y="357">6. Joint movement and edge/profile chosen by maker</text>
<text x="520" y="394">7. Signed 1:1 photograph / water inspection</text>
</g>
<rect x="25" y="500" width="1000" height="66" rx="8" fill="#efe9df"/>
<text x="41" y="526" font-family="Arial" font-size="15" fill="#813e35">REJECT: any sub3in finished pier, blocked pipe/glass, insufficient NICHE wet authority or missing owner instruction.</text>
<text x="41" y="550" font-family="Arial" font-size="14">No automatic payable changes; signed physical size and manufacturer system are separate procurement prerequisites.</text>
</svg>'''
 return body.encode("utf-8")
for r in F:PAY[f"R44_{r}_FABRICATION_W3_FIELD_TEMPLATE_AND_REJECTION_SHOP.svg"]=svg(r)

MAKER=[]
for r in F:
 origin=("Tones Opal 2x20 Glossy" if r=="PH-BATH3" else "Cortar Bone Ribbed" if r=="PH-BATH4" else "Tones Emerald 2x20 Glossy" if r=="TX-BATH3" else "Cortar Charcoal 24x48 Soft")
 url=("https://www.elmsurfaces.com/product/opal-tones" if r=="PH-BATH3" else "https://www.elmsurfaces.com/product/bone-ribbed" if r=="PH-BATH4" else "https://www.elmsurfaces.com/product/emerald-tones" if r=="TX-BATH3" else "https://www.elmsurfaces.com/product/cortar-charcoal")
 evidence=("Individual current page lists Walls/Backsplashes, NOT Wet Areas" if r in ("PH-BATH3","PH-BATH4") else
           "Archived wet-wall listing; current exact individual SKU and application renewal required" if r=="TX-BATH3" else
           "Individual Charcoal page Wet Areas listed; original specified Soft 24x48 exact variant/factory installation to reconcile")
 MAKER.append(dict(room=r,role="HISTORIC_ORIGINAL_WALL",product_identity=origin,current_manufacturer_URL=url,
   maker_individual_wet_WALL_status=evidence,maker_individual_wet_NICHE_status="ABSENT_OR_NOT_ESTABLISHED",
   complete_backer_membrane_mortar_drain_tub_system="UNAPPROVED",
   current_orderable_exact_color_finish_SKU_size_lot="UNKNOWN",
   owner_substitution_approved="FALSE",architect_approved="FALSE",purchasing_approved="FALSE"))
 for tier,item,link,composition,decision in OPTIONS[r]:
  MAKER.append(dict(room=r,role=tier+"_CONDITIONAL_NOT_OWNER_SELECTED",product_identity=item,
   current_manufacturer_URL=link,
   maker_individual_wet_WALL_status="Individual manufacturer item wet WALL listed, selected exact size/finish orderable factory SKU pending" if not (r=="TX-BATH4" and tier=="BETTER") else "Original Charcoal Wet Areas page; original Soft size/factory wall system must be reverified; Soho Ivory niche separately",
   maker_individual_wet_NICHE_status="WET_WALL_LISTING_IS_NOT_INDEPENDENT_NICHE_WP_APPROVAL",
   complete_backer_membrane_mortar_drain_tub_system="UNAPPROVED",
   current_orderable_exact_color_finish_SKU_size_lot="UNKNOWN",
   owner_substitution_approved="FALSE",architect_approved="FALSE",purchasing_approved="FALSE"))
assert len(MAKER)==12
csvout("R44_12_ORIGINAL_CONDITIONAL_INDIVIDUAL_WET_WALL_NICHE_AND_FACTORY_SYSTEM_AUTHORITY.csv",MAKER)

# Actual option-level bid deltas quantify surfaces using only documented
# provisional geometries, visibly segregating net scenario from ORIGINAL gross
# (15% waste already once). No real supplier/case/installed costs are invented.
SCOPE=[];CHOICE=[];bid=[]
for r in F:
 sourcefield=sum(float(W[r,q]["source_width_in_UNVERIFIED"])*float(W[r,q]["source_tiled_height_in_UNVERIFIED"])/144 for q in ("W1","W2","W3"))
 existing_gross=Decimal(O[r,"wall"]["source_gross_sf_one_copy_waste_15pct_once"])
 old_wall_two=Decimal(O[r,"wall"]["historic_usd_two_copies"])
 rate=old_wall_two/(2*existing_gross)
 for u in G[r]["revit_room_numbers"]:
  for tier,item,url,composition,decision in OPTIONS[r]:
   # One illustrative 16x12x4 niche, not existing wall aperture count.
   aperture=16*12/144
   returnface=aperture+2*4*12/144+2*4*16/144
   edge=(2*16+2*12)/12
   for quoteinterp in ("ORIGINAL_FULL_WALL_BILLED","ORIGINAL_OPENING_ALREADY_DEDUCTED"):
    SCOPE.append(dict(room=r,physical_copy=u,tier=tier,historical_wall_source=O[r,"wall"]["source_row_id"],
      original_accent_source=O[r,"accent"]["source_row_id"],proposed_material=item,
      old_quote_INTERPRETATION_MUTUALLY_EXCLUSIVE=quoteinterp,
      source_three_wall_full_NET_SF_UNVERIFIED=fmt(sourcefield),
      illustrative_one_aperture_16x12_NEGATIVE_field_SF=fmt(aperture) if quoteinterp=="ORIGINAL_FULL_WALL_BILLED" else "0.0000_ALREADY_DEDUCTED",
      proposed_new_full_wall_if_REPLACING_all_three_NET_SF=fmt(sourcefield-aperture),
      separate_new_NICHE_back_jambs_head_sill_NET_SF=fmt(returnface),
      proposed_sill_and_profile_if_four_undisguised_EDGES_LF=fmt(edge),
      original_WALL_GROSS_SF_ONE_COPY_with_15pct_once=str(existing_gross),
      original_historic_WALL_material_per_GROSS_SF_USD=fmt(rate),
      original_two_copy_WALL_historic_material_only_USD=str(old_wall_two),
      historic_RATE_is_NOT_new_substitution_price="TRUE",
      original_historic_one_copy_accent_material_only_USD=fmt(Decimal(O[r,"accent"]["historic_usd_two_copies"])/2),
      original_15pct_waste_on_historic_gross_REAPPLIED="FALSE",
      actual_1529_full_wall_after_WINDOWS_ROUGH_NICHE="UNKNOWN",
      actual_approved_new_waste_and_calibrated_TILE_OFFCUT_yield="UNKNOWN",
      actual_new_same_factory_SKU_color_finish_lot_verified="FALSE",
      exact_supplier_box_usable_case_SF_stock_delivery_freight="UNKNOWN",
      original_ordered_paid_received_reusable_material_and_credit="UNKNOWN",
      GC_field_demo_backer_WP_trim_plumber_glass_grout_labor_installed_bid_USD="UNKNOWN",
      signed_change_order_owner_and_GC="FALSE",actual_saved_USD="UNKNOWN_NOT_REALIZED",
      purchaser_approved="FALSE",purchase_authorized="FALSE"))
   for program in (("TUB_NO_TILED_PAN","WALKIN_POINT_PAN_ORIGINAL_QUOTE_INCL","WALKIN_POINT_PAN_ORIGINAL_QUOTE_EXCL") if r in ("PH-BATH3","TX-BATH3") else
                   ("WALKIN_POINT_PAN_ORIGINAL_QUOTE_INCL","WALKIN_POINT_PAN_ORIGINAL_QUOTE_EXCL") if r=="PH-BATH4" else ("DURAVIT_TUB_NO_TILED_PAN",)):
    bid.append(dict(room=r,physical_copy=u,option=tier,source_program_branch=program,
      selected_owner_status="UNSELECTED" if r in ("PH-BATH3","TX-BATH3") else "FIXED",
      original_POINT_shower_drain="DT062412 Chrome only WALKIN" if r=="PH-BATH3" else "BT062415-BNX BNX only WALKIN" if r in ("PH-BATH4","TX-BATH3") else "N_A_TUB",
      actual_original_WALKIN_pan_quote_included="UNKNOWN_MUTUALLY_EXCLUSIVE" if "WALKIN" in program else "N_A_TUB",
      original_exact_raw_numerical_LEVEL_lab="MISSING",
      independent_exact_raw_numerical_POINT_PAN_lab="MISSING" if "WALKIN" in program else "N_A_TUB",
      current_selected_membrane_drain_bonding_or_tub_flange="NOT_APPROVED",
      actual_original_quote_scope_WALL_and_PAN_credit="UNKNOWN",
      actual_current_supplier_and_GC_FURNISH_INSTALL="UNKNOWN",
      owner_program_selected="FALSE" if r in ("PH-BATH3","TX-BATH3") else "TRUE_FIXED",
      owner_option_selected="FALSE",GC_change_order_approved="FALSE",purchase_authorized="FALSE"))
   CHOICE.append(dict(room=r,physical_copy=u,tier=tier,selected_fixture_preservation=decision,
    W1_architectural_composition=composition,W2W3_fabrication_niche_jig="Actual measured pipe/glass obstruction +3in finished piers + shared W1W2W3 datum",
    manufacturer_individual_WALL_item=url,manufacturer_separate_NICHE_waterproofing="NEEDS_WRITTEN_FACTORY_SYSTEM",
    buyer_quality_rationale="Focal cohesive wall, calibrated finishes and maintainable details; no dollar buyer premium asserted",
    historic_material_already_in_original="TRUE",current_Chicago_material_supply_AND_installed_labor_delta="UNKNOWN",
    full_1TO1_physical_mockup_and_render_created="FALSE",owner_approved="FALSE",architect_approved="FALSE",
    four_authentic_blind_specialists_scored="FALSE",weighted_score="NULL",
    purchase_authorized="FALSE"))
assert len(SCOPE)==32 and len(CHOICE)==16 and len(bid)==36
# GOOD is retained historical visual reference, explicitly NONINSTALLABLE
# where its individual maker wet application has not been authenticated.
for r in F:
 for u in G[r]["revit_room_numbers"]:
  CHOICE.append(dict(room=r,physical_copy=u,tier="GOOD_HISTORIC_UNRELEASED",
   selected_fixture_preservation="ALL ORIGINAL OWNER AND PLUMBING PROGRAMS UNCHANGED",
   W1_architectural_composition="Retain historical original palette visually only; maker exact Wet WALL and independent NICHE permissions may be absent",
   W2W3_fabrication_niche_jig="No approved cut until true 1529 site and independent original factory wet system/3in finished piers",
   manufacturer_individual_WALL_item="ORIGINAL_SCHEDULE_NOT_FACTORY_CLEARED",
   manufacturer_separate_NICHE_waterproofing="NEEDS_WRITTEN_FACTORY_SYSTEM",
   buyer_quality_rationale="Baseline appearance for comparison, NOT construction-compliant or owner-approved release",
   historic_material_already_in_original="TRUE",
   current_Chicago_material_supply_AND_installed_labor_delta="UNKNOWN",
   full_1TO1_physical_mockup_and_render_created="FALSE",owner_approved="FALSE",
   architect_approved="FALSE",four_authentic_blind_specialists_scored="FALSE",
   weighted_score="NULL",purchase_authorized="FALSE"))
assert len(CHOICE)==24
csvout("R44_32_INSTALLED_WALL_SCOPE_AND_HISTORIC_FULL_VS_DEDUCTED_QUOTE_NORMALIZATION.csv",SCOPE)
csvout("R44_24_EIGHT_PHYSICAL_GOOD_BETTER_BEST_UNSCORED_ARCHITECTURAL_DECISIONS.csv",CHOICE)
csvout("R44_36_MUTUALLY_EXCLUSIVE_OWNER_TUB_OR_POINT_PAN_ORIGINAL_CONTRACT_AND_GC_BID_BRANCH.csv",bid)

UNIT=[]
for s in U26:
 r=s["room"]
 UNIT.append(dict(room=r,physical_copy_index=s["physical_copy_index"],
  source_room_number_UNPLACED_if_not_verified=s["source_room_number_UNPLACED_IF_NOT_ACTUALLY_VERIFIED"],
  old_R31_original_program=s["program"],
  new_focus_fabrication_jig="R44_8_FIELD_TEMPLATE_AND_WALL_WET_CORNERS" if r in F else "SOURCE_R31_PRESERVED",
  true_1529_field_address_and_W1W2W3_verified="FALSE",
  original_raw_numeric_wet_LEVEL="N_A_WOOD" if "POWDER" in r else "INHERIT_PARENT_PRIMARY" if r.endswith("-WC") else "MISSING",
  distinct_raw_numeric_POINT_OR_LINEAR_PAN="N_A_TUB" if r in ("PH-BATH2","TX-BATH2","TX-BATH4") else
  "N_A_WOOD_OR_WC" if "POWDER" in r or r.endswith("-WC") else
  "MISSING_IF_WALKIN" if r in ("PH-BATH3","TX-BATH3") else "MISSING",
  exact_original_selected_plumbing_unmodified="TRUE",
  owner_approved="FALSE",architect_approved="FALSE",plumber_approved="FALSE",
  WP_approved="FALSE",tiler_approved="FALSE",supplier_approved="FALSE",
  GC_approved="FALSE",purchaser_approved="FALSE",purchase_authorized="FALSE"))
assert len(UNIT)==26
csvout("R44_26_ORIGINAL_PHYSICAL_INSTANCE_CROSS_TRADE_WET_LAB_AND_JIG_WITNESS_BRIDGE.csv",UNIT)

REL=[]
for r in ROOMS:
 room=r["id"]
 source=(
  "PH_BATH3_UNSELECTED_TUB_OR_WALKIN_Chrome_DELTA_POINT_ONLY_WALKIN" if room=="PH-BATH3" else
  "PH_BATH4_FIXED_WALKIN_BRIZO_BNX_4IN_SQUARE_POINT_SEPARATE_4PLANE_PAN_AND_LEVEL" if room=="PH-BATH4" else
  "TX_BATH3_UNSELECTED_TUB_OR_WALKIN_BRIZO_BNX_POINT_ONLY_WALKIN" if room=="TX-BATH3" else
  "TX_BATH4_FIXED_DURAVIT_TUB_MATTE_WHITE_NO_PAN_R42_CONTROL_HOLD" if room=="TX-BATH4" else
  "PRIMARY_BNX_48IN_LINEAR_SEPARATE_ROUGH_NO_NICHE" if room in ("PH-PRIMARY","TX-PRIMARY") else
  "WC_PARENT_PRIMARY_FLOOR_INHERITED_ONCE_TX203A_UNPLACED" if room in ("PH-WC","TX-WC") else
  "OTHER_DURAVIT_TUB_NO_PAN_HANSGROHE_ORIGINAL_FINISH" if room in ("PH-BATH2","TX-BATH2") else
  "DRY_POWDER_WOOD_FLOOR_PRESERVE_WALL_VS_DECK_AND_BASIN_UNSELECTED")
 REL.append(dict(room=room,formal_board_round=17,original_status=r["status"],
  original_champion_id=r.get("champion_id") or "null",
  original_champion_score=str(r.get("champion_score")) if r.get("champion_score") is not None else "null",
  owner_program_original_fixed_or_unselected=source,old_owner_selected_fixture_CHANGED="FALSE",
  original_exact_WET_WALL_and_independent_NICHE_authorization="MISSING_OR_N_A_DRY",
  original_NUMERIC_raw_LEVEL_wet_DCOF="MISSING_OR_N_A_WOOD",
  separate_original_NUMERIC_raw_POINT_LINEAR_PAN_wet_DCOF="MISSING_OR_N_A_TUB_OR_DRY",
  original_15pct_in_old_GROSS_once="TRUE",true_native_1529_site_measurements_received="FALSE",
  original_paid_material_current_Chicago_supplier_factory_SKU_lot_box_and_GC_bid="UNKNOWN",
  original_all_four_AUTHENTIC_critic_scores_and_reviewer_CLEARANCE="FALSE",
  owner_approved="FALSE",architect_approved="FALSE",plumber_approved="FALSE",
  WP_approved="FALSE",tiler_approved="FALSE",supplier_approved="FALSE",
  GC_approved="FALSE",purchaser_approved="FALSE",purchase_authorized="FALSE"))
assert len(REL)==13
csvout("R44_13_ORIGINAL_ROOM_SELECTED_PROGRAM_WET_LAB_AND_UNRELEASED_AUTHORITY.csv",REL)

OLDN=[]
for x in OLD:
 OLDN.append(dict(room=x["room"],original_row_id=x["source_row_id"],
  original_surface=x["source_surface"],historic_GROSS_SF_one_copy_original_15pct_ONCE=x["source_gross_sf_one_copy_waste_15pct_once"],
  historic_two_copy_material_only_USD=x["historic_usd_two_copies"],original_excluded_PRIMARY_niche_no_order=x["historic_niche_excluded_no_scope"],
  R44_original_vs_new_material_delta="R44_32_CONDITIONAL_NONPAYABLE_SHOP" if x["room"] in F else "HISTORICAL_UNCHANGED",
  same_exact_SKU_COLOR_FINISH_CALIBER_LOT_and_OFFCUT_condition_authorized="FALSE",
  exact_current_factory_usable_box_chicago_stock_freight="UNKNOWN",actual_GC_all_trades_installed_bid="UNKNOWN",
  original_paid_material_returnable_credit="UNKNOWN",owner_approved="FALSE",
  purchaser_approved="FALSE",purchase_authorized="FALSE"))
assert len(OLDN)==27
csvout("R44_27_HISTORICAL_MATERIAL_LINES_CURRENT_SUPPLIER_AND_GC_NORMALIZATION.csv",OLDN)

SEQ=[]
TRADE=("OWNER","ARCHITECT","PLUMBER","WATERPROOFING","TILE_INSTALLER","SUPPLIER","GC","PURCHASER")
for r in (x["id"] for x in ROOMS):
 for i,t in enumerate(TRADE,1):
  action={
   "OWNER":"Select original conditional program/material/niche only if desired; explicit budget and approved changed scheme",
   "ARCHITECT":"Certify 1529 wall X/Z and actual W1/W2/W3 corner datum, minimum3in finished piers and actual opening",
   "PLUMBER":"Inspect selected rough valve, service, pipe exclusion, tub flange or BNX/Delta point drain; carry R42 conflict",
   "WATERPROOFING":"Approve manufacturer-specific wet WALL vs NICHE membranes, head/sill/corners/penetrations and tub/drain continuity",
   "TILE_INSTALLER":"Physical 1:1 factory calibrated tile, grout/profile/cut, actual finish plane, original raw LEVEL and separate PAN lab",
   "SUPPLIER":"Current exact factory SKU color finish/lot usable carton Chicago offer freight ETA and true offcut reuse",
   "GC":"Old invoiced full wall vs deducted opening and original PAN inclusion, paid credits, waterproof/demo labor + complete installed bid",
   "PURCHASER":"Post all real owner + seven trades, original four critic scores/hard gates and authentic Reviewer clearance"
  }[t]
  SEQ.append(dict(room=r,sequence=i,trade=t,shop_requirement=action,
   original_owner_program_unchanged="TRUE",
   real_trade_signature="FALSE",owner_approved="FALSE",GC_approved="FALSE",
   purchaser_approved="FALSE",purchase_authorized="FALSE"))
assert len(SEQ)==104
csvout("R44_104_SEQUENTIAL_13ROOM_EIGHT_TRADE_SHOP_JIG_AND_PROCUREMENT_HOLDS.csv",SEQ)

for r in F:
 w={x:float(W[r,x]["source_width_in_UNVERIFIED"]) for x in ("W1","W2","W3")}
 h=float(W[r,"W3"]["source_tiled_height_in_UNVERIFIED"])
 original=O[r,"wall"];accent=O[r,"accent"]
 program=("Owner TUB/WALKIN UNSELECTED, Hansgrohe Chrome; Delta DT062412 Chrome square POINT only WALKIN; basin UNSELECTED" if r=="PH-BATH3" else
 "FIXED WALKIN, Brizo BT062415-BNX Black Onyx square POINT with distinct four-plane PAN and bath LEVEL, no tub" if r=="PH-BATH4" else
 "Owner TUB/WALKIN UNSELECTED, Brizo BT062415-BNX Black Onyx square POINT only WALKIN" if r=="TX-BATH3" else
 "FIXED Duravit 700332000000090 TUB, Hansgrohe Matte White, NO tiled PAN; unresolved 15758701 thermostat vs PB-only 72411701 spout")
 lines=[f"# R44 {r} field-fabrication and architecture wet assembly",
 f"Original source physical copies: {', '.join(G[r]['revit_room_numbers'])}. Original fixture/program **{program}**. No selected owner design changed.",
 "## GOOD historical visual only",
 "Historic owner tile scheme retained as the comparison, but construction wet-wall or niche permission NOT assumed. This is not an owner-authorized changed tile.",
 "## BETTER and BEST distinct proposals"]
 for tier,item,url,composition,decision in OPTIONS[r]:
  lines += [f"### {tier}: {item}",f"Official manufacturer item: {url}.","W1/W2/W3: "+composition,
            "Fabrication and original fixture integration: "+decision,
            "Wet WALL product listing is distinct from exact NICHE waterproofing/mortar/backer/corner manufacturer approval; no SKU/finish/lot or owner choice invented."]
 lines += ["## Dimensioned W1/W2/W3 source and actual field jig",
 f"Drawing-provisional W1={w['W1']:.2f}in, W2={w['W2']:.2f}in, W3={w['W3']:.2f}in, tiled height={h:.2f}in, ALL unverified true 1529.",
 f"A hypothetical centered 16in x12in opening would leave {(w['W3']-16)/2:.2f}in raw source side piers; actual finished left/right must individually >=3.0in after actual profile projections, per-side tolerance, tile calibrated module, pipe/glass exclusion. No actual existing opening location is implied.",
 "Start tile grid on the actual W1 fixture/focal centerline and propagate its pitch around W1/W2/W3 corners, not separately centering returns. Match actual long/short calibrated size, manufacturer-approved illustrative 1/8 or 3/16in grout only after real SKU/lot and joint rules; 2in tile short-axis is not a fabricated 3in focal side-pier violation.",
 "Real field jig requires actual 1529 W3 finished width/height, signed owner-authorized niche centerline/sill/depth, true X obstruction intervals for valve/pipe/glass/door swing, actual LEFT/RIGHT edge trim projections, per-side tolerance, calibrated tile, fixture-to-finished plane and real backer/membrane/compressed mortar assembly.",
 "If any real finished side pier below 3in, height overlap or valve/glass/pipe obstruction: STOP. Architect may narrow or recenter opening, or omit/revise it after owner approval; relocating valve is separate licensed plumber + owner signoff. Never erase exclusion intervals to force PASS.",
 "## Wet section and actual 1:1 commissioning",
 "Source WALL aperture deducted once; manufacturer-approved niche BACK, two jambs, head and inward draining supported sill counted separately; actual trim lengths depend on exposed edges and selected profile, with movement joints at wall plane changes. Selected tile BODY thickness not same as compressed mortar + membrane + backer + tile finished projection. Confirm escutcheon seal/service and exact rough depth, then signed full-scale physical niche, transition, valve/glass, finished pier photos, membrane/waterproof inspection and accurate shop drawings.",
 "Where owner WALKIN selected or already fixed: maintain original selected four-inch POINT drain and true four-plane separately approved PAN receiving its own original measured numeric wet DCOF, independent bath LEVEL numeric raw measured wet test; certify actual centerline/slope/threshold/rough/bonding flange and water test. When actual TUB, preserve original tub flange/waste/overflow, no tiled shower PAN, LEVEL test remains required; original R42 manufacturer control conflict stays held in TX4.",
 "## Procurement and GC installed-scope consequences",
 f"Old historic WALL row {original['source_row_id']} = {original['source_gross_sf_one_copy_waste_15pct_once']}SF GROSS one-copy old original 15% once; old accent/niche row {accent['source_row_id']} already included. One hypothetical 16x12x4 niche wall field -1.3333SF once, BACK +1.3333, two sides +0.6667, head +0.4444, sill +0.4444 = +2.8889SF niche internal face NET, four-edge hypothetical trim 4.6667LF if all exposed. New approved actual layout may differ.",
 "GC quote compares mutually exclusive original full wall vs opening-already-deducted invoice and owner TUB vs shower POINT PAN original included/excluded branches, original paid/received/returnable material credit, new SKU/lot and physical offcuts, real waterproofing/rough/plumbing/glass/tile/trim labor. No theoretical credit, new 15% on historic gross, case yield, Chicago price, supplier lot or paid change order asserted.",
 "## 1:1 and owner image/camera brief",
 "Before owner presentation image or physical mockup, obtain true source 1529 camera/view and fixture/tub/walkin program. Render W1 focal and W3 niche with accurate tile manufacturer and finish, selected chrome/black/matte-white hardware, realistic actual grout/edges and actual niche width; show a separate detailed section of selected backed membrane and opening. No actual render or physical sample was generated.",
 "All original original specialists, independent Reviewer, wet maker approvals, raw numeric lab, actual site, owner/architect/plumber/WP/tile/supplier/GC/purchasing release flags FALSE. This is an unscored concept, not a code certified issued construction drawing."]
 md(f"R44_{r}_COORDINATED_SHOP_W1W2W3_NICHE_AND_FLOOR_OR_TUB_SECTIONS.md","\n\n".join(lines))

focus_usd=sum(Decimal(x["historic_usd_two_copies"] or "0") for x in OLD if x["room"] in F)
assert focus_usd==Decimal("9124.72")
md("START_HERE_R44_FULL_EIGHT_UNIT_ARCHITECTURAL_FIELD_JIG_AND_13ROOM_GC_OWNER_BOOK.md",f"""
# R44 complete additive four-bath/eight-unit architectural fabrication and 13-room GC program

**Entire 13-room objective OPEN, no release.** The original full signed R43 SHA {PRE["R43_FULL"][1]} and preliminary signed R44 source SHA {PRE["R44_SOURCE"][1]} are immutable predecessors, not overwritten.

## Substantive new work beyond prior niche scenarios

Deliver an actual OFFLINE executable, fail-closed finished-niche fabrication survey jig with eight original physical-room blank field input forms and synthetically documented pass/fail results, not just repeated R43 64 pier cases or R44 preliminary 108 scenarios. The jig checks real asymmetric left/right finished pier projections, measured true 1529 W3 X/Z/height, physical valve/glass/pipe service exclusion intervals, manufacturer tile calibrated dimensions and required geometry signoffs; incomplete/malformed survey HOLD/REJECT. It ALWAYS reports purchase_authorized false, even when geometry and signatures are provisionally acceptable, because actual manufacturer wet WALL vs independent NICHE system, raw numeric wet flooring labs, supplier SKU/lot/usable cartons and full GC installed scope are outside the jig.

Architectural package includes four conditional source W3 SVG elevation templates, 16 continuous-corner tile datum calculations derived from source W1/W2/W3 but not site measurements, four room-specific coordinated wet section books with differentiated R41/R43 alternatives genuinely connected to the physical proposed niche position, selected valve and glass, plus 24 eight-physical-unit GOOD/BETTER/BEST visual-construction decisions. GOOD retains historic appearance but cannot clear unproven wet original item applications. BETTER and BEST use current individual manufacturer Wet Areas WALL candidates, with independent NICHE membrane approval, owner substitution and factory orderable SKU/lot unresolved.

**Manufacturer evidence discipline:** Current individual Tones Opal and Cortar Bone Ribbed pages list Walls/Backsplashes but not Wet Areas, so no wet-wall authority is inferred; original Caviar collection does not authorize an exact wet NICHE. Original Tones Emerald archived Wet Areas source awaits live exact item renewal, Cortar Charcoal individual product page lists Wet Areas but owner-selected original Soft 24x48 finish/application/installation needs confirmation. Soho/Noho distinct sizes/colors/finishes individual wet-WALL listings do not transfer to different materials or the complete manufacturer niche membrane/adhesive/setting system.

## Physical wall/floor/rough and quantification

Eight actual source physical units have 80 separate ten-stage field-shop/installer/architect/plumber/waterproof/GC commissioning checkpoints. Non-negotiable PH-BATH4 WALKIN selected Brizo Black Onyx square POINT and four-plane PAN separate bath LEVEL; PH-BATH3/TX-BATH3 owner TUB/WALKIN undecided and selected POINT drains only shower branches; TX-BATH4 Duravit tub/Hansgrohe Matte White NO tiled PAN, R42 selected thermostat/diverter incompatibility held. Original both Primary 48in Black Onyx BNX LINEAR with separate rough, no added niches; WC floors inherited from parent, PH2/TX2/TX4 existing Duravit tubs no PAN and powder faucet mounting/unselected basin original constraints maintained.

Conditional source 16x12x4 niche means wall field -1.3333SF ONCE, niche BACK 1.3333+two side 0.6667+head .4444+sill .4444 = 2.8889SF net inner face before separately approved waste; four-edge theoretical trim 4.6667LF if all exposed. Original four-focus 12 historical two-copy tile material rows **USD {focus_usd}** ALREADY inside original 13-room four-unit historic **USD 23572.44** material-only, original 15% waste included once. Sandstone USD358.92, Cortar Grey USD1116.46, Caviar USD1163.32 and powder USD2159.30 remain included. New 32 full-wall versus opening-deducted SOURCE contracts, 36 original TUB/WALKIN/PAN included/excluded mutually exclusive program/installed GC scopes, 27 original material supplier quote/lot normalized lines, NO current factory yield/Chicago price, lead time, stock, paid credit, real labor quote, supplier confirmed offcut or approved saving.

Full original 13 distinct room IDs/26 physical instances, R31 13 lab specimen requirements, 50 wall targets, 25 source elevations, 65 trade actions and 104 original eight-trade sequential accepts integrated, all FALSE. Individual exact SKU/color/finish numerical original RAW wet LEVEL DCOF separate from sloped LINEAR/POINT PAN exact lab; generic threshold/target insufficient. Tub-only PAN/wood powder DCOF N/A; no 1527 model geometry asserted as 1529. 14 listing entries/nine buildings, Old Town first $2.4M-$3.2M PH $2.8M TX $2.7M; Lincoln Park/Gold Coast secondary, no competitor tile or buyer premium invented.

Original R014 DESIGN worker9 FAILED missing two critiques, R017 frozen original private keys, Reviewer worker15 FINISHED/nonrevivable. MARKET .30 DESIGN .25 BUILD .25 COST .20 original panel, individual >=3 and hard gates plus weighted +.25 required for actual challenger adoption. No critic dispatch or score, all new designs UNSCORED. No current samples, owner signatures, vendor/owner communication, email, purchases, Revit/Smartsheet/Git/model writes or GLOBAL DONE.
""")

lineage=dict(json.loads((B/PRE["R43_FULL"][0]).read_text(encoding="utf-8"))["predecessor_signed_file_hashes"])
lineage.update({k:h for k,(p,h) in PRE.items()})
meta=dict(round=44,date_local="2026-11-06",formal_board_round=17,
 phase="FULL_EIGHT_INSTANCE_FIELD_EXECUTABLE_NICHE_JIG_ARCHITECTURAL_13ROOM_GC_UNRELEASED",
 predecessor_signed_file_hashes=lineage,focus_rooms=list(F),
 physical_focus_copies=8,original_room_count=13,original_physical_copies=26,
 original_material_rows=27,original_wall_elevations=25,original_trade_actions=65,
 original_R31_wet_labs=13,original_R31_walls=50,original_R31_instances=26,
 original_material_ONLY_USD="23572.44",original_gross_old_15pct_waste_once=True,
 original_four_focus_material_ALREADY_INCLUDED_USD=str(focus_usd),
 original_Sandstone_INCL_USD="358.92",original_Cortar_Grey_INCL_USD="1116.46",
 original_Caviar_INCL_USD="1163.32",original_Powder_INCL_USD="2159.30",
 old_market_listings=14,distinct_market_buildings=9,
 executable_fail_closed_fabrication_jig=True,physical_blank_survey_templates=len(SURVEY),
 coordinated_three_wall_corner_datums=len(DATUM),actual_physical_trade_stages=len(SHOP),
 conditional_source_W3_fabrication_drawings=4,maker_individual_wet_WALL_vs_NICHE_rows=len(MAKER),
 wall_original_FULL_vs_DEDUCTED_GC_scope=len(SCOPE),unscored_GOOD_BETTER_BEST=len(CHOICE),
 mutually_exclusive_program_and_pan_contract_branches=len(bid),
 original_physical_unit_witnesses=len(UNIT),original_all_room_release=len(REL),
 original_material_supplier_normalization=len(OLDN),eight_trade_sequential=len(SEQ),
 original_OWNED_selected_program_CHANGED=False,actual_true_1529_geometry_received=False,
 actual_owner_selected_concept_or_niche=False,
 full_manufacturer_exact_original_WET_WALL_and_independent_WET_NICHE_approval=False,
 exact_original_RAW_numerical_wet_LEVEL_and_independent_POINT_LINEAR_PAN_lab_received=False,
 original_selected_tub_flange_POINT_drain_WP_bonding_approved=False,
 original_R42_thermostat_spout_incompatibility_resolved=False,
 original_PAN_full_wall_included_excluded_contract_interpretation_resolved=False,
 physical_1to1_sample_or_render_produced=False,
 current_supplier_usable_cases_Chicago_offer_and_installed_GC_bid_received=False,
 original_paid_returnable_inventory_verified=False,
 original_four_authentic_blind_critiques_complete=False,original_nonpro_Reviewer_GLOBAL_DONE=False,
 owner_approved=False,architect_approved=False,plumber_approved=False,WP_approved=False,
 tiler_approved=False,supplier_approved=False,GC_approved=False,purchaser_approved=False,
 purchase_authorized=False,global_DONE=False,
 files=[dict(path=n,bytes=len(data),sha256=hashlib.sha256(data).hexdigest()) for n,data in sorted(PAY.items())])
print("R44_EXPECTED_TECHNICAL_PAYLOADS",len(PAY))
assert len(PAY)>=22
D.mkdir(parents=True,exist_ok=False)
for name,data in sorted(PAY.items()):
 with (D/name).open("xb") as f:f.write(data)
(D/"MANIFEST.json").write_bytes((json.dumps(meta,indent=2,ensure_ascii=False)+"\n").encode("utf-8"))
print("R44_FULL_SHA",hashlib.sha256((D/"MANIFEST.json").read_bytes()).hexdigest())
