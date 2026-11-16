"""Extend measured site streets outside the preserved Phase 7 domain.

Offline only. Road centre lines: cached OSM/ODbL; elevations: measured ISGS DTM.
Widths without source dimensions are visualisation assumptions, reported by name.
No imagery, Google content, trees, signs, editor operations, or old mesh changes.
"""
from __future__ import annotations

import argparse
import datetime
import json
import math
from pathlib import Path

import numpy as np
import shapely
from PIL import Image, ImageDraw
from scipy import ndimage
from shapely import affinity, wkt
from shapely.geometry import LineString, MultiPoint, Point, Polygon, box
from shapely.ops import unary_union
from shapely.strtree import STRtree

import wieland_geo as geo

DOCS = Path(__file__).resolve().parent.parent
DATA = Path('E:/Wieland1529_site_data')
CACHE = DATA/'phase20/nearby_detail'
OUT = CACHE/'streets'
REVIEW = DOCS/'review/phase20/nearby_detail'
CM = geo.CM_PER_US_SURVEY_FOOT
CELL = 200.0
TILE = 5000.0
KERB = 13.0
KERB_WIDTH = 15.0
KERB_STEP = 100.0
LOT = box(-1508.76, -3115.1, 0.0, 0.0)


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, allow_nan=False, separators=(',', ':')), encoding='utf-8')


def parts(shape, kind='Polygon'):
    if shape.is_empty:
        return []
    if shape.geom_type == kind:
        return [shape]
    if hasattr(shape, 'geoms'):
        return [p for g in shape.geoms for p in parts(g, kind)]
    return []


def bilinear(field, a, b):
    a = np.clip(a, 0, field.shape[0]-1.001)
    b = np.clip(b, 0, field.shape[1]-1.001)
    i, j = np.floor(a).astype(int), np.floor(b).astype(int)
    u, v = a-i, b-j
    return ((1-u)*(1-v)*field[i,j] + u*(1-v)*field[i+1,j]
            + (1-u)*v*field[i,j+1] + u*v*field[i+1,j+1])


class Height:
    def __init__(self, frame, region_map, old_domain):
        self.frame, self.old_domain = frame, old_domain
        data = np.load(DATA/'phase17/rasters/view6ft_dtm.npz')
        z, x0, y1, cell = data['z'], float(data['x0']), float(data['y1']), float(data['cell'])
        e0,n0,e1,n1 = region_map.buffer(150).bounds
        j0 = max(0, int((e0-x0)/cell)); j1 = min(z.shape[1], int((e1-x0)/cell)+2)
        i0 = max(0, int((y1-n1)/cell)); i1 = min(z.shape[0], int((y1-n0)/cell)+2)
        self.dtm = z[i0:i1,j0:j1].astype(np.float64)
        bad = ~np.isfinite(self.dtm) | (self.dtm < -1000)
        if bad.any():
            _, inds = ndimage.distance_transform_edt(bad, return_indices=True)
            self.dtm = self.dtm[inds[0], inds[1]]
        # About 3.7m sigma removes source-grid steps, without inventing building heights.
        self.dtm = ndimage.gaussian_filter(self.dtm, 2.0)
        self.x0, self.y1, self.cell = x0+j0*cell, y1-i0*cell, cell
        # Read the saved top-surface triangles themselves at the preserved edge.
        # This accounts for the original 1m triangulation and stored rounding.
        boundary_band=old_domain.boundary.buffer(200)
        self.seam_xyz=[];seam_shapes=[]
        for path in sorted((DOCS/'review/phase7/ground/mesh').glob('SW_*.json')):
            obj=json.loads(path.read_text(encoding='utf-8'))
            if obj['kind'] not in ('ground','road'):continue
            v=np.asarray(obj['vertices'],float)+np.asarray(obj['pivot'],float)
            ti=np.asarray(obj['triangles'],int)
            xyz=v[ti]
            # Reject vertical faces and triangles away from the old perimeter.
            ab=xyz[:,1,:2]-xyz[:,0,:2];ac=xyz[:,2,:2]-xyz[:,0,:2]
            flat=np.abs(ab[:,0]*ac[:,1]-ab[:,1]*ac[:,0])>.01
            for tri in xyz[flat]:
                shape=Polygon(tri[:,:2])
                if boundary_band.intersects(shape):
                    seam_shapes.append(shape);self.seam_xyz.append(tri)
        self.seam_tree=STRtree(seam_shapes)
        self.seam_boundary=old_domain.boundary
        self.cache = {}

    def old_exact(self,x,y):
        point=Point(x,y)
        point=self.seam_boundary.interpolate(self.seam_boundary.project(point))
        ix=int(self.seam_tree.nearest(point))
        tri=self.seam_xyz[ix]
        # Use the closest actual stored triangle point; rounding can move the edge <.01cm.
        shape=self.seam_tree.geometries[ix]
        if not shape.covers(point):
            from shapely.ops import nearest_points
            point=nearest_points(shape,point)[0]
        a,b,c=tri
        uv=np.linalg.solve(np.column_stack([b[:2]-a[:2],c[:2]-a[:2]]),np.array([point.x,point.y])-a[:2])
        return float(a[2]+uv[0]*(b[2]-a[2])+uv[1]*(c[2]-a[2]))

    def upper(self, x, y):
        key=(round(x,3),round(y,3))
        if key not in self.cache:
            e,n = self.frame.map_from_level(x,y)
            z = float(bilinear(self.dtm, (self.y1-n)/self.cell-.5, (e-self.x0)/self.cell-.5))
            z = self.frame.origin_z_cm+(z-self.frame.origin_height_ft)*CM
            dist = Point(x,y).distance(self.old_domain)
            old = self.old_exact(x,y) if dist<1500 else z
            t = min(1.0, dist/1500.0)
            t = t*t*(3-2*t)
            self.cache[key] = old*(1-t)+z*t
        return self.cache[key]

    def road(self, x, y):
        # Both new surfaces meet the actual old top at the preserved boundary.
        # The 13cm road drop is introduced smoothly over the same 15m apron.
        # This avoids double-lowering where an old road reaches the seam.
        dist = Point(x,y).distance(self.old_domain)
        t = min(1.0, dist/1500.0)
        t=t*t*(3-2*t)
        return self.upper(x,y)-KERB*t


