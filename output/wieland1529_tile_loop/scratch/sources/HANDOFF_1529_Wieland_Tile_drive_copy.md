<!-- Read-only working copy of Google Drive file 12gJwYBe70RT8xjwjp9jpzBwvPad1iiMS, fetched 2026-11-06; source: 1529 tile handoff. -->
# HANDOFF — 1529 N Wieland St, tile selection
Written 2026-08-23, updated after the Smartsheet Qty write. Read this first, then project memory.

---

## 1. WHY A NEW CHAT
The pyRevit MCP server (`revitmcp`) now runs correctly in Claude Desktop, but it did NOT appear in the
previous Cowork session's tool list — that session spawned its server set before the server worked.
A new session should spawn its own copy at startup and pick it up. **First action in the new chat:
check whether `revitmcp` tools are available.** If they are, the wet-zone measurements below can be
replaced with exact model figures, which is the single biggest remaining accuracy gain.

If they still do not appear: the workaround that already worked is to run the query inside Claude
Desktop (where the tools do work) and paste the output back. Note Apify has the same symptom — it runs
in the desktop app and never appears in Cowork — so this may be a standing limitation, not a bug.

---

## 2. PROJECT IDENTITY
- **Project 25-006, 1529 N Wieland St, Chicago IL 60610.** Some files say 1527; every title block says 1529.
- Building: **2 x Penthouse** (3rd + 4th floors — the drawings call these DUPLEX) and **2 x Triplex**
  (Lower + 1st + 2nd). Per Max, always use the Smartsheet names: **Penthouse and Triplex.**
- Smartsheet **"FINISH DATABASE - 1529 Wieland"**, sheet id `8569278453206916`. Tile cost code
  `09 30 Tile - M`. Plumbing is `11 45 Plumbing Fixtures M`.
- Governing drawings: issue **2026.08.07, permit 101086781** (confirmed by Max). An older set exists in
  Drive at permit 101071048 dated 2026.04.13 — superseded.
- Vendor: **Studio 41, Edwin Colon, edwinc@studio41.com**.

---

## 3. MAX'S TILE RULES — FINAL. Do not re-derive these.
1. Wall tile **only within the confines of a shower or tub**.
2. Showers: tiled **floor to ceiling**.
3. Tub alcoves: tile starts **at the tub deck** — no tile on the band behind the apron. Default deduction 1.5 ft (18 in.).
4. Ceilings: **only the primary SHOWER ceilings**, not whole bathroom ceilings.
5. **Powder rooms: the vanity wall is a feature wall, tiled full height floor to ceiling.**
6. Freestanding tubs get **no surround**.
7. **Powder rooms have NO tile floor.** Vanity feature wall only. The floor is the unit's **wood floor,
   not in the tile scope**. (Max, 2026-08-23.)
8. **Toilet / WC rooms get floor tile only** — no wall tile (313A/B Penthouse 15 SF, 203A/B Triplex 14 SF).
   There is **no distinction between bathroom floor tile and WC floor tile — always the same tile**, so
   in the Smartsheet the WC SF is added into the adjoining Primary Bath floor row, not a separate line.
9. **Accent tile is always inside a niche.** Niche locations are not confirmed, so **no accent quantity exists**.
   Accent rows carry tile name, image and price only. When niches are fixed, accent SF comes **out of** the
   wall field, not in addition to it.
10. **Waste factor 15%.**

Grout: **one coordinated colour per tile, expressed in BOTH Mapei Ultracolor Plus FA and CBP Prism**,
because SHB uses both. Joint under 1/8 in. takes unsanded. Primary showers need epoxy or
single-component grout.

**Do not raise the steam topic.** Max said not to mention it until he brings it up.

---

## 4. CURRENT DELIVERABLE
`1529_Wieland_Tile_Takeoff_v7.xlsx` — four tabs: README & Inputs, Take-Off, Grout Schedule,
Assumptions & Gaps. All formulas live; recalc clean, zero errors (86 formulas).

**Building total 2,910.4 SF including 15% waste.** Penthouse set 1,454.8 SF, Triplex set 1,455.6 SF.

