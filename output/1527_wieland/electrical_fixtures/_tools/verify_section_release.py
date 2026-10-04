"""Independently check the final on-disk electrical delivery and all row coverage."""
from pathlib import Path
from collections import Counter
from functools import lru_cache
import datetime
import hashlib
import json
import re
import sys

ROOT=Path(__file__).resolve().parents[1]

def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

@lru_cache(maxsize=None)
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    inventory=load(ROOT/'ITEMS.json')['items']
    groups=load(ROOT/'GROUPS.json')['groups']
    before=load(ROOT/'_review'/'takeover_audit.json')
    status=load(ROOT/'ROW_STATUS.json')
    rows=status['rows']
    index=load(ROOT/'FINAL_FAMILY_INDEX.json')['families']
    review=load(ROOT/'_review'/'VISUAL_REVIEW.json')['families']
    report=(ROOT/'SECTION_REPORT.md').read_text(encoding='utf-8')
    checks=[]
    def check(name,ok,details=None):
        checks.append(dict(check=name,pass_=bool(ok),details=details))
    check('input_items_unchanged',sha(ROOT/'ITEMS.json')==before['items_sha256'])
    check('input_groups_unchanged',sha(ROOT/'GROUPS.json')==before['groups_sha256'])
    expected_ids={str(i['row_id']) for i in inventory}
    actual_ids=[r['row_id'] for r in rows]
    check('all_120_rows_final',len(actual_ids)==len(set(actual_ids))==120 and set(actual_ids)==expected_ids)
    table=report.split('## Item register',1)[1]
    report_ids=re.findall(r'^\| (\d+) \|',table,re.M)
    check('report_has_exactly_one_entry_per_row',len(report_ids)==len(set(report_ids))==120 and set(report_ids)==expected_ids)
    counts=Counter(r['status'] for r in rows)
    check('allowed_final_statuses',set(counts)<=set(['DOWNLOADED','AVAILABLE_LOGIN_REQUIRED+BUILT','BUILT','BUILT_WITH_LIMITATIONS','BLOCKED']))
    check('status_counts',counts==Counter({'BUILT_WITH_LIMITATIONS':115,'BLOCKED':5}),dict(counts))
    check('all_43_identity_groups_retained',len(groups)==43 and {r['group_key'] for r in rows}=={g['key'] for g in groups})
    by_folder={m['folder']:m for m in index}
    check('41_distinct_canonical_families',len(index)==len(by_folder)==41 and len({m['rfa_sha256'] for m in index})==41)
    check('41_visual_reviews_recorded',len(review)==41 and {r['key'] for r in review}=={m['key'] for m in index})
    native_summary=[]
    errors=[]
    total_component_checks=0
    total_radial_checks=0
    unique_native_previews=0
    for model in index:
        folder=ROOT/model['folder'];v=load(folder/'validation.json');geo=load(folder/'evidence'/'geometry_review.json')
        rfa=ROOT/model['rfa_path']
        material_tests=v.get('material_tests',{})
        bounds_error=[abs(a-b)*25.4 for a,b in zip(geo['measured_dimensions_in'],v['expected_dimensions_in'])]
        components=v.get('component_checks',[]);radials=v.get('radial_checks',[])
        comp_ok=all(c.get('pass') is True for c in components)
        radial_ok=all(c.get('pass') is True for c in radials)
        for component in components:
            # A null axis is deliberately not constrained by this component's
            # source dimension; only actual numeric errors enter statistics.
            for e in component.get('error_mm',[]):
                if e is not None:errors.append(dict(family=model['key'],check=component['label'],error_mm=e))
        for axis,e in enumerate(bounds_error):errors.append(dict(family=model['key'],check='Overall axis '+str(axis),error_mm=e))
        total_component_checks+=len(components);total_radial_checks+=len(radials)
        warning_count=sum(len(v.get(k,[])) for k in ['family_warnings','reopened_warnings','project_warnings'])
        previews=[folder/'evidence'/n for n in v['evidence_files']]+[Path(p) for p in geo['files']]
        unique_native_previews+=len(previews)
        preview_ok=all(p.exists() and p.read_bytes()[:8]==b'\x89PNG\r\n\x1a\n' for p in previews)
        bitmap_ok=all(Path(b['path']).exists() and b.get('exists') for b in v['saved_material_bitmaps'].values())
        native_ok=bool(v['technical_pass'] and v['revit_version']=='2025' and all(g is True for g in v['gates'].values())
                       and v.get('saved_file_reopened_for_measurement') and v['host']['hostface_present']
                       and v['host']['host_id']==v['host']['instance_host_id']
                       and material_tests and all(t['substitution_reaches_faces'] and t['writable'] for t in material_tests.values())
                       and warning_count==0 and max(bounds_error)<=1.0 and comp_ok and radial_ok and preview_ok and bitmap_ok)
        check('native_'+model['key'],native_ok)
        check('hash_'+model['key'],sha(rfa)==model['rfa_sha256']==geo['rfa_sha256']
              and geo['pass'] and geo['unchanged_after_review']
              and sha(folder/'validation.json')==model['validation_sha256'])
        expected_category='Mechanical Equipment' if model['key']=='RG-C811A' else 'Lighting Fixtures'
        check('category_'+model['key'],v['category']==expected_category)
        native_summary.append(dict(key=model['key'],native_pass=native_ok,max_overall_error_mm=max(bounds_error),
                                   component_checks=len(components),radial_checks=len(radials),warnings=warning_count,
                                   sha256=sha(rfa),preview_files=len(previews)))
    row_hashes=[];row_previews=0;row_bitmaps=0
    item_map={str(i['row_id']):i for i in inventory}
    holds={}
    for row in rows:
        item=item_map[row['row_id']];folder=ROOT/item['item_key'];note=(folder/'NOTES.md').read_text(encoding='utf-8')
        local=load(folder/'ROW_STATUS.json')
        check('row_notes_'+row['row_id'],all(s in note for s in [row['row_id'],item['description'],row['status'],'Source/spec:','Dimensions checked','ASSUMPTION','Blockers:']) and local==row)
        check('ignore_'+row['row_id'],row['agent_ignore_retained']==bool(item.get('agent_ignore')))
        for code in row['needs_user']:holds.setdefault(code,[]).append(row['row_id'])
        v=load(folder/'validation.json')
        if row['status']=='BLOCKED':
            check('blocked_'+row['row_id'],row['rfa_path'] is None and v['native_attempted'] is False and v['technical_pass'] is None and bool(row['needs_user']))
            continue
        model=by_folder[row['canonical_item']]
        rfa=ROOT/row['rfa_path'];row_hashes.append(sha(rfa))
        check('row_rfa_'+row['row_id'],sha(rfa)==row['rfa_sha256']==model['rfa_sha256']
              and rfa.read_bytes()[:8]==bytes.fromhex('d0cf11e0a1b11ae1') and v['technical_pass'])
        if row['validation_basis']=='byte-identical reuse':
            receipt=load(folder/'source'/'REUSE_RECEIPT.json')
            check('reuse_'+row['row_id'],receipt['sha256']==sha(rfa) and (ROOT/receipt['canonical_builder']).exists()
                  and v['row_rfa_sha256']==v['canonical_rfa_sha256']==sha(rfa))
        for name in v['evidence_files']:
            p=folder/'evidence'/name;q=ROOT/row['canonical_item']/'evidence'/name
            check('preview_'+row['row_id']+'_'+name,p.exists() and sha(p)==sha(q));row_previews+=1
        for basename in ['GeometryReview - 3D View - Geometry Front.png','GeometryReview - 3D View - Geometry Oblique.png']:
            p=folder/'evidence'/basename;q=ROOT/row['canonical_item']/'evidence'/basename
            check('outline_'+row['row_id']+'_'+basename,p.exists() and sha(p)==sha(q));row_previews+=1
        for bitmap in v['saved_material_bitmaps'].values():
            p=Path(bitmap['path']);q=folder/'source'/'textures'/p.name
            check('bitmap_'+row['row_id']+'_'+p.name,q.exists() and sha(p)==sha(q));row_bitmaps+=1
        check('source_builder_'+row['row_id'],(folder/'source'/'build_family.py').exists())
    check('115_rfa_copies_match_41_native_hashes',len(row_hashes)==115 and set(row_hashes)=={m['rfa_sha256'] for m in index})
    preserved=0
    for old in before['records']:
        if old['technical_pass']:
            check('preserved_'+old['key'],sha(Path(old['rfa_path']))==old['rfa_sha256'] and sha(ROOT/old['folder']/'validation.json')==old['validation_sha256'])
            preserved+=1
    check('original_ignore_flags_retained',sum(r['agent_ignore_retained'] for r in rows)==3)
    maxim=[r for r in rows if r['group_key']=='57670WTBK']
    check('24_Maxim_rows_use_selected_black_16inch_family',len(maxim)==24 and len({r['rfa_sha256'] for r in maxim})==1 and all(r['delivered_model']=='57670WTBK' for r in maxim))
    chrome=next(r for r in rows if r['row_id']=='8353463272013700')
    smoke=[r for r in rows if r['group_key']=='KZC1009570' and r is not chrome]
    check('Trinity_chrome_row_separated_from_smoke',chrome['delivered_model']=='PD62014-BK/CH'
          and len(smoke)==2 and all(r['delivered_model']=='PD62014-BK/SM' and r['rfa_sha256']!=chrome['rfa_sha256'] for r in smoke))
    expected_holds={
      'NEEDS_USER_PERGOLA_PRODUCT':{'1730804001013636','6234403628384132'},
      'NEEDS_USER_LED_STRIP_BOM':{'2856703907856260','7360303535226756'},
      'NEEDS_USER_D3_COMPATIBLE_ASSEMBLY':{'5108503721541508'},
      'NEEDS_USER_ORION_CONFIGURATION':{'1967952628416388','7223540899774340'}}
    check('all_explicit_decision_holds_exactly_preserved',{k:set(v) for k,v in holds.items()}==expected_holds)
    failures=[c for c in checks if not c['pass_']]
    summary=dict(checked_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),pass_=not failures,
        check_count=len(checks),failed_checks=failures,row_count=len(rows),status_counts=dict(counts),
        native_family_count=len(index),distinct_rfa_hashes=len(set(row_hashes)),row_local_rfas=len(row_hashes),
        native_preview_files=unique_native_previews,row_local_preview_files=row_previews,row_local_material_bitmaps=row_bitmaps,
        component_checks=total_component_checks,radial_checks=total_radial_checks,
        max_recorded_geometry_error_mm=max(e['error_mm'] for e in errors),
        largest_measured_errors=sorted(errors,key=lambda e:e['error_mm'],reverse=True)[:10],
        baseline_canonical_rfa_and_validation_pairs_preserved=preserved,extra_existing_variant='PD62014-BK/CH; final saved-file review confirms unchanged hash',
        report_sha256=sha(ROOT/'SECTION_REPORT.md'),row_status_sha256=sha(ROOT/'ROW_STATUS.json'),
        family_index_sha256=sha(ROOT/'FINAL_FAMILY_INDEX.json'),holds=holds,families=native_summary,
        remaining_build_native_errors=bool(failures),work_complete=not failures,delivery_ready=False)
    (ROOT/'FINAL_CHECKS.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    printed={k:v for k,v in summary.items() if k not in ['families','largest_measured_errors','holds']}
    print(json.dumps(printed,indent=2))
    return 1 if failures else 0

if __name__=='__main__':sys.exit(main())