class Mesh:
    def __init__(self, name, pivot):
        self.name, self.pivot = name, list(pivot)+([0.0] if len(pivot)==2 else [])
        self.vertices, self.triangles, self.tri_mat, self.uv, self.index = [],[],[],[],{}
        self.areas = [0.0,0.0,0.0]
        self.winding_errors = 0
        self.rejected_quantized = 0
        self.post_round_flips = 0
        self.max_edge = 0.0

    def vertex(self, p, uv):
        key = tuple(round(v,2) for v in p)+tuple(round(v,4) for v in uv)
        if key not in self.index:
            self.index[key] = len(self.vertices)
            self.vertices.append([round(p[0]-self.pivot[0],2),round(p[1]-self.pivot[1],2),round(p[2],2)])
            self.uv.append([round(uv[0],4),round(uv[1],4)])
        return self.index[key]

    def tri(self, a,b,c, mat, outward=(0,0,1), uv=None):
        a,b,c = np.asarray(a),np.asarray(b),np.asarray(c)
        normal = np.cross(b-a,c-a)
        if np.linalg.norm(normal)<.001:
            return
        if np.dot(normal,outward)>0:
            b,c = c,b
            if uv is not None:
                uv = [uv[0],uv[2],uv[1]]
        if uv is None:
            uv = [[p[0]/100,p[1]/100] for p in (a,b,c)]
        inds=[self.vertex(p,u) for p,u in zip((a,b,c),uv)]
        stored=np.asarray([self.vertices[i] for i in inds],float)
        normal=np.cross(stored[1]-stored[0],stored[2]-stored[0])
        if len(set(inds))<3 or np.linalg.norm(normal)<.001:
            self.rejected_quantized+=1
            return
        if np.dot(normal,outward)>0:
            inds[1],inds[2]=inds[2],inds[1]
            stored[[1,2]]=stored[[2,1]]
            normal=-normal
            self.post_round_flips+=1
        self.triangles.append(inds)
        self.tri_mat.append(mat)
        self.areas[mat] += np.linalg.norm(normal)/20000.0
        self.max_edge=max(self.max_edge,*(float(np.linalg.norm(q-p)) for p,q in ((a,b),(b,c),(c,a))))
        self.winding_errors += int(np.dot(normal,outward)>0.0001)

    def finish(self, path):
        obj={'name':self.name,'kind':'street','zone':'nearby_detail','pivot':self.pivot,
             'vertices':self.vertices,'triangles':self.triangles,'tri_mat':self.tri_mat,'uv0_m':self.uv}
        write_json(path,obj)
        return {'name':self.name,'path':str(path),'vertices':len(self.vertices),'triangles':len(self.triangles),
                'surface_area_m2':self.areas,'max_edge_cm':round(self.max_edge,2),'winding_errors':self.winding_errors,
                'rejected_quantized':self.rejected_quantized,'post_round_flips':self.post_round_flips}


