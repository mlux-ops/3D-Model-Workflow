"""Full-path ledger of authored recovery/detail artifacts, excluding incidental engine caches."""
import csv
import datetime
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

DOCS=Path(__file__).resolve().parent.parent
REPO=DOCS.parents[2]
PROJECT=Path('D:/Unreal_Engine_Projects/Wieland1527 5.9')
REVIEW=PROJECT/'Saved/Wieland1529Review'
DATA=Path('E:/Wieland1529_site_data')
SINCE=datetime.datetime.fromisoformat('2026-11-15T17:07:00-06:00').timestamp()


def main():
    REVIEW.mkdir(parents=True,exist_ok=True)
    previews={'review/phase20/nearby_detail/S2_hybrid.0000.png':'S2_hybrid.png',
              'review/phase20/nearby_detail/scope_map.png':'scope_map.png',
              'review/phase20/round2/panorama/grazing_clear_y-050_realtime.0000.png':'grazing_clear_gold_coast.png'}
    for source,dest in previews.items():shutil.copy2(DOCS/source,REVIEW/dest)
    paths={Path(__file__).resolve()}
    result=subprocess.run(['git','diff','--name-only','c6309914^','HEAD'],cwd=REPO,capture_output=True,text=True,check=True)
    for rel in result.stdout.splitlines():
        p=REPO/rel
        if p.is_file():paths.add(p)
    for folder in (DATA/'phase20/nearby_detail',PROJECT/'Content/Wieland1529/Surroundings/NearbyDetail',
                   PROJECT/'Content/Wieland1529/Delivery/Paths',DOCS/'delivery/video_paths',
                   DOCS/'profiles/2026-11-15_P20R2',DOCS/'profiles/2026-11-15_P20EXT',
                   DOCS/'review/phase20/nearby_detail',
                   DOCS/'review/phase20/final_extension',
                   Path('D:/Wieland1529_delivery/video_paths_frames'),
                   Path('D:/Wieland1529_delivery/package/1529_Wieland_UE5.9_Delivery_2026-11-15_r3'),
                   Path('F:/My Drive/Folders/3D Model Workflow/3D Models/1529_Wieland_UE5.9_Delivery_2026-11-15_r3'),REVIEW):
        paths.update(p for p in folder.rglob('*') if p.is_file() and p.name!='FILES_WRITTEN.csv')
    paths.update(p for p in (DATA/'phase17/rasters/bldg1ft').glob('*') if p.is_file() and p.stat().st_mtime>=SINCE)
    paths.update(p for p in (DOCS/'tools/__pycache__').glob('*') if p.is_file() and p.stat().st_mtime>=SINCE and
                 (p.name.startswith('nearby_') or p.name.startswith('phase20_')))
    for root in (Path('D:/Wieland1529_delivery/package'),Path('F:/My Drive/Folders/3D Model Workflow/3D Models')):
        note=root/'1529_Wieland_UE5.9_Delivery_2026-11-14_r2/SUPERSEDED.md'
        if note.exists():paths.add(note)
    for rel in ('Wieland1529/L_Site_M4.umap','Wieland1529/Surroundings/L_Surroundings_R15.umap',
                'Wieland1529/Surroundings/L_Surroundings_P17.umap','Wieland1529/Surroundings/L_Skyline_P17.umap',
                'Wieland1529/Surroundings/L_Nearby_Detail.umap','Wieland1529/Lighting/L_Light_SummerAfternoon.umap',
                'Wieland1529/Surroundings/LVS_W1529_Surroundings.uasset'):
        p=PROJECT/'Content'/rel
        if p.exists():paths.add(p)
    profile=DOCS/'profiles/2026-11-13_M7/P20R2'
    paths.update(p for p in profile.rglob('*') if p.is_file())
    for name in ('exterior','roofdeck'):
        record=json.loads((profile/('capture_P20R2_'+name+'.json')).read_text(encoding='utf-8'))
        for job in record['jobs']:
            for name in job.get('new_csv_files',[]):
                p=Path(record['csv_folder'])/name
                if p.exists():paths.add(p)
    for record_path in (DOCS/'profiles/2026-11-15_P20EXT').glob('capture_*.json'):
        record=json.loads(record_path.read_text(encoding='utf-8'))
        for job in record.get('jobs',[]):
            for name in job.get('new_csv_files',[]):
                p=Path(record['csv_folder'])/name
                if p.exists():paths.add(p)
    rows=[]
    for p in sorted(paths,key=lambda p:str(p).lower()):
        digest=hashlib.sha256()
        with p.open('rb') as handle:
            for data in iter(lambda:handle.read(1024*1024),b''):digest.update(data)
        rows.append({'absolute_path':p.resolve().as_posix(),'bytes':p.stat().st_size,'sha256':digest.hexdigest()})
    target=REVIEW/'FILES_WRITTEN.csv'
    with target.open('w',encoding='utf-8',newline='') as handle:
        writer=csv.DictWriter(handle,fieldnames=['absolute_path','bytes','sha256']);writer.writeheader();writer.writerows(rows)
    print(json.dumps({'ledger':target.as_posix(),'files':len(rows),'bytes':sum(r['bytes'] for r in rows),
                      'report':(REVIEW/'RECOVERY_AND_NEARBY_DETAIL.md').as_posix()}))


if __name__=='__main__':main()
