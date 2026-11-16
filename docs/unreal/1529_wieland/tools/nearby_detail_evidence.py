"""Join existing public city/OSM/assessor evidence to nearby measured county footprints."""
import csv
import json
from pathlib import Path

from shapely.geometry import Polygon, shape
from shapely.strtree import STRtree

import wieland_geo as geo

DOCS=Path(__file__).resolve().parent.parent
BASE=Path('E:/Wieland1529_site_data/phase17')
OUT=DOCS/'review/phase20/nearby_detail'


def main():
    scope=list(csv.DictReader((OUT/'building_scope.csv').open(encoding='utf-8')))
    ids={r['county_id'] for r in scope}
    county={str(f['attributes']['OBJECTID']):f for f in json.loads((BASE/'county/county_footprints_2022_viewbox.json').read_text(encoding='utf-8'))['features'] if str(f['attributes']['OBJECTID']) in ids}
    keys=sorted(county)
    polys=[Polygon(county[k]['geometry']['rings'][0]).buffer(0) for k in keys]
    tree=STRtree(polys)
    bounds=(min(p.bounds[0] for p in polys),min(p.bounds[1] for p in polys),max(p.bounds[2] for p in polys),max(p.bounds[3] for p in polys))
    lat0,lon0=geo.lat_lon_from_state_plane(bounds[0],bounds[1])
    lat1,lon1=geo.lat_lon_from_state_plane(bounds[2],bounds[3])
    city_matches={};osm_matches={}
    def matches(poly):
        if poly.is_empty:return []
        result=[]
        for index in tree.query(poly,predicate='intersects'):
            a=polys[int(index)]
            cover=a.intersection(poly).area/max(1,min(a.area,poly.area))
            if cover>=.3:result.append((keys[int(index)],cover))
        return result
    city=json.loads((BASE/'city/chicago_footprints_box.geojson').read_text(encoding='utf-8'))
    for feature in city['features']:
        geometry=feature.get('geometry')
        if not geometry:continue
        poly=shape(geometry)
        if poly.is_empty:continue
        b=poly.bounds
        if b[2]<lon0-.001 or b[0]>lon1+.001 or b[3]<lat0-.001 or b[1]>lat1+.001:continue
        parts=[poly] if poly.geom_type=='Polygon' else list(poly.geoms)
        for part in parts:
            if part.geom_type!='Polygon':continue
            mapped=Polygon([geo.state_plane_from_lat_lon(y,x) for x,y in part.exterior.coords]).buffer(0)
            for bid,score in matches(mapped):
                if score>city_matches.get(bid,(0,{}))[0]:city_matches[bid]=(score,feature['properties'])
    seen=set()
    for file in sorted((BASE/'osm').glob('osm_*.json')):
        for element in json.loads(file.read_text(encoding='utf-8')).get('elements',[]):
            token=(element['type'],element['id'])
            if token in seen:continue
            seen.add(token)
            tags=element.get('tags',{})
            points=element.get('geometry',[])
            if not points or not ('building' in tags or 'building:part' in tags):continue
            b=(min(p['lon'] for p in points),min(p['lat'] for p in points),max(p['lon'] for p in points),max(p['lat'] for p in points))
            if b[2]<lon0-.001 or b[0]>lon1+.001 or b[3]<lat0-.001 or b[1]>lat1+.001:continue
            if len(points)<4:continue
            poly=Polygon([geo.state_plane_from_lat_lon(p['lat'],p['lon']) for p in points]).buffer(0)
            for bid,score in matches(poly):
                if score>osm_matches.get(bid,(0,{}))[0]:osm_matches[bid]=(score,tags)
    assessor={}
    source=BASE/'assessor/zone12_assessor.csv'
    if source.exists():assessor={r['bldg_id']:r for r in csv.DictReader(source.open(encoding='utf-8'))}
    records=[]
    for r in scope:
        bid=r['county_id'];c=city_matches.get(bid,(0,{}))[1];o=osm_matches.get(bid,(0,{}))[1];a=assessor.get(bid,{})
        street=o.get('addr:street') or ' '.join(str(c.get(k,'')) for k in ('pre_dir1','st_name1','st_type1')).strip()
        number=o.get('addr:housenumber') or c.get('f_add1','')
        stories=o.get('building:levels') or c.get('stories') or c.get('no_stories','')
        if str(stories) in ('0','0.0'):stories=''
        records.append(dict(r,address=(str(number)+' '+street).strip(),name=o.get('name') or c.get('bldg_name1',''),
            storeys=stories,storeys_source='OSM building:levels' if o.get('building:levels') else ('City footprint record' if stories else ''),
            wall_material=o.get('building:material') or o.get('building:facade:material') or a.get('ext_wall',''),
            wall_colour=o.get('building:colour',''),roof_shape=o.get('roof:shape',''),roof_material=o.get('roof:material',''),
            city_overlap=round(city_matches.get(bid,(0,{}))[0],3),osm_overlap=round(osm_matches.get(bid,(0,{}))[0],3),
            facade_layout_source='Earlier detailed model' if r['earlier_detail_available']=='True' else 'No verified street-facing photograph',
            measured_roof_source='ISGS 2022 surface; clean-form fitting'))
    with (OUT/'building_evidence.csv').open('w',encoding='utf-8',newline='') as handle:
        writer=csv.DictWriter(handle,fieldnames=list(records[0]));writer.writeheader();writer.writerows(records)
    print(json.dumps({'buildings':len(records),'city_matches':len(city_matches),'osm_matches':len(osm_matches),
        'storeys':sum(bool(r['storeys']) for r in records),'wall_materials':sum(bool(r['wall_material']) for r in records),
        'wall_colours':sum(bool(r['wall_colour']) for r in records)}))


if __name__=='__main__':main()
