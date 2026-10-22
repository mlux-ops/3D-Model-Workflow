# -*- coding: utf-8 -*-
"""In-session entry point for the Miele KM 3054-1 cooktop family builder (Route B).

Use when `pyrevit run` cannot start its own Revit (0xe06d7363 at startup, House of
Troy 2026-09-23). The builder path is resolved from this file's own location, so the
RFA is written to <this checkout>/output/miele_km3054_1/ whichever checkout the
extension was registered from. The builder only creates, saves and closes its own new
documents and never touches open models.
"""
import os

__title__ = 'Build\nKM 3054-1'
__doc__ = 'Build and verify the Miele KM 3054-1 gas cooktop family (output/miele_km3054_1).'

_here = os.path.dirname(os.path.abspath(__file__))
_run_dir = os.path.normpath(os.path.join(_here, '..', '..', '..', '..', '..'))
_builder = os.path.join(_run_dir, 'source', 'build_km3054.py')
_scope = dict(globals())
_scope.update({'__file__': _builder, '__name__': '__main__'})
with open(_builder, 'rb') as _source:
    exec(compile(_source.read(), _builder, 'exec'), _scope)
print('KM 3054-1 build finished. RFA: ' + os.path.join(_run_dir, 'Miele_KM3054-1_Gas_Cooktop_R2025.rfa'))
print('Now run source/verify_km3054.py for the independent verdict.')
