# -*- coding: utf-8 -*-
"""Read-only inspection of source families, under the shared Revit lock."""
import os, sys, json, datetime, traceback
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit import DB
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(ROOT)))
sys.path.insert(0, os.path.join(ROOT, '_tools'))
from native_fixture_support import measured_geometry_bounds
app = __revit__.Application
JOBS = [(os.path.basename(r['path']),r['path']) for r in json.load(open(os.path.join(ROOT,'OEM_EXTRACTED_FILES.json'))) if r['extension']=='.rfa' and os.path.basename(r['path']).startswith('Lighting-')]
results = []
output = os.path.join(ROOT, 'OEM_ADDITIONAL_INSPECTION.json')
def json_safe(value):
    if isinstance(value, dict): return {json_safe(k):json_safe(v) for k,v in value.items()}
    if isinstance(value, (list,tuple)): return [json_safe(v) for v in value]
    if isinstance(value, basestring):
        return ''.join(chr(ord(c)) if ord(c)<128 else '[U+%04X]'%ord(c) for c in value)
    return value
for key, path in JOBS:
    row = {'key': key, 'path': path, 'stage': 'open', 'started_utc': datetime.datetime.utcnow().isoformat() + 'Z'}
    doc = None
    try:
        info = DB.BasicFileInfo.Extract(path)
        row['saved_format'] = str(info.Format)
        info.Dispose()
        doc = app.OpenDocumentFile(path)
        row.update({'category': doc.OwnerFamily.FamilyCategory.Name, 'placement': str(doc.OwnerFamily.FamilyPlacementType),
                    'family': doc.OwnerFamily.Name, 'warnings': [w.GetDescriptionText() for w in doc.GetWarnings()],
                    'types': [t.Name for t in doc.FamilyManager.Types]})
        parameters = []
        for param in doc.FamilyManager.Parameters:
            entry = {'name': param.Definition.Name, 'instance': param.IsInstance, 'read_only': param.IsReadOnly,
                     'formula': param.Formula, 'data_type': str(param.Definition.GetDataType().TypeId)}
            try:
                t = doc.FamilyManager.CurrentType
                if param.StorageType == DB.StorageType.Double:
                    entry['double_internal'] = t.AsDouble(param)
                elif param.StorageType == DB.StorageType.String:
                    entry['text'] = t.AsString(param)
                elif param.StorageType == DB.StorageType.ElementId:
                    element = doc.GetElement(t.AsElementId(param))
                    entry['element_name'] = element.Name if element else None
            except Exception as exc:
                entry['read_error'] = str(exc)
            parameters.append(entry)
        row['parameters'] = parameters
        forms = []
        for e in DB.FilteredElementCollector(doc).WhereElementIsNotElementType():
            if isinstance(e, DB.GenericForm) or isinstance(e, DB.FamilyInstance):
                entry = {'id': str(e.Id.Value), 'class': e.GetType().Name, 'category': e.Category.Name if e.Category else None}
                p=e.get_Parameter(DB.BuiltInParameter.MATERIAL_ID_PARAM)
                if p is not None:
                    mat=doc.GetElement(p.AsElementId())
                    fp=doc.FamilyManager.GetAssociatedFamilyParameter(p)
                    entry['material_name']=mat.Name if mat else None
                    entry['material_parameter']=fp.Definition.Name if fp else None
                box = e.get_BoundingBox(None)
                if box:
                    entry['display_bounds_in'] = [box.Min.X*12, box.Min.Y*12, box.Min.Z*12, box.Max.X*12, box.Max.Y*12, box.Max.Z*12]
                try:
                    entry['native_bounds_in'] = measured_geometry_bounds([e])
                except Exception:
                    entry['no_solid_geometry'] = True
                forms.append(entry)
        row['forms'] = forms
        row['stage'] = 'inspected'
    except Exception:
        row['stage'] = 'error'
        row['error'] = traceback.format_exc()
    finally:
        if doc is not None:
            doc.Close(False)
    results.append(row)
    with open(output, 'w') as stream:
        json.dump(json_safe(results), stream, indent=2, default=unicode)