Revision history so the numbers are not re-litigated:
| Rev | Model | Total SF | Why superseded |
|---|---|---|---|
| v1 | All walls, full height | 7,116 | Wrong — tile is not on all walls |
| v2 | Wet-zone walls full height, whole primary ceilings | 3,284 | Tub apron and ceiling scope wrong |
| v3 | Tub from deck, shower ceilings only, powder feature walls | 2,989 | Floor areas were PDF-scaled |
| v4 | Same rules, floor areas from Revit, WCs excluded | 2,924 | WCs should have had floor tile |
| v5 | WCs added back, floor tile only, 10% waste | 2,988 | Powder floors were tiled; waste was 10% |
| v6 | Powder floors removed, 15% waste | 2,945 | TX Bath 4 was modelled as a walk-in shower |
| **v7** | **TX Bath 4 corrected to a tub alcove** | **2,910** | **current** |

### Smartsheet state — DONE
All 22 Qty values are written into the TILES section of sheet `8569278453206916`.
Qty is **per unit**; the column formulas double it. Values written (per unit, 15% waste):

| Room | Wall | Floor | Vanity wall |
|---|---|---|---|
| PH Primary | 143.0 | 135.6 (incl. WC 17.2) | — |
| PH Bath 2 | 89.7 | 40.2 | — |
| PH Bath 3 | 86.2 | 40.2 | — |
| PH Bath 4 | 107.2 | 40.2 | — |
| PH Powder | — | none | 44.9 |
| TX Primary | 134.4 | 116.1 (incl. WC 16.1) | — |
| TX Bath 2 | 92.8 | 43.7 | — |
| TX Bath 3 | 91.8 | 42.5 | — |
| TX Bath 4 | 89.8 | 44.3 | — |
| TX Powder | — | none | 31.8 |
| TX Powder 2 | — | none | 40.5 |

Still blank on those rows, on purpose: **Accent Tile Qty** (niches unconfirmed), **Actual Unit Cost**
(no selected tile; the only figure is $12.09/SF back-solved from the $37,761.80 allowance, which is not
a real rate), and **Image** (the Smartsheet API cannot set cell images — needs the UI or Chrome).

Only these columns may be written on tile rows, per Max: **Primary Column, Image, Actual Unit Cost, Qty.**
`Cost of Good Sold` is a COLUMN FORMULA — writing to it returns error 1302.

## 5. ROOM SCHEDULE (per unit, x2 each)

| Unit | Room | Revit ID | Floor SF | Source |
|---|---|---|---|---|
| Penthouse | Primary Bath | 304A/B | 103 | Revit |
| Penthouse | Bath 2 | 305A/B | 35 | Revit |
| Penthouse | Bath 3 | 307A/B | 35 | Revit |
| Penthouse | Bath 4 | 311A/B | 35 | **Max** (Revit says 27 — see §7) |
| Penthouse | Powder | 405A/B | 28 | Revit |
| Triplex | Primary Bath | 202A/B | 87 | Revit |
| Triplex | Bath 2 | 205A/B | 38 | Revit |
| Triplex | Bath 3 | 207A/B | 37 | Revit |
| Triplex | Bath 4 | 007A/B | 38.5 | Revit |
| Triplex | Powder 2 | 009A/B | 27 | Revit |
| Triplex | Powder | 102A/B | 22.5 | Revit |
| Penthouse | Toilet (WC) | 313A/B | 15 | Revit — **floor tile only** |
| Triplex | Toilet (WC) | 203A/B | 14 | Revit — **floor tile only** |

Ceiling height **9'-3"**, confirmed on seven elevation sheets.

---

## 6. WHAT IS STILL DRAWING-DERIVED (the next job)
Floor areas are solid. **Every wet-zone dimension is not.** These drive all 791 SF of wall tile:

| Room | Zone | W x D (ft) | Tiled wall LF |
|---|---|---|---|
| PH Primary | Corner shower | 5.854 x 4.646 | 10.50 |
| PH Bath 2 | Tub alcove | 4.958 x 2.55 | 10.06 |
| PH Bath 3 | Tub alcove | 5.0 x 2.33 | 9.67 |
| PH Bath 4 | Walk-in shower | 5.0 x 2.54 | 10.08 |
| PH Powder | Vanity wall | — | 4.224 (low confidence) |
| TX Primary | Corner shower | 5.1875 x 4.7708 | 9.96 |
| TX Bath 2 | Tub alcove | 5.207 x 2.60 | 10.41 |
| TX Bath 3 | Tub alcove | 5.10 x 2.60 | 10.30 |
| TX Bath 4 | Walk-in shower | 5.0 x 2.54 | 10.08 |
| TX Powder 2 | Vanity wall | — | 3.806 |
| TX Powder | Vanity wall | — | 2.990 (verify — doubles if the vanity runs the long wall) |

