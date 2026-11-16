"""Phase 1 acceptance test: consecutive read-only calls to the editor's agent server.

Usage:
    python mcp_readonly_calls_test.py <result .json> [count] [url]

Speaks the Model Context Protocol over HTTP to the Unreal editor's own server
(default http://127.0.0.1:8000/mcp), as a second client beside the panel. It
opens one session, then makes <count> calls (default 50) one after another,
rotating through tools that the server itself marks as read-only. Nothing in
the project is changed.

A call passes when the server answers HTTP 200 with a result for that call,
with no protocol error and without the tool's error flag. The script records
each call's duration and writes a summary. Standard library only.
"""

import json
import sys
import time
import urllib.error
import urllib.request

DEFAULT_URL = "http://127.0.0.1:8000/mcp"
PROTOCOL = "2025-06-18"


def toolset_call(toolset, tool, arguments=None):
    return "call_tool", {"toolset_name": toolset, "tool_name": tool, "arguments": arguments or {}}


READ_ONLY_CALLS = [
    ("list_toolsets", {}),
    toolset_call("EditorToolset.LevelToolset", "GetCurrentLevel"),
    toolset_call("EditorToolset.EditorAppToolset", "GetCameraTransform"),
    toolset_call("ConsoleToolset.ConsoleToolset", "GetCVarValue", {"name": "r.ScreenPercentage"}),
    toolset_call("PerfToolset.StatsToolset", "GetFrameTimings"),
    toolset_call("EditorToolset.EditorAppToolset", "IsPIERunning"),
    toolset_call("SceneCaptureToolset.SceneCaptureToolset", "ListEditorViewports"),
    ("describe_toolsets", {"toolset_names": ["PerfToolset.StatsToolset"]}),
    toolset_call("ToolsetRegistry.AgentSkillToolset", "ListSkills"),
    toolset_call("EditorToolset.EditorAppToolset", "GetSelectedActors"),
]


class Client:
    def __init__(self, url):
        self.url = url
        self.session = None
        self.negotiated = None
        self.next_id = 1

    def post(self, payload, timeout=120.0):
        headers = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}
        if self.session:
            headers["Mcp-Session-Id"] = self.session
        if self.negotiated:
            headers["MCP-Protocol-Version"] = self.negotiated
        request = urllib.request.Request(self.url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
        with urllib.request.urlopen(request, timeout=timeout) as response:
            session = response.headers.get("Mcp-Session-Id")
            if session:
                self.session = session
            content_type = response.headers.get("Content-Type", "")
            body = response.read().decode("utf-8", errors="replace")
            status = response.status
        messages = []
        if "text/event-stream" in content_type:
            for block in body.replace("\r\n", "\n").split("\n\n"):
                data_lines = [line[5:].lstrip() for line in block.split("\n") if line.startswith("data:")]
                if data_lines:
                    try:
                        messages.append(json.loads("\n".join(data_lines)))
                    except ValueError:
                        pass
        elif body.strip():
            messages.append(json.loads(body))
        return status, messages

    def request(self, method, params, timeout=120.0):
        call_id = self.next_id
        self.next_id += 1
        status, messages = self.post({"jsonrpc": "2.0", "id": call_id, "method": method, "params": params}, timeout)
        for message in messages:
            if isinstance(message, dict) and message.get("id") == call_id:
                return status, message
        return status, None

    def open(self):
        status, message = self.request("initialize", {"protocolVersion": PROTOCOL, "capabilities": {}, "clientInfo": {"name": "phase1-readonly-calls-test", "version": "1"}})
        if message is None or "result" not in message:
            raise RuntimeError("initialize failed: HTTP %s %s" % (status, json.dumps(message)[:400]))
        result = message["result"]
        self.negotiated = result.get("protocolVersion")
        self.post({"jsonrpc": "2.0", "method": "notifications/initialized"})
        return result


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    result_path = argv[1]
    count = int(argv[2]) if len(argv) > 2 else 50
    url = argv[3] if len(argv) > 3 else DEFAULT_URL
    client = Client(url)
    opened = client.open()
    calls = []
    for index in range(count):
        name, arguments = READ_ONLY_CALLS[index % len(READ_ONLY_CALLS)]
        label = name if name != "call_tool" else arguments["toolset_name"] + "." + arguments["tool_name"]
        entry = {"n": index + 1, "tool": label, "ok": False}
        started = time.perf_counter()
        try:
            status, message = client.request("tools/call", {"name": name, "arguments": arguments})
            entry["http"] = status
            if message is None:
                entry["problem"] = "no response message for this call"
            elif "error" in message:
                entry["problem"] = "protocol error: " + json.dumps(message["error"])[:300]
            elif message.get("result", {}).get("isError"):
                entry["problem"] = "tool error: " + json.dumps(message["result"])[:300]
            else:
                entry["ok"] = status == 200
                entry["result_chars"] = len(json.dumps(message.get("result")))
                if not entry["ok"]:
                    entry["problem"] = "HTTP %s" % status
        except urllib.error.HTTPError as error:
            entry["http"] = error.code
            entry["problem"] = "HTTP error %s: %s" % (error.code, error.read().decode("utf-8", errors="replace")[:300])
        except Exception as error:
            entry["problem"] = repr(error)[:300]
        entry["ms"] = round((time.perf_counter() - started) * 1000.0, 1)
        calls.append(entry)
    durations = sorted(call["ms"] for call in calls)
    failures = [call for call in calls if not call["ok"]]
    longest_run = 0
    run = 0
    for call in calls:
        run = run + 1 if call["ok"] else 0
        longest_run = max(longest_run, run)
    summary = {
        "url": url,
        "started_local": time.strftime("%Y-%m-%d %H:%M:%S"),
        "server": opened.get("serverInfo"),
        "protocol": opened.get("protocolVersion"),
        "calls": len(calls),
        "passed": len(calls) - len(failures),
        "failed": len(failures),
        "longest_run_without_error": longest_run,
        "ms_min": durations[0],
        "ms_median": durations[len(durations) // 2],
        "ms_mean": round(sum(durations) / len(durations), 1),
        "ms_max": durations[-1],
        "distinct_tools": sorted(set(call["tool"] for call in calls)),
        "failures": failures,
    }
    with open(result_path, "w", encoding="utf-8") as handle:
        json.dump({"summary": summary, "calls": calls}, handle, indent=1)
    print(json.dumps(summary, indent=1))
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
