"""Independently calculate R033 WC blind-seat arithmetic from original criterion rows."""
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP
import json
import re

ROOT = Path(__file__).resolve().parents[1]
ROOMS = ("PH-WC", "TX-WC")
WEIGHTS = {"market": Decimal(".30"), "design": Decimal(".25"), "build": Decimal(".25"), "cost": Decimal(".20")}
CRITERIA_COUNTS = {"market": 4, "design": 5, "build": 5, "cost": 5}
RX = re.compile(r"^\|[^|]+\|\s*(?:\*\*)?([1-5](?:\.\d+)?)(?:/5)?(?:\*\*)?\s*\|")
Q = lambda d: d.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
EXPECTED = {
 "PH-WC": {"A": ("4.3", "4.4", "3.8", "3.8"), "B": ("3.9", "3.8", "3.2", "3.4")},
 "TX-WC": {"A": ("4.3", "4.0", "3.4", "3.6"), "B": ("3.8", "3.8", "3.0", "3.6")},
}
out = {}
ratings = 0
for room in ROOMS:
    data = {"A": {}, "B": {}}
    for seat, weight in WEIGHTS.items():
        p = ROOT / "rooms" / room / "board" / "round-033" / ("critic-" + seat + ".md")
        text = p.read_text(encoding="utf-8-sig")
        parts = re.split(r"(?m)^## Candidate ([AB])\b", text)
        assert len(parts) == 5, (p, len(parts))
        assert set((parts[1], parts[3])) == {"A", "B"}, p
        for i in (1, 3):
            letter, section = parts[i], parts[i+1]
            vals = [Decimal(m.group(1)) for line in section.splitlines() if (m := RX.match(line))]
            assert len(vals) == CRITERIA_COUNTS[seat], (room, seat, letter, vals)
            ratings += len(vals)
            mean = Q(sum(vals) / Decimal(len(vals)))
            assert mean == Decimal(EXPECTED[room][letter][list(WEIGHTS).index(seat)]), (room, seat, letter, mean)
            for field in ("top_fix", "gate_flags", "confidence"):
                assert re.search(field, section, re.IGNORECASE), (room, seat, letter, field)
            data[letter][seat] = {"criteria": [str(v) for v in vals], "mean": str(mean)}
    for letter in ("A", "B"):
        mins = [Decimal(data[letter][s]["mean"]) for s in WEIGHTS]
        total = sum(Decimal(data[letter][s]["mean"]) * w for s, w in WEIGHTS.items()).quantize(Decimal(".001"))
        data[letter].update(weighted=str(total), min_seat=str(min(mins)), seat_gate_pass=all(x >= 3 for x in mins),
                            inherited_parent_only=True, separate_wc_order_sf=0, separate_wc_order_usd=0,
                            full_room_accepted=False)
    out[room] = data
assert ratings == 76, ratings
assert Decimal(out["PH-WC"]["A"]["weighted"]) == Decimal("4.100")
assert Decimal(out["PH-WC"]["B"]["weighted"]) == Decimal("3.600")
assert Decimal(out["TX-WC"]["A"]["weighted"]) == Decimal("3.860")
assert Decimal(out["TX-WC"]["B"]["weighted"]) == Decimal("3.560")
print(json.dumps({"criterion_count": ratings, "data": out}, indent=2))
