"""One-time immutable 12 genuine R013 critique SHA collection, distinct-turn scores remain NULL."""
from pathlib import Path
import json,hashlib,subprocess,sys,re

ROOT=Path(__file__).resolve().parents[1]
COL=ROOT/'state/ROUND013_CRITIC_COLLECTION.json'
assert not COL.exists(), 'Original critic collection receipt must not be regenerated'
assert not (ROOT/'state/ROUND013_SCORING.json').exists(), 'Score only in distinct later turn'

result=subprocess.run([sys.executable,str(ROOT/'scratch/verify_round013_critic_collection_no_scoring.py')],cwd=ROOT,text=True,capture_output=True)
assert result.returncode==0,result.stdout+'\n'+result.stderr
assert '114 independently recomputed criterion values/ 24 arithmetic means' in result.stdout
assert '12 own-seat reports' in result.stdout

def fp(p):
 b=p.read_bytes();return {'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}

sub=ROOT/'state/ROUND013_SUBMISSION.json'
dis=ROOT/'state/ROUND013_CRITIC_DISPATCH.json'
src=json.loads(sub.read_bytes());dist=json.loads(dis.read_bytes())
assert dist['source_submission_sha256']==fp(sub)['sha256']
assert dist['scoring_deferred_to_next_distinct_prime_turn'] and src['all_critic_scores'] is None
assert not src['owner_approval'] and not src['procurement_release']
files={};local=0
for rid,options in src['candidate_files'].items():
 files[rid]={}
 for seat,worker in dist['critic_worker_seats'].items():
  p=ROOT/f'rooms/{rid}/board/round-013/{seat}.md'
  assert p.exists(),(rid,seat)
  t=p.read_text(encoding='utf-8')
  for link in re.findall(r'\]\(([^)]+)\)',t):
   if link.startswith(('http://','https://','#','mailto:')):continue
   assert (p.parent/link.split('#')[0]).resolve().is_file(),(rid,seat,link)
   local+=1
  files[rid][seat]={**fp(p),'worker_id':worker,'candidate_letters':sorted(options)}
 assert len(files[rid])==4

receipt={
 'round':13,'phase':'2-board','as_of':'2026-11-06',
 'source_submission_sha256':fp(sub)['sha256'],
 'dispatch_receipt_sha256':fp(dis)['sha256'],
 'reviewer_cleared_pre_dispatch':'worker-11 CONTINUE (FIX1 source-specific same-round rereview)',
 'critic_worker_seats':dist['critic_worker_seats'],
 'report_files':files,
 'original_source_candidates_preserved':src['candidate_files'],
 'total_critic_files':12,
 'distinct_seats':4,
 'local_links':local,
 'individual_criteria':114,
 'independent_unweighted_arithmetic_means':24,
 'all_critic_scores':None,
 'weighted_scoring':None,
 'owner_approved':False,
 'procurement_release':False,
 'next_action':'Perform private candidate role mapping and weighted calculations ONLY in genuinely subsequent distinct prime turn; hard gates always prevail',
}
COL.write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print('PASS R013 immutable collection: 12 authentic files, 4 separate workers, 114 independent criteria, 24 arithmetic means,',local,'resolved links, scores NULL, receipt SHA',fp(COL)['sha256'])
