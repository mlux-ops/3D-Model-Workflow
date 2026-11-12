"""Native Revit local controller. Python standard library only; no provider requests."""
from __future__ import annotations

import argparse
import copy
import ipaddress
import json
import os
from pathlib import Path
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid

TERMINAL = frozenset({"completed", "failed", "rolled_back", "cancelled", "rejected"})
SUCCESS = frozenset({"completed"})
PROTOCOLS = ("2024-11-05", "2025-03-26", "2025-06-18")


class ControllerError(Exception):
    def __init__(self, code, message, details=None):
        super().__init__(message)
        self.code, self.message, self.details = code, message, details or {}

    def as_dict(self):
        return {"code": self.code, "message": self.message, "details": self.details}


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def reject_constant(value):
    raise ValueError("Non-finite JSON number")


def operation_id(value=None):
    try:
        return str(uuid.UUID(value)) if value else str(uuid.uuid4())
    except (ValueError, TypeError, AttributeError):
        raise ControllerError("invalid_argument", "operation_id must be a UUID")


class Client:
    def __init__(self, base_url=None, token=None, token_file=None, receipt_dir=None, timeout=None):
        self.base_url = (base_url or os.environ.get("CODEX_NATIVE_REVIT_URL", "http://127.0.0.1:49327")).rstrip("/")
        parsed = urllib.parse.urlsplit(self.base_url)
        try:
            loopback = parsed.hostname == "localhost" or ipaddress.ip_address(parsed.hostname or "").is_loopback
        except ValueError:
            loopback = False
        if parsed.scheme != "http" or not loopback or parsed.username or parsed.password or parsed.query or parsed.fragment or parsed.path:
            raise ControllerError("invalid_configuration", "Bridge URL must be an HTTP loopback origin")
        local = Path(os.environ.get("LOCALAPPDATA", str(Path.home() / ".local"))) / "CodexNativeRevit"
        self.token = token or os.environ.get("CODEX_NATIVE_REVIT_TOKEN")
        self.token_file = Path(token_file or os.environ.get("CODEX_NATIVE_REVIT_TOKEN_FILE", str(local / "token")))
        self.receipt_dir = Path(receipt_dir or os.environ.get("CODEX_NATIVE_REVIT_RECEIPT_DIR", str(local / "controller-receipts")))
        try:
            self.timeout = float(timeout if timeout is not None else os.environ.get("CODEX_NATIVE_REVIT_HTTP_TIMEOUT", "10"))
        except (ValueError, TypeError):
            raise ControllerError("invalid_configuration", "HTTP timeout must be a positive number")
        if not 0 < self.timeout <= 120:
            raise ControllerError("invalid_configuration", "HTTP timeout must be within (0, 120] seconds")
        self.metrics = {"http_round_trips": 0, "request_bytes": 0, "response_bytes": 0}
        # Ignore environment HTTP proxies for the authenticated loopback transport.
        self.opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))

    def _auth(self):
        token = self.token
        if token is None:
            try:
                token = self.token_file.read_text(encoding="utf-8-sig").strip()
            except OSError:
                raise ControllerError("authentication_unavailable", "Cannot read bridge bearer-token file", {"token_file": str(self.token_file)})
        if not token or "\n" in token or "\r" in token:
            raise ControllerError("authentication_unavailable", "Bearer token is missing or invalid")
        return token

    def _request(self, method, path, payload=None, timeout=None):
        data = canonical(payload).encode("utf-8") if payload is not None else None
        request = urllib.request.Request(self.base_url + path, data=data, method=method,
            headers={"Authorization": "Bearer " + self._auth(), "Content-Type": "application/json", "Accept": "application/json"})
        self.metrics["http_round_trips"] += 1
        self.metrics["request_bytes"] += len(data or b"")
        try:
            with self.opener.open(request, timeout=timeout if timeout is not None else self.timeout) as response:
                raw = response.read(32 * 1024 * 1024 + 1)
        except urllib.error.HTTPError as exc:
            # Do not include response text: unexpected servers can reflect credentials.
            code = exc.code
            exc.close()
            raise ControllerError("http_error", "Bridge returned HTTP " + str(code), {"http_status": code})
        except (OSError, urllib.error.URLError) as exc:
            raise ControllerError("transport_error", "Bridge request did not produce a receipt", {"exception_type": type(exc).__name__})
        self.metrics["response_bytes"] += len(raw)
        if len(raw) > 32 * 1024 * 1024:
            raise ControllerError("invalid_response", "Bridge response exceeded 32 MiB")
        try:
            value = json.loads(raw, parse_constant=reject_constant)
        except (ValueError, UnicodeDecodeError):
            raise ControllerError("invalid_response", "Bridge returned invalid JSON")
        if not isinstance(value, dict):
            raise ControllerError("invalid_response", "Bridge response must be an object")
        return value

    def _path(self, oid):
        return self.receipt_dir / (operation_id(oid) + ".json")

    def _read_record(self, oid):
        path = self._path(oid)
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            return None
        except (OSError, ValueError):
            raise ControllerError("receipt_unreadable", "Cannot safely reconcile local operation record", {"operation_id": oid})

    def _write_record(self, oid, record):
        self.receipt_dir.mkdir(parents=True, exist_ok=True)
        temporary = self.receipt_dir / (oid + "." + uuid.uuid4().hex + ".tmp")
        try:
            with temporary.open("x", encoding="utf-8", newline="\n") as stream:
                stream.write(canonical(record) + "\n")
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, self._path(oid))
        finally:
            if temporary.exists():
                temporary.unlink()

    def _receipt(self, oid, value):
        if value.get("schema_version") != 1 or value.get("operation_id") != oid or value.get("status") not in TERMINAL | {"queued", "running", "unknown_completion"}:
            raise ControllerError("invalid_response", "Receipt has an unsupported schema, mismatched operation_id or unknown status", {"operation_id": oid})
        return value

    def capabilities(self):
        result = self._request("GET", "/v1/capabilities")
        if result.get("schema_version") != 1:
            raise ControllerError("invalid_response", "Unsupported capability schema")
        return result

    def job(self, oid, timeout=None):
        if not oid:
            raise ControllerError("invalid_argument", "operation_id is required")
        oid = operation_id(oid)
        result = self._receipt(oid, self._request("GET", "/v1/jobs/" + oid, timeout=timeout))
        try:
            record = self._read_record(oid)
            if record:
                record["receipt"] = result
                self._write_record(oid, record)
        except (OSError, ControllerError):
            result = {**result, "controller_warnings": [{"code": "receipt_cache_update_failed", "operation_id": oid,
                "message": "Native receipt was read; local cache could not be updated. Preserve this operation ID."}]}
        return result

    def cancel(self, oid):
        if not oid:
            raise ControllerError("invalid_argument", "operation_id is required")
        oid = operation_id(oid)
        try:
            return self._receipt(oid, self._request("POST", "/v1/jobs/" + oid + "/cancel", {}))
        except ControllerError as exc:
            if exc.code in {"transport_error", "invalid_response"} or exc.details.get("http_status", 0) >= 500:
                return self._unknown(oid, exc, action="cancel")
            raise

    @staticmethod
    def _unknown(oid, error=None, last=None, action="submit"):
        result = {"schema_version": 1, "operation_id": oid, "status": "unknown_completion",
            "recovery": {"action": "query_original_operation_id", "operation_id": oid, "resubmit_allowed": False},
            "pending_action": action}
        if error:
            result["error"] = error.as_dict()
        if last:
            result["last_known_status"] = last.get("status")
            result["last_receipt"] = last
        return result

    def submit(self, operation, document, arguments=None, preconditions=None, operation_id_value=None):
        if not isinstance(operation, str) or not operation.strip():
            raise ControllerError("invalid_argument", "operation must be a nonempty string")
        for name, value in (("document", document), ("arguments", arguments), ("preconditions", preconditions)):
            if not isinstance(value, dict) and not (name != "document" and value is None):
                raise ControllerError("invalid_argument", name + " must be an object")
        oid = operation_id(operation_id_value)
        envelope = {"schema_version": 1, "operation_id": oid, "operation": operation,
            "document": document, "preconditions": preconditions or {}, "arguments": arguments or {}}
        canonical(envelope)  # Validate serialization before journaling.
        previous = self._read_record(oid)
        if previous:
            if canonical(previous.get("request")) != canonical(envelope):
                raise ControllerError("operation_id_conflict", "Operation UUID is already bound to a different request", {"operation_id": oid})
            try:
                return self.job(oid)
            except ControllerError as exc:
                return self._unknown(oid, exc, previous.get("receipt"), action="reconcile")
        # Authenticate before reserving a UUID, so missing credentials do not imply submission.
        self._auth()
        record = {"request": envelope, "receipt": self._unknown(oid, action="submission_started")}
        # Exclusive initial creation also prevents concurrent controllers from posting the same UUID.
        self.receipt_dir.mkdir(parents=True, exist_ok=True)
        try:
            with self._path(oid).open("x", encoding="utf-8") as stream:
                stream.write(canonical(record) + "\n")
                stream.flush()
                os.fsync(stream.fileno())
        except FileExistsError:
            return self.submit(operation, document, arguments, preconditions, oid)
        try:
            receipt = self._receipt(oid, self._request("POST", "/v1/jobs", envelope))
        except ControllerError as exc:
            if exc.code == "http_error" and 400 <= exc.details.get("http_status", 0) < 500 and exc.details["http_status"] not in {408, 409, 429}:
                receipt = {"schema_version": 1, "operation_id": oid, "status": "rejected", "error": exc.as_dict()}
            else:
                receipt = self._unknown(oid, exc)
        record["receipt"] = receipt
        try:
            self._write_record(oid, record)
        except OSError:
            receipt = {**receipt, "controller_warnings": [{"code": "receipt_cache_update_failed", "operation_id": oid,
                "message": "Native receipt was received; local cache could not be updated. Preserve this operation ID."}]}
        return receipt

    def wait(self, oid, timeout_seconds=30, poll_interval=0.25):
        if not oid:
            raise ControllerError("invalid_argument", "operation_id is required")
        oid = operation_id(oid)
        if not isinstance(timeout_seconds, (int, float)) or not 0 <= timeout_seconds <= 120:
            raise ControllerError("invalid_argument", "timeout_seconds must be between 0 and 120")
        if not isinstance(poll_interval, (int, float)) or not 0.01 <= poll_interval <= 10:
            raise ControllerError("invalid_argument", "poll_interval must be between 0.01 and 10")
        deadline = time.monotonic() + timeout_seconds
        last = None
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return self._unknown(oid, last=last, action="wait")
            try:
                last = self.job(oid, timeout=min(self.timeout, remaining))
            except ControllerError as exc:
                if exc.code == "http_error" and exc.details.get("http_status") in {401, 403}:
                    raise
                return self._unknown(oid, exc, last, action="wait")
            if last["status"] in TERMINAL:
                return last
            time.sleep(min(poll_interval, max(0, deadline - time.monotonic())))

    def batch(self, steps, batch_id=None, timeout_seconds=30, native_operation=None, document=None, preconditions=None):
        """Resume deterministically; independent steps proceed, failed prerequisites block dependents."""
        batch_id = operation_id(batch_id)
        ordered = validate_graph(steps)
        if not isinstance(timeout_seconds, (int, float)) or not 0 <= timeout_seconds <= 120:
            raise ControllerError("invalid_argument", "timeout_seconds must be between 0 and 120")
        if native_operation:
            if native_operation != "batch.atomic":
                raise ControllerError("invalid_argument", "Only the declared batch.atomic native batch contract is supported")
            if not isinstance(document, dict) or not document:
                raise ControllerError("invalid_argument", "Native atomic batch requires an explicit target document")
            for step in ordered:
                if canonical(step["document"]) != canonical(document) or step.get("preconditions"):
                    raise ControllerError("invalid_argument", "Native atomic batch requires one document and combined top-level preconditions")
                if contains_placeholder(step.get("arguments", {})):
                    raise ControllerError("invalid_argument", "Native atomic batch cannot resolve result placeholders; use a client batch")
            # The implemented native contract executes predefined mutations in one document.
            # Order prerequisites first; an exception rolls back the enclosing transaction.
            return self.submit(native_operation, document, {"steps": ordered, "batch_id": batch_id}, preconditions, batch_id)
        if document is not None or preconditions is not None:
            raise ControllerError("invalid_argument", "Client batches require document and preconditions on each step")
        # Bind the entire graph before any step runs. A changed graph needs a new batch UUID.
        manifest_text = canonical({"schema_version": 1, "batch_id": batch_id, "steps": steps})
        self.receipt_dir.mkdir(parents=True, exist_ok=True)
        manifest_path = self.receipt_dir / ("batch-" + batch_id + ".json")
        try:
            with manifest_path.open("x", encoding="utf-8") as stream:
                stream.write(manifest_text + "\n")
                stream.flush()
                os.fsync(stream.fileno())
        except FileExistsError:
            try:
                same = canonical(json.loads(manifest_path.read_text(encoding="utf-8"))) == manifest_text
            except (OSError, ValueError):
                raise ControllerError("receipt_unreadable", "Cannot safely reconcile batch manifest", {"batch_id": batch_id})
            if not same:
                raise ControllerError("batch_id_conflict", "Batch UUID is already bound to a different graph", {"batch_id": batch_id})
        started, before = time.monotonic(), dict(self.metrics)
        results = {}
        for step in ordered:
            sid = step["id"]
            dependencies = [results[dep] for dep in step["depends_on"]]
            if any(value["status"] not in SUCCESS for value in dependencies):
                results[sid] = {"status": "blocked", "reason": "prerequisite_not_completed", "depends_on": step["depends_on"]}
                continue
            oid = str(uuid.uuid5(uuid.UUID(batch_id), sid))
            try:
                arguments = resolve_placeholders(step.get("arguments", {}), results, set(step["depends_on"]))
                doc = resolve_placeholders(step["document"], results, set(step["depends_on"]))
                guards = resolve_placeholders(step.get("preconditions", {}), results, set(step["depends_on"]))
                receipt = self.submit(step["operation"], doc, arguments, guards, oid)
                if receipt["status"] in {"queued", "running", "unknown_completion"}:
                    receipt = self.wait(oid, timeout_seconds)
                results[sid] = receipt
            except ControllerError as exc:
                results[sid] = {"operation_id": oid, "status": "failed", "error": exc.as_dict()}
        statuses = [value["status"] for value in results.values()]
        status = "completed" if all(value in SUCCESS for value in statuses) else (
            "unknown_completion" if "unknown_completion" in statuses else "partial_completion" if "completed" in statuses else "failed")
        return {"schema_version": 1, "batch_id": batch_id, "status": status, "atomic": False,
            "steps": results, "metrics": {**{key: self.metrics[key] - before[key] for key in before}, "elapsed_seconds": time.monotonic() - started}}


