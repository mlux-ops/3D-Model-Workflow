"""Collect authentic R014 market/design/build/cost room reports without weighted scores.

Read all four frozen candidates, four original specialist seats per room, validate
individual arithmetic and source links, write one separate immutable receipt.
Run ONLY after all four original workers have reported completion.
"""
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP
import hashlib
import json
import re

R=Path(__file__).resolve().parents[1]
S=R/"state"
SOURCE=S/"ROUND014_SUBMISSION.json"
DISPATCH=S/"ROUND014_CRITIC_DISPATCH.json"
DEST=S/"ROUND014_CRITIC_COLLECTION.json"
assert not DEST.exists(), "One-time collection receipt already exists; preserve signed original"
assert not (S/"ROUND014_SCORING.json").exists(), "Formal scoring cannot predate collection"

def fingerprint(path):
    b=path.read_bytes()
    return {"sha256": hashlib.sha256(b).hexdigest(), "bytes":len(b)}

s=json.loads(SOURCE.read_text(encoding="utf-8"))
d=json.loads(DISPATCH.read_text(encoding="utf-8"))
assert fingerprint(SOURCE)["sha256"]=="946b3eda0a097961e28e76823607fd7d52b82209156e5bb59cdeb9c36450c8ed"
assert fingerprint(DISPATCH)["sha256"]=="f1d27d7e220e8581b2d039c42107595745305c95925f808850e018f4edf50270"
assert d["source_submission_sha256"]==fingerprint(SOURCE)["sha256"]
assert s["all_critic_scores"] is None and s["weighted_scoring"] is None
assert d["all_critic_scores"] is None and d["weighted_scoring"] is None
assert d["independent_reports_collected"] is False
assert s["rooms"]==d["room_ids"]==["PH-BATH3","TX-BATH3"]
seats={"market":4,"design":5,"build":5,"cost":5}
counts={"reports":0,"criteria":0,"means":0,"local_links":0,"external_links":0}
rooms={}
for rid,letters in s["candidate_files"].items():
    root=R/"rooms"/rid/"board/round-014"
    assert len(letters)==2
    for letter,c in letters.items():
        assert fingerprint(R/c["file"])=={"sha256":c["sha256"],"bytes":c["bytes"]},(rid,letter)
    room={}
    for seat,needed in seats.items():
        path=root/("critic-"+seat+".md")
        assert path.exists() and path.stat().st_size>2500,("missing authentic report",rid,seat)
        t=path.read_text(encoding="utf-8")
        assert not re.search(r"(?i)_key\.json|state/ROOMS\.json|state/LEDGER\.md|ROUND014_SCORING\.json|R16_13_ROOM_DESIGN",t),(rid,seat,"prohibited reference")
        blocks=re.split(r"(?im)^##\s+(?:Neutral\s+)?Candidate\s+([A-Z])\b[^\n]*\n",t)
        assert len(blocks)==5 and set(blocks[1::2])==set(letters),(rid,seat,"candidate headings")
        candidate_scores={}
        for letter,block in zip(blocks[1::2],blocks[2::2]):
            vals=[]
            cited=[]
            for line in block.splitlines():
                if not line.startswith("|"):
                    continue
                cells=[c.strip() for c in line.strip("|").split("|")]
                if len(cells)!=3:
                    continue
                value=re.sub(r"\s*/\s*5(?:\.0)?\s*$","",cells[1].replace("**","")).strip()
                if re.fullmatch(r"[1-5](?:\.\d+)?",value):
                    assert len(cells[2])>=30 and ("[" in cells[2] or "http" in cells[2]),(rid,letter,seat,"uncited criterion")
                    vals.append(Decimal(value))
                    cited.append(cells[0][:100])
            assert len(vals)==needed,(rid,letter,seat,"wrong criteria count",vals)
            avg=(sum(vals,Decimal(0))/Decimal(needed)).quantize(Decimal("0.1"),rounding=ROUND_HALF_UP)
            assert all(z in block.lower() for z in ("top_fix","gate_flags","confidence")),(rid,letter,seat,"missing assessment")
            assert any(str(avg) in ln for ln in block.splitlines() if "mean" in ln.lower() or "overall" in ln.lower()),(rid,letter,seat,"mean not printed",str(avg))
            assert "LEVEL" in block.upper() and ("PAN" in block.upper() or "TUB" in block.upper()),(rid,letter,seat,"level/pan")
            assert "DCOF" in block.upper() and "WALL" in block.upper() and "NICHE" in block.upper(),(rid,letter,seat,"wet surface evidence")
            candidate_scores[letter]={
                "criteria_1_to_5":[str(v) for v in vals],
                "unweighted_arithmetic_mean_1_decimal":str(avg),
                "distinct_criterion_titles":cited,
                "source_cited":True,
                "hard_gate_text_present":True
            }
            counts["criteria"]+=needed
            counts["means"]+=1
        for link in re.findall(r"\]\(([^)]+)\)",t):
            if link.startswith(("https:","http:","mailto:","#")):
                counts["external_links"]+=1
            else:
                assert (root/link.split("#")[0]).exists(),(rid,seat,"bad local evidence link",link)
                counts["local_links"]+=1
        room[seat]={
            "file":str(path.relative_to(R)).replace("\\","/"),
            "worker_id":d["worker_seats"]["critic-"+seat],
            **fingerprint(path),
            "candidate_letters":sorted(candidate_scores),
            "authentic_original_worker_report":True,
            "unweighted_criterion_audit":candidate_scores
        }
        counts["reports"]+=1
    rooms[rid]=room
assert counts["reports"]==8 and counts["criteria"]==76 and counts["means"]==16
assert all(set(rooms[r])==set(seats) for r in s["rooms"])
receipt={
    "round":14,"as_of":"2026-11-06","phase":"authentic_collection_audited_unscored",
    "source_submission_path":str(SOURCE.relative_to(R)).replace("\\","/"),
    "source_submission_sha256":fingerprint(SOURCE)["sha256"],
    "dispatch_path":str(DISPATCH.relative_to(R)).replace("\\","/"),
    "dispatch_sha256":fingerprint(DISPATCH)["sha256"],
    "original_workers":d["worker_seats"],
    "frozen_candidates_preserved":True,
    "original_critic_reports":rooms,
    "validation_counts":counts,
    "unweighted_seat_arithmetic_only":True,
    "all_critic_scores":None,
    "weighted_scoring":None,
    "private_role_mapping_not_used":True,
    "source_submission_and_dispatch_immutable":True,
    "reviewer_collection_clearance":None,
    "owner_approval":False,
    "procurement_release":False,
    "global_13_room_done":False
}
DEST.write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
print("PASS genuine R014 8 reports, 76 criteria, 16 verified means, all four original seats; NO weighted score")
print("COUNTS",json.dumps(counts))
print("COLLECTION_SHA",fingerprint(DEST)["sha256"])