Primary shower volumes cross-check against Max's own steam figures: TX 24.8 SF x 9.25 = 229 cf
(he said 231), PH 26.9 SF x 9.25 = 249 cf (he said 250). Good corroboration.

---

## 7. OPEN ITEMS
1. **Tile selected, not written.** Tile Schedule v4 names a product for every row (§7b), but the Smartsheet cells are still empty and Elm publishes no prices. Six conflicts in §7b must be closed first.
2. **Wet-zone dims from Revit** — highest-value remaining query.
3. **PH Bath 4 discrepancy.** Max: 7'-0" x 5'-0" = 35 SF. Revit: 27 SF / 20.79 ft perimeter, which solves
   to a clean 5'-0" x 5'-5" rectangle. Using 35. The Revit room object looks drawn short of a wall face.
4. **Tub deck heights** — 1.5 ft assumed everywhere. Duravit Starck 700332 is ~18 1/8 in.; the Bath 3 tub
   models are unconfirmed.
5. **Powder vanity wall lengths** — see table above.
6. **Model data quality**: room `213A` is used twice (TOILET 134 SF and PRIMARY WIC 40 SF — the 134 is
   clearly wrong); same duplication on `011A` and `001A`; about a dozen rooms return blank areas
   (unplaced/unbounded), including a second `202A PRIMARY BATH`.
7. **203A is unplaced** in the Revit model and returns no area; 203B's 14 SF is used for both. Room `007D` on the 2nd floor reports an identical 14 SF / 15.67 ft and may be the mislabelled 203A — worth checking.
8. **Powder 2 sink** still has no product (audit item F13). Pairs with Hansgrohe Tecturis E 73072341 Brushed Black Chrome.
9. **Powder 2 hardware** — Max is swapping the Logis 5-piece set himself. Do not touch.
10. **Powder floor finish — RESOLVED.** Wood, same as the rest of the unit. Not in the tile scope.
11. **Job Numbers column** — "25-006 1529 Wieland" was added to the Smartsheet picklist, but the rows were
   never bulk-updated; they still read "23-002 640 W Webster". Blocked in-session; Max may do it in the UI.

---

## 7b. TILE SELECTIONS — Tile Schedule v4 (Max, 2026-08-23)
Source: `tile_schedule_v4_2.html`. Vendor **Elm Surfaces**. Four collections: **Cortar** (limestone-tone
porcelain, wet-rated, Reed and Ribbed 3D faces, Anti-Slip variant), **Tones** (2"x20" glossy sticks,
wet-rated, quick-ship), **Vera Forma** (relief ceramic, walls only), **Haze** (matte kit-kat, walls only),
plus one **Clara** zellige. Elm publishes no prices — the whole schedule needs a showroom quote.

### Master list
Revised 2026-08-23 per Max: no powder floor tile; WC floor = the adjoining bathroom floor, same tile;
anti-slip covers the WHOLE floor of any room that referenced it.

