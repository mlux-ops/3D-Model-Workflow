"""One-time R015 source-only relative-link correction BEFORE predispatch or critics.
Records old/new candidate and source SHA. Does not touch older signed rounds.
"""
from pathlib import Path
import hashlib,json,re
R=Path(__file__).resolve().parents[1]
S=R/"state";p=S/"ROUND015_SUBMISSION.json"
receipt=S/"ROUND015_PREDISPATCH_SOURCE_LINK_FIX.json"
assert not receipt.exists()
assert not (S/"ROUND015_CRITIC_DISPATCH.json").exists()
assert not (S/"ROUND015_SCORING.json").exists()
def sig(f):
 b=f.read_bytes()
 return {"sha256":hashlib.sha256(b).hexdigest(),"bytes":len(b)}
before=sig(p)
# Initial pre-dispatch author emitted literal trailing slash-n and literal
# slash-n line separators in candidate text. Fix these before ANY critic sees
# the packets, together with evidence-link depth.
d=json.loads(p.read_text(encoding="utf-8").replace(chr(92)+"n",chr(10)))
fixes=[]
for rid,letters in d["candidate_files"].items():
 for letter,rec in letters.items():
  f=R/rec["file"]
  assert sig(f)=={"sha256":rec["sha256"],"bytes":rec["bytes"]}
  t=f.read_text(encoding="utf-8")
  t=t.replace(chr(92)+"n",chr(10))
  t2=t.replace("../../geometry.json","../../../geometry.json").replace("../../plumbing.json","../../../plumbing.json")
  t2=t2.replace("../../../../research/","../../../../../research/").replace("../../../../board/","../../../../../board/").replace("../../../../state/","../../../../../state/")
  assert f.read_text(encoding="utf-8")!=t2
  original=sig(f)
  f.write_text(t2,encoding="utf-8")
  changed=sig(f)
  links=re.findall(r"\]\(([^)]+)\)",t2)
  local=[s for s in links if not s.startswith(("http:","https:","mailto:","#"))]
  assert all((f.parent/s.split("#")[0]).exists() for s in local),(rid,letter,local)
  assert len(local)>=8 and len(links)>=11
  assert len(t2.splitlines())>55,(rid,letter)
  rec.update(changed)
  fixes.append({"room":rid,"letter":letter,"before":original,"after":changed,"verified_local_links":len(local)})
d["revision"]="SAME-R015 predispatch link depth correction before any Reviewer/critic, no scores; original owner/quote remains unchanged"
p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
receipt.write_text(json.dumps({"round":15,"reason":"candidate-local evidence paths from one extra candidates/ directory","submission_before":before,"submission_after":sig(p),"fixes":fixes,"reviewer_predispatch_clearance":None,"critic_dispatch":False,"weighted_scoring":None,"owner_approved":False,"procurement_release":False},indent=2)+"\n",encoding="utf-8")
print("PASS R015 4 source-only relative link fixes, all 4x8 local evidence links resolving; SHA/bytes refrozen; no critics/reviewer/weight")
print("SUBMISSION_SHA",sig(p)["sha256"])
print("FIX_RECEIPT",sig(receipt)["sha256"])
