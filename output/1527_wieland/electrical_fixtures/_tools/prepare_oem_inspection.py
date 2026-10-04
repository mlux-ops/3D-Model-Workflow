"""Prepare a separate read-only inspector for extracted manufacturer families."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
source=(ROOT/'_tools/inspect_native_sources.py').read_text()
a=source.index('JOBS = [');b=source.index('\nresults = []',a)
replacement="JOBS = [(os.path.basename(r['path']),r['path']) for r in json.load(open(os.path.join(ROOT,'OEM_EXTRACTED_FILES.json'))) if r['extension']=='.rfa']"
source=source[:a]+replacement+source[b:]
source=source.replace("'NATIVE_SOURCE_INSPECTION.json'","'OEM_SOURCE_INSPECTION.json'")
source=source.replace("                box = e.get_BoundingBox(None)","""                p=e.get_Parameter(DB.BuiltInParameter.MATERIAL_ID_PARAM)
                if p is not None:
                    mat=doc.GetElement(p.AsElementId())
                    fp=doc.FamilyManager.GetAssociatedFamilyParameter(p)
                    entry['material_name']=mat.Name if mat else None
                    entry['material_parameter']=fp.Definition.Name if fp else None
                box = e.get_BoundingBox(None)""")
(ROOT/'_tools/inspect_oem_families.py').write_text(source,encoding='utf-8')
print('OEM inspector staged for '+str(len(json.loads((ROOT/'OEM_EXTRACTED_FILES.json').read_text())))+' extracted files')