| Code | Product | Format | Used in |
|---|---|---|---|
| FT1 | Cortar Bone, **Anti-Slip** | 24"x48" | PH Primary floor — whole floor incl. WC 313A/B |
| FT2 | Cortar Clay, **Anti-Slip** | 24"x48" | TX Primary floor — whole floor incl. WC 203A/B |
| FT3 | Cortar Grey, Soft | 12"x24" | PH Bath 2, TX Bath 3 floors |
| FT4 | Cortar Bone, Soft | 12"x24" | PH Bath 3, TX Bath 4 floors |
| FT5 | Cortar Clay, Soft | 12"x24" | TX Bath 2 floor |
| FT6 | Cortar Charcoal, **Anti-Slip** | 12"x24" | PH Bath 4 floor — whole floor (confirm Charcoal Anti-Slip) |
| WT1 | Cortar Bone | 24"x48" | PH Primary shower walls + ceiling |
| WT2 | Cortar Bone Reed (fluted 3D) | per catalog | PH Primary texture wall — same line, texture only |
| WT3 | Cortar Clay | 24"x48" | TX Primary shower walls + ceiling |
| WT4 | Cortar Clay Ribbed (3D) | per catalog | TX Primary texture wall — same line, texture only |
| WT5 | Tones Sapphire, glossy | 2"x20" stacked | PH Bath 2 tub walls |
| WT6 | Tones Opal, glossy | 2"x20" stacked | PH Bath 3 tub walls |
| WT7 | Tones Copper, glossy | 2"x20" stacked | TX Bath 2 tub walls |
| WT8 | Tones Emerald, glossy | 2"x20" stacked | TX Bath 3 tub walls |
| WT9 | Cortar Bone Ribbed (3D) | per catalog | PH Bath 4 shower walls |
| WT10 | Cortar Charcoal | 24"x48" | TX Bath 4 tub alcove field walls |
| WT9 | Cortar Bone Ribbed (3D) | per catalog | ALSO TX Bath 4 accent — Max 2026-08-23 |
| WT11 | Vera Forma Earth Lines (relief) | 2"x10" | PH Powder feature wall |
| WT12 | Haze Camel + Wheat mix, matte | 1.6"x5" stacked | TX Powder feature wall |
| WT13 | Vera Forma Indigo Edge (relief) | 6"x6" | TX Powder 2 feature wall |
| AT1 | Clara Caviar zellige, black | 2"x8" | PH + TX Bath 4 niche bands |
| AT2 | Tones Sandstone, glossy | 2"x20" | PH/TX Bath 2 + 3 niche backs |

Codes **SF1 and SF2 are retired.** The v4 schedule used them for anti-slip shower pans only. Anti-slip now
runs the whole floor in those rooms, so the pan is not a separate product.

**Powder floors carry no tile.** They take the unit's wood floor. FT5 and FT3 no longer appear in PH Powder,
TX Powder or TX Powder 2.

**WC floors are the adjoining bathroom floor, same tile.** Both WCs are notched out of the Primary baths
(313A/B out of PH Primary, 203A/B out of TX Primary), so they take FT1 and FT2. Their SF stays inside the
Primary Floor rows in the Smartsheet — no separate line, no separate product.

### Smartsheet row map — what goes in Primary Column
Sheet `8569278453206916`. **Nothing below is written yet.**

| Row ID | Row | Tile |
|---|---|---|
| 4302621473570692 | PH Primary Wall | WT1 Cortar Bone 24"x48", WT2 Bone Reed on the texture wall |
| 2715002737917828 | PH Primary Floor | FT1 Cortar Bone Anti-Slip 24"x48" |
| 6554421287255940 | PH Primary Accent | none — no niche in the schedule |
| 8806221100941188 | PH Bath 2 Wall | WT5 Tones Sapphire |
| 221234311266180 | PH Bath 2 Floor | FT3 Cortar Grey |
| 7218602365288324 | PH Bath 2 Accent | AT2 Tones Sandstone |
| 4724833938636676 | PH Bath 3 Wall | WT6 Tones Opal |
| 2473034124951428 | PH Bath 3 Floor | FT4 Cortar Bone |
| 1589102831075204 | PH Bath 3 Accent | AT2 Tones Sandstone |
| 6976633752321924 | PH Bath 4 Wall | WT9 Cortar Bone Ribbed |
| 1347134218108804 | PH Bath 4 Floor | FT6 Cortar Charcoal Anti-Slip 12"x24" |
| 6092702458445700 | PH Bath 4 Accent | AT1 Clara Caviar |
| 5850733845479300 | PH Powder Floor | **NO TILE — wood floor, out of scope. Qty cleared.** |
| 6851772612214660 | PH Powder Vanity Wall | WT11 Vera Forma Earth Lines |
| 8102533659164548 | TX Primary Wall | WT3 Cortar Clay 24"x48", WT4 Clay Ribbed on the texture wall |
| 784184264687492 | TX Primary Floor | FT2 Cortar Clay Anti-Slip 24"x48" |
| 3840902644760452 | TX Primary Accent | none — no niche in the schedule |
| 3035984078372740 | TX Bath 2 Wall | WT7 Tones Copper |
| 7539583705743236 | TX Bath 2 Floor | FT5 Cortar Clay |
| 8344502272130948 | TX Bath 2 Accent | AT2 Tones Sandstone |
| 6413683798900612 | TX Bath 3 Wall | WT8 Tones Emerald |
| 4161883985215364 | TX Bath 3 Floor | FT3 Cortar Grey |
| 1026152877653892 | TX Bath 3 Accent | AT2 Tones Sandstone |
| 502709287976836 | TX Bath 4 Wall | WT10 Cortar Charcoal field + WT9 Cortar Bone Ribbed accent |
| 5006308915347332 | TX Bath 4 Floor | FT4 Cortar Bone |
| 5529752505024388 | TX Bath 4 Accent | AT1 Clara Caviar |
| 4966802551603076 | TX Powder Vanity Wall | WT12 Haze Camel + Wheat |
| 7258108729032580 | TX Powder 2 Vanity Wall | WT13 Vera Forma Indigo Edge |

