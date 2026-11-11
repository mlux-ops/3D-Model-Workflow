"""Remove reviewer-identified candidate role disclosures from Round 002 packets."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
replacements = {
    "TX-BATH2/B.md": [
        ("# TX-BATH2 — Candidate B — Copper tub walls / certified-intent cream floor test",
         "# TX-BATH2 — Candidate B — Copper wet walls / Cream floor"),
        ("This scheme retains the manufacturer wet-listed, originally quoted Copper tub surround and the Sandstone niche, and tests a *different* 12x24 matte porcelain floor from Daltile Portfolio instead of the scheduled Cortar Clay Soft with unknown wet DCOF.",
         "This scheme uses manufacturer wet-listed Copper tub walls and Sandstone niche with Daltile Portfolio Cream 12x24 matte porcelain floor. Cortar Clay Soft is also a priced reference in the project records, but its exact wet DCOF remains undocumented."),
        ("(FT5-replacement test)", "(FT5 floor)"),
        ("replaces 43.7 SF Cortar Clay Soft row", "43.7 SF per unit is the quantity in Cortar Clay Soft reference row"),
        ("current quoted Cortar Clay", "quoted Cortar Clay reference"),
        ("retained wall+niche", "wall+niche"),
        ("**Gate verdict:** DCOF", "**Gate verdict:** DCOF"),
    ],
    "TX-BATH3/B.md": [
        ("# TX-BATH3 — Candidate B — Emerald with Ash Grey certified-intent floor and mosaic pan study",
         "# TX-BATH3 — Candidate B — Emerald / Ash Grey wet room"),
        ("Retain quoted **Tones Emerald** wet walls and **Tones Sandstone** niche, test Daltile Portfolio **Ash Grey PF05 matte 12x24** on main floor",
         "Specify quoted **Tones Emerald** wet walls and **Tones Sandstone** niche, and Daltile Portfolio **Ash Grey PF05 matte 12x24** on the main floor"),
        ("(FT3-replacement test)", "(FT3 floor)"),
        ("replaces Cortar Grey row", "compares to Cortar Grey reference row"),
        ("Current flooring allowance", "Flooring allowance"),
    ],
    "TX-BATH4/A.md": [
        ("# TX-BATH4 — Candidate A — Charcoal flat tub field / Soho Black wet niche",
         "# TX-BATH4 — Candidate A — Charcoal / Soho Black tub surround"),
        ("Remove unapproved **Clara Caviar** 2x8 niche tile and substitute manufacturer **Wet Areas-listed ELM Soho Black 2x10 Glossy**.",
         "Specify manufacturer **Wet Areas-listed ELM Soho Black 2x10 Glossy** for the tub niche. Clara Caviar is a separately quoted project reference with no published Wet Areas tag."),
        ("replaces Clara Tierra Madre Caviar 2x8", "within the separately quoted Clara Tierra Madre Caviar 2x8 quantity basis"),
        ("**not a resolved floor alternative**", "**floor certification still unresolved**"),
        ("(AT1 substitution)", "(AT1 niche)"),
        ("**Do not transfer** Clara's", "Clara's"),
        ("WT9 Bone Ribbed 24x48 optional accent", "WT9 Bone Ribbed 24x48 relief panel"),
        ("retain existing", "include"),
    ]
}
for rel, rules in replacements.items():
    room, letter = rel.split("/")
    path = ROOT / "rooms" / room / "board" / "round-002" / "candidates" / letter
    data = path.read_text(encoding="utf-8")
    for old, new in rules:
        data = data.replace(old, new)
    path.write_text(data, encoding="utf-8")
    print(rel, len(data))
