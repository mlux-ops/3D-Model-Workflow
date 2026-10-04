"""Assemble every item from validated canonical RFAs; preserve all source artifacts."""
from pathlib import Path
from collections import Counter
import copy
import datetime
import hashlib
import json
import shutil
import sys

ROOT=Path(__file__).resolve().parents[1]
STAMP=datetime.datetime.now(datetime.timezone.utc).isoformat()
MARKER='Electrical Fixtures final row record - worker-4'
CHROME='K1-1__8353463272013700'
HOLDS={
 'HOLD_PERGOLA':('NEEDS_USER_PERGOLA_PRODUCT','Select the exterior wet-rated pergola fixture, exact SKU, finish and dimensional cut sheet. Scope remains three fixtures per unit; no product can be dimensioned from the current row.'),
 'HOLD_LED_STRIP':('NEEDS_USER_LED_STRIP_BOM','Issue run lengths, channel/diffuser profile, selected tape, driver, wattage/CCT and wet-location details. Five runs per unit remain in scope; no complete assembly or channel size is specified.'),
 'EA-PAR16-7.0W-36D-2790-D_16_WH':('NEEDS_USER_D3_COMPATIBLE_ASSEMBLY','Resolve the recorded R14/R16 intermediate-base Juno 16 WH versus E26 PAR16 lamp mismatch and identify the compatible housing/trim/lamp assembly. Three required fixtures per Triplex unit remain recorded.')}

def load(path):return json.loads(path.read_text(encoding='utf-8-sig'))
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def rel(path):return str(Path(path).relative_to(ROOT)).replace('\\','/')
def text(value):return str(value or '').replace('|','/').replace('\n',' ')
def dims(values):return ' x '.join('n/a' if v is None else ('%.6f'%v).rstrip('0').rstrip('.') for v in values)
def save(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    content=json.dumps(value,indent=2,ensure_ascii=True)+'\n' if not isinstance(value,str) else value
    if path.exists() and path.read_text(encoding='utf-8-sig')!=content:
        archive=ROOT/'_review'/'assembly_history'/path.relative_to(ROOT)
        if not archive.exists():
            archive.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,archive)
    path.write_text(content,encoding='utf-8')

def copy_exact(source,target):
    target.parent.mkdir(parents=True,exist_ok=True)
    if target.exists():
        if digest(source)!=digest(target):raise RuntimeError('Conflicting existing artifact preserved: '+str(target))
    else:shutil.copy2(source,target)
    assert digest(source)==digest(target)

