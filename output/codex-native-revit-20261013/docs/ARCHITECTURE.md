# Architecture decision — 2026-10-13

Build a separate Revit 2025 C# add-in with an ExternalEvent dispatcher and a provider-independent Python stdio MCP controller. Keep OakPlank RevitMCP and pyRevit intact. Initial discovery was read-only. No AGENTS.md was found at the workspace or inspected ancestors; WORKFLOW.md was read. Existing workspace content is untracked; work stays in this isolated output folder.

Observed: Revit 2025.4 build 25.4.50.35, process 33580, active Belmont production project; pyRevit 6.4.0.26100+0515 under the roaming pyRevit-Master folder. Its pyrevitlib/pyrevit/agent folder is absent. Existing Revit listeners are 0.0.0.0:48884 and 127.0.0.1:8088; the new identity is `codex-native-revit-2025`, default 127.0.0.1:49327. Historical ports/IDs are not reused as document targets.

Current upstream documentation describes an experimental/off-by-default agent runtime, with lifecycle restrictions and an evolving CLI/MCP implementation. This installed version cannot provide it. Upgrading the user's working pyRevit is unnecessary and outside the isolation boundary. C# owns background family document lifecycles; Python is an external controller, not an in-process Python sandbox.

Network workers only validate JSON, authenticate, persist receipts and enqueue detached requests. Every Revit API read and write runs inside the single ExternalEvent handler. Document session IDs are freshly assigned per process/document object; caller must target them explicitly. An optional expected path prevents targeting another file; ID/UniqueId checks occur immediately before execution. Undo transactions are named by operation ID. Lifecycle/file actions are separate and never advertised as transaction-atomic across documents or files.

Durable receipts transition queued -> running -> terminal. On restart queued/running receipts become unknown_completion and are never replayed automatically. A repeated operation UUID retrieves the original receipt only if the envelope matches. Queued cancellation has no model effects; running cancellation is checked at safe operation boundaries. Timeout is a controller observation, not a rollback claim.

Compiled operation extension loading is disabled by default and restricted to an explicit local plugin directory when enabled. Trusted in-process code has full process privileges; query declarations are not a secure sandbox. Saving, synchronization, publication and family overwrite must remain explicit operations.

Native verification will use new disposable project/family documents in a separate Revit process when possible. Production documents are not test targets. Synthetic test cabinet dimensions are test data, not manufacturer dimensions or design clearances.

Sources consulted:

- https://help.autodesk.com/cloudhelp/2025/ENU/Revit-API/files/Revit_API_Developers_Guide/Advanced_Topics/Revit_API_Revit_API_Developers_Guide_Advanced_Topics_External_Events_html.html
- https://docs.pyrevitlabs.io/agent-runtime/
- https://developers.openai.com/codex/mcp
- https://learn.chatgpt.com/docs/enterprise/workspace-model-availability

Astra is available in this Codex host's advertised model catalog. That does not establish API-project access. The optional standalone API application is conditional on a verified API credential/model; no key is requested by the native add-in and no model-provider call is needed for Codex MCP use.
