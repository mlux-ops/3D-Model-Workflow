"""Produce row-complete appliance delivery records from actual validation artifacts."""
import collections
import datetime
import hashlib
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parent
STAMP=datetime.datetime.now(datetime.timezone.utc).isoformat()
inventory=json.loads((ROOT/'ITEMS.json').read_text(encoding='utf-8'))
items=inventory['items']
downloaded={x['slug']:x for x in json.loads((ROOT/'downloaded_models.json').read_text())}
custom={x['slug']:x for x in json.loads((ROOT/'custom_models.json').read_text())}
models=dict(downloaded,**custom)
ROW_MODELS=[
 (3292695531945860,['lg_wm4000hba','lg_dlgx4001b']),
 (7384660666023812,['miele_kwt6722is']),
 (3328172767117188,['miele_g5051scvi']),
 (4418595438788484,['miele_h7280bp']),
 (8816514970877828,['miele_h7270bm']),
 (6670395252473732,['miele_km3054_1g']),
 (2166795625103236,['miele_kfmc3858fd']),
 (7796295159316356,['tradewind_i32363rc']),
 (8923394272198532,['ge_gfw550ssnww']),
 (5407997394747268,['ge_gfd55gssnww']),
 (4443914724376452,['lg_wm4000hba','lg_dlgx4001b']),
 (904397767376772,['miele_g5051scvi']),
 (4666245805309828,['miele_kwtus7172f']),
 (3025963735121796,['miele_h7280bp']),
 (6403663455649668,['miele_h7270bm']),
 (7831772394487684,['miele_km3054_1g']),
 (1900063828279172,['miele_kfmc3858fd']),
 (162646177939332,['tradewind_i32363rc']),
 (6521680267116420,['summit_sdhwc98pnr']),
 (2705397813673860,['thermador_t18iw905sp']),
 (6703228487401348,['thermador_t24ur905rp']),
 (7829128394243972,['thermador_t42it100np']),
 (2018080639745924,['thermador_mc30wp']),
 (2199628860030852,['thermador_podmc301w']),
 (7647580173959044,['thermador_prd48wisgu']),
 (8955028301086596,['thermador_pcg486wd']),
 (4451428673716100,['thermador_wd30w'])
]
mapping=dict(ROW_MODELS)
assert len(items)==27 and set(mapping)=={x['row_id'] for x in items}

ASSUMPTIONS={
 3292695531945860:'One row is a washer/dryer pair: both separate native families are provided. Black Steel follows the B model suffix.',
 4443914724376452:'One row is a washer/dryer pair. The stated WM4000HBA model controls the conflicting 5.0-cu-ft wording; no alternate washer was substituted.',
 6670395252473732:'The supplied correction KM 3054-1 G governs the older KM2355G row wording.',
 7831772394487684:'The supplied correction KM 3054-1 G governs the older KM2355G row wording.',
 5407997394747268:'The supplied correction GFD55GSSNWW gas dryer governs the obsolete electric-model wording.',
 7796295159316356:'The explicit Trade-Wind I32363RC model governs the conflicting Zephyr vendor/description text.',
 162646177939332:'The explicit Trade-Wind I32363RC model governs the conflicting Zephyr vendor/description text.',
 2705397813673860:'ASSUMPTION: abbreviated T18IW905S link resolves to the official panel-ready T18IW905SP model. The full suffix is a working selection requiring design confirmation.',
 6703228487401348:'ASSUMPTION / IDENTITY HOLD: the exact T24UR905RP product URL governs the working family. It is a 24-inch undercounter refrigerator; the row says 30-inch warming drawer. These are different appliances.',
 2018080639745924:'ASSUMPTION: MC30WP is the manufacturer Professional-series 30-inch 1.6-cu-ft speed oven matching the description. The row has no exact SKU or URL.',
 7647580173959044:'ASSUMPTION / IDENTITY HOLD: exact URL model PRD48WISGU governs the working family. It is a 48-inch range with steam and induction; the row describes a 30-inch double/triple oven.',
 4451428673716100:'ASSUMPTION / IDENTITY HOLD: exact URL and manufacturer indicate Thermador WD30W warming drawer; the row description instead identifies a Zephyr 47-inch hood. The family is explicitly WD30W, not a hood.'
}
IDENTITY_HOLDS={6703228487401348,7647580173959044,4451428673716100}
PRODUCT_URLS={
 'miele_h7280bp':'https://www.mieleusa.com/product/11968200/30-inch-convection-oven-h-7280-bp-obsidian-black',
 'miele_h7270bm':'https://www.mieleusa.com/product/11968190/30-speed-oven-h-7270-bm-obsidian-black',
 'miele_g5051scvi':'https://www.mieleusa.com/product/11636710/fully-integrated-ada-dishwasher-g-5051-scvi-active-stainless-steel',
 'miele_kwt6722is':'https://www.mieleusa.com/product/11329860/24-built-in-wine-refrigerator-kwt-6722-is',
 'miele_kwtus7172f':'https://www.mieleusa.com/product/12519520/24-built-under-wine-refrigerator-kwtus-7172-f',
 'miele_kfmc3858fd':'https://www.mieleusa.com/product/12489440/42-mastercool-frenchdoor-bottom-mount-unit-kfmc-3858-fd-compatible-with-furniture-fronts'
}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def rel(path):
    return Path(path).relative_to(ROOT).as_posix()
