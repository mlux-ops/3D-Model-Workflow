"""Copied 1533 upper architecture refit to the measured flat roof; XY and ground storey fixed."""
import json
from pathlib import Path
import numpy as np
import unreal
import wieland_site as ws

OUT=Path(__file__).resolve().parent.parent/'review/phase20/nearby_detail/neighbours'
ROOT='/Game/Wieland1529/Surroundings/NearbyDetail/NeighbourMeshes/'

def reference_roof(xy):
    data=np.load(OUT/'audit_current_1533_opaque.npz')
    vertices=data['positions'];triangles=data['triangles'][data['material_ids']==4]
    faces=vertices[triangles]
    nearest=np.argmin(((xy[:,None,:]-faces[:,:,:2].mean(axis=1)[None,:,:])**2).sum(axis=2),axis=1)
    heights=np.zeros(len(xy));assigned=np.zeros(len(xy),dtype=bool)
    for i,face in enumerate(faces):
        matrix=np.c_[face[:,:2],np.ones(3)]
        plane=np.linalg.solve(matrix,face[:,2])
        bary=np.c_[xy,np.ones(len(xy))]@np.linalg.inv(matrix)
        inside=(bary>=-1e-6).all(axis=1)
        use=(inside&~assigned)|((nearest==i)&~assigned)
        heights[use]=np.c_[xy[use],np.ones(use.sum())]@plane
        assigned|=inside
    if (heights<1200).any():raise RuntimeError('Roof reference outside expected height')
    return heights

def apply(kind):
    if kind not in ('opaque','glass'):raise ValueError(kind)
    if ws.world_path()!='/Game/Wieland1529/L_Site_M4':raise RuntimeError('Wrong level')
    label='R15_PART_'+kind+'_xm05_yp01_part01'
    actor=next(a for a in ws.actors() if a.get_actor_label()==label)
    component=actor.static_mesh_component
    source_path='/Game/Wieland1529/Surroundings/R15Fit/SM_R15fit_'+kind+'_xm05_yp01_part01'
    data=np.load(OUT/('audit_current_1533_'+kind+'.npz'))
    vertices=data['positions'].copy();triangles=data['triangles'];materials=data['material_ids']
    selected=materials<=(7 if kind=='opaque' else 4)
    ids=np.unique(triangles[selected]);other=np.unique(triangles[~selected])
    shared=np.intersect1d(ids,other)
    if len(shared):raise RuntimeError('Shared target/unrelated vertices; isolate first')
    roof=reference_roof(vertices[ids,:2]);z=vertices[ids,2]
    weight=np.clip((z-300)/(roof-300),0,1)
    vertices[ids,2]+=(1364.14-roof)*weight
    if not np.array_equal(vertices[other],data['positions'][other]):raise RuntimeError('Unrelated geometry changed')
    if not np.array_equal(vertices[:,:2],data['positions'][:,:2]):raise RuntimeError('XY changed')
    source,dynamic=ws._dynamic(source_path)
    lists=unreal.GeometryScript_List
    current=unreal.GeometryScript_MeshQueries.get_all_vertex_positions(dynamic,False)[-2]
    current=np.array([(v.x,v.y,v.z) for v in lists.convert_vector_list_to_array(current)])
    if current.shape!=vertices.shape or np.max(abs(current-data['positions']))>.001:raise RuntimeError('Source changed since audit')
    moved=[unreal.Vector(float(x),float(y),float(z)) for x,y,z in vertices]
    unreal.GeometryScript_MeshEdits.set_all_mesh_vertex_positions(dynamic,lists.convert_array_to_vector_list(moved))
    target_path=ROOT+'SM_Neighbour1533_'+kind
    target=unreal.load_asset(target_path) if unreal.EditorAssetLibrary.does_asset_exist(target_path) else unreal.EditorAssetLibrary.duplicate_asset(source_path,target_path)
    opts=unreal.GeometryScriptCopyMeshToAssetOptions();opts.enable_recompute_normals=False;opts.emit_transaction=False
    _,outcome=unreal.GeometryScript_AssetUtils.copy_mesh_to_static_mesh(dynamic,target,opts,unreal.GeometryScriptMeshWriteLOD())
    if outcome!=unreal.GeometryScriptOutcomePins.SUCCESS:raise RuntimeError('Copy failed')
    before=[component.get_material(i).get_path_name() for i in range(component.get_num_materials())]
    component.modify();component.set_static_mesh(target)
    after=[component.get_material(i).get_path_name() for i in range(component.get_num_materials())]
    if before!=after:raise RuntimeError('Material slots changed')
    saved=unreal.EditorAssetLibrary.save_loaded_asset(target,False)
    record={'kind':kind,'asset':target.get_path_name(),'saved':bool(saved),'target_vertices':len(ids),'unrelated_vertices_unchanged':len(other),'max_lower_cm':float((data['positions'][:,2]-vertices[:,2]).max()),'xy_unchanged':True,'roof_target_cm':1364.14,'anchor_cm':300,'source_unchanged':True}
    (OUT/('refit_'+kind+'.json')).write_text(json.dumps(record,indent=2),encoding='utf-8')
    return record
