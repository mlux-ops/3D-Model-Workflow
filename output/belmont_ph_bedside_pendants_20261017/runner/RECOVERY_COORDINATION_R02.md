# Native recovery coordination, 2026-10-17

No Revit launch, process attachment or termination has been performed by this follow-up worker. Do not repeat the original crashing command without new recovery evidence.

The visible Revit PID 11796 started at 01:54:13 local, has an empty main-window title, and its parent is explorer.exe PID 7860. It was not created by this worker. Native document state is unknown. Do not stop or attach to it. The latest application journal observed at 02:13 was zero bytes; this does not certify a running or empty Revit API session.

Read-only process tree receipt: `E:\Claude\3D-Model-Workflow\output\belmont_ph_bedside_pendants_20261017\runner\receipts\process_ownership_r02.json`. EnumWindows returned false with last-error 0 in this restricted execution context; no UI/window state can be inferred. CIM is already known to deny access and was not retried.

Prepared native validation script: `E:\Claude\3D-Model-Workflow\output\belmont_ph_bedside_pendants_20261017\qa\native_readonly_oem_r02.py`.

Prepared isolated launcher: `E:\Claude\3D-Model-Workflow\output\belmont_ph_bedside_pendants_20261017\runner\launch_readonly_r02.py`.

Fresh preflight receipt: `E:\Claude\3D-Model-Workflow\output\belmont_ph_bedside_pendants_20261017\runner\receipts\readonly_preflight_r02_preflight.json`.

The launcher defaults to preflight only. Its explicit launch path requires a task-local recovery-evidence file, no unresolved visible Revit processes, a unique run ID, and exclusive task reservation. It injects a unique ownership handshake inherited only by the spawned child and redirects temporary runner files into the task directory. It does not terminate any process if startup stalls. A receipt is required regardless of CLI exit code.

Native script guards require Revit 2025, no active document, zero initial documents, and the isolated ownership marker. It hashes all four OEM inputs before opening them, opens the originals without Save/SaveAs, inventories actual types/materials/native LightFamily sources, and tests a representative/exact symbol in a new unsaved project. It creates a real Ceiling, not a floor or unhosted point proxy. Every source and disposable document closes without saving; original hashes are checked again. Geometry bounds come only from placed positive-volume solids; standalone meshes, body/canopy segmentation, exact source dimensions and optical fidelity remain separate gates. The first bounded native probe does not export visual views or auto-approve a variant.

Supported factory geometry path for the missing Stucco wrapper: local Revit 2025 XML documents `Document.Import(String, ImportOptions3DM, View)` and STEP import. Both require the installed optional importer and a healthy native process. The official No.2 `.3dm` and `.stp` are now preserved. A different importer is not a fix for a process that fails before its API script; no alternate startup is claimed to work. No standalone headless console executable was found in the installed Revit directory.

Schneid manufacturer dimensions corrected directly from its PDF: body D105 × H265 mm; No.2 rose D140 × H140 mm. Do not use the earlier No.1 rose dimensions. Source review: `E:\Claude\3D-Model-Workflow\output\belmont_ph_bedside_pendants_20261017\qa\SCHNEID_OEM_CAD_REVIEW_R02.json`.

Recovery worker: preserve any changed startup method, owned process identity, current crash/root-cause evidence and successful document-free probe in this task directory before a new native run. An empty or arbitrary text file is not evidence of recovery; the launch operator must inspect it. A full package release is still blocked by the exact Jarvis/Malabar/Marset variant holds, independently of runtime recovery.