def mm(values):
    return ' x '.join(f'{v:.3f}' for v in values)+' mm'
def esc(text):
    return str(text).replace('|','/').replace('\n',' ')
def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))
def traverse(value):
    if isinstance(value,dict):
        if value.get('url') and (value.get('item') or value.get('slug')):
            yield value
        for child in value.values():
            yield from traverse(child)
    elif isinstance(value,list):
        for child in value:
            yield from traverse(child)

source_records=collections.defaultdict(list)
manifest_names=['source_downloads.json','source_downloads_more.json','thermador_downloads.json',
                'thermador_downloads_extra.json','reference_downloads.json','final_reference_downloads.json',
                'catalog_sources.json','additional_source_search.json']
for name in manifest_names:
    p=ROOT/name
    if p.exists():
        for record in traverse(read_json(p)):
            slug=record.get('item',record.get('slug'))
            if slug in models:
                source_records[slug].append({'url':record['url'],'manifest':name,'download_ok':record.get('ok')})

validations={}
for slug,c in models.items():
    p=ROOT/slug/'validation.json'
    v=read_json(p)
    assert v.get('ok') and v.get('reopened') and v.get('saved_revit_format')=='2025',(slug,v.get('stage'),v.get('error'))
    assert v.get('placement',{}).get('placed'),slug
    # This is source reconciliation only; the actual native measurements remain untouched.
    if slug in downloaded:
        if v['target_xyz_mm']!=c['target_xyz_mm']:
            v['reference_reconciliation']={'utc':STAMP,'prior_target_xyz_mm':v['target_xyz_mm'],
                'reason':'Use explicit metric values in the preserved current manufacturer product sheet; native measured geometry is unchanged.'}
        v['target_xyz_mm']=c['target_xyz_mm']
        v['dimension_basis']=c['dimension_basis']
        v['dimension_delta_mm']=[v['placed_bounds']['xyz_size_mm'][i]-c['target_xyz_mm'][i] for i in range(3)]
        v['dimension_gate']=all(abs(d)<=1.0 for d in v['dimension_delta_mm'])
        v['all_acceptance_gates_pass']=bool(v['dimension_gate'] and v.get('parameter_flex') and all(x['pass'] for x in v['parameter_flex']))
        p.write_text(json.dumps(v,indent=2),encoding='utf-8')
    assert Path(v['saved_rfa']).is_file(),slug
    assert v.get('previews') and all(Path(x).is_file() for x in v['previews']),slug
    validations[slug]=v