def main():
    inventory=load(ROOT/'ITEMS.json');items=inventory['items'];groups=load(ROOT/'GROUPS.json')['groups']
    before=load(ROOT/'_review'/'takeover_audit.json')
    assert digest(ROOT/'ITEMS.json')==before['items_sha256']
    assert digest(ROOT/'GROUPS.json')==before['groups_sha256']
    assert len(items)==120 and len(groups)==43
    mapping={str(r['row_id']):g for g in groups for r in g['rows']}
    assert len(mapping)==120 and set(mapping)=={str(i['row_id']) for i in items}
    review=load(ROOT/'_review'/'final'/'manifest.json')
    notes=load(ROOT/'_review'/'visual_review_notes.json')
    assert len(review)==41 and set(notes)=={r['key'] for r in review}
    families={};visual=[]
    for r in review:
        folder=Path(r['folder']);v=load(folder/'validation.json');geo=load(folder/'evidence'/'geometry_review.json')
        rfa=Path(v['rfa_path']);sha=digest(rfa)
        assert v.get('technical_pass') is True and all(x is True for x in v['gates'].values()),folder
        assert geo.get('pass') and geo.get('unchanged_after_review') and geo['rfa_sha256']==sha==r['rfa_sha256']
        assert v['revit_version']=='2025' and v['category'] in ['Lighting Fixtures','Mechanical Equipment']
        assert rfa.read_bytes()[:8]==bytes.fromhex('d0cf11e0a1b11ae1')
        assert all(abs(a-b)*25.4<=1. for a,b in zip(geo['measured_dimensions_in'],v['expected_dimensions_in']))
        assert not any(v.get(k) for k in ['family_warnings','reopened_warnings','project_warnings'])
        assert all(Path(value['path']).exists() for value in v['saved_material_bitmaps'].values())
        for path in [r['outline'],r['native'],*geo['files']]:assert path and Path(path).exists()
        sources=[];definitions=[]
        for definition in (folder/'source').glob('*definition.json'):
            definitions.append(rel(definition));entry=load(definition)
            if entry.get('source_url'):sources.append(entry['source_url'])
        if not definitions:
            definitions.append(rel(folder/'source'/'build_family.py'))
        if v.get('source_url'):sources.append(v['source_url'])
        model=dict(key=r['key'],folder=folder.name,rfa_path=rel(rfa),rfa_sha256=sha,
            validation_path=rel(folder/'validation.json'),validation_sha256=digest(folder/'validation.json'),
            geometry_review_path=rel(folder/'evidence'/'geometry_review.json'),
            manufacturer=v['manufacturer'],model=v['model'],category=v['category'],
            expected_dimensions_in=v['expected_dimensions_in'],measured_dimensions_in=geo['measured_dimensions_in'],
            source_urls=list(dict.fromkeys(sources)),source_definitions=definitions,
            review_page='_review/final/'+r['review_page'],visual_review='REVIEWED_WITH_LIMITATIONS',
            visual_note=notes[r['key']],native_gates=v['gates'],needs_user=v.get('needs_user',[]))
        families[folder.name]=(model,v,r)
        visual.append(dict(key=r['key'],rfa_sha256=sha,reviewed_utc=STAMP,status='REVIEWED_WITH_LIMITATIONS',
                           review_page=model['review_page'],note=notes[r['key']]))
    assert len(families)==41 and len({m[0]['rfa_sha256'] for m in families.values()})==41
    for old in before['records']:
        if old['technical_pass']:
            assert digest(Path(old['rfa_path']))==old['rfa_sha256'],'Preexisting RFA changed'
            assert digest(ROOT/old['folder']/'validation.json')==old['validation_sha256'],'Preexisting validation changed'
    rows=[]
    for item in items:
        rid=str(item['row_id']);group=mapping[rid];folder=ROOT/item['item_key']
        row=dict(row_id=rid,item_key=item['item_key'],group_key=group['key'],description=item['description'],
                 source_model=item.get('model_number'),agent_ignore_retained=bool(item.get('agent_ignore')),
                 unit=item.get('unit_type'),room=item.get('room_type'),notes_path=rel(folder/'NOTES.md'))
        lines=['# '+MARKER,'','Row ID: `'+rid+'`','',
               'Inventory identity: '+str(item['description'])+'; recorded model `'+str(item.get('model_number') or 'unspecified')+'`.',
               '','Location: '+str(item.get('unit_type'))+' / '+str(item.get('room_type'))+'. Agent Ignore retained: '+str(bool(item.get('agent_ignore')))+'.',
               '','All package paths below are relative to the Electrical Fixtures section root.','']
        if group['key'] in HOLDS:
            code,reason=HOLDS[group['key']]
            row.update(status='BLOCKED',rfa_path=None,technical_pass=None,needs_user=[code],summary=reason)
            lines.extend(['Status: **BLOCKED**','',
                'Source/spec: original ITEMS.json inventory and recorded schedule scope in inventory_row.json; no selected dimensional product specification is present.','',
                'Dimensions checked: none. No unverified generic product dimensions were substituted.','',
                'ASSUMPTION: preserve the explicit required scope and hold instead of selecting a new fixture or assembly.','',
                'Blockers: **'+code+'**. '+reason,'',
                'Last verified stage: row identity/schedule reconciliation. RFA search and native build cannot select a defensible exact product until this hold is resolved.','',
                'Recorded source notes: '+str(item.get('source_notes') or 'None.'),''])
            save(folder/'validation.json',dict(row_id=rid,status='BLOCKED',native_attempted=False,technical_pass=None,
                 dimensions_checked=[],blockers=[code],last_verified_stage='Inventory / explicit schedule hold',reason=reason))
        else:
            canonical=item['item_key'] if item['item_key']==CHROME else group['canonical_item']
            model,v,r=families[canonical]
            source_rfa=ROOT/model['rfa_path'];target=folder/source_rfa.name
            copy_exact(source_rfa,target)
            reuse=folder.name!=canonical
            for bmp in v['saved_material_bitmaps'].values():copy_exact(Path(bmp['path']),folder/'source'/'textures'/Path(bmp['path']).name)
            evidence=folder/'evidence';evidence.mkdir(exist_ok=True)
            for name in v['evidence_files']:
                copy_exact(ROOT/canonical/'evidence'/name,evidence/name)
            for name in ['GeometryReview - 3D View - Geometry Front.png','GeometryReview - 3D View - Geometry Oblique.png']:
                copy_exact(ROOT/canonical/'evidence'/name,evidence/name)
            if reuse:
                copied=copy.deepcopy(v)
                copied.update(rfa_path=str(target),row_id=rid,canonical_rfa_path=str(source_rfa),
                    canonical_validation_path=str(ROOT/canonical/'validation.json'),
                    validation_basis='Measurements and native gates inherited only after byte-identical RFA hash verification; not a separately rerun native build.',
                    canonical_rfa_sha256=model['rfa_sha256'],row_rfa_sha256=digest(target))
                save(folder/'validation.json',copied)
                link=dict(row_id=rid,canonical_item=canonical,canonical_builder=canonical+'/source/build_family.py',
                          path_basis='Electrical section root',canonical_rfa=model['rfa_path'],
                          sha256=model['rfa_sha256'],reuse='Byte-identical validated native family')
                save(folder/'source'/'REUSE_RECEIPT.json',link)
                # A row-local reproducer copies the validated canonical RFA; it never rebuilds accepted geometry.
                builder="""\"\"\"Reproduce this row from its hash-verified native canonical family.\"\"\"
from pathlib import Path
import hashlib,shutil
row=Path(__file__).resolve().parents[1]
source=row.parent / %r
target=row/source.name
assert hashlib.sha256(source.read_bytes()).hexdigest()==%r
if target.exists():
    assert hashlib.sha256(target.read_bytes()).hexdigest()==%r
else:
    shutil.copy2(source,target)
print('Validated native row copy:',target)
"""%(model['rfa_path'],model['rfa_sha256'],model['rfa_sha256'])
                save(folder/'source'/'build_family.py',builder)
            limit=v.get('limitations') or v.get('inferences') or 'Fixed product geometry with editable visualization materials.'
            user_holds=list(model['needs_user'])
            if group['key']=='ORION_TUBE_UNSPECIFIED' and 'NEEDS_USER_ORION_CONFIGURATION' not in user_holds:user_holds.append('NEEDS_USER_ORION_CONFIGURATION')
            status='BUILT_WITH_LIMITATIONS'
            summary=notes[model['key']]
            row.update(status=status,rfa_path=rel(target),rfa_sha256=digest(target),canonical_item=canonical,
                canonical_rfa_path=model['rfa_path'],validation_path=rel(folder/'validation.json'),
                validation_basis='byte-identical reuse' if reuse else 'native saved-file measurement',
                technical_pass=True,needs_user=user_holds,delivered_manufacturer=model['manufacturer'],
                delivered_model=model['model'],expected_dimensions_in=model['expected_dimensions_in'],
                measured_dimensions_in=model['measured_dimensions_in'],summary=summary,
                review_page=model['review_page'],source_urls=model['source_urls'])
            lines.extend(['Status: **'+status+'**','',
                'Delivered identity: **'+model['manufacturer']+' '+model['model']+'**.','',
                'RFA: `'+rel(target)+'`','SHA-256: `'+model['rfa_sha256']+'`','',
                'Category/template: '+model['category']+'; native Revit 2025 Generic Model face-based template recategorized for the fixture. Native '+str(v['host']['host_kind'])+' face placement was verified.','',
                'Source/spec: '+('; '.join(model['source_urls']) or 'See source definitions and retained receipts.')+'.','',
                'RFA search: '+str(v.get('rfa_search') or 'See retained primary-source acquisition and inspection records.')+'','',
                'Source evidence: `'+canonical+'/source/`; definitions '+', '.join('`'+p+'`' for p in model['source_definitions'])+'.','',
                'Terms/version: anonymous public sources only; no account, credentials or license acceptance used. Manufacturer copyright retained. Final family saved and reopened in Revit 2025; original OEM files and older-version upgrade receipts remain in the source folders. This output is a native build/reconstruction, not an unchanged downloaded OEM family.','',
                '## Dimensions checked','',
                '| Check | Expected, inches | Saved measurement, inches |','|---|---|---|',
                '| Overall native envelope | '+dims(model['expected_dimensions_in'])+' | '+dims(model['measured_dimensions_in'])+' |'])
            for component in v.get('component_checks',[]):
                lines.append('| '+text(component['label'])+' | '+dims(component['expected_dimensions_in'])+' | '+dims(component.get('measured_dimensions_in',[]))+' |')
            lines.extend(['','Local coordinate order: wall families width / height / projection; overhead families X / Y / total envelope. For fans the static rectangular envelope differs from swept blade diameter; radial checks are retained below.'])
            if v.get('radial_checks'):lines.extend(['','Radial checks: `'+json.dumps(v['radial_checks'],ensure_ascii=True)+'`'])
            lines.extend(['','Native gates: '+', '.join(name+'=PASS' for name in v['gates'])+'.',
                'Warnings: zero in family, reopened file and disposable host project. Finish substitution reached native faces and was restored. Saved bitmap bindings resolve.','',
                'Validation: `'+rel(folder/'validation.json')+'`. Canonical evidence: `'+canonical+'/validation.json` and `'+canonical+'/evidence/geometry_review.json`.','',
                ('This row uses a byte-identical RFA copy. Canonical native measurements are reused only after SHA-256 comparison; no separate native run is claimed for this duplicate.' if reuse else 'This canonical family was measured in saved-file native checks and independently reopened for the final geometry review.'),
                '','## Assumptions and limitations','','ASSUMPTION / modeled limitations: '+limit,'',
                'Parameter scope: '+str(v.get('parameter_scope') or 'Fixed nominal dimensions; editable material parameters.')+'','',
                'Visual review: REVIEWED_WITH_LIMITATIONS. '+summary,
                'Review image: `'+model['review_page']+'`; individual front/side/oblique/material and hosted images are retained in this row evidence folder.','',
                'Viewport shading is unlit evidence. Accurate photometric output, production-render glass/reflection matching, and final client visual approval are not established by the native gates.','',
                'Blockers: '+('; '.join(user_holds) if user_holds else 'No remaining source/build/native gate blocker. The listed modeling assumptions remain for orchestrator acceptance')+'.','',
                'Loading: keep the section directory structure and companion textures. Bitmap bindings currently resolve to canonical source/textures folders. When relocating, add the included texture folders to Revit Additional Render Appearance Paths or relink them. Copying only an RFA omits appearance assets.','',
                'Original inventory notes: '+str(item.get('source_notes') or 'None.'),''])
        save(folder/'NOTES.md','\n'.join(lines))
        save(folder/'ROW_STATUS.json',row)
        rows.append(row)
    status_counts=dict(Counter(r['status'] for r in rows))
    assert status_counts=={'BUILT_WITH_LIMITATIONS':115,'BLOCKED':5}
    assert all((ROOT/r['notes_path']).exists() for r in rows)
    final=dict(completed_utc=STAMP,task='1527 Wieland Electrical Fixtures',rows=rows,
        row_count=120,identity_groups=43,unique_native_families=41,status_counts=status_counts,
        input_sha256=before['items_sha256'],groups_sha256=before['groups_sha256'],
        work_complete=True,delivery_ready=False,release='Orchestrator review required; source holds and model limitations are explicit.')
    save(ROOT/'ROW_STATUS.json',final)
    save(ROOT/'FINAL_FAMILY_INDEX.json',dict(families=[m[0] for m in families.values()],count=41))
    save(ROOT/'_review'/'VISUAL_REVIEW.json',dict(reviewed_utc=STAMP,family_count=41,status='REVIEWED_WITH_LIMITATIONS',families=visual))
    report=['# Electrical Fixtures - 1527 Wieland','',MARKER,'',
        'Completed '+STAMP+'. All 120 input rows have a final status and row NOTES.md.','',
        '**115 BUILT_WITH_LIMITATIONS; 5 BLOCKED.** The 115 row-local RFA files represent 41 distinct native families across 40 built identity groups. Three identity groups remain explicitly blocked. The additional family is the separately selected chrome Trinity variant. Three Agent Ignore rows were retained and processed.','',
        'All 41 canonical families passed saved-file Revit 2025 checks and were reopened for a final measured review. The final review generated 82 additional front/oblique views and left all 41 RFA hashes unchanged. The 40 passing families present at takeover and their canonical validation files were preserved. This continuation added Orion, repaired its thin-wire build, completed visual evidence, and assembled the row deliverables.','',
        'No final family is classified DOWNLOADED: preserved OEM sources either needed geometry/host/material adaptation or could not be accepted unchanged. No exact, usable login-only RFA is asserted by this final classification. Source acquisition and inspection histories remain intact.','',
        '## Remaining decisions','',
        '| Code | Rows | Required resolution |','|---|---|---|']
    for key,(code,reason) in HOLDS.items():
        ids=', '.join(r['row_id'] for r in rows if r['group_key']==key)
        report.append('| '+code+' | '+ids+' | '+text(reason)+' |')
    report.append('| NEEDS_USER_ORION_CONFIGURATION | 1967952628416388, 7223540899774340 | Confirm finish, orientation, connected-module arrangement and installed drop. Representative ORI0120 gold / horizontal / 48-inch family is built and technically validated. |')
    report.extend(['','## Review limits','',
        'All native models were visually inspected using 11 source/outline/shaded review sheets. REVIEWED_WITH_LIMITATIONS is separate from client visual approval. Glass/reflection/glow, fine construction details, several installed drops and the fans\' blade contours remain approximations. Silvio and Panasonic have retained dimensional/spec evidence but no paired source photograph in the review sheets. The Commercial Electric reference thumbnail is low resolution. The chrome Trinity smoke photograph is labeled geometry-only. These limits are recorded for each affected row.','',
        'Use FINAL_FAMILY_INDEX.json for distinct families, ROW_STATUS.json for all 120 rows, _review/VISUAL_REVIEW.json for image observations, and each row validation.json for measured values and native gates. Duplicate rows contain byte-identical copies and explicitly inherit canonical native evidence; they are not represented as 115 independent native builds.','',
        'Keep the section and its source/textures folders together. Revit bitmap bindings currently point to the canonical source folders; relocation requires appearance search paths or relinking. No Drive upload or Smartsheet edit was performed.','',
        '## Item register','',
        '| Row ID | Item / delivered identity | Final status | RFA path | Gate results | Note |',
        '|---|---|---|---|---|---|'])
    for r in rows:
        identity=(r.get('delivered_manufacturer','')+' '+r.get('delivered_model','')).strip() or r['description']
        gate='Revit 2025 / dimensions / host / materials / warnings PASS; visual limitations' if r['technical_pass'] else 'Not attempted: explicit product or compatibility hold'
        report.append('| '+r['row_id']+' | '+text(identity)+' | '+r['status']+' | '+('`'+r['rfa_path']+'`' if r['rfa_path'] else 'None')+' | '+gate+' | '+text(r['summary'])+' |')
    save(ROOT/'SECTION_REPORT.md','\n'.join(report)+'\n')
    print(json.dumps(dict(rows=120,status_counts=status_counts,unique_native_families=41,row_local_rfas=115,notes=120,report='SECTION_REPORT.md'),indent=2))

if __name__=='__main__':main()
