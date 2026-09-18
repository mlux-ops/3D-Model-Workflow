# Project memory and error logging

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

User instruction, recorded 2026-09-17: **All materials must appear seamless and non-repeating.** Apply immediately to every new or revised material and to acceptance reviews of existing materials.

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
