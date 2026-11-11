# R036 independent BUILD critique — TX-BATH3

Seat: BUILD (tile installer / GC; weight 0.25). Blind review of only R036 neutral A/B. **Prior selection role, incumbent, previous score or other critic evidence seen: NONE.** Five individual integer 1–5 ratings for each scheme, with arithmetic seat mean HALF_UP rounded to one decimal.

Room evidence: `rooms/TX-BATH3/geometry.json` (207A/207B; 5.10-ft W1, two 2.60-ft returns, 7.75-ft assumed tiled height, 37-SF LEVEL area; openings/niche/substrate/drain location not measured), `rooms/TX-BATH3/plumbing.json` (Brizo Brilliance Black Onyx BT062415-BNX POINT drain recorded), and current R036 neutral A/B. **Owner TUB/WALK-IN unresolved** despite older plumbing notes assuming a shower; the latest owner rule controls. Original gross WALL 91.8 SF, NICHE pool 4.89 SF, **bathroom LEVEL only** 42.5 SF per copy, with original 15% waste already counted once; two copies. For a later WALK-IN, independent PAN SF and price **NULL** pending measurement; for a TUB, PAN N/A and BNX POINT is never tub waste.

## Candidate A — La Belle Antique Blue wet wall / La Belle Purity niche / Luxe Sand LEVEL

1. **Substrate flatness and setting — 4/5:** [La Belle Antique Blue 3x12 pressed 8.5 mm](https://www.flooranddecor.com/ceramic-tile/la-belle-antique-blue-high-gloss-ceramic-tile-100507706.html) uses smaller, readily cut wall modules; [Luxe Sand 24x24, 8 mm](https://www.flooranddecor.com/porcelain-tile/luxe-sand-matte-porcelain-tile-101317949.html) still requires measured level substrate flatness and compatible shower/wet-floor assembly (`geometry.json`).
2. **Lippage, offset and joints — 4/5:** Maker lists 1/16-in grout for pressed La Belle wall tile, giving an explicit basis for detailing its 3x12 modules across assumed 61.2-in W1 and 31.2-in returns, subject to site-measured edge and opening setouts ([La Belle Antique Blue](https://www.flooranddecor.com/ceramic-tile/la-belle-antique-blue-high-gloss-ceramic-tile-100507706.html)).
3. **LEVEL/PAN slope and wet suitability — 4/5:** [Luxe Sand](https://www.flooranddecor.com/porcelain-tile/luxe-sand-matte-porcelain-tile-101317949.html) independently lists Bathroom Floor YES, Shower Floors YES and DCOF >=0.42; 24x24 is an accommodating size for a conditional four-plane BNX POINT PAN, though actual slope/drain cut diagram must await the owner's WALK-IN choice and field measurements.
4. **Cuts, edges and niche assembly — 3/5:** [La Belle Purity 3x12](https://www.flooranddecor.com/ceramic-tile/la-belle-purity-high-gloss-ceramic-tile-100507722.html) lists Shower Walls YES, Shower Floors NO; small pieces support tight vertical niches but actual niche/sill/valve and threshold measurements, horizontal waterproof assembly and >=3-in edge cuts remain unverified (`geometry.json`, `plumbing.json`).
5. **Waste, sequencing and schedule — 3/5:** Original 91.8/4.89/42.5 gross SF pools include historical 15% just once; 3x12 wet wall has more tile handling and grout joints than large-format, while all F&D cited rates were 2026-11-07 out-of-state retail, without verified Chicago matched lot/ETA (R036 A).

**BUILD seat mean: (4 + 4 + 4 + 3 + 3) / 5 = 3.6 (HALF_UP, one decimal).**

**top_fix:** Set a measured 3x12 wall/niche pattern with 1/16-in maker joint, a complete pitched/waterproof niche sill, exact BNX penetrations and field-confirmed >=3-in edges; resolve TUB/WALK-IN before any separate PAN cut sheet.

**gate_flags:** No documented tile **application/DCOF** failure: La Belle wall+niche are individually Shower Walls YES, explicitly **not shower floor** materials; Luxe Sand independently lists Shower Floors YES and DCOF >=0.42. **FIELD/OWNER HOLD (not proved gate failure):** owner TUB/WALK-IN decision, niche/sill waterproof assembly, cutting and point-drain geometry, plus optional PAN SF/cost **NULL**. No ceiling tile scheduled.

**confidence:** medium for direct tile use; low for setout and conditional pan.

## Candidate B — Elm Tones Emerald wet wall / La Belle Purity niche / Pienza Terra LEVEL

1. **Substrate flatness and setting — 4/5:** [Emerald Tones 2x20 8.5 mm](https://www.elmsurfaces.com/product/emerald-tones) is a manageable modular wet-wall tile and maker-listed for Walls/Wet Areas; the [Pienza 24x48 rectified 9-mm floor](https://www.flooranddecor.com/porcelain-tile/pienza-terra-matte-porcelain-tile-110850387.html) demands measured large-format subfloor flatness and suitable setting mortar, still unverified (`geometry.json`).
2. **Lippage, offset and joints — 3/5:** The glossy 2x20 elongated Elm wall and 3x12 pressed [La Belle Purity](https://www.flooranddecor.com/ceramic-tile/la-belle-purity-high-gloss-ceramic-tile-100507722.html) niche have different module sizes and require a deliberate stack/offset, grout and trim interface; Elm's product page does not state a verified project joint or offset, and the 7.75-ft height is assumed.
3. **LEVEL/PAN slope and wet suitability — 3/5:** [Pienza 23.59x47.30 actual](https://www.flooranddecor.com/porcelain-tile/pienza-terra-matte-porcelain-tile-110850387.html) independently lists Shower Floors YES, Bathroom Floor YES and DCOF >=0.42; a 24x48 four-plane cut at a four-inch BNX POINT is feasible only after a field-based map and rough-drain elevation, and only **if WALK-IN is selected**; it is not automatically a floor failure.
4. **Cuts, edges and niche assembly — 3/5:** Emerald maker lists Walls/Wet Areas and La Belle Purity lists Shower Walls YES, both suitable for vertical work, but the two widths need corner/edge detailing and an independently waterproofed and pitched horizontal niche sill; `geometry.json` lacks niche, penetrations, thresholds and >=3-in cut proof.
5. **Waste, sequencing and schedule — 3/5:** Elm Emerald has a 2026-09-04 actual-job $6.95/SF quote (`inputs/TRADE_QUOTES.md`), while Pienza and La Belle prices are out-of-state F&D retail; historical 15% in 91.8/4.89/42.5 SF must not be doubled, and current Chicago delivery/lot, eventual POINT-PAN waste and cartons remain unresolved.

**BUILD seat mean: (4 + 3 + 3 + 3 + 3) / 5 = 3.2 (HALF_UP, one decimal).**

**top_fix:** Field-confirm the owner wet-fixture type, prepare BNX square-drain 24x48 four-plane cuts with >=3-in edge pieces if WALK-IN, and issue the Elm 2x20/La Belle 3x12 vertical-niche trim and pitched sill detail.

**gate_flags:** No documented tile **application/DCOF** hard-gate failure: Emerald lists Walls/Wet Areas; La Belle Purity Shower Walls YES; Pienza independently Shower Floor YES with DCOF >=0.42. **FIELD/OWNER HOLD (not a proved failure):** actual pan geometry and optional PAN quantity/price **NULL**, tub/walk-in decision, waterproof niche, measured edges/flatness and matched Chicago lot. BNX shower drain is **not** a tub waste substitution; no ceiling tile.

**confidence:** medium for product applications, low for field cut and drain geometry.
