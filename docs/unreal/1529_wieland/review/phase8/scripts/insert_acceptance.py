"""Insert review/phase8/scripts/acceptance_text.md into phase8_results.md, before "How to resume" (once)."""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
JOURNAL = os.path.normpath(os.path.join(HERE, "..", "..", "..", "phase8_results.md"))
with open(JOURNAL, "r", encoding="utf-8") as handle:
    text = handle.read()
with open(os.path.join(HERE, "acceptance_text.md"), "r", encoding="utf-8") as handle:
    block = handle.read()
if "## Acceptance" in text:
    raise SystemExit("already inserted")
old = "`/Game/Wieland1529/L_Site_M4` (11 levels before this phase)"
if old not in text or "## How to resume" not in text:
    raise SystemExit("anchor not found")
text = text.replace("## How to resume", block + "## How to resume", 1)
text = text.replace(old, "`/Game/Wieland1529/L_Site_M4` (11 levels before this phase, 12 with the lighting level)")
with open(JOURNAL, "w", encoding="utf-8", newline="\n") as handle:
    handle.write(text)
print("inserted")
