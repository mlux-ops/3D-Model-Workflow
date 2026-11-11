# Open decisions for the owner

Written 2026-11-10. Companion to [PLAN.md](PLAN.md). Each decision has a recommended default that the plan is written against, and a note of what changes if the owner chooses otherwise.

## Already settled on 2026-11-10

| Subject | Settled as |
|---|---|
| Output | Both a real-time scene (2560 by 1440 at 60 frames per second on the RTX 4080) and offline work (path-traced stills at 3840 by 2160; animation at 3840 by 2160, 30 frames per second). |
| Extent | Full detail on both sides of Wieland for the block the building stands on, plus the alley behind. Simplified massing one block further each way. A stand-in for the city beyond. |
| Reference condition | A clear, leaf-on summer afternoon, with a leaf-off set used only to check massing. |
| Interiors | In scope. The Revit interior is fully built out and is to be refined in detail, furniture, geometry and materials. |
| Site visit | Yes. The shot list is in [REFERENCE_VIEWS.md](REFERENCE_VIEWS.md). |
| Starting point | The existing "1527 Wieland" Unreal site model is to be audited and improved. The audit is in [SITE_MODEL_AUDIT.md](SITE_MODEL_AUDIT.md). |

## Decisions waiting on the owner

They are ordered by how much each could change the plan.

### 1. Confirm that this is new construction

- **What records show:** demolition permits for the houses at 1527 and 1531 N. Wieland were issued in June 2026 and are marked complete, a new-construction permit for a four-story, four-unit residence was issued at 1529 on 2026-09-03, and the August 2026 street imagery shows the lot cleared and fenced. The default the owner accepted earlier ("existing building, renovated") does not fit these records.
- **Recommended default:** new construction. "Match reality" applies to the surroundings. The building is checked against the Revit model.
- **If otherwise:** if any existing structure remains in the design, it needs its own reference photographs and tolerances, and Phase 10 gains building stations.

### 2. Which engine version the project commits to, and when

- **What is known:** Epic calls 5.9 an unstable "MegaJam Preview" and advises copying projects. Assets saved in 5.9 do not open in 5.8. On 5.9 there is no NVIDIA DLSS plugin and no Cesium plugin, and the editor's experimental agent server did not start by itself on this workstation (it answered after the editor was restarted with it on). 5.9 offers a new lighting cache, better handling of overlapping glass, faster Nanite culling and more agent tools. 5.8.3 is installed; 5.8.4 is the current hotfix.
- **Recommended default:** no content work happens until the Phase 1 gate. The 5.9 copy (`D:\Unreal_Engine_Projects\Wieland1527 5.9`) is a test bench. The project commits to 5.9 only if every must-pass test in Phase 1 passes in 5.9 and at least one of the new 5.9 features gives a visible gain at a reference view for no more than 1.0 ms. Otherwise the project stays on 5.8, updated to 5.8.4, and the question is asked again when 5.9 is released in final form.
- **If the owner commits to 5.9 now:** the real-time tier loses DLSS as an option, the Google 3D city backdrop becomes unavailable, the risk of preview defects is accepted, and there is no way back to 5.8 for anything saved afterwards.

### 3. How build sessions reach the editor

- **Where this stands:** the agent server was answering by 19:30 on 2026-11-10 after the owner restarted the editor, and the owner installed the Unreal Engine skills for Claude Code. The owner intends to run later sessions from the terminal inside the Unreal editor.
- **Recommended default:** run sessions from the editor's terminal, one session per open editor, in a permission mode that asks before edits and commands. Set the server to start with the editor. Give the 5.8 project and the 5.9 copy different ports. Approve a short pointer file in the Unreal project folder so that those sessions load this repository's rules and this plan.
- **If sessions run from the desktop app instead:** they keep the browser, Revit and Drive connections, and need a connection file (`.mcp.json`) in the folder they start from to reach the editor.
- **If the server is unavailable:** every step marked "Agent" falls back to Python scripts the owner runs by hand, and the plan takes several times longer.

### 4. Keep and correct the existing site model, or rebuild the surroundings

