"""Owner-approved presentation facades on measured nearby building forms.

Offline only. Original roof/mast geometry and all inputs remain untouched. New wall openings
are cut from exposed planar wall patches, with modeled reveals, recessed reflective glazing,
frames, sills and lintels. Appearance/layout choices are explicitly inferences, not field facts.
"""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

import numpy as np
import shapely
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union
from shapely.strtree import STRtree

import wieland_geo as geo

DOCS=Path(__file__).resolve().parent.parent
WORK=Path('E:/Wieland1529_site_data/phase20/nearby_detail')
BASE=Path('E:/Wieland1529_site_data/phase17')
OUT=WORK/'meshes_facade'
RECORDS=DOCS/'review/phase20/nearby_detail'
FRAME=geo.LevelFrame.load(str(DOCS/'review/phase2/level_frame.json'))
FT=geo.US_SURVEY_FOOT_M
SLOTS={'wall':0,'roof':1,'mast':2,'glass':3,'frame':4,'trim':5}


def rnd(bid):
    return [v/255 for v in hashlib.sha256(('nearby-detail-'+bid).encode()).digest()]


class Context:
    def __init__(self):
        self.evidence={r['county_id']:r for r in csv.DictReader((RECORDS/'building_evidence.csv').open(encoding='utf-8'))}
        self.active={r['bldg_id'] for r in csv.DictReader((WORK/'active_targets.csv').open(encoding='utf-8'))}
        features=json.loads((BASE/'county/county_footprints_2022_viewbox.json').read_text(encoding='utf-8'))['features']
        scope=set(self.evidence)
        self.ids=[];self.polys=[]
        for f in features:
            bid=str(f['attributes']['OBJECTID'])
            if bid in scope:
                p=unary_union([Polygon(r).buffer(0) for r in f['geometry']['rings']])
                if not p.is_empty:self.ids.append(bid);self.polys.append(p)
        self.tree=STRtree(self.polys)
        lines=[]
        for el in json.loads((WORK/'roads_osm.json').read_text(encoding='utf-8'))['elements']:
            points=el.get('geometry',[])
            if len(points)>1:lines.append(LineString([geo.state_plane_from_lat_lon(p['lat'],p['lon']) for p in points]))
        self.roads=unary_union(lines)

    def exposed(self,bid,xy,outward,pivot):
        wx,wy=xy[0]+pivot[0],xy[1]+pivot[1]
        e,n,_=FRAME.map_from_level(wx,wy,pivot[2])
        e2,n2,_=FRAME.map_from_level(wx+outward[0]*100,wy+outward[1]*100,pivot[2])
        direction=np.array([e2-e,n2-n]);direction/=np.linalg.norm(direction)
        hit=False
        for cm in (35,80,150):
            q=Point(e+direction[0]*cm/(100*FT),n+direction[1]*cm/(100*FT))
            for index in self.tree.query(q,predicate='intersects'):
                if self.ids[int(index)]!=bid:hit=True;break
            if hit:break
        point=Point(e,n)
        nearest=self.roads.interpolate(self.roads.project(point))
        v=np.array([nearest.x-e,nearest.y-n]);distance=float(np.linalg.norm(v))*FT
        facing=float(np.dot(v/max(1e-9,np.linalg.norm(v)),direction))
        return not hit, distance, facing


class Mesh:
    def __init__(self,pivot):
        self.pivot=pivot;self.v=[];self.t=[];self.m=[];self.uv=[]
        self.orientation_checks=0;self.min_area=math.inf

    def tri(self,points,mat,inward=None,uvs=None):
        p=np.asarray(points,dtype=float)
        cross=np.cross(p[1]-p[0],p[2]-p[0]);area=np.linalg.norm(cross)/2
        if area<1e-5:return
        if inward is not None and np.dot(cross,inward)<0:
            p=p[[0,2,1]];cross=-cross
            if uvs is not None:uvs=[uvs[i] for i in (0,2,1)]
        if inward is not None:
            if np.dot(cross,inward)<=0:raise RuntimeError('Incorrect face winding')
            self.orientation_checks+=1
        self.min_area=min(self.min_area,float(area))
        start=len(self.v)
        self.v.extend([[round(float(a),4) for a in v] for v in p])
        self.t.append([start,start+1,start+2]);self.m.append(mat)
        # Preserve source roof/mast UV exactly; new detail receives valid physical-scale box mapping.
        if uvs is not None:self.uv.extend(uvs)
        else:
            axis=int(np.argmax(np.abs(cross)))
            a,b=(1,2) if axis==0 else ((0,2) if axis==1 else (0,1))
            self.uv.extend([[round(float(v[a])/100,5),round(float(v[b])/100,5)] for v in p])

    def quad(self,points,mat,inward):
        self.tri([points[0],points[1],points[2]],mat,inward)
        self.tri([points[0],points[2],points[3]],mat,inward)


