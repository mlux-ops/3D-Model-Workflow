# Project memory and error logging

## File paths in replies

User instruction, recorded 2026-10-04: **Every file path you give the user must be a full absolute path they can copy and paste**, for example `E:\Claude\3D-Model-Workflow\output\wieland_strip_grazer\README.md`. No relative paths, no `output/...` shorthand, no bare filenames, no `~`. This applies to every reply, summary, README, hand-off note and memory entry. Use Windows backslash form for local files and put each path in code formatting. For Drive files, give the full Drive-mount path (`F:\My Drive\3D Model Workflow\...`) and the Drive link. Paths inside this file and in scripts may stay relative where they are code or repo-internal references; paths shown to the user may not.

## Effort level

User instruction, recorded 2026-09-26: **Default effort is high. Use max only for challenging textures, and only when the user requests it.** Don't pick max, or xhigh, on your own initiative, including for subagents and headless runs. The evidence is in `output/effort-trial-2026-09-26-hex/TRIAL_RESULTS.md`: max gave the best texture at about 4× the cost of high, and xhigh gave no clear gain over high.

User instruction, recorded 2026-09-30: **Model defaults by job type.** They come from the Sonnet 5.5 trial in `output/effort-trial-2026-09-29-sonnet/TRIAL_RESULTS.md`.
- **Revit family builds (light fixtures, casework profiles and similar):** Sonnet 5.5 (`claude-sonnet-5-5`) at **high**, for the main session, subagents and headless `claude -p` runs. All three efforts passed every native gate. xhigh and max cost 2.7× and 5× with no gain.
- **Materials and textures:** Opus 5.5 at **high** (user instruction, 2026-09-30, replacing a brief Sonnet-xhigh setting). It ranked 3rd of 6 in the blind texture review for $6.88. Use Opus max only for challenging production textures, and only when the user requests it. Never use Sonnet high for materials; it ranked last.
- **xhigh:** don't use it on either model.
- **The model and effort for this main session are set in the app's model and effort pickers, not by the agent.** When a family-build task starts in an Opus session, say so and suggest switching; for delegated work, pass `model` / `--model claude-sonnet-5-5 --effort high`.
- **Cost of `claude -p` Sonnet runs:** compute it from tokens ($2 in, $10 out, $4 cache write (1 h), $0.20 cache read per million). The CLI reports Sonnet 5.5 at Opus rates.

## Stalls and retries

User instruction, recorded 2026-09-22: **If work or a tool is stalling, tell the user promptly instead of repeatedly retrying or polling without meaningful progress.** State what is stalled, how long it has been stalled, and the last verified stage. Do not make repeated attempts at the same action without new evidence or a changed approach. Continue independent work when possible, and report any remaining blocker clearly.

User instruction, recorded 2026-09-11: **Every time there is an error, log it in the project memory along with its solution.** This applies to all work in this project, including tool errors, failed commands, application import failures, incorrect outputs, and failed validation.

- Before starting work, grep [PROJECT_MEMORY.md](PROJECT_MEMORY.md) for the artifact, product, tool or error you are working on and read only the matching entries; apply their lessons. Do not read the whole file — it is over 60k tokens and stays in context for every later turn.
- When an error occurs, record it in PROJECT_MEMORY.md during the same task. Include the date, affected artifact or action, observed error, known cause (or explicitly say it is unknown), solution or next step, and verification/status.
- If unresolved, log it immediately as unresolved; update the same entry when resolved. Do not invent a solution or claim success without evidence.
- For a repeated error, update its occurrence history and prevention guidance instead of silently treating it as new.
- Distinguish a confirmed error from an untested risk or a user-requested design change. Record applicable limitations without calling them failures.
- Do not include secrets, credentials, or unnecessary personal data in the log.
- Keep artifact-specific technical notes when useful, but also put each error and solution in the central project memory so later tasks can find them.

Existing discipline-specific conventions remain in [WORKFLOW.md](WORKFLOW.md).

## Material deliverables

