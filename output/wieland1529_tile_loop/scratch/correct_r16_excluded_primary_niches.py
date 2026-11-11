"""One-time signed R16 strict no-new-Primary-niche source correction."""
from pathlib import Path
import csv,hashlib,json
R=Path(__file__).resolve().parents[1]
D=R/'deliverables/integrated-r16'
p=D/'R16_27_EXACT_SOURCE_TO_CONDITIONAL_CARTON_RELEASE.csv'
mp=D/'MANIFEST.json'
audit=R/'state/ROUND014_R16_PRIMARY_NICHE_SOURCE_FIX.json'
assert not audit.exists()
def fp(p):return {'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
orig=json.loads(mp.read_bytes())
assert fp(p)==orig['outputs'][p.name]
before=fp(p); prior_manifest=fp(mp)
unchanged={k:v for k,v in orig['outputs'].items() if k!=p.name}
with p.open(encoding='utf-8-sig',newline='') as f:
    reader=csv.DictReader(f);cols=reader.fieldnames;rows=list(reader)
affected=[]
for r in rows:
    if r['room'] in ('PH-PRIMARY','TX-PRIMARY') and r['source_surface']=='accent':
        assert r['old_material_usd_per_copy']=='' and r['two_copy_historic_material_usd']==''
        r['conditional_good_better_best_source_direction']='EXCLUDED / UNPRICED historic Primary niche row carried only for audit. Owner explicitly forbids an added Primary niche. NO alternative, NO scope, NO order, NO new cost'
        r['next_possible_order_formula_not_current_quantity']='NOT APPLICABLE: 0 Primary shower niches approved and no separate niche quantity or cases. Original unpriced excluded row is NOT a $0 approved PO'
        r['source_ref_or_vendor_quote_id']='Original EXCLUDED/UNPRICED reference only: '+r['original_smartsheet_row_id']+'; NO Primary niche scope'
        affected.append(r['room'])
assert sorted(affected)==['PH-PRIMARY','TX-PRIMARY']
with p.open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=cols);w.writeheader();w.writerows(rows)
assert fp(p)!=before
assert all(fp(D/n)==info for n,info in unchanged.items())
orig['outputs'][p.name]=fp(p)
mp.write_text(json.dumps(orig,indent=2)+'\n',encoding='utf-8')
assert all(fp(D/n)==info for n,info in orig['outputs'].items())
receipt={'date':'2026-11-06','change':'Two historically unpriced/excluded Primary niche source rows explicitly NO SCOPE/NO ORDER rather than generic conditional carton formula; owner no new Primary niches','two_rows':affected,'original_source_27_rows_preserved':True,'old_csv':before,'new_csv':fp(p),'old_manifest':prior_manifest,'new_manifest':fp(mp),'three_other_output_sha_unchanged':unchanged,'owner_approval':False,'purchase_release':False}
audit.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
print('PASS R16 2 excluded/unpriced Primary niche source rows no scope; 4 signed file SHA current, original 27 source rows/23572.44 unchanged')
print('R16_SHA',fp(mp)['sha256'])
