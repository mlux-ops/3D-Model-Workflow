"""Phase 10 journal helper. Replaces the PENDING cell of the last journal line of phase10_results.md with the
outcome (first file) and, when a second file is given, appends the next line as PENDING. Both times are read
from the clock here, never typed. Usage: python -B review/phase10/scripts/journal.py outcome.txt [next.txt]"""
import datetime
import re
import sys

PATH = "phase10_results.md"
now = datetime.datetime.now().strftime("%H:%M")
with open(PATH, encoding="utf-8", newline="") as handle:
    text = handle.read()
with open(sys.argv[1], encoding="utf-8") as handle:
    outcome = " ".join(handle.read().split())
head, sep, tail = text.rpartition("| PENDING |")
if not sep:
    raise SystemExit("no PENDING line")
text = head + "| DONE " + now + ". " + outcome + " |" + tail
if len(sys.argv) > 2:
    with open(sys.argv[2], encoding="utf-8") as handle:
        step = " ".join(handle.read().split())
    last = int(re.findall(r"^\| J(\d+) \|", text, flags=re.M)[-1])
    text = text.rstrip("\n") + "\n| J%d | %s | %s | PENDING |\n" % (last + 1, now, step)
with open(PATH, "w", encoding="utf-8", newline="") as handle:
    handle.write(text)
print("journal written at", now)
