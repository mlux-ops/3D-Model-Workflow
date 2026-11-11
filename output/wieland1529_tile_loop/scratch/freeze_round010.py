from pathlib import Path
import json,hashlib,re
R=Path(__file__).resolve().parents[1]
mapping={"PH-PRIMARY":{"C":"historic v4 source","A":"revised design option"},
"PH-BATH2":{"A":"historic v4 source","C":"revised design option"},
"PH-BATH4":{"C":"historic v4 source","B":"revised design option"}}
intro="This specification is a design option for independent evaluation; model geometry, manufacturer compliance, procurement terms and owner approval must be verified."
rp=R/"state/ROUND010_SUBMISSION.json"
assert not rp.exists(),"Round010 frozen receipt already exists, do not overwrite."
regpath=R/"state/ROOMS.json";reg=json.loads(regpath.read_text(encoding="utf-8"))
assert len(reg["rooms"])==13
out={"as_of":"2026-11-06","round":10,"phase":"2-board","all_critic_scores":None,
"candidate_files":{},"critic_seats":["critic-market","critic-design","critic-build","critic-cost"],
"owner_approval":None,"native_1529_confirmed":False,"release_allowed":False,
"prior_round004_round009_frozen_unchanged":True}
for rid,roles in mapping.items():
 d=R/"rooms"/rid/"board/round-010"
 assert not (d/"_key.json").exists(),rid
 paths=sorted((d/"candidates").glob("*.md"))
 assert {p.stem for p in paths}==set(roles),(rid,paths)
 room=next(z for z in reg["rooms"] if z["id"]==rid)
 assert room["status"]=="blocked" and room["champion_id"] is None and room["owner_status"] is None
 sizes=[]
 out["candidate_files"][rid]={}
 for p in paths:
  b=p.read_bytes();t=b.decode("utf-8");lines=t.splitlines();sizes.append(len(b))
  assert len(b)>6500,(p,len(b))
  assert lines[0]=="# "+rid+" — Candidate "+p.stem+" — complete tile design option" and lines[1]=="" and lines[2]==intro,(p,lines[:4])
  assert not re.search(r"(?i)\bincumbent\b|\bchallenger\b|\bchampion\b|round[- ]?00[1-9]\b|_key\.json|state/ROOMS\.json|state/LEDGER\.md|\bsteam\b",t),p
  assert t.count("|")>=35 and "DCOF" in t and "15%" in t and "null" in t.lower(),p
  five=sum(len([x.strip() for x in line.strip("|").split("|")])==5 for line in lines if line.startswith("|"))
  assert five>=5,(p,five)
  for row in room["carried_tile_rows"]:
   assert row["smartsheet_row_id"] in t,(rid,p.stem,row["smartsheet_row_id"])
  for link in re.findall(r"\]\(([^)]+)\)",t):
   if link.startswith(("http://","https://","#","mailto:")):continue
   assert (p.parent/link.split("#")[0]).exists(),(p,link)
  out["candidate_files"][rid][p.stem]={"sha256":hashlib.sha256(b).hexdigest(),"bytes":len(b)}
 assert max(sizes)/min(sizes)<2,(rid,"blind packet depth difference",sizes)
for rid,roles in mapping.items():
 d=R/"rooms"/rid/"board/round-010";(d/"_key.json").write_text(json.dumps(roles,indent=2)+"\n",encoding="utf-8")
 room=next(z for z in reg["rooms"] if z["id"]==rid)
 room["last_round"]=10
 room["round_010_submission"]={"status":"blind_review_pending","scores":None,"candidate_count":2,"critics_required":out["critic_seats"],"owner_approved":False,"release_allowed":False,"frozen_source":"state/ROUND010_SUBMISSION.json","prior_scoring_preserved":True}
 hist=R/"rooms"/rid/"history.md"
 old=hist.read_text(encoding="utf-8")
 if "Round010 blind submission" not in old:
  old+="\n- 2026-11-06 Round010 blind submission: two neutral maker-sourced tile options frozen, independent four seats pending, scores null; prior Round004 blocked verdict preserved, owner approval null and purchasing held. Role mapping private; source hashes state/ROUND010_SUBMISSION.json.\n"
  hist.write_text(old,encoding="utf-8")
rp.write_text(json.dumps(out,indent=2)+"\n",encoding="utf-8")
regpath.write_text(json.dumps(reg,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
print("PASS R010 6 neutral SHA/bytes frozen, 3 private mappings, 3 historical PH block statuses retained, original scores NULL")
for rid,cs in out["candidate_files"].items():
 print(rid,[(k,v["sha256"][:12],v["bytes"]) for k,v in cs.items()])