def material_choice(row,bid,height):
    d=rnd(bid);source=row.get('wall_material','').lower()
    if 'frame' in source and 'masonry' not in source:family='siding';why='Assessor frame construction; colour inferred'
    elif any(s in source for s in ('stone','limestone')):family='limestone';why='Recorded stone material; colour inferred'
    elif 'stucco' in source:family='concrete';why='Recorded stucco; neutral mineral appearance inferred'
    elif 'glass' in source:family='concrete';why='Recorded glass; opaque structural bands with modeled glazing, inferred proportions'
    elif source:family=('red brick 2','common brick','dark brick')[int(d[0]*2.999)];why='Recorded masonry or mixed masonry; brick appearance inferred'
    else:
        family='siding' if d[0]<.12 and height<1400 else ('limestone' if d[0]>.84 else ('common brick' if d[1]>.65 else 'red brick 2'))
        why='Presentation assumption approved by owner; not a verified facade material'
    frame='white' if family=='siding' else ('bronze' if d[3]<.5 else 'black')
    tint=[round(.78+.25*d[4],3),round(.78+.23*d[5],3),round(.78+.22*d[6],3)]
    if family=='siding':
        palette=[(.65,.67,.64),(.42,.49,.54),(.69,.64,.55),(.53,.59,.53),(.78,.76,.69)]
        tint=list(palette[int(d[7]*4.999)])
    return {'family':family,'wall_tint':tint,'frame':frame,'source_or_assumption':why,
            'colour_status':'Inferred presentation colour, not field verified',
            'layout_status':'Inferred opening positions/proportions approved by owner'}


def planar_groups(data):
    vertices=np.asarray(data['vertices'],dtype=float)
    groups={};kept=[]
    for tri,mat in zip(data['triangles'],data['tri_mat']):
        p=vertices[tri];cross=np.cross(p[1]-p[0],p[2]-p[0]);length=np.linalg.norm(cross)
        if length<1e-8:raise RuntimeError('Degenerate source triangle')
        normal=cross/length
        if mat!=0 or abs(normal[2])>.06:
            kept.append((p.tolist(),int(mat),[data['uv0_m'][i] for i in tri]));continue
        n=normal[:2]/np.linalg.norm(normal[:2])
        # Measured-tier walls share edges with rounding-level differences in their
        # normals. Cluster complete planes before triangulation, including their
        # opposite-facing sides. Opposite overlaps are internal tier interfaces,
        # not two visible facades on which to put conflicting windows.
        nq=n if (n[0]>1e-7 or (abs(n[0])<=1e-7 and n[1]>=0)) else -n
        d=float(np.mean(p[:,:2]@nq))
        key=None
        for candidate,g in groups.items():
            if np.dot(g['n'],nq)>1-2e-8 and np.max(np.abs(p[:,:2]@g['n']-g['d']))<.75:
                key=candidate;nq=g['n'];d=g['d'];break
        if key is None:key=len(groups)
        tangent=np.array([-nq[1],nq[0]])
        polygon=Polygon([(float(np.dot(v[:2],tangent)),float(v[2])) for v in p]).buffer(0)
        group=groups.setdefault(key,{'n':nq,'t':tangent,'d':d,'positive':[],'negative':[],'triangles':0})
        group['positive' if np.dot(n,nq)>0 else 'negative'].append(polygon);group['triangles']+=1
    exterior={}
    for g in groups.values():
        pos=unary_union(g['positive']).buffer(0);neg=unary_union(g['negative']).buffer(0)
        for patch,sign in ((pos.difference(neg),1),(neg.difference(pos),-1)):
            if patch.is_empty:continue
            if sign>0:parts=[patch]
            else:
                # Tangent flips with normal; reflect wall-coordinate u as well.
                from shapely.affinity import scale
                parts=[scale(patch,xfact=-1,yfact=1,origin=(0,0))]
            exterior[len(exterior)]={'n':g['n']*sign,'t':g['t']*sign,'d':g['d']*sign,
                                     'parts':parts,'triangles':g['triangles'] if sign>0 or pos.is_empty else 0}
    return exterior,kept


