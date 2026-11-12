"""Native regression for Revit dotted-prefix truncation and immutable exports."""
import argparse
import hashlib
from pathlib import Path
from native_hosting_recovery import NativeRun

def main():
    p=argparse.ArgumentParser();p.add_argument('--process-id',type=int,required=True);p.add_argument('--output-dir',required=True);o=p.parse_args();r=NativeRun(o.output_dir,o.process_id)
    try:
        project=r.call('project','document.create',{}, {'template':r'C:\ProgramData\Autodesk\RVT 2025\Templates\Default_I_ENU.rte'});d={'session_id':project['session_id']}
        types=r.call('viewtypes','elements.query',d,{'class':'ViewFamilyType','types':True})['items'];draft=next(t for t in types if t['view_family']=='Drafting')
        view=r.call('view','view.create',d,{'type':draft['unique_id'],'kind':'drafting','name':'EXPORT PREFIX REGRESSION','scale':24})
        texttype=r.call('texttypes','elements.query',d,{'class':'TextNoteType','types':True})['items'][0]
        r.call('text','annotation.text',d,{'view':view['unique_id'],'type':texttype['unique_id'],'point':[0,0,0],'text':'IMMUTABLE NATIVE EXPORT TEST'})
        prefix=str(r.root/'safe_first');first=r.call('first','capture.export',d,{'view':view['unique_id'],'path_prefix':prefix,'pixels':1000})
        r.check('nonempty-actual-file-list',len(first['files'])>0,True)
        files={path:hashlib.sha256(Path(path).read_bytes()).hexdigest() for path in first['files']}
        for label,path in [('dotted',prefix+'.changed'),('existing',prefix),('relative','relative_prefix')]:
            receipt=r.client.submit('capture.export',d,{'view':view['unique_id'],'path_prefix':path,'pixels':1000});receipt=r.client.wait(receipt['operation_id'],30)
            r.report['steps']['rejected-'+label]=receipt;r.write();r.check(label+'-rejected',receipt['status'],'failed')
            for file,original in files.items():r.check(label+'-preserved-'+Path(file).name,hashlib.sha256(Path(file).read_bytes()).hexdigest(),original)
        second=r.call('second','capture.export',d,{'view':view['unique_id'],'path_prefix':str(r.root/'safe_second'),'pixels':1000})
        r.check('second-native-file-list',len(second['files'])>0,True)
        for file,original in files.items():r.check('second-preserves-first-'+Path(file).name,hashlib.sha256(Path(file).read_bytes()).hexdigest(),original)
        r.report['status']='passed';r.report['original_export_hashes']=files
    except Exception as e:r.report['status']='incomplete';r.report['error']=str(e);raise
    finally:r.write()

if __name__=='__main__':main()
