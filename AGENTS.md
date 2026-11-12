# Agent entry point

## Native Revit integration

For Revit work, start with [docs/NATIVE-REVIT.md](docs/NATIVE-REVIT.md).
The authoritative release pointer is [native-revit.json](native-revit.json).
Use `codex-native-revit-2025` / `native_revit_*` tools when available. Discover
tools by name or description if they are deferred. If MCP is unavailable, use
`python tools/revit.py <command>` for the same bridge and receipt protocol. This
wrapper reads the current client config, including URL and matching token file;
it also works when an existing chat's MCP process still caches old settings.
Do not choose an older bridge, pyRevit workflow, copied DLL, or dated output
folder merely because a search finds it first. Older workflows remain useful
references; select them deliberately when the native integration lacks a needed
capability, and explain that limitation.

Before native work:

1. Run `python tools/revit-doctor.py` from the repo root. This is read-only.
2. Check live capabilities and the returned Revit process ID.
3. Submit `documents.list` with `document: {}`; select the intended document's
   fresh session ID and verify title/path before further operations.
4. Read the operation contract and native evidence linked in the guide.

Never infer connectivity from installation or a visible tool catalog. Never
infer the intended document from the active window. Keep original operation IDs;
reconcile timeouts/unknown completion before another mutation. Saving and
synchronizing are explicit operations requiring task authorization and verified
receipts. Do not restart/close Revit or discard unsaved work to repair a bridge.
Never print, commit, or copy authentication tokens into prompts or repo files.

## Modeling work

Read [WORKFLOW.md](WORKFLOW.md) for modeling and visual acceptance requirements.
Preserve source references and existing deliverables. Write new artifact work to
its own `output/<task>/` directory. Verify native results and visual fidelity
separately. Record task errors and their resolution by appending to
`PROJECT_MEMORY.md`; preserve historical entries. Documentation and integration
maintenance may update their owning repo files when requested.

When updating the integration, update `native-revit.json`, the guide, and relevant
setup instructions together. Verify the actual installed assembly and live
process separately; a source change does not update an already running add-in.


## Standing geometry rule — November 4, 2026

All geometry created by any agent must remain directly editable by the user in Revit at any time. No DirectShape elements. Use native editable system elements or native families with editable sketches, forms, and meaningful exposed dimensions/material parameters. Do not substitute imported meshes, opaque FreeFormElement solids, or flattened geometry for editable construction. Verify Edit Family/Edit Sketch and parameter behavior before acceptance. Apply this rule to replacement geometry as well as new work.

# Project memory and error logging

## Stalls and retries

User instruction, recorded 2026-09-22: **If work or a tool is stalling, tell the user promptly instead of repeatedly retrying or polling without meaningful progress.** State what is stalled, how long it has been stalled, and the last verified stage. Do not make repeated attempts at the same action without new evidence or a changed approach. Continue independent work when possible, and report any remaining blocker clearly.

User instruction, recorded 2026-09-11: **Every time there is an error, log it in the project memory along with its solution.** This applies to all work in this project, including tool errors, failed commands, application import failures, incorrect outputs, and failed validation.

- Read [PROJECT_MEMORY.md](PROJECT_MEMORY.md) before starting work and apply its relevant lessons.
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

User instruction, recorded 2026-09-14: Every outputted final material or 3D model package must be uploaded to Google Drive under **3D Model Workflow** (folder ID `1Xsd3Y96SOi00cWNaxqYeqlp4tNe3Z8CD`).

- File final model packages in **3D Models** and final material packages in **Material Packages** beneath that folder.
- Preserve the local deliverables and include all required companion textures, setup notes, and native files in the uploaded package.
- Check for an existing identical package before uploading to avoid duplicates. Clearly identify superseded revisions when retaining historical deliveries.
- Verify uploaded file metadata and report the Drive link. Local creation or placement in a sync directory alone is not evidence that upload completed.
- This is standing authorization to upload these project deliverables to that destination; no repeated confirmation is needed. If upload fails, log the error and report the pending upload rather than claiming delivery is complete.