There are **8 Accent Tile rows**. The two Primary accent rows have no product in this schedule.

Texture walls (WT2, WT4, and the optional Reed wall in TX Bath 4) are the **same line in a different face**.
They sit inside the wall Qty. No split is needed and no extra SF is added.

### ANTI-SLIP AVAILABILITY — CHECKED IN THE CATALOG 2026-08-23
Source: **Cortar Catalog PDF**, `elmsurfaces.com` → Cortar → SPEC SHEET / CATALOG, page 3 table
"Porcelain Tiles Available Sizes & Finishes". The product pages list sizes and finishes as two flat
lists and do NOT say which finish comes in which size. The catalog table does.

| Nominal size | Inch size | Soft Textured C2·R10·CB | Anti-Slip C3·R11·CC |
|---|---|---|---|
| 30x60 cm | 12"x24" | yes | **yes** |
| 60x60 cm | 24"x24" | yes | **yes** |
| 45x90 cm | 18"x36" | yes | **yes** |
| 90x90 cm | 36"x36" | yes | **yes** |
| **60x120 cm** | **24"x48"** | yes | **YES** |
| 120x120 cm | 48"x48" | yes | **yes** |
| 120x270 cm | 48"x106" | yes | no |

**24"x48" Anti-Slip exists** — 59,8x119,8x0,9 cm, price code 62, 2 pc/box, 1.43 m²/box.
Anti-slip runs across every size except the 48"x106" slab.

**Result: both Primary flags close.** The floors keep the 24"x48" format and change finish only —
a texture change, nothing else.
- PH Primary floor → **Cortar Bone, Anti-Slip, 24"x48"**
- TX Primary floor → **Cortar Clay, Anti-Slip, 24"x48"**
- PH Bath 4 floor → **Cortar Charcoal, Anti-Slip, 12"x24"** (same size as the v4 field, finish only)

The catalog prints the colour range — **Bone, Grey, Clay, Terra, Charcoal** — against the whole
Color Body Porcelain range with **no per-colour finish exclusion**. So Charcoal Anti-Slip should exist.
The catalog does not carry a colour x finish grid, so confirm Charcoal Anti-Slip on the order.

### TX BATH 4 — Bone Ribbed accent on the Charcoal field
Catalog page 4, "Ductile Reliefs 60x120": **Reed and Ribbed come in Bone, Clay and Terra only** — there
is no Charcoal relief. Max 2026-08-23: **run Cortar Bone Ribbed (WT9) as an accent on the Cortar
Charcoal (WT10) field.** Ribbed, not the Reed the v4 text suggested.

WT9 Bone Ribbed is now used twice — PH Bath 4 shower walls and the TX Bath 4 accent. One relief SKU
covers both, which helps the order.

**No quantity split is carried.** Accent SF is not known, and an accent does not take a whole wall as a
rule. The TX Bath 4 Wall row holds the full wet-zone Qty; the Bone Ribbed area comes OUT of it once the
accent is sized. Do not add SF for it.

### TX BATH 4 IS A TUB — CORRECTED 2026-08-23
Max confirmed 007A/B has a **tub**, not a walk-in shower. The take-off had it as a walk-in shower with
full-height tile. Tile now starts at the tub deck, 1.5 ft deducted, matching the other four tub alcoves.

