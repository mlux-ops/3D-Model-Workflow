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

## Final package delivery to Google Drive

User instruction, recorded 2026-09-14: Every outputted final material or 3D model package must be uploaded to Google Drive under **3D Model Workflow** (folder ID `1Xsd3Y96SOi00cWNaxqYeqlp4tNe3Z8CD`).

- File final model packages in **3D Models** and final material packages in **Material Packages** beneath that folder.
- Preserve the local deliverables and include all required companion textures, setup notes, and native files in the uploaded package.
- Check for an existing identical package before uploading to avoid duplicates. Clearly identify superseded revisions when retaining historical deliveries.
- Verify uploaded file metadata and report the Drive link. Local creation or placement in a sync directory alone is not evidence that upload completed.
- This is standing authorization to upload these project deliverables to that destination; no repeated confirmation is needed. If upload fails, log the error and report the pending upload rather than claiming delivery is complete.
