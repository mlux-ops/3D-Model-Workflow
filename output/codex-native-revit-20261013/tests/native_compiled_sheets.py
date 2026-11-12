"""Flexible native C# execution, three-axis casework instance and two test sheets."""
import argparse
import json
import math
from pathlib import Path
from native_hosting_recovery import NativeRun


def normalize(v):
    length=math.sqrt(sum(x*x for x in v));return [x/length for x in v]
def cross(a,b):return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]


def run(opts):
    r=NativeRun(opts.output_dir,opts.process_id)
    try:
        plugin=str((Path(__file__).parent/'CompiledProbe/bin/Release/net8.0-windows/CodexNativeRevit.CompiledProbe.dll').resolve())
        def compiled(label,doc,args,query=False):
            return r.call(label,'compiled.query' if query else 'compiled.modify',doc,{'assembly':plugin,
                'type':'CodexNativeRevit.CompiledProbe.ProbeQuery' if query else 'CodexNativeRevit.CompiledProbe.ProbeModify',
                'purpose':'Disposable native acceptance '+label,'expected_changes':[] if query else [args.get('action','instance_comments')],
                'arguments':{'document_session_id':doc['session_id'],**args}})
        p=r.call('project','document.create',{}, {'template':r'C:\ProgramData\Autodesk\RVT 2025\Templates\Default_I_ENU.rte'});doc={'session_id':p['session_id']}
        r.call('family-load','family.load',doc,{'path':str(Path(opts.family).resolve()),'replacement_policy':'reject'})
        symbols=r.call('symbols','elements.query',doc,{'class':'FamilySymbol','types':True,'category':'OST_Casework'})['items']
        if len(symbols)!=1: raise RuntimeError('Expected one explicit loaded synthetic Casework type')
        symbol=symbols[0]
        level=r.call('levels','elements.query',doc,{'class':'Level'})['items'][0]['unique_id']
        instances=r.call('cabinet-run','family.place',doc,{'type':symbol['unique_id'],'instances':[{'point':[x,0,0],'level':level} for x in (0,3,6)]})['instances']
        duplicate=r.call('duplicate','type.duplicate',doc,{'type':symbol['unique_id'],'name':'Codex_Three_Axis_Modified'})
        for name,value in [('CodexWidth',2.5),('CodexDepth',1.75),('CodexHeight',3.5)]:
            r.call('set-'+name,'parameter.set',doc,{'element':duplicate['unique_id'],'name':name,'value':value,'allow_type_change':True})
        r.call('change-type','element.type',doc,{'element':instances[0]['unique_id'],'type':duplicate['unique_id']})
        shape=r.call('instance-geometry','elements.inspect',doc,{'element':instances[0]['unique_id'],'geometry':True})
        faces=[f for f in shape['geometry'] if f['kind']=='face' and f.get('normal')]
        areas=[max(f['area'] for f in faces if abs(f['normal'][i])>0.99) for i in range(3)]
        measured=[math.sqrt(areas[1]*areas[2]/areas[0]),math.sqrt(areas[0]*areas[2]/areas[1]),math.sqrt(areas[0]*areas[1]/areas[2])]
        for name,actual,expected in zip(['width','depth','height'],measured,[2.5,1.75,3.5]):r.check('native-'+name,actual,expected)
        r.check('native-volume',sum(g['volume'] for g in shape['geometry'] if g['kind']=='solid'),15.3125)
        unaffected=r.call('unrelated-type','elements.inspect',doc,{'element':instances[1]['unique_id']})['element']
        r.check('unrelated-type-unchanged',unaffected['type_id'],symbol['id'])
        comments=compiled('comments',doc,{'element_unique_id':instances[0]['unique_id'],'comment':'Codex disposable compiled API test'})
        r.report['compiled_comments_readback']=comments
        viewtypes=r.call('view-types','elements.query',doc,{'class':'ViewFamilyType','types':True})['items']
        byfamily={t['view_family']:t for t in viewtypes}
        three=r.call('3d','view.create',doc,{'type':byfamily['ThreeDimensional']['unique_id'],'kind':'3d','name':'CODEX - NATIVE PARAMETRIC CASEWORK','scale':24})
        r.call('3d-settings','view.settings',doc,{'view':three['unique_id'],'section_box':{'min':[-1,-1,-1],'max':[9,3,5]},'detail_level':'Fine','category_visibility':{'OST_Casework':True,'OST_Levels':False}})
        forward=normalize([-10,-15,-9]);right=normalize(cross(forward,[0,0,1]));up=normalize(cross(right,forward))
        compiled('camera',doc,{'action':'view_orientation','view_unique_id':three['unique_id'],'eye':[14,18,12],'up':up,'forward':forward})
        r.report['compiled_query']=compiled('query',doc,{'view_unique_id':three['unique_id']},query=True)
        sheet=r.call('sheet1','sheet.create',doc,{'number':'TEST-ID1.0','name':'DISPOSABLE THREE-AXIS CASEWORK'})
        viewport=r.call('viewport1','viewport.place',doc,{'sheet':sheet['unique_id'],'view':three['unique_id'],'center':[1,1,0]})
        r.call('viewport-label1','viewport.settings',doc,{'viewport':viewport['element']['unique_id'],'label_line_length':0.5,'label_offset':[0,0,0]})
        schedule=r.call('schedule','schedule.create',doc,{'category':'OST_Casework','name':'Native Casework Types','fields':['Family and Type','Count']})
        compiled('schedule-widths',doc,{'action':'schedule_widths','schedule_unique_id':schedule['unique_id'],'widths':[1,0.3]})
        scheduleinstance=r.call('schedule-place','schedule.place',doc,{'sheet':sheet['unique_id'],'schedule':schedule['unique_id'],'point':[2.6,1.8,0]})
        layout={'content_region':[0,0,4,3],'moves':[{'element':viewport['element']['unique_id'],'point':[1,1,0]},{'element':scheduleinstance['element']['unique_id'],'point':[2.6,1.8,0]}]}
        proposal=r.call('layout1-propose','layout.propose',doc,layout);r.check('layout1-valid',proposal['valid'],True);r.call('layout1-apply','layout.apply',doc,layout)
        plan=r.call('plan','view.create',doc,{'type':byfamily['FloorPlan']['unique_id'],'level':level,'kind':'plan','name':'CODEX - CASEWORK PLAN','scale':24})
        r.call('plan-crop','view.settings',doc,{'view':plan['unique_id'],'crop':{'min':[-1,-1,0],'max':[9,3,1]},'detail_level':'Fine'})
        elevation=compiled('elevation',doc,{'action':'create_elevation','elevation_type_unique_id':byfamily['Elevation']['unique_id'],'plan_view_unique_id':plan['unique_id'],'point':[4,6,0],'index':1,'name':'CODEX - CASEWORK ELEVATION','scale':24})
        ev=elevation['elevation']['unique_id']
        r.call('elevation-crop-full','view.settings',doc,{'view':ev,'crop':{'min':[-1,-1,0],'max':[9,5,10]},'detail_level':'Fine'})
        sheet2=r.call('sheet2','sheet.create',doc,{'number':'TEST-ID1.1','name':'DISPOSABLE PLAN AND ELEVATION'})
        vpplan=r.call('plan-place','viewport.place',doc,{'sheet':sheet2['unique_id'],'view':plan['unique_id'],'center':[1,1.5,0]})
        vpelev=r.call('elevation-place','viewport.place',doc,{'sheet':sheet2['unique_id'],'view':ev,'center':[2.8,1.5,0]})
        for label,vp in [('plan',vpplan),('elevation',vpelev)]:r.call(label+'-label','viewport.settings',doc,{'viewport':vp['element']['unique_id'],'label_line_length':0.5,'label_offset':[0,0,0]})
        layout2={'content_region':[0,0,4,3],'moves':[{'element':vpplan['element']['unique_id'],'point':[1,1.5,0]},{'element':vpelev['element']['unique_id'],'point':[2.8,1.5,0]}]}
        proposal=r.call('layout2-propose','layout.propose',doc,layout2);r.check('layout2-valid',proposal['valid'],True);r.call('layout2-apply','layout.apply',doc,layout2)
        coverage=r.call('layout2-coverage-propose','layout.propose',doc,layout2);r.check('layout2-full-coverage-valid',coverage['valid'],True);r.call('layout2-coverage-apply','layout.apply',doc,layout2)
        for label,view in [('casework',three),('sheet_TEST_ID1_0',sheet),('sheet_TEST_ID1_1',sheet2)]:r.call('capture-'+label,'capture.export',doc,{'view':view['unique_id'],'path_prefix':str(r.root/label),'pixels':1600})
        r.call('save-project','document.save_as',doc,{'path':str(r.root/'Codex_Three_Axis_Sheets_Test.rvt')})
        r.call('capture-sheet2-coverage-safe','capture.export',doc,{'view':sheet2['unique_id'],'path_prefix':str(r.root/'sheet_TEST_ID1_1_full_coverage'),'pixels':1600})
        r.call('save-project-coverage','document.save_as',doc,{'path':str(r.root/'Codex_Three_Axis_Sheets_Coverage_Checked.rvt')})
        r.report['status']='passed';r.report['limitations']=['Synthetic box category Casework, not manufacturer cabinets','Synthetic 4x3 sheet content regions, no production titleblock/print release','Visual/design acceptance requires user review','Compiled plugin directory enabled for this test process only']
    except Exception as e:r.report['status']='incomplete';r.report['error']=str(e);raise
    finally:r.write()

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--process-id',type=int,required=True);p.add_argument('--output-dir',required=True);p.add_argument('--family',required=True);run(p.parse_args())
