"""Pre-review private R015 _key JSON trailing literal slash-n correction, no critic exposure."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1]
S=R/"state"
out=S/"ROUND015_PRIVATE_KEY_JSON_FIX.json"
assert not out.exists()
assert not (S/"ROUND015_CRITIC_DISPATCH.json").exists()
assert not (S/"ROUND015_SCORING.json").exists()
def fp(p):
 b=p.read_bytes()
 return {"sha256":hashlib.sha256(b).hexdigest(),"bytes":len(b)}
results=[]
for room in ("TX-BATH2","TX-BATH4"):
 p=R/"rooms"/room/"board/round-015/_key.json"
 before=fp(p)
 t=p.read_text(encoding="utf-8")
 assert t.endswith(chr(92)+"n")
 obj=json.loads(t.replace(chr(92)+"n",chr(10)))
 assert obj["round"]==15 and obj["room"]==room and obj["confidential_prime_and_reviewer_only"]
 assert len(obj["neutral_candidate_roles"])==2
 p.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+chr(10),encoding="utf-8")
 results.append({"room":room,"before":before,"after":fp(p),"private":True})
out.write_text(json.dumps({"round":15,"as_of":"2026-11-06","reason":"original private JSON source had literal trailing backslash-n not a newline; fixed BEFORE reviewer or any critic dispatch","private_key_repairs":results,"critic_dispatch":False,"weighted_scoring":None,"owner_approval":False,"procurement_release":False},indent=2)+chr(10),encoding="utf-8")
print("PASS two confidential R015 _key JSON corrected and parseable, no source candidate changes, dispatch/scoring null")
print("KEY_FIX_SHA",fp(out)["sha256"])
