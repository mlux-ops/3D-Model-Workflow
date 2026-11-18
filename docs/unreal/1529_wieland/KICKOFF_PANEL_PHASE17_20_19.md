# Kickoff prompt: finish Phase 17, then Phase 20, then Phase 19, editor panel

Written by the supervising session on 2026-11-14 for the owner to paste into the Unreal editor's agent panel. Everything below the line is the prompt.

---

Finish the accurate site model (Phase 17), refine it from open images (Phase 20), then make the owner's path videos (Phase 19), for the 1529 N. Wieland scene plan

What this session is for

You are working in the Unreal Engine 5.9 project `D:\Unreal_Engine_Projects\Wieland1527 5.9\Wieland1527.uproject`, for the plan in `E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\docs\unreal\1529_wieland\PLAN.md`. You have none of the earlier sessions' memory; their records are in the plan folder. The owner is away and wants the work to keep going: decide what you can, and put anything that truly needs the owner in the final report.

There are three phases, in this order. Each has a full brief in the plan folder. Read each brief before you start that phase, and follow it, together with the rules below:

1. **Phase 17: accurate site model.** Brief: `KICKOFF_PHASE17.md`. Journal: `phase17_results.md`.
2. **Phase 20: refine the surroundings from open images.** Brief: `KICKOFF_PHASE20.md`. Journal: `phase20_results.md`, which you start.
3. **Phase 19: the owner's walking-path videos.** Brief: `KICKOFF_PHASE19.md`. Journal: `phase19_results.md`, which you start.

Where Phase 17 stands

- The work so far:
  - the laser-scan data is in;
  - the viewshed (what each viewpoint sees) is done;
  - 418 downtown towers and 144 Zone 1-2 buildings are built and checked against the point cloud;
  - the Variant Manager list `Surroundings` has "Laser-scan model (Phase 17)" as its default;
  - the roof-deck panorama and the silhouette check against two licensed photographs are done.
- After the owner said the roofs were jagged, every roof was rebuilt as clean built forms (J21 to J23, last commit `b634093f`). The roofs are flat planes with parapets, setbacks as prisms, pitched roofs from fitted planes, and crowns and rooftop structures as simple shapes.
- **The headless session was stopped at about 17:05** while fixing faults it had found in its own test renders:
  - dormers floating: fixed;
  - wall faces pointing inward, so walls looked folded: being fixed when it stopped.
- `tools\phase17_clean.py` and `tools\phase17_panorama.py` have uncommitted edits from that fix. Check them first: finish the wall-facing fix, rebuild and swap the buildings, and look at a test frame. Then commit.
- Then carry on from the first unfinished journal line (J24 onward):
  - re-render the stills and the roof-deck panorama with the clean roofs;
  - measure frame time against the Phase 9 budget;
  - fill in the acceptance table;
  - write the report;
  - set Status DONE.

Before Phase 20 and Phase 19

- **Phase 20** uses the owner's photographs in `D:\Wieland1529_owner_photos\` first, then KartaView and Wikimedia Commons. Mapillary is used only if the owner has left a token file there. Never use Google imagery of any kind.
- **Phase 19's plan images** are done (Phase 18, `owner_review\paths\plans\`). The path page is at http://127.0.0.1:8766/. If it is not running, start it with `owner_review\paths\Open path editor.bat`. Render only the paths the owner has saved with "Request videos", plus your own `_test_` path.

Keeping records

- **The journal:** for each phase, write a line marked PENDING and commit it before each step, then replace it with the outcome. A phase is finished only when its first `Status:` line says DONE, with the time.
- **Errors:** log every error in `E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\PROJECT_MEMORY.md`, with cause, fix and status.
- **Commits:** commit by explicit path on the current branch, `claude/1529-wieland-scene-plan-e84a03`. Do not push or merge.

What is still the owner's

- **Covered:** the downloads and locations each brief names, within their caps and at no cost.
- **Not covered; put these in the final report instead:**
  - anything with a price
  - any account or key
  - any deletion
  - any store or Fab asset
  - Google content of any kind
  - any change to Revit, Windows, drivers or the graphics card
  - any push or merge

Rules that apply throughout (these override anything older in the briefs)

- **Do not restart the editor.** This session runs inside the editor's panel, so closing it ends the session. Never close, quit or restart it.
- **Memory:** there is no free-memory floor any more (owner, 2026-11-14), so do not wait or stop because free commit memory is low. Free memory inside the editor when you need to: open an empty level and then the working level, or run garbage collection. Log the editor's committed memory every few seconds during heavy steps.
- **Roofs:** they must be clean built forms, never a draped scan surface (owner, 2026-11-14). This applies in Phase 20 as well: detail added from images is built as clean elements.
- **Nanite ray tracing stays OFF.** Keep the console variable `r.RayTracing.Nanite.Mode` at 0; mode 2 hung the graphics card three times. Render one picture at a time, and let a freshly opened level settle five minutes first.
- **Saving:** never save `/Game/Wieland/R15_Landscape/L_R15_Production` and never use "Save All". Save named assets only.
- **Datasmith assets:** never edit one; apply changes as overrides, new assets or recorded swaps. Keep the older surroundings options switchable.
- **Backslashes:** use the Edit tool, not shell commands, for any text containing backslashes; earlier sessions turned `\t` into tabs.
- **Settings:** put back any console or quality setting you change, and read it back to confirm.

Finishing the work

Keep going through all three phases. If you notice yourself offering to stop or handing back a list of remaining steps, do the next step instead. Errors, timeouts and failing tools are ordinary obstacles: diagnose them and work through them. If the same step fails twice, change one thing at a time. If something stalls, say in one line what is stalled, for how long, and the last stage you verified. Then try another route.

Progress and the final report

Give a one-line update as each step finishes. At the end of each phase, write that phase's report in its results file, as its brief asks. Finish with a short report that stands on its own:

- what each phase delivered, with its acceptance numbers;
- the new delivery package on D: and on Google Drive;
- the items that need the owner;
- the full path of every file you wrote.

The owner knows Revit and construction well and Unreal less well. Use plain words and full sentences, say what an Unreal term means the first time you use it, and use the same word for the same thing throughout.