def validate_graph(steps):
    if not isinstance(steps, list) or not steps or len(steps) > 1000:
        raise ControllerError("invalid_argument", "steps must contain between 1 and 1000 steps")
    by_id = {}
    for step in steps:
        if not isinstance(step, dict) or not isinstance(step.get("id"), str) or not step["id"] or step["id"] in by_id:
            raise ControllerError("invalid_graph", "Each step requires a unique nonempty string id")
        if not isinstance(step.get("depends_on"), list) or any(not isinstance(dep, str) for dep in step["depends_on"]):
            raise ControllerError("invalid_graph", "Every step requires explicit depends_on")
        if not isinstance(step.get("operation"), str) or not step["operation"] or not isinstance(step.get("document"), dict):
            raise ControllerError("invalid_graph", "Each step requires operation and document")
        if any(not isinstance(step.get(key, {}), dict) for key in ("arguments", "preconditions")):
            raise ControllerError("invalid_graph", "Step arguments and preconditions must be objects")
        if set(step) - {"id", "operation", "document", "depends_on", "arguments", "preconditions"}:
            raise ControllerError("invalid_graph", "Unexpected step fields")
        by_id[step["id"]] = step
    if any(dep not in by_id for step in steps for dep in step["depends_on"]):
        raise ControllerError("invalid_graph", "Dependency refers to a missing step")
    result, done = [], set()
    while len(result) < len(steps):
        ready = [step for step in steps if step["id"] not in done and set(step["depends_on"]) <= done]
        if not ready:
            raise ControllerError("invalid_graph", "Dependency graph contains a cycle")
        result.extend(ready)
        done.update(step["id"] for step in ready)
    return result


