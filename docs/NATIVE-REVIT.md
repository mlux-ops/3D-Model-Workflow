# Native Revit: authoritative integration guide

Start from [native-revit.json](../native-revit.json), not the newest-looking output
directory. It identifies this repo's selected native integration release. It does
not assert that no newer version exists elsewhere or that Revit is connected.

For a different computer or a fresh checkout, follow
[local installation and verification](NATIVE-REVIT-SETUP.md). Historical drive,
token-file, PID and session examples below belong to their recorded workstation;
they are not settings to copy to another computer.

## Identify and check

Preferred MCP server: `codex-native-revit-2025`. Its six tools are
`native_revit_capabilities`, `native_revit_submit`, `native_revit_job`,
`native_revit_wait`, `native_revit_cancel`, and `native_revit_batch`.
These are provider-independent; an agent needs this server registered in its own
client, or access to the local Python controller. A repo alone cannot grant tools
to another client or machine.

From the repo root, using Python 3.11 or newer for this diagnostic:

```powershell
python tools/revit-doctor.py
```

The diagnostic reads only this integration's Codex configuration, checks the
installed add-in assembly hash, and calls detached capabilities. It prints no
token. Exit 0 means the configured endpoint responded and the installed assembly
matches the manifest; it does not establish document access or feature coverage.
Exit 1 reports an unavailable connection or installation mismatch. Exit 2 reports
a configuration/diagnostic error. An explicit `--config PATH` selects another
Codex config; otherwise it uses `$CODEX_HOME/config.toml` or `~/.codex/config.toml`.
It never installs, launches, restarts, modifies configuration, or queries a model.

Then call the MCP tools in this order:

```text
native_revit_capabilities({})
native_revit_submit({"operation":"documents.list","document":{},"arguments":{}})
native_revit_wait({"operation_id":"<original returned UUID>"})
```

Inspect completed results and select the intended document's fresh `session_id`.
Check the capability `process_id` against the intended Revit process. Use explicit
document identity and relevant preconditions on subsequent jobs. Do not copy
session IDs from old evidence or assume the active model is the correct target.

## CLI and connection setup

For an already configured workstation, use the repo wrapper. It reads the current
Codex config so URL and token file stay paired, including after a repair:

```powershell
python tools/revit.py capabilities
python tools/revit.py submit request.json
python tools/revit.py wait ORIGINAL_OPERATION_UUID --timeout 30
```

The wrapper requires Python 3.11+ and accepts `--config PATH` before the command.
It delegates to the existing controller without changing receipt/replay semantics.
It fails if URL or token-file configuration is missing. Existing chats may retain
old MCP environment settings after configuration changes: use this wrapper now,
or refresh the client's MCP tools/open a fresh chat before using cached tools.

The controller requires Python 3.10+ with no third-party dependencies. For clients
without MCP, the same bridge is available through the manifest's controller path:

```powershell
python output/codex-native-revit-20261013/controller/native_revit.py --url http://127.0.0.1:49327 --token-file "$env:LOCALAPPDATA/CodexNativeRevit/token" capabilities
python output/codex-native-revit-20261013/controller/native_revit.py --url http://127.0.0.1:49327 --token-file "$env:LOCALAPPDATA/CodexNativeRevit/token" submit request.json
python output/codex-native-revit-20261013/controller/native_revit.py --url http://127.0.0.1:49327 --token-file "$env:LOCALAPPDATA/CodexNativeRevit/token" wait ORIGINAL_OPERATION_UUID --timeout 30
```

`request.json` for document discovery is
`{"operation":"documents.list","document":{},"arguments":{}}`.
Use the URL and token-file path verified for the intended process, consistently
across submit/status/wait. Do not print the token itself.

The normal listener is `http://127.0.0.1:49327`; its token file is
`%LOCALAPPDATA%/CodexNativeRevit/token`. Port 49328 and
`%LOCALAPPDATA%/CodexNativeRevit/export-safe-test/token` belong to the historical
isolated acceptance setup. They are not the default production connection.
An intentionally isolated process may use another port/state directory; verify
its identity before selecting it. Do not silently try endpoints for mutations.

