# -*- coding: utf-8 -*-
"""In-session entry point for the Cassia SF549315AGOP family builder.

Use when `pyrevit run` cannot start its own Revit: on 2026-09-23 the House of Troy
build hit a native startup exception (0xe06d7363) that way and succeeded from a
button in the already-open session instead. This button runs
output/cassia/source/build_cassia.py inside the open Revit; the builder only creates,
saves and closes its own new documents and never touches open models.

The builder path is resolved from this file's location, so the RFA is written to
<this checkout>/output/cassia/ whichever checkout the extension was registered from.
"""
import os

__title__ = 'Build\nCassia'
__doc__ = 'Build and verify the Alora Mood Cassia SF549315AGOP family (output/cassia).'

_here = os.path.dirname(os.path.abspath(__file__))
_run_dir = os.path.normpath(os.path.join(_here, '..', '..', '..', '..', '..'))
_builder = os.path.join(_run_dir, 'source', 'build_cassia.py')
_scope = dict(globals())
_scope.update({'__file__': _builder, '__name__': '__main__'})
with open(_builder, 'rb') as _source:
    exec(compile(_source.read(), _builder, 'exec'), _scope)
print('Cassia build finished. RFA: ' + os.path.join(_run_dir, 'Alora_Cassia_SF549315AGOP_Aged_Gold_Opal_R2025.rfa'))
print('Now run source/verify_cassia.py for the independent verdict.')