| | Was (rev 6) | Now (rev 7) |
|---|---|---|
| TX Bath 4 wall, net per unit | 93.2 SF | **78.1 SF** |
| TX Bath 4 wall Qty at 15% | 107.2 | **89.8** |
| Building total at 15% | 2,945.2 SF | **2,910.4 SF** |

Smartsheet row `502709287976836` is updated to **89.8**. All five tub alcoves now share one rule.

Still open: **powder fixture finish** is brushed brass/bronze, unconfirmed, so WT11 and WT12 stay
provisional.

### PRODUCT IMAGES — pulled 2026-08-23
16 unique product images are downloaded from the Elm Surfaces CDN and delivered as
`Wieland_Tile_Images.zip` plus a contact sheet `Wieland_Tile_Images_Contact_Sheet.png`.

| File | Product | Pixels | Size |
|---|---|---|---|
| FT1_WT1_Cortar_Bone.jpg | Cortar Bone | 1701 x 1701 | 3.7 MB |
| FT2_WT3_Cortar_Clay.jpg | Cortar Clay | 1701 x 1701 | 3.5 MB |
| FT3_Cortar_Grey.jpg | Cortar Grey | 1200 x 1200 | 1.8 MB |
| FT6_WT10_Cortar_Charcoal.jpg | Cortar Charcoal | 1701 x 1701 | 2.9 MB |
| WT2_Cortar_Bone_Reed.jpg | Cortar Bone Reed | 2560 x 900 | 0.5 MB |
| WT4_Cortar_Clay_Ribbed.jpg | Cortar Clay Ribbed | 2560 x 900 | 0.7 MB |
| WT9_Cortar_Bone_Ribbed.jpg | Cortar Bone Ribbed | 2560 x 900 | 0.6 MB |
| WT5_Tones_Sapphire.png | Tones Sapphire | 122 x 1200 | 0.2 MB |
| WT6_Tones_Opal.png | Tones Opal | 122 x 1200 | 0.05 MB |
| WT7_Tones_Copper.png | Tones Copper | 122 x 1200 | 0.2 MB |
| WT8_Tones_Emerald.png | Tones Emerald | 418 x 4000 | 2.0 MB |
| AT2_Tones_Sandstone.png | Tones Sandstone | 122 x 1200 | 0.2 MB |
| WT11_VeraForma_Earth_Lines.webp | Vera Forma Earth Lines | 1920 x 1920 | 1.1 MB |
| WT13_VeraForma_Indigo_Edge.webp | Vera Forma Indigo Edge | 1920 x 1920 | 0.9 MB |
| WT12_Haze_Camel_Wheat.jpg | Haze Camel + Wheat | 2000 x 2000 | 0.7 MB |
| AT1_Clara_Caviar.jpg | Clara Caviar | 1000 x 1000 | 1.0 MB |
| WT5_Tones_Sapphire_field.png | Sapphire installed scene (reference) | 1980 x 2829 | 2.6 MB |

FT4 and FT5 reuse the FT1 and FT2 images — they are the same body in a smaller format.

Notes on quality:
- The five **Tones** images are single-stick renders, 122 px wide. That is how Elm publishes them.
  There is no flat field swatch on the site. An installed scene exists per colour if a richer image
  is wanted; the Sapphire one is included as a sample.
- **WT12 Haze Camel + Wheat** — the file Elm serves for this product (`0009_AMB03_CAMEL-WHEAT.jpg`)
  shows a peach and terracotta scene. It does not read as camel and wheat to me. **Check it.** The
  flat Camel and Wheat swatches on the Haze pages are only 270 x 270, too small to use.
- Images cannot be written into the Smartsheet Image column by API. They need the UI or Chrome.

**Tool note: crawl4ai cannot reach elmsurfaces.com from the Cowork container.** The egress allowlist
returns `403 CONNECT tunnel failed` for that host and for `cdn.prod.website-files.com`, so Playwright
fails with `ERR_TUNNEL_CONNECTION_FAILED`. curl fails the same way. The images were pulled through the
**Nimble MCP** instead, which is allowlisted. Use Nimble for any Elm work from Cowork.

### Pricing
Elm publishes no prices. **Actual Unit Cost stays blank on all 22 rows** until the showroom quotes the
schedule. Check the quote against the **$37,761.80** allowance (2,945.2 SF ≈ $12.82/SF). Quick-ship /
US-stocked: Tones, Vera Forma, Haze, Clara. Confirm lead times for Cortar field, Reed/Ribbed and Anti-Slip,
and the exact Reed/Ribbed panel sizes.

