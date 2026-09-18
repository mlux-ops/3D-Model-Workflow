# Edge TXW2A — 18 nominal metal channel

## Revit family
`Edge_TXW2A_18_Chrome_R2025.rfa` requires Revit 2025 or newer. Load Family, then Place on Face on a native vertical wall. The insertion point is the center of the backplate. Category: Lighting Fixtures.

Fixed geometry for visualization. Edit type materials **Frame Finish** and **Diffuser Finish**. Polished chrome uses the installed Revit mirror-chrome appearance asset. The white lens is unlit; no electrical connectors, IES data, photometric light source, dimming simulation, or adjustable pivot is included.

## Dimensions and reference interpretation
- Selected visible table row: 18 nominal / **19.1 inches metal channel overall**. The 19.5-inch wood option is not used.
- Backplate: **4.62 x 4.62 x 0.37 inches**.
- Bar height: **0.9 inch**; center clamp width: **2 inches**.
- Side projection: **2.49 inches**, interpreted as plate 0.37 + gap 0.88 + clamp depth 1.24.
- The photo depicts a longer-looking variant. This reconstruction uses the visible table dimensions, so its bar-to-plate proportion is shorter than the photo.
- Bar depth, clamp height, hidden pivot, lens thickness, seams and edge profiles are inferred. The photo's chrome appearance is followed without assigning an unverified finish SKU.

Both supplied reference images are preserved in `references`. Redacted content was not reconstructed or treated as instructions. No external textures are required; appearance assets are stored in the family. The included builder uses the installed face-based family template and pyRevit/Revit API.

## Validation
See `validation.json` and native Revit preview images for saved-family reopen, dimensions, native wall-face placement, material substitution and warning results. Preview shading is a geometry/material review, not a production render or photometric validation.
