# Source selection — ELM Fog Cross-Cut Chevron, 24 x 48 module

Product identified from the user's first image: it is ELM's own swatch
`ElmStone_Fog_Cross-Cut_Chevron-Deco_48x110_01.jpg` downscaled (mean abs diff 2.19/255
after resizing ELM's 4460 px file to 2000 px). ELM ElmStone is Florim USA's MILE stone
EcoStone, "Matte Chevron Deco", 3D textured surface, **sold only as 48 x 110 in, 6 mm**
(ELM product page, MILE stone product page and the 2026 EcoStone brochure all agree).
The user specified 24 x 48; see README "Size".

Colourway check: Fog, not Mist or Jute. Mean RGB of the flat swatches — Fog chevron
244/240/228, Fog Cross-Cut 24x48 240/235/220, Mist chevron 201/195/184, Jute Cross-Cut
24x48 218/205/185.

| # | file (references/candidates unless noted) | px | view | verdict | reason / use |
|---|---|---|---|---|---|
| U1 | `../user_01_flat_swatch_fog_chevron_2000x875.webp` | 2000 x 875 | flat, straight-on | identification only | Same image as #1 at 45 % of its resolution; the full-size original was used instead. |
| U2 | `../user_02_room_render_crop_1093x584.webp` | 1093 x 584 | room render crop (crop of #6) | **REJECTED** as a source | Room scene: perspective, lighting, plants. Used only to confirm band orientation: ELM installs the slab portrait, so the bands run parallel to the slab's long side (vertical in that scene). |
| 1 | `6508c...423d_ElmStone_Fog_Cross-Cut_Chevron-Deco_48x110_01.jpg` | 4460 x 1951 | flat, straight-on, full 110 x 48 in slab | **ACCEPTED — geometry analysis** | Chevron geometry measured here (source/_analysis). Heavy JPEG (0.65 bit/px, 8 x 8 block edges 2.4x the interior step), so not used for pixels once #10 was found. |
| 10 | `MILE_stone_EcoStone_Fog_CrossCut_ChevronDeco_48x110_01.jpg` | 1951 x 4460 | same swatch, portrait | **ACCEPTED — primary colour + structure source** | Florim's own copy of #1, rotated 90 deg: low-pass r = 0.995, registration shift 0,0 against #1. 2.2x the JPEG bits, no block artefacts, fine-grain std 5.61 vs 3.00. Rotated to landscape; four non-overlapping 48 x 24 in cuts (x 0-48 and 48-96 in, top and bottom halves). |
| 2 | `6508c...4269_ElmStone_Mist_Cross-Cut_Chevron-Deco.jpg` | 4460 x 1951 | flat swatch | REJECTED | Mist colourway; same graphic as #1, so no new content. |
| 3, 4 | `67a949..._mist-cross-cut-chevron*.jpg` | 2172 x 1381, 1541 x 1946 | room renders | REJECTED | Room scenes, Mist. |
| 5, 6 | `67aa3a..._fog-cross-cut*_fog-cross-cut-chevron.jpg` | 1371 x 2187, 2000 x 1500 | room renders | REJECTED | Room scenes (U2 is a crop of #6). |
| 7 | `6508c...4232_ELMStone_Fog_Cross_Cut_24x48_03.jpg` | 1890 x 945 | flat, straight-on 48 x 24 face | **ACCEPTED — colour only** | A different real Fog Cross-Cut face (NCC 0.02 against every other face). Plain Cross-Cut, so no groove shading to remove; grooves come from the measured structure. |
| 8 | `6508c...4250_ElmStone_Jute_Cross-Cut_24x48_03.jpg` | 1890 x 945 | flat swatch | REJECTED | Jute colourway; kept as the colourway evidence above. |
| 9 | `MILE_stone_EcoStone_Cross-Cut_Fog_24x48_Panel.jpg` | 3600 x 2400 | flat digital layout, 72 x 48 in, half offset | **ACCEPTED — two tile interiors** | Not an installed or perspective panel: joints straight to 0 px across the full width (row 1198 at every column), verticals exactly at 24 / 48 in, uniform light, 50 px/in. Its top-left and bottom-right full tiles are genuinely new faces (NCC 0.02-0.15 against all other sources; a true match scores 0.89). Interiors only, inset 4 px from the layout's own joints (joint pixels 1196-1201). Bottom-left half-tile = #7 rotated 180 deg (NCC 0.89), top-right is a half tile: neither used. |
| 11 | `MILE_stone_EcoStone_Fog_CrossCut_24x48_03.jpg` | 1890 x 945 | flat swatch | not used | #7 rotated 180 deg. |
| V | `../../belmont_tiles/ElmStone_Jute_24x48/references/manufacturer_03_flat_swatch.webp` | 2000 x 875 | flat swatch, no chevron | validation only | The same slab graphic without the chevron structure, pixel-registered with #1 (shift 0,0, low-pass r = 0.990). Used to confirm the de-grooving; never a colour source. Its colour (244/239/225) is Fog, not Jute — see README "Observation". |

Not downloaded: MILE stone's two room scenes (filenames name wall/floor/vanity installs).

## Chevron geometry, measured from #1 (source/_analysis)

- Six horizontal bands per 48 in slab height, straight to +/-3 px over the full 110 in.
  Spine rows 0 / 309 / 646 / 976 / 1265 / 1626 / 1951 px, band heights 7.13-8.88 in.
  The middle spine sits at 24.01 in, so a 24 in cut carries exactly three bands with
  spines at the tile edges: top half = type A (/ \ /), bottom half = type B (\ / \).
- Groove lines at 49.3-49.6 deg (one band 48.3 deg) from the long side, alternating
  band to band; chevron vertices point along the long side.
- Groove spacing: fundamental 7.55-8.38 px (0.186-0.206 in, 4.7-5.2 mm) per band, with
  components at 1.47x, 2.54x and 3.1x that scale with each band's pitch: a designed
  irregular raking (singles and pairs of incised lines between flat plateaus), not moire.
- Each groove is constant along its length: subtracting the extruded 1D profile removes
  the chevron from the colour (`textures/_REVIEW_degroove_before_after.jpg`). Local
  residual after the fit: median 0.01, p5-p95 -0.10 to +0.10 of the groove contrast
  (about +/-0.3 grey levels), measured in 200 px windows over the whole slab.
  Groove-band share of high-pass energy: #10 14.6 % -> 8.1 %; on #1 16.7 % -> 6.0 %.
  The remainder is stone grain in that frequency wedge (the sharper #10 keeps more of it);
  #V, a 2000 px render, holds 3.9 %.
- A frequency-notch removal was tried first (`source/degroove.py`) and rejected: it
  left the groove sub-harmonics as visible diagonal streaks.

## Non-repetition

Seven genuinely different 48 x 24 faces for twelve atlas cells. Five faces appear twice,
always two rows apart, in another column, rotated 180 deg; the verifier finds exactly
those five pairs and no adjacency on the wrapped 3 x 4 grid. This is the source limit:
no further Fog Cross-Cut faces are published. More real faces would replace the repeats
directly.
