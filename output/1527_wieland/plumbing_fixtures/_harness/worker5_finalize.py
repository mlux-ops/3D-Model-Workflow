"""Close every plumbing inventory row against immutable native evidence."""
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import os

ROOT = Path(__file__).resolve().parents[1]
MARKER = '<!-- worker5 completion -->'
ALLOWED = {'DOWNLOADED', 'AVAILABLE_LOGIN_REQUIRED+BUILT', 'BUILT', 'BUILT_WITH_LIMITATIONS', 'BLOCKED'}
SINK_IDS = {'2580485884149636', '326865367203716', '5006187243962244'}
NATIVE_NEW = {'62820LF-BL', '63221LF-BLLHP', '873111-BNX-2.5'}
HOLDS = {
    '700337000000090': ('NEEDS_USER_DURAVIT_700337_HEIGHT_SCOPE',
        'Manufacturer envelope is 1700.000 x 900.000 x 531.042 mm. Length and width pass; authoritative overall height/body-versus-accessory scope is unresolved. Confirm the height convention and exact 700337000000090 suffix scope before release.'),
    'MS642124CEFG_01': ('NEEDS_USER_TOTO_NEXUS_DIMENSION_AND_LEVER',
        'Manufacturer width is 451.348 mm versus 444.500 mm (+6.848 mm). Flush Lever Finish is writable but its substitution does not reach faces. Dimension and material gates remain false; source geometry has not been scaled.'),
    'SS124_01': ('NEEDS_USER_TOTO_SS124_ENVELOPE',
        'Manufacturer seat envelope is 355.658 x 513.772 x 122.104 mm versus 355.600 x 473.075 x 46.038 mm. Depth +40.697 mm and height +76.067 mm include hinge/rod extents; reconcile seat-body and accessory scope before release.'),
    '443306': ('NEEDS_USER_BLANCO_443306_FINISH',
        'Exact manufacturer SKU 443306 is White; the inventory requests Black. The saved Black family is an explicitly unresolved visual variant. Confirm finish/SKU; no replacement identity has been selected.'),
    '240328': ('NEEDS_USER_BLANCO_240328_FINISH',
        'Exact manufacturer SKU 240328 is White; the inventory requests Black. The saved Black flange is an explicitly unresolved visual variant with inferred secondary dimensions. Confirm finish/SKU before release.'),
    '32526141': ('NEEDS_USER_32526141_IDENTITY_SCOPE',
        'Exact SKU 32526141 is Metropol wall faucet trim, although the inventory describes a rough-in. The saved family represents trim; required rough 13622181 is not included. Confirm row identity/scope and the inferred 8-inch centers.'),
    'THU842_01-A': ('NEEDS_USER_THU842_DIMENSIONS',
        'Button and rod dimensions are inferred from the illustrated relationship to the known tank. Native agreement with configured geometry does not verify manufacturer dimensions. Confirm actual dimensions or approve this limited representation.'),
    'TD954-20LT': ('NEEDS_USER_TD954_20LT_SUFFIX',
        'Base TD954 is verified in the preserved manufacturer evidence; the exact -20LT suffix was not independently established. Confirm the scheduled package identity before release.'),
    'BT062415-BNX': ('NEEDS_USER_BT062415_GRATE_IDENTITY',
        'The current manufacturer description calls BT062415 Tile-In, while the dimensioned Rev C sheet depicts a slotted grate. The family follows Rev C. Confirm the purchased grate/trim configuration.'),
    '80019-ISE': ('NEEDS_USER_80019_ISE_PACKAGE',
        'The preserved current manufacturer page redirects Power .75 to package SKU 81222K. The family retains scheduled legacy package 80019-ISE. Confirm the intended package identity before release.'),
}

