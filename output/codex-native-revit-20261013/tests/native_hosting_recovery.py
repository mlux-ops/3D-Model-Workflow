"""Native hosted placement and dropped-response recovery in a new disposable project."""
import argparse
import json
import math
from pathlib import Path
import socket
import sys
import time
import urllib.request
import uuid

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'controller'))
from native_revit import Client, canonical


def data(receipt):
    r=receipt['result']
    return r.get('data',r.get('result',r)) if isinstance(r,dict) else r


class NativeRun:
    def __init__(self,root,pid):
        self.root=Path(root).resolve();self.root.mkdir(parents=True,exist_ok=True)
        self.client=Client(receipt_dir=self.root/'controller-receipts')
        self.path=self.root/'native-hosting-recovery.json'
        self.report=json.loads(self.path.read_text()) if self.path.exists() else {'run_id':str(uuid.uuid4()),'status':'incomplete','steps':{},'checks':{},'native':True}
        if self.client.capabilities()['process_id']!=pid:raise RuntimeError('Refused wrong process')
        self.write()
    def write(self):
        t=self.path.with_suffix('.tmp');t.write_text(json.dumps(self.report,indent=2),encoding='utf-8');t.replace(self.path)
    def call(self,label,op,doc,a=None):
        oid=str(uuid.uuid5(uuid.UUID(self.report['run_id']),label))
        old=self.report['steps'].get(label)
        if old and old['status']=='completed':
            accepted=old['request']
            if accepted['operation']!=op or accepted['document']!=doc or accepted['arguments']!=(a or {}):
                raise RuntimeError('Completed step differs from new request; use a new step label/attempt, never reuse its UUID.')
            return data(old)
        r=self.client.submit(op,doc,a or {},operation_id_value=oid);self.report['steps'][label]=r;self.write()
        r=self.client.wait(oid,45);self.report['steps'][label]=r;self.write()
        if r['status']!='completed':raise RuntimeError(f'{label}: {r["status"]} {r.get("error")}')
        return data(r)
    def check(self,name,actual,expected):
        ok=actual==expected if isinstance(expected,(str,bool)) else math.isclose(actual,expected,abs_tol=1e-6)
        self.report['checks'][name]={'actual':actual,'expected':expected,'pass':ok};self.write()
        if not ok:raise AssertionError(name)
    def family(self,name,template):
        f=self.call(name+'-create','family.create',{}, {'template':template});doc={'session_id':f['session_id']}
        self.call(name+'-type','family.type.create',doc,{'name':name})
        self.call(name+'-geometry','family.extrusion.create',doc,{'units':'feet','plane':{'origin':[0,0,0],'normal':[0,0,1]},'profile':[[[0,0,0],[1,0,0],[1,1,0],[0,1,0]]],'end':1})
        path=self.root/(name+'.rfa');self.call(name+'-save','family.save',doc,{'path':str(path)})
        return path


