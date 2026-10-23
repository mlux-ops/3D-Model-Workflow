# Wieland hidden linear wall grazer (uplight) - Revit 2025 family

Built from `Wieland_Strip_Grazer_Fixture_Spec.md` (1529/1527 N Wieland, 25-006, replaces LSI PST strip 17775622).

- `Wieland_Hidden_Linear_Wall_Grazer_4-10_2800K_R2025_Rev2.rfa`: **current**. (`..._R2025.rfa` is Rev1, superseded: its cone ran along the fixture.)
- Details: Lighting Fixtures, face-based (WorkPlaneBased), type `4-10 Grazer 2800K`, Light Source on.
- Body: 4'-10" x 2" x 1 1/2" box, type material parameter `Body Finish` (matte black). Sits on the host face, centred.
- Light: Line, length 4'-10", Spot, beam 10 deg, field 30 deg (spec range 25-30), **Tilt 90**, 2,500 lm, 2800 K, loss factor 1.0. Source centred, 1 3/4 in above the host face, rotated 180 deg about X, and Tilt 90 turns the cone to +Z (up the stone). Rev1 used tilt 0 per the spec and the cone pointed along -X, parallel to the fixture. For a Line + Spot source the source frame's -Z is not the cone axis; the spec's aim recipe does not hold for this configuration.
- Not set: IES (none per spec). `Emit shape visible in rendering` does not exist on this template.

## Verification (validation.json, 26 gates, all pass)
Saved/reopened in Revit 2025, zero warnings, hosted on the top face of a ledge in a disposable project, the spot-cone solid of the light source runs from the source straight up 120 in, centred in X and Y (world direction 0, 0, 1), source 1.75 in above the host, body envelope 58 x 2 x 1.5 in, material substitution on all 6 faces, views in `views/`.

## Not verified
The graze on the fluted stone. Headless Revit can't ray trace artificial light. Place at 4-6 in from the stone face on the band ledge, set Ray Trace / Exterior: Artificial only, and check that light reaches the roof line.
The field angle of 30 deg is the top of the spec's 25-30 range; lower it in the type if the roof line is overlit.

Rebuild: `python _harness/revit_run.py <abs>/source/build_grazer.py`, then `validate_grazer.py`.

Evidence for the aim: `source/explore_aim.py` and `explore_aim.json`, `explore_aim2.json`, `explore_aim3.json` (cone solid per tilt/rotation). Tilt 0 gives -X, 45 gives -X/+Z, 90 gives +Z.
A headless ray trace is not possible (ExportImage returns a hidden-line image), so the cone symbol is the evidence, not a render.
