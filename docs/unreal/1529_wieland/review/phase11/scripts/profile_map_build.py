"""Phase 11, steps 11.4 and 11.5: prepare the two levels the packaged build starts in.

1. The walk-through: L_Site_M4 has no player start, so a packaged build would put the viewer at the world's origin.
   One object is added to L_Site_M4's own top level: a player start "PS_W1529_S1" at station S1 (the west sidewalk,
   eye height 1.59 m, facing the building, as Phase 9's hold S1), tagged W1529.Generated, folder W1529_Generated.
   L_Site_M4 is then saved by name (wieland_levels.save_master). Skipped if the object exists.
2. The profile: a NEW level /Game/Wieland1529/Delivery/L_W1529_Profile, a copy of L_Site_M4 (it loads the same eleven
   levels, with the same streaming boxes) plus one object that plays /Game/Wieland1529/Delivery/Profile/
   SEQ_W1529_ProfilePaths by itself when the level starts, looping, with the viewer's own movement switched off.
   Saved by name. L_Site_M4 is opened again at the end.

Never saves anything else; refuses if anything is unsaved when it starts or if a render is running.
"""
import sys, json, importlib
sys.dont_write_bytecode = True
T = "E:/Claude/3D-Model-Workflow/.claude/worktrees/1529-wieland-scene-plan-e84a03/docs/unreal/1529_wieland/tools"
if T not in sys.path:
    sys.path.insert(0, T)
import unreal
import wieland_levels as wlv
importlib.reload(wlv)

SITE = "/Game/Wieland1529/L_Site_M4"
PROFILE = "/Game/Wieland1529/Delivery/L_W1529_Profile"
MASTER = "/Game/Wieland1529/Delivery/Profile/SEQ_W1529_ProfilePaths"
S1 = {"loc": [-754.4, 1400.0, 158.6], "yaw": -88.82}
utils = unreal.EditorLoadingAndSavingUtils
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
editor = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)


def world_path():
    return editor.get_editor_world().get_path_name().split(".")[0]


def dirty():
    return sorted(p.get_name() for p in list(utils.get_dirty_content_packages()) + list(utils.get_dirty_map_packages()))


out = {}
if unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem).is_rendering():
    raise RuntimeError("a render is running")
if world_path() != SITE:
    raise RuntimeError("the open level is %s, not %s" % (world_path(), SITE))
if dirty():
    raise RuntimeError("unsaved packages before starting: %s" % dirty())
if not unreal.EditorAssetLibrary.does_asset_exist(MASTER):
    raise RuntimeError("no profile sequence " + MASTER)
if unreal.EditorAssetLibrary.does_asset_exist(PROFILE):
    raise RuntimeError("the level %s already exists; this tool does not overwrite" % PROFILE)

# 1. the player start in L_Site_M4
world = editor.get_editor_world()
existing = [a for a in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.PlayerStart) if a.get_actor_label() == "PS_W1529_S1"]
if existing:
    out["player_start"] = "exists"
else:
    level_editor = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    level_editor.set_current_level_by_name(SITE.split("/")[-1])
    start = actors.spawn_actor_from_class(unreal.PlayerStart, unreal.Vector(*S1["loc"]), unreal.Rotator(pitch=0.0, yaw=S1["yaw"], roll=0.0))
    start.set_actor_label("PS_W1529_S1")
    start.set_folder_path("W1529_Generated")
    start.tags = [unreal.Name(wlv.TAG_GENERATED)]
    out["player_start"] = {"level": start.get_outermost().get_name(), "loc": str(start.get_actor_location()), "rot": str(start.get_actor_rotation())}
    out["site_saved"] = wlv.save_master()
out["dirty_after_site_save"] = dirty()

# 2. the profile level: copy L_Site_M4 while it is not the open level
utils.new_blank_map(False)
copy = unreal.EditorAssetLibrary.duplicate_asset(SITE, PROFILE)
out["duplicated"] = copy.get_path_name() if copy else None
if not copy:
    raise RuntimeError("could not copy %s to %s" % (SITE, PROFILE))
utils.load_map(PROFILE)
if world_path() != PROFILE:
    raise RuntimeError("the profile level did not open: %s" % world_path())
level_editor = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
level_editor.set_current_level_by_name(PROFILE.split("/")[-1])
player = actors.spawn_actor_from_class(unreal.LevelSequenceActor, unreal.Vector(0.0, 0.0, 0.0), unreal.Rotator(0.0, 0.0, 0.0))
player.set_actor_label("LSA_W1529_ProfilePaths")
player.set_folder_path("W1529_Generated")
player.tags = [unreal.Name(wlv.TAG_GENERATED)]
player.set_sequence(unreal.load_asset(MASTER))
settings = player.get_editor_property("playback_settings")
done = {}
for name, value in (("auto_play", True), ("disable_movement_input", True), ("disable_look_at_input", True),
                    ("hide_player", True), ("hide_hud", True), ("pause_at_end", False)):
    try:
        settings.set_editor_property(name, value)
        done[name] = value
    except Exception as error:  # a name the engine version does not have is reported, not guessed around
        done[name] = "not set: %s" % error
loop = settings.get_editor_property("loop_count")
loop.set_editor_property("value", -1)
settings.set_editor_property("loop_count", loop)
player.set_editor_property("playback_settings", settings)
back = player.get_editor_property("playback_settings")
out["sequence_player"] = {"level": player.get_outermost().get_name(), "sequence": str(player.get_sequence().get_path_name()),
                          "set": done, "loop_count": back.get_editor_property("loop_count").get_editor_property("value"),
                          "auto_play": back.get_editor_property("auto_play")}
out["profile_saved"] = bool(utils.save_map(editor.get_editor_world(), PROFILE))
out["dirty_after_profile_save"] = dirty()

# 3. back to the walk-through level
utils.load_map(SITE)
out["open_at_end"] = world_path()
out["dirty_at_end"] = dirty()
json.dumps(out, default=str)