canonical=[]
for slug,c in models.items():
    v=validations[slug]
    folder=ROOT/slug
    rfa=Path(v['saved_rfa'])
    source_urls=list(dict.fromkeys(x['url'] for x in source_records[slug]))
    source_urls=list(dict.fromkeys(([PRODUCT_URLS[slug]] if slug in PRODUCT_URLS else [])+
                    ([c['spec_url']] if c.get('spec_url') else [])+source_urls))
    existing_originals=sorted((folder/'source'/'original').rglob('*.rfa')) if (folder/'source'/'original').exists() else []
    payload={'model':c['model'],'slug':slug,'status':'DOWNLOADED' if slug in downloaded else 'BUILT_WITH_LIMITATIONS',
             'rfa':rel(rfa),'rfa_bytes':rfa.stat().st_size,'rfa_sha256':sha(rfa),
             'row_ids':[row for row,slugs in ROW_MODELS if slug in slugs],
             'source_urls':source_urls,'original_rfas':[{'path':rel(p),'sha256':sha(p)} for p in existing_originals],
             'validation':rel(folder/'validation.json'),'previews':[rel(x) for x in v['previews']]}
    (folder/'source_manifest.json').write_text(json.dumps(payload,indent=2),encoding='utf-8')
    canonical.append(payload)
    flex=v.get('parameter_flex',[])
    success=sum(bool(x.get('pass',x.get('substitution_pass',False))) for x in flex)
    measured=v['placed_bounds']['xyz_size_mm']
    text=[f'# {c["brand"]} {c["model"]}', '',f'Status: **{payload["status"]}**. Recorded {STAMP}.',
          '',f'Smartsheet row IDs: {", ".join(str(x) for x in payload["row_ids"])}.',
          f'RFA: `{payload["rfa"]}`. SHA-256: `{payload["rfa_sha256"]}`.',
          '', '## Native evidence',
          f'Revit 2025 save/reopen: PASS. Category: {v["category"]}. Placement: {v["placement_type"]}; actual test host: {v["placement"]["host_category"]}.',
          f'Actual full placed bounds (W x D x H): **{mm(measured)}**.',
          f'Comparison target (W x D x H): {mm(v["target_xyz_mm"])}.',
          f'Dimension gate: **{"PASS" if v["dimension_gate"] else "HOLD"}**; scope: {v["dimension_gate_scope"]}.',
          f'Dimension basis: {v["dimension_basis"]}',
          f'Delta against comparison target (W, D, H): {", ".join(f"{d:+.6f}" for d in v["dimension_delta_mm"])} mm.',
          f'Material parameter substitution with geometry evidence: {success}/{len(flex)}. Zero exposed parameters means the manufacturer materials remain nested/fixed, not that editability passed.',
          f'Family warnings: {len(v.get("warnings",[]))}; placed-project warnings: {len(v.get("placed_warnings",[]))}.']
    for warning in v.get('warnings',[])+v.get('placed_warnings',[]):
        text.append(f'- Warning: {warning}')
    text+=['',f'Detailed native results: `../{payload["validation"]}`.',
           'Native previews: '+', '.join('`../'+x+'`' for x in payload['previews'])+'.',
           '', '## Visual review',v.get('visual_review',{}).get('observation','Visual review not recorded.'),
           '', '## Sources and access',*['- '+u for u in source_urls],
           '', 'Manufacturer media were accessed through public product/download pages without a sign-in, new account, payment or acceptance interaction. No new redistribution license was inferred. Manufacturer copyright/terms remain applicable; this is an internal project working copy.',
           'Original RFA hashes and source records are in `source_manifest.json`. An older download manifest can describe an overwritten ZIP filename; actual retained original RFA hashes, rather than a historical ZIP pathname, establish the source artifacts.']
    if slug in custom:
        text+=['', '## Build and material dependencies',
               'Entry point: `source/build.py`; shared implementation: `../build_custom.py` and `../family_common.py`. Always invoke the entry point by absolute path through the repository serialized Revit runner.',
               'Manufacturer dimensions are fixed. Finish parameters are intended to flex. Companion uniform diffuse PNG files in `source/` are bound to appearance assets and checked after reopen. Revit stores their workstation paths; retain the source folder and relink/search that folder when relocating the family.',
               '', '## Assumptions and limitations',*['- '+a for a in c.get('assumptions',[])+c.get('limitations',[])]]
        if slug.startswith('ge_'):
            text+=['- The official 3D DWG is retained under `source/` as reference. Its audit candidate is not the delivered RFA: washer geometry is mesh-only and has a deeper envelope; dryer default units were inconsistent. The native editable family uses the published overall dimensions and image-derived face details.',
                   '- Control legends and exact molded/vent profiles are simplified; no close-up photographic equivalence is claimed.']
    else:
        text+=['', '## Assumptions and limitations',
               '- DOWNLOADED means a manufacturer model was recovered and a working Revit 2025 copy was saved/reopened. It does not mean all dimension, finish or design-identity gates passed.',
               '- Native source geometry is preserved. Some projections can be handles, panels, flanges, feet or accessories. The recorded dimensional mismatch is unresolved unless a specific component comparison proves otherwise; do not scale the model silently.',
               '- Category and hosting were normalized to Specialty Equipment / work plane placement. Missing source appearance assets were repaired from existing source colors where possible; optical fidelity is not established by that repair.',
               '- Manufacturer materials can be nested/imported. Only the material substitutions explicitly evidenced in validation.json are verified.',
               *['- '+a for a in v.get('limitations',[])]]
    row_assumptions=[ASSUMPTIONS[x] for x in payload['row_ids'] if x in ASSUMPTIONS]
    if row_assumptions:
        text+=['', '## Row identity decisions',*['- '+x for x in row_assumptions]]
    text+=['', '## Blockers and disposition',
           'No native save/reopen or placement blocker remains. Design identity, dimensional fit and material limitations above remain review holds. The section does not authorize procurement, installation or release for final visualization.', '']
    (folder/'NOTES.md').write_text('\n'.join(text),encoding='utf-8')

