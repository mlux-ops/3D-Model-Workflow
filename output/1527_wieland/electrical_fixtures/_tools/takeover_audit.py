"""Read and hash existing row and native evidence without changing prior artifacts."""
from pathlib import Path
from collections import Counter
import json
import hashlib
import datetime
import re
import sys

sys.stdout.reconfigure(errors='replace')
ROOT = Path(__file__).resolve().parents[1]

def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    items = load(ROOT / 'ITEMS.json')['items']
    groups = load(ROOT / 'GROUPS.json')['groups']
    row_ids = [str(i['row_id']) for i in items]
    mapped = [r['row_id'] for g in groups for r in g['rows']]
    assert len(items) == 120 and len(set(row_ids)) == 120
    assert Counter(row_ids) == Counter(mapped)
    records = []
    for group in groups:
        folder = ROOT / group['canonical_item']
        vp = folder / 'validation.json'
        v = load(vp) if vp.exists() else {}
        rfap = Path(v['rfa_path']) if v.get('rfa_path') else None
        evidence = [folder / 'evidence' / n for n in v.get('evidence_files', [])]
        rec = dict(key=group['key'], rows=len(group['rows']), folder=group['canonical_item'],
                   technical_pass=v.get('technical_pass'), model=v.get('model'),
                   source_url=v.get('source_url'), inferences=v.get('inferences'),
                   search=v.get('rfa_search'), category=v.get('category'),
                   actual=v.get('measured_saved_dimensions_in'), expected=v.get('expected_dimensions_in'),
                   gates=v.get('gates'), rfa_path=str(rfap) if rfap else None,
                   rfa_sha256=sha(rfap) if rfap and rfap.exists() else None,
                   rfa_signature=rfap.read_bytes()[:8].hex() if rfap and rfap.exists() else None,
                   validation_sha256=sha(vp) if vp.exists() else None,
                   preview_count=len(evidence), missing_previews=[str(p) for p in evidence if not p.exists()],
                   source_notes=group['source_notes'])
        records.append(rec)
        print('%2d | %-40s | %-5s | %-24s | %s' % (rec['rows'], rec['key'],rec['technical_pass'],rec['model'],rec['actual']))
        if not v:
            print(' HOLD/REMAINING', json.dumps([i for i in items if i['item_key'] in {r['item_key'] for r in group['rows']}],ensure_ascii=True))
    validations=[]
    for vp in ROOT.glob('*/validation.json'):
        v=load(vp)
        validations.append(dict(folder=vp.parent.name,technical_pass=v.get('technical_pass'),model=v.get('model'),rfa=v.get('rfa_path')))
    variants=[]
    canon={g['canonical_item'] for g in groups}
    for v in validations:
        if v['folder'] not in canon:
            variants.append(v)
    summary=dict(checked_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        items_sha256=sha(ROOT/'ITEMS.json'),groups_sha256=sha(ROOT/'GROUPS.json'),
        rows=len(items),groups=len(groups),canonical_passes=sum(r['technical_pass'] is True for r in records),
        unique_validated_families=sum(v['technical_pass'] is True for v in validations),
        row_notes=sum((ROOT/i['item_key']/'NOTES.md').exists() for i in items),
        non_backup_row_root_rfas=len([p for p in ROOT.glob('*/*.rfa') if not re.search(r'\.\d{4}$',p.stem)]),
        variants=variants,records=records)
    destination=ROOT/'_review'/'takeover_audit.json'
    if destination.exists():
        destination=ROOT/'_review'/('takeover_audit_'+datetime.datetime.now().strftime('%H%M%S')+'.json')
    destination.write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print('SUMMARY',json.dumps({k:v for k,v in summary.items() if k!='records'},ensure_ascii=True))

if __name__=='__main__':
    main()
