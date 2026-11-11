"""One-time R013 cleared dispatch and new R14 owner/GC release bridge ledger."""
from pathlib import Path
import hashlib,json
root=Path(__file__).resolve().parents[1]
ledger=root/'state/LEDGER.md'
heading='## R013 independent PH blind clearance, four-seat critic dispatch and R14 all-room release bridge - 2026-11-06'
old=ledger.read_text(encoding='utf-8')
assert heading not in old
d=root/'state/ROUND013_CRITIC_DISPATCH.json'
disp=json.loads(d.read_bytes())
assert disp['independent_preflight'].startswith('CONTINUE')
assert disp['all_critic_scores'] is None
ro=root/'state/ROUND013_ROOMS_PENDING_SYNC.json'
state=json.loads(ro.read_bytes())
m=root/'deliverables/integrated-r14/MANIFEST.json'
manifest=json.loads(m.read_bytes())
assert manifest['room_count']==13 and not manifest['procurement_release'] and not manifest['owner_approval']
text='\n\n'+heading+'\n'
text+='- Existing non-Pro Reviewer **worker-11** returned explicit R013 PH FIX1 **CONTINUE, done solely for four-seat blind dispatch** after independent rehash of all six controlled SHA candidate documents, 32 source links, corrected copied niche quantities, correct PH Bath2 nominal 59.496-in wall versus Duravit 59-in total 0.496-in physical fit HOLD, PH Bath4 point not linear research scope, no maker Target treated as actual raw numerical DCOF, and corrected present-only blind descriptions. Standing Reviewer did NOT declare global 13-room DONE or owner/purchasing release. Source receipt SHA '+disp['source_submission_sha256']+' preserved unchanged.\n'
text+='- Four real independent blind critic seats now **DISPATCHED**, all four accepted messages: original sleeping worker-9 DESIGN 0.25, worker-10 BUILD/installer 0.25, worker-12 COST/procurement 0.20, plus one new independent worker-13 MARKET 0.30 because original market worker-3 was permanently finished (never revived). Assignment/clearance/frozen source SHAs in separate `state/ROUND013_CRITIC_DISPATCH.json` SHA '+hashlib.sha256(d.read_bytes()).hexdigest()+'; old original submission `all_critic_scores:null` intentionally stays frozen. Specialists restricted to each current neutral R013 candidate, owner feedback, geometry/plumbing and maker/comps; no private maps, champion/history, prior rounds, ROOMS/LEDGER or other reports. No original specialist critique or weighted scoring invented. All outcomes withheld until actual collection, then formal scoring only next genuinely distinct prime turn.\n'
text+='- `state/ROOMS.json` three PH rooms are synchronized to **last_round:13 pending blind unscored** while retaining their prior R010 scored BLOCKED evidence and still `champion_id:null`, `champion_score:null`, owner/purchase false. Separate `state/ROUND013_ROOMS_PENDING_SYNC.json` audits exact source old/new room SHA '+state['old_sha256']+' to '+state['new_sha256']+' and 10 untouched non-PH room records.\n'
text+='- Substantially extended entire **13-room** construction/owner program with additive **R14** new three-output SHA-signed release bridge in `deliverables/integrated-r14/`: 13 uniquely room-specific decision/GC evidence cards, CSV 13 exact program/physical/source/release rows and START_HERE; SHA manifest '+hashlib.sha256(m.read_bytes()).hexdigest()+'. All preserve original two-copy per-room tile-only total **$23,572.44** including original 15% source waste once; no double PH/TX WC or niche, no release. Explicit new technical issues include manufacturer-specific **RL21 1.5in hex 5/16 vs old 1/4** and 12x24 3/8 origin/separate raw wet DCOF; Brizo factory solid grate + BR73480 stainless sloped Water Protection System does not certify 1529 actual mortar/membrane/rough system; PH Bath2 nominal 0.496-in total tub fit requires actual flange/rough; PH4 35/27 SF & Soft/AntiSlip and historic 214.4-SF supplier-grand-total issue are hold not payable shortage. Two independently displayed online RL21 retailers have differing 12x24 suffix/packages and list rates, with New England-only/unavailable flags; none are current Chicago SHB installed bid or authorization. Original R12/R13 previously signed eleven output SHAs untouched.\n'
text+='- New R14 manifest read-only SHA recheck PASS three files, all 13 CSV cards, original **$23,572.44** Decimal arithmetic, all room owner/GC release flags FALSE. Live Revit identity still 1527, not certified 1529; Smartsheet strictly read-only; no emails/vendor messages, sample/purchasing/deployment changes. Whole owner/GC objective remains OPEN.\n'
ledger.write_text(old+text,encoding='utf-8')
print('PASS material R013 critic dispatch + 13-room signed R14 release bridge ledger')
