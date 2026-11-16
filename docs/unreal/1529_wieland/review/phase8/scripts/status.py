"""Put a new first status line into phase8_results.md; the line in force becomes "Earlier status:".

    python status.py <text file with the new status, one paragraph, starting after "Status: ">
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
JOURNAL = os.path.normpath(os.path.join(HERE, "..", "..", "..", "phase8_results.md"))
with open(sys.argv[1], "r", encoding="utf-8") as handle:
    text = " ".join(line.strip() for line in handle.read().splitlines() if line.strip())
with open(JOURNAL, "r", encoding="utf-8") as handle:
    lines = handle.read().split("\n")
for i, line in enumerate(lines):
    if line.startswith("Status: "):
        lines[i] = "Earlier status: " + line[len("Status: "):]
        lines[i:i] = ["Status: " + text, ""]
        break
else:
    raise SystemExit("no status line")
with open(JOURNAL, "w", encoding="utf-8", newline="\n") as handle:
    handle.write("\n".join(lines))
print("status set")