User instruction, recorded 2026-09-18: An `.adsklib` with its required companion textures and setup notes is sufficient for material delivery. Individual Revit projects (`.rvt`) are not required when the library is provided; do not produce them by default. Temporary projects may be used for creation or validation. Deliver an RVT only when specifically requested or needed because no ADSKLIB is provided.

## Mandatory material appearance standard

### Revit material delivery — mandatory format

User instruction, recorded 2026-09-17: **Never use RVT-based material transfer again.** Do not deliver materials through Transfer Project Standards or copying material swatches between projects. Deliver a native `.adsklib` with all companion textures and concise library-loading notes. Verify the library opens and its materials/textures load in a disposable Revit project before calling delivery complete. If library creation is blocked, report the blocker; do not substitute an RVT transfer workflow. This overrides older package instructions. The user reported excessive transfer time and a suspected Revit crash; the crash cause is unconfirmed.

Workflow improvement, recorded 2026-09-18: **Every delivered Revit appearance must have at least one explicit bound color/diffuse bitmap in the ADSKLIB package.** A visually uniform finish may use a spatially uniform bitmap matching the intended base color; this is preferred to inventing grain, scratches, or other texture that the source finish does not have. Keep that bitmap with the library and verify the bound path resolves. Do not treat shader numeric values alone as a complete portable material package.

Workflow improvement, recorded 2026-09-18: **Release ADSKLIB revisions without overwriting a library that may be open in Revit.** Build to a candidate/temp file, run archive/readback checks, then release to a new revision or descriptive filename. If Windows reports a file lock, preserve the validated candidate bytes and release under a distinct filename rather than closing the user's working Revit session or forcing replacement.

User instruction, recorded 2026-09-17: **All materials must appear seamless and non-repeating.** Apply immediately to every new or revised material and to acceptance reviews of existing materials.

User instruction, recorded 2026-09-18: **Do not produce V-Ray material assets unless they are specifically requested.** VRMAT and VRSCENE files are not part of the default material deliverable. Build the Revit material, the `.adsklib` and the companion textures; stop there unless the user asks for V-Ray output for a particular job. Where a test or checklist lists a V-Ray gate, record it as *not requested* rather than blocked or failed, and keep any genuine tooling limitation recorded separately so the two are not confused.