def run(opts):
    r=NativeRun(opts.output_dir,opts.process_id)
    try:
        project=r.call('project','document.create',{}, {'template':r'C:\ProgramData\Autodesk\RVT 2025\Templates\Default_I_ENU.rte'})
        doc={'session_id':project['session_id']}
        level=r.call('levels','elements.query',doc,{'class':'Level'})['items'][0]['unique_id']
        walltype=r.call('wall-types','elements.query',doc,{'class':'WallType','types':True})['items'][0]['unique_id']
        wall=r.call('wall','wall.create',doc,{'type':walltype,'level':level,'start':[0,0,0],'end':[10,0,0],'height':8})
        inspection=r.call('wall-geometry','elements.inspect',doc,{'element':wall['unique_id'],'geometry':True})
        template_root=r'C:\ProgramData\Autodesk\RVT 2025\Family Templates\English-Imperial'
        hosted=r.family('Codex_Wall_Hosted',template_root+r'\Casework wall based.rft')
        face=r.family('Codex_Face_Hosted',template_root+r'\Generic Model face based.rft')
        for label,path,category in [('wall-hosted',hosted,'OST_Casework'),('face-hosted',face,'OST_GenericModel')]:
            r.call(label+'-load','family.load',doc,{'path':str(path),'replacement_policy':'reject'})
            symbols=r.call(label+'-symbol','elements.query',doc,{'class':'FamilySymbol','types':True,'category':category})['items']
            sym=next(s for s in symbols if s['name']==path.stem)
            args={'type':sym['unique_id'],'point':[3,0,2],'level':level,'host':wall['unique_id']}
            if label=='face-hosted':
                refs=[f for f in inspection['geometry'] if f.get('kind')=='face' and f.get('normal') and abs(f['normal'][1])>0.9]
                if not refs:raise RuntimeError('No vertical referenceable wall face')
                # Native face normal determines host-side coordinate, wall thickness comes from native bounds.
                chosen=refs[0];bounds=inspection['element']['bounds'];y=bounds['max'][1] if chosen['normal'][1]>0 else bounds['min'][1]
                args.update({'point':[6,y,2],'face_reference':chosen['reference'],'reference_direction':[1,0,0]})
            placed=r.call(label+'-place','family.place',doc,args)['instances'][0]
            actual=r.call(label+'-verify','elements.inspect',doc,{'element':placed['unique_id'],'geometry':True})
            r.check(label+'-host',actual['element']['host_id'],wall['id'])
            r.report[label]={'placement_type':sym['placement_type'],'element':actual['element'],'geometry':actual['geometry']};r.write()
        uid=wall['unique_id']
        before=r.call('timeout-before','elements.inspect',doc,{'element':uid})['element']['location']['start']
        oid=str(uuid.uuid5(uuid.UUID(r.report['run_id']),'timeout-move'))
        accepted=r.client.submit('element.move',doc,{'element':uid,'vector':[0,1,0]},operation_id_value=oid)
        observed=r.client.wait(oid,timeout_seconds=0)
        r.report['timeout_observation']=observed;r.write()
        final=r.client.wait(oid,45);r.report['steps']['timeout-move']=final;r.write()
        if final['status']!='completed':raise RuntimeError('Timeout reconciliation failed')
        after=r.call('timeout-after','elements.inspect',doc,{'element':uid})['element']['location']['start']
        r.check('timeout-single-move',after[1]-before[1],1)
        # A duplicate client submission uses the old UUID for GET reconciliation, never a second mutation.
        repeat=r.client.submit('element.move',doc,{'element':uid,'vector':[0,1,0]},operation_id_value=oid)
        r.check('duplicate-id-same-receipt',repeat['operation_id'],oid)
        stable=r.call('duplicate-after','elements.inspect',doc,{'element':uid})['element']['location']['start']
        r.check('duplicate-not-replayed',stable[1],after[1])
        # Intentionally discard a complete HTTP response after sending a new mutation.
        oid=str(uuid.uuid5(uuid.UUID(r.report['run_id']),'disconnect-move'))
        envelope={'schema_version':1,'operation_id':oid,'operation':'element.move','document':doc,'preconditions':{},'arguments':{'element':uid,'vector':[0,1,0]}}
        r.report['dropped_response_request']=envelope;r.write()
        if not r.report.get('dropped_response_send_started'):
            r.report['dropped_response_send_started']=True;r.write()
            body=canonical(envelope).encode();token=r.client._auth()
            request=(f'POST /v1/jobs HTTP/1.1\r\nHost: 127.0.0.1:49327\r\nAuthorization: Bearer {token}\r\nContent-Length: {len(body)}\r\nContent-Type: application/json\r\nConnection: close\r\n\r\n').encode()+body
            with socket.create_connection(('127.0.0.1',49327),timeout=10) as sock:
                sock.sendall(request);sock.shutdown(socket.SHUT_WR)
                # No response is consumed; native acceptance/completion is reconciled solely by UUID.
        final=r.client.wait(oid,45);r.report['steps']['disconnect-move']=final;r.write()
        if final['status']!='completed':raise RuntimeError('Dropped response unresolved; never replay')
        after_drop=r.call('disconnect-after','elements.inspect',doc,{'element':uid})['element']['location']['start']
        r.check('disconnect-single-move',after_drop[1]-stable[1],1)
        # Queued cancellation is best-effort; record races honestly.
        outcomes=[]
        for i in range(8):
            j=r.client.submit('api.lookup',{}, {'type':'Autodesk.Revit.DB.Wall','member':'Create'})
            cancelled=r.client.cancel(j['operation_id']);terminal=r.client.wait(j['operation_id'],10)
            outcomes.append({'operation_id':j['operation_id'],'cancel_response':cancelled['status'],'terminal_status':terminal['status']})
        r.report['cancellation_trials']=outcomes
        r.report['cancellation_verified']=any(x['terminal_status']=='cancelled' for x in outcomes)
        r.report['status']='passed';r.report['limitations']=['Synthetic hosting only, not manufacturer appliance fit','Cancellation races explicitly recorded; no forced running interruption','Native process-restart recovery not exercised']
    except Exception as e:r.report['status']='incomplete';r.report['error']=str(e);raise
    finally:r.write()

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--process-id',type=int,required=True);p.add_argument('--output-dir',required=True);run(p.parse_args())
