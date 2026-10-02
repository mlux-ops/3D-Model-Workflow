# -*- coding: utf-8 -*-
"""Write guard for the xhigh trial arm. Works in CPython 3 and IronPython 2.7.

Every file this arm writes goes through safe_path(), which refuses anything outside RUN_DIR.
"""
import os

RUN_DIR = os.path.normcase(os.path.abspath(
    'E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce/xhigh'))


def safe_path(path):
    full = os.path.normcase(os.path.abspath(path))
    if full != RUN_DIR and not full.startswith(RUN_DIR + os.sep):
        raise IOError('write refused outside run folder: ' + path)
    return path


def safe_open(path, mode='w'):
    safe_path(path)
    d = os.path.dirname(os.path.abspath(path))
    if not os.path.isdir(d):
        os.makedirs(d)
    return open(path, mode)


def _clean(o):
    if isinstance(o, dict):
        return dict((_clean(k) if not isinstance(k, (int, float)) else k, _clean(v)) for k, v in o.items())
    if isinstance(o, (list, tuple)):
        return [_clean(v) for v in o]
    if isinstance(o, float):
        if o != o or o in (float('inf'), float('-inf')):
            return str(o)
        return o
    if isinstance(o, (bool, int, long_t, type(None))):
        return o
    try:
        s = o if isinstance(o, basestring_t) else str(o)
    except Exception:
        s = repr(o)
    return u''.join(c if ord(c) < 128 else u'?' for c in s)


try:
    long_t = long
    basestring_t = basestring
except NameError:
    long_t = int
    basestring_t = str


def dump_json(obj, path):
    import json
    f = safe_open(path, 'w')
    try:
        f.write(json.dumps(_clean(obj), indent=1, sort_keys=True))
    finally:
        f.close()
