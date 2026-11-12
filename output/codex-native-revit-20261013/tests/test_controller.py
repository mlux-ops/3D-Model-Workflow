"""Fake HTTP/protocol tests only. Passing tests are NOT native Revit evidence."""
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import threading
import time
import unittest
import uuid
from unittest.mock import patch
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

MODULE = Path(__file__).resolve().parents[1] / "controller" / "native_revit.py"
spec = importlib.util.spec_from_file_location("native_revit", MODULE)
nr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(nr)


class FakeBridge:
    def __init__(self):
        self.requests, self.jobs = [], {}
        self.post_delay = 0
        self.mode = "completed"
        self.invalid_receipt = False
        owner = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def answer(self, status, data):
                raw = json.dumps(data).encode()
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(raw)))
                self.end_headers()
                try:
                    self.wfile.write(raw)
                except OSError:
                    pass

            def handle_request(self):
                payload = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
                owner.requests.append((self.command, self.path, payload))
                if self.headers.get("Authorization") != "Bearer test-secret":
                    self.answer(401, {"error": "unauthorized"})
                    return
                if self.command == "GET" and self.path == "/v1/capabilities":
                    self.answer(200, {"schema_version": 1, "operations": ["query", "create"]})
                    return
                if self.command == "POST" and self.path == "/v1/jobs":
                    oid = payload["operation_id"]
                    receipt = {"schema_version": 1, "operation_id": oid, "status": "failed" if payload["operation"] == "fail" else owner.mode,
                        "result": {"created": [{"unique_id": "new-native-id"}], "arguments": payload["arguments"]}}
                    owner.jobs[oid] = receipt
                    time.sleep(owner.post_delay)
                    self.answer(200, {**receipt, "operation_id": str(uuid.uuid4())} if owner.invalid_receipt else receipt)
                    return
                oid = self.path.split("/")[3] if self.path.startswith("/v1/jobs/") else None
                if oid not in owner.jobs:
                    self.answer(404, {"error": "not found"})
                    return
                if self.path.endswith("/cancel") and self.command == "POST":
                    owner.jobs[oid] = {**owner.jobs[oid], "status": "cancelled"}
                self.answer(200, owner.jobs[oid])

            do_GET = handle_request
            do_POST = handle_request

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.server.daemon_threads = True
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.url = "http://127.0.0.1:" + str(self.server.server_port)

    def close(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()

    @property
    def posts(self):
        return [request for request in self.requests if request[:2] == ("POST", "/v1/jobs")]


class ControllerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bridge = FakeBridge()

    @classmethod
    def tearDownClass(cls):
        cls.bridge.close()

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.bridge.requests.clear()
        self.bridge.jobs.clear()
        self.bridge.mode = "completed"
        self.bridge.post_delay = 0
        self.bridge.invalid_receipt = False
        self.client = nr.Client(base_url=self.bridge.url, token="test-secret", receipt_dir=self.directory.name, timeout=0.1)
        self.doc = {"session_id": "disposable-document-session"}

    def test_auth_and_detached_capabilities(self):
        self.assertEqual(self.client.capabilities()["operations"], ["query", "create"])
        self.assertEqual(len(self.bridge.posts), 0)
        wrong = nr.Client(base_url=self.bridge.url, token="wrong", receipt_dir=self.directory.name)
        with self.assertRaises(nr.ControllerError) as failure:
            wrong.capabilities()
        self.assertEqual(failure.exception.details["http_status"], 401)
        self.assertNotIn("wrong", str(failure.exception.as_dict()))

    def test_all_document_queries_use_targeted_jobs(self):
        receipt = self.client.submit("query", self.doc, {"filter": "cabinet"}, {"document_fingerprint": "fixture-only"})
        self.assertEqual(receipt["status"], "completed")
        request = self.bridge.posts[0][2]
        self.assertEqual(request["schema_version"], 1)
        self.assertEqual(request["document"], self.doc)
        self.assertEqual(request["preconditions"], {"document_fingerprint": "fixture-only"})
        self.assertEqual(request["operation_id"], receipt["operation_id"])

    def test_receipt_persists_and_reused_id_only_queries(self):
        oid = str(uuid.uuid4())
        first = self.client.submit("create", self.doc, {"x": 2}, operation_id_value=oid)
        restarted = nr.Client(base_url=self.bridge.url, token="test-secret", receipt_dir=self.directory.name)
        self.assertEqual(restarted.submit("create", self.doc, {"x": 2}, operation_id_value=oid), first)
        self.assertEqual(len(self.bridge.posts), 1)
        with self.assertRaises(nr.ControllerError) as failure:
            restarted.submit("create", self.doc, {"x": 3}, operation_id_value=oid)
        self.assertEqual(failure.exception.code, "operation_id_conflict")
        self.assertEqual(len(self.bridge.posts), 1)

    def test_timeout_keeps_original_id_then_reconciles_without_replay(self):
        self.bridge.post_delay = 0.2
        oid = str(uuid.uuid4())
        receipt = self.client.submit("create", self.doc, operation_id_value=oid)
        self.assertEqual(receipt["status"], "unknown_completion")
        self.assertEqual(receipt["operation_id"], oid)
        self.assertFalse(receipt["recovery"]["resubmit_allowed"])
        reconciled = self.client.submit("create", self.doc, operation_id_value=oid)
        self.assertEqual(reconciled["status"], "completed")
        self.assertEqual(len(self.bridge.posts), 1)

    def test_invalid_receipt_is_unknown_not_success(self):
        self.bridge.invalid_receipt = True
        receipt = self.client.submit("create", self.doc)
        self.assertEqual(receipt["status"], "unknown_completion")
        self.assertEqual(receipt["error"]["code"], "invalid_response")
        self.assertEqual(len(self.bridge.posts), 1)

    def test_missing_server_receipt_never_replays_local_reservation(self):
        oid = str(uuid.uuid4())
        self.client.submit("create", self.doc, operation_id_value=oid)
        self.bridge.jobs.clear()
        receipt = self.client.submit("create", self.doc, operation_id_value=oid)
        self.assertEqual(receipt["status"], "unknown_completion")
        self.assertEqual(receipt["error"]["details"]["http_status"], 404)
        self.assertEqual(len(self.bridge.posts), 1)

    def test_cache_write_failure_preserves_actual_receipt_and_original_id(self):
        oid = str(uuid.uuid4())
        with patch.object(self.client, "_write_record", side_effect=OSError("disk unavailable")):
            receipt = self.client.submit("create", self.doc, operation_id_value=oid)
        self.assertEqual(receipt["status"], "completed")
        self.assertEqual(receipt["operation_id"], oid)
        self.assertEqual(receipt["controller_warnings"][0]["code"], "receipt_cache_update_failed")
        self.assertEqual(self.client.job(oid)["status"], "completed")
        self.assertEqual(len(self.bridge.posts), 1)

    def test_corrupt_local_record_can_query_but_cannot_resubmit(self):
        oid = str(uuid.uuid4())
        self.client.submit("create", self.doc, operation_id_value=oid)
        self.client._path(oid).write_text("invalid", encoding="utf-8")
        self.assertEqual(self.client.job(oid)["status"], "completed")
        with self.assertRaises(nr.ControllerError) as failure:
            self.client.submit("create", self.doc, operation_id_value=oid)
        self.assertEqual(failure.exception.code, "receipt_unreadable")
        self.assertEqual(len(self.bridge.posts), 1)

    def test_wait_timeout_and_safe_cancellation_receipt(self):
        self.bridge.mode = "running"
        receipt = self.client.submit("create", self.doc)
        waited = self.client.wait(receipt["operation_id"], timeout_seconds=0.04, poll_interval=0.01)
        self.assertEqual(waited["status"], "unknown_completion")
        self.assertEqual(waited["last_known_status"], "running")
        self.assertEqual(self.client.cancel(receipt["operation_id"])["status"], "cancelled")
        self.assertEqual(self.client.wait(receipt["operation_id"], 0.1)["status"], "cancelled")

    def test_batch_blocks_failed_dependents_and_runs_independent_steps(self):
        steps = [
            {"id": "dependent", "operation": "create", "document": self.doc, "depends_on": ["bad"]},
            {"id": "bad", "operation": "fail", "document": self.doc, "depends_on": []},
            {"id": "independent", "operation": "query", "document": self.doc, "depends_on": []},
        ]
        batch = self.client.batch(steps)
        self.assertEqual(batch["status"], "partial_completion")
        self.assertFalse(batch["atomic"])
        self.assertEqual(batch["steps"]["dependent"]["status"], "blocked")
        self.assertEqual(batch["steps"]["independent"]["status"], "completed")
        self.assertEqual([request[2]["operation"] for request in self.bridge.posts], ["fail", "query"])
        self.assertEqual(batch["metrics"]["http_round_trips"], 2)
        self.assertGreater(batch["metrics"]["request_bytes"], 0)

    def test_batch_resolves_new_identifiers_and_resume_never_recreates(self):
        bid = str(uuid.uuid4())
        steps = [
            {"id": "make", "operation": "create", "document": self.doc, "depends_on": []},
            {"id": "modify", "operation": "modify", "document": self.doc, "depends_on": ["make"],
             "arguments": {"target": {"$result": "make", "path": "created.0.unique_id"}}},
        ]
        batch = self.client.batch(steps, batch_id=bid)
        self.assertEqual(batch["status"], "completed")
        self.assertEqual(self.bridge.posts[1][2]["arguments"]["target"], "new-native-id")
        self.assertEqual(self.client.batch(steps, batch_id=bid)["status"], "completed")
        self.assertEqual(len(self.bridge.posts), 2)

    def test_batch_cycles_and_missing_dependencies_fail_before_submission(self):
        for dependencies in (["a"], ["missing"]):
            with self.assertRaises(nr.ControllerError):
                self.client.batch([{"id": "a", "operation": "create", "document": self.doc, "depends_on": dependencies}])
        self.assertEqual(len(self.bridge.posts), 0)

    def test_changed_batch_graph_is_rejected_before_additional_posts(self):
        bid = str(uuid.uuid4())
        steps = [{"id": "one", "operation": "create", "document": self.doc, "depends_on": []}]
        self.client.batch(steps, batch_id=bid)
        changed = [{"id": "new", "operation": "create", "document": self.doc, "depends_on": []}] + steps
        with self.assertRaises(nr.ControllerError) as failure:
            self.client.batch(changed, batch_id=bid)
        self.assertEqual(failure.exception.code, "batch_id_conflict")
        self.assertEqual(len(self.bridge.posts), 1)

    def test_invalid_batch_timeout_is_rejected_before_post(self):
        with self.assertRaises(nr.ControllerError):
            self.client.batch([{"id": "one", "operation": "create", "document": self.doc, "depends_on": []}], timeout_seconds=-1)
        self.assertEqual(len(self.bridge.posts), 0)

    def test_native_atomic_batch_orders_dependencies_and_rejects_unhandled_guards(self):
        steps = [
            {"id": "b", "operation": "element.move", "document": self.doc, "arguments": {}, "depends_on": ["a"]},
            {"id": "a", "operation": "element.move", "document": self.doc, "arguments": {}, "depends_on": []},
        ]
        receipt = self.client.batch(steps, native_operation="batch.atomic", document=self.doc)
        self.assertEqual(receipt["status"], "completed")
        self.assertEqual([step["id"] for step in self.bridge.posts[0][2]["arguments"]["steps"]], ["a", "b"])
        steps[0]["preconditions"] = {"expected_pinned": False}
        with self.assertRaises(nr.ControllerError):
            self.client.batch(steps, native_operation="batch.atomic", document=self.doc)
        self.assertEqual(len(self.bridge.posts), 1)

    def test_native_atomic_batch_rejects_placeholders_before_post(self):
        steps = [
            {"id": "a", "operation": "element.move", "document": self.doc, "depends_on": []},
            {"id": "b", "operation": "element.move", "document": self.doc, "depends_on": ["a"], "arguments": {"element": {"$result": "a"}}},
        ]
        with self.assertRaises(nr.ControllerError):
            self.client.batch(steps, native_operation="batch.atomic", document=self.doc)
        self.assertEqual(len(self.bridge.posts), 0)

    def test_mcp_protocol_structured_results_notifications_and_errors(self):
        server = nr.MCPServer(self.client)
        def call(method, params=None):
            return server.dispatch({"jsonrpc": "2.0", "id": 7, "method": method, "params": params or {}})
        self.assertEqual(call("initialize", {"protocolVersion": "2025-03-26"})["result"]["protocolVersion"], "2025-03-26")
        self.assertIsNone(server.dispatch({"jsonrpc": "2.0", "method": "notifications/initialized"}))
        definitions = call("tools/list")["result"]["tools"]
        submit = next(tool for tool in definitions if tool["name"] == "native_revit_submit")
        self.assertFalse(submit["annotations"]["readOnlyHint"])
        self.assertFalse(submit["annotations"]["idempotentHint"])
        self.assertTrue(submit["annotations"]["openWorldHint"])
        success = call("tools/call", {"name": "native_revit_capabilities"})["result"]
        self.assertEqual(json.loads(success["content"][0]["text"]), success["structuredContent"])
        self.assertFalse(success["isError"])
        error = call("tools/call", {"name": "native_revit_submit", "arguments": {"operation": "create"}})["result"]
        self.assertTrue(error["isError"])
        self.assertEqual(error["structuredContent"]["error"]["code"], "invalid_argument")
        self.assertEqual(call("unknown")["error"]["code"], -32601)

    def test_mcp_stdout_is_only_json_rpc_and_survives_bad_json(self):
        input_stream = io.StringIO('broken\n{"jsonrpc":"2.0","method":"notifications/initialized"}\n{"jsonrpc":"2.0","id":1,"method":"ping"}\n')
        output = io.StringIO()
        nr.MCPServer(self.client).serve(input_stream, output)
        records = [json.loads(line) for line in output.getvalue().splitlines()]
        self.assertEqual(len(records), 2)
        self.assertEqual(records[0]["error"]["code"], -32700)
        self.assertEqual(records[1], {"jsonrpc": "2.0", "id": 1, "result": {}})

    def test_loopback_origin_enforced(self):
        for url in ("https://127.0.0.1:49327", "http://example.com", "http://user:pass@127.0.0.1", "http://127.0.0.1/path"):
            with self.assertRaises(nr.ControllerError):
                nr.Client(base_url=url)


if __name__ == "__main__":
    unittest.main()
