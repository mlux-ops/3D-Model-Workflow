"""Phase 9: list the console variables whose name contains a text, with value and the start of the help text.

Usage: python -B cvars.py <text> [<only names containing this second text>]
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__)).replace(os.sep, "/")
sys.path.insert(0, HERE.rsplit("/review/", 1)[0] + "/tools")
sys.dont_write_bytecode = True

import ue_call  # noqa: E402

client = ue_call.Client()
client.open()
message = client.call("call_tool", {"toolset_name": "ConsoleToolset.ConsoleToolset", "tool_name": "SearchCVars", "arguments": {"name": sys.argv[1]}}, 120.0)
text = "".join(item.get("text", "") for item in message["result"]["content"])
found = json.loads(text)["returnValue"]
second = sys.argv[2].lower() if len(sys.argv) > 2 else ""
if isinstance(found, str):
    found = json.loads(found)
for name in sorted(found):
    entry = found[name]
    line = "%s = %s | %s" % (name, entry.get("value"), str(entry.get("help", "")).replace("\n", " ")[:170])
    if second in line.lower():
        print(line)