- **What the audit found:** the sun was never set for the site (it is at the engine's template values for a December morning near Montreal), heights are estimates on a 2015 footprint layer, trees and street furniture are not evidenced, buildings are merged into grid cells that cannot be handled one by one, and several materials fail the repository's rules. The project shell, performance method, lot registration and material parents are sound.
- **Recommended default:** keep the project and its sound parts. Rebuild neighbouring massing from lidar, re-model the two adjacent buildings from site photographs, and replace all trees and street furniture from the site survey.
- **If the owner prefers a clean project:** Phase 1 creates a new project and migrates only the material parents and the performance scripts. This adds about one phase of work and removes inherited unknowns.

### 5. One site visit now, or also one in summer

- **The problem:** a November visit yields leaf-off photographs and a site under construction. The agreed reference condition is leaf-on summer.
- **Recommended default:** visit now for measurements, materials and the leaf-off photograph set. Judge the summer look by eye against Google's August 2026 imagery in a browser. Decide in spring 2027 whether a second visit is worth it.
- **If no visit happens:** tree species, trunk sizes, colours and the positions of poles, hydrant and signs cannot be scored, and the plan must say so in its final report.

### 6. What stands in for the distant city

- **Options:** (a) simple massing built from public lidar; (b) Google's 3D city tiles streamed live through Cesium.
- **Recommended default:** (a). It uses unrestricted public data, needs no account or payment, works offline, and can appear in any still or video.
- **If (b):** it needs a Cesium ion account or a Google billing account (the owner creates either one). It works only on engine 5.6 to 5.8. Google's attribution must stay on screen, nothing may be cached or baked, promotional video is limited to 30 seconds, and the terms are silent on other stills and video. Cost: Cesium's free plan is for personal, non-commercial use and its commercial plan is listed at 149 US dollars a month; Google's own price appeared to be 6 US dollars per 1,000 sessions after 1,000 free each month, which needs checking on the live pricing page. Both prices were read on 2026-11-10; the pages are listed in SOURCES.md.

### 7. Which lot width governs

- **The conflict:** the survey measured 50.18 ft of frontage and 50.50 ft at the rear; the record lot is 49.50 ft wide. The difference is 0.21 m, which is four times the placement tolerance.
- **Recommended default:** the Revit model's own lot lines govern, because the building was designed to them.
- **If otherwise:** the building shifts by up to 0.1 m against its neighbours.

### 8. Where trees, furniture and textures come from

- **Recommended default:** materials from the owner's site photographs first, then public-domain libraries, then authored work. Trees built per species once the site visit names them, using the engine's vegetation editor where it can produce the species and a licensed library where it cannot. Interior furniture from a licensed library chosen after the Revit model is opened. Each acquisition is asked for separately with its size and cost.
- **If the owner wants no store assets at all:** vegetation and furniture are authored, which is slower and limits species accuracy.

### 9. Disk layout

- **What was measured on 2026-11-10:** free space is C: 20.8 GB, D: 61.0 GB, E: 57.2 GB, H: 233.7 GB. The engine keeps 10.5 GB of processed-asset data on C:. The project copy holds 10 GB of content from other projects.
- **Recommended default:** the owner sets the environment variable `UE-LocalDataCachePath` to a folder on H: so that the cache leaves C:; the unrelated content is removed from the working copy; archives and offline frames go to H:.
- **If H: is a slow hard disk:** the cache goes to D: instead with a 20 GB cap, which leaves D: at 31 GB free against its 25 GB floor. E: has no room for it.
- **Not yet known:** whether that variable moves the 10.5 GB at all. Epic's page names a different default folder from the one the data sits in. Phase 1 step 1.4 measures it.

### 10. Records left by earlier work and by this session

- **Found:** a log from earlier work that stores a Google access key in plain text (path in [SITE_MODEL_AUDIT.md](SITE_MODEL_AUDIT.md), finding R1). Separately, the browser tool used in this session keeps a capture of each page it looks at in the session's cache under `C:\Users\cowey\.claude\projects\`, including about twelve Street View frames, and a research helper saved text copies of Google's terms pages in the session's temporary folder.
- **Recommended default:** the owner restricts or replaces the key, and approves deleting the Street View captures from the session cache.
- **If otherwise:** nothing in the plan depends on them; they simply remain on disk.

### 11. Rooms for the interior views

- **Recommended default:** one unit's main living space, kitchen and one bathroom, plus the entry at dusk.
- **If the owner wants every unit refined:** the interior phase scales roughly with the number of distinct rooms.

### 12. What is delivered, and where

- **Recommended default:** stills, the animation, a packaged Windows build of the real-time scene and the delivery notes uploaded to the Google Drive folder "3D Models" under "3D Model Workflow". This repository's rule asks for native files in the uploaded package, so the Unreal project archive (about 30 GB) is uploaded too, and a copy is kept on H:.
- **If the owner waives the native upload:** the project archive stays on H: only, and the delivery notes say so.

### 13. How the animation is rendered

- **Options:** the Path Tracer (about 90 seconds a frame budgeted, 45 hours for 1,800 frames) or Lumen at its highest settings with many samples per frame (about 15 seconds a frame, 7.5 hours).
- **Recommended default:** stills are path-traced. The animation uses Lumen at its highest settings, with one path-traced frame per shot rendered for comparison so the owner can see what is given up.
- **If the owner wants a path-traced animation:** allow two days of unattended rendering and the H: space budgeted for frames.

### 14. Smaller decisions

| Subject | Recommended default | If otherwise |
|---|---|---|
| The tolerances proposed in REFERENCE_VIEWS.md | Accepted as written until Phase 2 measures what the sources actually support | Tighter figures need more site measurements; looser figures shorten Phases 4 and 7 |
| Blender for re-modelling the adjacent buildings | Not used; the editor's own geometry tools are used | If approved, modelling is faster and adds an FBX step per building |
| Mapillary street imagery | Looking only | If the owner wants it used for textures or measurements, its terms need a legal reading first, as SOURCES.md explains |
| The existing project's Revit import (`Content\Wieland\Revit1527`, 2 GB, no recorded source) | Kept for comparison until Phase 3's fresh import is accepted, then removed | Keeping it costs 2 GB on D: |
