"""One requested video at a time, retaining every outcome across renderer callbacks."""
import json
from pathlib import Path
import wieland_paths as paths

ROOT=Path(__file__).resolve().parent.parent
RESULT=ROOT/'delivery/owner_videos_result.json'

def start(name):
    status=next(x for x in (ROOT/'phase20_results.md').read_text(encoding='utf-8').splitlines() if x.startswith('Status:'))
    if not status.startswith('Status: DONE'):raise RuntimeError('Phase20 final model must be DONE before owner renders')
    request=json.loads((ROOT/'owner_review/paths/RENDER_REQUEST').read_text(encoding='utf-8'))
    if name not in request['names']:raise RuntimeError('Path not requested: '+name)
    if paths.status().get('active'):raise RuntimeError('Another video is active')
    def completed(record):
        aggregate=json.loads(RESULT.read_text(encoding='utf-8')) if RESULT.exists() else {'requested_names':request['names'],'requested_at':request['requested_at'],'results':[]}
        outcomes=[]
        for row in record.get('rendered',[]):outcomes.append(dict(row,name=name))
        for row in record.get('refused',[]):outcomes.append(dict(row,name=name))
        if not outcomes:outcomes=[{'name':name,'refused':'No rendered or refusal outcome returned; inspect renderer record','renderer_record':record}]
        aggregate['results']=[x for x in aggregate['results'] if x['name']!=name]+outcomes
        RESULT.parent.mkdir(parents=True,exist_ok=True)
        RESULT.write_text(json.dumps(aggregate,indent=2),encoding='utf-8')
    previous=paths.up_to_date
    try:
        # Old metadata tracks the path, not changes to surrounding model geometry.
        paths.up_to_date=lambda file_path,path:False
        return paths.render_requested(only=[name],on_done=completed)
    finally:paths.up_to_date=previous

def status():return paths.status()
