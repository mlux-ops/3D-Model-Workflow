"""Append-only R026 scored and R027 prepared/frozen actual room history entries."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
R026="state/ROUND026_INDEPENDENT_POSTSCORE_REVIEWER35_CLEARANCE.json"
R027="state/ROUND027_PREDISPATCH_FIX2_ROOM_ONLY_RESEARCH_REFREEZE.json"
CARDS="state/ROUND027_13_PROVISIONAL_OWNER_PREVIEWS_SIGNED.json"
def add(room,tag,body):
 p=ROOT/"rooms"/room/"history.md"
 s=p.read_text(encoding="utf-8")
 if tag in s:raise ValueError("Already appended "+tag)
 with p.open("a",encoding="utf-8",newline="\n") as f:
  f.write(("\n" if s.endswith("\n") else "\n\n")+"## "+tag+"\n"+body+"\n")
def main():
 for p in (R026,R027,CARDS):
  if not (ROOT/p).is_file():raise FileNotFoundError(p)
 r=json.loads((ROOT/R026).read_text(encoding="utf-8"))
 if r["authentic_verdict"]!="CONTINUE FOR R026 NONACCEPTANCE SCORING ONLY":
  raise RuntimeError("Independent R026 receipt not cleared")
 f=json.loads((ROOT/R027).read_text(encoding="utf-8"))
 if f["independent_post_FIX_reviewer"] is not None or f["critic_dispatch"] is not None:
  raise RuntimeError("R027 predispatch status changed")
 add("TX-PRIMARY","R026 authentic four-seat scored, Reviewer35 NONACCEPTANCE — 2026-11-07",
     "- MARKET31/DESIGN32/BUILD33/COST34 original critiques: A 3.62 (COST2.6), B 3.55 (COST2.8), both below individual specialist 3.0. Signed formal scoring and independent Reviewer35 verdict in "+R026+".\n- Brizo BNX 48in LINEAR+BR73480/solid grate/no niche, inherited TX-WC once. Native shower ceiling, cuts/drain position, full delivered price, Chicago exact lot/ETA UNKNOWN. No champion or owner approval.")
 add("TX-BATH3","R026 authentic four-seat scored, Reviewer35 NONACCEPTANCE — 2026-11-07",
     "- MARKET31/DESIGN32/BUILD33/COST34 original critiques: A3.11 COST1.8 FAIL, B3.70 COST3.0 specialist PASS, but owner TUB/WALK-IN, native floor/niche/POINT drain cuts, Chicago dye lot and total delivered budget UNKNOWN. Independent Reviewer35 confirmed score/nonacceptance only in "+R026+".\n- Brizo BNX POINT/PAN only if owner chooses WALK-IN; if tub, no tiled PAN and no invented basin decision. No incumbent, owner approval or champion.")
 for room in ("PH-BATH2","TX-BATH2","TX-BATH4"):
  add(room,"R027 wet-tub tile-only new source, independent PRECISE FIX corrected — 2026-11-07",
      "- Two materially differentiated permitted-vendor R027 tub tile schemes now source-prepared and formally neutral-frozen, no tiled PAN. Exact Elm wet WALL/NICHE, published floor product wet DCOF >=0.42, MSI and unqualified Porcelanosa comparisons, same-job trade vs non-Chicago retail correctly separated.\n- Reviewer38 PRECISE FIX found former shared research leaking R024 outcomes; controlled room-only research and six source reference SHA corrections in "+R027+". Independent post-FIX Reviewer39 PENDING at this entry, NOT DISPATCHED, NO scores or approved champion. Original floor/niche/wall gross 15% waste once; Chicago lot, full delivery, actual tub opening/niche and focal cuts UNKNOWN.")
 print("R026 2 room scored histories and R027 3 tub source histories appended, owner cards signed",CARDS)
if __name__=="__main__":main()
