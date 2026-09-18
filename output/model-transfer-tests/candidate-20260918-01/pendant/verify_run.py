r"""Independent gate verifier for a P01 pendant run.

pyRevit returns exit code 0 even when the hosted script raises: that happened on
both failing attempts of this run (2026-09-18). Never read the runner's exit
status as a result. Run this afterwards and read ITS exit code.

    "C:\Program Files\pyRevit-Master\bin\cengines\CPY3123\python.exe" verify_run.py

Exits 0 only when validation.json reports a complete run with every gate true for
every configuration and the recorded RFAs exist on disk. Exits 1 otherwise.
Standard library only; no numpy or PIL, neither of which is installed here.

A pass from this script is a TECHNICAL pass. PENDANT.md also requires a visual
pass, which no script may award itself.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPORT = os.path.join(HERE, 'validation.json')
EXPECTED_CONFIGS = ('baseline', 'variant')


def fail(problems):
    print('FAIL - %d problem(s):' % len(problems))
    for item in problems:
        print('  - %s' % item)
    return 1


def main():
    if not os.path.isfile(REPORT):
        return fail(['validation.json is missing; the run did not reach its first checkpoint'])

    with open(REPORT) as handle:
        try:
            report = json.load(handle)
        except ValueError as exc:
            return fail(['validation.json is not parseable: %s' % exc])

    problems = []

    stage = report.get('stage')
    if stage != 'complete':
        problems.append('stage is %r, expected "complete"' % stage)
    if report.get('technical_pass') is not True:
        problems.append('top-level technical_pass is %r' % report.get('technical_pass'))
    if report.get('error'):
        problems.append('an error is recorded at the top level of the report')
    # failed_gates is a mapping of configuration to list; an empty list per
    # configuration is the passing shape, and the dict itself is always truthy.
    failed_gates = report.get('failed_gates') or {}
    if isinstance(failed_gates, dict):
        offenders = dict((k, v) for k, v in failed_gates.items() if v)
        if offenders:
            problems.append('failed_gates records failures: %r' % (offenders,))
    elif failed_gates:
        problems.append('failed_gates is not empty: %r' % (failed_gates,))

    configs = report.get('configs')
    if not isinstance(configs, dict):
        return fail(['configs is %s, expected a mapping of configuration key to record'
                     % type(configs).__name__])
    for key in EXPECTED_CONFIGS:
        if key not in configs:
            problems.append('configuration %r is missing from the report' % key)

    for key in sorted(configs):
        config = configs[key]
        label = config.get('label') or key

        if config.get('technical_pass') is not True:
            problems.append('%s: technical_pass is %r' % (label, config.get('technical_pass')))

        gates = config.get('gates') or {}
        if not gates:
            problems.append('%s: no gate map recorded' % label)
        for name in sorted(gates):
            if gates[name] is not True:
                problems.append('%s: gate %s is %r' % (label, name, gates[name]))

        # Every dimension and flex row must hold on its own terms, not only in
        # the gate map, so a future gate-logic bug cannot hide a real failure.
        for name, dim in sorted((config.get('dimensions') or {}).items()):
            if dim.get('pass') is not True:
                problems.append('%s: dimension %s measured %r against target %r'
                                % (label, name, dim.get('measured_in'), dim.get('target_in')))

        flex = config.get('flex_tests') or []
        if not flex:
            problems.append('%s: no flex tests recorded' % label)
        for test in flex:
            cord = test.get('cord_inches')
            if test.get('formula_pass') is not True:
                problems.append('%s: formula_pass false at cord %s' % (label, cord))
            if test.get('measured_pass') is not True:
                problems.append('%s: measured_pass false at cord %s' % (label, cord))

        for name, test in sorted((config.get('material_tests') or {}).items()):
            if test.get('reached_nested_geometry') is not True:
                problems.append('%s: %s did not reach nested geometry' % (label, name))

        for warn_key in ('family_warnings', 'project_warnings'):
            if config.get(warn_key):
                problems.append('%s: %s is not empty' % (label, warn_key))

        for path_key in ('rfa_path', 'body_rfa_path'):
            path = config.get(path_key)
            if not path:
                problems.append('%s: %s not recorded' % (label, path_key))
            elif not os.path.isfile(path):
                problems.append('%s: %s does not exist on disk: %s' % (label, path_key, path))

    if problems:
        return fail(problems)

    print('TECHNICAL PASS - %d configurations, every gate true, RFAs present.' % len(configs))
    for key in sorted(configs):
        config = configs[key]
        print('  %-12s %s' % (key, os.path.basename(config.get('rfa_path', ''))))
        print('  %-12s %s' % ('', config.get('label')))
    print('')
    print('visual_verdict: %s' % configs[EXPECTED_CONFIGS[0]].get('visual_verdict'))
    print('A technical pass is not a visual pass. PENDANT.md requires both.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
