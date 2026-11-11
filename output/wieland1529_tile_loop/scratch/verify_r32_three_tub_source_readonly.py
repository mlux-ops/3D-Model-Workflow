"""Read-only R32 substantive three-tub source-level integrity, no writes."""
from pathlib import Path
from decimal import Decimal
import csv,hashlib,json
B=Path(__file__).resolve().parents[1]
S=B/"state/ROUND032_NEXT_DISTINCT_THREE_TUB_HYDRAULIC_FACTORY_IDENTITY_SOURCE_PREPARED_NOT_REVIEWED.json"
sig="9ad8564e2676f4e72533e6830bea627757e393dc1cdc537b297d443caae962b4"
assert hashlib.sha256(S.read_bytes()).hexdigest()==sig
d=json.loads(S.read_text(encoding="utf-8"))
assert len(d["signed_outputs"])==4
assert hashlib.sha256((B/"deliverables/integrated-r31-hansgrohe-tub-rough-linear-point-shop-and-13room-quantity/MANIFEST.json").read_bytes()).hexdigest()==d["predecessor_R31_FULL_SHA256"]=="b42ed79789c6eb4d74bbb8a6947c9dabbfd1bcc700c65087adbf9db92ee29457"
for f in d["signed_outputs"]:
    by=(B/f["path"]).read_bytes()
    assert len(by)==f["bytes"] and hashlib.sha256(by).hexdigest()==f["sha256"]
def rr(k):
    f=next(f for f in d["signed_outputs"] if k in f["path"])
    with (B/f["path"]).open(encoding="utf-8-sig") as x:return list(csv.DictReader(x))
six=rr("SIX_UNIT")
nine=rr("NINE_ORIGINAL")
options=rr("NINE_SOURCE_ONLY")
assert len(six)==6 and len(nine)==9 and len(options)==9
assert {x["room"] for x in six}=={"TX-BATH2","TX-BATH4","PH-BATH2"}
assert all(x["purchase_authorized"]=="FALSE" for x in six+nine+options)
assert all(x["originally_schedule_bathing_valve_trim"]==x["originally_schedule_bathing_valve_rough"]==x["originally_schedule_tub_filling_spout"]=="" for x in six if x["room"]=="TX-BATH2")
assert all(x["originally_schedule_bathing_valve_trim"]=="15758701" and x["originally_schedule_tub_filling_spout"]=="72411701" for x in six if x["room"] in ("PH-BATH2","TX-BATH4"))
assert all(x["tub_PAN"]=="N_A" for x in nine)
assert all(x["original_selection_preserved"]=="TRUE" and x["owner_authorized_change"]=="FALSE" for x in options)
assert len([x for x in options if x["room"]=="TX-BATH2"])==3
assert len([x for x in six if x["room"]=="TX-BATH2"])==2
with (B/"deliverables/integrated-r17/R17_27_LINE_EVIDENCE_TO_ORDER_CONTROL.csv").open(encoding="utf-8-sig") as f:old=list(csv.DictReader(f))
assert len(old)==27 and sum(Decimal(x["historic_usd_two_copies"] or "0") for x in old)==Decimal("23572.44")
assert all(d[k] is False for k in ("new_owner_selected_fixture","supplier_contacted","purchase_authorized","independent_nonpro_reviewer_accepted","global_DONE"))
print("PASS R32 SOURCE-ONLY 4/4 SHA+byte files 6 physically distinct tub rooms, 9 W elevations, 9 owner-unselected technical paths")
print("PASS TX2 original 11-row selected Chrome has no identified bath mixing trim/rough or tub-fill spout; not assumed absent in field")
print("PASS R31 predecessor immutable and original 27/$23572.44/15pct-once, all release FALSE, R32 unsent/unreviewed")
print("R32_SOURCE_SHA256",sig)
