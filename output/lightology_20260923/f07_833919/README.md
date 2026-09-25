# F07 - Nodes Angled Wall Sconce (KW1041)

Status: PREPARATION COMPLETE / NATIVE AND VISUAL GATES PENDING. Native Revit slot is currently assigned to F03; do not launch this builder until prime grants F07 the slot.

## Requested deliverables

Two independent native Revit 2025 face-based Lighting Fixtures RFAs:

- `Visual_Comfort_Nodes_KW1041BBS_Burnished_Brass_R2025.rfa` - Burnished Brass / Milk, Lightology VCS833918, manufacturer model KW1041BBS.
- `Visual_Comfort_Nodes_KW1041MBK_Midnight_Black_R2025.rfa` - Midnight Black / Milk, Lightology VCS833919, manufacturer model KW1041MBK.

## Published product data

Nodes Angled Wall Sconce by Kelly Wearstler for Visual Comfort Studio. Published size is 8 in W x 7.63 in H x 5.5 in D. Round backplate is 5.25 in dia x 0.125 in D. Milk glass shade is 3.5 in dia x 3.25 in H. Materials are glass and steel. Lamp is 1 x JCD/G9/3W/120V LED, bulb not included; standard 120V dimming; ETL/cETL damp location.

## Geometry interpretation

The manufacturer installation sheet confirms the assembly sequence: round mounting/backplate, tapered fixture housing, angled socket, removable circular plate/reflector, lamp, and screw-on milk shade. The reflector is modeled as an 8 in physical disc tilted 18 degrees from the host normal; that yields about 7.633 in projected wall-plane height including the modeled 0.08 in thickness, matching the published 7.63 in overall height. The exact tilt, reflector thickness, housing diameters/depth and socket dimensions are photo/drawing-derived inferences and are recorded in `sources_and_inferences.json`.

The shade is modeled as a clipped spherical milk-glass form with exact 3.5 in maximum diameter and 3.25 in axial length. The socket/globe axis is shared with the reflector normal. Geometry is native FreeFormElement solid geometry associated to editable family material parameters.

## Builder

`build_nodes_payload_expanded.py` is the authoritative plain native builder and is the READY command target. It was reconstructed from a SHA-verified transport payload during preparation and then checked directly on the Windows project root. The transport launcher `build_nodes.py` and payload segments are retained only as provenance/error-recovery evidence.

- authoritative source bytes: 30,212
- authoritative source SHA-256: `41e6a0142a6e365305f164e2a0fa7e2a60f8a511c64cc797359e4a595d6882de`
- validation: Windows `C:\Python314\python.exe` `py_compile` and `ast.parse` both pass on this exact file.

The older `build_nodes_payload.py.gz` and `build_nodes_payload.b64.3` are superseded transport attempts and are intentionally not referenced by the launcher. They are retained as error evidence.

## Native command

`D:\Games\pyRevit-Master\bin\pyrevit.exe run "E:\Claude\3D-Model-Workflow\output\lightology_20260923\f07_833919\build_nodes_payload_expanded.py" --revit=2025`

Success is determined from newly timestamped validation JSON and its gates, never from CLI exit code alone.

## Required native gates

For both RFAs the builder saves/reopens the family, checks Lighting Fixtures category and face-based/work-plane placement, loads into a disposable project, hosts the instance on an actual exterior wall face reference, records host identity and mounting-normal relationship, measures the placed envelope, substitutes both Metal Finish and Glass Finish parameters and verifies the alternate material reaches geometry faces, requires zero family/reopen/project warnings, and exports front/side/oblique/material/hosted views. Native source comparison and visual review remain pending until the serialized Revit run.