VISUAL = {
    '62820LF-BL': {
        'review': 'Native oblique and side images inspected: wall flange, two swivel stages, two downward paddles and downward outlet are visible. Simplified collars and paddles remain disclosed.',
        'source_review': 'Manufacturer BSP-K-62810LF Rev N page 1 screenshot inspected, including the 62820 lever detail. The dimensioned drawing is the chosen authority for 20.375-inch full projection and 19.25-inch outlet reach.',
        'additional_limitations': ['ASSUMPTION: use the explicit Rev N drawing rather than the undifferentiated 22-inch reach on the current product page. The 9.25-inch posed height includes a drawing-derived downward handle; it is not the product-page 6.5-inch body-height value.'],
        'sources': ['https://media.brizo.com/SpecSheet/BSP-K-62810LF%20Rev%20N.pdf', 'https://www.brizo.com/kitchen/product/62820LF-BL'],
    },
    '63221LF-BLLHP': {
        'review': 'Native oblique and side images inspected: two articulated arms, wand, separate hose, base and less-handle spindle are visible. Pose and rigid simplified sections remain limitations.',
        'source_review': 'Current official product page links BSP-K-63121LF-LHP Rev B. Rev B parsed successfully but its screenshot returned cache miss. Manufacturer Rev A, linked by a supplier, was successfully viewed as a PDF screenshot; the relevant 2.4375/6.75/5.875/4.75/21.5-inch and 23-inch hose callouts match Rev B text. Rev A is used only for visual corroboration.',
        'additional_limitations': ['ASSUMPTION: retain the documented fixed pose at 21.75-inch outer hose height and exactly 23-inch native hose path. It is not a verified manufacturer overall height. The current product page states 19.875 inches, while its linked drawing depicts 21.5 inches and states height varies with arm position. Resolve pose/clearance convention during visual review.'],
        'sources': ['https://media.brizo.com/SpecSheet/BSP-K-63121LF-LHP%20Rev%20B.pdf', 'https://media.brizo.com/SpecSheet/BSP-K-63121LF-LHP%20Rev%20A.pdf', 'https://www.brizo.com/kitchen/product/63221LF-BLLHP'],
    },
    '873111-BNX-2.5': {
        'review': 'Native oblique and side images inspected: round wall flange, asymmetric pivot/arm, inclined cylinder and recessed nozzle disk are present. Fixed 45-degree pose and simplified hardware remain disclosed.',
        'source_review': 'Manufacturer BSP-B-873111 Rev A page 1 screenshot inspected. Cylinder/flange diameter 4.75 inches, cylinder length 7.75 inches and full thread-to-head envelope 16 inches are the selected drawing authority.',
        'additional_limitations': ['ASSUMPTION: use the explicit 873111 title/model drawing even though standard-specification body text names 873110. The 16-inch total includes the assumed 1.5-inch concealed stub; it is not a finished-wall projection.'],
        'sources': ['https://media.brizo.com/SpecSheet/BSP-B-873111%20Rev%20A.pdf'],
    },
}


def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(path):
    return Path(path).resolve().relative_to(ROOT.resolve()).as_posix()


