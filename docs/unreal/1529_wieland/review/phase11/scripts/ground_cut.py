"""Phase 11 (J2): give a ground mesh a rectangular hole where the building's lower level is, as a NEW mesh asset.

The lot's flat ground (SG_lot_placeholder) and the apron of the distant-city stand-in (FAR_CityStandIn) are flat
sheets that run straight through the inside of the lower level (floor at -152.4 cm). This copies the object's mesh,
slices the copy along the four sides of the hole, removes the triangles inside the hole between HOLE_Z, writes the
result as a new asset under /Game/Wieland1529/Delivery/Meshes/ and puts it on the object in place of the old mesh.
The old mesh asset is not changed. Nothing is saved here except the new mesh asset itself; the level that holds
the object is saved separately, by name, after the picture has been checked.

Reads review/phase11/ground_cut_job.json = {"label": "SG_lot_placeholder", "asset": "SM_W1529_LotGround_Cut",
"swap": true}. With "swap": false it only builds the asset and reports.
"""
import sys, json
sys.dont_write_bytecode = True
T = "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/tools"
if T not in sys.path:
    sys.path.insert(0, T)
import unreal
import wieland_lighting as wl

BASE = "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/review/phase11/"
FOLDER = "/Game/Wieland1529/Delivery/Meshes/"
# The hole in level coordinates: the middle of the thickness of the foundation walls, and the heights it clears.
HOLE_X = (-1404.0, -104.0)
HOLE_Y = (-3013.0, -327.0)
HOLE_Z = (-200.0, 20.0)

with open(BASE + "ground_cut_job.json", "r", encoding="utf-8") as handle:
    job = json.load(handle)
actor = [a for a in wl.actors() if a.get_actor_label() == job["label"]]
if len(actor) != 1:
    raise RuntimeError("expected one object labelled %s, found %d" % (job["label"], len(actor)))
actor = actor[0]
component = actor.static_mesh_component
source = component.static_mesh
transform = actor.get_actor_transform()
rotator = transform.rotation.rotator()
scale = transform.scale3d
if max(abs(rotator.roll), abs(rotator.pitch), abs(rotator.yaw)) > 0.001 or max(abs(scale.x - 1.0), abs(scale.y - 1.0), abs(scale.z - 1.0)) > 0.0001:
    raise RuntimeError("the object is turned or scaled; this tool only handles a plain offset")
offset = transform.translation
# the hole in the mesh's own coordinates
x0, x1 = HOLE_X[0] - offset.x, HOLE_X[1] - offset.x
y0, y1 = HOLE_Y[0] - offset.y, HOLE_Y[1] - offset.y
z0, z1 = HOLE_Z[0] - offset.z, HOLE_Z[1] - offset.z

mesh = unreal.DynamicMesh()
copy_options = unreal.GeometryScriptCopyMeshFromAssetOptions()
_, outcome = unreal.GeometryScript_AssetUtils.copy_mesh_from_static_mesh(source, mesh, copy_options, unreal.GeometryScriptMeshReadLOD())
before = mesh.get_triangle_count()
slice_options = unreal.GeometryScriptMeshPlaneSliceOptions()
slice_options.set_editor_property("gap_width", 0.0)
for value, axis in ((x0, "x"), (x1, "x"), (y0, "y"), (y1, "y")):
    if axis == "x":
        frame = unreal.Transform(location=unreal.Vector(value, 0.0, 0.0), rotation=unreal.Rotator(roll=0.0, pitch=90.0, yaw=0.0))
    else:
        frame = unreal.Transform(location=unreal.Vector(0.0, value, 0.0), rotation=unreal.Rotator(roll=90.0, pitch=0.0, yaw=0.0))
    unreal.GeometryScript_MeshBooleans.apply_mesh_plane_slice(mesh, frame, slice_options)
sliced = mesh.get_triangle_count()
box = unreal.Box(min=unreal.Vector(x0 - 0.05, y0 - 0.05, z0), max=unreal.Vector(x1 + 0.05, y1 + 0.05, z1))
selection = unreal.GeometryScript_MeshSelection.select_mesh_elements_in_box(mesh, box, unreal.GeometryScriptMeshSelectionType.TRIANGLES, False, 3)
if isinstance(selection, tuple):
    selection = [item for item in selection if isinstance(item, unreal.GeometryScriptMeshSelection)][0]
removed = unreal.GeometryScript_MeshEdits.delete_selected_triangles_from_mesh(mesh, selection)
if isinstance(removed, tuple):
    removed = [item for item in removed if isinstance(item, int)][0]
after = mesh.get_triangle_count()

path = FOLDER + job["asset"]
existing = unreal.EditorAssetLibrary.does_asset_exist(path)
if existing and unreal.EditorAssetLibrary.find_asset_data(path).package_name and unreal.Paths.file_exists(
        unreal.Paths.project_content_dir() + path[len("/Game/"):] + ".uasset"):
    raise RuntimeError("the asset %s is already saved on disk; this tool does not overwrite" % path)
create_options = unreal.GeometryScriptCreateNewStaticMeshAssetOptions()
create_options.set_editor_property("enable_recompute_normals", False)
create_options.set_editor_property("enable_recompute_tangents", False)
create_options.set_editor_property("enable_nanite", bool(source.get_editor_property("nanite_settings").enabled))
create_options.set_editor_property("enable_collision", True)
if existing:
    # left in memory, never saved, by an earlier run of this tool that stopped after creating it
    new_mesh = unreal.EditorAssetLibrary.load_asset(path)
else:
    new_mesh, outcome = unreal.GeometryScript_NewAssetUtils.create_new_static_mesh_asset_from_mesh(mesh, path, create_options)
new_mesh.set_editor_property("static_materials", source.get_editor_property("static_materials"))
old_setup, new_setup = source.get_editor_property("body_setup"), new_mesh.get_editor_property("body_setup")
if old_setup and new_setup:
    new_setup.set_editor_property("collision_trace_flag", old_setup.get_editor_property("collision_trace_flag"))
saved = bool(unreal.EditorAssetLibrary.save_asset(path, False))

swapped = None
if job.get("swap"):
    overrides = [component.get_material(i) for i in range(component.get_num_materials())]
    component.modify()
    component.set_static_mesh(new_mesh)
    for index, material in enumerate(overrides):
        if component.get_material(index) != material:
            component.set_material(index, material)
    actor.modify()
    swapped = component.static_mesh.get_path_name()

json.dumps({"label": job["label"], "old_mesh": source.get_path_name(), "new_mesh": new_mesh.get_path_name(),
            "triangles": [before, sliced, after], "removed": removed, "local_hole": [x0, x1, y0, y1, z0, z1],
            "new_bounds": str(new_mesh.get_bounding_box()), "old_bounds": str(source.get_bounding_box()),
            "new_tris": new_mesh.get_num_triangles(0), "materials": [str(m.material_interface.get_name()) for m in new_mesh.static_materials],
            "asset_saved": saved, "swapped_to": swapped, "level": actor.get_outermost().get_name(), "dirty": wl.dirty()}, default=str)
