"""One-time record of independent non-Pro R014 Bath3 manual addendum clearance.

No modification to any signed R013-R16 or additive addendum outputs or critics.
"""
from pathlib import Path
import hashlib, json

R=Path(__file__).resolve().parents[1]
S=R/"state"
MAN=R/"deliverables/r014-bath3-point-drain-installation-addendum/MANIFEST.json"
R16=R/"deliverables/integrated-r16/MANIFEST.json"
SOURCE=S/"ROUND014_SUBMISSION.json"
DISPATCH=S/"ROUND014_CRITIC_DISPATCH.json"
OUT=S/"ROUND014_BATH3_ADDENDUM_REVIEWER_CLEARANCE.json"
LEDGER=S/"LEDGER.md"
TITLE="## Round014 independent non-Pro clearance of additive Bath3 Delta/Brizo manuals — 2026-11-06"
assert not OUT.exists(), "Existing receipt must remain immutable"
assert TITLE not in LEDGER.read_text(encoding="utf-8"), "Already recorded in ledger"

def fp(p):
    b=p.read_bytes()
    return {"sha256":hashlib.sha256(b).hexdigest(),"bytes":len(b)}

assert fp(MAN)["sha256"]=="5974eef4be47f7126ab7bec00f08ef2890c6a45022baf88feea244c23af23ac3"
assert fp(R16)["sha256"]=="03bf0e1e811642d72778df053fcaa5495920a653db02ec36bddaa7b76f1ed7c1"
assert fp(SOURCE)["sha256"]=="946b3eda0a097961e28e76823607fd7d52b82209156e5bb59cdeb9c36450c8ed"
assert fp(DISPATCH)["sha256"]=="f1d27d7e220e8581b2d039c42107595745305c95925f808850e018f4edf50270"
m=json.loads(MAN.read_text(encoding="utf-8"))
for fn, sig in m["outputs"].items():
    assert fp(MAN.parent/fn)==sig,fn
assert m["all_critic_scores"] is None and m["weighted_scoring"] is None
assert m["owner_approval"] is False and m["procurement_release"] is False
assert not (S/"ROUND014_SCORING.json").exists()

receipt={
    "round":14,
    "as_of":"2026-11-06",
    "standing_non_pro_reviewer":"worker-14",
    "actual_independent_result":"CONTINUE — SAME-R014 additive PH/TX Bath3 point-drain installation addendum and R16 FIX3 clearance pass independently; no narrow FIX required",
    "scope":"Additive Bath3 manual/quantities/owner program and R16 independent receipt ONLY; not original four-critic collection or formal R014 scoring or global DONE",
    "reviewer_read_only":True,
    "reviewer_reported_sha_checks_passed":51,
    "reviewer_reported_geometry_checks_each_room":16,
    "reviewer_reported_geometry_checks_passed":True,
    "signed_addendum_manifest_sha256":fp(MAN)["sha256"],
    "signed_r16_manifest_sha256":fp(R16)["sha256"],
    "frozen_r014_source_sha256":fp(SOURCE)["sha256"],
    "immutable_dispatch_sha256":fp(DISPATCH)["sha256"],
    "manuals":{
        "PH-BATH3":"https://media.deltafaucet.com/MandI/113919%20Rev%20B.pdf",
        "TX-BATH3":"https://media.brizo.com/MandI/113920%20Rev%20C.pdf"
    },
    "reviewer_manual_observations":{
        "distinct_one_quarter_in_per_foot_pipe_pitch_and_mortar_pre_slope":True,
        "conventional_clamped_liner_drain_not_arbitrary_bonded_system":True,
        "actual_two_inch_trap_mortar_liner_weeps_and_flood_still_require_field_shop":True,
        "selected_Delta_and_Brizo_square_POINT_preserved":True,
        "unselected_Brizo_new_family_or_Primary_linear_not_substituted":True
    },
    "source_15pct_waste_included_once":True,
    "original_historic_four_unit_material_usd":23572.44,
    "owner_Bath3_TUB_vs_WALKIN_selected":False,
    "exact_numeric_wet_LEVEL_PAN_DCOF_evidenced":False,
    "native_1529_geometry_verified":False,
    "all_critic_scores":None,
    "weighted_scoring":None,
    "owner_approval":False,
    "procurement_release":False,
    "global_13_room_done":False
}
OUT.write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
ledger="\n"+TITLE+"\n\n"
ledger+="- Actual read-only worker-14: CONTINUE — SAME-R014 additive Bath3 official manufacturer drain/branch source and R16 FIX3 receipt accepted with no narrow FIX; 51 SHA/provenance checks PASS, 16/16 geometry/source checks each Bath3 PASS. Reviewer receipt SHA "+fp(OUT)["sha256"]+".\n"
ledger+="- Official Delta 113919 Rev B and Brizo 113920 Rev C page images independently inspected: separate pipe pitch and presloped shower mortar 1/4-in/ft, clamped waterproof liner, curb/wall turns, bolted collar, weep protection and water test. Source details are NOT project-specific membrane shop certification or owner-selected tub waste.\n"
ledger+="- Original R014 source "+fp(SOURCE)["sha256"]+", dispatch "+fp(DISPATCH)["sha256"]+", signed R16 "+fp(R16)["sha256"]+", additive Bath3 manifest "+fp(MAN)["sha256"]+" preserved. Nothing rescored, released or owner-approved. DESIGN seat pending at this checkpoint; only complete 8/8 authentic original critic collection permits independent collection audit.\n"
with LEDGER.open("a",encoding="utf-8",newline="") as h:
    h.write(ledger)
assert fp(MAN)["sha256"]==receipt["signed_addendum_manifest_sha256"]
print("PASS actual independent non-Pro R014 Bath3 addendum CONTINUE receipt and ledger; 51 SHA and 16/16 per room reported, NO scored source or release")
print("CLEARANCE_SHA",fp(OUT)["sha256"])
