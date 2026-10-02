# Errors and fixes (2026-09-29, xhigh arm)

Every error I hit, in order, with cause, fix and status. "Resolved" means the fix was run and the result checked.

| # | Action | Observed | Cause | Fix / next step | Status |
|---|---|---|---|---|---|
| 1 | `pdftoppm` / `pdfinfo` on the install sheet | exit 127, command not found | The brief says Poppler is on PATH; in this shell it was not | Wrote my own vector-stream renderer (`source/pdf_draw.py`); the sheet has no raster | Resolved (worked around) |
| 2 | Bash `cd` between commands | Later commands ran in the wrong folder (several times) | The shell's working directory persisted | Absolute paths only | Resolved |
| 3 | First analysis of `work/pdf/points.json` | Wrong path picked | I indexed by position | Select paths by bounding box | Resolved |
| 4 | `explore1.py` | `Modification of the document is forbidden` | `doc.Regenerate()` called outside a transaction | Removed the call | Resolved |
| 5 | Reading `explore1.json` | An 8,828-line JSON cost about 58k tokens to read | I read it whole | Filter with small Python scripts | Resolved (process) |
| 6 | `explore2.py` | `UnicodeDecodeError` in `json.dump` | IronPython 2.7 and a degree sign | `guard.dump_json` (ensure_ascii) | Resolved |
| 7 | `ElementTransformUtils.CopyElements` on the light source | `Light source can not be copied` | Revit forbids copying light sources between documents | Create the source with `OwnerFamily.get_Parameter(FBX_ASSET_TYPE).Set(1)` | Resolved (worked around) |
| 8 | `FamilyManager.Set` on Initial Intensity, Initial Color, Light Loss Factor | `Parameter name: familyParameter` | These are not settable as ordinary family parameters | `LightFamily.GetLightFamily(doc)` and `LightType.SetInitialIntensity/SetInitialColor/SetLossFactor` | Resolved |
| 9 | `get_Geometry` on the light source element | no such attribute | The element exposes no geometry | Use its bounding box and `GetLightSourceTransform` | Resolved (informational) |
| 10 | Runner stall: `explore4.py` through `revit_run.py` | The script finished in about 37 s but the runner returned only at its 900 s timeout (`END code=124`, 22:08:05 to 22:23:05). It held the shared Revit lock for 15 minutes and delayed another arm by about 920 s | **Unknown.** Every later run I timed (14 to 29 s) returned normally | Used shorter timeouts afterwards and wrote JSON before closing documents. I did not retry blindly | **Unresolved (cause unknown)**; reported in the final message |
| 11 | `explore6.py` light-source bounding box | `None` | Read in the same transaction as the shape change | Read after commit | Resolved |
| 12 | Build 1 warning | `Light source is inside solid geometry. No light will be emitted during rendering.` | The shade was a solid sphere | Made the shade hollow with an inferred 0.10 in wall; no warning on reopen | Resolved |
| 13 | Build 1 view export | `Path does not exist` | `work/export/` did not exist | `os.makedirs` | Resolved |
| 14 | Build 1 Apparent Power | Displayed `0.28 VA` for a value of 3.0 | Internal units are not VA | `UnitUtils.ConvertToInternalUnits(3.0, UnitTypeId.VoltAmperes)`; now `3.00 VA` | Resolved |
| 15 | Family-view exports | Zoomed out, with a huge grey slab | The template's uncategorised host extrusion can't be hidden, and a section box does not change fit extents | Set the crop box from projected bounding-box corners; the grey backdrop remains | Resolved (limitation kept) |
| 16 | Validation run 1 | `AttributeError: Name` on `Family.Name` | IronPython does not expose `Name` on `Family` / `FamilySymbol` | `DB.Element.Name.GetValue(e)` | Resolved |
| 17 | Shade analytic measurement | Reported the base-ring arcs (0.9014 and 1.8028) | A heredoc patch wrote a literal newline into `split`; `RevolvedFace` has no `GetProfileCurve*` | `splitlines()`; replaced with a sphere fit on LOD 1.0 vertices (exact; poor at LOD 0.5) | Resolved |
| 18 | Hosted-on-wall view | Fixture rendered flat black | My material-swap test left the type parameters on `ZZ Test Metal` and `ZZ Test Glass`, which default to black | Restore the original type-parameter materials after the swap test and read them back | Resolved |
| 19 | Repeated `SaveAs` of the RFA | `.0002`, `.0003`, `.0004.rfa` backup files appeared | Revit's backup-on-save | Deleted before finishing | Resolved |
| 20 | Disc-off exports from the family document | Pixel-identical to disc-on (max pixel difference 0, identical sizes) | A family-document view does not apply the Yes/No visibility parameter; a project instance does | `source/render_hosted_off.py` sets the instance parameter in a hosted project and exports there; the invalid exports were deleted. Caught by the identical file sizes | Resolved |
| 21 | `fit_camera_black.py` first run | Exceeded the 300 s foreground limit and Bash moved it to the background | Dense distance matrices and 27 starting points | Stopped it by task ID (not by process name); switched to `cKDTree`, subsampled points and 8 starts (about 4 s) | Resolved |
| 22 | Sphere/disc boundary segmentation in `fit_camera_black.py` | Sphere RMS 110 px, free circle r 254 px | The segmented boundary leaked into the white background | Convex-hull-inside filter plus a 140 to 225 px distance band; sphere RMS now 1.6 px | Resolved |
| 23 | Plate-rim term in `fit_camera_black.py` / `fit_camera_black2.py` | Plate RMS 13 to 20 px in every configuration | Unknown; the drum in the photo is longer and cut at a different angle than in the model, which probably explains it | Did not tune the model to it; recorded in the README. Roll and elevation stay degenerate and both fits are shown | Unresolved (recorded as a fidelity deviation) |
| 24 | Process slips | Ran `hosted_probe.py` twice in one command; briefly viewed a contact sheet indirectly before rebuilding it at 780 px wide | My mistake | None needed; no harm | Resolved |

## Environment notice, not a task error

Three connectors (Devil's Advocate, FormEdge, Meridian Connector for QuickBooks) reported that they need authentication. This session is non-interactive, so they cannot be authorized here; they stay unavailable until authorized in claude.ai connector settings. None was needed for this task.
