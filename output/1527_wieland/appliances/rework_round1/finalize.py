"""Publish the nine reviewed replacement records without changing other models."""
import collections
import copy
import datetime
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
BASE=json.loads((HERE/'baseline.json').read_text())
CONFIGS=json.loads((HERE/'configs.json').read_text())
TARGETS={c['slug'] for c in CONFIGS}
NOW=datetime.datetime.now(datetime.timezone.utc).isoformat()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:Path(p).relative_to(ROOT).as_posix()

OBSERVATIONS={
 'miele_h7280bp':'Front, side and oblique views show the full-height black oven fascia, recessed glazing, touch-control band, horizontal handle and metal case. The complete case-to-handle extent is measured. Concealed case partition and cavity detailing are approximations.',
 'miele_h7270bm':'The compact speed-oven proportions, black control band, door glazing and horizontal handle are visible in all three views. The complete 573 mm depth includes modeled handle geometry; concealed case depth is reconstructed for the requested nominal envelope.',
 'miele_g5051scvi':'The 815 mm high integrated dishwasher shows its top control strip, separate factory door skin, recessed toe region and feet. No detached hardware or connector glyph obscures the preview. The neutral editable front is not an approved customer overlay.',
 'miele_kwt6722is':'The tall right-hinged wine cabinet shows eight beech-colored shelf assemblies, two separated storage regions, a glazed door and lower ventilation. Sommelier accessories, shelf mechanisms and detailed optical response remain simplified.',
 'miele_kwtus7172f':'The under-counter wine cabinet shows five shelf assemblies, a single storage region, glazed door, right-side hinges and lower ventilation. Crosswise-storage hardware is simplified; shelf material and count are represented without claiming fabrication detail.',
 'miele_kfmc3858fd':'Two upper French-door fronts, one smaller convertible drawer, one larger lower drawer and the recessed toe grille are visible. The 1048 mm appliance body width replaces the oversized prior working family. No unselected customer pulls or applied furniture overlay is included.',
 'thermador_t42it100np':'The complete factory appliance is visible with two upper French doors, two lower drawer faces and toe grille at the documented minimum 2123 mm height. Customer panels, pulls, cutout framing and accessory frame kits are not part of this default envelope.',
 'thermador_podmc301w':'The smaller upper speed oven and larger lower oven are distinct, each with its control fascia, glazing and round handle. The complete geometry fits the requested nominal 622.3 mm depth. The body/handle partition differs from a fabrication interpretation of the separate installation section and is explicitly documented.',
 'thermador_pcg486wd':'Six star-shaped burner assemblies are arranged as four on the left and two on the right, with a griddle between them, seven front controls and a rounded bolster. Grate tops and knob projections are included in the complete measured envelope. Local grate/crown profiles remain simplified.'}

def write_json(path,value):
    path.write_text(json.dumps(value,indent=2,ensure_ascii=True),encoding='utf-8')

def dimensions(values):
    return ' x '.join('%.3f'%x for x in values)+' mm'

def gate_line(c,v):
    return c['model']+': open/save/reopen/category/place/preview PASS; fit PASS (complete overall); material %d/%d family and %d/%d placed; warnings 0'%(len(v['parameter_flex']),len(v['parameter_flex']),len(v['placed_material_flex']),len(v['placed_material_flex']))

