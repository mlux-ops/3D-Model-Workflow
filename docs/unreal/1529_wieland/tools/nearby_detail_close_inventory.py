"""Record historical site exclusions and newly fetched dataset provenance. No editor mutation."""
import csv
import json
from pathlib import Path

DOCS=Path(__file__).resolve().parent.parent
OUT=DOCS/'review/phase20/nearby_detail'
WORK=Path('E:/Wieland1529_site_data/phase20/nearby_detail')
EXCLUDED={'781075':'2022 building on the project lot; demolished before the new construction',
          '781331':'2022 building on the project lot; demolished before the new construction'}


def annotate(name):
    target=OUT/name
    rows=list(csv.DictReader(target.open(encoding='utf-8')))
    for row in rows:
        bid=row['county_id']
        row['excluded_historical_site']=bid in EXCLUDED
        row['exclusion_reason']=EXCLUDED.get(bid,'')
        row['active_extension_target']=bid not in EXCLUDED and row['earlier_detail_available']=='False'
    with target.open('w',encoding='utf-8',newline='') as handle:
        writer=csv.DictWriter(handle,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)


def append_row(path,row):
    with path.open(encoding='utf-8',newline='') as handle:
        reader=csv.DictReader(handle);fields=reader.fieldnames;existing=list(reader)
    key=fields[0]
    if any(r[key]==row[key] for r in existing):return
    with path.open('a',encoding='utf-8',newline='') as handle:
        writer=csv.DictWriter(handle,fieldnames=fields);writer.writerow(row)


def main():
    for name in ('building_scope.csv','building_evidence.csv'):annotate(name)
    (OUT/'scope_exclusions.json').write_text(json.dumps(EXCLUDED,indent=2),encoding='utf-8')
    source=WORK/'targets.csv'
    rows=list(csv.DictReader(source.open(encoding='utf-8')))
    active=[r for r in rows if r['bldg_id'] not in EXCLUDED]
    with (WORK/'active_targets.csv').open('w',encoding='utf-8',newline='') as handle:
        writer=csv.DictWriter(handle,fieldnames=list(active[0]));writer.writeheader();writer.writerows(active)
    roads=[WORK/'roads_osm.json',WORK/'roads_osm.source.txt']
    dsm=[WORK/'scope1ft_dsm.npz',WORK/'scope1ft_dsm.source.txt']
    # Raster helper uses the actual output filename plus .source.txt.
    if not dsm[1].exists():dsm[1]=WORK/'scope1ft_dsm.npz.source.txt'
    for title,files,what,url,licence,note in (
        ('Owner nearby detail extension: OSM roads',roads,'Street names and cross-street spacing for the extension boundary',
         'https://overpass-api.de/api/interpreter','Open Database Licence 1.0',
         '(c) OpenStreetMap contributors. No imagery or Google content.'),
        ('Owner nearby detail extension: ISGS DSM',dsm,'1 ft surface measurements over the expanded street-bounded area',
         'https://data.isgs.illinois.edu/arcgis/rest/services/Elevation/IL_Cook_DSM_2022/ImageServer',
         'ISGS service: no restrictions; cite Illinois State Geological Survey',
         'Reuses the already recorded ISGS 2022 dataset and terms; 498 per-building crops prepared separately. Clean built forms only.')):
        append_row(DOCS/'asset_downloads.csv',dict(name=title,files=len(files),size_mb=round(sum(p.stat().st_size for p in files)/1e6,3),
            what_it_is=what,source=url,licence=licence,evidence_or_note=note,kept_at=str(WORK).replace(chr(92),'/')))
    summary={'raw_scope_footprints':736,'historical_site_exclusions':EXCLUDED,
             'earlier_detailed_buildings':52,'active_extension_targets':len(active),
             'staged_native_forms':684,'staged_forms_excluded':2,'facade_detail':'pending owner decision; not complete'}
    (OUT/'inventory_status.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print(json.dumps(summary))


if __name__=='__main__':main()
