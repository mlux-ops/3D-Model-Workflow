"""Narrow R14 signed-product-source correction requested by independent Reviewer."""
from pathlib import Path
import hashlib,json,csv,io
R=Path(__file__).resolve().parents[1]
D=R/'deliverables/integrated-r14'
M=D/'MANIFEST.json'
audit=R/'state/ROUND013_R14_REVIEWER_SOURCE_IDENTITY_FIX.json'
assert not audit.exists()
before=json.loads(M.read_bytes())
old='revised Emser RL floor'
new='revised Emser Capisco Trosa F08CAPITR1224M LEVEL floor'
def fp(path):
 b=path.read_bytes();return {'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
manifest_before=fp(M)
assert len(before['outputs'])==3 and not before['owner_approval'] and not before['procurement_release']
paths=[D/'R14_OWNER_13_ROOM_EXACT_RELEASE_DECISIONS.md',D/'R14_13_ROOM_EXACT_SOURCE_AND_OWNER_GC_RELEASE_BRIDGE.csv']
third=D/'START_HERE_R14.md'
unchanged_third=fp(third)
assert unchanged_third==before['outputs'][third.name]
plans={}
old_new={}
for p in paths:
 b=p.read_bytes()
 assert fp(p)==before['outputs'][p.name]
 assert b.count(old.encode())==1,(p,b.count(old.encode()))
 n=b.replace(old.encode(),new.encode())
 assert n!=b and n.count(new.encode())==1
 plans[p]=n
for p,b in plans.items():
 old_new[p.name]={'before':fp(p)}
 p.write_bytes(b)
 old_new[p.name]['after']=fp(p)
 before['outputs'][p.name]=fp(p)

# CSV exact room-specific source and closed release checks remain invariant.
with paths[1].open('r',encoding='utf-8-sig',newline='') as f:
 rows=list(csv.DictReader(f))
assert len(rows)==13
assert 'revised Emser Capisco Trosa F08CAPITR1224M LEVEL floor' in next(x['source_specific_open_releases'] for x in rows if x['room']=='TX-BATH4')
assert all(x['owner_approval']=='FALSE' and x['gc_procurement_release']=='FALSE' for x in rows)
assert fp(third)==unchanged_third
M.write_text(json.dumps(before,indent=2)+'\n',encoding='utf-8')
assert all(fp(D/n)==f for n,f in before['outputs'].items())
data={'as_of':'2026-11-06','reviewer':'worker-11','exact_fix':'R14 TX-BATH4 revised Emser manufacturer SKU and LEVEL identity, not Daltile RL21; unchanged original Cortar Bone Soft, Soho Ivory/Caviar wet gate and tub program','output_before_after':old_new,'third_file_unchanged':{third.name:unchanged_third},'manifest_before':manifest_before,'manifest_after':fp(M),'original_r013_candidate_and_critic_files_unchanged':True,'scored_round012_unchanged':True,'all_critic_scores':None,'owner_approval':False,'procurement_release':False}
audit.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
print('PASS narrow R14 Emser source FIX, two outputs and signed manifest updated; START_HERE unchanged; no other scoring or source edits')
print('R14 manifest new SHA',fp(M)['sha256'])