### Grout (after approval)
Shadow-matched **unsanded** on the Reed, Ribbed and Vera Forma relief faces. Colour-matched on the Tones
sticks at 1/16" joints. Issue each pair in **Mapei Ultracolor Plus FA and CBP Prism**.

---

## 8. DESIGN CONSTRAINTS FOR TILE SELECTION
Plumbing finishes are locked and constrain tile hard:
- **Both Primaries and both Bath 4s**: Brizo **Brilliance Black Onyx**
- **Both Bath 2s**: Hansgrohe **Matte White**
- **Both Bath 3s**: chrome (PH Hansgrohe, TX GROHE)
- **Triplex Powder 2**: Hansgrohe **Brushed Black Chrome**

Budget: current allowance is **$37,761.80 material** against 2,910.4 SF ≈ **$12.98/SF** before installation.
That allowance was derived on 07-16-26 by scaling 519 Fullerton down 33.45% on whole-building floor area —
a weak basis for bathrooms, which are wall-tile heavy. Treat it as a soft target, and ask Max whether it is
a target or a ceiling.

---

## 9. TOOLING — what works, what does not
- **Nimble beats Bright Data for scraping.** Benchmarked head-to-head on elmsurfaces.com: Nimble pulled the
  full spec block first attempt with `driver="vx8"`; Bright Data timed out at 60s twice. **Use `vx8` for
  JS-rendered sites** (Webflow, Shopify, most manufacturer PDPs). Nimble raw markdown is ~40% nav/footer
  noise — for volume work use the Web Search Agent with an `output_schema`.
- **Elm Surfaces is at 1455 W Hubbard St, Chicago** — local, stocked in the US, proven scrapeable. Good
  first stop.
- **No tile manufacturer catalog API or MCP exists anywhere.** Not Daltile, Bedrosians, Architessa; Material
  Bank has no public API. Do not go looking again.
- **Avoid the "AI interior design" MCPs** (Architecture MCP, MeltFlex, Interior Design 3D). They generate
  "specification-grade" material data from a model rather than a catalog — exactly the failure mode that
  produced an invented Hansgrohe SKU earlier in this project.
- Smartsheet: `add_rows` takes one `siblingId` per call. Section header rows carry Room Type values and show
  up in filters. `update_column` works for picklist options; a column formula was sandbox-blocked.
- The Smartsheet API **cannot set cell images**.

---

## 10. VERIFIED VENDOR MULTIPLIERS (Studio 41)
- **Brizo x 0.5496** — verified on 8 lines
- **Hansgrohe x 0.5548** — verified on 6 lines
- **Delta ~0.55** — derived from the 3754 Claremont proposal S2343240, not quoted. Observed range 0.4935–0.5704.
- **Rough-in valves never follow the trim multiplier.** Use quoted figures.
- A blank cost renders as $0.00 and the line silently vanishes from the bid. Never leave one blank.

---

## 11. DISCIPLINE THAT MATTERS ON THIS PROJECT
Errors made earlier and what they cost:
- **An invented SKU** (`04731341`). Zero organic search results is the reliable tell for a fake part number.
  Verify every SKU against the manufacturer before it lands in the sheet.
- **A half-applied fix** — SKU changed, name and reference URL left stale. Name, SKU, reference, cost and
  picklists are independent columns; changing one leaves the others wrong.
- **Quoting a spec from a YouTube caption.** Never take figures from video captions or marketing copy.
- **Trusting "dimensioned" over "scaled."** The Revit check proved the reverse on this project: every scaled
  room matched within 1 SF, while three rooms marked "high confidence" were 16–41% out, because a printed
  overall dimension is not a room boundary.
- **A PowerShell BOM** (`Set-Content -Encoding UTF8` in PS 5.1) corrupted the Claude Desktop config and made
  the app reset it. Use `[System.IO.File]::WriteAllText` with `UTF8Encoding($false)`.

Max's standing preferences: do not make assumptions, ask when unclear, do not be a people pleaser, question
his direction and offer better options, and **always write in ASD-STE100 Simplified Technical English**.

