"""Phase 7 helper: call the Unreal editor's agent server from a terminal.

Usage:
    python -B ue_call.py list
    python -B ue_call.py describe <toolset name> [<toolset name> ...]
    python -B ue_call.py tool <toolset name> <tool name> [<json arguments>]
    python -B ue_call.py py <script file> [timeout seconds]
    python -B ue_call.py pyc "<python source>" [timeout seconds]
    python -B ue_call.py ws "<expression using ws, the module wieland_site>" [timeout seconds]
    python -B ue_call.py wg "<expression using ws and wg, the module wieland_ground>" [timeout seconds]

Speaks the Model Context Protocol over HTTP to http://127.0.0.1:8000/mcp, the
same way `mcp_readonly_calls_test.py` does. `py` sends a script file to the
editor's Python; the script's printed output and its result come back as text.
Standard library only.
"""

import json
import os
import sys
import urllib.error
import urllib.request

URL = "http://127.0.0.1:8000/mcp"
PROTOCOL = "2025-06-18"
PY_TOOLSET = "editor_toolset.toolsets.python_scripting.PythonScriptingTools"
PY_TOOL = "execute_python"


class Client:
    def __init__(self, url=URL):
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
        return messages

    def request(self, method, params, timeout=120.0):
        call_id = self.next_id
        self.next_id += 1
        for message in self.post({"jsonrpc": "2.0", "id": call_id, "method": method, "params": params}, timeout):
            if isinstance(message, dict) and message.get("id") == call_id:
                return message
        return None

    def open(self):
        message = self.request("initialize", {"protocolVersion": PROTOCOL, "capabilities": {}, "clientInfo": {"name": "phase7-ue-call", "version": "1"}})
        if message is None or "result" not in message:
            raise RuntimeError("initialize failed: %s" % json.dumps(message)[:400])
        self.negotiated = message["result"].get("protocolVersion")
        self.post({"jsonrpc": "2.0", "method": "notifications/initialized"})

    def call(self, name, arguments, timeout=120.0):
        return self.request("tools/call", {"name": name, "arguments": arguments}, timeout)


def show(message):
    if message is None:
        print("NO RESPONSE")
        return 1
    if "error" in message:
        print("PROTOCOL ERROR: " + json.dumps(message["error"]))
        return 1
    result = message.get("result", {})
    for item in result.get("content", []):
        if item.get("type") == "text":
            print(item.get("text", ""))
        else:
            print(json.dumps(item)[:2000])
    if result.get("isError"):
        print("TOOL ERROR FLAG SET")
        return 1
    return 0


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    client = Client()
    try:
        client.open()
        mode = argv[1]
        if mode == "list":
            return show(client.call("list_toolsets", {}))
        if mode == "describe":
            return show(client.call("describe_toolsets", {"toolset_names": argv[2:]}))
        if mode == "tool":
            arguments = json.loads(argv[4]) if len(argv) > 4 else {}
            return show(client.call("call_tool", {"toolset_name": argv[2], "tool_name": argv[3], "arguments": arguments}, 300.0))
        if mode == "wg":
            # As "ws", with the site-ground module wieland_ground loaded too (as wg).
            tools = os.path.dirname(os.path.abspath(__file__)).replace(os.sep, "/")
            source = ("import sys\nimport importlib\nsys.dont_write_bytecode = True\n"
                      "TOOLS = %r\nif TOOLS not in sys.path:\n    sys.path.insert(0, TOOLS)\n"
                      "import wieland_site as ws\nimportlib.reload(ws)\n"
                      "import wieland_ground as wg\nimportlib.reload(wg)\n" % tools) + argv[2] + "\n"
            timeout = float(argv[3]) if len(argv) > 3 else 300.0
            arguments = {"script": {"language": "Python", "content": source}}
            return show(client.call("call_tool", {"toolset_name": PY_TOOLSET, "tool_name": PY_TOOL, "arguments": arguments}, timeout))
        if mode == "ws":
            # One expression against the Phase 7 editor module, reloaded so that edits to the file count.
            tools = os.path.dirname(os.path.abspath(__file__)).replace(os.sep, "/")
            source = ("import sys\nimport importlib\nsys.dont_write_bytecode = True\n"
                      "TOOLS = %r\nif TOOLS not in sys.path:\n    sys.path.insert(0, TOOLS)\n"
                      "import wieland_site as ws\nimportlib.reload(ws)\n" % tools) + argv[2] + "\n"
            timeout = float(argv[3]) if len(argv) > 3 else 300.0
            arguments = {"script": {"language": "Python", "content": source}}
            return show(client.call("call_tool", {"toolset_name": PY_TOOLSET, "tool_name": PY_TOOL, "arguments": arguments}, timeout))
        if mode in ("py", "pyc"):
            if mode == "py":
                with open(argv[2], "r", encoding="utf-8") as handle:
                    source = handle.read()
            else:
                source = argv[2]
            timeout = float(argv[3]) if len(argv) > 3 else 120.0
            arguments = {"script": {"language": "Python", "content": source}}
            return show(client.call("call_tool", {"toolset_name": PY_TOOLSET, "tool_name": PY_TOOL, "arguments": arguments}, timeout))
        print(__doc__)
        return 2
    except urllib.error.URLError as error:
        print("SERVER NOT REACHABLE: %r" % (error,))
        return 3


if __name__ == "__main__":
    sys.exit(main(sys.argv))
