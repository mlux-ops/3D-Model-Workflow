# -*- coding: utf-8 -*-
"""Six-family, one-session Revit 2025 batch. IronPython 2.7 / pyRevit."""
from __future__ import print_function
import os
import sys
import json
import time
import traceback
import hashlib

import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB

ROOT = os.path.dirname(os.path.abspath(__file__))
MANIFEST = os.path.join(ROOT, 'manifest.json')
OUT = os.path.join(ROOT, 'receipts')
APP = __revit__.Application
MM = 304.8

def write_json(path, data):
    parent = os.path.dirname(path)
    if not os.path.isdir(parent):
        os.makedirs(parent)
    temp = path + '.tmp'
    with open(temp, 'w') as stream:
        json.dump(data, stream, indent=2, default=str)
    if os.path.exists(path):
        os.remove(path)
    os.rename(temp, path)

def progress(jobid, stage, detail=None):
    entry = {'time_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
             'job': jobid, 'stage': stage, 'detail': detail}
    with open(os.path.join(OUT, 'progress.jsonl'), 'a') as log:
        log.write(json.dumps(entry, default=str) + '\n')
    print('%s: %s' % (jobid, stage))
    sys.stdout.flush()

def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as stream:
        while True:
            b = stream.read(1048576)
            if not b:
                break
            h.update(b)
    return h.hexdigest()

def inside(path, root):
    p = os.path.normcase(os.path.abspath(path))
    base = os.path.normcase(os.path.abspath(root))
    return p.startswith(base + os.sep)

def bounds_from_geometry(doc):
    # Union real native solids, including nested geometry instances.
    # Do not include reference planes, template extrusions, or annotation bounds.
    opts = DB.Options()
    opts.DetailLevel = DB.ViewDetailLevel.Fine
    opts.IncludeNonVisibleObjects = False
    minima = [float('inf')] * 3
    maxima = [float('-inf')] * 3
    count = [0]
    def walk(objects, transform):
        for item in objects:
            if isinstance(item, DB.GeometryInstance):
                walk(item.GetInstanceGeometry(), transform)
            elif isinstance(item, DB.Solid) and item.Volume > 1e-12:
                count[0] += 1
                # Tessellated actual faces avoid imprecise template / element bounding boxes.
                for face in item.Faces:
                    mesh = face.Triangulate()
                    for v in mesh.Vertices:
                        for i, x in enumerate((v.X, v.Y, v.Z)):
                            minima[i] = min(minima[i], x)
                            maxima[i] = max(maxima[i], x)
    # Only geometry-bearing elements. OEM imports may be represented via ImportInstance.
    cats = (DB.GenericForm, DB.ImportInstance)
    for cls in cats:
        try:
            for element in DB.FilteredElementCollector(doc).OfClass(cls):
                try:
                    geo = element.get_Geometry(opts)
                    if geo is not None:
                        walk(geo, None)
                except Exception:
                    pass
        except Exception:
            pass
    if not count[0]:
        return {'available': False, 'reason': 'No physical solid faces measured', 'solid_count': 0}
    dims = [round((maxima[i] - minima[i]) * MM, 4) for i in range(3)]
    return {'available': True, 'solid_count': count[0],
            'xyz_mm': dims, 'dimensions_sorted_mm': sorted(dims),
            'minimum_xyz_mm': [round(a * MM, 4) for a in minima],
            'maximum_xyz_mm': [round(a * MM, 4) for a in maxima],
            'scope': 'measured physical solid faces; XYZ axes; includes import solids if exposed'}

def inspect_family(doc, job):
    category = None
    try:
        category = doc.OwnerFamily.FamilyCategory.Name
    except Exception:
        pass
    warnings = []
    for w in doc.GetWarnings():
        try:
            warnings.append(w.GetDescriptionText())
        except Exception:
            warnings.append(str(w))
    measured = bounds_from_geometry(doc)
    actual = measured.get('xyz_mm', [])
    expected = job.get('expected_dimensions_mm')
    fit = {'evaluated': False, 'passed': None}
    if expected:
        xyz = [float(expected[x]) for x in ('width', 'depth', 'height')]
        if measured['available']:
            errors = [abs(actual[i] - xyz[i]) for i in range(3)]
            fit = {'evaluated': True, 'passed': max(errors) <= float(job.get('tolerance_mm', 1.0)),
                   'errors_mm': errors, 'max_error_mm': max(errors),
                   'axis_convention': 'Revit XYZ interpreted as width, depth, height'}
        else:
            fit = {'evaluated': False, 'passed': None, 'reason': 'Native solids unavailable'}
    category_ok = category == job.get('expected_category', 'Lighting Fixtures')
    caps = {'native_revit_open': True, 'reopened_from_saved_rfa': True,
            'family_category_inspected': category is not None,
            'geometry_envelope_measured': measured['available'],
            'warnings_inspected': True,
            'editable_material_parameter_tested': False,
            'placement_tested': False,
            'photometry_tested': False,
            'geometry_flex_tested': False,
            'source_verified': False}
    return {'family_category': category, 'category_pass': category_ok,
            'warnings': warnings, 'warning_count': len(warnings),
            'dimensions': measured, 'dimension_fit': fit, 'capabilities': caps}

