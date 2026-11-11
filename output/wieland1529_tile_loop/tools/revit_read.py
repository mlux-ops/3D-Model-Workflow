"""Read-only access to the open Revit model through the codex-native-revit-2025 bridge.

The tile loop uses this instead of any Revit MCP plugin. It refuses every operation that is
not on READ_OPERATIONS, so it cannot change, save or sync the model.

Usage (from the loop folder):
  python tools/revit_read.py capabilities
  python tools/revit_read.py documents.list
  python tools/revit_read.py <operation> --title "25-006 1527 N Wieland" [--args-file req.json | --args '{"...": ...}']

Every completed job is saved under state/revit_receipts/<operation_id>.json. The bearer token is
read from the bridge's token file and is never printed or saved.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path

READ_OPERATIONS = frozenset({
    "documents.list",
    "context.query",
    "categories.query",
    "warnings.query",
    "elements.query",
    "elements.inspect",
    "parameters.query",
    "links.query",
    "sheet.inspect",
    "view.inspect",
    "api.lookup",
})

DEFAULT_URL = "http://127.0.0.1:49327"
DEFAULT_TOKEN = Path(os.environ.get("LOCALAPPDATA", "")) / "CodexNativeRevit" / "token"
LOOP_ROOT = Path(__file__).resolve().parent.parent
RECEIPTS = LOOP_ROOT / "state" / "revit_receipts"


class BridgeError(Exception):
    """The bridge refused the request or did not answer as expected."""


def _token(path: Path) -> str:
    try:
        value = path.read_text(encoding="utf-8").strip()
    except OSError as exc:
        raise BridgeError(f"cannot read token file {path}: {exc.strerror}") from exc
    if not value:
        raise BridgeError(f"token file {path} is empty")
    return value


def _call(url: str, token: str, method: str, route: str, body: dict | None = None) -> dict:
    data = json.dumps(body).encode("utf-8") if body is not None else None
    request = urllib.request.Request(url.rstrip("/") + route, data=data, method=method)
    request.add_header("Authorization", f"Bearer {token}")
    if data is not None:
        request.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        hint = " (token does not match the running Revit; check the token file)" if exc.code == 401 else ""
        raise BridgeError(f"bridge returned HTTP {exc.code} for {method} {route}{hint}") from exc
    except urllib.error.URLError as exc:
        raise BridgeError(f"bridge not reachable at {url}: {exc.reason} (is Revit open with the add-in loaded?)") from exc


def _run_job(url: str, token: str, operation: str, document: dict, arguments: dict, timeout: float) -> dict:
    if operation not in READ_OPERATIONS:
        raise BridgeError(f"refused: {operation} is not a read operation; this loop never changes the model")
    envelope = {
        "schema_version": 1,
        "operation_id": str(uuid.uuid4()),
        "operation": operation,
        "document": document,
        "arguments": arguments,
    }
    receipt = _call(url, token, "POST", "/v1/jobs", envelope)
    op_id = receipt.get("operation_id", envelope["operation_id"])
    deadline = time.monotonic() + timeout
    while receipt.get("status") in ("queued", "running"):
        if time.monotonic() > deadline:
            raise BridgeError(f"job {op_id} still {receipt.get('status')} after {timeout:.0f}s; Revit may be busy "
                              "or showing a dialog. Do not resubmit; query it later with: job " + op_id)
        time.sleep(0.5)
        receipt = _call(url, token, "GET", f"/v1/jobs/{op_id}")
    RECEIPTS.mkdir(parents=True, exist_ok=True)
    (RECEIPTS / f"{op_id}.json").write_text(json.dumps(receipt, indent=1), encoding="utf-8")
    if receipt.get("status") != "completed":
        raise BridgeError(f"job {op_id} ended {receipt.get('status')}: {json.dumps(receipt.get('error'))}")
    if receipt.get("transaction_status") not in (None, "not_started"):
        raise BridgeError(f"job {op_id} reported transaction_status={receipt.get('transaction_status')}; stop and tell the owner")
    return receipt


def _document_for_title(url: str, token: str, title: str, timeout: float) -> dict:
    listing = _run_job(url, token, "documents.list", {}, {}, timeout)
    matches = [d for d in listing.get("result") or [] if d.get("title") == title and not d.get("is_family")]
    if len(matches) != 1:
        open_titles = [d.get("title") for d in listing.get("result") or []]
        raise BridgeError(f"expected exactly one open project titled {title!r}; open documents: {open_titles}")
    return {"session_id": matches[0]["session_id"]}


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("operation", help="capabilities, job, or one of: " + ", ".join(sorted(READ_OPERATIONS)))
    parser.add_argument("job_id", nargs="?", help="operation id, only with 'job'")
    parser.add_argument("--title", help="exact title of the open project to query")
    parser.add_argument("--args", dest="args_json", default=None, help="arguments as a JSON object")
    parser.add_argument("--args-file", type=Path, default=None, help="file holding the arguments JSON object")
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument("--token-file", type=Path, default=DEFAULT_TOKEN)
    parser.add_argument("--timeout", type=float, default=60.0)
    opts = parser.parse_args(argv)

    try:
        if opts.operation not in READ_OPERATIONS | {"capabilities", "job"}:
            raise BridgeError(f"refused: {opts.operation} is not a read operation; this loop never changes the model")
        token = _token(opts.token_file)
        if opts.operation == "capabilities":
            print(json.dumps(_call(opts.url, token, "GET", "/v1/capabilities")))
            return 0
        if opts.operation == "job":
            if not opts.job_id:
                raise BridgeError("job needs an operation id")
            print(json.dumps(_call(opts.url, token, "GET", f"/v1/jobs/{opts.job_id}")))
            return 0
        if opts.args_json is not None and opts.args_file is not None:
            raise BridgeError("use --args or --args-file, not both")
        raw = opts.args_file.read_text(encoding="utf-8") if opts.args_file else (opts.args_json or "{}")
        arguments = json.loads(raw)
        if not isinstance(arguments, dict):
            raise BridgeError("arguments must be a JSON object")
        if opts.operation == "documents.list":
            document: dict = {}
        elif opts.title:
            document = _document_for_title(opts.url, token, opts.title, opts.timeout)
        else:
            raise BridgeError("--title is required for every operation except documents.list")
        receipt = _run_job(opts.url, token, opts.operation, document, arguments, opts.timeout)
        print(json.dumps({"operation_id": receipt["operation_id"], "result": receipt.get("result")}))
        return 0
    except (BridgeError, json.JSONDecodeError, OSError) as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
