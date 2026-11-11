"""Derive date/round-scoped read-only PDF and image QA from tested R034 QA."""
from pathlib import Path

root=Path(__file__).resolve().parent
for name in ('verify_split_owner_pdf','visual_qa','verify_owner_illustrations'):
    source=(root/('r034_'+name+'.py')).read_text(encoding='utf-8')
    source=source.replace('r034','r035').replace('R034','R035')
    source=source.replace('r033-13-owner-review-PROVISIONAL','r035-13-owner-review-PROVISIONAL')
    target=root/('r035_owner_'+name+'.py' if name=='visual_qa' else 'r035_'+name+'.py')
    if target.exists():
        print('PRESERVE',target.name)
        continue
    target.write_text(source,encoding='utf-8')
    print(target.name)