def prepare():
    frame=geo.LevelFrame.load(DOCS/'review/phase2/level_frame.json')
    theta=math.radians(frame.north_grid_bearing_deg)
    a,b,d,e=-CM*math.sin(theta),-CM*math.cos(theta),-CM*math.cos(theta),CM*math.sin(theta)
    tr=[a,b,d,e,frame.origin_x_cm-a*frame.origin_east_ft-b*frame.origin_north_ft,
        frame.origin_y_cm-d*frame.origin_east_ft-e*frame.origin_north_ft]
    def local(s): return affinity.affine_transform(s,tr)
    data=json.loads((CACHE/'roads_osm.json').read_text(encoding='utf-8'))['elements']
    named=[]
    for r in data:
        pts=[geo.state_plane_from_lat_lon(p['lat'],p['lon']) for p in r.get('geometry',[])]
        if len(pts)>1:
            named.append((r,LineString(pts)))
    site=geo.state_plane_from_lat_lon(41.910215,-87.635389)
    core=unary_union([l for r,l in named if any(n in r.get('tags',{}).get('name','') for n in ('Wieland','Wells'))])
    crossings={}
    for r,l in named:
        n=r.get('tags',{}).get('name','')
        if n.startswith('West '):
            for p in parts(l.intersection(core),'Point'):
                crossings.setdefault(n,[]).append(p.y)
    cross=[(float(np.median(ys)),n) for n,ys in crossings.items()]
    north=sorted((y,n) for y,n in cross if y>site[1]+20)
    south=sorted(((y,n) for y,n in cross if y<site[1]-20),reverse=True)
    def east(name):
        line=unary_union([l for r,l in named if r.get('tags',{}).get('name')==name])
        return line.interpolate(line.project(Point(site))).x
    region_map=box(east('North Orleans Street')-135,south[3][0],east('North Clark Street')+135,north[3][0])
    region=local(region_map)
    cover=np.load(DOCS/'review/phase7/ground/cover.npz')
    inside=np.load(DOCS/'review/phase7/ground/sources.npz')['inside']
    ii,jj=np.nonzero(inside & ~ndimage.binary_erosion(inside))
    old_domain=MultiPoint(np.column_stack([float(cover['x0'])+(ii+.5)*float(cover['step']),
        float(cover['y0'])+(jj+.5)*float(cover['step'])])).convex_hull.buffer(-10)
    old_road=wkt.loads(json.loads((DOCS/'review/phase7/ground/shapes.json').read_text(encoding='utf-8'))['roadway'])
    selected=[(r,local(l).intersection(region.buffer(2500))) for r,l in named if l.intersects(region_map.buffer(100))]
    # Fit a name's width from perpendicular sections of the earlier built road.
    measurements={}
    for r,l in selected:
        name=r.get('tags',{}).get('name','unnamed')
        for line in parts(l,'LineString'):
            for s in np.arange(500,line.length-500,350):
                p=line.interpolate(s)
                if not old_domain.buffer(-600).contains(p): continue
                q=line.interpolate(s-50);t=line.interpolate(s+50)
                dx,dy=t.x-q.x,t.y-q.y
                norm=math.hypot(dx,dy)
                if norm<1: continue
                nx,ny=-dy/norm,dx/norm
                section=LineString([(p.x-2200*nx,p.y-2200*ny),(p.x+2200*nx,p.y+2200*ny)])
                widths=[piece.length for piece in parts(section.intersection(old_road),'LineString')
                        if piece.distance(p)<140 and 400<piece.length<2500]
                if widths: measurements.setdefault(name,[]).append(min(widths))
    road_buffers=[];walk_buffers=[];records=[]
    defaults={'primary':1800,'secondary':1350,'tertiary':1250,'residential':760,'unclassified':760,'living_street':650}
    for r,line in selected:
        tags=r.get('tags',{});name=tags.get('name','unnamed'); highway=tags.get('highway','residential')
        measured=measurements.get(name,[])
        width=defaults.get(highway,760);basis='inferred road-class width'
        if len(measured)>=3:
            width=float(np.percentile(measured,30));basis='30th percentile of earlier Phase 7 road cross-sections'
        elif tags.get('width'):
            try:
                width=float(tags['width'].split()[0])*100;basis='OSM tagged width (not independently surveyed)'
            except ValueError: pass
        width=max(450,min(2200,width))
        walk=240 if highway in ('primary','secondary','tertiary') else 210
        rb=line.buffer(width/2,quad_segs=4,cap_style=2,join_style=1)
        wb=line.buffer(width/2+walk,quad_segs=5,cap_style=2,join_style=1)
        road_buffers.append(rb);walk_buffers.append(wb)
        records.append({'osm_way':r['id'],'name':name,'highway':highway,'road_width_m':round(width/100,3),
            'sidewalk_width_m':walk/100,'basis':basis,'calibration_sections':len(measured),'centreline_length_m':round(line.length/100,2)})
    county=json.loads((DATA/'phase17/county/county_footprints_2022_viewbox.json').read_text(encoding='utf-8'))['features']
    builds=[]
    for f in county:
        p=Polygon(f['geometry']['rings'][0]).buffer(0)
        if p.intersects(region_map.buffer(50)):builds.append(local(p))
    buildings=unary_union(builds)
    exclusion=old_domain.union(LOT)
    raw_road=unary_union(road_buffers).intersection(region).difference(exclusion)
    road=raw_road.difference(buildings.buffer(15)).buffer(0)
    walk=unary_union(walk_buffers).intersection(region).difference(road).difference(exclusion).difference(buildings.buffer(20)).buffer(0)
    # Keep only the pavement strip adjacent to an actual road after footprint clipping.
    walk=walk.intersection(road.buffer(260)).buffer(0)
    # Curb bands occupy 15cm of sidewalk, so there is no coplanar overlap.
    kerb_band=road.buffer(KERB_WIDTH).difference(road).intersection(walk)
    sidewalk=walk.difference(kerb_band).buffer(0)
    height=Height(frame,region_map,old_domain)
    info={'created':datetime.datetime.now().isoformat(),'boundary_map_ft':list(region_map.bounds),
        'limits':{'south':south[3][1],'north':north[3][1],'west':'North Orleans Street','east':'North Clark Street'},
        'source':'OpenStreetMap contributors, ODbL 1.0; ISGS 2022 measured DTM; preserved Phase 7 source ground',
        'inference':'Road widths calibrated from old roadway where available; other widths and all sidewalk widths are labelled visualisation assumptions, not surveyed kerb lines.',
        'preserved':'All existing Phase 7 ground/road/kerb meshes and project lot; no changes to native editor or source meshes.',
        'elevations':'6ft DTM with 3.7m Gaussian smoothing; 15m smooth blend to actual saved Phase 7 surface triangles. Both new surfaces meet the old top; 13cm kerb upstand grows smoothly across that apron.',
        'kerb_height_cm':KERB,'grid_cell_cm':CELL,'tile_cm':TILE,'material_slots':['road','sidewalk','kerb'],
        'roads':records,'widths_by_name':{n:{'samples':len(v),'p30_m':round(float(np.percentile(v,30))/100,3),
            'median_m':round(float(np.median(v))/100,3)} for n,v in measurements.items()},
        'areas_m2':{'road':road.area/10000,'sidewalk':sidewalk.area/10000,'kerb':kerb_band.area/10000,
            'road_removed_at_buildings':(raw_road.area-road.area)/10000,'old_preserved_domain':old_domain.area/10000}}
    return road,sidewalk,kerb_band,height,region,old_domain,buildings,info


