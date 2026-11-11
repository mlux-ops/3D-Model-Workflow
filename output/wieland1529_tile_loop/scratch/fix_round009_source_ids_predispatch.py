from pathlib import Path
import json,hashlib,re
R=Path(__file__).resolve().parents[1]
reg={x['id']:x for x in json.loads((R/'state/ROOMS.json').read_text(encoding='utf-8'))['rooms']}
receiptpath=R/'state/ROUND009_SUBMISSION.json'
receipt=json.loads(receiptpath.read_text(encoding='utf-8'))
assert receipt['all_critic_scores'] is None and receipt['phase']=='2-board'
baselines={'TX-PRIMARY':'C','TX-BATH2':'A','TX-BATH4':'B'}
fixed=0
for rid,letter in baselines.items():
 p=R/'rooms'/rid/'board/round-009/candidates'/(letter+'.md')
 original=p.read_text(encoding='utf-8');lines=original.splitlines()
 assert lines[2]=='This specification is a design option for independent evaluation; model geometry, manufacturer compliance, procurement terms and owner approval must be verified.'
 for z in reg[rid]['carried_tile_rows']:
  surface=z['surface'];rowid=z['smartsheet_row_id']
  assert rowid not in '\n'.join(lines),(rid,rowid,'already cited; no second mutation')
  matches=[i for i,line in enumerate(lines) if line.startswith('| '+surface+' |')]
  assert len(matches)==1,(rid,surface,len(matches))
  i=matches[0];lines[i]=lines[i].replace('| '+surface+' |','| '+surface+' | Smartsheet row '+rowid+':',1)
  fixed+=1
 p.write_text('\n'.join(lines)+'\n',encoding='utf-8')
 for l in receipt['candidate_files'][rid]:
  file=R/'rooms'/rid/'board/round-009/candidates'/(l+'.md')
  data=file.read_bytes()
  receipt['candidate_files'][rid][l]={'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)}
assert fixed==9
receipt['pre_dispatch_original_row_id_citation_fix']='9 original source row IDs inserted in 3 neutral source candidates; SHA/byte refreshed before any critic dispatched'
receiptpath.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
print('PASS 9 exact source row IDs inserted, all six SHA receipts refreshed pre-dispatch; no scoring or role mapping changed')