def run_job(job):
    jid = job['id']
    destination = job['target_rfa']
    rec = {'id': jid, 'mode': job['mode'], 'target_rfa': destination,
           'started_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
           'status': 'STARTED', 'revit_version': str(APP.VersionNumber)}
    doc = None
    try:
        if os.path.exists(destination):
            raise ValueError('Target already exists. Revision-safe runner refuses overwrite.')
        if not os.path.isdir(os.path.dirname(destination)):
            os.makedirs(os.path.dirname(destination))
        progress(jid, 'SOURCE_PRECHECK')
        if job['mode'] == 'oem':
            source = job['source_rfa']
            if not os.path.isfile(source):
                raise IOError('OEM source absent: ' + source)
            rec['input_sha256'] = sha(source)
            # Opens OEM separately and creates a new output path, leaving OEM unchanged.
            doc = APP.OpenDocumentFile(source)
            if not doc.IsFamilyDocument:
                raise ValueError('OEM input is not a Revit family')
            progress(jid, 'OEM_OPENED', doc.Title)
            opts = DB.SaveAsOptions()
            opts.OverwriteExistingFile = False
            opts.Compact = True
            doc.SaveAs(destination, opts)
            progress(jid, 'SAVED')
        else:
            script = job['builder_script']
            if not os.path.isfile(script):
                raise IOError('Builder absent: ' + script)
            rec['builder_sha256'] = sha(script)
            scope = {'__name__': '__main__', '__file__': script,
                     '__revit__': __revit__, 'APP': APP, 'DB': DB,
                     'JOB': job, 'TARGET_RFA': destination, 'SOURCE_RFA': None,
                     'progress': lambda stage, detail=None: progress(jid, stage, detail),
                     'result': {}}
            progress(jid, 'BUILD_START')
            execfile(script, scope)
            rec['builder_result'] = scope.get('result', {})
            if not os.path.isfile(destination):
                raise IOError('Builder completed without expected target RFA')
            progress(jid, 'SAVED')
        if doc is not None:
            doc.Close(False)
            doc = None
        progress(jid, 'REOPEN')
        doc = APP.OpenDocumentFile(destination)
        if not doc.IsFamilyDocument:
            raise ValueError('Saved file failed family identity')
        rec.update(inspect_family(doc, job))
        rec['rfa_sha256'] = sha(destination)
        rec['rfa_size_bytes'] = os.path.getsize(destination)
        # Save/reopen and category/warning gates are required.
        fit = rec['dimension_fit']
        rec['technical_pass'] = (rec['category_pass'] and
                                 rec['warning_count'] == 0 and
                                 (not fit['evaluated'] or fit['passed']))
        if job.get('expected_dimensions_mm') and not fit['evaluated']:
            rec['technical_pass'] = False
        rec['status'] = 'PASS' if rec['technical_pass'] else 'HOLD'
        progress(jid, rec['status'])
    except Exception:
        rec['status'] = 'FAIL'
        rec['error'] = traceback.format_exc()
        progress(jid, 'FAIL', rec['error'][-2000:])
    finally:
        if doc is not None:
            try:
                doc.Close(False)
            except Exception as e:
                rec['close_error'] = str(e)
        rec['completed_utc'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        write_json(os.path.join(OUT, jid + '.json'), rec)
    return rec

def main():
    if not os.path.isdir(OUT):
        os.makedirs(OUT)
    if os.path.exists(os.path.join(OUT, 'batch_final.json')):
        raise ValueError('Batch receipt exists; refusing replay')
    with open(MANIFEST, 'r') as stream:
        manifest = json.load(stream)
    if manifest.get('schema_version') != 1 or len(manifest.get('families', [])) != 6:
        raise ValueError('Manifest must specify exactly six schema_version=1 families')
    ids = set()
    for job in manifest['families']:
        if job['id'] in ids or not job['id'].replace('_', '').isalnum():
            raise ValueError('Duplicate/invalid ID')
        ids.add(job['id'])
        if job.get('mode') not in ('oem', 'custom'):
            raise ValueError('Invalid mode')
        path = job['target_rfa']
        if not os.path.isabs(path) or not path.lower().endswith('.rfa'):
            raise ValueError('Target must be absolute .rfa')
        if not inside(path, os.path.dirname(ROOT)):
            raise ValueError('Target must stay in Belmont PH Good output')
        key = 'source_rfa' if job['mode'] == 'oem' else 'builder_script'
        if not os.path.isabs(job[key]):
            raise ValueError('Source/build script must be absolute')
        if os.path.exists(path):
            raise ValueError('Output preexists; choose new revision: ' + path)
    if str(APP.VersionNumber) != '2025':
        raise ValueError('Expected Revit 2025, found ' + str(APP.VersionNumber))
    uidoc = getattr(__revit__, 'ActiveUIDocument', None)
    if uidoc is not None:
        raise ValueError('Batch runner requires isolated pyrevit run without an active document')
    progress('batch', 'READY', {'jobs': len(ids), 'version': str(APP.VersionNumber)})
    results = []
    for job in manifest['families']:
        results.append(run_job(job))
    summary = {'schema_version': 1, 'batch_id': manifest.get('batch_id'),
               'family_results': [{'id': r['id'], 'status': r['status'],
                                   'technical_pass': r.get('technical_pass', False)} for r in results],
               'all_pass': all(r['status'] == 'PASS' for r in results),
               'complete_count': len(results)}
    write_json(os.path.join(OUT, 'batch_final.json'), summary)
    progress('batch', 'FINISHED', summary)

try:
    main()
except Exception:
    if not os.path.isdir(OUT):
        os.makedirs(OUT)
    write_json(os.path.join(OUT, 'batch_error.json'), {'error': traceback.format_exc()})
    raise