- Follow the material construction and visual acceptance gate in [WORKFLOW.md](WORKFLOW.md#seamless-and-non-repeating-materials).
- Preserve intentional tile joints, flutes, and designed motifs; eliminate unintended texture seams and recognizable repeated texture blocks.
- A small repeated atlas, rotations of one face, or a successful native-file check alone does not satisfy this requirement. Do not deliver a material as final until the visual gate passes; explicitly identify pending checks and source limitations.

User instruction, recorded 2026-09-18: **A dimensional tile's sculpted pattern must read as relief, not as a faint texture.** When the supplied product is a 3D or dimensional tile, meaning its face carries a moulded, carved or otherwise sculpted geometric pattern, drive that pattern's bump and normal response noticeably harder than a photo-derived default produces. Reviewer feedback on the Adella M01 build: the grout-line relief was correct, the geometric pattern relief was too shallow.

- Judge relief under **grazing** light, never frontal only. Shallow relief looks acceptable head-on and disappears at a glancing angle, which is the angle it actually matters at.
- The pattern and the grout joint are separate depths. Deepen the pattern; do not deepen the grout to compensate, and do not raise a global bump multiplier that scales both.
- There is a hard ceiling: pattern relief must stay above the grout floor. If the pattern's deepest points reach or pass the joint depth, the tile face reads as punctured and the joint stops reading as a joint. Measure the clearance rather than assuming it.
- Record the chosen amplitude, the resulting relief in millimetres, the grout step in millimetres and the remaining clearance, so a later reviewer can see the margin that was left.

## Final package delivery to Google Drive

User instruction, recorded 2026-09-26: **All ADSKLIBs, colour maps and bump maps go in `F:\My Drive\Revit Material Maps - 25-012 651 Belmont`.** The rest of each package (README, notes, source-selection records, previews and scripts) stays in `3D Model Workflow/Material Packages`.
- Revit materials in the 25-012 651 Belmont project reference maps in that folder by the user's own names (for example `B1-01 - …`).
- Add new revisions under distinct filenames rather than overwriting a map the user has already placed there, unless the user asks for an in-place replacement.

User instruction, recorded 2026-09-26, for the ELM Formed Hexagon Sand job: no ADSKLIB is necessary; deliver colour and bump only.

User instruction, recorded 2026-09-26: **Each bump map is named with the tile name, the image's real-world size in feet and inches (the Revit Sample Size), and the bump amount to set in the Revit material.**
- Windows forbids `"` and `/` in filenames, so write inches as `in` with decimals, for example `ELM Formed Hexagon Sand - 5'-10.148in x 5'-10.875in - Bump 100.png`.
- **The Revit bump amount is a whole number on the editor's scale, which is 100× the stored value.** The Generic schema stores a float (default 0.3), and the editor shows it ×100 (default 30) in whole numbers, 0–1000.
  - Found 2026-09-26: the user saw 0.5 round to 0, and a render at 1 showed no visible relief.
  - Never quote the stored decimal. Quote the editor value, for example 100, not 1.0.
  - Calibration, confirmed by the user in a Revit view on 2026-09-26: for a full-range 16-bit dimensional map (ELM Formed Hexagon Sand: 2.6 mm full scale, 1.6 mm joint), 1 showed nothing, 50 showed joints only, and 100 made the tile relief read. Start dimensional tiles at 100.
- Name the colour map to match, without the bump amount.

Found 2026-09-26: **Revit's Texture Editor rounds Sample Size to the project's length units (1/4 in in the Belmont project).** A 39.39 in height became 3'-3 1/2", and the texture drifted off the model pattern.
- Choose the atlas so both Sample Size numbers are exact quarter-inch multiples, and whole inches where possible.
- If the real module can't reach that, absorb up to about 0.5 % in the drawn tile size (keep the joint) and record the drawn size against the actual size.
- Verifiers must fail a Sample Size that isn't an exact quarter inch.

User instruction, recorded 2026-09-26: **Every tile colour/bump delivery also includes a Revit model (surface) fill pattern `.pat`.**
- Put it in the same Belmont folder as the maps, named `<Tile name> - Model Pattern.pat`.
- Header `;%UNITS=INCH`, then `;%TYPE=MODEL` under each `*Name, description` line. Lines are the grout-joint centrelines at real scale, from the actual tile size plus the joint.
- Give it the same orientation as the maps. Put the pattern origin at the maps' top-left corner and state the first tile's offset from it.
- Add a second pattern in the same file for the rotated layout when the tile can be laid either way.
- Verify the file by re-parsing it and measuring line-to-joint offsets against the colour map or face-ID map, and view a 1:1 overlay preview.
- Examples: `output/elm_ligne_noir/source/e01_model_pattern.py` (stack bond) and `output/elm_formed_hex_sand/source/e01_model_pattern.py` (hexagon, dashed families).
- The request came after two deliveries had shipped without one. A Sep 23 ElmStone Fog Chevron `.pat` shows the format was already in use but had not been recorded as standing.

User instruction, recorded 2026-09-14: Every outputted final material or 3D model package must be uploaded to Google Drive under **3D Model Workflow** (folder ID `1Xsd3Y96SOi00cWNaxqYeqlp4tNe3Z8CD`).

- File final model packages in **3D Models** and final material packages in **Material Packages** beneath that folder.
- Preserve the local deliverables and include all required companion textures, setup notes, and native files in the uploaded package.
- Check for an existing identical package before uploading to avoid duplicates. Clearly identify superseded revisions when retaining historical deliveries.
- Verify uploaded file metadata and report the Drive link. Local creation or placement in a sync directory alone is not evidence that upload completed.
- This is standing authorization to upload these project deliverables to that destination; no repeated confirmation is needed. If upload fails, log the error and report the pending upload rather than claiming delivery is complete.
