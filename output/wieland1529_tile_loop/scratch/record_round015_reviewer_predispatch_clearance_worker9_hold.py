"""One-time actual independent worker-14 CONTINUE for R015 source, not dispatch.

R014 DESIGN seat worker-9 is failed; this clearance is source-only and does
not authorize invented critic reports, weighted scores, purchase or owner approval.
"""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1];S=R/"state";D=R/"deliverables"
OUT=S/"ROUND015_PREDISPATCH_REVIEWER_CLEARANCE.json"
LEDGER=S/"LEDGER.md"
H="## Round015 real non-Pro Reviewer pre-dispatch CONTINUE and original DESIGN seat routing hold — 2026-11-06"
assert not OUT.exists() and H not in LEDGER.read_text(encoding="utf-8")
def fp(p):
 b=p.read_bytes()
 return {"sha256":hashlib.sha256(b).hexdigest(),"bytes":len(b)}
src=S/"ROUND015_SUBMISSION.json"
r17=D/"integrated-r17/MANIFEST.json"
leads=D/"integrated-r17-numeric-product-leads/MANIFEST.json"
assert fp(src)["sha256"]=="cf150c8156ab556c0b7dee386f62d8cdda33a4e14ea54019731fc345957dbca8"
assert fp(r17)["sha256"]=="78c0849c14a83dba65023d7ede812181d7360d2c7cd00eaa2f8cc0e33927aac1"
assert fp(leads)["sha256"]=="988166847464298c8341061e9bebdc7e4fedd83dc09fcaff5c5e6d80eecd146a"
s=json.loads(src.read_text(encoding="utf-8"))
assert s["critic_dispatch"]=="NOT_DISPATCHED"
assert s["all_critic_scores"] is None and s["weighted_scoring"] is None
assert not (S/"ROUND015_CRITIC_DISPATCH.json").exists()
assert not (S/"ROUND015_CRITIC_COLLECTION.json").exists()
assert not (S/"ROUND015_SCORING.json").exists()
assert not (S/"ROUND014_CRITIC_COLLECTION.json").exists()
assert not (S/"ROUND014_SCORING.json").exists()
for rid,letters in s["candidate_files"].items():
 for letter,rec in letters.items():
  assert fp(R/rec["file"])=={"sha256":rec["sha256"],"bytes":rec["bytes"]}
assert fp(R/s["shared_neutral_maker_research"])["sha256"]==s["shared_neutral_maker_research_sha256"]
receipt={
 "round":15,"as_of":"2026-11-06",
 "standing_independent_non_pro_reviewer":"worker-14",
 "actual_result":"CONTINUE — SAME-R015 corrected blind source and R17 owner/GC book independently CLEARED",
 "scope":"R015 neutral four candidate technical pre-dispatch SOURCE ONLY; R17 owner book revised, separate numerical lead source. No workers dispatched and no R014/R015 collection or weighted scoring",
 "independent_reviewer_shas_checked":34,"independent_reviewer_sha_errors":0,
 "source_submission_sha256":fp(src)["sha256"],
 "shared_maker_research_sha256":s["shared_neutral_maker_research_sha256"],
 "candidate_sha_byte_checks":4,"candidate_local_link_checks":32,"candidate_external_links_recorded":12,
 "private_key_checks":2,"blind_role_cues_fixed_and_cleared":True,
 "r17_signed_manifest_sha256":fp(r17)["sha256"],
 "r17_source_rows":27,"r17_trade_actions":65,"r17_wall_studies":25,"r17_rooms":13,
 "r17_numerical_research_manifest_sha256":fp(leads)["sha256"],
 "R014_original_worker9_design_status":"FAILED browser did not claim two revivals; worker chat exists; 2 of 8 R014 reports absent",
 "R014_original_reports_collected":6,"R014_original_reports_required":8,
 "R015_four_authentic_critic_seat_dispatch_ready":False,
 "R015_dispatch_blocked_reason":"Original DESIGN seat worker-9 cannot claim task; do not substitute without explicit governance resolution",
 "R015_critic_dispatch":"NOT_DISPATCHED","all_critic_scores":None,
 "R014_weighted_scoring":None,"R015_weighted_scoring":None,
 "native_1529_verified":False,"raw_numeric_level_DCOF_verified":False,
 "owner_approval":False,"GC_release":False,"procurement_release":False,
 "global_13_room_done":False
}
OUT.write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
t="\n"+H+"\n\n"
t+="- **Actual original independent worker-14 returned CONTINUE**, NOT global DONE, on SAME-R015 corrected four neutral source candidates, revised R17 signed owner book and separate numeric product leads. Source submission SHA "+fp(src)["sha256"]+"; Reviewer reported **34 SHA/byte/pointer checks, zero mismatches**, 32 local links/12 maker URLs, 2 confidential role maps. Signed R17 manifest "+fp(r17)["sha256"]+"; optional public numeric lead manifest "+fp(leads)["sha256"]+". Receipt "+fp(OUT)["sha256"]+".\n"
t+="- **Pre-dispatch only:** four original candidates independently source-cleared with correct EL30 Mexico, KC04 USA grout 3/16, distinct maker Wet Areas listing vs owner approval, no private history role labels. TUB-only Duravit programs TX2 Chrome basin unselected and TX4 Matte White no PAN. Strict raw numerical exact wet LEVEL DCOF absent and R15 candidate source/dispatch score NULL. Critic dispatch remains **NOT DISPATCHED**, even though source has CONTINUE.\n"
t+="- **Actual blocked worker routing:** worker-9 original DESIGN seat state FAILED after two browser unclaimed revival attempts; existing worker chat tab was read-only inspected and displayed Task failed. Six authentic R014 reports only; two DESIGN files absent. No new worker was substituted or called a critic, no R014 weighted score, no R015 dispatch. Authentic four-seat governance requires verified original worker recovery OR a user-authorized explicit governance change; no blindly repeated revive.\n"
t+="- **Owner program and commercial gates still open:** Bath3 TUB/WALK-IN, PH3/TX2/TX Powder2 basins; original $23,572.44 with 15% gross once, no added niches in Primaries; source 27/65/25/13 independent R17 review PASS; exact wet lab, 1529 geometry, installed local Chicago bid/lot, proper tub/drain/membrane shop and owner/GC signatures null. All procurement release FALSE, all signed older outputs preserved.\n"
with LEDGER.open("a",encoding="utf-8",newline="") as f:f.write(t)
print("PASS actual R015 non-Pro Reviewer source CONTINUE signed receipt, ledger appended; R015 dispatch blocked by original DESIGN seat; no R014/R015 scoring/releases")
print("CLEARANCE_SHA",fp(OUT)["sha256"])