For a new installation, follow the [package instructions](../output/codex-native-revit-20261013/README.md)
and [controller configuration example](../output/codex-native-revit-20261013/controller/codex-config.example.toml).
Use real absolute Python/controller paths. Set both URL and token-file path to
the intended process. Configuration belongs to each agent client, outside this
repo; never commit credentials. Installing a DLL does not load it into an already
running Revit process. Preserve existing manifest customizations and do not
blindly rerun the installer to fix a connection: this workstation's manifest
currently uses a ProgramData assembly location rather than the installer's default.
Never close/restart an unsaved Revit session for installation. After a deliberate
configuration change, refresh the client's tools or open a fresh chat and repeat
the checks above.

## Verified repair: November 3, 2026

The current verified connection is `http://127.0.0.1:49327`, with token file
`D:/RevitRecovery/Wieland_20261023_015054/bridge-state/token`. Codex config was
backed up and only this server's URL and token-file path were changed. The
default token-file examples above apply to a standard installation; this session
uses the existing recovery bootstrap's state directory. Prefer the wrapper to
avoid accidentally mixing those configurations.

The initial Revit startup failed while the port was occupied by another Revit
process. The existing pyRevit recovery bootstrap also recorded a port-conflict
failure. Once the port was free, **pyRevit > Reload** reran that existing bootstrap
inside process 28288. No Revit restart, document edit, save, or synchronization
was performed. The selected DLL hash remained unchanged.

Completed verification against process 28288:

- Detached capabilities identified `codex-native-revit-2025`.
- `documents.list`: `88e0614c-6828-4ed6-8bd8-764bab2081f2`.
- Explicitly targeted `context.query`: `78540ed0-d163-4ea6-aa4e-16e3596ccb5e`.
- Target: `Autodesk Docs://25-006 1527 N Wieland St/25-006 1527 N Wieland.rvt`;
  active sheet `TRIPLEX KITCHEN PLAN AND ELEVATIONS`; document has unsaved changes.
- Both query receipts completed with `transaction_status: not_started`. The first
  wait timed out while queued; querying its original UUID confirmed completion.
- [Saved receipts](../output/native-revit-access-repair-20261103/) preserve the
  evidence. Current chat MCP calls still used their old cached endpoint; the
  configured CLI connection works immediately. Refresh tools for MCP access.

For a recurrence, verify process/port/identity first. If the same existing bootstrap
failed at startup due to a port conflict and the port is now free, the verified
recovery action is pyRevit Reload. Do not reload blindly when another process still
owns the port, and do not install another listener or restart an unsaved model.
This repair does not change the bridge's first-process-owns-port behavior.

## Initial audit observations (superseded by the repair above)

- Repo build and installed assembly both hash to the SHA-256 in the manifest:
  release `3f41f299be45`.
- Installed add-in manifest:
  `%APPDATA%/Autodesk/Revit/Addins/2025/CodexNativeRevit2025.addin`.
- Its assembly points to
  `C:/ProgramData/CodexNativeRevit/2025/3f41f299be45/CodexNativeRevit.dll`.
- Codex configuration still targets historical test port 49328 and its test token
  file. The capability call failed with `transport_error`.
- Revit is open as process 28288 with `25-006 1527 N Wieland.rvt`. An earlier
  process check missed it; a subsequent process query confirmed it is running.
  Both the configured 49328 endpoint and a direct authenticated capability check
  on standard port 49327 failed with `transport_error`. Live bridge access is
  unavailable even though Revit is open; the cause has not been established.

These initial observations are retained as history. The repair above subsequently
verified the endpoint and changed configuration; Revit was not restarted.

## Contracts, evidence, and recovery

- [Operation contract](../output/codex-native-revit-20261013/docs/TOOL-API.md)
- [Family API](../output/codex-native-revit-20261013/docs/family-api.md)
- [Capability matrix](../output/codex-native-revit-20261013/docs/CAPABILITY-MATRIX.md)
- [Native test report](../output/codex-native-revit-20261013/docs/NATIVE-TEST-REPORT.md)
- [Controller, batches, and receipts](../output/codex-native-revit-20261013/controller/README.md)

Listed operations are not proof of native verification; consult the evidence.
Coordinates are internal feet, rotations radians, sheet coordinates sheet feet.
Keep original operation IDs and receipt directories. A timeout does not imply
rollback; query the original job before any further mutation. Use document-qualified
element references. Treat save, synchronization, reload, and external file effects
as explicit boundaries and verify their results separately. If the bridge is
unavailable, report the blocker instead of falling back to an arbitrary model.

When promoting a release, update the manifest hash, release and paths; update this
guide; verify the installed manifest/assembly; then verify live capabilities and
document discovery separately. Do not label an installed release as loaded without
runtime evidence.
