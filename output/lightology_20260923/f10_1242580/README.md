# F10 - Visual Comfort Covet KW 4115AB-ALB

Exact requested Lightology option: option_id=1242586, model KW 4115AB-ALB, Antique-Burnished Brass with Alabaster.

The selected Lightology option reports 18.25 in width, 2.75 in height, 17.25 in canopy, 50 W dedicated LED, 4000 lm, and 2700 K. Visual Comfort currently lists the same model at 18.25 in width and approximately 3 in height with a 17.5 in square canopy; this discrepancy is preserved rather than silently normalized. The generated family uses the exact linked Lightology option's 2.75 in overall height and 17.25 in canopy as the task-specific controlling dimensions.

Geometry is independently generated from the Revit 2025 English-Imperial Generic Model face based template, recategorized to Lighting Fixtures. The alabaster body is a shallow square tapered solid below a thin brass canopy, with the 18.25 in ceiling-side stone edge narrowing to an inferred 17.50 in exposed underside. Two opposite-side brass retainers are modeled from the exact option photograph and native manufacturer-reference bounds: the reference RFA contains two matching solids approximately 1.60 x 3.02 x 11.01 in. Their exact seating and corner treatment remain inferred.

source/visualcomfort_kw4115_reference.rfa is preserved as manufacturer reference evidence only. The build script opens it read-only for native inspection and records placement/category/solid bounds; generated output remains an independent family.

The natural alabaster appearance uses source/covet_alabaster_diffuse.jpg, a crop from the exact Lightology option photograph, bound to the editable Natural Alabaster material. Antique-Burnished Brass and Natural Alabaster are editable family material parameters.

Native acceptance requires: saved RFA reopen in Revit 2025, Lighting Fixtures category, real face-based host/reference in a disposable project, mounting normal, geometry bounds within tolerance of 18.25 x 18.25 x 2.75 in, material substitutions reaching geometry, 2700 K parameter, zero warnings, and exported front/side/oblique/material plus hosted evidence views.


## Native revision history

The first native run passed every technical gate but was rejected in self-review because four small retainers and an overly dark alabaster underside did not match the source. The saved builder has been corrected to two large seated retainers, reversed stone taper (wider at ceiling side, narrower underside), and stronger 2700K alabaster emission. A new native run is required; the first validation/evidence remain superseded until that rerun passes.
