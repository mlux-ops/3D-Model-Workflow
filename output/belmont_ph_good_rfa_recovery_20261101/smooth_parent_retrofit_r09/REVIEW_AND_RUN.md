# Smooth R09 native photometric parent — implementation handoff

Status: **SOURCE-ONLY / UNEXECUTED / UNAPPROVED**. Never distribute as a completed family until the native gates below pass.

## Build strategy

The recovered Hinkley Eos R05 is a native Revit 2025 `Lighting Fixtures` family with `WorkPlaneBased` placement, one valid `LightType`, and a photometric-web distribution, verified in `../native_release_audit.json`. It is used **only as a native light-source seed**. The script deletes every physical Hinkley `FreeFormElement`, `ImportInstance`, and `FamilyInstance` from the copy, replaces type identity, and loads one nonshared nested instance of untouched Modern Forms Smooth R02. The parent remains the only schedulable root. It binds the exact official manufacturer LM-63 `FR-W2502-52L.IES`, whose SHA256 is `6044dda98294020d03decd14ad118be2717845536597d1ca9bb9cc296fdcda8e` and tested flux is 707.09 lm. All sources are immutable SHA guarded.

Builder: `E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_recovery_20261101\smooth_parent_retrofit_r09\build_smooth_parent_r09.py`

Runner: an **isolated, document-free Revit 2025** pyRevit IronPython 2.7 environment, invoking the builder by full absolute path. Do not run with an active user project. Preserve its `native_build_receipt.json`; failed scripts create no promoted candidate. Native execution has **not** yet been attempted.

## Native QA required independently of the builder

1. Open both original Smooth R02 and R09. Compare source SHA and exact 9 `FreeFormElement` plus 13 `ImportInstance` parts; R09 must contain exactly one nested instance of the original nonshared Smooth and zero remaining Hinkley geometry. Audit all family type names and all Hinkley-related source parameters; reject stale manufacturer/type identity. Confirm only **one root type** and no nested shared family in the project schedule.
2. Validate nesting on a disposable ceiling underside; assert the instance is genuinely face hosted, that its family placement is `WorkPlaneBased`, and that nested fan's coordinate transform and material appearances are preserved. Measure blade sweep from actual placed mesh geometry, not the proxy light-source bounding box. Expected 1321.6925205853231 mm radial swept envelope with <=1 mm difference, without rotating or offsetting the OEM blades. Compare each source part's position and angular orientation, not merely its size.
3. Reopen the R09 family and call `DB.Lighting.LightFamily.GetLightFamily(doc)`. Require `GetNumberOfLightTypes()==1`, real `DB.Lighting.PhotometricWebLightDistribution`, exact IES filename on both the distribution and family type parameter, `InitialFluxIntensity.Flux==707.09` lm, zero Revit warnings, and unchanged parent hosting. Report actual emitter transform and confirm it is below the lamp diffuser, outside opaque solids and aimed down according to IES photometric orientation. **This position/orientation is not automatically corrected by the builder.**
4. Load into an empty disposable project and render/evaluate actual room illumination with the IES alongside an untouched IES reference. Confirm photometric output remains after copying to a fresh machine with the IES sidecar. `16.7549 W` is measured photometry; `16 W` is nominal LED-kit rating. Neither is verified whole fan electrical input.
5. Determine whether a root electrical connector is required for construction BIM; original Smooth and Hinkley R05 both have zero. A photometric LightType does not create electrical circuitry. If needed, construct `DB.ConnectorElement.CreateElectricalConnector` on a valid parent planar reference with correct `ElectricalSystemType`, and independently verify `MEPModel.ConnectorManager`, voltage, apparent load, circuit creation, and schedule in a disposable project. Fan motor supply/control specifics are unknown and must not be invented.

## Known API barriers and anticipated native failures

- `LightFamily` offers no public light-type constructor in Revit 2025; editing a source with zero light types and toggling `FBX_ASSET_TYPE` did not activate Smooth R02. A photometric file text field alone is insufficient. Existing native Hinkley R05 is the vetted parent source.
- Revit may reject nesting a face-based OEM fan using `FamilyCreate.NewFamilyInstance(ReferencePlane.GetReference(), XYZ.Zero, XYZ.BasisX, symbol)` depending on its host requirements. The builder fails closed and records the exception. If so, rebuild from OEM geometry within a validated face-based light template, using `FreeFormElement.Create` for solid forms and separately audited imported CAD. Do not approximate or reconstruct the original blade envelope.
- The Hinkley source is retained as the seed, which can carry other seed-specific category/parameter artifacts. An independent type/element inventory must pass before release.
- `SaveAs`, fresh reopen and family-level photometry do not establish project photometric direction, portable IES resolution, or electrical functionality.

Source audit: `../native_release_audit.json`, `../unpacked/QA/independent/SMOOTH_FRW2502_EXACT_IES_R03_EVIDENCE.md`, and `../unpacked/WORKFLOW.md`.