def patch_triangles(mesh,poly,point,mat,inward):
    if poly.is_empty:return 0.0
    triangulated=shapely.constrained_delaunay_triangles(poly)
    area=0.0
    for tri in triangulated.geoms:
        coords=list(tri.exterior.coords)[:3]
        mesh.tri([point(u,z,0) for u,z in coords],mat,inward)
        area+=tri.area
    if abs(area-poly.area)>max(.1,poly.area*1e-7):raise RuntimeError('Wall triangulation area mismatch')
    return area


def add_box(mesh,point,n,t,u0,u1,z0,z1,depth0,depth1,mat):
    # Each face's target is inward, matching the source mesh's Unreal winding convention.
    v=[point(u,z,d) for u,z,d in ((u0,z0,depth0),(u1,z0,depth0),(u1,z1,depth0),(u0,z1,depth0),
                                 (u0,z0,depth1),(u1,z0,depth1),(u1,z1,depth1),(u0,z1,depth1))]
    for idx,inward in (((0,1,2,3),n),((4,7,6,5),-n),((0,3,7,4),t),((1,5,6,2),-t),
                       ((0,4,5,1),np.array([0,0,1])),((3,2,6,7),np.array([0,0,-1]))):
        mesh.quad([v[i] for i in idx],mat,inward)


def wall_depth_clear(source_tri,origin,direction,inside=21,outside=100000):
    """Reject thin sliver parts or a second source wall across the proposed recess.

    Roof-tier fitting can leave very narrow measured volume parts. Windows cannot
    be 180 mm deep in a 20 mm sliver. Test both directions without altering roofs.
    """
    e1=source_tri[:,1]-source_tri[:,0];e2=source_tri[:,2]-source_tri[:,0]
    h=np.cross(np.broadcast_to(direction,e2.shape),e2)
    a=np.einsum('ij,ij->i',e1,h);valid=np.abs(a)>1e-8
    f=np.divide(1,a,out=np.zeros_like(a),where=valid)
    s=origin-source_tri[:,0];u=f*np.einsum('ij,ij->i',s,h);q=np.cross(s,e1)
    v=f*np.einsum('j,ij->i',direction,q);distance=f*np.einsum('ij,ij->i',e2,q)
    valid&=(u>=-1e-7)&(v>=-1e-7)&(u+v<=1+1e-7)
    return not np.any(valid&(((distance>.9)&(distance<inside))|((distance<-.9)&(distance>-outside))))