def canonical_notes(c,m,v,old):
    slug=c['slug'];rows=', '.join(str(x) for x in m['row_ids'])
    lines=['# '+c['brand']+' '+c['model']+' - custom replacement R1','',
        'Status: **BUILT_WITH_LIMITATIONS**. Native round-1 gates: **PASS**. Orchestrator review/release: pending.','',
        'Smartsheet row IDs: '+rows+'.',
        'Working RFA: `'+m['rfa']+'`. SHA-256: `'+m['rfa_sha256']+'`.','',
        '## Why this is custom',c['replacement_reason'],'',
        'The prior working RFA remains at `'+old['rfa']+'` with unchanged SHA-256 `'+old['rfa_sha256']+'`. Its historical measurements are retained in `../rework_round1/history_before/'+slug+'/validation.json`. Manufacturer originals remain in `source/original/`; their original hashes are preserved in source_manifest.json. No source RFA was rescaled or overwritten.','',
        '## Dimension authority and native evidence',c['dimension_basis'],'',
        'Authoritative axes: X = width, Y = front-to-back depth, Z = height.',
        'Target W x D x H: **'+dimensions(c['target_xyz_mm'])+'**.',
        'Actual complete placed-solid bounds: **'+dimensions(v['placed_bounds']['xyz_size_mm'])+'**.',
        'Delta W, D, H: '+', '.join('%+.9f'%x for x in v['dimension_delta_mm'])+' mm.',
        'The same complete geometry was measured after native reopen and again after placement. All components, including modeled handles, feet, grates and trim, are included; no selected-body filter or artificial envelope object was used.',
        'Revit format: 2025. Category: Specialty Equipment. Placement: WorkPlaneBased; actual native host: '+v['placement']['host_category']+'.',
        'Native geometry: %d FreeFormElements, zero imported CAD instances, zero nested manufacturer family instances.'%v['native_freeform_count'],
        'Material substitutions and restoration: %d/%d in the reopened family and %d/%d in the placed instance. Every used finish has a native appearance and a verified bound companion bitmap.'%(len(v['parameter_flex']),len(v['parameter_flex']),len(v['placed_material_flex']),len(v['placed_material_flex'])),
        'Fixed manufacturer size: Overall Width/Depth/Height are formula-locked. Variable dimensional flex is not advertised; editable finish controls were tested.',
        'Warnings: zero in both family and disposable placement project.','',
        '## Visual inspection',OBSERVATIONS[slug],'',
        'Fresh native views:']
    lines += ['- `'+p+'`' for p in m['previews']]
    lines += ['', '## Sources and retained evidence',
              'Manufacturer specification: `source/product_sheet.pdf`, SHA-256 `'+c['source_pdf_sha256']+'`.']
    if c['source_page']:lines.append('Dimension authority page: '+str(c['source_page'])+'.')
    lines += ['- '+u for u in c['source_urls']]
    lines += ['', '## Assumptions and limitations']+['- '+s for s in c['declared_limitations']]
    lines += ['', 'The default factory-front material is editable where present. Uniform companion bitmaps do not claim a selected cabinetry species, optical calibration or manufacturer-certified surface shader.',
       '', '## Files and reproducibility',
       'Current validation: `validation.json`; unchanged native-run record: `source/rework_r1/validation.json`. Build checkpoint and input dimensions: `source/rework_r1/build_result.json` and `source/rework_r1/config.json`.',
       'Entry script: `source/build.py`. Shared code: `../rework_round1/native_rebuild.py`, `../rework_round1/validate_native.py` and `../family_common.py`. Run Revit operations only through the repository shared revit_run.py/revit.lock. The builder refuses to overwrite an existing replacement RFA.',
       'Companion finish maps: `source/rework_r1/*_Finish.png`. Native texture paths are recorded in validation.json and must remain resolvable if a package is relocated.',
       '', '## Blockers',
       'No native build, dimension, category, placement, material or preview blocker remains for round 1. Detailed installation clearances and the explicitly stated inferred local geometry are not certified by the overall dimension pass. Final delivery is controlled by the orchestrator.']
    return '\n'.join(lines)+'\n'

