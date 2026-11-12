"""Native drafting, annotations, dimension, mirror/delete, and dependency fencing."""
import argparse
import json
from pathlib import Path
from native_hosting_recovery import NativeRun

def main():
    p=argparse.ArgumentParser();p.add_argument('--process-id',type=int,required=True);p.add_argument('--output-dir',required=True);o=p.parse_args();r=NativeRun(o.output_dir,o.process_id)
    try:
        project=r.call('project','document.create',{}, {'template':r'C:\ProgramData\Autodesk\RVT 2025\Templates\Default_I_ENU.rte'});d={'session_id':project['session_id']}
        types=r.call('view-types','elements.query',d,{'class':'ViewFamilyType','types':True})['items'];byfamily={t['view_family']:t for t in types}
        drafting=r.call('drafting','view.create',d,{'type':byfamily['Drafting']['unique_id'],'kind':'drafting','name':'CODEX DISPOSABLE DRAFTING','scale':24})
        texttype=r.call('text-types','elements.query',d,{'class':'TextNoteType','types':True})['items'][0]['unique_id']
        text=r.call('text','annotation.text',d,{'view':drafting['unique_id'],'type':texttype,'point':[0,0,0],'text':'CODEX NATIVE TEST ONLY'})
        lines=r.call('lines','annotation.lines',d,{'view':drafting['unique_id'],'segments':[{'start':[0,-1,0],'end':[3,-1,0]},{'start':[3,-1,0],'end':[3,-2,0]}]})
        r.check('detail-lines-count',len(lines),2)
        regions=r.call('region-types','elements.query',d,{'class':'FilledRegionType','types':True})['items']
        if regions:r.call('filled-region','annotation.filled_region',d,{'view':drafting['unique_id'],'type':regions[0]['unique_id'],'profile':[[0,-3,0],[2,-3,0],[2,-4,0],[0,-4,0]]})
        else:r.report['filled_region']='requires explicit loaded type; not tested'
        r.call('drafting-duplicate','view.duplicate',d,{'view':drafting['unique_id'],'name':'CODEX DUPLICATE WITH DETAILS','option':'WithDetailing'})
        count_before=r.call('text-before-failure','elements.query',d,{'class':'TextNote','limit':500})['items']
        steps=[{'id':'bad-view','depends_on':[],'operation':'annotation.text','document':d,'arguments':{'view':'missing-view','type':texttype,'point':[0,0,0],'text':'THIS MUST FAIL'}},
            {'id':'dependent-text','depends_on':['bad-view'],'operation':'annotation.text','document':d,'arguments':{'view':drafting['unique_id'],'type':texttype,'point':[0,0,0],'text':'THIS MUST BE SKIPPED'}},
            {'id':'independent-read','depends_on':[],'operation':'elements.query','document':d,'arguments':{'class':'TextNote'}}]
        batch=r.client.batch(steps,batch_id=r.report['run_id'],timeout_seconds=30);r.report['dependency_batch']=batch;r.write()
        outcomes=batch['steps'] if 'steps' in batch else batch['results']
        r.check('dependent-blocked',outcomes['dependent-text']['status'],'blocked')
        r.check('independent-completed',outcomes['independent-read']['status'],'completed')
        count_after=r.call('text-after-failure','elements.query',d,{'class':'TextNote','limit':500})['items'];r.check('dependent-did-not-create',len(count_after),len(count_before))
        level=r.call('levels','elements.query',d,{'class':'Level'})['items'][0]['unique_id'];walltype=r.call('wall-types','elements.query',d,{'class':'WallType','types':True})['items'][0]['unique_id']
        wall=r.call('wall','wall.create',d,{'type':walltype,'level':level,'start':[0,0,0],'end':[8,0,0],'height':6})
        geometry=r.call('wall-geometry','elements.inspect',d,{'element':wall['unique_id'],'geometry':True})
        plan=r.call('plan','view.create',d,{'type':byfamily['FloorPlan']['unique_id'],'level':level,'kind':'plan','name':'CODEX DIMENSION PLAN','scale':24})
        refs=[f['reference'] for f in geometry['geometry'] if f.get('normal') and abs(f['normal'][0])>0.99]
        dimension=r.call('dimension','annotation.dimension',d,{'view':plan['unique_id'],'start':[0,-2,0],'end':[8,-2,0],'references':refs})
        ps=r.call('dimension-parameters','parameters.query',d,{'element':dimension['unique_id']})['instance']
        values=[p for p in ps if p['name']=='Value' and p['storage_type']=='Double']
        if len(values)==1:r.check('native-dimension-length',values[0]['value'],8)
        else:r.report['dimension_readback']=ps
        mirrored=r.call('mirror','element.mirror',d,{'element':wall['unique_id'],'normal':[1,0,0],'origin':[0,0,0],'copy':True});r.check('mirror-copy-count',len(mirrored['after']),1)
        r.call('wall-curve','element.curve',d,{'element':wall['unique_id'],'start':[0,0,0],'end':[8,1,0]})
        changed=r.call('wall-curve-readback','elements.inspect',d,{'element':wall['unique_id']})['element'];r.check('curve-end-y',changed['location']['end'][1],1)
        delete=r.call('delete-preview','element.delete_preview',d,{'element':text['unique_id']})
        deletion=r.call('delete','element.delete',d,{'element':text['unique_id'],'expected_deleted_ids':delete['deleted_ids_if_applied']});r.check('deleted-target-present',text['id'] in deletion['deleted_ids'],True)
        r.call('capture','capture.export',d,{'view':drafting['unique_id'],'path_prefix':str(r.root/'drafting-native'),'pixels':1200})
        r.report['status']='passed';r.report['limitations']=['Tag placement not included; requires an explicit compatible tag fixture','Native dependent batch stops failed view prerequisites','No production annotations changed']
    except Exception as e:r.report['status']='incomplete';r.report['error']=str(e);raise
    finally:r.write()

if __name__=='__main__':main()
