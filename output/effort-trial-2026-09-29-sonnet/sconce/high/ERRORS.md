# ERRORS

Every error hit while building this family, with cause, fix and status. PROJECT_MEMORY.md is off-limits in this trial, so the log lives here.
Dates are 2026-09-29.

| # | Where | Error / symptom | Cause | Fix | Status |
|---|---|---|---|---|---|
| 1 | Input prep | `pdftoppm` not found | The brief says it is on PATH; it is not on this machine | Extracted the embedded raster images with `pypdf`. The install-instruction drawing is vector, so it could not be rasterised and was not used | Worked around; drawing not used |
| 2 | Light source | `LightFamily.GetLightFamily` threw "The document is not valid because it is not a light family document" | A face-based Generic Model document that is switched to Lighting Fixtures does not automatically contain a light source | After the category transaction commits, set the owner-family parameter `FBX_ASSET_TYPE` to 1 ("Light Source"); the source then exists (element 3202) | Resolved, confirmed in the saved RFA |
| 3 | Light source | `CopyElements` of a Light Source threw "Light source can not be copied!" | Revit does not allow copying the source between documents | Abandoned copying; enabled the source with the parameter (row 2) | Resolved |
| 4 | Exploration script | "Modification of the document is forbidden" | I called `Regenerate()` after `tx.RollBack()`, outside a transaction | Regenerate only inside a transaction (Commit already regenerates) | Resolved (my script bug) |
| 5 | Exploration script | `SyntaxWarning: invalid escape sequence \P` | Windows path in a heredoc string | Harmless; scripts now use forward slashes | Closed |
| 6 | Harness | `revit_run.py` waited 920 s for the Revit lock | The other arm's script hung and hit its own timeout, and the runner serialises Revit runs | Waited in the foreground, told the user about the stall, then continued. No retry loop | Resolved; not caused by this arm |
| 7 | Bash tool | First Bash call moved to the background on the tool's own timeout | Lock wait exceeded the tool timeout | It still completed; later calls set an explicit timeout above the runner timeout | Resolved |
| 8 | Validation | `AttributeError: Name` on `WallType.Name`; then `'getset_descriptor' object has no attribute 'GetValue'` | IronPython cannot read `Element.Name` on an `ElementType` through the normal binder | `DB.Element.Name.__get__(el)` (`ename` helper) | Resolved |
| 9 | Validation | "Modification of the document is forbidden" on `pdoc.Regenerate()` | Regenerate called outside a transaction after Commit | Removed the standalone calls | Resolved |
| 10 | Build | Light read back Wattage 100, Efficacy 3 | `InitialWattageIntensity` takes (efficacy, wattage); I passed (3.0, 100.0) | `InitialWattageIntensity(90.0, 3.0)`; read back 3.0 W / 90 lm/W | Resolved |
| 11 | Family views | A large dark slab dominated the family views | The face-based template contains a 96 x 96 x 12 in Extrusion (id 1537, no category, so category hiding cannot remove it) | Not part of the placed instance (confirmed by measurement). `HideElements` did not remove it in every view, so all four deliverable views are now exported from the hosted project instead | Resolved; slab is template decoration only |
| 12 | Family views | Exports with absurd aspect ratios (side 1400 x 7073, later 1400 x 14000) and a tiny fixture | `ExportImage` FitToPage fits the whole model, not the section box | Set a crop box around the fixture (`View3D.CropBox` in view coordinates); exports are now about 1400 x 1400 | Resolved |
| 13 | Validation | `FacingOrientation` was (0,0,1) on a wall whose exterior normal is (0,1,0), so it failed as a hosting check | Facing orientation is in the family frame, not the wall normal | Hosting is judged geometrically: backplate at w = 0..0.125 along the wall normal, all solids at w >= 0, host element is the wall | Resolved |
| 14 | Measurement | First envelope read 24 x 24 x 24 in | Revit adds a fixed 24 in "Light Source" proxy solid to the instance geometry (and to `get_BoundingBox`); the symbol size is read-only | `measure` excludes solids whose subcategory is "Light Source" and reports them separately | Limitation, documented in the README. Naive bounding-box checks will read 24 in |
| 15 | Views | Yellow translucent cube in views | The light-source proxy (row 14) | Hid the "Light Source" subcategory in the view | Resolved |
| 16 | Views | Shade looked grey and showed the socket through the glass | Milk glass was 15 % transparent in the shaded view | Set the glass transparency to 0 (opal glass is diffusing, not see-through) and rebuilt | Resolved |
| 17 | Process | Scripts were patched with a Python heredoc once | Convenience | Later edits use the Edit tool | Minor; closed |
| 18 | Housekeeping | `.0001.rfa` / `.0002.rfa` backup files appeared next to the deliverable | Revit writes backups on `SaveAs` over an existing file | Deleted them; only the final RFA remains | Resolved |

Not errors, recorded so they are not mistaken for defects: the height (7.63 in) forces a 17.93 degree face tilt where the photos measure about 15.8 degrees (see README, Inferred and compromise values).