def surface(mesh,shape,height,mat):
    if shape.is_empty: return
    xmin,ymin,xmax,ymax=shape.bounds
    for i in range(math.floor(xmin/CELL),math.ceil(xmax/CELL)):
        for j in range(math.floor(ymin/CELL),math.ceil(ymax/CELL)):
            cell=box(i*CELL,j*CELL,(i+1)*CELL,(j+1)*CELL)
            if not shape.intersects(cell): continue
            clipped=shape.intersection(cell)
            for poly in parts(clipped):
                if poly.area<.02:continue
                for tri in parts(shapely.constrained_delaunay_triangles(poly)):
                    xy=list(tri.exterior.coords)[:3]
                    h=height.road if mat==0 else height.upper
                    mesh.tri(*[(x,y,h(x,y)) for x,y in xy],mat)


def curb_faces(mesh,road,walk,clip,height):
    # Boundary is split at 1m for smooth elevation changes; no faces at tile/scope cuts.
    boundary=road.boundary.intersection(clip)
    for original in parts(boundary,'LineString'):
      coords=list(original.coords)
      for line in [LineString([a,b]) for a,b in zip(coords,coords[1:])]:
        count=max(1,math.ceil(line.length/KERB_STEP))
        for k in range(count):
            p=line.interpolate(k/count*line.length);q=line.interpolate((k+1)/count*line.length)
            dx,dy=q.x-p.x,q.y-p.y;norm=math.hypot(dx,dy)
            if norm<.1:continue
            mid=Point((p.x+q.x)/2,(p.y+q.y)/2)
            nx,ny=-dy/norm,dx/norm
            if road.covers(Point(mid.x+nx*2,mid.y+ny*2)): nx,ny=-nx,-ny
            # nx/ny points from carriageway into the sidewalk.
            if not walk.buffer(.1).covers(Point(mid.x+nx*7,mid.y+ny*7)):continue
            topa=height.upper(p.x,p.y);topb=height.upper(q.x,q.y)
            bottoma=height.road(p.x,p.y);bottomb=height.road(q.x,q.y)
            a=(p.x,p.y,bottoma);b=(q.x,q.y,bottomb);c=(q.x,q.y,topb);d=(p.x,p.y,topa)
            uv=[[0,0],[norm/100,0],[norm/100,(topb-bottomb)/100],[0,(topa-bottoma)/100]]
            mesh.tri(a,b,c,2,(-nx,-ny,0),uv[:3]);mesh.tri(a,c,d,2,(-nx,-ny,0),[uv[0],uv[2],uv[3]])