def resolve_placeholders(value, results, dependencies):
    if isinstance(value, dict):
        if "$result" in value:
            if set(value) - {"$result", "path"} or not isinstance(value["$result"], str) or value["$result"] not in dependencies:
                raise ControllerError("invalid_placeholder", "Result references must name an explicit direct dependency")
            current = results[value["$result"]].get("result")
            path = value.get("path", "")
            if not isinstance(path, str):
                raise ControllerError("invalid_placeholder", "Result path must be a string")
            try:
                for part in path.split(".") if path else []:
                    current = current[int(part)] if isinstance(current, list) else current[part]
            except (KeyError, IndexError, ValueError, TypeError):
                raise ControllerError("invalid_placeholder", "Result path does not exist", {"step": value["$result"], "path": path})
            return copy.deepcopy(current)
        return {key: resolve_placeholders(item, results, dependencies) for key, item in value.items()}
    if isinstance(value, list):
        return [resolve_placeholders(item, results, dependencies) for item in value]
    return value


def contains_placeholder(value):
    if isinstance(value, dict):
        return "$result" in value or any(contains_placeholder(item) for item in value.values())
    return isinstance(value, list) and any(contains_placeholder(item) for item in value)


def tool(name, description, properties, required=(), readonly=False, destructive=False, idempotent=False, openworld=False):
    return {"name": name, "description": description,
        "inputSchema": {"type": "object", "properties": properties, "required": list(required), "additionalProperties": False},
        "annotations": {"readOnlyHint": readonly, "destructiveHint": destructive, "idempotentHint": idempotent, "openWorldHint": openworld}}


