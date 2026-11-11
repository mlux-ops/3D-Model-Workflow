"""Check Round003 blind packets and refresh precise SHA receipt after final neutralization."""
from pathlib import Path
import hashlib,json,re

ROOT=Path(__file__).resolve().parents[1]
expected={"TX-PRIMARY":{"A","B"},"TX-POWDER":{"B","C"},"TX-POWDER2":{"A","B"}}
receipt=json.loads((ROOT/"state/ROUND003_SUBMISSION.json").read_text(encoding="utf-8"))
rooms=json.loads((ROOT/"state/ROOMS.json").read_text(encoding="utf-8"))["rooms"]
assert len(rooms)==13
indexed={r["id"]:r for r in rooms}
for room,letters in expected.items():
    d=ROOT/"rooms"/room/"board/round-003"
    key=json.loads((d/"_key.json").read_text(encoding="utf-8"))
    assert {k for k in key if k in ("A","B","C")}==letters
    assert len([k for k in letters if "incumbent" in key[k]])==1
    files=list((d/"candidates").glob("*.md"))
    assert {p.stem for p in files}==letters
    assert indexed[room]["round_003_submission"]["scores"] is None
    assert indexed[room]["round_003_submission"]["status"]=="blind_review_pending"
    for p in files:
        data=p.read_bytes(); text=data.decode("utf-8")
        assert text.startswith("# "+room+" — Candidate "+p.stem),(room,p.name)
        assert "**Round 003 / per Triplex unit; two units.**" in text
        assert any(line.startswith("|---") and line.count("---") >= 5 for line in text.splitlines()), (room,p.name)
        low=text.lower()
        assert "incumbent" not in low and "independent challenger" not in low and "one developed challenger" not in low
        lines=[x for x in text.splitlines() if x.startswith("|")]
        assert len(lines)>3,(room,p.name)
        assert all(len(x.split("|"))==7 for x in lines),(room,p.name,[len(x.split("|")) for x in lines])
        for rel in re.findall(r"\]\(([^)]+)\)",text):
            if rel.startswith(("http","mailto:")):continue
            assert (p.parent/rel.split("#")[0]).exists(),(room,p.name,rel)
        receipt["candidates"][room][p.stem]={"bytes":len(data),"sha256":hashlib.sha256(data).hexdigest()}
        print(room,p.stem,len(data),hashlib.sha256(data).hexdigest()[:14])
(ROOT/"state/ROUND003_SUBMISSION.json").write_text(json.dumps(receipt,indent=2)+"\n",encoding="utf-8")
print("PASS Round003: six blind candidates, five-column comparable tables, no scores")
