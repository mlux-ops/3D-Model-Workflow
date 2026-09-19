# Source selection — Poke Cloud Flecks, Straight Joint 3x3 Matte

Product page: https://www.daltile.com/products/terrazzo-look/poke/cloud-flecks-straight-joint-3x3-matte

Candidates identified from the page's Scene7 image set (fetched 2026-09-19, all downloaded at
3000x3000 px via `?wid=3000&hei=3000`):

| File / asset | Pixels | View type | Verdict | Reason |
|---|---|---|---|---|
| **`poke_cloud_flecks_3x3_DAL_PK20_3x3_Msc_CloudFlecks_MT_Silo_01.jpg`** (`DAL_PK20_3x3_Msc_CloudFlecks_MT_Silo_01`) | 3000x3000 | Flat, straight-on 4x4 chip mosaic sheet, no scene, no fixtures, no perspective, uniform lighting | **ACCEPTED** | Matches the WORKFLOW.md requirement for a flat straight-on tile-face image with no baked scene lighting or perspective. Used as the sole colour/pattern source for the final maps. |
| `poke_cloud_flecks_3x3_DAL_PK20_3x3_Msc_CloudFlecks_MT_ScanPanel_01.jpg` (`DAL_PK20_3x3_Msc_CloudFlecks_MT_ScanPanel_01`) | 3000x3000 | Flat, straight-on larger multi-sheet panel grid, no scene | REJECTED (not needed) | Also a flat straight-on scan, but a redundant, larger panel; the accepted Silo swatch already provides a flat, uniformly-lit source at full resolution, so this was not used. |
| `poke_cloud_flecks_3x3_DAL_PK20_3x3_CloudFlecks_MT_ScanPanel_Prop_01.jpg` (`DAL_PK20_3x3_CloudFlecks_MT_ScanPanel_Prop_01`) | 3000x3000 | Installed bathroom room scene (round mirror, wall-mount faucet, vessel sink, window, perspective wall) | REJECTED | Not a tile face; contains fixtures, reflections, and perspective wall convergence, per WORKFLOW.md line 30 and the visual acceptance gate. |
| `poke_cloud_flecks_3x3_DAL_PK20_3x3_Msc_CloudFlecks_MT_ScanPanel_Angle_01.jpg` (`DAL_PK20_3x3_Msc_CloudFlecks_MT_ScanPanel_Angle_01`) | 3000x3000 | Angled panel photo, raking perspective | REJECTED | Angled/perspective view, not a flat tile face. |
| `poke_cloud_flecks_3x3_DAL_PK20_3x3_Msc_CloudFlecks_MT_Angle.jpg` (`DAL_PK20_3x3_Msc_CloudFlecks_MT_Angle`) | 3000x3000 | Angled 4x4 sheet photo (raised/tilted perspective view showing tile edge thickness) | REJECTED | Angled tile detail; perspective distorts true face proportions. |
| `poke_cloud_flecks_3x3_DAL_PK20_3x3_Msc_CloudFlecks_MT_Corner.jpg` (`DAL_PK20_3x3_Msc_CloudFlecks_MT_Corner`) | 3000x3000 | Angled corner/edge detail, tilted perspective | REJECTED | Corner/edge shot in perspective, not a flat face. |
| `poke_cloud_flecks_3x3_DAL_PK20_3x3_Msc_CloudFlecks_MT_Detail.jpg` (`DAL_PK20_3x3_Msc_CloudFlecks_MT_Detail`) | 3000x3000 | Flat straight-on close-up crop of ~1.5 chips | REJECTED (not needed) | Flat but a partial close-up crop with less usable field than the full Silo swatch; not required once the Silo swatch was accepted. |
| `poke_cloud_flecks_3x3_DAL_PK20_3x3_Msc_CloudFlecks_MT_MosaicFlip.jpg` (`DAL_PK20_3x3_Msc_CloudFlecks_MT_MosaicFlip`) | 3000x3000 | Marketing shot of a hand holding/flexing the mesh-backed sheet, angled | REJECTED | Not a flat face; shows mesh backing and sheet flex from an angle, with a hand in frame. |

## Product facts sourced directly from the page (2026-09-19)

- Nominal Size: 3x3 (in)
- Nominal Mounted Sheet Size: 12x12 (in), Mount Method: Dot Mount — confirmed visually in the
  accepted Silo swatch, which shows a 4x4 grid of 3 in chips per 12x12 in sheet.
- Mosaic Pattern: Straight Joint
- Grout Joint Recommendation: 1/8 in -> actual chip size = 3 - 0.125 = 2.875 x 2.875 in
- Finish: Matte; Color Name: Cloud Flecks (white terrazzo-look with black/grey/taupe flecks)
- Body Type: Glazed Mosaics; Edge: Non Rectified

## Build note

Built from the accepted Silo swatch only, cropped first to its tile-face bounding box (the
swatch has a white photography margin around the 4x4 chip grid) so that every sampled crop
lands on flecked tile, never blank background. An 8x8 chip atlas of the 3 in nominal module
(2.875 in actual chip + 0.125 in joint, matching the page's stated 1/8 in grout joint) was
generated with per-module crop/tone variation for non-repetition — 8x8 chosen as the minimum
atlas size specified for this build, per WORKFLOW.md's seamless/non-repeating instruction and
visual acceptance gate.
