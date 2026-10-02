"""Derive the Sonnet hex brief from the 2026-09-26 Opus brief, changing only the run context.

The task, inputs, geometry, deliverables and gates are copied unchanged so the Sonnet arms can be
graded against the Opus high/xhigh/max results with the same grader and blind review.
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "..", "..", "effort-trial-2026-09-26-hex", "BRIEF.md")
DST = os.path.join(HERE, "..", "BRIEF.md")

text = open(SRC, encoding="utf-8").read()

REPLACEMENTS = [
    (
        "Three agents run this same brief on Opus 5.5.",
        "Three agents run this same brief on Sonnet 5.5.",
    ),
    (
        "- **Don't look at earlier builds of this tile or the other arms.** Don't open, list or grep `output/hex_10in_dimensional/`,",
        "- **Don't look at earlier builds of this tile or the other arms.** Don't open, list or grep `output/hex_10in_dimensional/`, `output/effort-trial-2026-09-26-hex/` (an earlier trial of this same brief),",
    ),
    (
        "- Stop when every gate passes and your review is done.",
        "- Run every long build or check in the **foreground** and wait for it. Never end your turn while a background job is running: this is a headless session, and ending the turn kills background jobs.\n"
        "- Kill processes only by the PID you started. Never kill python.exe or any other process by name.\n"
        "- Stop when every gate passes and your review is done.",
    ),
]

for old, new in REPLACEMENTS:
    if text.count(old) != 1:
        raise SystemExit("expected exactly one occurrence of: %r" % old)
    text = text.replace(old, new)

with open(DST, "w", encoding="utf-8", newline="\n") as f:
    f.write(text)
print("wrote", os.path.normpath(DST), len(text), "chars")