def output(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    text = value if isinstance(value, str) else json.dumps(value, indent=2, ensure_ascii=True) + '\n'
    if path.exists() and path.suffix == '.md' and MARKER not in path.read_text(encoding='utf-8-sig'):
        raise RuntimeError('Existing authored document must be preserved: ' + str(path))
    path.write_text(text, encoding='utf-8')


def cell(value):
    return str(value if value is not None else '-').replace('|', '\\|').replace('\r', ' ').replace('\n', ' ')


def link(label, section_path, from_folder=None):
    destination = ROOT / section_path
    href = os.path.relpath(destination, from_folder or ROOT).replace('\\', '/')
    return '[' + cell(label) + '](<' + href + '>)'


def number(value):
    return 'unresolved' if value is None else ('%.4f' % value).rstrip('0').rstrip('.')


def dimensions(data):
    actual = data['actual_dimensions_after_reopen_mm']
    expected = data.get('expected_dimensions_mm')
    if expected is None:
        expected = [v * 25.4 for v in data['expected_dimensions_in']]
    return [{'axis': a, 'actual_mm': x, 'target_mm': y, 'delta_mm': None if y is None else x-y,
             'within_1mm': None if y is None else abs(x-y) <= 1.0}
            for a, x, y in zip('XYZ', actual, expected)]


def group_record(group):
    key = group['key']
    validation_path = ROOT / key / 'validation.json'
    v = load(validation_path)
    spec_path = ROOT / key / 'source/model_spec.json'
    spec = load(spec_path) if spec_path.exists() else {}
    downloaded = v.get('source_kind') == 'MANUFACTURER_RFA'
    search = v.get('rfa_search') or spec.get('rfa_search') or {'result': 'Public manufacturer family recovered', 'url': v.get('source_url')}
    status = 'DOWNLOADED' if downloaded else ('AVAILABLE_LOGIN_REQUIRED+BUILT' if search.get('result') == 'AVAILABLE_LOGIN_REQUIRED' else 'BUILT_WITH_LIMITATIONS')
    assert downloaded or v.get('native_gates_pass'), 'Unresolved native build: ' + key
    rfa = Path(v['rfa_path'])
    assert rfa.is_file(), str(rfa)
    sources = list(v.get('source_references') or spec.get('sources') or [])
    if downloaded:
        sources += [{'url': v.get('source_url'), 'document': 'Public manufacturer RFA'}, {'url': v.get('spec_url'), 'document': 'Manufacturer dimensional reference'}]
    sources += [{'url': url, 'document': 'Worker-5 source cross-check'} for url in VISUAL.get(key, {}).get('sources', [])]
    evidence = []
    for filename in v['evidence_files']:
        path = Path(filename)
        path = path if path.is_absolute() else ROOT / key / 'evidence' / path
        assert path.is_file(), str(path)
        evidence.append({'path': relative(path), 'sha256': sha(path)})
    limitations = list(v.get('limitations') or spec.get('limitations') or [])
    limitations += VISUAL.get(key, {}).get('additional_limitations', [])
    if downloaded:
        limitations.append('Original manufacturer geometry retained in its separate Revit 2025 copy; documented failed source gates remain holds. No source geometry was scaled to force agreement.')
    holds = [{'code': HOLDS[key][0], 'detail': HOLDS[key][1]}] if key in HOLDS else []
    return {
        'key': key, 'model': group['sku'], 'manufacturer': spec.get('manufacturer') or group['rows'][0].get('manufacturer'),
        'row_ids': [str(row['row_id']) for row in group['rows']], 'status': status,
        'native_gates_pass': bool(v.get('native_gates_pass')), 'technical_pass': bool(v.get('technical_pass')),
        'release_ready': False, 'release_review': 'PENDING_ORCHESTRATOR_REVIEW', 'holds': holds,
        'rfa_path': relative(rfa), 'rfa_sha256': sha(rfa), 'rfa_bytes': rfa.stat().st_size,
        'validation_path': relative(validation_path), 'validation_sha256': sha(validation_path),
        'source_spec_path': relative(spec_path) if spec else None, 'source_spec_sha256': sha(spec_path) if spec else None,
        'source_spec_hash_matches': sha(spec_path) == v.get('source_spec_sha256') if spec else None,
        'build_script': key + '/source/build.py' if spec else '_harness/inspect_downloaded_families.py',
        'source_reference': v.get('source_reference'), 'source_kind': 'MANUFACTURER_RFA' if downloaded else 'CUSTOM_NATIVE_FAMILY',
        'source_search': search, 'sources': sources,
        'source_version': v.get('manufacturer_original_format'), 'saved_version': v.get('saved_format') or v.get('revit_version'),
        'revit_build': v.get('revit_build'), 'last_verified_stage': v.get('stage'), 'native_finished_utc': v.get('finished_utc'),
        'category': v.get('category'), 'selected_type': v.get('selected_type') or v.get('type'),
        'placement': v.get('placement'), 'host': v.get('host'), 'gates': v.get('gates'),
        'dimensions': dimensions(v), 'all_overall_dimensions_authoritative': bool(v.get('all_overall_dimensions_authoritative')),
        'dimension_authority': v.get('source_dimensions') or spec.get('dimension_authority') or [],
        'dimension_anchor_checks': v.get('dimension_anchor_checks') or [], 'native_path_checks': v.get('native_path_checks') or [],
        'material_tests': v.get('material_tests') or {}, 'appearance_bindings': v.get('appearance_bindings') or {},
        'family_warnings': v.get('family_warnings') or [], 'reopened_warnings': v.get('reopened_warnings') or [],
        'project_warnings': v.get('project_warnings') or [], 'evidence': evidence, 'limitations': limitations,
        'visual_review': 'NATIVE_OBLIQUE_AND_SIDE_INSPECTED_WITH_LIMITATIONS' if key in VISUAL else 'PENDING_ORCHESTRATOR_VISUAL_REVIEW',
        'visual_observations': VISUAL.get(key),
    }


def notes(row, result, group):
    folder = ROOT / row['item_key']
    lines = [MARKER, '# Plumbing fixture row ' + str(row['row_id']), '', '**Final status: ' + result['status'] + '**', '',
             '## Identity and scope', '',
             '- Row ID: `' + str(row['row_id']) + '`; item key: `' + row['item_key'] + '`.',
             '- Scheduled product: ' + cell(row.get('manufacturer')) + ' / ' + cell(row.get('model_number')) + '.',
             '- Scheduled description: ' + cell(row.get('description')) + '.',
             '- Scheduled finish: ' + cell(row.get('finish')) + '; unit: ' + cell(row.get('unit_type')) + '; room: ' + cell(row.get('room_type')) + '.',
             '- Original agent_ignore: `' + str(bool(row.get('agent_ignore'))).lower() + '`. Coverage does not reinstate an ignored or descoped product.', '',
             'Original source note: ' + (row.get('source_notes') or 'None recorded.') + '', '',
             '## Source and last verified stage', '']
    if not group:
        lines += ['Inventory evidence: ' + link('ITEMS.json', 'ITEMS.json', folder) + '.',
                  'Last verified stage: inventory identity review; no selected product, source family, dimensions or native geometry.', '',
                  '## Assumptions and blockers', '', result['disposition'], '',
                  'ASSUMPTION: ' + ('An unspecified sink is not interchangeable with a selected sink elsewhere in the project.' if result['row_id'] in SINK_IDS else 'This row is an organizational label, not an independently modelable fixture. BLOCKED is the permitted status for a non-buildable inventory row; no user selection is needed for this header.'), '',
                  'Native gates: not applicable until a product identity exists. RFA: none.', '',
                  'Hold: ' + (result['holds'][0]['code'] if result['holds'] else 'ADMINISTRATIVE_NONPRODUCT; no action needed.')]
        return '\n'.join(lines) + '\n'
    lines += ['Shared product group: `' + group['key'] + '`. The same exact scheduled product reuses one validated family across its inventory rows.',
              'RFA: ' + link(group['rfa_path'], group['rfa_path'], folder) + '.',
              'RFA SHA-256: `' + group['rfa_sha256'] + '`.',
              'Validation: ' + link('validation.json', group['validation_path'], folder) + '; last verified stage: `' + group['last_verified_stage'] + '`.',
              'Saved Revit version: ' + str(group['saved_version']) + '; build: ' + str(group['revit_build']) + '; native evidence finished: ' + str(group['native_finished_utc']) + '.',
              'Source RFA input version: ' + str(group['source_version'] or 'Native custom build') + '.',
              'RFA search result: ' + cell(group['source_search'].get('result')) + '. This records recovered evidence, not a claim that no other family exists.',
              'Search evidence: ' + json.dumps(group['source_search'], ensure_ascii=True) + '.',
              'Access/terms note: the preserved workflow used public sources without account sign-in or license acceptance. No new account or terms acceptance was performed in this continuation; redistribution permission is not established by public access.', '',
              'Source/spec references:']
    seen = set()
    for source in group['sources']:
        url = source.get('url')
        if url and url not in seen:
            lines += ['- ' + source.get('document', 'Manufacturer reference') + ': ' + url + (('; page ' + str(source['page'])) if source.get('page') else '') + '.']
            seen.add(url)
    lines += ['', '## Dimensions checked', '',
              'Values below are local X/Y/Z extents after saving, closing and reopening, measured from native geometry. For wall fixtures Y is vertical and Z is projection; for floor/deck fixtures Z is vertical. The comparison tolerance is 1 mm.', '',
              '| Axis | Actual mm | Target mm | Delta mm | Within 1 mm |', '|---|---:|---:|---:|---|']
    for d in group['dimensions']:
        lines += ['| ' + d['axis'] + ' | ' + number(d['actual_mm']) + ' | ' + number(d['target_mm']) + ' | ' + number(d['delta_mm']) + ' | ' + ('UNRESOLVED' if d['within_1mm'] is None else ('PASS' if d['within_1mm'] else 'FAIL')) + ' |']
    lines += ['', 'All overall dimensions have manufacturer authority: **' + str(group['all_overall_dimensions_authoritative']).lower() + '**. Where false, a configured-envelope pass verifies the reconstruction, not an independently published overall size.', '']
    for authority in group['dimension_authority']:
        lines += ['- ' + authority]
    for check in group['dimension_anchor_checks'] + group['native_path_checks']:
        lines += ['- Native anchor/path: ' + str(check.get('label') or check.get('part')) + ', measured ' + number(check.get('actual_mm')) + ' mm; nominal ' + number(check.get('nominal_mm')) + ' mm; ' + ('PASS' if check.get('pass') else 'FAIL') + '.']
    lines += ['', '## Native gates and parameters', '',
              'Native gate result: **' + ('PASS' if group['native_gates_pass'] else 'HOLD') + '**. Category: ' + str(group['category']) + '; selected type: ' + str(group['selected_type']) + '; placement: ' + str(group['placement']) + '.',
              'Gate details: ' + json.dumps(group['gates'], sort_keys=True) + '.',
              'Host evidence: ' + json.dumps(group['host'], sort_keys=True) + '.',
              'Finish parameter substitution is the tested flex operation. Fixed-dimension custom geometry is not an operational/articulating or general size-flex family.', '',
              '| Material parameter | Writable | Substitution reaches faces |', '|---|---|---|']
    for label, test in sorted(group['material_tests'].items()):
        lines += ['| ' + cell(label) + ' | ' + str(test.get('writable')) + ' | ' + str(test.get('substitution_reaches_faces')) + ' |']
    lines += ['', 'Warnings (family / reopened / placed project): ' + json.dumps([group['family_warnings'], group['reopened_warnings'], group['project_warnings']]) + '.',
              'Build/inspection script: ' + link(group['build_script'], group['build_script'], folder) + '.',
              'Visual review: ' + group['visual_review'] + '. Final release is pending orchestrator review.', '']
    for evidence in group['evidence']:
        lines += ['- ' + link(Path(evidence['path']).name, evidence['path'], folder)]
    if group['visual_observations']:
        lines += ['', group['visual_observations']['review'], '', group['visual_observations']['source_review']]
    lines += ['', '## Assumptions and limitations', '']
    lines += ['- ' + limitation for limitation in group['limitations']]
    lines += ['', '## Blockers and release', '']
    lines += ['- ' + hold['code'] + ': ' + hold['detail'] for hold in group['holds']]
    if not group['holds']:
        lines += ['No additional identity-specific NEEDS_USER hold is recorded. Inferred geometry/finish fidelity still requires orchestrator review.']
    lines += ['', 'Release ready: **false**. Acquisition/build status does not override failed source gates, assumptions, scope exclusions or final visual review.']
    return '\n'.join(lines) + '\n'


def main():
    inventory = load(ROOT / 'ITEMS.json')
    groups = load(ROOT / '_research/groups.json')
    baseline = load(ROOT / '_harness/worker5_takeover_baseline.json')
    assert sha(ROOT / 'ITEMS.json') == baseline['inventory_sha256']
    assert sha(ROOT / '_research/groups.json') == baseline['groups_sha256']
    by_row = {str(r['row_id']): g for g in groups for r in g['rows']}
    records = {g['key']: group_record(g) for g in groups if g['sku']}
    assert len(records) == 71 and sum(g['native_gates_pass'] for g in records.values()) == 68
    for old in baseline['groups']:
        if old['validation_exists']:
            current = records[old['key']]
            assert current['validation_sha256'] == old['validation_sha256'], 'Prior validation changed: ' + old['key']
            assert current['rfa_sha256'] == old['rfa_sha256'], 'Prior RFA changed: ' + old['key']
            assert current['source_spec_sha256'] == old['spec_sha256'], 'Prior spec changed: ' + old['key']
    results = []
    for row in inventory['items']:
        row_id = str(row['row_id'])
        raw_group = by_row[row_id]
        group = records.get(raw_group['key']) if raw_group['sku'] else None
        if group:
            disposition = 'Native PASS; inferred details and source/visual review limits apply.' if group['native_gates_pass'] else 'Manufacturer candidate; native source gate HOLD.'
            if group['holds']:
                disposition = group['holds'][0]['code'] + ': ' + group['holds'][0]['detail']
            result = {'row_id': row_id, 'item_key': row['item_key'], 'group_key': group['key'], 'status': group['status'],
                      'rfa_path': group['rfa_path'], 'native_gates_pass': group['native_gates_pass'],
                      'holds': group['holds'], 'disposition': disposition}
        else:
            is_sink = row_id in SINK_IDS
            disposition = 'Unselected sink: manufacturer, model, dimensions and finish are absent; product selection is required.' if is_sink else 'Organizational header retained for complete row coverage; no independent fixture or user selection is required.'
            holds = [{'code': 'NEEDS_USER_SELECT_SINK_' + row_id, 'detail': (row.get('unit_type') or '') + ' / ' + (row.get('room_type') or '') + ': ' + disposition}] if is_sink else []
            result = {'row_id': row_id, 'item_key': row['item_key'], 'group_key': None, 'status': 'BLOCKED', 'rfa_path': None,
                      'native_gates_pass': None, 'holds': holds, 'disposition': disposition,
                      'blocker_kind': 'MISSING_PRODUCT_SELECTION' if is_sink else 'ADMINISTRATIVE_NONPRODUCT'}
        result.update(notes_path=row['item_key'] + '/NOTES.md', agent_ignore=bool(row.get('agent_ignore')), release_ready=False,
                      unit_type=row.get('unit_type'), room_type=row.get('room_type'), model_number=row.get('model_number'), description=row.get('description'))
        assert result['status'] in ALLOWED
        output(ROOT / result['notes_path'], notes(row, result, group))
        result['notes_sha256'] = sha(ROOT / result['notes_path'])
        results.append(result)
    count = Counter(row['status'] for row in results)
    group_count = Counter(group['status'] for group in records.values())
    now = datetime.now(timezone.utc).isoformat()
    manifest = {'schema': 'plumbing_completion_v1', 'generated_utc': now, 'section': 'Plumbing Fixtures',
                'inventory_sha256': sha(ROOT / 'ITEMS.json'), 'group_inventory_sha256': sha(ROOT / '_research/groups.json'),
                'coverage_complete': True, 'release_ready': False, 'row_count': len(results), 'row_status_counts': dict(count),
                'product_groups': len(records), 'group_status_counts': dict(group_count), 'product_rows': sum(bool(r['group_key']) for r in results),
                'native_pass_groups': sum(g['native_gates_pass'] for g in records.values()),
                'manufacturer_hold_groups': [k for k, g in records.items() if not g['native_gates_pass']],
                'administrative_header_rows': sum(r.get('blocker_kind') == 'ADMINISTRATIVE_NONPRODUCT' for r in results),
                'unselected_sink_rows': sum(r.get('blocker_kind') == 'MISSING_PRODUCT_SELECTION' for r in results),
                'rows': results, 'groups': list(records.values()),
                'preservation': {'existing_validations_unchanged': 68, 'existing_rfas_unchanged': 68, 'existing_specs_unchanged': 65},
                'native_continuation': load(ROOT / '_harness/batch_current.json')}
    output(ROOT / 'FINAL_STATUS.json', manifest)
    output(ROOT / '_review/WORKER5_VISUAL_REVIEW.json', {'generated_utc': now, 'scope': 'Three newly completed native families; source corroboration and disclosed pose limitations.', 'items': VISUAL})
    hold_register = []
    for group in records.values():
        for hold in group['holds']:
            hold_register.append(dict(hold, group_key=group['key'], row_ids=group['row_ids']))
    for result in results:
        if result.get('blocker_kind') == 'MISSING_PRODUCT_SELECTION':
            hold_register.append(dict(result['holds'][0], group_key=None, row_ids=[result['row_id']]))
    output(ROOT / 'NEEDS_USER_HOLDS.json', {'generated_utc': now, 'holds': hold_register,
        'general_review': 'Orchestrator must review the native previews and all limitations before delivery; no final visual release is implied.'})
    report = [MARKER, '# 1527 Wieland - Plumbing Fixtures', '', '## RESULT', '',
        'All **178 inventory rows** have a final status and individual NOTES.md. The 160 product rows map to **71 current RFA families** and 71 measured validation records. **68** custom families pass their recorded native gates; **3** manufacturer families retain explicit native/source holds.', '',
        '**Coverage complete: true. Release ready: false.** Completion means every row was processed and its evidence/limitations recorded; it does not mean all products satisfy every manufacturer dimension or final visual acceptance.', '',
        'The 18 BLOCKED no-SKU rows comprise **15 organizational headers** requiring no product selection and **3 unspecified sinks** requiring selection. Headers are not counted as unresolved fixture selections.', '',
        '| Final status | Inventory rows | Product groups |', '|---|---:|---:|']
    for status in ['DOWNLOADED', 'AVAILABLE_LOGIN_REQUIRED+BUILT', 'BUILT', 'BUILT_WITH_LIMITATIONS', 'BLOCKED']:
        report.append('| ' + status + ' | ' + str(count[status]) + ' | ' + str(group_count[status]) + ' |')
    report += ['', 'Status interpretation: DOWNLOADED records manufacturer acquisition, including the three held candidates. AVAILABLE_LOGIN_REQUIRED+BUILT records the protected-source discovery plus completed fallback family; its listed custom limitations still apply. BUILT_WITH_LIMITATIONS records fixed visualization geometry, inferred details and any identity/source holds. BLOCKED retains every non-buildable inventory row.', '',
        '## CHANGES', '',
        'Completed only 62820LF-BL, 63221LF-BLLHP and 873111-BNX-2.5 through the assigned shared Revit runner. Preserved the existing 68 RFA/validation pairs and 65 model specifications byte-for-byte. Previous harness queue/index/batch evidence is archived under `_harness/worker5_history/`. Raw ITEMS.json and groups.json are unchanged.', '',
        'Created 178 row notes, FINAL_STATUS.json, NEEDS_USER_HOLDS.json and the new-family visual review record. No Smartsheet edits, Drive uploads, project-model loads or product substitutions were made.', '',
        '## VALIDATION', '',
        'The new shared-lock run waited 22 seconds, then exited 0 after 40 seconds; its item-level native results all passed. Native batch timestamps: 2026-10-02T16:07:05.484Z through 16:07:29.709Z. Native save/reopen, category, face placement, orientation, material substitution, warning, configured-envelope and applicable anchor/path checks are recorded in each validation.json.', '',
        '| Newly completed family | Reopened local X / Y / Z, mm | Additional measured check |', '|---|---|---|']
    extra = {'62820LF-BL': 'Full projection 517.525 mm', '63221LF-BLLHP': 'Base diameter 61.9125 mm; hose path 584.2 mm (23 inches)', '873111-BNX-2.5': 'Head diameter 120.6500 mm'}
    for key in sorted(NATIVE_NEW):
        g = records[key]
        report += ['| ' + key + ' | ' + ' / '.join(number(d['actual_mm']) for d in g['dimensions']) + ' | ' + extra[key] + ' |']
    report += ['', 'The new native oblique and side previews were inspected. Articulation is represented as a fixed pose; no joint operation is claimed. The Odin 21.75-inch posed hose crown is an assumption, with its exact 23-inch path independently measured. The pot-filler drawing controls over the conflicting short product-page dimension text. Roccesco projection includes the disclosed concealed stub.', '',
        'Configured dimensions and manufacturer dimensions are distinguished in every note. `all_overall_dimensions_authoritative=false` is not promoted to manufacturer compliance merely because configured geometry passes. Manufacturer holds retain their false gates.', '',
        'Final machine audit: `_harness/worker5_completion_audit.json` checks every row, status, notes/report linkage, current RFA and validation hash, saved format, evidence image and active custom texture reference. Existing validation visual-review flags are preserved; the separate `_review/WORKER5_VISUAL_REVIEW.json` records this continuation\'s actual inspections.', '',
        '## BLOCKERS / NEEDS_USER', '']
    for h in hold_register:
        report += ['- **' + h['code'] + '** - ' + h['detail'] + ' Rows: ' + ', '.join('`' + rid + '`' for rid in h['row_ids']) + '.']
    report += ['', 'These are explicit identity/dimension decisions for orchestrator review. All other disclosed inferences, source-access limitations and native previews remain part of the required review before release. Agent-ignore and descoped inventory notes remain authoritative for procurement/install scope.', '',
        '## Row-by-row results', '',
        '| Row ID | Item | Final status | RFA path | Gate results | One-line note |',
        '|---|---|---|---|---|---|']
    for r in results:
        group = records.get(r['group_key'])
        gate = ('Native PASS; source/visual limits' if group and group['native_gates_pass'] else 'Native HOLD: ' + ', '.join(k for k, v in group['gates'].items() if not v)) if group else 'No selected product; no native gate'
        item = (group['model'] if group else r['description']) + ' - ' + (r['unit_type'] or '') + ' / ' + (r['room_type'] or '')
        rfa = link(r['rfa_path'], r['rfa_path']) if r['rfa_path'] else '-'
        report += ['| ' + r['row_id'] + ' | ' + link(item, r['notes_path']) + ' | ' + r['status'] + ' | ' + rfa + ' | ' + cell(gate) + ' | ' + cell(r['disposition']) + ' |']
    report += ['', 'Detailed dimensions, source URLs, license/access observations, material flex results, assumptions, original source notes and blockers are in each linked NOTES.md. Exact row and group records are in FINAL_STATUS.json.']
    output(ROOT / 'SECTION_REPORT.md', '\n'.join(report) + '\n')
    print(json.dumps({'rows': len(results), 'row_status_counts': dict(count), 'group_status_counts': dict(group_count), 'explicit_holds': len(hold_register), 'native_pass_groups': 68, 'preserved_pairs': 68}))


if __name__ == '__main__':
    main()
