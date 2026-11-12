# Codex Native Revit controller

Start with [the repo integration guide](../../../docs/NATIVE-REVIT.md) for current
release selection, endpoint checks, and workstation status. This controller
reference documents protocol behavior; it does not establish a live connection.

`native_revit.py` is a Python standard-library MCP stdio server and command-line client for the **Codex Native Revit** add-in. It does not call OpenAI, start Revit, select an active production document, save a model, or retry a native operation. Python 3.10 or newer is required. No pip packages are needed.

The controller's fake HTTP tests establish transport, protocol and recovery behavior only. They do not demonstrate that any Revit API operation worked. Consult the package's native test report and capability matrix for native evidence and limitations.

## Start and configure

Use an installed Python interpreter with its absolute path in the MCP configuration. Copy `codex-config.example.toml` into the existing Codex configuration only after updating its two paths. The configuration names this server `codex-native-revit-2025` to distinguish it from the existing OakPlank RevitMCP server. This package does not edit the user's Codex configuration.

```powershell
python .\native_revit.py stdio
python .\native_revit.py capabilities
python .\native_revit.py submit .\example-submit.json
python .\native_revit.py status ORIGINAL_OPERATION_UUID
python .\native_revit.py wait ORIGINAL_OPERATION_UUID --timeout 30
python .\native_revit.py cancel ORIGINAL_OPERATION_UUID
python .\native_revit.py batch .\example-batch.json
```

`stdio` is the default; `stdin` is an alias. MCP stdout contains only newline-delimited JSON-RPC messages. CLI commands return one JSON value on stdout; CLI setup errors go to stderr. Exit codes are 0 for a successful result/accepted job, 2 for failed, partial or unknown completion, and 1 for a controller/setup error.

| Setting | Default | Purpose |
|---|---|---|
| `CODEX_NATIVE_REVIT_URL` | `http://127.0.0.1:49327` | HTTP loopback bridge origin; HTTP proxies are bypassed |
| `CODEX_NATIVE_REVIT_TOKEN_FILE` | `%LOCALAPPDATA%\CodexNativeRevit\token` | UTF-8 bearer token created by the add-in |
| `CODEX_NATIVE_REVIT_TOKEN` | unset | Optional direct token; prefer the token file |
| `CODEX_NATIVE_REVIT_RECEIPT_DIR` | `%LOCALAPPDATA%\CodexNativeRevit\controller-receipts` | Durable client requests, receipts and batch manifests |
| `CODEX_NATIVE_REVIT_HTTP_TIMEOUT` | `10` | Individual HTTP request timeout, seconds; maximum 120 |

`--url`, `--token-file` and `--receipt-dir` override the associated settings and must precede the CLI command. The bridge URL is restricted to an HTTP loopback origin. Credentials are not included in errors or stored in the client receipts. Receipts contain document identities, operation arguments and native results, so protect this directory as project data. Token possession permits invoking the native service; this controller is not an isolation boundary for trusted compiled extensions.

The add-in's `CODEX_REVIT_STATE_DIR` override changes where its token is created; set `CODEX_NATIVE_REVIT_TOKEN_FILE` to that token path when using an overridden state directory. Configure the controller URL to the add-in's actual configured listener port.

## Tools and requests

| MCP tool | Behavior |
|---|---|
| `native_revit_capabilities` | Detached service metadata from `GET /v1/capabilities`; no Revit document query |
| `native_revit_submit` | Persist request, submit once using `POST /v1/jobs`, return receipt immediately |
| `native_revit_job` | Read the original receipt from `GET /v1/jobs/{operation_id}` |
| `native_revit_cancel` | Request safe-boundary cancellation via `POST /v1/jobs/{operation_id}/cancel`; inspect resulting status |
| `native_revit_wait` | Poll the original job up to the requested timeout; maximum 120 seconds |
| `native_revit_batch` | Run an explicit dependency graph; optionally delegate the graph to a named native operation |

