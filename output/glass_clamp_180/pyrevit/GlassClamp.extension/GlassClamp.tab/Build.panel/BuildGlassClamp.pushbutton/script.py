# -*- coding: utf-8 -*-
"""In-session entry point for the SHB_Glass Clamp 180 Square family builder.

Use when `pyrevit run` cannot start its own Revit (the 2026-09-23 House of Troy build hit a
native startup exception 0xe06d7363 that way and succeeded from a button in the already-open
session instead). Runs output/glass_clamp_180/source/build_glass_clamp.py inside the open
Revit; the builder only creates, saves and closes its own new documents and never touches
open models or the Belmont model.

The builder path is resolved from this file's location, so the RFA is written to
<this checkout>/output/glass_clamp_180/ whichever checkout the extension was registered from.
"""
import os

__title__ = 'Build\nGlass Clamp'
__doc__ = 'Build the SHB_Glass Clamp 180 Square family (output/glass_clamp_180).'

_here = os.path.dirname(os.path.abspath(__file__))
_run_dir = os.path.normpath(os.path.join(_here, '..', '..', '..', '..', '..'))
_builder = os.path.join(_run_dir, 'source', 'build_glass_clamp.py')
_scope = dict(globals())
_scope.update({'__file__': _builder, '__name__': '__main__'})
with open(_builder, 'rb') as _source:
    exec(compile(_source.read(), _builder, 'exec'), _scope)
print('Glass clamp build finished. RFA: ' + os.path.join(_run_dir, 'SHB_Glass Clamp 180 Square.rfa'))
print('Now run source/verify_glass_clamp.py for the independent verdict.')
