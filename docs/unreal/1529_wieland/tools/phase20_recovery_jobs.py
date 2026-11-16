"""Short-call launch/status wrappers for the remaining recovery checks.

No memory limits, cancellation, editor restart, or level saves are added here.
"""
import asyncio
import importlib.util
import json
from pathlib import Path

import phase9_profile_m7 as m7

ROOT = Path(__file__).resolve().parent.parent
TASK = None
RESULT = None


async def _record(coro, target):
    global RESULT
    try:
        RESULT = {'result': await coro}
    except Exception as exc:
        RESULT = {'error': repr(exc)}
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(RESULT, indent=2, default=str), encoding='utf-8')


def profile():
    global TASK, RESULT
    if TASK is not None and not TASK.done():
        raise RuntimeError('Recovery job is already active')
    RESULT = None
    folder = ROOT / 'profiles/2026-11-13_M7/P20R2'
    TASK = asyncio.create_task(_record(
        m7.run(str(folder), 'P20R2', parts=('exterior', 'roofdeck'), skip_first_walk=True,
               note='Round 2 final saved model after crash recovery; owner removed memory guards'),
        folder / 'run_result.json'))
    return {'started': 'profile'}


def grazing():
    global TASK, RESULT
    if TASK is not None and not TASK.done():
        raise RuntimeError('Recovery job is already active')
    RESULT = None
    source = ROOT / 'tools/phase20r2_grazing.py'
    spec = importlib.util.spec_from_file_location('phase20r2_grazing_recovery', source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    TASK = asyncio.create_task(_record(module.run(), ROOT / 'review/phase20/round2/grazing_result.json'))
    return {'started': 'grazing'}


def status():
    return {'active': TASK is not None and not TASK.done(), 'result': RESULT}