`native_revit_submit` requires `operation` and `document`; `arguments`, `preconditions`, and `operation_id` are optional. The HTTP envelope always contains `schema_version: 1`, a generated or caller-supplied UUID, the operation, document, preconditions and arguments. All native queries go through the serialized job queue. A document object normally contains the current `session_id` and optionally an expected path. Use document-qualified element references returned by the native service, and include relevant preconditions. Empty document targeting is reserved for operations whose declared API allows global discovery or document creation. It never implies an active-document mutation.

Operation names, units, argument fields and native support come from the add-in's operation reference and capabilities. Generic submission does not imply that all API operations are implemented or native-tested. The controller exposes no provider selector and no standalone GPT application.

## Recovery and durable operation IDs

Before POST, the controller writes the full request and original operation UUID to an exclusive client record and flushes it to disk. A network failure, unreadable/malformed receipt, uncertain HTTP result or polling timeout returns `unknown_completion` with that UUID and a recovery instruction. A timeout never claims rollback or cancellation.

Query or wait on the **original UUID**. Supplying the same UUID and identical request to `native_revit_submit` queries the existing job instead of sending another POST. Supplying that UUID with different arguments fails with `operation_id_conflict`. Even if the bridge returns 404 after restart, an existing client record is reconciled and never replayed. Examine the bridge's durable record and native state before deciding whether a new operation with a new UUID is appropriate.

Keep and back up the client receipt directory. Deleting client receipts defeats its no-replay protection; the native service has its own durable receipts and may have independent duplicate detection. Unreadable client records fail safely. A process crash during the initial exclusive record write can leave an unreadable record that requires manual investigation.

MCP tool calls include both a text result and identical `structuredContent`. Failed, rolled-back, cancelled, rejected, partial and unknown results set `isError: true`. Queued/running results are accepted work, not evidence of completion. Submit/batch annotations conservatively identify possible destructive mutations regardless of the requested operation.

## Task batches

Every step requires a unique `id`, `operation`, `document` and explicit `depends_on` array. A step may also provide `arguments` and `preconditions`. The graph is validated before execution. Independent branches continue; a failed, cancelled, rejected, rolled-back or unresolved prerequisite blocks its dependents. There is no implicit retry.

Use a result placeholder in arguments, document identity or preconditions to read a **direct dependency** result:

```json
{"$result": "create-cabinet", "path": "created.0.unique_id"}
```

The path is a dot-separated dictionary/list path relative to the dependency receipt's `result`. Copy the actual result shape from native receipts. Predefined model mutations wrap operation data under `result.data`, so their paths commonly begin `data.`; queries and family operations return their declared result directly. Missing fields stop that step. A placeholder can be a whole object to pass a document-qualified element reference; refreshing only a numerical element ID is insufficient when document identity changes.

A client batch gets a UUID and persists its entire graph before running. Each step's operation UUID is deterministically derived from the batch UUID and step ID. Resume by passing the same `batch_id` and unchanged graph: completed or uncertain steps are queried, never recreated. A changed graph requires a new batch UUID. A dependent blocked by an uncertain predecessor can run on resume after the original predecessor is confirmed completed.

Client batches report `atomic: false`: completed earlier steps remain completed when later steps fail. Top-level document/preconditions are rejected for client batches; target and guard each step explicitly. The optional native route supports the declared `native_operation: "batch.atomic"` contract: provide one top-level target document, use that identical document on every step, and combine all guards in top-level preconditions. Per-step preconditions and result placeholders are rejected because that native contract cannot evaluate them. The controller orders prerequisites first and submits one job. The native operation permits predefined mutations in one document and excludes lifecycle, family and compiled operations; its enclosing transaction controls rollback. Native-tested support still comes from the package's evidence report.

Client batch reports include elapsed seconds, HTTP round trips, request bytes and response bytes measured by the controller. These are transport metrics, not native speed or design acceptance claims.

## Controller verification

From the package directory:

```powershell
python -m unittest discover -s tests -p test_controller.py -v
```

Tests use a fake loopback HTTP server, disposable client receipt directories and invented document IDs. They verify authentication, job envelopes, persistent receipts, timeout recovery without replay, mismatch handling, safe cancellation receipt handling, dependency stopping, refreshed result references, changed-batch rejection, MCP protocol errors and stdout framing. Native test results are a separate evidence boundary.