rows=[]
for item in items:
    row=item['row_id'];slugs=mapping[row]
    status='DOWNLOADED' if all(s in downloaded for s in slugs) else 'BUILT_WITH_LIMITATIONS'
    gates=[]
    for slug in slugs:
        v=validations[slug];f=v.get('parameter_flex',[])
        passed=sum(bool(x.get('pass',x.get('substitution_pass',False))) for x in f)
        gates.append(f'{models[slug]["model"]}: open/save/reopen/category/place/preview PASS; fit {"PASS" if v["dimension_gate"] else "HOLD"} ({v["dimension_gate_scope"]}); material {passed}/{len(f)}; warnings {len(v.get("warnings",[]))}')
    note=ASSUMPTIONS.get(row,'Exact specified or linked model retained; see canonical notes for measured fit and finish limits.')
    folder=ROOT/item['item_key'];folder.mkdir(parents=True,exist_ok=True)
    rfas=[rel(Path(validations[s]['saved_rfa'])) for s in slugs]
    record={'row_id':row,'item':item['description'],'model_slugs':slugs,'status':status,'agent_ignore':item.get('agent_ignore',False),
            'rfa_paths':rfas,'gate_results':gates,'note':note,'identity_hold':row in IDENTITY_HOLDS,
            'notes_path':rel(folder/'NOTES.md')}
    rows.append(record)
    lines=[f'# Row {row} - {item["description"]}', '',f'Status: **{status}**.',
           f'Unit / room: {item.get("unit_type")} / {item.get("room_type")}. Original Agent Ignore: {item.get("agent_ignore",False)}; this row was still processed.',
           '', '## Identity',note,
           f'Input model: {item.get("model_number")}; manufacturer: {item.get("manufacturer")}; finish: {item.get("finish")}.',
           *['Input link: '+u for u in item.get('product_urls',[])],
           '', '## Families and evidence']
    for slug in slugs:
        v=validations[slug]
        lines += [f'- RFA: `../{rel(Path(v["saved_rfa"]))}`. Native full bounds (W x D x H): {mm(v["placed_bounds"]["xyz_size_mm"])}.',
                  f'  Sources, dimensions, assumptions, warnings and blockers: [canonical notes](../{slug}/NOTES.md); [validation](../{slug}/validation.json).']
    lines+=['', '## Gate results',*['- '+g for g in gates],
            '', '## Disposition',
            'IDENTITY HOLD: description and linked model disagree; coordinator must resolve which appliance is intended.' if row in IDENTITY_HOLDS else 'Native files are available. Canonical dimensional, finish and visual limitations remain applicable.', '']
    (folder/'NOTES.md').write_text('\n'.join(lines),encoding='utf-8')

counts=collections.Counter(r['status'] for r in rows)
rollup={'generated_utc':STAMP,'inventory_rows':len(rows),'unique_models':len(canonical),'status_counts':dict(counts),
        'native_saved_reopened_placed':sum(bool(v.get('ok')) for v in validations.values()),
        'full_dimension_pass_models':[s for s,v in validations.items() if v['dimension_gate'] and v['dimension_gate_scope']=='overall'],
        'body_dimension_pass_models':[s for s,v in validations.items() if v['dimension_gate'] and v['dimension_gate_scope']=='body'],
        'dimension_hold_models':[s for s,v in validations.items() if not v['dimension_gate']],
        'identity_hold_row_ids':sorted(IDENTITY_HOLDS),'delivery_ready':False,
        'rows':rows,'canonical_models':canonical}
(ROOT/'section_manifest.json').write_text(json.dumps(rollup,indent=2),encoding='utf-8')

