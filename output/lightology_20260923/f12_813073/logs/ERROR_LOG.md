# F12 error notes

2026-09-23
- Deferred Core method binding initially returned TypeError; resolved by looking up exact tool names from ALL_TOOLS.
- Assigned fixture folder did not exist; created the owned F12 folder tree.
- pdftotext/pdftoppm absent from PATH; using Python PDF fallback while retaining source PDFs.
- First view_image wrapper assumed an array result and threw TypeError; image files were unaffected.
- One JavaScript orchestration draft had a syntax error before execution; discarded and replaced with direct calls.
- Guessed Visual Comfort media URL for `rv_orbel_wall.zip` returned a PNG placeholder instead of a ZIP. Discarded; no manufacturer RFA reference is claimed. Official resource link resolution remains optional/pending.
- PRIME revoked the F12 native grant during launch handoff after the command had already spawned pyRevit 28320 -> Revit 40408. Both task-specific processes were terminated immediately. This interrupted attempt is not valid native evidence; PRIME owns the next serialized run.
- Static pre-recovery audit found two intended prep corrections had not persisted after an interrupted tool call: the globe revolve frame was still the earlier left-handed form and `review/VISUAL_REVIEW_CHECKLIST.md` was absent; hosted-project image export was also not present in the saved builder. Cause: the multi-step correction call was interrupted by the slot handoff before its write result was confirmed. Solution: re-applied the right-handed revolve frame, inserted Hosted Wall export into the disposable project QA, created the checklist, and re-ran Python compilation. Status: correction applied; native verification remains PRIME-owned.
