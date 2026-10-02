# -*- coding: utf-8 -*-
"""Probe 3: on the brief's Generic Model face based template, does changing the category expose a 'Light Source'
family parameter, and does setting it create a light source element? Writes _work/probe_light3.json after each step."""
import sys
import json
import traceback

RUN = "E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce/max"
if RUN + "/source" not in sys.path:
    sys.path.insert(0, RUN + "/source")
from common import *

OUT = RUN + "/_work/probe_light3.json"
app = __revit__.Application
R = {'revit': app.VersionName + ' ' + app.VersionBuild, 'steps': {}, 'closes': []}
DOCS = []


def save():
    with open(safe(OUT), 'w') as f:
        json.dump(R, f, indent=1, default=str)


def owner_params(doc):
    out = {}
    for p in doc.OwnerFamily.Parameters:
        out[p.Definition.Name] = {'value': pval(p), 'readonly': p.IsReadOnly}
    return out


def light_ids(doc):
    col = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_LightingFixtureSource)
    return [str(e.Id.Value) for e in col.WhereElementIsNotElementType()]


try:
    d = app.NewFamilyDocument(TEMPLATE)
    DOCS.append(d)
    R['steps']['params_before_category'] = owner_params(d)
    R['steps']['lights_before_category'] = light_ids(d)
    save()
    with Tx(d, 'category'):
        d.OwnerFamily.FamilyCategory = d.Settings.Categories.get_Item(DB.BuiltInCategory.OST_LightingFixtures)
        d.Regenerate()
    R['steps']['params_after_category'] = owner_params(d)
    R['steps']['lights_after_category'] = light_ids(d)
    save()
    target = None
    for p in d.OwnerFamily.Parameters:
        if p.Definition.Name == 'Light Source':
            target = p
    R['steps']['light_source_param_present'] = target is not None
    if target is not None:
        try:
            with Tx(d, 'set light source param'):
                target.Set(1)
                d.Regenerate()
            R['steps']['set_light_source_param'] = 'ok'
        except Exception:
            R['steps']['set_light_source_param'] = traceback.format_exc()
        R['steps']['lights_after_set'] = light_ids(d)
        R['steps']['light_read_after_set'] = read_light(d)
    save()
except Exception:
    R['steps']['error'] = traceback.format_exc()
    save()
finally:
    for d in reversed(DOCS):
        close_doc(d, R['closes'], 'probe doc')
    R['done'] = True
    save()
