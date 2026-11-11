# TX-BATH2 — R027 independent DESIGN replacement

**Scope:** Independent design-seat comparison of neutral candidates A and B. This report does not assign a private mapping, score other seats, or accept a candidate.

**Preserved room state:** Duravit Starck tub; Hansgrohe Chrome; basin UNSELECTED; no tiled shower pan. The basin remains unselected, so no basin-faucet finish or basin-form judgment is assumed. The tub and shower hardware are the relevant visible plumbing context. [plumbing.json:9-22,41-54,57-86,185-194] [A.md:3] [B.md:3]

## Six design criteria (1–5)

| Criterion | Candidate A | Candidate B |
|---|---|---|
| **1. Plumbing-finish harmony** | **4.0** — Copper is a warm contrast to the room's Chrome hardware; Chrome is neutral enough to mediate it, though the palette is not a direct tonal match. [A.md:3,6] [plumbing.json:41-54] | **4.5** — Sapphire's cooler blue reads more directly with Chrome; the warm Sandstone niche and beige floor keep the room from becoming uniformly cool. [B.md:3,6-7] [plumbing.json:41-54] |
| **2. Palette and material composition** | **4.4** — Copper, Sandstone and ivory Luxe Sand form a restrained warm composition. The official floor image is low-contrast ivory with a quiet concrete-look face, which gives the glossy wall tile visual priority. [A.md:6-8] [F&D Luxe Sand product page](https://www.flooranddecor.com/porcelain-tile/luxe-sand-matte-porcelain-tile-101317949.html) | **4.1** — Sapphire against Sandstone and beige Riviera Oat gives a deliberate high-contrast focal wall. The travertine-look floor adds visible linear variation; the strong blue may dominate a 38-SF bath. [B.md:6-8] [F&D Riviera Oat product page](https://www.flooranddecor.com/porcelain-tile/riviera-oat-matte-porcelain-tile-101487775.html) |
| **3. Scale and proportion** | **4.3** — The 24x24 floor is still large format and is the more proportionate starting point for the 38-SF drawing-derived room. The actual room dimensions and entry orientation remain unverified. [A.md:8,13] [geometry.json:11-18,145-160] | **3.7** — The 24x48 floor meets the large-format priority and reduces joint count, but its long proportion could dominate this small room; orientation and perimeter cuts cannot be judged from the unverified 38-SF area alone. [B.md:8,13] [geometry.json:11-18] [OWNER_FEEDBACK.md:53-57] |
| **4. Layout and grout rhythm** | **3.7** — The horizontal 2x20 wall stack contrasts usefully with the square floor. The proposed 1/8-in joint has no selected grout color, and the actual wall setout is absent. [A.md:6,14] [geometry.json:27-62] | **3.6** — The horizontal wall stack and linear travertine-look floor may create a strong directional rhythm; the 24x48 setout, 1/3-offset limit, grout color and perimeter cuts are not demonstrated. [B.md:6,8,14] [F&D Riviera Oat product page](https://www.flooranddecor.com/porcelain-tile/riviera-oat-matte-porcelain-tile-101487775.html) |
| **5. Niche and wet-wall composition** | **4.2** — Sandstone repeats the wall module in a warmer, quieter niche treatment and keeps the alcove composition cohesive. Niche dimensions, edge profile and actual opening are unknown. [A.md:6-7,13-14] [geometry.json:56-62] [R027_TX_BATH2_BLIND_PRODUCT_EVIDENCE.md:4-11] | **4.0** — The same Sandstone module gives the saturated Sapphire wall a distinct warm recess. The contrast could be effective, but the niche opening and trim resolution are unverified. [B.md:6-7,13-14] [geometry.json:56-62] [R027_TX_BATH2_BLIND_PRODUCT_EVIDENCE.md:4-11] |
| **6. Competitive character** | **4.0** — The restrained warm treatment can read as considered and premium. The cited Old Town sales establish a high-end bath program, but the comp file does not verify tile colors, layouts or metal finishes, so no specific visual precedent is claimed. [A.md:15] [COMPS.md:24-30,46,54] | **4.1** — Riviera Oat's travertine look has a modest connection to the natural-stone bath language marketed at 1942 N Orchard; Sapphire supplies a stronger point of distinction. The comps do not establish blue tile or a particular layout as a market precedent. [B.md:8,15] [COMPS.md:30,42,46,54] |

## Arithmetic means

- **A:** (4.0 + 4.4 + 4.3 + 3.7 + 4.2 + 4.0) / 6 = **4.1** (24.6 / 6).
- **B:** (4.5 + 4.1 + 3.7 + 3.6 + 4.0 + 4.1) / 6 = **4.0** (24.0 / 6).

## Top fix

- **A:** Produce a dimensioned horizontal 2x20 wall setout using verified W1 length and actual openings/niche location; resolve the possible narrow focal end cut before fixing the stack start and edge treatment.
- **B:** Produce a dimensioned 24x48 floor setout aligned to the verified entry and tub, with perimeter cuts and the permitted offset shown; include the shared 2x20 wall setout in the same coordinated layout.

## Gate flags

- **Geometry — unresolved for both; potential hard-gate issue, not a confirmed failure.** W1 is currently 5.207 ft (about 62.5 in), drawing-derived/assumed and not live-Revit verified. If the 20-in side of the horizontal wall tile runs across that length, three nominal lengths total 60 in and leave about 2.5 in before grout and end cuts. That may create a focal piece below the board's 3-in threshold. Confirm the actual tile dimension, wall length, openings and niche, then show a layout that resolves it. The floor dimensions and focal perimeter cuts are also unverified. [geometry.json:27-62,65-98,101-134,171-179] [A.md:13-14] [B.md:13-14] [BOARD.md:58-60]
- **Wet-use — supported by the room-local evidence.** Both exact Elm wall and niche products are individually listed for Wet Areas WALL. Luxe Sand and Riviera Oat are listed for Bathroom Floor and each publishes wet DCOF >=0.42. The room is a tub bath; tiled shower-pan criteria are N/A. [R027_TX_BATH2_BLIND_PRODUCT_EVIDENCE.md:3-19] [F&D Luxe Sand product page](https://www.flooranddecor.com/porcelain-tile/luxe-sand-matte-porcelain-tile-101317949.html) [F&D Riviera Oat product page](https://www.flooranddecor.com/porcelain-tile/riviera-oat-matte-porcelain-tile-101487775.html)
- **Availability — local confirmation pending, no discontinuation failure established.** F&D pages are live and list the SKUs, but the room-local evidence says Chicago matching lot, cartons and ETA are unknown; Elm Chicago stock/lot also remains unconfirmed. [R027_TX_BATH2_BLIND_PRODUCT_EVIDENCE.md:17,20]
- **Plumbing / owner veto — no confirmed failure.** Both schemes retain Chrome and the selected Duravit tub; the basin stays unselected. The owner feedback's Do not use list contains no product veto. [plumbing.json:9-22,41-54,185-194] [OWNER_FEEDBACK.md:13-16,53-62]

**Confidence:** Medium. The product identities, published finish/application data and comparative product appearance are documented. The judgment is limited by unverified live room dimensions, missing niche/opening measurements, absent grout/edge selections and unconfirmed Chicago stock. Board design scope and hard gates: [BOARD.md:12-15,33-61].
