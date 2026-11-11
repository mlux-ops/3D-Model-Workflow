"""Remove historical decision disclosures from PH Round004 challenger copies only."""
from pathlib import Path
import json,hashlib,re
R=Path(__file__).resolve().parents[1]
mapping={"PH-PRIMARY":"A","PH-BATH2":"B","PH-BATH3":"C","PH-BATH4":"B"}
replacements={
 "PH-PRIMARY":{
 "The v4 schedule names Bone Soft 24×48 walls/ceiling, Bone Reed dimensional accent and Bone Anti-Slip 24×48 entire floor;":"Source tile documents name Bone Soft 24×48 walls/ceiling, Bone Reed relief and a 24×48 Anti-Slip entire-floor treatment;",
 },
 "PH-BATH2":{
 "Replace the 2×20 Tones Sapphire shower surround, whose exact individual wet listing remains unresolved in this review, with":"The wet-wall composition uses",
 },
 "PH-BATH3":{
 "Round001 preferred Tones Sandstone rather than Opal but could not accept the undocumented Cortar Bone Soft floor DCOF or overlapping niche allowances. Substitute":"The proposed wet-wall palette uses",
 "across the wet tub wall and existing same-color niche.":"across the wet tub wall and existing same-color niche.",
 },
 "PH-BATH4":{
 "Round001 rejected Bone Ribbed relief and Clara Caviar shower niche for lacking Wet Areas listing and could not validate 12×24 floor pitch to the selected square point drain. Substitute":"This composition uses",
 "for the wall/niche. Retain the dark floor identity via":"for the wall/niche. It maintains a dark floor identity via",
 }
}
rec=R/"state/ROUND004_SUBMISSION.json"
d=json.loads(rec.read_text(encoding="utf-8"))
for room,letter in mapping.items():
 p=R/"rooms"/room/"board/round-004/candidates"/(letter+".md")
 txt=p.read_text(encoding="utf-8")
 for old,new in replacements[room].items():
  assert old in txt,(room,old)
  txt=txt.replace(old,new)
 lines=txt.splitlines()
 lines[0]="# "+room+" — Candidate "+letter+" — "+re.sub(r"(?i)round\s*004\s*candidate\s*[ABC][: ]*", "", lines[0].split(":",1)[-1] if ":" in lines[0] else lines[0].split("—",2)[-1]).strip()
 assert not any(word in txt.lower() for word in ["actual challenger","incumbent","round001 preferred","round001 rejected"])
 txt="\n".join(lines)+"\n"
 p.write_text(txt,encoding="utf-8")
 d["candidate_files"][room][letter]={"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"bytes":len(p.read_bytes())}
 print(room,letter,len(p.read_bytes()))
rec.write_text(json.dumps(d,indent=2)+"\n",encoding="utf-8")