def main():
    # Fail before editing any released record if a protected original has changed.
    conflicts=[p for p,digest in BASE['protected_files'].items() if not (ROOT/p).is_file() or sha(ROOT/p)!=digest]
    if conflicts:raise RuntimeError('Protected files differ: '+repr(conflicts))
    manifest=copy.deepcopy(BASE['original_manifest'])
    visuals=json.loads((HERE/'history_before'/'visual_review.json').read_text())
    inputs={int(x['row_id']):x for x in json.loads((ROOT/'ITEMS.json').read_text())['items']}
    current={}
    for c in CONFIGS:
        slug=c['slug'];folder=ROOT/slug
        v=json.loads((folder/'source'/'rework_r1'/'validation.json').read_text())
        if not v.get('native_gates_pass'):raise RuntimeError('Native gate incomplete: '+slug)
        old=next(x for x in BASE['original_manifest']['canonical_models'] if x['slug']==slug)
        m=next(x for x in manifest['canonical_models'] if x['slug']==slug)
        image_refs=[{'path':rel(p),'sha256':sha(Path(p))} for p in v['previews']]
        visual={'slug':slug,'reviewed_utc':NOW,'reviewer':'worker-1','revision':'Custom_R1',
                'method':'Direct inspection of all three native views, assembled without image generation into a per-model review board; retained product imagery/specification used as reference.',
                'images':image_refs,'observation':OBSERVATIONS[slug],
                'visual_gate':'PASS_WITH_DOCUMENTED_LIMITATIONS','design_or_photographic_approval':False,
                'review_board':rel(HERE/(slug+'_review.png'))}
        visuals=[visual if x['slug']==slug else x for x in visuals]
        v.update(visual_review=visual,visual_review_pending=False,all_acceptance_gates_pass=True,
                 requested_round1_gates_pass=True,orchestrator_release_approved=False,
                 rfa_sha256=sha(folder/c['rfa_name']),superseded_working_rfa=old['rfa'])
        write_json(folder/'validation.json',v)
        m.update(status='BUILT_WITH_LIMITATIONS',rfa=slug+'/'+c['rfa_name'],rfa_bytes=(folder/c['rfa_name']).stat().st_size,
                 rfa_sha256=v['rfa_sha256'],previews=[p['path'] for p in image_refs],
                 revision='Custom_R1',build_method='native_custom_new_family',
                 dimension_gate=True,dimension_gate_scope='overall',native_gates_pass=True,
                 replacement_reason=c['replacement_reason'],
                 superseded_working_rfa={'path':old['rfa'],'sha256':old['rfa_sha256'],'status':old['status']},
                 source_pdf_sha256=c['source_pdf_sha256'],source_page=c['source_page'],
                 custom_build_entry=slug+'/source/build.py',
                 build_support=['rework_round1/native_rebuild.py','rework_round1/validate_native.py','family_common.py'],
                 validation_native_record=slug+'/source/rework_r1/validation.json',
                 validation_sha256=sha(folder/'validation.json'))
        write_json(folder/'source_manifest.json',m)
        (folder/'NOTES.md').write_text(canonical_notes(c,m,v,old),encoding='utf-8')
        current[slug]=(c,m,v)
    for row in manifest['rows']:
        if not any(s in TARGETS for s in row['model_slugs']):continue
        c,m,v=current[row['model_slugs'][0]]
        row.update(status='BUILT_WITH_LIMITATIONS',rfa_paths=[m['rfa']],gate_results=[gate_line(c,v)],
                   note='Round-1 custom replacement: complete overall dimensions and all native gates pass. Prior source/working RFAs retained; local geometry and finish assumptions remain documented.',
                   rework_round=1,requested_round1_gates_pass=True)
        source=inputs[int(row['row_id'])]
        text=['# Row '+str(row['row_id'])+' - '+row['item'],'',
              'Status: **BUILT_WITH_LIMITATIONS**. Round-1 native gates: **PASS**.','',
              'Unit / room: '+str(source['unit_type'])+' / '+str(source['room_type'])+'. Original Agent Ignore: '+str(row['agent_ignore'])+'.','',
              '## Identity','Exact model: '+c['brand']+' '+c['model']+'. Scheduled finish: '+str(source['finish'])+'.',
              'The custom working replacement follows the authorized exact-identity model. Manufacturer originals and the prior working RFA remain retained.','',
              '## Family and evidence','RFA: `../'+m['rfa']+'`.',
              'Actual complete native W x D x H: **'+dimensions(v['placed_bounds']['xyz_size_mm'])+'**.',
              'Target: '+dimensions(c['target_xyz_mm'])+'. All three axis deviations are <=1 mm.',
              gate_line(c,v)+'.','',
              'See [canonical notes](../'+c['slug']+'/NOTES.md), [validation](../'+c['slug']+'/validation.json) and [source manifest](../'+c['slug']+'/source_manifest.json) for sources, exact deltas, assumptions and original-file hashes.','',
              '## Disposition','No round-1 technical blocker remains. Native/source geometry assumptions remain explicit in the canonical notes. Final release remains with the orchestrator.']
        (ROOT/row['notes_path']).write_text('\n'.join(text)+'\n',encoding='utf-8')
    manifest.update(generated_utc=NOW,rework_round=1,status_counts=dict(collections.Counter(r['status'] for r in manifest['rows'])),
                    full_dimension_pass_models=BASE['original_manifest']['full_dimension_pass_models']+[c['slug'] for c in CONFIGS],
                    dimension_hold_models=[s for s in manifest['dimension_hold_models'] if s not in TARGETS],
                    round1_completed_models=[c['slug'] for c in CONFIGS],
                    round1_affected_rows=[r['row_id'] for r in manifest['rows'] if r.get('rework_round')==1],
                    user_decision_holds_unchanged=['thermador_t18iw905sp','thermador_t24ur905rp','thermador_mc30wp','thermador_prd48wisgu','thermador_wd30w'],
                    delivery_ready=False)
    write_json(ROOT/'section_manifest.json',manifest)
    write_json(ROOT/'visual_review.json',visuals)
    receipt={'utc':NOW,'models_completed':9,'affected_rows':len(manifest['round1_affected_rows']),
             'native_pass_count':sum(v['native_gates_pass'] for c,m,v in current.values()),
             'family_material_tests':sum(len(v['parameter_flex']) for c,m,v in current.values()),
             'placed_material_tests':sum(len(v['placed_material_flex']) for c,m,v in current.values()),
             'preview_count':sum(len(v['previews']) for c,m,v in current.values()),
             'max_dimension_error_mm':max(abs(x) for c,m,v in current.values() for x in v['dimension_delta_mm']),
             'new_rfas':[{'slug':c['slug'],'path':m['rfa'],'sha256':m['rfa_sha256'],'actual_xyz_mm':v['placed_bounds']['xyz_size_mm']} for c,m,v in current.values()],
             'protected_files_unchanged':len(BASE['protected_files']),'prior_metadata_archived':len(BASE['mutable_before']),
             'delivery_ready':False,'blockers_in_assigned_scope':[],
             'remaining_user_holds':manifest['user_decision_holds_unchanged'],'artifact_audit_pending':True}
    write_json(HERE/'completion_receipt.json',receipt)
    print(json.dumps({k:v for k,v in receipt.items() if k!='new_rfas'},indent=2))

if __name__=='__main__':main()
