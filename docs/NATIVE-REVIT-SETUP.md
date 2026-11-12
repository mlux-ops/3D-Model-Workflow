# Native Revit on another computer

These instructions are relative to the checkout root and require no mapped drive.
Read AGENTS.md, NATIVE-REVIT.md and WORKFLOW.md before model work. The selected
release is defined by native-revit.json, not by a dated folder name.

## Install locally

Requirements: Windows, Revit 2025, Python 3.11+ with the `py` launcher, PowerShell 7
(`pwsh`), and Codex CLI on PATH for automatic MCP registration. The add-in runs
inside Revit on this same computer; this is not a remote cross-computer bridge.

1. Pull the branch containing these files into your local checkout. Verify these
   paths exist: AGENTS.md, WORKFLOW.md, native-revit.json, docs/NATIVE-REVIT.md,
   tools/revit-doctor.py and tools/revit.py.
2. Check the bundled DLL hash from the checkout root:

   ```powershell
   $selected = Get-Content native-revit.json -Raw | ConvertFrom-Json
   $dll = Join-Path $selected.package_root 'src/NativeRevit/bin/Release/net8.0-windows/CodexNativeRevit.dll'
   if ((Get-FileHash -LiteralPath $dll -Algorithm SHA256).Hash.ToLowerInvariant() -ne $selected.assembly_sha256) {
       throw 'Bundled DLL does not match the selected release'
   }
   ```

3. Inspect existing local native-bridge settings before replacing an established
   installation. In PowerShell 7, from the checkout root:

   ```powershell
   ./output/codex-native-revit-20261013/install.ps1 -ConfigureCodex
   ```

   The installer uses the bundled DLL, installs a local controller, creates a
   local authentication token and registers both the local URL and token-file
   path. Do not transfer tokens or another computer's Codex configuration.

4. The add-in loads in a new Revit session. Never close/restart an unsaved session
   or discard model changes to install it. If Revit is already open without the
   add-in loaded, prepare installation and wait until the user has safely saved
   their work before arranging a new session. Do not bypass the unsigned add-in
   trust prompt.
5. Refresh the agent's MCP configuration or start a fresh chat after registration.

## Verify before accessing a model

```powershell
python tools/revit-doctor.py
python tools/revit.py capabilities
```

The doctor is read-only. Verify the live process ID rather than inferring access
from installation. Use native_revit_submit to submit documents.list with
document:{} and arguments:{}, then read the original operation's completed
receipt. Alternatively, submit the following JSON using tools/revit.py:

```json
{"operation":"documents.list","document":{},"arguments":{}}
```

Select the intended model by its exact title/path and fresh session ID. Retain
operation IDs and reconcile timeouts before another mutation. Follow the native
operation contract, model editability rules and separate visual acceptance checks.
Saving and synchronizing remain explicit task-authorized operations.

## Workstation-specific history

The source workstation's recovery drive, endpoint overrides, process IDs and
document session IDs in historical evidence are not destination configuration.
Use this computer's local installation and fresh live discovery. Pulling the
repository supplies files, not a running Revit add-in, a model, credentials or
verified connectivity. Destination installation and native operation must be
verified there.
