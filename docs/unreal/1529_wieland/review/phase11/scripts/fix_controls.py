"""Phase 11: repair text where a backslash followed by a, t or f was turned into a control character (BEL, TAB, FF)
when text was passed through the shell. Only BEL, FF and TAB characters that sit inside a Windows path are restored.
    python -B fix_controls.py <file>
"""
import sys

BS = chr(92)
path = sys.argv[1]
with open(path, encoding="utf-8", newline="") as handle:
    text = handle.read()
before = sum(1 for c in text if c in "\x07\x0c")
text = text.replace("\x07", BS + "a").replace("\x0c", BS + "f")
# a TAB is restored only where it follows a path character (letters, digits, underscore) inside a path
out, fixed_tabs = [], 0
for i, c in enumerate(text):
    if c == "\t" and i > 0 and (text[i - 1].isalnum() or text[i - 1] in "_-.:") and BS in text[max(0, i - 60):i]:
        out.append(BS + "t")
        fixed_tabs += 1
    else:
        out.append(c)
text = "".join(out)
with open(path, "w", encoding="utf-8", newline="") as handle:
    handle.write(text)
left = [hex(ord(c)) for c in text if ord(c) < 32 and c not in "\r\n"]
print({"bel_ff_fixed": before, "tabs_fixed": fixed_tabs, "control_characters_left": len(left)})
