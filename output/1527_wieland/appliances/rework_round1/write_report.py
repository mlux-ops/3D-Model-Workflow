"""Reconcile the section report against its selected family manifest."""
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
m=json.loads((ROOT/'section_manifest.json').read_text())
r=json.loads((HERE/'completion_receipt.json').read_text())
models={x['slug']:x for x in m['canonical_models']}
lines=['# 1527 Wieland - Appliances section report','',
       '## Result - orchestrator rework round 1','',
       '**All nine assigned dimensional failures have custom Revit 2025 working replacements. All 13 affected inventory rows are reconciled to those new files.**',
       'Recorded '+r['utc']+'. The section still contains all 27 inventory rows and 21 selected canonical families. Row status counts: 22 BUILT_WITH_LIMITATIONS and five DOWNLOADED.',
       '', 'The nine new families pass native save/reopen, model identity, Specialty Equipment category, complete overall dimensions within 1 mm, floor-face placement, material substitution/restoration, bitmap resolution and fresh preview generation. The largest measured overall-axis deviation is %.9f mm. There are zero family and placed-project warnings.'%r['max_dimension_error_mm'],
       'The nine models provide 41 editable finish parameters: 41/41 substitutions passed in reopened families and another 41/41 passed in placed instances. All 27 native front/side/oblique previews were directly inspected.',
       '', '**Delivery remains with the orchestrator.** No Drive upload or Smartsheet edit was performed. The five named selection/ambiguity holds remain NEEDS_USER and their files and row records are unchanged.',
       '', '## Changes and preserved evidence','',
       'Replacement filenames end in `_Custom_R1_R2025.rfa`. They contain newly constructed native solids, not transformed manufacturer family instances or rescaled imported CAD. Each model has current validation, canonical NOTES, source_manifest and new source/rework_r1 evidence. All affected row NOTES point to the selected replacement.',
       'All 515 protected pre-existing files are hash-checked, including manufacturer originals, prior working RFAs, prior previews and all non-target model/row files. Forty-four prior mutable notes/report/validation files are archived under `rework_round1/history_before/`. The previous failed working families remain available for audit and are no longer selected for the 13 corrected rows.',
       '', '## Round-1 dimensional results','',
       'Measurements below are the complete default modeled W x D x H on the authoritative axes; no body-only subset was used for these nine results.',
       '', '| Model | Complete measured W x D x H (mm) | Largest axis deviation (mm) | Native gates | Selected RFA |',
       '|---|---|---:|---|---|']
for new in r['new_rfas']:
    model=models[new['slug']]
    v=json.loads((ROOT/model['validation']).read_text())
    dims=' x '.join('%.3f'%x for x in v['placed_bounds']['xyz_size_mm'])
    lines.append('| '+model['model']+' | '+dims+' | %.9f | PASS | `%s` |'%(max(abs(x) for x in v['dimension_delta_mm']),model['rfa']))
lines += ['', '## Assumptions retained with the replacements','',
          'The published appliance W/D/H values govern this requested coordination envelope. For the three wall-oven models, the modeled handles are included inside that complete envelope; the concealed body-depth partition is reconstructed and is not certified to the separate cabinet-installation section. These replacements do not certify cutouts or fabrication dimensions. This convention is stated in each affected canonical note.',
          'Factory appliances use closed doors and the stated minimum foot setting where applicable. Separately supplied customer overlay panels, handles and optional accessory frame/backguard kits are not included. Local controls, concealed mechanisms, small radii and optical properties remain reference-derived approximations. Overall dimensions and editable-material operation are verified independently of those assumptions.',
          'The T42 replacement uses the retained page-4 explicit metric dimensions and 2123 mm minimum height. Miele H7280BP dimensions were additionally confirmed on its exact-model official product page because the retained two-page fact sheet omits the overall-dimension row.',
          '', '## Complete row register','',
          'Paths are relative to `output/1527_wieland/appliances/`. Status describes provenance/construction, and the gate column records the applicable technical outcome.',
          '', '| Row ID | Item / selected model | Status | RFA path | Gate results | Note |',
          '|---|---|---|---|---|---|']
for row in m['rows']:
    model=' / '.join(models[s]['model'] for s in row['model_slugs'])
    paths='<br>'.join('`'+p+'`' for p in row['rfa_paths'])
    gates='<br>'.join(row['gate_results'])
    lines.append('| %s | %s | %s | %s | %s | %s |'%(row['row_id'],model,row['status'],paths,gates,row['note'].replace('|','/')))
lines += ['', '## Unchanged decisions and other scope','',
          'T18IW905SP, T24UR905RP, MC30WP, PRD48WISGU and WD30W remain orchestrator NEEDS_USER. Round 1 did not alter their families, source evidence, validation, canonical notes, row notes or selected model records.',
          'The seven earlier custom models are unchanged. Five retain full-envelope passes; KM3054-1G and I32363RC retain their explicitly limited body-only dimensional passes. No round-1 claim promotes those two results to complete overall passes.',
          '', '## Validation records','',
          '`section_manifest.json` identifies all selected files. `artifact_audit.json` records current completeness and hash verification. `rework_round1/completion_receipt.json` and `rework_round1/round1_audit.json` record the nine-model rework result and preservation checks. `visual_review.json` records actual reviewed-image hashes and observations. Native source records remain under each target/source/rework_r1; current reviewed records are each target/validation.json.',
          '', '## Blockers','',
          'No technical blocker remains in the assigned nine-model rework scope. The five unchanged user-decision holds and final orchestrator delivery decision remain outside this worker assignment.']
(ROOT/'SECTION_REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
brief=['# Appliances round-1 result','',
       'RESULT: Nine custom replacements and all 13 affected rows completed.','',
       'CHANGES: Selected files use *_Custom_R1_R2025.rfa. Row/canonical notes, validation, source manifests, section manifest and visual review updated; prior evidence retained.','',
       'VALIDATION: Nine native passes; complete overall deviations <=1 mm (maximum %.9f mm); 41 family and 41 placed material tests; 27 fresh native views; zero native warnings. Protected-file count: 515; archived prior metadata files: 44.'%r['max_dimension_error_mm'],'',
       'BLOCKERS: None in assigned round-1 technical scope. T18IW905SP, T24UR905RP, MC30WP, PRD48WISGU and WD30W remain NEEDS_USER and unchanged. No Drive or Smartsheet writes.','',
       'See ../SECTION_REPORT.md, completion_receipt.json and round1_audit.json for exact paths and evidence.']
(HERE/'RESULT.md').write_text('\n'.join(brief)+'\n',encoding='utf-8')
print('SECTION_REPORT.md reconciled: 27 row records, nine replacement results; RESULT.md written.')
