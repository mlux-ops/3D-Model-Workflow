"""Apply two independent reviewer-specified factual corrections in Round002."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
changes = [
    ("TX-BATH2", "C",
     "within one measured recessed niche",
     "in one provisionally estimated recessed niche"),
    ("TX-BATH4", "A",
     "$299.03/unit",
     "$299.02/unit (carried row rounding; $299.025 before rounding)"),
    ("TX-BATH4", "B",
     "$299.03/unit",
     "$299.02/unit (carried row rounding; $299.025 before rounding)"),
]
for room, letter, old, new in changes:
    path = ROOT / "rooms" / room / "board" / "round-002" / "candidates" / (letter + ".md")
    text = path.read_text(encoding="utf-8")
    assert old in text, (room, old)
    text = text.replace(old, new)
    path.write_text(text, encoding="utf-8")
    print(room, letter, "fixed", text.count(new))