report=['# 1527 Wieland - Appliances section report','',f'Recorded {STAMP}.',
        '',f'**27 inventory rows processed; 21 unique native Revit 2025 working families. {counts["DOWNLOADED"]} rows are DOWNLOADED; {counts["BUILT_WITH_LIMITATIONS"]} rows are BUILT_WITH_LIMITATIONS.** Two rows contain LG washer/dryer pairs, and duplicate selections reference the same canonical family.',
        '', 'All 21 working RFAs were saved, reopened and placed in Revit 2025. All 27 rows, including the nine originally marked Agent Ignore, have individual notes. No Smartsheet write or Drive upload was performed.',
        '', '**Delivery is not released.** Five custom models pass the full published-envelope dimensional comparison; two custom models pass body dimensions only. Fourteen downloaded manufacturer models have full-envelope differences against the referenced published dimensions. Their native files are available, but those comparisons are not approved by this report.',
        '', '## Decisions and holds',
        '- The Miele KM 3054-1 G and GE GFD55GSSNWW corrections govern the obsolete row model text. The Trade-Wind I32363RC model governs conflicting vendor wording.',
        '- The cooktop casing is 53 mm high; the modeled full height is approximately 88 mm because grate height is inferred. The hood body is 330.2 mm high; modeled full height is 355.6 mm because collar extension is inferred. Neither full-height gate is represented as passed.',
        '- Three ignored rows have incompatible description-versus-URL identities: T24UR905RP refrigerator versus warming drawer; PRD48WISGU 48-inch range versus 30-inch oven; WD30W warming drawer versus Zephyr hood. Working families follow the exact URLs and remain explicit design holds. T18IW905SP and MC30WP are separately documented model-selection assumptions.',
        '- Manufacturer-family material editability is only proven for parameters with geometry evidence. Miele source materials remain nested; T24UR905RP and T42IT100NP expose unproven imported-material controls. See individual results rather than assuming downloaded content is fully parametric.',
        '', '## Row register',
        'Paths are relative to `output/1527_wieland/appliances/`. Native PASS means save/reopen, category, placement and actual exported preview; fit and material results remain separate.',
        '', '| Row ID | Item / working model | Status | RFA path | Gate results | Note |',
        '|---|---|---|---|---|---|']
for row in rows:
    short_gates=[]
    for slug in row['model_slugs']:
        v=validations[slug];flex=v.get('parameter_flex',[])
        p=sum(bool(x.get('pass',x.get('substitution_pass',False))) for x in flex)
        short_gates.append(f'{models[slug]["model"]}: Native PASS; fit {"PASS" if v["dimension_gate"] else "HOLD"}'+(' body only' if v['dimension_gate_scope']=='body' else '')+f'; material {p}/{len(flex)}; warnings {len(v.get("warnings",[]))}')
    report.append('| '+ ' | '.join([str(row['row_id']),esc(' / '.join(models[s]['model'] for s in row['model_slugs'])),row['status'],
                                  '<br>'.join('`'+x+'`' for x in row['rfa_paths']),esc('; '.join(short_gates)),esc(row['note'])])+' |')
report+=['', '## Measured canonical geometry', 'All dimensions below are millimetres, W x D x H. Values are actual placed geometry, not parameter labels.',
         '', '| Model | Measured full bounds | Comparison target | Scope / result |', '|---|---|---|---|']
for slug,v in validations.items():
    report.append('| '+' | '.join([models[slug]['model'],mm(v['placed_bounds']['xyz_size_mm']),mm(v['target_xyz_mm']),
        esc(v['dimension_gate_scope'])+' / '+('PASS' if v['dimension_gate'] else 'HOLD')])+' |')
report+=['', '## Evidence and use',
         '`section_manifest.json` maps all rows to canonical RFAs, SHA-256 hashes, notes and evidence. Every canonical folder contains `NOTES.md`, `validation.json`, `source_manifest.json`, sources and native views. Each inventory item-key folder has its own row-level `NOTES.md`.',
         'Custom build entry points are under each model `source/` directory. Manufacturer originals remain under `source/original/`. GE CAD trial RFAs are research evidence under `source/` and are not the delivered working families. Historical initial audit files are superseded by each canonical `validation.json`.',
         'Keep the companion material PNG files with the custom families when copying the package. Uniform finish maps are project visualization approximations. Imported/nested manufacturer textures and exact optical equivalence are not universally validated.',
         'The coordinator owns delivery, design identity resolution and acceptance of the listed visual/dimensional limits. No fabrication, installation-clearance or procurement acceptance is implied.', '']
(ROOT/'SECTION_REPORT.md').write_text('\n'.join(report),encoding='utf-8')
audit_path=ROOT/'artifact_audit.json'
if audit_path.exists():
    audit=read_json(audit_path)
    with (ROOT/'SECTION_REPORT.md').open('a',encoding='utf-8') as handle:
        handle.write('\nArtifact audit: %d/%d checks passed; see `artifact_audit.json`. Review holds remain in force.\n'%(audit['passed'],audit['checks']))
print(json.dumps({k:v for k,v in rollup.items() if k not in ('rows','canonical_models')},indent=2))
