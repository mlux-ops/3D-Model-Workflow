"""Reconcile PH R004 packets; neutralize blind text, freeze hashes, no scoring."""
from pathlib import Path
import hashlib
import json
import re

R=Path(__file__).resolve().parents[1]
mapping={
 "PH-PRIMARY":{"C":"historic v4 source","A":"revised design option"},
 "PH-BATH2":{"A":"historic v4 source","B":"revised design option"},
 "PH-BATH3":{"B":"historic v4 source","C":"revised design option"},
 "PH-BATH4":{"A":"historic v4 source","B":"revised design option"},
}
neutral="**Round 004 / per Penthouse unit; two units.** This specification is a design option for independent evaluation; model geometry, manufacturer compliance, procurement terms and owner approval must be verified."
statepath=R/"state/ROOMS.json"
state=json.loads(statepath.read_text(encoding="utf-8"))
byid={room["id"]:room for room in state["rooms"]}
fingerprints={}
for room,m in mapping.items():
 folder=R/"rooms"/room/"board/round-004"
 paths=sorted((folder/"candidates").glob("*.md"))
 assert {f.stem for f in paths}==set(m),(room,"unexpected candidate set")
 assert len(paths)==2
 fingerprints[room]={}
 for file in paths:
  lines=file.read_text(encoding="utf-8").splitlines()
  assert lines and lines[0].startswith("# ")
  if re.search(r"(?i)candidate\s+[ABC]",lines[0]):
   lines[0]=re.sub(r"(?i)candidate\s+[ABC]", "Candidate "+file.stem,lines[0],count=1)
  else:
   lines[0]="# "+room+" — Candidate "+file.stem+" — "+lines[0].lstrip("# ").replace(room,"").strip()
  assert "Candidate "+file.stem in lines[0]
  content="\n".join(lines)+"\n"
  # Remove explicit role identifiers while preserving historical source differences.
  content=content.replace("One complete challenger for each of two PH units.","This option is considered for each of two PH units.")
  content=content.replace("one full challenger for the existing","one complete specification for the existing")
  content=content.replace("A proposed complete material specification for board criticism, **not an approved substitution**.","A complete material specification for board criticism, **not an approved substitution**.")
  content=content.replace("one full challenger","one complete specification")
  content=content.replace("This candidate uses a new","This scheme uses a")
  content=content.replace("This candidate","This scheme")
  # Common neutral preface for eight packets. Strip existing first prose paragraph,
  # but retain its full substantive material description as the next paragraph.
  lines=content.splitlines()
  assert lines[0].startswith("# ")
  i=1
  while i<len(lines) and not lines[i].strip(): i+=1
  if i<len(lines) and lines[i].startswith("**Round 004 / per Penthouse"):
   lines[i]=neutral
  else:
   lines.insert(1,"")
   lines.insert(2,neutral)
  content="\n".join(lines)+"\n"
  assert "actual challenger" not in content.lower()
  assert "incumbent" not in content.lower()
  assert "v4 champion" not in content.lower()
  assert "Round 004 / per Penthouse unit" in content
  for link in re.findall(r"\]\(([^)]+)\)",content):
   if link.startswith(("https://","http://","mailto:")): continue
   resolved=(file.parent/link.split("#")[0]).resolve()
   assert resolved.exists(),(room,file.name,"broken research link",link)
  file.write_text(content,encoding="utf-8")
  data=file.read_bytes()
  assert len(data)>2500,(room,file.name)
  table=[line for line in content.splitlines() if line.startswith("|")]
  tableheader=next(i for i,line in enumerate(table) if "Surface" in line or "surface" in line)
  cols=[len(line.split("|")) for line in table[tableheader:]]
  assert all(n==7 for n in cols),(room,file.name,cols)
  assert len(table)>=5
  fingerprints[room][file.stem]={"sha256":hashlib.sha256(data).hexdigest(),"bytes":len(data)}
 (folder/"_key.json").write_text(json.dumps({"round":4,"room_id":room,"blind_review":True,"not_for_critics":True,**m},indent=2)+"\n",encoding="utf-8")
 r=byid[room]
 assert r["last_round"] in (0,1) and r["owner_status"] is None
 r["status_before_round004"]=r["status"]
 r["status"]="active"
 r["last_round"]=4
 r["round_004_submission"]={"status":"blind_review_pending","candidate_count":2,
  "critics_required":["critic-market","critic-design","critic-build","critic-cost"],
  "scores":None,"owner_approved":False,"source_geometry_verified":False,
  "previous_decisions_preserved":True}
 print(room,[(k,v["bytes"],v["sha256"][:12]) for k,v in fingerprints[room].items()])
statepath.write_text(json.dumps(state,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
(R/"state/ROUND004_SUBMISSION.json").write_text(json.dumps({"as_of":"2026-11-06","round":4,"phase":"2-board","all_critic_scores":None,
 "candidate_files":fingerprints,"owner_feedback_checked":True,"independent_review":"pending"},
 indent=2)+"\n",encoding="utf-8")
print("PASS Round004 8 source-linked, five-column candidates; 4 rooms, score NULL")
