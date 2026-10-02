# Errors and lessons

Every error hit in this run, in the order found, with cause, fix and status. The project rule to log errors in `PROJECT_MEMORY.md` is overridden by the brief, which confines writes to this folder, so the log lives here. Dates are 2026-09-29 unless stated.

Kinds: **error** (something failed or was wrong), **stall** (work or a tool stopped progressing), **trap** (a measurement pitfall in the product, not a failure), **note** (recorded for completeness, not an artifact error). Numbers are stable: the README refers to them.

| # | Kind | Status |
|---|---|---|
| 1 | error | Resolved |
| 2 | note | Not an artifact error |
| 3 | error | Resolved |
| 4 | error | Resolved (lesson) |
| 5 | error | Resolved |
| 6 | stall | Resolved (cause unknown) |
| 7 | error | Resolved |
| 8 | error, caught before the run | Resolved |
| 9 | error, caught before the run | Resolved |
| 10 | design error, caught before the run | Resolved |
| 11 | design error, caught before the run | Resolved |
| 12 | error | Resolved |
| 13 | error | Resolved |
| 14 | error | Resolved |
| 15 | error | Resolved |
| 16 | stall | Resolved by mitigation (cause unknown) |
| 17 | trap | Documented |
| 18 | error | Resolved by a changed approach (cause unknown) |
| 19 | note | Recorded limitations |
| 20 | note | Applied from the start |
| 21 | note | Harmless |
| 22 | error | Resolved |
| 23 | error | Resolved |
| 24 | error | Resolved |
| 25 | error | Resolved |
| 26 | note | Not a geometry error |
| 27 | note | Risk did not occur |

## Entries

1. **Poppler tools missing.** `pdftoppm` exited 127 and `pdfinfo` was not found, although the brief says Poppler is on PATH. Only `pdftotext` exists. Fix: extracted the embedded images with pypdf and rendered the vector install drawing with the Windows PDF renderer (`_work/render_pdf.ps1`). Verified: `_work/pdf/` holds the renders and images.

2. **Noisy `which` output.** A `which` call printed a very long PATH. Not an artifact error; recorded because it wasted context.

3. **Contaminated fit in `_work/analyze_side2.py`.** The row range 700 to 900 included the start of the globe at row 889, so the cut-face angle fit was pulled off. Fix: rows 700 to 880, or the corner-to-corner line (about 17.2 degrees). Verified by the later `side_metrics.py`.

4. **Oversized tool output.** An unfiltered regex scan of `RevitAPI.dll` returned about 446 names. Lesson: filter narrowly and set a head limit. No artifact effect.

5. **Bash timeout ceiling.** A wait with `timeout=660000` exceeded the 600000 ms maximum, so the call was moved to the background after 600 s. Fix: foreground waits of at most 600 s and a runner timeout of at most 540 s. No job was left running.

6. **Runner queue stall.** `probe_light.py` waited 816 s (about 13.6 min) for `revit.lock` (START 22:23:57 in `_harness/revit_runs.log`, `wait=816s`). The lock freed by itself and the probe then ran 18 s with exit code 0. Root cause unknown: probably another arm's headless Revit ran long or hung. I reported it when it happened and did not retry or kill anything. Status: resolved.

7. **`doc.Regenerate()` outside a transaction** (`probe_light.py`, line 56). Revit refuses it. Fix: call it only inside an open transaction; every later script uses the `Tx` wrapper in `common.py`. Verified.

8. **Wrong constructor argument order (caught before the run).** `InitialWattageIntensity` takes efficacy first, then wattage; my first draft passed (3.0, 90.0). Fix: (90.0, 3.0) plus explicit setters and a readback. Verified in `validation.json` (3.0 W, 90.0 lm/W).

9. **Misread API documentation (caught before the run).** An empty search for `OST_Light*` in `RevitAPI.xml` was read as "the category may not exist". The XML does not document `BuiltInCategory` members. Fix: discover at run time; `OST_LightingFixtureSource` exists. Verified.

10. **Design error, silent warning deletion (caught before the run).** My first failure preprocessor deleted warnings, which would have made the zero-warnings gate dishonest. Fix: `FailureCollector` in `common.py` records every message and leaves warnings in the document; an error rolls the transaction back. Verified: 0 warnings on reopen.

11. **Design error, stale geometry (caught before the run).** `validate_sconce.py` kept `Solid` objects across the `Show Disc` toggle and the material swap; a solid is invalid after a document modification. Fix: `fresh_named()` fetches the solids again after each change. Exercised and passing.

12. **Light source not created by the category change alone** (build run at about 23:06). `LightFamily.GetLightFamily` raised "The document is not valid because it is not a light family document". I first concluded the source could not be created: `probe_light2` showed that `CopyElements` fails ("Light source can not be copied!"), and I planned to switch to the `Lighting Fixture.rft` template. That conclusion was wrong. `probe_light3` found that after the category change the family gains a settable Light Source property (default No), and setting it to Yes creates the source. Verified: gate 6 passes. The brief's template is used with no deviation.

13. **`ElementTransformUtils.MoveElement` on the light source rolled back** ("transaction move light ended as RolledBack"). Fix: `element.Location.Move(XYZ)`. Verified: position error 2e-5 in.

