# -*- coding: utf-8 -*-
"""In-session entry point for the SHB_Glass Clamp 180 Square builder.

Use when `pyrevit run` cannot start its own Revit (native startup exception 0xe06d7363,
House of Troy 2026-09-23). Runs output/glass_clamp_180/source/build_clamp.py inside the
open Revit; the builder only creates, saves and closes its own new documents.

The builder path is resolved from this file's location, so the RFA is written to
<this checkout>/output/glass_clamp_180/.
"""
import os

__title__ = 'Build\nClamp 180'
__doc__ = 'Build and verify SHB_Glass Clamp 180 Square (output/glass_clamp_180).'

_here = os.path.dirname(os.path.abspath(__file__))
_run_dir = os.path.normpath(os.path.join(_here, '..', '..', '..', '..', '..'))
_builder = os.path.join(_run_dir, 'source', 'build_clamp.py')
_scope = dict(globals())
_scope.update({'__file__': _builder, '__name__': '__main__'})
with open(_builder, 'rb') as _source:
    exec(compile(_source.read(), _builder, 'exec'), _scope)
print('Clamp build finished. RFA: ' + os.path.join(_run_dir, 'SHB_Glass Clamp 180 Square.rfa'))
print('Now run source/verify_clamp.py for the independent verdict.')
