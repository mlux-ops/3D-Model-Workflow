"""Add one truthful post-interruption R016 source-only continuation ledger record."""
from pathlib import Path
import json,hashlib
from decimal import Decimal
R=Path(__file__).resolve().parents[1];S=R/"state";L=S/"LEDGER.md"
HEADER="## Round016 three-powder-room blind source cycle after Loop continuation and original-seat HOLD — 2026-11-06"
assert HEADER not in L.read_text(encoding="utf-8")
def fingerprint(p):
 b=p.read_bytes()
 return {"sha256":hashlib.sha256(b).hexdigest(),"bytes":len(b)}
s=S/"ROUND016_SUBMISSION.json"
d=json.loads(s.read_text(encoding="utf-8"))
assert fingerprint(s)["sha256"]=="1265b5fce959a862d1e7c067c44be434eba174a56ab57b595d1365309221aa2e"
assert d["critic_dispatch"]=="NOT_DISPATCHED" and d["R016_weighted_scoring"] is None
assert len(d["candidate_source"])==3 and sum(len(v) for v in d["candidate_source"].values())==6
assert sum(Decimal(x["material_usd"])*2 for x in d["room_source_per_copy_gross_and_usd"].values())==Decimal("2159.30")
for room,options in d["candidate_source"].items():
 for letter,record in options.items():
  assert fingerprint(R/record["path"])=={"sha256":record["sha256"],"bytes":record["bytes"]}
assert fingerprint(S/"ROUND014_SUBMISSION.json")["sha256"]==d["R014_source_sha256"]
assert fingerprint(S/"ROUND015_SUBMISSION.json")["sha256"]==d["R015_source_sha256"]
assert fingerprint(R/"deliverables/integrated-r21-install-witness-sequence/MANIFEST.json")["sha256"]==d["last_signed_R21_manifest_sha256"]
assert not (S/"ROUND014_CRITIC_COLLECTION.json").exists()
assert not (S/"ROUND014_SCORING.json").exists()
assert not (S/"ROUND015_CRITIC_DISPATCH.json").exists()
assert not (S/"ROUND015_SCORING.json").exists()
assert not (S/"ROUND016_CRITIC_DISPATCH.json").exists()
assert not (S/"ROUND016_SCORING.json").exists()

text="\n"+HEADER+"\n\n"
text+="- Recovered original project authority after reported Loop delivery interruption at approximately 21:08 UTC. Re-read loop AGENTS, board/BOARD, owner feedback, all 13 current ROOMS and final signed LEDGER. Actual agents action=status: original DESIGN worker-9 FAILED/unclaimed two browser revival commands and 3 waiting; original MARKET worker-13, BUILD worker-10 and COST worker-12 asleep with their authentic 6/8 PH-BATH3/TX-BATH3 R014 reports intact; sole standing non-Pro Reviewer worker-15 asleep/revivable. R014 DESIGN two files absent, R014 weighted score or collection nonexistent. R015 TX-BATH2/TX-BATH4 source has independent pre-dispatch CONTINUE but no four-seat critic dispatch.\n"
text+="- Re-asked same independent successor worker-15 to interpret board/BOARD.md 84–103 and original user instructions before any R015 partial seat dispatch. Actual Reviewer returned HOLD, not permission: four original critic seats required for R015 board dispatch, source clearance explicitly dispatch_ready=false; missing original worker9 may not be impersonated by one of three sleeping specialists or a new worker without documented authorized governance amendment. The latest user request to continue and score only with four opinions does NOT amend that constraint. No R014/R015 scoring, no worker reassignment, no R015 critic dispatch or unauthorized owner decisions.\n"
text+="- Reassessed original 13 room board and selected meaningful next technical source focus of three ACTIVE dry powder rooms below stable 4.0: PH Powder, TX Powder, TX Powder2. Unlike wet Bath3 program decisions, these can improve manufacturer-specific layout/market/installer/evidence design independently. Created new R016 six equal-depth neutral source packets, two alternatives per room, under each room's board/round-016/candidates and confidential prime/Reviewer-only mappings. Options compare Earth Lines glossy relief versus a conditional FLAT DRY painted Brizo Luxe Gold wall-mounted trim plane in PH; controlled matte Haze Camel/Wheat 70:30 versus Earth Lines glossy at TX Powder keeping Hansgrohe 48140991 WALL rough; and Indigo Edge 6x6 full relief versus Earth Lines 2x10 alternative at TX Powder2, keeping Tecturis 73072341 Brushed Black Chrome DECK faucet and UNSELECTED basin. None of these walls-only materials is used in wet showers, bath floors or tile PANS. Wood floors remain.\n"
text+="- New neutral shared maker evidence research/products/R16_POWDER_THREE_ROOM_FLAT_LANDING_SHOP_AND_COMP_SOURCE_20261106.md, prior ELM sources and precise distinct price origins. R016 signed SOURCE SHA "+fingerprint(s)["sha256"]+" with six frozen candidate SHA/byte receipts and three confidential maps. scratch/verify_round016_blind_powder_source_readonly.py PASS six candidate fingerprints, 24 links, neutral headings and three original dated quote rows: PH Powder $368.18/copy gross44.9SF, TX Powder $379.37/copy gross31.8SF, TX Powder2 $332.10/copy gross40.5SF; $2,159.30 for two copies of all three rooms (subset of historic four-unit $23,572.44 material-only, original 15% gross waste ONCE). No current lot/installed quote, field net, owner cap or approved paint landing inferred. R014/R015/R17-R21 source unchanged.\n"
text+="- R016 is SOURCE-PREPARED ONLY, awaiting same non-Pro Reviewer independent pre-dispatch FIX/CONTINUE. Its four-seat critics cannot be authentically dispatched while original worker9 cannot claim its seat; no private maps sent to specialists; no scoring and no owner/architect/GC/PO release. R20/R21 prior CONTINUE valid. On exact R016 pre-dispatch FIX correct source in SAME round; after CONTINUE preserve cleared source pending original DESIGN governance and continue technical/owner evidence without bypass. Selection board R015 phase=2-board; future R016 preflight. Global thirteen-room objective OPEN.\n"
with L.open("a",encoding="utf-8",newline="") as f:f.write(text)
print("PASS R016 substantive dry-powder neutral source ledger and original-seat governance HOLD, no weighted scores or releases")
