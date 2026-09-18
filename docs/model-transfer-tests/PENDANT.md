# P01 — Adjustable Mila pendant

## Worked example and reading order

1. `references/mila/PRODUCT 661292 - Mila Pendant.pdf` and the images in `references/mila`: inspect both drawing and photos.
2. `output/mila/README.md` and `output/mila/REVIEW.md`: approved interpretation and known inferences.
3. `scripts/build_mila.py`: nested fixed body; native parent suspension; associated material parameters; save/reopen, host placement, flex and substitution checks.
4. `output/mila/validation.json` and three native PNGs: historical evidence format and visual reference, not new-run evidence.

The source builder constructs the body in local positive Z, then places the parent on an overhead face. Judge final orientation in the native test project, not by assuming local Z means world up. It calls `child.Regenerate()` before reading bounds; omission previously produced None bounds.

## A — Reproduction

Create a new Revit 2025 Lighting Fixtures RFA from the source references and adapted builder. Preserve:

| Requirement | Target |
|---|---|
| Placement | Underside of a native ceiling/floor face; pendant hangs down |
| Open capsule loop | 8.2 in wide, 29.1 in high; 0.5 in frame thickness |
| Canopy | 7.1 in diameter, 1.1 in high |
| Globe | 6.7 in diameter, lower end of loop; explicitly inferred |
| Band depth | 0.5 in; explicitly inferred |
| Default total drop | 60 in |
| Cord Length | Editable instance length; default 29.45 in |
| Total Drop | Read-only formula result: Cord Length + 30.55 in |
| Materials | Editable type parameters `Metal Finish`, `Glass Finish`, propagated to nested geometry |
| Finish | Dark metal/dark canopy, warm opal appearance |

The 29.1 in dimension describes the loop. The historical body bounds include a socket extending 0.35 in above it; do not incorrectly fail or shrink the loop because combined body height is 29.45 in. This is visualization geometry; no MEP connectors, IES or photometric claims are required.

Save/reopen the new RFA, place it on a native overhead face in a disposable project, and flex Cord Length through **8, 18.1496062992, 48 and 118 in**. Expected Total Drop values are respectively **38.55, 48.6996062992, 78.55 and 148.55 in**. Measure actual host-to-bottom geometry, not merely the formula parameter. Use the historical 0.1 in tolerance for total-drop checks; target 0.01 in for the specified loop and canopy dimensions, with measurement method recorded. These are test tolerances, not manufacturing specifications.

## B — Controlled variation

From your newly built family, create a separately named revision with **72 in default Total Drop** (41.45 in Cord Length) and a **user-requested satin brass appearance** for metal/canopy. Retain opal glass, geometry, hosting and material editability. Label this an independent visual variant; do not assert a manufacturer SKU. Record approximate appearance settings.

Freshly verify the 72 in default, then flex Cord Length to 12 and 60 in, expecting 42.55 and 90.55 in actual drop. Restore/save the requested default before final delivery. This stage tests adaptation rather than copying the existing RFA.

## Required evidence and acceptance

- New baseline and variant RFAs, nested source family, adapted builder, preserved references and setup README.
- Revit version, fresh timestamps, reopen result, category, native host ID/type and placement result.
- All flex values: input, formula result, actual measured drop, tolerance and pass/fail.
- Material substitution for both parameters: assign distinguishable test materials and verify actual face material IDs including nested solids. A parameter value change alone is insufficient. Restore requested materials.
- Family/project warning lists. Acceptance requires zero unexplained warnings; record any warning and its disposition.
- Native front, side and oblique views, including a view of the hosted fixture. Reviewer assesses loop continuity, globe location, canopy, centered cord, downward orientation and unchanged body dimensions across flex states.
- A separate visual verdict. Correct bounds and a loadable RFA do not prove reference fidelity. Shaded previews do not prove photometric output.
- Package integrity, hashes and Drive delivery status for final packages.

Pass requires both A and B technical and visual gates. Missing native access means blocked, not pass. Record repair attempts and log every error/solution in root PROJECT_MEMORY.md without changing historical entries.