def build(ctx,bid):
    if bid not in ctx.active:raise RuntimeError('Refused non-active target '+bid)
    data=json.loads((WORK/'meshes_clean'/('ND_'+bid+'.json')).read_text(encoding='utf-8'))
    row=ctx.evidence[bid];groups,kept=planar_groups(data);mesh=Mesh(data['pivot'])
    for p,mat,uv in kept:mesh.tri(p,mat,uvs=uv)
    original_v=np.asarray(data['vertices'],dtype=float)
    source_tri=original_v[np.asarray(data['triangles'])]
    wall_top=max((max(p[2] for p in data['vertices'] if True)),250)
    # Mast tips do not dictate storeys; use the top of wall groups instead.
    if groups:wall_top=max(max(p.bounds[3] for p in g['parts']) for g in groups.values())
    height=max(0,float(wall_top))
    try:source_storeys=float(row.get('storeys') or 0)
    except ValueError:source_storeys=0
    storeys=int(round(source_storeys)) if source_storeys>0 else max(1,round(height/325))
    storeys=max(1,min(70,storeys))
    floor=height/storeys if height>0 else 300
    storeys_source=row.get('storeys_source','') or 'Derived from measured wall height; assumption'
    if floor<240 or floor>520:
        storeys=max(1,min(70,round(height/325)));floor=height/storeys
        storeys_source='Measured wall height; recorded storey count inconsistent with height, inferred replacement'
    choice=material_choice(row,bid,height)
    windows=doors=party=0;removed=0;area_error=0.0;groups_rec=[];proof_openings=[];thin_rejected=0
    for group in groups.values():
        patch=unary_union(group['parts']).buffer(0)
        n2,t2,d=group['n'],group['t'],group['d']
        n=np.array([n2[0],n2[1],0.]);t=np.array([t2[0],t2[1],0.])
        def point(u,z,depth):return np.array([n2[0]*(d+depth)+t2[0]*u,n2[1]*(d+depth)+t2[1]*u,z])
        bounds=patch.bounds;u0,z0,u1,z1=bounds;width=u1-u0
        center=(u0+u1)/2
        free,road_distance,road_facing=ctx.exposed(bid,point(center,250,0)[:2],-n2,data['pivot'])
        if not free:party+=1
        front=road_facing>.35 and road_distance<55
        holes=[];entries=[]
        if free and width>=200 and z1>=260:
            spacing=(230+55*rnd(bid)[0]) if front else (270+70*rnd(bid)[1])
            count=max(1,min(36,int(width/spacing)))
            centers=[u0+(i+.5)*width/count for i in range(count)]
            for story in range(storeys):
                sill=story*floor+max(72,min(100,floor*.24))
                tall=min(185,max(125,floor*.55))
                winw=min(135 if front else 110,max(78,width/count*.49))
                for column,uc in enumerate(centers):
                    doorway=front and story==0 and column==count-1 and height>=350
                    b=5 if doorway else sill
                    top=min(floor*.80 if doorway else sill+tall,z1-22)
                    w=min(105,winw) if doorway else winw
                    opening=box(uc-w/2,b,uc+w/2,top)
                    if top-b<95 or not patch.buffer(-13).covers(opening):continue
                    if not all(wall_depth_clear(source_tri,point(pu,pz,0),n)
                               for pu,pz in ((uc,b+(top-b)*.25),(uc,b+(top-b)*.75),
                                             (uc-w*.35,(b+top)/2),(uc+w*.35,(b+top)/2))):
                        thin_rejected+=1;continue
                    if doorway:doors+=1
                    else:windows+=1
                    holes.append(opening);entries.append((uc-w/2,uc+w/2,b,top,doorway))
        cut=unary_union(holes) if holes else Polygon()
        wall=patch.difference(cut)
        area=patch_triangles(mesh,wall,point,0,n)
        area_error=max(area_error,abs(area-(patch.area-cut.area)))
        removed+=group['triangles']
        for left,right,bottom,top,doorway in entries:
            depth=18.0
            # Actual recess: four reveals connect the cut front wall to glazing 180 mm behind it.
            mesh.quad([point(left,bottom,0),point(left,top,0),point(left,top,depth),point(left,bottom,depth)],0,-t)
            mesh.quad([point(right,bottom,0),point(right,bottom,depth),point(right,top,depth),point(right,top,0)],0,t)
            mesh.quad([point(left,bottom,0),point(left,bottom,depth),point(right,bottom,depth),point(right,bottom,0)],5,np.array([0,0,-1]))
            mesh.quad([point(left,top,0),point(right,top,0),point(right,top,depth),point(left,top,depth)],0,np.array([0,0,1]))
            mesh.quad([point(left,bottom,depth),point(right,bottom,depth),point(right,top,depth),point(left,top,depth)],3,n)
            probe_u=(left+right)/2;probe_z=bottom+(top-bottom)*.25
            proof_openings.append({'origin':point(probe_u,probe_z,-30).tolist(),'direction':n.tolist(),
                                    'expected_first_material':3,'expected_distance_cm':48.0})
            frame=5.5
            for a,b,c,e in ((left,left+frame,bottom,top),(right-frame,right,bottom,top),
                            (left+frame,right-frame,bottom,bottom+frame),(left+frame,right-frame,top-frame,top)):
                add_box(mesh,point,n,t,a,b,c,e,-2,5,4)
            if not doorway:
                mid=bottom+(top-bottom)*.48
                add_box(mesh,point,n,t,left+frame,right-frame,mid-1.8,mid+1.8,4,10,4)
                add_box(mesh,point,n,t,left-9,right+9,bottom-10,bottom-2,-11,2,5)
            add_box(mesh,point,n,t,left-9,right+9,top+3,top+15,-6,1,5)
        if free and width>=230:
            # Keep cornices below the measured roof top; no invented increase in building height.
            flat_top=patch.intersection(box(u0+10,z1-22,u1-10,z1-2))
            cornice_clear=all(wall_depth_clear(source_tri,point(u,z1-15,0),n,inside=21,outside=100000)
                               for u in (u0+20,(u0+u1)/2,u1-20))
            if flat_top.area>(width-20)*16 and cornice_clear:
                add_box(mesh,point,n,t,u0+2,u1-2,z1-22,z1-10,-14,1,5)
                add_box(mesh,point,n,t,u0+2,u1-2,z1-10,z1-2,-18,1,5)
            if patch.covers(box(u0+3,12,u1-3,48)):
                add_box(mesh,point,n,t,u0+3,u1-3,12,48,-5,1,5)
        groups_rec.append({'width_cm':round(width,2),'wall_area_cm2':round(patch.area,2),
                           'opening_area_cm2':round(cut.area,2),'openings':len(entries),'exposed':free,
                           'street_facing':front,'road_distance_m':round(road_distance,2)})
    vertices=np.asarray(mesh.v)
    if not np.isfinite(vertices).all():raise RuntimeError('Non-finite output vertex')
    new_top=float(vertices[:,2].max());source_top=float(original_v[:,2].max())
    if new_top>source_top+.1:raise RuntimeError('Facade detail exceeded measured top')
    record={'county_id':bid,'name':'NDF_'+bid,'source':'ND_'+bid,'address':row.get('address',''),
            'status':'Owner-approved inferred presentation facade; footprint and roof from measurements',
            'source_triangles':len(data['triangles']),'preserved_nonwall_triangles':len(kept),
            'replaced_wall_triangles':removed,'triangles':len(mesh.t),'vertices':len(mesh.v),
            'windows':windows,'doors':doors,'party_wall_patches_without_openings':party,
            'openings_rejected_thin_or_overlapping_source_wall':thin_rejected,
            'recess_depth_mm':180,'frame_width_mm':55,'storeys':storeys,'storeys_source':storeys_source,
            'floor_height_cm':round(floor,2),'measured_top_cm':source_top,'output_top_cm':new_top,
            'max_wall_area_error_cm2':area_error,'min_triangle_area_cm2':mesh.min_area,
            'orientation_checks':mesh.orientation_checks,'appearance':choice,'patches':groups_rec}
    record['opening_ray_probes']=proof_openings
    result={'name':'NDF_'+bid,'kind':'building','zone':2,'pivot':data['pivot'],'vertices':mesh.v,
            'triangles':mesh.t,'tri_mat':mesh.m,'uv0_m':mesh.uv}
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/('NDF_'+bid+'.json')).write_text(json.dumps(result,separators=(',',':')),encoding='utf-8')
    (OUT/('NDF_'+bid+'.record.json')).write_text(json.dumps(record,indent=2),encoding='utf-8')
    return record


def main():
    parser=argparse.ArgumentParser();parser.add_argument('ids',nargs='*');parser.add_argument('--all',action='store_true')
    args=parser.parse_args();ctx=Context()
    ids=sorted(ctx.active) if args.all else (args.ids or ['777585','780284','781722'])
    rows=[];failed=[]
    for bid in ids:
        try:
            r=build(ctx,bid);rows.append(r)
            print(bid,'windows',r['windows'],'doors',r['doors'],'tris',r['triangles'],flush=True)
        except Exception as exc:
            failure={'county_id':bid,'error':repr(exc)};failed.append(failure);print('FAILED',json.dumps(failure),flush=True)
    name='facade_plan.json' if args.all else 'facade_pilots.json'
    summary={'targets':len(ids),'built':len(rows),'failures':failed,'windows':sum(r['windows'] for r in rows),
             'doors':sum(r['doors'] for r in rows),'triangles':sum(r['triangles'] for r in rows),'records':rows,
             'slots':SLOTS,'geometry_folder':str(OUT),'source_status':'Inferences explicitly approved by owner 2026-11-15'}
    (RECORDS/name).write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in summary.items() if k!='records'}),flush=True)
    return 1 if failed else 0


if __name__=='__main__':raise SystemExit(main())
