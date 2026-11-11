"""Finalize blind Round003 identities and state only when all three B challengers exist.

DO NOT score Round003 here: following turn consumes four independent critiques.
"""
from pathlib import Path
import hashlib
import json
import re

ROOT=Path(__file__).resolve().parents[1]
focus=("TX-PRIMARY","TX-POWDER","TX-POWDER2")
folders={r:ROOT/"rooms"/r/"board/round-003" for r in focus}
for r,d in folders.items():
    assert (d/"candidates/B.md").exists(),f"Challenger B not yet supplied: {r}"
    assert len(list((d/"candidates").glob("*.md")))==2,r
# Reletter Powder2 so the private roles are not uniformly A/C incumbents.
d=folders["TX-POWDER2"]/"candidates"
assert {x.stem for x in d.glob("*.md")}=={"B","C"} and not (d/"A.md").exists()
(d/"C.md").rename(d/"incumbent_pre_swap.md")
(d/"B.md").rename(d/"A.md")
(d/"incumbent_pre_swap.md").rename(d/"B.md")
maps={"TX-PRIMARY":{"A":"incumbent historical v4","B":"revised candidate"},
      "TX-POWDER":{"C":"incumbent historical v4","B":"revised candidate"},
      "TX-POWDER2":{"B":"incumbent historical v4","A":"revised candidate"}}
receipt={"as_of":"2026-11-06","round":3,"phase":"2-board",
         "all_critic_scores":None,"candidates":{}}
for room,mapping in maps.items():
    d=folders[room]
    assert set(x.stem for x in (d/"candidates").glob("*.md"))==set(mapping)
    record={}
    for letter in mapping:
        path=d/"candidates"/(letter+".md")
        body=path.read_text(encoding="utf-8")
        first=body.splitlines()[0]
        first=re.sub(r"(?i)candidate\s+[ABC]", "Candidate "+letter, first, count=1)
        assert "Candidate "+letter in first,(room,letter,first)
        body=first+"\n"+"\n".join(body.splitlines()[1:])+"\n"
        body=body.replace("independent challenger","design option").replace("v4 source scheme","tile specification")
        path.write_text(body,encoding="utf-8")
        assert "Round 003" in body and "|---" in body,(room,letter)
        assert "incumbent" not in body.lower() and "independent challenger" not in body.lower(),(room,letter)
        record[letter]={"bytes":len(path.read_bytes()),"sha256":hashlib.sha256(path.read_bytes()).hexdigest()}
    k={"round":3,"room_id":room,"blind_review":True,"not_for_critics":True,**mapping}
    (d/"_key.json").write_text(json.dumps(k,indent=2)+"\n",encoding="utf-8")
    receipt["candidates"][room]=record
state_path=ROOT/"state/ROOMS.json"
state=json.loads(state_path.read_text(encoding="utf-8"))
for r in state["rooms"]:
    if r["id"] not in focus:continue
    assert r["status"]=="seeded" and r["last_round"]==0 and r["champion_score"] is None,r["id"]
    r["status"]="active"
    r["last_round"]=3
    r["round_003_submission"]={
        "status":"blind_review_pending","candidate_count":2,
        "critics_required":["critic-market","critic-design","critic-build","critic-cost"],
        "scores":None,"owner_approved":False,"geometry_verified":False,
        "owner_source_preserved":True}
state_path.write_text(json.dumps(state,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
(ROOT/"state/ROUND003_SUBMISSION.json").write_text(json.dumps(receipt,indent=2)+"\n",encoding="utf-8")
print("ROUND003 SUBMISSION PASS; scored=False; candidate fingerprints saved")
for room in focus:print(room,{k:len(v) for k,v in receipt["candidates"][room].items()})
