# -*- coding: utf-8 -*-
"""Evidence probe, run inside Revit 2025 through the pyRevit CLI.

Dumps, for every appearance schema that could carry clear glass, the property
names, types and default values, and which connected-texture schemas each
relief / colour slot accepts. Nothing is delivered from this script; it only
writes source/revit_probe.json inside output/clear_reeded_glass/.

It writes its JSON first and re-raises: an exit code is not evidence.
"""
import json
import os
import traceback

import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB

# pyrevit run may execute a temp copy of this file, so __file__ is not trusted.
RUN_DIR_CANDIDATES = [
    'E:/Claude/3D-Model-Workflow/.claude/worktrees/revit-clear-reeded-glass-4376d3/output/clear_reeded_glass',
    'E:/Claude/3D-Model-Workflow/output/clear_reeded_glass',
]
RUN_DIR = None
for _candidate in RUN_DIR_CANDIDATES:
    if os.path.isfile(os.path.join(_candidate, 'source', 'build_maps.py')):
        RUN_DIR = os.path.normpath(_candidate)
        break
if RUN_DIR is None:
    raise RuntimeError('Run directory not found among: ' + ' | '.join(RUN_DIR_CANDIDATES))
REPORT = {'stage': 'started', 'schemas': {}, 'connect_tests': {}}

WANTED = ['GenericSchema', 'SolidGlassSchema', 'GlazingSchema',
          'PrismTransparentSchema', 'PrismGlazingSchema', 'PrismOpaqueSchema']
TEXTURE_SCHEMAS = ['UnifiedBitmap', 'BumpMap']


def out_path(*parts):
    target = os.path.normpath(os.path.join(RUN_DIR, *parts))
    if not target.startswith(RUN_DIR + os.sep):
        raise RuntimeError('Write path escapes the run directory: ' + target)
    parent = os.path.dirname(target)
    if not os.path.isdir(parent):
        os.makedirs(parent)
    return target


def checkpoint(stage):
    REPORT['stage'] = stage
    with open(out_path('source', 'revit_probe.json'), 'w') as handle:
        handle.write(json.dumps(REPORT, indent=1, default=str, sort_keys=True))


def value_of(prop):
    kind = str(prop.Type)
    try:
        if isinstance(prop, DB.Visual.AssetPropertyDoubleArray4d):
            return [round(v, 5) for v in prop.GetValueAsDoubles()]
        if isinstance(prop, DB.Visual.AssetPropertyDoubleArray3d):
            return [round(v, 5) for v in prop.GetValueAsDoubles()]
        if isinstance(prop, DB.Visual.AssetPropertyDoubleArray2d):
            return [round(v, 5) for v in prop.GetValueAsDoubles()]
        if isinstance(prop, DB.Visual.AssetPropertyDistance):
            return [prop.Value, str(prop.GetUnitTypeId().TypeId)]
        if isinstance(prop, (DB.Visual.AssetPropertyDouble, DB.Visual.AssetPropertyFloat,
                             DB.Visual.AssetPropertyInteger, DB.Visual.AssetPropertyBoolean,
                             DB.Visual.AssetPropertyString, DB.Visual.AssetPropertyEnum)):
            return prop.Value
    except Exception as exc:
        return 'ERR ' + str(exc)
    return '<' + kind + '>'


def dump_asset(asset):
    rows = []
    for i in range(asset.Size):
        prop = asset.Get(i)
        row = [prop.Name, str(prop.Type), value_of(prop)]
        try:
            n = prop.NumberOfConnectedProperties
            if n:
                row.append('connected=%d' % n)
        except Exception:
            pass
        rows.append(row)
    return rows


def main():
    app = __revit__.Application
    REPORT['revit_version'] = app.VersionNumber
    REPORT['revit_build'] = app.VersionBuild

    found, counts = {}, {}
    for asset in app.GetAssets(DB.Visual.AssetType.Appearance):
        schema = asset.FindByName('BaseSchema')
        key = schema.Value if schema is not None else '<none>'
        counts[key] = counts.get(key, 0) + 1
        if key not in found:
            found[key] = asset
    REPORT['schema_counts'] = counts
    for key in WANTED:
        if key in found:
            REPORT['schemas'][key] = {'library_asset_name': found[key].Name,
                                      'properties': dump_asset(found[key])}
        else:
            REPORT['schemas'][key] = None
    checkpoint('schemas-dumped')

    # Which slots accept which connected texture schema, and what those expose.
    doc = app.NewProjectDocument(DB.UnitSystem.Imperial)
    tx = DB.Transaction(doc, 'probe')
    tx.Start()
    for key in WANTED:
        if key not in found:
            continue
        result = {}
        element = DB.AppearanceAssetElement.Create(doc, 'probe ' + key, found[key])
        scope = DB.Visual.AppearanceAssetEditScope(doc)
        editable = scope.Start(element.Id)
        for i in range(editable.Size):
            prop = editable.Get(i)
            name = prop.Name
            low = name.lower()
            if not any(t in low for t in ('bump', 'normal', 'relief', 'color', 'diffuse',
                                          'albedo', 'transmi', 'cutout', 'roughness')):
                continue
            slot = {}
            for tex in TEXTURE_SCHEMAS:
                try:
                    if prop.NumberOfConnectedProperties:
                        prop.RemoveConnectedAsset()
                    prop.AddConnectedAsset(tex)
                    connected = prop.GetSingleConnectedAsset()
                    slot[tex] = 'ok' if connected is not None else 'none'
                    if connected is not None and ('texprops_' + tex) not in REPORT:
                        REPORT['texprops_' + tex] = dump_asset(connected)
                    prop.RemoveConnectedAsset()
                except Exception as exc:
                    slot[tex] = 'ERR ' + str(exc).splitlines()[0][:160]
            result[name] = slot
        scope.Cancel()
        scope.Dispose()
        REPORT['connect_tests'][key] = result
        checkpoint('connect-' + key)
    tx.RollBack()
    doc.Close(False)
    checkpoint('complete')


if __name__ == '__main__':
    try:
        main()
    except Exception:
        REPORT['error'] = traceback.format_exc()
        try:
            checkpoint('failed')
        finally:
            raise
