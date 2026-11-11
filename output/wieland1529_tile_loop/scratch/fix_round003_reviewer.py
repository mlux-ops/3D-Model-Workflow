"""Apply exact Round003 independent Reviewer FIX without changing source quantities."""
from pathlib import Path

R=Path(__file__).resolve().parents[1]
prefix="rooms"
shared="**Round 003 / per Triplex unit; two units.** This specification is a design option for independent evaluation; model geometry, manufacturer compliance, procurement terms and owner approval must be verified."
for room,letters in (("TX-PRIMARY","AB"),("TX-POWDER","BC"),("TX-POWDER2","AB")):
 for letter in letters:
  path=R/prefix/room/"board/round-003/candidates"/(letter+".md")
  body=path.read_text(encoding="utf-8")
  lines=body.splitlines()
  assert lines[2].startswith("**Round 003 / per Triplex unit; two units.**"),(room,letter)
  lines[2]=shared
  body="\n".join(lines)+"\n"
  if room=="TX-POWDER" and letter=="B":
   assert "actual challenger" in body
   body=body.replace("actual challenger","composition under review")
  if room=="TX-PRIMARY" and letter=="A":
   old="point/linear drain type, pan slope/geometry, tile division and actual format compatibility **unverified**"
   new="selected 48-in Brizo linear drain; exact installed location, orientation, pan slope, tile division and format compatibility **unverified**"
   assert old in body
   body=body.replace(old,new)
  if room=="TX-PRIMARY" and letter=="B":
   old="Original floor row **784184264687492** carries **116.1 SF/unit** blended from **87.64 SF Soft at $8.14 = $713.39** plus **28.46 SF Anti-Slip at $6.75 = $192.11**."
   new=("Original floor row **784184264687492** carries **116.1 SF/unit at blended $7.80/SF = $905.58/unit**. "
        "An **unverified illustrative component allocation** of 87.64 SF Soft at $8.14/SF and 28.46 SF Anti-Slip at $6.75/SF yields "
        "**$905.4946 before rounding**, or **$905.50 after rounding each component** ($713.39 + $192.11). "
        "The $0.08 discrepancy does not establish separately confirmed product prices or a revised supplier quotation.")
   assert old in body
   body=body.replace(old,new)
  assert "actual challenger" not in body.lower() and "incumbent" not in body.lower()
  path.write_text(body,encoding="utf-8")
  print(room,letter,"FIX PASS")
