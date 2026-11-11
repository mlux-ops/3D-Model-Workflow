"""Neutralize Round003 candidate role disclosures and match parallel table structure."""
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec={
"TX-PRIMARY":{"header":"all-flat Clay walls / Cream field and mosaic pan",
  "gate":["Flat Clay Wet Areas listed, exact wet-wall detailing pending",
          "Flat Clay Wet Areas listed, no wet relief product",
          "Shower ceiling product listed wet; overhead substrate assembly pending",
          "PF07 exact measured wet DCOF **null; FAIL** for level floor",
          "PF07 2×2 exact measured wet DCOF **null; FAIL** for sloped pan",
          "No primary niche scope; do not add unpriced tile"]},
"TX-POWDER":{"header":"Camel/Wheat controlled two-color dry feature",
  "gate":["Manufacturer Walls listing supports dry feature; floor DCOF not applicable",
          "Dry feature wall only; quantity split and sample hold",
          "Wood floor: no tile wet-DCOF gate"]},
"TX-POWDER2":{"header":"Indigo relief with coordinated flush mounting area",
  "gate":["Manufacturer Walls listing supports dry feature; no floor wet DCOF",
          "Flat mounting zone material/price **null**, needs basin and elevation",
          "Wood floor: no tile wet-DCOF gate"]},
}
for room, data in spec.items():
 path=ROOT/"rooms"/room/"board/round-003/candidates/B.md"
 t=path.read_text(encoding="utf-8").splitlines()
 t[0]="# "+room+" — Candidate B — "+data["header"]
 t[2]=t[2].replace("One refined challenger, per TX unit (2 units).","This is a dry vanity-wall design option for two Triplex units, per-unit quantities below.")
 t[2]=t[2].replace("One developed challenger, per TX unit (two units).","This is a dry vanity-wall design option for two Triplex units, per-unit quantities below.")
 t[2]=t[2].replace("Preserve the original warm Clay/Brizo Black Onyx palette while removing the unapproved Cortar Clay Ribbed from wet surfaces.", "This scheme specifies warm Clay with Brizo Black Onyx and no Cortar Clay Ribbed in wet surfaces.")
 t[2]=t[2].replace("Substitute **manufacturer Wet Areas-listed flat ELM Cortar Clay 24×48 Soft**", "Specify **manufacturer Wet Areas-listed flat ELM Cortar Clay 24×48 Soft**")
 t[2]=t[2].replace("Replace the carried level-floor 24×48 Soft and 12×24 Anti-Slip pan with proposed", "On the bathroom level floor and shower pan use")
 t.insert(2,"")
 t.insert(2,"**Round 003 / per Triplex unit; two units.** Source-backed design option for blind specialist review; not an owner approval, model change or procurement instruction.")
 # Table row and divider counts are derived from actual source; preserve all factual cells.
 start=next(i for i,x in enumerate(t) if x.startswith("| Surface |"))
 divider=start+1
 assert t[divider].startswith("|---")
 end=divider+1
 while end<len(t) and t[end].startswith("|"):
  end+=1
 assert end-(divider+1)==len(data["gate"]),(room,end-(divider+1))
 t[start]=t[start]+" Evidence / hard gate |"
 t[divider]=t[divider]+"---|"
 for i,gate in enumerate(data["gate"],divider+1):
  t[i]=t[i]+" "+gate+" |"
 body="\n".join(t)+"\n"
 assert "independent challenger" not in body.lower()
 assert body.count("|---")>=1
 path.write_text(body,encoding="utf-8")
 print(room,len(path.read_bytes()),"table rows",len(data["gate"]))
