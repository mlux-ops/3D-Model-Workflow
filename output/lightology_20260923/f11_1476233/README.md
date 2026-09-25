# Terzani Mizu Round Multi Light Pendant - F11

Requested configuration: Gold crystal, 8.7-inch nominal width, 3000K. Exact matching Lightology option: TRZ1476232 / Terzani 0R03SE8A4ATE, White canopy / Gold crystal, 8.66 in W x 13.77 in crystal-cluster H.

The original supplied link is TRZ1476230 / 0R03SE8A4AT, the same 3-light / Gold / 8.66-inch configuration with G4 Xenon. The family follows the explicit 3000K selection and retains the linked option as provenance.

## Native model
- Revit 2025 Lighting Fixtures category from Autodesk Generic Model face based.rft.
- Round White canopy: 8.3 in diameter x 1.6 in H.
- Minimum installed total drop: 19.7 in.
- Three separate thin suspension cords in a triangular composition.
- Three vertically staggered, distinct hand-cast Gold crystal drops.
- Each crystal is a non-rotational asymmetric lofted outer shell minus an asymmetric inner loft, producing true hollow glass with an open crown/neck.
- Each drop uses its own scale, lean, radial phase and lobe amplitude; these are not repeated spherical globes.
- Three separate visible 3000K LED cores.
- Editable Canopy Finish, Cord Finish, Crystal Finish and Emitter Finish material parameters.

## Numeric/source gates
Authoritative: 8.66 in body width, 13.77 in crystal-cluster height, 8.3 in canopy diameter, 1.6 in canopy height, 19.7 in minimum overall height, 74.8 in listed cord length, approximately 3.9 in individual crystal height. The 3000K option is 3 x 1.5W integrated LED, 4.5W total, 438 delivered lumens, not dimmable.

Inferred from photographs: plan offsets, precise stagger distribution, cord diameter, glass wall thickness, LED core size, and exact organic surface variation. See sources/SOURCE_REVIEW.md and sources/source_manifest.json.

## Builder
build_mizu.py syntax-checks with C:\Python314\python.exe.

Prime-owned native command:

D:\Games\pyRevit-Master\bin\pyrevit.exe run "E:\Claude\3D-Model-Workflow\output\lightology_20260923\f11_1476233\build_mizu.py" --revit=2025

Native execution, RFA reopen/host/material/warning gates and source-vs-native visual review remain pending until PRIME runs the serialized Revit slot.