OID = {"type": "string", "format": "uuid"}
OBJECT = {"type": "object"}
TOOLS = [
    tool("native_revit_capabilities", "Discover detached bridge capabilities. Native document queries must be submitted as jobs.", {}, readonly=True, idempotent=True),
    tool("native_revit_submit", "Submit one explicitly targeted Revit job. Retain operation_id; reconcile any unknown completion before considering a new mutation.",
         {"operation": {"type": "string"}, "document": OBJECT, "arguments": OBJECT, "preconditions": OBJECT, "operation_id": OID}, ("operation", "document"), destructive=True, openworld=True),
    tool("native_revit_job", "Read a persistent operation receipt without resubmitting the operation.", {"operation_id": OID}, ("operation_id",), readonly=True, idempotent=True),
    tool("native_revit_cancel", "Request cancellation at a safe boundary. Read the eventual receipt to determine whether changes completed.", {"operation_id": OID}, ("operation_id",), idempotent=True),
    tool("native_revit_wait", "Poll the original operation. A timeout returns unknown_completion and never implies rollback.",
         {"operation_id": OID, "timeout_seconds": {"type": "number", "minimum": 0, "maximum": 120}, "poll_interval": {"type": "number", "minimum": 0.01, "maximum": 10}}, ("operation_id",), readonly=True, idempotent=True),
    tool("native_revit_batch", "Execute a dependency graph with deterministic receipts; block failed dependents, report partial completion. Client batches are not atomic. A named native operation can implement its declared transaction boundary.",
         {"steps": {"type": "array", "minItems": 1, "maxItems": 1000, "items": {"type": "object"}}, "batch_id": OID,
          "timeout_seconds": {"type": "number", "minimum": 0, "maximum": 120}, "native_operation": {"type": "string"}, "document": OBJECT, "preconditions": OBJECT}, ("steps",), destructive=True, openworld=True),
]


