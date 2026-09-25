# READY_REVIT — F07 Nodes KW1041

Preparation complete. Native execution is intentionally not launched from this worker because prime centralized the serialized Revit batch.

Authoritative plain builder:
E:\Claude\3D-Model-Workflow\output\lightology_20260923\f07_833919\build_nodes_payload_expanded.py

Static verification:
- C:\Python314\python.exe -m py_compile — PASS
- ast.parse — PASS
- bytes: 30,212
- SHA-256: 41e6a0142a6e365305f164e2a0fa7e2a60f8a511c64cc797359e4a595d6882de

Exact serialized native command:
D:\Games\pyRevit-Master\bin\pyrevit.exe run "E:\Claude\3D-Model-Workflow\output\lightology_20260923\f07_833919\build_nodes_payload_expanded.py" --revit=2025

Expected separate final RFAs:
- Visual_Comfort_Nodes_KW1041BBS_Burnished_Brass_R2025.rfa
- Visual_Comfort_Nodes_KW1041MBK_Midnight_Black_R2025.rfa

Implemented native gates:
- Revit 2025 and face-based template preflight.
- Lighting Fixtures category.
- Separate save/reopen for each finish RFA.
- Load into disposable project and place on an actual exterior wall-face Reference.
- Verify instance Host and HostFace.
- Measure published/inferred geometry and placed envelope.
- Substitute both Metal Finish and Glass Finish and confirm substitute material IDs reach geometry faces.
- Require zero warnings in family, reopen, and disposable project.
- Export front, side, oblique, material, and hosted views.
- Write timestamped JSON validation; CLI exit code alone is not accepted.

Source evidence and inference notes are in sources\, sources_and_inferences.json, README.md, manifest.txt, and ERROR_LOG.md.

Routing note:
The agents API could not deliver the READY message to prime because this continuation is not attached to the original active sub-agent family. This file is the durable handoff in the shared workspace.

