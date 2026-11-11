#!/usr/bin/env python3
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