class MCPServer:
    def __init__(self, client):
        self.client = client

    def dispatch(self, request):
        if not isinstance(request, dict) or request.get("jsonrpc") != "2.0" or not isinstance(request.get("method"), str):
            return {"jsonrpc": "2.0", "id": request.get("id") if isinstance(request, dict) else None, "error": {"code": -32600, "message": "Invalid Request"}}
        if "id" not in request:
            return None  # MCP notifications never receive a response.
        rid = request["id"]
        params = request.get("params", {})
        if not isinstance(params, dict):
            return {"jsonrpc": "2.0", "id": rid, "error": {"code": -32602, "message": "params must be an object"}}
        method = request["method"]
        if method == "initialize":
            wanted = params.get("protocolVersion")
            result = {"protocolVersion": wanted if wanted in PROTOCOLS else PROTOCOLS[-1], "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": "codex-native-revit", "version": "1.0.0"},
                "instructions": "Use explicit document session identities and preconditions. Keep operation IDs; unknown completion requires reconciliation. Native saves and synchronization are explicit operations."}
        elif method == "ping":
            result = {}
        elif method == "tools/list":
            result = {"tools": TOOLS}
        elif method == "tools/call":
            try:
                data = self.call(params.get("name"), params.get("arguments", {}))
                result = {"content": [{"type": "text", "text": canonical(data)}], "structuredContent": data,
                    "isError": data.get("status") in {"failed", "rolled_back", "cancelled", "rejected", "unknown_completion", "partial_completion"}}
            except ControllerError as exc:
                data = {"error": exc.as_dict()}
                result = {"content": [{"type": "text", "text": canonical(data)}], "structuredContent": data, "isError": True}
            except Exception as exc:
                # Preserve stdout protocol and avoid credential-bearing exception text.
                data = {"error": {"code": "controller_error", "message": "Controller could not complete the tool call", "details": {"exception_type": type(exc).__name__}}}
                result = {"content": [{"type": "text", "text": canonical(data)}], "structuredContent": data, "isError": True}
        else:
            return {"jsonrpc": "2.0", "id": rid, "error": {"code": -32601, "message": "Method not found"}}
        return {"jsonrpc": "2.0", "id": rid, "result": result}

    def call(self, name, arguments):
        definition = next((item for item in TOOLS if item["name"] == name), None)
        if not definition:
            raise ControllerError("unknown_tool", "Unknown tool name")
        if not isinstance(arguments, dict):
            raise ControllerError("invalid_argument", "Tool arguments must be an object")
        schema = definition["inputSchema"]
        if set(arguments) - set(schema["properties"]) or any(key not in arguments for key in schema["required"]):
            raise ControllerError("invalid_argument", "Missing or unexpected tool arguments")
        args = dict(arguments)
        if name == "native_revit_capabilities":
            return self.client.capabilities()
        if name == "native_revit_submit":
            args["operation_id_value"] = args.pop("operation_id", None)
            return self.client.submit(**args)
        if name == "native_revit_job":
            return self.client.job(args["operation_id"])
        if name == "native_revit_cancel":
            return self.client.cancel(args["operation_id"])
        if name == "native_revit_wait":
            args["oid"] = args.pop("operation_id")
            return self.client.wait(**args)
        return self.client.batch(**args)

    def serve(self, input_stream=sys.stdin, output_stream=sys.stdout):
        for line in input_stream:
            try:
                request = json.loads(line, parse_constant=reject_constant)
            except ValueError:
                response = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "Parse error"}}
            else:
                response = self.dispatch(request)
            if response is not None:
                output_stream.write(canonical(response) + "\n")
                output_stream.flush()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url")
    parser.add_argument("--token-file")
    parser.add_argument("--receipt-dir")
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("stdio", aliases=["stdin"], help="Run MCP newline-delimited JSON-RPC on stdin/stdout (default)")
    sub.add_parser("capabilities")
    submit_parser = sub.add_parser("submit")
    submit_parser.add_argument("request_file", help="JSON containing operation, document, arguments, preconditions and optional operation_id")
    for name in ("status", "cancel", "wait"):
        item = sub.add_parser(name)
        item.add_argument("operation_id")
        if name == "wait":
            item.add_argument("--timeout", type=float, default=30)
    batch_parser = sub.add_parser("batch")
    batch_parser.add_argument("request_file", help="JSON containing steps, optional batch_id and timeout_seconds")
    options = parser.parse_args(argv)
    try:
        client = Client(base_url=options.url, token_file=options.token_file, receipt_dir=options.receipt_dir)
        if options.command in {None, "stdio", "stdin"}:
            if hasattr(sys.stdin, "reconfigure"):
                sys.stdin.reconfigure(encoding="utf-8")
            if hasattr(sys.stdout, "reconfigure"):
                sys.stdout.reconfigure(encoding="utf-8")
            MCPServer(client).serve()
            return 0
        if options.command == "capabilities":
            result = client.capabilities()
        elif options.command == "submit":
            args = json.loads(Path(options.request_file).read_text(encoding="utf-8-sig"))
            result = MCPServer(client).call("native_revit_submit", args)
        elif options.command == "batch":
            args = json.loads(Path(options.request_file).read_text(encoding="utf-8-sig"))
            result = MCPServer(client).call("native_revit_batch", args)
        elif options.command == "wait":
            result = client.wait(options.operation_id, options.timeout)
        elif options.command == "cancel":
            result = client.cancel(options.operation_id)
        else:
            result = client.job(options.operation_id)
        print(canonical(result))
        return 0 if result.get("status") not in {"failed", "rolled_back", "rejected", "cancelled", "unknown_completion", "partial_completion"} else 2
    except (ControllerError, OSError, ValueError) as exc:
        data = exc.as_dict() if isinstance(exc, ControllerError) else {"code": "controller_error", "message": "Could not read or process CLI request", "details": {"exception_type": type(exc).__name__}}
        print(canonical({"error": data}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
