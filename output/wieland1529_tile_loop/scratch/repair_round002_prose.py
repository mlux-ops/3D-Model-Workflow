"""Final standalone candidate descriptions for blind Round 002 review."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
for room, letter, title in (
    ("TX-BATH2", "B", "Copper tub walls / Cream floor"),
    ("TX-BATH3", "B", "Emerald / Ash Grey bathroom"),
    ("TX-BATH4", "A", "Charcoal / Soho Black tub alcove"),
):
    path = ROOT / "rooms" / room / "board" / "round-002" / "candidates" / (letter + ".md")
    content = path.read_text(encoding="utf-8").splitlines()
    content[0] = "# " + room + " — Candidate " + letter + " — " + title
    if room == "TX-BATH2":
        content[2] = ("**Round 002 / per Triplex unit; two units.** Specify manufacturer wet-listed ELM Tones Copper wet tub walls, "
                      "Tones Sandstone niche and Daltile Portfolio Cream 12×24 matte porcelain bath floor. "
                      "Cortar Clay Soft provides a historical project price comparison; its wet DCOF is not documented. "
                      "**Hard-gate FAIL:** exact Cream floor DCOF measurement and project quote are pending.")
        content[7] = content[7].replace("**38 SF prior unverified net, 43.7 SF gross** 43.7 SF per unit is the quantity in", "**38 SF prior unverified net / 43.7 SF gross** from").replace("ELM carry", "ELM project reference")
        content[8] = content[8].replace("| Existing niche back/returns", "| Niche back/returns").replace("Existing **8.63 SF gross**", "**8.63 SF gross**")
    elif room == "TX-BATH3":
        content[2] = content[2].replace("**Important existing conflict:**", "**Source conflict:**")
        content[9] = content[9].replace("| Existing niche (AT2)", "| Niche (AT2)")
    else:
        content[2] = ("**Round 002 / per Triplex unit; two units.** Specify manufacturer Wet Areas-listed ELM Soho Black 2×10 "
                      "glossy tub niche, Cortar Charcoal 24×48 Soft flat tub walls, and Cortar Bone 12×24 Soft main bath floor. "
                      "Clara Caviar is a separately quoted project reference without a Wet Areas listing. Bone Ribbed relief may "
                      "only be considered in a measured dry area until product-specific wet-wall approval exists. "
                      "**Hard-gate FAIL:** floor wet DCOF and geometry unverified.")
        content[7] = content[7].replace("| Existing tub-niche back and returns", "| Tub-niche back and returns")
        content[8] = content[8].replace("Retain ELM", "ELM")
        content[9] = content[9].replace("Within wet enclosure replace all proposed Ribbed with the already covered Charcoal field", "Wet enclosure uses flat Charcoal field only")
    path.write_text("\n".join(content) + "\n", encoding="utf-8")
    print(room, letter, len(content))
