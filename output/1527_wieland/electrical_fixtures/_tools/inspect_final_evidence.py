"""Compact final model, source and variant evidence index."""
from pathlib import Path
import json
import sys
sys.stdout.reconfigure(errors='replace')
ROOT=Path(__file__).resolve().parents[1]

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))

def main():
    groups=load(ROOT/'GROUPS.json')['groups']
    items=load(ROOT/'ITEMS.json')['items']
    jobs=[]
    for p in ROOT.glob('*JOBS.json'):
        entries=load(p)
        if isinstance(entries,list):jobs.extend(entries)
    rows=[]
    for g in groups+[dict(key='KZC1009570_CH',canonical_item='K1-1__8353463272013700',rows=[{}],source_notes=[])]:
        folder=ROOT/g['canonical_item'];vp=folder/'validation.json'
        if not vp.exists():continue
        v=load(vp)
        row={k:v.get(k) for k in ['manufacturer','model','source_url','rfa_search','source_rfa','source_rfa_sha256','source_file_unchanged','inferences','limitations','parameter_scope','category','component_checks','radial_checks','expected_dimensions_in','measured_saved_dimensions_in','dimensional_error_mm','technical_pass','needs_user']}
        row.update(key=g['key'],folder=folder.name,rows=len(g['rows']),source_notes=g['source_notes'])
        row['source_receipts']=[str(p.relative_to(ROOT)) for p in (folder/'source').rglob('*.acquisition.json')]
        row['source_definitions']=[str(p.relative_to(ROOT)) for p in (folder/'source').glob('*definition.json')]
        row['jobs']=[j for j in jobs if Path(j.get('out','')).name==folder.name]
        row['row_differences']=[{k:i.get(k) for k in ['row_id','item_key','description','model_number','finish','agent_ignore','source_notes']} for i in items if i['item_key'] in {r.get('item_key') for r in g['rows']}]
        rows.append(row)
        print('\n'+g['key']+' | '+str(row['category'])+' | '+str(row['technical_pass']))
        print('SOURCE '+str(row['source_url']))
        print('SEARCH '+str(row['rfa_search']))
        print('LIMIT '+str(row['limitations'] or row['inferences']))
        if g['source_notes']:print('ROW NOTES '+json.dumps(g['source_notes'],ensure_ascii=True))
    (ROOT/'_review'/'family_evidence_index.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
    print('\nIndexed',len(rows),'families; ignored rows retained:',sum(bool(i.get('agent_ignore')) for i in items))

if __name__=='__main__':main()