def preview(road,walk,kerb,region,old,buildings,path):
    xmin,ymin,xmax,ymax=region.bounds
    w,h=1800,1200
    scale=min((w-60)/(xmax-xmin),(h-60)/(ymax-ymin))
    def xy(x,y):return (30+(x-xmin)*scale,h-30-(y-ymin)*scale)
    image=Image.new('RGB',(w,h),'#eeebe4');draw=ImageDraw.Draw(image)
    for shape,col in [(old,'#d8d0bc'),(buildings.intersection(region),'#a99a8d'),(walk,'#c9c9c3'),(road,'#50555b'),(kerb,'#e8e5db')]:
        for p in parts(shape):
            draw.polygon([xy(x,y) for x,y in p.exterior.coords],fill=col)
            for hole in p.interiors:draw.polygon([xy(x,y) for x,y in hole.coords],fill='#eeebe4')
    draw.text((25,10),'NEW STREET / SIDEWALK EXTENSION - preserved Phase 7 area in tan; level -X = north',fill='#222222')
    image.save(path)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--pilot',action='store_true');args=parser.parse_args()
    OUT.mkdir(parents=True,exist_ok=True);REVIEW.mkdir(parents=True,exist_ok=True)
    # A data mask, not a photographic texture: RGB0 + alpha1 selects the existing
    # Phase7 concrete sidewalk layer everywhere when used on a new material copy.
    Image.new('RGBA',(8,8),(0,0,0,255)).save(OUT/'T_NS_AllWalk.png')
    road,walk,kerb,height,region,old,buildings,info=prepare()
    write_json(REVIEW/'street_plan.json',info)
    preview(road,walk,kerb,region,old,buildings,REVIEW/'street_plan.png')
    xmin,ymin,xmax,ymax=region.bounds
    tiles=[]
    for i in range(math.floor(xmin/TILE),math.ceil(xmax/TILE)):
        for j in range(math.floor(ymin/TILE),math.ceil(ymax/TILE)):
            tile=box(i*TILE,j*TILE,(i+1)*TILE,(j+1)*TILE)
            area=road.intersection(tile).area+walk.intersection(tile).area+kerb.intersection(tile).area
            if area>10:tiles.append((i,j,tile,area))
    if args.pilot:
        # Include preserved seam and an ordinary intersection instead of only largest tiles.
        seam=[t for t in tiles if t[2].intersects(old.boundary)]
        tiles=sorted(seam,key=lambda t:t[3],reverse=True)[:2]+sorted([t for t in tiles if t not in seam],key=lambda t:t[3],reverse=True)[:2]
    records=[]
    for n,(i,j,tile,area) in enumerate(tiles):
        name='NS_%s_%s'%(i,j)
        mesh=Mesh(name,(i*TILE,j*TILE))
        for shape,mat in [(road,0),(walk,1),(kerb,2)]:
            surface(mesh,shape.intersection(tile),height,mat)
        curb_faces(mesh,road,walk.union(kerb),tile,height)
        if mesh.triangles:records.append(mesh.finish(OUT/(name+'.json')))
        if (n+1)%10==0 or n+1==len(tiles):print('built',n+1,'/',len(tiles),flush=True)
    # Geometric facts, independent of triangle-count bookkeeping.
    overlaps={'road_sidewalk_m2':road.intersection(walk).area/10000,
        'road_kerb_m2':road.intersection(kerb).area/10000,'sidewalk_kerb_m2':walk.intersection(kerb).area/10000,
        'old_domain_m2':unary_union([road,walk,kerb]).intersection(old).area/10000,
        'county_buildings_m2':unary_union([road,walk,kerb]).intersection(buildings).area/10000}
    seam=unary_union([road,walk,kerb]).intersection(old.boundary.buffer(1))
    seam_points=[]
    for p in parts(seam):
        seam_points.extend(list(p.exterior.coords)[::max(1,len(p.exterior.coords)//10)])
    errors=[];road_errors=[]
    for x,y in seam_points:
        expected=height.old_exact(x,y)
        errors.append(abs(height.upper(x,y)-expected))
        if road.buffer(.1).covers(Point(x,y)):
            road_errors.append(abs(height.road(x,y)-expected))
    qc={'mode':'pilot' if args.pilot else 'full','tiles':len(records),'triangles':sum(r['triangles'] for r in records),
        'vertices':sum(r['vertices'] for r in records),'winding_errors':sum(r['winding_errors'] for r in records),
        'rejected_quantized':sum(r['rejected_quantized'] for r in records),
        'post_round_flips':sum(r['post_round_flips'] for r in records),
        'overlap_areas_m2':overlaps,'seam_samples':len(errors),'seam_upper_max_error_cm':max(errors,default=0),
        'seam_road_samples':len(road_errors),'seam_road_max_error_cm':max(road_errors,default=0),
        'seam_reference':'Actual saved Phase7 top-surface triangle elevations at the nearest preserved-boundary point',
        'largest_edge_cm':max((r['max_edge_cm'] for r in records),default=0),'finite_json_enforced':True,
        'material_slots':['road','sidewalk','kerb'],'records':records,
        'limitations':['Widths and sidewalk extents outside the original measured works are inferred visualisation geometry.',
          'Original Phase 7 roadway mask has inherited short caps within its preserved domain; no old meshes were altered.',
          'No tactile paving, road paint, signs, traffic, or vegetation have been added.']}
    qc['passed']=all(v<.001 for v in overlaps.values()) and qc['winding_errors']==0 and qc['seam_upper_max_error_cm']<.01 and qc['seam_road_max_error_cm']<.01 and qc['largest_edge_cm']<400
    write_json(REVIEW/('street_pilot_qc.json' if args.pilot else 'street_qc.json'),qc)
    print(json.dumps({k:v for k,v in qc.items() if k!='records'},indent=2),flush=True)
    if not qc['passed']:raise SystemExit('Street geometry QC failed; do not import.')


if __name__=='__main__':main()
