# Kickoff prompt: Phase 1, for a Claude Code session in the Unreal 5.9 Assistant panel

Paste everything below the line into a new chat in the panel. Before pasting, check that the model shows as Fable 5.2 and that the permission mode is not "Bypass permissions".

---

Kickoff: build Phase 1 of the 1529 N. Wieland scene plan

What this session is for

Carry out Phase 1 of an existing plan, and only Phase 1: prove the toolchain in Unreal Engine 5.9, take a baseline measurement, and import my Revit building once into a scratch level. You are running inside the Unreal editor that has the project `D:\Unreal_Engine_Projects\Wieland1527 5.9\Wieland1527.uproject` open. No content work starts until this phase is finished, so stop when Phase 1's acceptance list is complete and report.

Read these first

The plan lives in a git working copy outside this project folder. Read, in this order:

1. `E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\docs\unreal\1529_wieland\PLAN.md`. Read the sections "Rules for every phase", "What the owner settled on 2026-11-10", "How the build sessions run", "Facts every phase relies on", "Budgets" (for the fixed camera path and what a profile is), "Approvals this plan will ask for", and "Phase 1". The other phases are not yours.
2. `E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\docs\unreal\1529_wieland\ENGINE_NOTES.md`, for which engine features are untested.
3. `E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\docs\unreal\1529_wieland\SITE_MODEL_AUDIT.md`, for what is already known about the level.
4. `E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\AGENTS.md`, for the repository's standing rules.
5. The last section of `E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\PROJECT_MEMORY.md`, headed "1529 N. Wieland Unreal scene plan". The file is large; read that section, not the whole file. It records the errors already met and how each was solved.

What is already true

- I have committed to 5.9. The 5.8 original at `D:\Unreal_Engine_Projects\Wieland1527\` is never opened in 5.9 and never modified. If something fails in 5.9, work around it inside 5.9 using the workaround the plan names, record it, and carry on.
- My Datasmith export is at `E:\Claude\3D-Model-Workflow\references\1529 Wieland - Datasmith\25-006_1527_N_Wieland-3DView-3D_View_188.udatasmith`. Revit 2025 wrote it at the Unreal 5.3 level, and it has not yet been imported into 5.9. It holds 3,562 placed objects and 587 lights.
- The editor's agent server answers at `http://127.0.0.1:8000/mcp`. In this engine the discovery tools are named `list_toolsets`, `describe_toolsets`, `describe_tools` and `call_tool`. The Python tool takes its script as an object with `content` and `language`, returns only the script's final expression, and asks you to call its `read_me` first. Scripts run on the editor's main thread, so keep each call short.
- The production level is `/Game/Wieland/R15_Landscape/L_R15_Production`. Its sun is still at the engine's template values and its exposure is automatic; that is recorded, and fixing it belongs to a later phase.

Before you change anything

Do these three checks and tell me the results in one message:

- Make one read-only tool call to the editor and confirm it succeeds.
- Tell me which model you are running as and which permission mode the panel is in.
- Tell me which of these you have in this session: a web browser, file access to the `E:` paths above, and git.

In the same message, ask me for everything in Phase 1 that needs me, each with its size on disk and its cost: approval to archive the project to `H:` (step 1.5), approval to remove the unrelated Belmont and beech content (step 1.14), my action to move the engine cache to `D:` (step 1.4), and my second Datasmith export for the re-import rehearsal (step 1.8). Then keep working on every step that does not depend on my answers.

How to work

- Until the `H:` archive exists, save nothing. Do the read-only steps first: list the tool sets, finish the live audit, and take the baseline measurement.
- Do every test in a new scratch level under `/Game/Wieland1529/Scratch/`. Never save `L_R15_Production`, and never use "Save All". Save named assets only.
- You are the only writer to this project. A tool call that times out has an unknown result: inspect the editor's state before you repeat it.
- Follow the installed `unreal-mcp` skill: look for skills registered in the project first, read each result before the next call, and make dependent changes one at a time.
- If you have no browser for the sun check (step 1.10), give me the inputs and I will read the NOAA calculator for you: latitude 41.910215, longitude -87.635389, 15 August 2026, 15:30 Central Daylight Time.

Ask me before you do any of these

Install or update anything; download anything; get anything from Fab or another store; write outside this project folder and the plan's working copy; delete content; change Windows settings or my sign-in; push to the remote. Name the action, its size on disk and its cost. Reading files, read-only queries to the editor, creating scratch levels and assets, writing results into the plan's working copy, and committing there need no approval.

Done means

- Every line of Phase 1's acceptance list has a measured number, or the workaround the plan names for it, written into `E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\docs\unreal\1529_wieland\phase1_results.md`.
- The baseline profile is saved under `...\docs\unreal\1529_wieland\profiles\` in a folder named with the date and `M0`, and it records the viewport size.
- The live audit's missing part, the material on every part of the existing level, is appended to `SITE_MODEL_AUDIT.md`.
- Every error you met is logged in `PROJECT_MEMORY.md` with its cause, its fix and its status, in the same session.
- Those files are committed in the working copy on its current branch. Do not push.

Keep going until that list is met. Errors, timeouts and failing tools are things to diagnose and work through. Stop early only for something that needs my decision, and say plainly what you found. If something stalls, tell me promptly what is stalled, for how long, and the last stage you verified, instead of retrying the same action.

Progress and the final report

Give me a short update as each step finishes. I know Revit and construction well and Unreal less well, so use plain words and say what a term means the first time you use it. Finish with a report that stands on its own: what passed, with its number; what failed and which workaround replaced it; what is still waiting on me; the full path of every file you wrote; and whether anything in the project was saved.
