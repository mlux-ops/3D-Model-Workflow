"""Remove inherited canopy-height ground in the refined area using measured bare-earth DTM."""
import json
from pathlib import Path
import numpy as np
from scipy import ndimage
import wieland_geo as geo

DOCS=Path(__file__).resolve().parent.parent
BASE=Path('E:/Wieland1529_site_data/phase17')
OUT=Path('E:/Wieland1529_site_data/phase20/nearby_detail/ground')

def main():
    data=json.loads((BASE/'meshes_ground/P17G_Terrain.json').read_text())
    v=np.asarray(data['vertices'],dtype=float);pivot=np.asarray(data['pivot']);world=v+pivot
    frame=geo.LevelFrame.load(DOCS/'review/phase2/level_frame.json')
    origin=np.array(frame.map_from_level(0,0));dx=np.array(frame.map_from_level(1,0))-origin;dy=np.array(frame.map_from_level(0,1))-origin
    coords=origin+world[:,:1]*dx+world[:,1:2]*dy
    limits=json.loads((DOCS/'review/phase20/nearby_detail/street_plan.json').read_text())['boundary_map_ft']
    lo=np.asarray(limits[:2]);hi=np.asarray(limits[2:]);outside=np.maximum(np.maximum(lo-coords,coords-hi),0)
    dist=np.linalg.norm(outside,axis=1)*.3048
    weight=np.clip(1-dist/25,0,1);weight=weight*weight*(3-2*weight)
    ids=np.flatnonzero(weight>0)
    raster=np.load(BASE/'rasters/view6ft_dtm.npz');z=ndimage.gaussian_filter(raster['z'].astype(float),2)
    rows=(float(raster['y1'])-coords[ids,1])/float(raster['cell'])-.5
    cols=(coords[ids,0]-float(raster['x0']))/float(raster['cell'])-.5
    heights=ndimage.map_coordinates(z,[rows,cols],order=1,mode='nearest')
    target=frame.origin_z_cm+(heights-frame.origin_height_ft)*geo.CM_PER_US_SURVEY_FOOT-25
    old=world[ids,2].copy();world[ids,2]=old+(target-old)*weight[ids]
    v[ids,2]=world[ids,2]-pivot[2]
    data['name']='Nearby_Ground_DTM';data['vertices']=v.tolist()
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'Nearby_Ground_DTM.json').write_text(json.dumps(data,separators=(',',':')),encoding='utf-8')
    record={'source':'P17G_Terrain topology/UVs and measured 6ft bare-earth DTM','changed_vertices':len(ids),'max_lower_cm':float((old-world[ids,2]).max()),'blend_outside_scope_m':25,'clearance_below_dtm_cm':25,'xy_unchanged':True,'outside_blend_unchanged':True,'preserved_old_site_hole':True,'triangles':len(data['triangles'])}
    (DOCS/'review/phase20/nearby_detail/ground_refit.json').write_text(json.dumps(record,indent=2),encoding='utf-8');print(record)

if __name__=='__main__':main()
