#!/usr/bin/env python3
"""Preliminary R45 site-measured physical W3 niche clearance.
NO project/model/network/vendor interaction. Returns engineering geometry only.
NEVER purchase approval. X measured from finished W3 left corner, Z above
finished bath LEVEL floor. A missing actual depth or obstruction survey HOLD.
"""
import csv,json,sys
MEASURED=("actual_W3_FINISHED_WIDTH_in","actual_W3_FINISHED_HEIGHT_in",
          "ACTUAL_niche_X0_in","ACTUAL_niche_X1_in",
          "ACTUAL_niche_Z0_in","ACTUAL_niche_Z1_in",
          "ACTUAL_left_profile_and_tolerance_in","ACTUAL_right_profile_and_tolerance_in",
          "ACTUAL_available_niche_backing_depth_in","ACTUAL_required_niche_assembly_depth_in")
def evaluate(row):
 id_=str(row.get("room"))+"/"+str(row.get("physical_copy"))
 missing=[k for k in MEASURED if not str(row.get(k,"")).strip()]
 if missing:return dict(unit=id_,status="HOLD_REAL_SURVEY_MISSING",missing=missing,purchase_authorized=False)
 try:
  v={k:float(row[k]) for k in MEASURED}
 except (ValueError,TypeError):
  return dict(unit=id_,status="REJECT_NUMERIC_SURVEY",purchase_authorized=False)
 W=v["actual_W3_FINISHED_WIDTH_in"];H=v["actual_W3_FINISHED_HEIGHT_in"]
 a=v["ACTUAL_niche_X0_in"];b=v["ACTUAL_niche_X1_in"]
 z0=v["ACTUAL_niche_Z0_in"];z1=v["ACTUAL_niche_Z1_in"]
 profL=v["ACTUAL_left_profile_and_tolerance_in"]
 profR=v["ACTUAL_right_profile_and_tolerance_in"]
 depth=v["ACTUAL_available_niche_backing_depth_in"]
 req=v["ACTUAL_required_niche_assembly_depth_in"]
 if not (W>0 and H>0 and 0<=a<b<=W and 0<=z0<z1<=H and profL>=0 and profR>=0 and depth>0 and req>0):
  return dict(unit=id_,status="REJECT_NONPHYSICAL_REAL_SURVEY",purchase_authorized=False)
 finished_L=a-profL;finished_R=W-b-profR
 if finished_L<3 or finished_R<3:
  return dict(unit=id_,status="REJECT_FINISHED_W3_PIER_MINIMUM",
              actual_left_FINISHED_pier_in=round(finished_L,4),
              actual_right_FINISHED_pier_in=round(finished_R,4),purchase_authorized=False)
 if depth<req:
  return dict(unit=id_,status="REJECT_ACTUAL_BACKING_DEPTH",
              actual_depth_in=depth,required_depth_in=req,purchase_authorized=False)
 raw=str(row.get("ACTUAL_SIGNED_obstruction_rectangles_X0_X1_Z0_Z1","")).strip()
 if not raw:return dict(unit=id_,status="HOLD_NO_SIGNED_2D_PIPE_VALVE_GLASS_SURVEY",purchase_authorized=False)
 if raw.upper()=="NONE":rects=[]
 else:
  try:
   rects=[]
   for item in raw.split(";"):
    nums=[float(n) for n in item.split(":")]
    if len(nums)!=4:raise ValueError
    x0,x1,y0,y1=nums
    if not (0<=x0<x1<=W and 0<=y0<y1<=H):raise ValueError
    rects.append(nums)
  except ValueError:
   return dict(unit=id_,status="REJECT_BAD_2D_OBSTRUCTION_GEOMETRY",purchase_authorized=False)
 colliding=[rect for rect in rects if max(a,rect[0])<min(b,rect[1]) and max(z0,rect[2])<min(z1,rect[3])]
 if colliding:return dict(unit=id_,status="REJECT_ACTUAL_TWO_DIMENSIONAL_CLASH",
                          colliding_rectangles=colliding,purchase_authorized=False)
 signed=("certified_TRUE_1529_site_survey","plumber_signed_XZ_obstructions",
         "architect_approved_EXISTING_niche_location","maker_signed_individual_WET_WALL_and_NICHE_system",
         "waterproofer_signed_backer_and_membrane","tile_installer_SIGNED_1TO1")
 holds=[name for name in signed if row.get(name)!="TRUE"]
 return dict(unit=id_,status="GEOMETRY_XZ_PASS_SHOP_HOLDS" if holds else "FIELD_XZ_SIGNATURES_PRESENT_STILL_NO_LAB_OR_GC_RELEASE",
             finished_left_pier_in=round(finished_L,4),
             finished_right_pier_in=round(finished_R,4),
             actual_pipe_glass_obstructions_checked=len(rects),missing_signatures=holds,
             exact_original_wet_LEVEL_PAN_RAW_measured_numeric_labs="NOT_VERIFIED",
             selected_drain_tub_membrane_factory_system="NOT_VERIFIED",
             original_PAID_stock_current_supplier_and_FULL_GC_bid="NOT_VERIFIED",
             purchase_authorized=False)
def main():
 if len(sys.argv)!=2:raise SystemExit("usage: python R45_FIELD_W3_2D_XZ_NICHE_VALE_GLASS_OBSTRUCTION_SOLVER_SOURCE_ONLY.py actual_survey_copy.csv")
 with open(sys.argv[1],encoding="utf-8-sig",newline="") as f:
  for r in csv.DictReader(f):print(json.dumps(evaluate(r),sort_keys=True))
if __name__=="__main__":main()
