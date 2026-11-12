# Codex Native Revit 2025

For current repo release selection and workstation connection status, start with
[the authoritative integration guide](../../docs/NATIVE-REVIT.md) and
[release manifest](../../native-revit.json). Endpoint descriptions below include
historical acceptance-test setup; verify the current runtime before use.

Provider-independent, authenticated local MCP connection to native Revit project and family documents. Source and installer are isolated here; the existing OakPlank RevitMCP and pyRevit installation are preserved. Revit 2025.4 build 25.4.50.35 is the current build target. The package is a development implementation; consult the capability matrix and native evidence before relying on an operation.

## Install and connect

1. Read [the setup guide](../../docs/NATIVE-REVIT-SETUP.md). The selected prebuilt DLL is included in the checkout; verify its hash against `native-revit.json`. Rebuilding is optional: `dotnet build src/NativeRevit/NativeRevit.csproj -c Release` (Windows, .NET 8 SDK or newer, full Revit 2025 installed). A rebuild is not automatically a newly selected release.
2. Run `./install.ps1 -ConfigureCodex` from PowerShell 7. This creates one distinct user add-in manifest, restricts state-folder permissions, installs a release DLL/controller and registers `codex-native-revit-2025` with its local URL and matching token-file path. It backs up its own prior manifest. Existing MCP servers and extensions remain present.
3. Start a new Revit session. Never close an unsaved session for installation. Revit displays its unsigned add-in prompt; the user must choose whether to load this locally built package. The package does not bypass this prompt or modify trust settings.
4. Open a fresh Codex chat or refresh MCP configuration so the new tool catalog is available. `native_revit_capabilities` reports identity/process ID; `documents.list` is submitted as a job with `document:{}`. Select an explicit document session ID from its result.

The first Revit process loading this add-in owns port 49327. Additional instances encountering a port conflict fail to start this listener rather than silently attach to another process. For another isolated instance, launch it with `CODEX_REVIT_PORT` and `CODEX_REVIT_STATE_DIR` set in its process environment and point the controller at that port/token. Environment variables should be set for the launched process, not globally.

At the original delivery, MCP registration targeted the isolated acceptance process on **49328**, with its separate token file. That was evidence against disposable documents, not a connection to the active Belmont model. The generated standard TOML uses 49327. Follow the current [integration guide](../../docs/NATIVE-REVIT.md) to verify the intended process, token-file path, and endpoint before changing configuration; preserve workstation-specific manifest customizations. A new chat/tool refresh may be needed after switching.

## Safe operation workflow

Inspect -> propose -> submit -> query original operation ID -> read native results. Mutation requests require an explicit session ID. Existing documents additionally require `preconditions.allow_existing_document:true`; the service never defaults a mutation to the active model. Include `document.path`, `expected_title` and `is_family` where applicable. Unrecognized preconditions are rejected. IDs must be refreshed after closing, recreating, reopening or loading documents.

Element references use a UniqueId within the explicitly targeted document, or `{document_session_id,id,expected_unique_id}`. Naked numeric IDs are rejected. Coordinates and bounding boxes are internal feet; rotation is radians; sheet coordinates are sheet feet. Parameter writes optionally accept a specific Forge unit ID. Shared/link conversions report direction and transforms; sheet coordinates are separate from model transforms.

Pinned/grouped/owned elements fail guarded mutations. Unpinning is its own explicit operation. Type parameter edits require `allow_type_change:true`; duplicate a type first to avoid changing every instance of a shared type. Deletion requires a rollback preview and the exact native dependency set. No operation implicitly saves, synchronizes, publishes or substitutes mesh objects for native system elements.

Project edits commit one transaction per job, or one transaction for `batch.atomic`. The controller's normal dependency batch has independent receipts and explicit partial completion; it skips dependent steps after prerequisite failure. Family operations own separate transactions. Saved files, reloads and multi-document workflows are external boundaries and cannot be undone by one project transaction.

Timeout/disconnect does not mean rollback. Keep the operation UUID and query it. A process restart changes in-flight durable receipts to `unknown_completion`; no mutation is automatically replayed. Cancellation is honored before execution or before project transaction commit; running family/file calls are not interrupted. Query receipts and actual native state before planning another mutation.

## Tests and evidence

- `tests/test_controller.py`: fake HTTP/protocol/recovery tests; no native Revit evidence.
- `tests/native_family_sequence.py`: explicit-template synthetic Casework family with native extrusion height association, reversible flex, save/reopen/load/placement; resumable receipts.
- `tests/native_workflow.py`: requires isolated Revit process ID and explicit test RFA; project queries, walls/floors, cabinet run, type/parameter edits, transforms, failure rollback, actual viewport/schedule coordinates, layout and unaltered native image exports.
- `tests/native_extended_family.py`: true Width/Depth/Height constraints, geometry flex, basic native forms, formula, material readback and nested-definition load; independent numerical evidence verifier included.
- `tests/native_hosting_recovery.py`: native wall/face hosting, timeout and dropped-response reconciliation without replay.
- `tests/native_compiled_sheets.py`: full-trust compiled API query/modifications and two numerical test-sheet layouts with native plan/elevation/schedule.
- `tests/native_annotations_batch.py`: drafting content, annotations, native dimension, mirror/delete and dependent-step failure fencing.
- `tests/native_stdio_probe.py`: real MCP subprocess -> authenticated native API-context document query.

Run native tests only with a fresh output directory against the isolated process. They never fall back to a production document. Failed steps retain their UUID; repair code or prerequisites and create a new named attempt when warranted. Native reports distinguish technical checks from visual/design acceptance. Synthetic dimensions are test fixtures, not approved manufacturer dimensions or clearances.

## Backup and uninstall

`uninstall.ps1` verifies and removes only this package's manifest. It preserves receipts, release directories, token and manifest backups. Use `codex mcp remove codex-native-revit-2025` to remove the distinct MCP configuration. Never recursively remove the whole Revit add-ins or pyRevit directories. Restoring a prior package manifest affects new Revit sessions only; keep existing receipt evidence for reconciliation.

## Documentation

- `docs/ARCHITECTURE.md`: discovery and architecture decision, upstream sources.
- `docs/TOOL-API.md`: native operation contract and trust boundary.
- `docs/family-api.md`: family lifecycle and authoring reference.
- `docs/CAPABILITY-MATRIX.md`: implementation and native verification status.
- `docs/NATIVE-TEST-REPORT.md`: native results, limits and blockers.
- `controller/README.md`: six MCP tools, CLI and dependency batches.

The native add-in contains no OpenAI credentials or model requests. Any Codex model with access to these MCP tools can use it, including Astra when available to the signed-in client. Standalone Astra API use is conditional on separate API-project model access; this package does not infer that access from ChatGPT sign-in.
