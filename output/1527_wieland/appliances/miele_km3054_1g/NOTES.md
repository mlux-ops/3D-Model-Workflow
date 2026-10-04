# Miele KM 3054-1 G

Status: **BUILT_WITH_LIMITATIONS**. Recorded 2026-10-02T14:36:37.480895+00:00.

Smartsheet row IDs: 6670395252473732, 7831772394487684.
RFA: `miele_km3054_1g/miele_km3054_1g_R2025.rfa`. SHA-256: `1b105d404097a468ea8225a290ffb3046813d928c3985fc6a2987f8cc51e4db3`.

## Native evidence
Revit 2025 save/reopen: PASS. Category: Specialty Equipment. Placement: WorkPlaneBased; actual test host: Floors.
Actual full placed bounds (W x D x H): **942.000 x 526.000 x 88.000 mm**.
Comparison target (W x D x H): 942.000 x 526.000 x 53.000 mm.
Dimension gate: **PASS**; scope: body.
Dimension basis: 942 x 526 mm glass outline. 46 mm casing below + 7 mm glass above countertop = 53 mm casing height; installation drawing page 3.
Delta against comparison target (W, D, H): -0.000013, +0.000016, -0.000000 mm.
Material parameter substitution with geometry evidence: 3/3. Zero exposed parameters means the manufacturer materials remain nested/fixed, not that editability passed.
Family warnings: 0; placed-project warnings: 0.

Detailed native results: `../miele_km3054_1g/validation.json`.
Native previews: `../miele_km3054_1g/views/oblique - 3D View - oblique.png`, `../miele_km3054_1g/views/front - 3D View - front.png`.

## Visual review
Five burners are asymmetric: large wok burner at left, four smaller burners to the right, one left knob and four right knobs. Grate cross sections and elevation are inferred; full-height approval is withheld.

## Sources and access
- https://media.miele.com/downloads/n-/us/FS_11766750_USE_US-en-US.pdf
- https://www.mieleusa.com/product/11766750/gas-cooktop-km-3054-1

Manufacturer media were accessed through public product/download pages without a sign-in, new account, payment or acceptance interaction. No new redistribution license was inferred. Manufacturer copyright/terms remain applicable; this is an internal project working copy.
Original RFA hashes and source records are in `source_manifest.json`. An older download manifest can describe an overwritten ZIP filename; actual retained original RFA hashes, rather than a historical ZIP pathname, establish the source artifacts.

## Build and material dependencies
Entry point: `source/build.py`; shared implementation: `../build_custom.py` and `../family_common.py`. Always invoke the entry point by absolute path through the repository serialized Revit runner.
Manufacturer dimensions are fixed. Finish parameters are intended to flex. Companion uniform diffuse PNG files in `source/` are bound to appearance assets and checked after reopen. Revit stores their workstation paths; retain the source folder and relink/search that folder when relocating the family.

## Assumptions and limitations
- KM3054-1 replaces KM2355G per provided item correction. Wok burner is left-center, not centered.
- Grate height 35 mm above glass is inferred, not covered by the 53 mm casing dimension. Gas and electrical projections under the casing are omitted.
- Visualization geometry; no MEP connectors, operating mechanisms or fabrication tolerances.
- Overall dimensions are manufacturer dimensions. Undimensioned seams, controls, edge radii and optical properties are inferred from product imagery.
- Fixed product dimensions; editable finish parameters are the intended flex controls.
- Full height including grate is not dimensioned in the recovered sheet. Only the defined casing-height gate can pass; overall-height acceptance remains limited.

## Row identity decisions
- The supplied correction KM 3054-1 G governs the older KM2355G row wording.
- The supplied correction KM 3054-1 G governs the older KM2355G row wording.

## Blockers and disposition
No native save/reopen or placement blocker remains. Design identity, dimensional fit and material limitations above remain review holds. The section does not authorize procurement, installation or release for final visualization.