14. **`AttributeError: Name`** on `WallType.Name` and `FamilySymbol.Name` in the pyRevit IronPython engine. Fix: the `ename()` helper (`DB.Element.Name.GetValue`). Verified.

15. **Build-summary measurement artifact.** `part_report` sampled only edges, so the shade extents came out as the neck circle and the family envelope depth as 3.4168 in instead of 5.50 in. The geometry was correct (shade volume 3.4216 in3 against 3.41 analytic). Fix: sample edges plus tessellation vertices. Verified.

16. **Probe run timeout, Revit did not exit.** `probe_light2.py`: START 23:09:51, END code=124 at 23:14:51 (300 s). Every experiment and the `closed_all` record were written by about 23:10, but the headless Revit did not exit. The runner killed only its own process tree. Root cause unknown. Reported promptly. Mitigation: `close_doc` in `common.py` logs each close, and later runs exited normally.

17. **Light source symbol in the placed instance's geometry (trap).** The placed instance returns a 24 in "Light Source" sphere solid (2 faces, 7238.2 in3, symbol size read-only), so an unfiltered envelope reads 24 in. Handling: the envelope is taken from the five named parts, and the raw envelope, the excluded solid and `geometry_option_probe` are recorded in `validation.json`. See the README gate 3 caveat. Status: documented, not fixable in the family.

18. **Family-document `Show Disc` toggle did not change the family-view export.** `views/family_side_no_disc.png` was byte-identical to `family_side.png`. Cause unknown. Fix: removed those previews; `stage_no_disc_views` sets `Show Disc` to No on the placed instance and exports three wall-hidden views, then restores Yes. Verified: `no_disc_state_show_disc_value` 0, `show_disc_value_after_restore` 1, the disc solid absent while off.

19. **Published values against photo values (recorded limitations, not errors).** Photo plate thickness 0.257 in against 0.125 published; photo depth 5.63 in against 5.50 published (the plate accounts for it); photo cut-face angles 15.6 and 19.0 degrees (mean about 17.3) against the modelled 17.78; hero-photo globe offset from the disc centre about 0.20 disc heights against 0.165 modelled (a difference of about 0.27 in, unresolved); photo perspective about 1.08 times on the front-view globe. The published values were kept.

20. **Practices applied from the start.** Set family parameters with `FamilyManager.Set`, regenerate inside a transaction before bounding-box queries, convert .NET types for JSON with `default=str`, and use a section box and hidden categories for previews (the allowed precedent script `build_house_of_troy_usledz15.py` shows the first four); keep curves above the short-curve tolerance, read at run time from `app.ShortCurveTolerance` (my own check); pass absolute script paths to the runner (the brief's command); report stalls promptly rather than polling (the project stall rule). I did not read `PROJECT_MEMORY.md`, so none of this came from its error log.

21. **Harmless probe artifacts.** A search of `_work/build_result.json` for "Light Source" or "Host" found nothing because `family_param_list` reads `FamilyManager.Parameters`, not `OwnerFamily.Parameters`. A template-extrusion record held `"error": "'type' object has no attribute 'ELEMENT_IS_REFERENCE'"`, a probe field that does not exist. Neither affects the family.

22. **`make_overlays.py` registered the side view on the wrong column.** It picked faint white-on-white edges (a fringe column). Fix: `plate_extent()` takes the first column whose count reaches 0.75 of the maximum. Verified: scale 1.0120, 241.7 px/in, and the overlay lines up.

23. **`probe_side_cols.py` crashed** with `ValueError: zero-size array to reduction operation minimum` on an empty column. Fix: guard for empty columns.

24. **`side_metrics.py` first-version measurement errors.** The flat-edge range ran into the cut-face region, the globe circle fit used the wrong cap region, and the per-row right-edge deviation was ill-conditioned near a circle's top and bottom. Fix: bottom range x0 + 100 to + 300, top range x0 + 120 to + 600, circle fit on boundary pixels within 1.2 in of the far-right x, straight-line fits for the cut-face edges. Verified against the registered overlay.

25. **`measure_disc_rim.py` used the wrong apparent-width factor.** It used sin(view) = B/A = 0.5798 instead of sqrt(1 - (B/A)^2) = 0.8148, which made the thickness estimate 1.405 times too high. Fixed and rerun: median 0.030 in (mean 0.043, min 0.014, max 0.086, n = 13). An arithmetic slip while solving the tilt for t = 0.03 was caught and redone by series expansion.

26. **A by-eye side comparison suggested a proportion mismatch.** The photo cell looked smaller than the model cell. Cause: faint artefacts at the photo's left edge extend the content box of the tight crop, so the photo is scaled down. Not a geometry error: the registered overlay and `side_metrics.py` are the authority.

27. **Short-curve risk from the thin disc did not occur.** Rebuilding with a 0.04 in disc and the 17.78 degree tilt was expected to risk a short-curve warning (tolerance 0.0307 in, read from `app.ShortCurveTolerance`). Result: 0 warnings, all gates pass. The 18 degree, 0.07 in fallback build was not needed.
