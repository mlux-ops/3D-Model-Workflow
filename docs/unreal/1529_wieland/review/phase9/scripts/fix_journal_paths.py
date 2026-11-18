"""Phase 9: repair path text in phase9_results.md that a shell here-document damaged (backslash sequences were
turned into control characters). Usage: python -B fix_journal_paths.py"""

import io
import os

PATH = os.path.dirname(os.path.abspath(__file__)).replace(os.sep, "/").rsplit("/review/", 1)[0] + "/phase9_results.md"
BACK = chr(92)
text = io.open(PATH, encoding="utf-8").read()
fixed = text.replace("profiles" + chr(0x82) + "6-", "profiles" + BACK + "2026-").replace("scripts" + chr(9) + "ree_dump", "scripts" + BACK + "tree_dump")
left = sorted(set(ch for ch in fixed if ord(ch) < 32 and ch != "\n") | set(ch for ch in fixed if 127 <= ord(ch) < 160))
io.open(PATH, "w", encoding="utf-8", newline="\n").write(fixed)
print("changed", text != fixed, "control characters left", [hex(ord(ch)) for ch in left])
