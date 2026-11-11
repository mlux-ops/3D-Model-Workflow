"""One-time pre-Reviewer SAME-R015 research role-language removal and SHA pointer fix."""
from pathlib import Path
import hashlib,json,re
R=Path(__file__).resolve().parents[1];S=R/"state"
src=S/"ROUND015_SUBMISSION.json"
out=S/"ROUND015_SHARED_RESEARCH_ROLE_NEUTRALITY_FIX.json"
assert not out.exists()
assert not (S/"ROUND015_CRITIC_DISPATCH.json").exists()
assert not (S/"ROUND015_SCORING.json").exists()
def fp(p):
 b=p.read_bytes()
 return {"sha256":hashlib.sha256(b).hexdigest(),"bytes":len(b)}
old=fp(src)
assert old["sha256"]=="7968300845f67bd2fc6188e89aad49b2810daa46e86a930be649a327775905f5"
d=json.loads(src.read_text(encoding="utf-8"))
research=R/d["shared_neutral_maker_research"]
assert d["shared_neutral_maker_research_sha256"]=="f4dd2a754ab664043f1fb1c30dcd819d7e50a85d400fa516ba178ea413a37d44"
t=research.read_text(encoding="utf-8")
assert not re.search(r"(?i)(challenger|incumbent|prior champion|revised candidate|source candidate)",t)
d["shared_neutral_maker_research_sha256"]=fp(research)["sha256"]
frozen=[]
for rid,letters in d["candidate_files"].items():
 for letter,v in letters.items():
  assert fp(R/v["file"])=={"sha256":v["sha256"],"bytes":v["bytes"]}
  frozen.append({"room":rid,"letter":letter,**fp(R/v["file"])})
src.write_text(json.dumps(d,indent=2,ensure_ascii=False)+chr(10),encoding="utf-8")
out.write_text(json.dumps({"round":15,"as_of":"2026-11-06","before_source":old,"after_source":fp(src),
    "before_shared_research_SHA":"f4dd2a754ab664043f1fb1c30dcd819d7e50a85d400fa516ba178ea413a37d44",
    "after_shared_research":fp(research),"frozen_candidates_unchanged":frozen,
    "research_role_label_leak_removed":True,"critic_dispatch":False,
    "all_critic_scores":None,"weighted_scoring":None,"owner_approval":False,
    "procurement_release":False},indent=2,ensure_ascii=False)+chr(10),encoding="utf-8")
print("PASS R015 maker shared research candidate-role text cleared, submission SHA updated, four frozen candidates unchanged, no critic/scoring")
print("SOURCE_SHA",fp(src)["sha256"])
print("RESEARCH_SHA",fp(research)["sha256"])
print("FIX_SHA",fp(out)["sha256"])
