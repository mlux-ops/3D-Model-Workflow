"""Phase 11: cancel the render that is running in the editor (Movie Render Graph quick render or Movie Render Queue).
Used by floor_watch.ps1 when free commit memory falls under the hard floor. Returns what it found and did."""
import json
import unreal
queue = unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem)
out = {"was_rendering": bool(queue.is_rendering())}
if queue.is_rendering():
    executor = queue.get_active_executor()
    if executor is not None:
        executor.cancel_all_jobs()
        out["cancelled"] = True
json.dumps(out)
