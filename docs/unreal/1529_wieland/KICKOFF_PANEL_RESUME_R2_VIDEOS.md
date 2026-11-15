# Kickoff prompt: resume after the out-of-video-memory crash, finish Phase 20 round 2, then the owner's path videos, editor panel

Written by the supervising session on 2026-11-15 at about 12:50, after the editor closed on an "out of video memory" error during the D1 path-traced still (error 10 of Phase 20 round 2 in PROJECT_MEMORY). Everything below the line is the prompt.

---

Resume the 1529 N. Wieland scene plan after the out-of-video-memory crash: finish Phase 20 round 2's last checks without running out of video memory again, then make the owner's seven walking-path videos and delivery r3

What this session is for

You are working in the Unreal Engine 5.9 project `D:\Unreal_Engine_Projects\Wieland1527 5.9\Wieland1527.uproject`, for the plan in `E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\docs\unreal\1529_wieland\PLAN.md`. You have none of the earlier chats' memory; their records are in that plan folder.

Your full brief is `KICKOFF_PANEL_VIDEOS_PHASE20R2.md` in the plan folder: Part 1 is Phase 20 round 2, and Part 2 is the owner's path videos and delivery r3. Read it, together with `phase20_results.md`, in particular:

- the first Status line;
- journal line J15;
- the section "How to resume round 2";
- the report.

Also read the "Phase 20 round 2" section of `E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\PROJECT_MEMORY.md`, especially error 10.

Where it stands

- Every model change of round 2 is saved on disk:
  - the Hancock refinement;
  - the nine landmarks added;
  - the instance settings;
  - Two Prudential's spire.
- J15 is partly done: the panoramas with all 27 landmarks labelled and the 12 real-time stills.
- **Still to do in round 2:**
  - the D1 path-traced still;
  - the frame-time and video-memory profile;
  - the two grazing-light frames;
  - J15's outcome, the report's frame-time line, and the status set to DONE.
- **Then Part 2:**
  - the owner's seven requested paths (Roof Deck, Basement Tour, First Floor, Second Floor, Third Floor, Fourth Floor, Grade Level; read `owner_review\paths\RENDER_REQUEST` again in case the owner has added paths);
  - delivery r3 on D: and Google Drive.
- **The editor was restarted by the owner after the crash.**
  - If it opened `L_R15_Production`, open `/Game/Wieland1529/L_Site_M4` by script, and save nothing.
  - Let the level settle for five minutes, then read `r.RayTracing.Nanite.Mode` back as 0.
  - Add a journal line recording the restart and whether the owner restored the three unsaved levels. Look at the levels' state; do not guess.

Video memory: what went wrong, and the rules from now on

The graphics card has 16 GB. The crash came on a path-traced render at 3,840 by 2,160 with 1,024 samples and `r.RayTracing.Nanite.MaxAppendInstances` raised to 400,000. It ran straight after 22 real-time renders in the same editor session, with nothing freed between them. Round 1's D1 path-traced still finished in 189 s. From now on:

1. **Before every heavy step, free memory and measure it.** Heavy steps are any path-traced picture, the profile, and each video.
   - Open an empty level, then `L_Site_M4`, then run garbage collection.
   - Read the card's used video memory with `nvidia-smi --query-gpu=memory.used,memory.total --format=csv` and write it in the journal.
   - Start only when used memory is under 9 GB with the level loaded. If it is not, free memory again. If it still is not, say so in one line and look for what holds it, such as another program using the card.
2. **Log memory while the step runs.** Log the card's used memory and the editor's committed memory every few seconds (`tools\memory_log.ps1`, with `nvidia-smi` added if it lacks it), into the profile folder.
3. **The D1 path-traced still uses round 1's settings,** not round 2's heavier ones. Use round 1's resolution, samples and console values, which are in `review\phase20\stills_driver.log` and `review\phase20\scripts\`. Leave `r.RayTracing.Nanite.MaxAppendInstances` at its default unless round 1 changed it.
   - If memory rises toward 15 GB during the render, stop it before it fails.
   - If the render fails or stops, change one thing at a time: first the resolution to 1,920 by 1,080, then the sample count. Record each try.
4. **Videos render in real time,** one at a time, with memory freed and measured before each one. The real-time profile measured about 8.8 GB.
   - If a video's memory climbs past 14 GB, stop it. Then lower its resolution or the quality setting that drives memory (for example the virtual shadow map pool or the streaming pool), put the setting back afterwards, and read it back to confirm.
5. **If an "out of video memory" or other fatal dialog appears again,** do not press OK: that closes the editor, and closing it ends this chat.
   - Write the journal line and the error entry, and commit them.
   - Then say in one line that the owner must clear the dialog, and stop.

Everything else follows the full brief

The order, the records and the commits are as the full brief says:

- the path videos only after round 2 is DONE;
- the journal line marked PENDING and committed before each step;
- every error logged with cause, fix and status;
- commits by explicit path on `claude/1529-wieland-scene-plan-e84a03`;
- no push or merge.

What is still the owner's, and the standing rules, are also as the full brief says:

- never restart, close or quit the editor;
- no free-memory floor for system memory (the video-memory checks above are separate and do apply);
- clean built forms only;
- Nanite ray tracing stays OFF (`r.RayTracing.Nanite.Mode` 0);
- never save `L_R15_Production` and never use "Save All";
- never edit a Datasmith asset;
- the material rule (seamless, non-repeating, a colour map, checked under grazing light);
- the Edit or Write tool for text with backslashes;
- put back every setting you change, and read it back to confirm;
- no Google content of any kind.

Keep going through both parts. If you notice yourself offering to stop or handing back a list of remaining steps, do the next step instead, except in the case of rule 5 above. Give a one-line update as each step or video finishes, with the video memory it used. Finish with the short report the full brief asks for, in plain words for an owner who knows Revit and construction well and Unreal less well, with the full path of every file you wrote.
