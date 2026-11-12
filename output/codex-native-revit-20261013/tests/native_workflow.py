"""Native acceptance runner. Requires loaded isolated add-in; never targets a production document.

Every step stores its original UUID and receipt before continuing. Resume reconciles;
failed mutations require a fresh separately named test run, never blind replay.
"""
import argparse
import json
import math
from pathlib import Path
import sys
import time
import uuid

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'controller'))
from native_revit import Client, MCPServer

def payload(receipt):
    value = receipt.get('result')
    if isinstance(value, dict):
        return value.get('data', value.get('result', value))
    return value


class Run:
    def __init__(self, root, expected_pid):
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self.path = self.root / 'native-workflow-report.json'
        self.client = Client(receipt_dir=self.root / 'controller-receipts')
        self.server = MCPServer(self.client)
        self.report = json.loads(self.path.read_text()) if self.path.exists() else {
            'run_id': str(uuid.uuid4()), 'status': 'incomplete', 'native': True,
            'steps': {}, 'checks': {}, 'tool_round_trips': 0, 'native_process_id': expected_pid,
            'visual_acceptance': 'pending', 'design_acceptance': 'not assessed'}
        caps = self.server.call('native_revit_capabilities', {})
        if caps['process_id'] != expected_pid:
            raise RuntimeError('Listener belongs to another process; refused native test.')
        docs = self.call('initial-documents', 'documents.list', {})
        if any(not d['is_family'] and d['path'] for d in docs):
            raise RuntimeError('Isolated test process has an existing saved project; refused test.')
        self.write()

    def write(self):
        p = self.path.with_suffix('.tmp')
        p.write_text(json.dumps(self.report, indent=2, allow_nan=False), encoding='utf-8')
        p.replace(self.path)

    def call(self, label, op, document, arguments=None, expected='completed'):
        oid = str(uuid.uuid5(uuid.UUID(self.report['run_id']), label))
        prior = self.report['steps'].get(label)
        if prior and prior['status'] == expected:
            return payload(prior)
        receipt = self.server.call('native_revit_submit', {'operation': op, 'document': document,
            'arguments': arguments or {}, 'operation_id': oid})
        self.report['tool_round_trips'] += 1
        self.report['steps'][label] = receipt
        self.write()
        if receipt['status'] in ('queued', 'running', 'unknown_completion'):
            receipt = self.server.call('native_revit_wait', {'operation_id': oid, 'timeout_seconds': 45})
            self.report['tool_round_trips'] += 1
            self.report['steps'][label] = receipt
            self.write()
        if receipt['status'] != expected:
            raise RuntimeError(f'{label}: {receipt["status"]}: {receipt.get("error")}; reconcile {oid}')
        return payload(receipt)

    def check(self, label, actual, expected, tolerance=1e-6):
        passed = actual == expected if isinstance(expected, (str, bool)) else math.isclose(actual, expected, abs_tol=tolerance)
        self.report['checks'][label] = {'actual': actual, 'expected': expected, 'pass': passed}
        self.write()
        if not passed:
            raise AssertionError(label)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--process-id', type=int, required=True)
    p.add_argument('--output-dir', required=True)
    p.add_argument('--project-template', default=r'C:\ProgramData\Autodesk\RVT 2025\Templates\Default_I_ENU.rte')
    p.add_argument('--cabinet-family', required=True, help='Explicit synthetic/representative RFA; never a production-project fallback')
    opts = p.parse_args()
    run = Run(opts.output_dir, opts.process_id)
    start = time.perf_counter()
    try:
        project = run.call('project-create', 'document.create', {}, {'template': opts.project_template})
        doc = {'session_id': project['session_id']}
        levels = run.call('levels', 'elements.query', doc, {'class': 'Level', 'limit': 500})['items']
        types = run.call('wall-types', 'elements.query', doc, {'class': 'WallType', 'types': True, 'limit': 500})['items']
        level = levels[0]['unique_id']
        wall = run.call('wall-create', 'wall.create', doc, {'type': types[0]['unique_id'], 'level': level,
            'start': [0, 0, 0], 'end': [12, 0, 0], 'height': 8})
        run.call('wall-inspect', 'elements.inspect', doc, {'element': wall['unique_id'], 'geometry': True})
        loaded = run.call('load-cabinet', 'family.load', doc, {'path': str(Path(opts.cabinet_family).resolve()), 'replacement_policy': 'reject'})
        symbols = run.call('cabinet-types', 'elements.query', doc, {'class': 'FamilySymbol', 'types': True, 'category': 'OST_Casework', 'limit': 500})['items']
        family_name = loaded['family']['name']
        symbol = next(s for s in symbols if s['name'] == 'Codex_Disposable_Box')
        run.report['synthetic_family_name'] = family_name
        placements = run.call('cabinet-run', 'family.place', doc, {'type': symbol['unique_id'],
            'instances': [{'point': [x, 2, 0], 'level': level, 'rotation_radians': 0} for x in (0, 3, 6)]})
        first = placements['instances'][0]['unique_id']
        parameters = run.call('cabinet-parameters', 'parameters.query', doc, {'element': first})
        run.report['parameter_inventory'] = parameters
        run.call('duplicate-cabinet-type', 'type.duplicate', doc, {'type': symbol['unique_id'], 'name': 'Codex_Modified_Test'})
        modified_type = next(s for s in run.call('modified-types', 'elements.query', doc, {'class': 'FamilySymbol', 'types': True, 'name_contains': 'Codex_Modified_Test'})['items'])
        run.call('set-height', 'parameter.set', doc, {'element': modified_type['unique_id'], 'name': 'Codex_Test_Height', 'value': 4, 'allow_type_change': True})
        run.call('change-type', 'element.type', doc, {'element': first, 'type': modified_type['unique_id']})
        run.call('move', 'element.move', doc, {'element': first, 'vector': [0, 1, 0]})
        run.call('rotate', 'element.rotate', doc, {'element': first, 'axis_start': [0, 3, 0], 'axis_end': [0, 3, 1], 'radians': math.pi/2})
        copied = run.call('copy', 'element.copy', doc, {'element': first, 'vector': [9, 0, 0]})
        actual = run.call('cabinet-readback', 'elements.inspect', doc, {'element': first})['element']
        run.check('move-x', actual['location']['point'][0], 0)
        run.check('move-y', actual['location']['point'][1], 3)
        run.check('height-geometry', actual['bounds']['max'][2]-actual['bounds']['min'][2], 4)
        run.check('rotate', actual['location']['rotation_radians'], math.pi/2)
        run.call('pin', 'element.pin', doc, {'element': first, 'pinned': True})
        run.call('pinned-move-rejected', 'element.move', doc, {'element': first, 'vector': [5, 0, 0]}, expected='rolled_back')
        run.call('unpin-explicit', 'element.pin', doc, {'element': first, 'pinned': False})
        run.call('stale-id-rejected', 'element.move', doc, {'element': 'not-a-valid-unique-id', 'vector': [1, 0, 0]}, expected='rolled_back')
        before = run.call('atomic-before', 'elements.inspect', doc, {'element': first})['element']['location']['point']
        run.call('atomic-failure', 'batch.atomic', doc, {'steps': [
            {'operation': 'element.move', 'arguments': {'element': first, 'vector': [5, 0, 0]}},
            {'operation': 'element.move', 'arguments': {'element': 'missing', 'vector': [1, 0, 0]}}]}, expected='rolled_back')
        after = run.call('atomic-after', 'elements.inspect', doc, {'element': first})['element']['location']['point']
        for i in range(3): run.check('atomic-restored-'+str(i), after[i], before[i])
        unaffected = run.call('unrelated-cabinet', 'elements.inspect', doc, {'element': placements['instances'][1]['unique_id']})['element']
        run.check('unrelated-type', unaffected['type_id'], symbol['id'])
        run.check('unrelated-position-x', unaffected['location']['point'][0], 3)
        floor_types = run.call('floor-types', 'elements.query', doc, {'class': 'FloorType', 'types': True})['items']
        run.call('floor', 'floor.create', doc, {'type': floor_types[0]['unique_id'], 'level': level,
            'profile': [[-1, -1, 0], [14, -1, 0], [14, 6, 0], [-1, 6, 0]]})
        view_types = run.call('view-types', 'elements.query', doc, {'class': 'ViewFamilyType', 'types': True})['items']
        # Lookup enum family through parameters instead of guessing names.
        view_family = {}
        for t in view_types:
            ps = run.call('view-type-'+str(t['id']), 'parameters.query', doc, {'element': t['unique_id']})
            view_family[t['name']] = t
        three = next(t for t in view_types if '3D' in t['name'])
        model_view = run.call('3d-view', 'view.create', doc, {'type': three['unique_id'], 'kind': '3d', 'name': 'Codex Native Cabinet Verification', 'scale': 24})
        sheet = run.call('sheet', 'sheet.create', doc, {'number': 'TEST-ID1.0', 'name': 'DISPOSABLE CABINET TEST'})
        vp = run.call('viewport', 'viewport.place', doc, {'sheet': sheet['unique_id'], 'view': model_view['unique_id'], 'center': [1.2, 1.2, 0]})
        moved_vp = run.call('viewport-move', 'viewport.move', doc, {'viewport': vp['element']['unique_id'], 'center': [1.5, 1.2, 0]})
        run.check('viewport-x', moved_vp['center'][0], 1.5)
        run.check('viewport-y', moved_vp['center'][1], 1.2)
        schedule = run.call('schedule', 'schedule.create', doc, {'category': 'OST_Casework', 'name': 'Codex Real Cabinet Schedule', 'fields': ['Family and Type', 'Count']})
        schedule_inst = run.call('schedule-place', 'schedule.place', doc, {'sheet': sheet['unique_id'], 'schedule': schedule['unique_id'], 'point': [2.5, 2, 0]})
        schedule_moved = run.call('schedule-move', 'schedule.move', doc, {'instance': schedule_inst['element']['unique_id'], 'point': [3, 2, 0]})
        run.check('schedule-x', schedule_moved['point'][0], 3)
        run.call('test-view-scale-fit', 'view.settings', doc, {'view': model_view['unique_id'], 'scale': 24, 'detail_level': 'Fine',
            'section_box': {'min': [-3,-2,-1], 'max': [16,8,9]},
            'category_visibility': {'OST_Casework': True, 'OST_Levels': False}})
        run.call('test-label-length-fit', 'viewport.settings', doc, {'viewport': moved_vp['element']['unique_id'], 'label_line_length': 0.5, 'label_offset': [0, 0, 0]})
        layout = {'content_region': [0, 0, 4, 3], 'moves': [
            {'element': moved_vp['element']['unique_id'], 'point': [1, 1.2, 0]},
            {'element': schedule_moved['element']['unique_id'], 'point': [3, 2, 0]}]}
        proposal = run.call('layout-propose-label-fit', 'layout.propose', doc, layout)
        run.check('proposed-layout-valid', proposal['valid'], True)
        run.call('layout-apply', 'layout.apply', doc, layout)
        run.call('sheet-readback', 'sheet.inspect', doc, {'sheet': sheet['unique_id']})
        run.call('sheet-capture', 'capture.export', doc, {'view': sheet['unique_id'], 'path_prefix': str(run.root/'native_sheet'), 'pixels': 1600})
        run.call('model-capture', 'capture.export', doc, {'view': model_view['unique_id'], 'path_prefix': str(run.root/'native_model'), 'pixels': 1600})
        run.call('save-disposable-project', 'document.save_as', doc, {'path': str(run.root/'Codex_Disposable_Native_Test.rvt')})
        run.report['status'] = 'technical_pass'
        run.report['limitations'] = ['Synthetic height-parametric box only; width/depth changes and manufacturer cabinets unproven',
            'Hosted appliance workflow pending', 'ID1.1 plan/elevation composition pending', 'Unaltered captures require visual review']
    except Exception as exc:
        run.report['status'] = 'incomplete'
        run.report['blocking_error'] = str(exc)
        raise
    finally:
        run.report['elapsed_seconds'] = time.perf_counter()-start
        run.report['receipt_payload_bytes'] = sum(p.stat().st_size for p in (run.root/'controller-receipts').glob('*.json'))
        run.write()


if __name__ == '__main__': main()
