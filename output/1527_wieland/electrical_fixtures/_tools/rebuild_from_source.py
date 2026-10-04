# -*- coding: utf-8 -*-
"""Rebuild native source solids into task-local face-based families."""
import os, sys, json, traceback, hashlib
from wieland_native import WielandFixture, DB, xyz
from native_fixture_support import all_solids, measured_geometry_bounds
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def run_one(app, key):
    jobs = json.load(open(os.path.join(ROOT,'REUSE_JOBS.json')))
    job = next(j for j in jobs if j['key']==key)
    source_doc = None
    source_tx = None
    fixture = None
    source_hash = hashlib.sha256(open(job['source_rfa'],'rb').read()).hexdigest()
    try:
        source_doc = app.OpenDocumentFile(job['source_rfa'])
        if job.get('source_parameter_inches'):
            source_tx = DB.Transaction(source_doc,'Temporary current-spec dimension flex')
            source_tx.Start()
            for name, value in job['source_parameter_inches'].items():
                p = source_doc.FamilyManager.get_Parameter(name)
                if p is None: raise RuntimeError('Missing manufacturer parameter '+name)
                source_doc.FamilyManager.Set(p,float(value)/12.)
            source_doc.Regenerate()
            source_tx.Commit()
            source_tx = None
        source_elements = []
        for element in DB.FilteredElementCollector(source_doc).OfClass(DB.GenericForm):
            eid = str(element.Id.Value)
            if eid in job.get('skip_ids',[]): continue
            category = element.Subcategory.Name if element.Subcategory else (element.Category.Name if element.Category else '')
            label = job.get('id_material',{}).get(eid) or job.get('category_material',{}).get(category)
            if label:
                source_elements.append((element,label,category or 'Manufacturer form '+eid))
        if not source_elements:
            raise RuntimeError('No product forms selected from source family')
        fixture = WielandFixture(app,job['out'],job['name'],job['manufacturer'],job['model'],job['model'],job['host'],job['dimensions'])
        materials = {}
        for material in job['materials']:
            values = dict(material)
            label = values.pop('label')
            materials[label] = fixture.material(label,**values)
        for element,label,category in source_elements:
            options = DB.Options()
            options.DetailLevel = DB.ViewDetailLevel.Fine
            solids = list(all_solids(element.get_Geometry(options)))
            for n,solid in enumerate(solids):
                copy = DB.SolidUtils.CreateTransformed(solid, DB.Transform.Identity)
                form = fixture.add(category+' / source '+str(element.Id.Value)+' / '+str(n),copy,materials[label])
        canopy = job.get('replacement_canopy')
        if canopy:
            fixture.cylinder('Current-spec canopy',xyz(),DB.XYZ.BasisZ,canopy['diameter']/2,0,canopy['height'],materials[canopy['material']],.04)
        fixture.note(job['notes'])
        fixture.report.update({'source_url':job['source_url'],'rfa_search':job['rfa_search'],
            'source_rfa':job['source_rfa'],'source_rfa_sha256':source_hash,
            'rebuild_method':'Inspected native source solids reconstructed as new FreeFormElements with new editable finish parameters; no source RFA renamed as an original model.',
            'source_parameter_inches':job.get('source_parameter_inches',{}),
            'limitations':job['notes']})
        report = fixture.finish()
        unchanged = hashlib.sha256(open(job['source_rfa'],'rb').read()).hexdigest()==source_hash
        report['source_file_unchanged'] = unchanged
        report['technical_pass'] = report['technical_pass'] and unchanged
        with open(os.path.join(job['out'],'validation.json'),'w') as stream:json.dump(report,stream,indent=2,default=str)
        return report
    except Exception:
        if fixture is not None:
            fixture.fail()
            with open(os.path.join(job['out'],'validation.json'),'w') as stream:json.dump(fixture.report,stream,indent=2,default=str)
        else:
            with open(os.path.join(job['out'],'validation.json'),'w') as stream:json.dump({'technical_pass':False,'stage':'source_rebuild_error','error':traceback.format_exc()},stream,indent=2)
        raise
    finally:
        if source_tx is not None:
            try:source_tx.RollBack()
            except Exception:pass
        if source_doc is not None:
            source_doc.Close(False)

def main(app):
    summary=[]
    for job in json.load(open(os.path.join(ROOT,'REUSE_JOBS.json'))):
        try:
            report=run_one(app,job['key'])
            summary.append({'key':job['key'],'passed':report['technical_pass'],'path':report['rfa_path']})
        except Exception:
            summary.append({'key':job['key'],'passed':False,'error':traceback.format_exc()})
        with open(os.path.join(ROOT,'REUSE_BATCH_RESULT.json'),'w') as stream:json.dump(summary,stream,indent=2)

if __name__=='__main__':
    main(__revit__.Application)
