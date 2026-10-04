"""Freeze round-0 evidence and prepare only the nine authorized replacements."""
from pathlib import Path
import datetime
import hashlib
import json
import shutil
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
TARGETS = ['miele_h7280bp','miele_h7270bm','miele_g5051scvi',
           'miele_kwt6722is','miele_kwtus7172f','miele_kfmc3858fd',
           'thermador_t42it100np','thermador_podmc301w','thermador_pcg486wd']
stamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
manifest = json.loads((ROOT/'section_manifest.json').read_text(encoding='utf-8'))
baseline = HERE/'baseline.json'
if not baseline.exists():
    mutable = [ROOT/n for n in ['section_manifest.json','SECTION_REPORT.md','artifact_audit.json','visual_review.json']]
    protected = []
    for model in manifest['canonical_models']:
        folder = ROOT/model['slug']
        if model['slug'] in TARGETS:
            mutable += [folder/n for n in ['validation.json','NOTES.md','source_manifest.json']]
            protected += [p for p in folder.rglob('*') if p.is_file() and p not in mutable]
        else:
            protected += [p for p in folder.rglob('*') if p.is_file()]
    for row in manifest['rows']:
        p = ROOT/row['notes_path']
        (mutable if any(s in TARGETS for s in row['model_slugs']) else protected).append(p)
    history = HERE/'history_before'
    for p in mutable:
        dst = history/p.relative_to(ROOT)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p,dst)
    frozen = {'utc':stamp,'targets':TARGETS,'mutable_before':{
        p.relative_to(ROOT).as_posix():sha(p) for p in mutable},
        'protected_files':{p.relative_to(ROOT).as_posix():sha(p) for p in protected},
        'original_manifest':manifest}
    baseline.write_text(json.dumps(frozen,indent=2),encoding='utf-8')
else:
    frozen = json.loads(baseline.read_text(encoding='utf-8'))
    manifest = frozen['original_manifest']

targets = {x['slug']:x for x in json.loads((ROOT/'downloaded_models.json').read_text())}
kinds = dict(zip(TARGETS,['miele_oven','miele_oven','dishwasher','wine_tall','wine_under','fridge','fridge','double_oven','rangetop']))
pages = dict(zip(TARGETS,[None,2,2,2,2,2,4,1,1]))
palette = {
    'Metal Finish':[[165,168,170],0.55,0.0],
    'Black Finish':[[24,26,28],0.45,0.0],
    'Glass Finish':[[30,35,38],0.9,0.18],
    'Clear Glass Finish':[[188,202,205],0.9,0.72],
    'Panel Finish':[[152,149,141],0.24,0.0],
    'Wood Finish':[[174,143,98],0.2,0.0],
    'Grate Finish':[[37,38,38],0.08,0.0],
    'Interior Finish':[[78,81,83],0.2,0.0],
    'Display Finish':[[66,75,80],0.6,0.0]}
configs=[]
for slug in TARGETS:
    original = next(m for m in manifest['canonical_models'] if m['slug']==slug)
    c = dict(targets[slug])
    folder = ROOT/slug/'source'/'rework_r1'
    folder.mkdir(parents=True,exist_ok=True)
    c.update(kind=kinds[slug],rfa_name=slug+'_Custom_R1_R2025.rfa',
             source_page=pages[slug],source_pdf=str(ROOT/slug/'source'/'product_sheet.pdf'),
             source_pdf_sha256=sha(ROOT/slug/'source'/'product_sheet.pdf'),
             source_urls=original['source_urls'],row_ids=original['row_ids'],
             replacement_reason='Orchestrator round 1: exact-identity manufacturer working family fails the <=1 mm complete overall dimension gate. New native custom geometry replaces the working selection; OEM originals and prior working RFA remain preserved.',
             axis_convention='X width, Y front-to-back depth, Z vertical height; millimetres.',
             dimension_gate_scope='overall',
             declared_limitations=['Fixed manufacturer model size; exposed finish parameters are flex-tested.',
                 'Internal partitions, edge radii, controls and concealed mechanisms are reference-derived visualization approximations.'],
             palette=palette,prepared_utc=stamp)
    if c['kind'] in ('miele_oven','double_oven'):
        c['declared_limitations'].append('Published nominal appliance W/D/H is the requested complete coordination envelope. Handles are included inside this envelope; the concealed case-depth partition is reconstructed rather than certified to the separate installation section. This family is not a cabinet-cutout or manufacturing authority.')
        c['handle_projection_mm']=66.675 if c['kind']=='double_oven' else 45.0
    if c['kind'] in ('dishwasher','fridge','wine_tall','wine_under'):
        c['declared_limitations'].append('Default envelope represents the factory appliance without separately supplied customer overlay panels or handles. Panel Finish changes the represented factory front; it does not certify an overlay thickness or panel shop drawing.')
    if slug=='thermador_t42it100np':
        c['dimension_basis']='Retained September 2026 manufacturer drawing, page 4: explicit metric W1048 x D608 x H2123 mm with leveling feet at minimum. Drawing metric values govern inconsistent rounded inch equivalents.'
    if slug=='miele_h7280bp':
        c['dimension_basis']='Official exact-model Miele product page, Technical data: W757 x H727 x D626 mm, checked 2026-10-02; retained two-page fact sheet omits this overall row.'
        (folder/'supplemental_dimension_evidence.md').write_text(
            '# H 7280 BP dimension authority\n\nChecked 2026-10-02.\n\n'
            'https://www.mieleusa.com/product/11968200/30-inch-convection-oven-h-7280-bp-obsidian-black\n\n'
            'Exact model H 7280 BP; material number 11968200; Obsidian Black. Technical data states appliance dimensions W757 x H727 x D626 mm. These are appliance dimensions, distinct from niche W724 x H718 x D610 mm. Explicit metric values govern this replacement. The retained two-page fact sheet remains unchanged.\n',encoding='utf-8')
    c['reference_check']={'method':'Retained manufacturer product text and native reference imagery, plus official exact-model web evidence for H7280BP and page-4 T42 metric drawing text.','pages':pages[slug]}
    (folder/'config.json').write_text(json.dumps(c,indent=2),encoding='utf-8')
    for pname,(rgb,gloss,trans) in palette.items():
        Image.new('RGB',(16,16),tuple(rgb)).save(folder/(pname.replace(' ','_')+'.png'))
    entry = "# -*- coding: utf-8 -*-\nimport os, sys\nsection=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))\nsys.path.insert(0,os.path.join(section,'rework_round1'))\nfrom native_rebuild import build_one\nbuild_one(%r,__revit__.Application)\n" % slug
    (ROOT/slug/'source'/'build.py').write_text(entry,encoding='utf-8')
    configs.append(c)
(HERE/'configs.json').write_text(json.dumps(configs,indent=2),encoding='utf-8')
(HERE/'ACTIVE_TASK.md').write_text('# Appliances round 1\n\nNine custom replacements authorized. Prior metadata frozen in history_before; all prior RFA/source bytes protected by baseline.json.\n\nPhase: preparing native geometry. All Revit operations use the shared revit_run.py/revit.lock. Scope and row ids are in configs.json. Five user-decision holds and seven earlier custom models are untouched.\n',encoding='utf-8')
print(json.dumps({'models':len(configs),'affected_rows':sum(len(c['row_ids']) for c in configs),
                  'protected_files':len(frozen['protected_files']),'snapshot_files':len(frozen['mutable_before'])}))
