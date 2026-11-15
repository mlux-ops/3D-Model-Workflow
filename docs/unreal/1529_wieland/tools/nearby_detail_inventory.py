"""Map owner scope against existing measured outlines; road data from OSM, never Google."""
import csv
import datetime
import json
import pathlib
import sys
import urllib.parse
import urllib.request

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import polygonize, unary_union

import wieland_geo as geo

DOCS = pathlib.Path(__file__).resolve().parent.parent
DATA = pathlib.Path('E:/Wieland1529_site_data')
OUT = DOCS/'review/phase20/nearby_detail'
CACHE = DATA/'phase20/nearby_detail'
LAT,LON=41.910215,-87.635389
SITE=geo.state_plane_from_lat_lon(LAT,LON)
FT=geo.US_SURVEY_FOOT_M


def fetch_roads():
    CACHE.mkdir(parents=True,exist_ok=True)
    target=CACHE/'roads_osm.json'
    if not target.exists():
        query='[out:json][timeout:90];way[highway~"^(primary|secondary|tertiary|residential|unclassified|living_street)$"](around:1600,%s,%s);out tags geom;'% (LAT,LON)
        req=urllib.request.Request('https://overpass-api.de/api/interpreter?'+urllib.parse.urlencode({'data':query}),
            headers={'User-Agent':'Wieland1529-site-model/1.0 (private architectural visualisation)'})
        with urllib.request.urlopen(req,timeout=120) as response:
            raw=response.read()
        json.loads(raw)
        target.write_bytes(raw)
        (CACHE/'roads_osm.source.txt').write_text('OpenStreetMap contributors, ODbL 1.0. Public Overpass API, roads only. '+datetime.datetime.now().isoformat(),encoding='utf-8')
    return json.loads(target.read_text(encoding='utf-8'))


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    roads=fetch_roads()['elements']
    segments=[]
    named=[]
    for road in roads:
        points=[geo.state_plane_from_lat_lon(p['lat'],p['lon']) for p in road.get('geometry',[])]
        if len(points)<2:continue
        line=LineString(points)
        segments.append(line)
        named.append((road.get('tags',{}).get('name',''),line))
    # Polygonal street blocks are measured from the actual road network, rather than an assumed block length.
    clip=box(SITE[0]-4500,SITE[1]-4500,SITE[0]+4500,SITE[1]+4500)
    network=unary_union([s.intersection(clip) for s in segments]+[clip.boundary])
    blocks=[p for p in polygonize(network) if p.area>1000]
    core_roads=[s for name,s in named if 'Wieland' in name or 'Wells' in name]
    roads_union=unary_union(core_roads)
    # Working interpretation: two actual cross-street intervals north/south on Wieland and Wells;
    # the surrounding two-block band is selected by block adjacency below.
    cross=[]
    for name,line in named:
        if name and 'Wieland' not in name and 'Wells' not in name:
            hit=line.intersection(roads_union)
            if not hit.is_empty:
                geoms=list(hit.geoms) if hasattr(hit,'geoms') else [hit]
                for p in geoms:
                    if p.geom_type=='Point':cross.append((p.y,name,p.x))
    # Deduplicate a cross-street across both parallel roads and divided-road carriageways.
    by_name={}
    for y,name,x in cross:
        if name.startswith('West '):by_name.setdefault(name,[]).append(y)
    crossings=[(float(np.median(ys)),name) for name,ys in by_name.items()]
    north=sorted((y,name) for y,name in crossings if y>SITE[1]+20)
    south=sorted(((y,name) for y,name in crossings if y<SITE[1]-20),reverse=True)
    def street_east(name):
        line=unary_union([s for n,s in named if n==name])
        return line.interpolate(line.project(Point(SITE))).x
    core_w=street_east('North Wieland Street')-135
    core_e=street_east('North Wells Street')+135
    low,high=south[1][0],north[1][0]
    inner_region=box(core_w,low,core_e,high)
    middle_region=box(street_east('North North Park Avenue')-135,south[2][0],
                      street_east('North LaSalle Drive')+135,north[2][0])
    region=box(street_east('North Orleans Street')-135,south[3][0],
               street_east('North Clark Street')+135,north[3][0])
    features=json.loads((DATA/'phase17/county/county_footprints_2022_viewbox.json').read_text(encoding='utf-8'))['features']
    old={n.removeprefix('SB_') for n in json.loads((DOCS/'review/phase7/phase4_hidden_buildings.json').read_text(encoding='utf-8'))['hidden_with_earlier_detailed_buildings']}
    records=[]
    outlines=[]
    for f in features:
        ring=f['geometry']['rings'][0]
        if not ring:continue
        poly=Polygon(ring).buffer(0)
        if poly.is_empty or not region.intersects(poly):continue
        bid=str(f['attributes']['OBJECTID'])
        depth=0 if inner_region.intersects(poly) else (1 if middle_region.intersects(poly) else 2)
        a=f['attributes']
        record={'county_id':bid,'band':depth,'earlier_detail_available':bid in old,
                'centroid_east_ft':round(poly.centroid.x,2),'centroid_north_ft':round(poly.centroid.y,2),
                'ground_ft':a.get('Ground_Z'),'max_point_ft':a.get('Max_Point'),
                'existing_p17_local':(DATA/'phase17/meshes_zone12_clean'/('P17RZ_'+bid+'.json')).exists(),
                'existing_dsm':(DATA/'phase17/rasters/bldg1ft'/(bid+'_dsm.npz')).exists()}
        records.append(record)
        outlines.append((poly,record))
    with (OUT/'building_scope.csv').open('w',newline='',encoding='utf-8') as handle:
        writer=csv.DictWriter(handle,fieldnames=list(records[0]))
        writer.writeheader();writer.writerows(records)
    summary={'interpretation':'Two cross-street intervals north and south on Wieland/Wells, plus two adjoining block rings; provisional map for owner review',
        'crossings':[(round(y),n) for y,n in sorted(crossings) if region.bounds[1]-10<=y<=region.bounds[3]+10],
        'inner_limits':{'north':north[1][1],'south':south[1][1],'streets':['North Wieland Street','North Wells Street']},
        'outer_limits':{'north':north[3][1],'south':south[3][1],'west':'North Orleans Street','east':'North Clark Street'},
        'north_ft':high,'south_ft':low,'buildings':len(records),
        'earlier_available':sum(r['earlier_detail_available'] for r in records),
        'bands':{str(d):sum(r['band']==d for r in records) for d in (0,1,2)}}
    (OUT/'scope_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    bounds=region.bounds
    width=1200;height=1800;margin=75
    scale=min((width-2*margin)/(bounds[2]-bounds[0]),(height-2*margin)/(bounds[3]-bounds[1]))
    def xy(x,y):return (margin+(x-bounds[0])*scale,height-margin-(y-bounds[1])*scale)
    image=Image.new('RGB',(width,height),'#f3f0e8');draw=ImageDraw.Draw(image)
    for b,colour in ((region,'#ece7d9'),(middle_region,'#e4e8d9'),(inner_region,'#d5e7dc')):
        draw.polygon([xy(x,y) for x,y in b.exterior.coords],fill=colour,outline='#c3bfb5')
    for poly,r in outlines:
        geoms=[poly] if poly.geom_type=='Polygon' else list(poly.geoms)
        for p in geoms:draw.polygon([xy(x,y) for x,y in p.exterior.coords],fill='#b46943' if r['earlier_detail_available'] else '#a6a6a0',outline='#faf7ef')
    font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',19)
    for name in sorted(set(name for name,line in named if name)):
        line=unary_union([s for n,s in named if n==name]).intersection(region)
        if line.is_empty:continue
        if line.geom_type!='LineString':
            pieces=[part for part in getattr(line,'geoms',[]) if part.geom_type=='LineString']
            if not pieces:continue
            line=max(pieces,key=lambda part:part.length)
        c=line.interpolate(.5,normalized=True)
        draw.text(xy(c.x,c.y),name,fill='#183b2a',font=font,stroke_width=2,stroke_fill='#f3f0e8')
    x,y=xy(*SITE);draw.ellipse((x-7,y-7,x+7,y+7),fill='#b92c32');draw.text((x+12,y),'1529 N Wieland',fill='#a0242a')
    draw.text((75,22),'Provisional scope: inner street blocks + two adjoining block bands. Brown = existing earlier detail.',fill='#273b30')
    draw.text((75,45),'NORTH UP. Sources: Cook County 2022 outlines; OpenStreetMap contributors (ODbL).',fill='#273b30')
    image.save(OUT/'scope_map.png')
    print(json.dumps(summary))


if __name__=='__main__':main()
