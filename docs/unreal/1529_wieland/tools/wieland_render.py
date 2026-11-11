"""Editor-side helper: render the current viewport to a still with Movie Render Graph.

Runs inside the Unreal editor's Python interpreter. It uses the engine's
Quick Render with one-off settings, so no asset is created or saved: the
viewport's camera is rendered once to a PNG in the folder given.

    import sys
    sys.dont_write_bytecode = True
    sys.path.insert(0, "<this folder>")
    import wieland_render
    wieland_render.still("<output folder>", "name", 3840, 2160, path_traced=True, samples=256)

still() returns at once. The render then runs on the editor's own ticks; poll
status() from later, separate calls and look for the file. The file is named
<name>.0000.png.

Set the viewport camera (and its field of view) before calling. The level is
not changed.
"""

import os
import time

import unreal

_LAST = {}


def still(output_folder, name, width, height, path_traced=True, samples=64, play_in_editor=True, warm_up_frames=None):
    """Start one still render of the current viewport. Returns a short record."""
    queue = unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem)
    if queue.is_rendering():
        raise RuntimeError("a render is already running")
    os.makedirs(output_folder, exist_ok=True)
    target = os.path.join(output_folder, name + ".0000.png")
    if os.path.exists(target):
        raise RuntimeError("output already exists: " + target)
    settings = unreal.MovieGraphQuickRenderModeSettings()
    settings.set_configuration_type(unreal.MovieGraphQuickRenderConfigurationType.BASIC)
    settings.set_editor_property("post_render_behavior", unreal.MoviePipelinePostRenderActionType.DO_NOTHING)
    mode = unreal.MovieGraphQuickRenderExecutionMode.PLAY_IN_EDITOR if play_in_editor else unreal.MovieGraphQuickRenderExecutionMode.EDITOR_WORLD
    settings.set_editor_property("execution_mode", mode)
    basic = settings.get_basic_config()

    def override(prop, value, flag=None):
        basic.set_editor_property(flag or ("override_" + prop), True)
        basic.set_editor_property(prop, value)

    override("use_path_traced_renderer", bool(path_traced), "override_b_use_path_traced_renderer")
    override("use_deferred_renderer", not path_traced, "override_b_use_deferred_renderer")
    if path_traced:
        override("path_traced_spatial_sample_count", int(samples))
    else:
        override("deferred_spatial_sample_count", int(samples))
    if warm_up_frames is not None:
        override("num_warm_up_frames", int(warm_up_frames))
    override("output_resolution", unreal.MovieGraphLibrary.named_resolution_from_size(int(width), int(height)))
    override("output_directory", unreal.DirectoryPath(path=output_folder.replace("\\", "/")))
    override("file_name_format", name + ".{frame_number}")
    _LAST.clear()
    _LAST.update(name=name, target=target, started=time.time(), width=int(width), height=int(height), path_traced=bool(path_traced), samples=int(samples), play_in_editor=bool(play_in_editor), warm_up_frames=basic.get_editor_property("num_warm_up_frames"), denoiser=str(basic.get_editor_property("path_traced_denoiser_type")))
    quick = unreal.get_editor_subsystem(unreal.MovieGraphQuickRenderSubsystem)
    quick.begin_quick_render(unreal.MovieGraphQuickRenderMode.CURRENT_VIEWPORT, settings)
    return dict(_LAST)


def status():
    """One snapshot: is a render running, and has the last still been written."""
    queue = unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem)
    record = dict(_LAST)
    record["is_rendering"] = bool(queue.is_rendering())
    target = record.get("target")
    if target and os.path.exists(target):
        record["file_bytes"] = os.path.getsize(target)
        record["seconds_to_file"] = round(os.path.getmtime(target) - record["started"], 1)
    else:
        record["file_bytes"] = None
        record["seconds_since_start"] = round(time.time() - record["started"], 1) if record.get("started") else None
    return record
