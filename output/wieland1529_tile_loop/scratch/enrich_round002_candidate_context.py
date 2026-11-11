"""Give every Round 002 scheme a comparable source and installation review scope."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
additional = {
    ("TX-BATH2", "C"): """

## Manufacturer, setting and sample evidence

This packet includes 2×20 glossy ELM Tones Copper on wet alcove walls and Sandstone in a recessed niche. The project handoff reports these Tones colors for wet areas, while physical lot, surface profile, joint geometry and wet-wall mounting instruction need final maker verification. The 12×24 Cortar Clay Soft floor product is listed in the same-project quote, but no published exact wet DCOF >=0.42 has been established; it cannot clear the board floor gate. Catalog finish wording, appearance and anti-slip class should not substitute for the required manufacturer value.

Wet-wall installation must stop at the actual tub flange, continue waterproofing behind the tile and use a compatible flexible sealant at all changes of plane. Niche sills must pitch toward the tub, with matching trim and waterproofed returns. Since the actual position of the niche, valves, door and window openings is not measured, wall cuts and grout lines must remain a dimensioned shop-drawing task. A 20-in horizontal stack over a 62.48-in drawn back wall leaves course/cut choices dependent on real joint/module dimensions.

**Cost and procurement:** The quoted tile rates originate in ELM's September 3 project quote. Stock/lead and Chicago-delivered pricing are not confirmed; wall and niche quantities should be reconciled on a net non-overlapping basis, then rounded to cartons with 15% waste applied once. The carried unit baseline is an allowance, excluding labor, mortar/grout, waterproofing, trim, tax and freight. Mock up Copper, Sandstone and Clay with chrome fittings and the owner-selected basin once known. No products are ordered or approved.
""",
    ("TX-BATH3", "A"): """

## Manufacturer, setting and sample evidence

Tones Emerald and Sandstone wall/niche colors are recorded in the project as Wet Areas-compatible. Cortar Grey 12×24 Soft on the level floor lacks an exact published wet DCOF >=0.42 from the checked maker sources, so the floor must fail the board gate pending evidence. The fact that ELM lists floor applications does not constitute a measured ANSI wet-DCOF certificate. Niche and field wall SF need explicit subtraction to avoid including a recess twice.

**Scope conflict:** The drawing-based geometry identifies a tub alcove whose tile begins at an assumed 18-in tub deck. The plumbing selection records a walk-in shower and 4-in tile-in square point drain. A shower would require a different full-height wall and a positively sloped pan, neither priced nor measured here. The 12×24 level-floor field cannot be assumed usable on four planes of point-drain fall. Resolve this technical scope against the correct 1529 model and owner-selected plumbing before calculating pan area.

**Layout and finish review:** The prior 5.10-ft rear wall and two 2.60-ft returns are assumptions, not 1529 verified geometry. Check Emerald 2×20 straight stack courses and cuts around black controls, glass or tub flange, waterproof recess returns and negative-space detailing. Choose a tonal Emerald grout with both Mapei Ultracolor Plus FA and CBP Prism equivalents only after physical samples. Confirm Chicago lot availability, exact quantities and box rounding against the September 3 ELM historical quote. Labor, trim, shower waterproofing, freight and tax remain unpriced.
""",
    ("TX-BATH4", "B"): """

## Manufacturer, setting and sample evidence

Flat ELM Cortar Charcoal 24×48 is Wet Areas-listed; the Bone Ribbed relief product's individual maker page is not. The current wall allocation includes an unquantified relief area. It is not a separate extra wall: if any relief enters the dry side of the design, its measured SF must be deducted from the Charcoal field. Clara Caviar has a quoted niche allowance but its individual listing lacks Wet Areas approval, so it cannot be released for tub-niche placement. The 12×24 Cortar Bone Soft bath floor likewise lacks a certified numeric wet DCOF >=0.42.

**Geometry and installation:** The owner corrected TX Bath 4 to a tub alcove. Use 5.0-ft back and two 2.54-ft returns as drawing-derived planning figures only. Tile begins at assumed tub deck and extends to 9-ft-3-in ceiling, but final layout requires real opening/niche dimensions and full-face cut elevations. Do not create an unsupported shower floor. For the 24×48 wall format, offset and lippage should follow manufacturer/installer restrictions; a zero-offset stack is a candidate, with confirmed corner returns and no narrow focal slivers. The dark Charcoal field must be physically reviewed with matte-white Hansgrohe faucet/trim and a corresponding grout/edge sample.

**Quote and supply limitations:** The quoted 89.8-SF wall, 44.3-SF floor and 8.63-SF niche allowances include 15% waste. Current Chicago lot availability, landed price, final trim and carton rounding are not confirmed. Cortar's historical September 2026 supplier terms include overseas lead and minimum-import restrictions. These are not current guarantees. The package remains a study and does not approve unlisted wet-wall relief or niche material.
"""
}
for (room, letter), addition in additional.items():
    path = ROOT / "rooms" / room / "board" / "round-002" / "candidates" / (letter + ".md")
    original = path.read_text(encoding="utf-8")
    if "## Manufacturer, setting and sample evidence" in original:
        raise RuntimeError("Already enriched " + str(path))
    path.write_text(original.rstrip() + "\n" + addition, encoding="utf-8")
    print(room, letter, "chars", len(original) + len(addition))
