import json,hashlib,datetime
from pathlib import Path
root=Path(__file__).resolve().parents[1]
initial=json.loads((root/'native_final_review.json').read_text())
patch=json.loads((root/'native_final_review_patch.json').read_text())
assert initial['all_pass'] and patch['all_pass'], 'Native review requires correction'
updates={r['name']:r for r in patch['files']}
rows=[updates.get(r['name'],r) for r in initial['files']]
assert len(rows)==14 and len({r['name'] for r in rows})==14
for row in rows:
    assert row['pass'] and all(row['gates'].values()), row['name']
    assert hashlib.sha256(Path(row['rfa']).read_bytes()).hexdigest()==row['sha256'], row['name']+' changed after review'
report={'all_pass':True,'coverage':initial['coverage'],'files':rows,'source_reviews':['native_final_review.json','native_final_review_patch.json'],'verified_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'method':'Original independent review for unchanged files; targeted new native review replaces F01 and F10 records. Every current RFA hash verified.'}
(root/'release_native_validation.json').write_text(json.dumps(report,indent=2))
print('CURRENT_RFA_NATIVE_REVIEW_PASS 14/14')