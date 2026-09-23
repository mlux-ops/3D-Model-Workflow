# Belmont bathroom materials � eight new tiles

Native Revit 2025 library: Belmont_New_Tiles_R2025.adsklib. Open in Manage > Materials > Open Existing Library; add the desired Belmont materials to your project. Optional source RVT contains the same eight assets. Each material folder contains V-Ray VRMAT and material-only VRSCENE, four texture maps, a preview, and scale/source notes.

Revit physical scales are set. In V-Ray, map UV channel 1 to the rectangular repeat below. Dimensions are nominal tile dimensions plus estimated 1/16-inch light grout. A mosaic texture repeat need not equal its commercial sheet size.

| Material | Repeat, inches W x H | Folder |
|---|---|---|
| MSI Domino White Matte 1x6 Stack | 12.7500 x 12.1250 | Domino_White_1x6 |
| MSI Soreno Ivory 2x2 Mosaic | 10.3125 x 10.3125 | Soreno_Ivory_2x2 |
| ELM RAW Greige 24x48 Matte | 48.0625 x 24.0625 | RAW_Greige_24x48 |
| ELM Clara Bermuda 4x4 Glazed | 16.2500 x 16.2500 | Clara_Bermuda_4x4 |
| MSI Soreno Ivory 24x48 Matte | 96.1250 x 48.1250 | Soreno_Ivory_24x48 |
| ELM ElmStone Jute Vein-Cut 24x48 Matte | 48.0625 x 24.0625 | ElmStone_Jute_24x48 |
| Ribesalbes Scandinavian Grey Plain 6x7 | 10.6094 x 18.1875 | Scandinavian_Grey_Plain |
| MSI Honey Comb 2in Hex Multi-Finish | 6.1875 x 7.1447 | Honey_Comb_2in_Hex |

Keep every texture subfolder intact. Revit references absolute paths in this workspace; if relocating, repath each material to its own folder. Do not flatten the folders: their Color.png/Bump.png names repeat. V-Ray texture references are relative to each VRMAT folder; use its texture directory if your host requires repathing.

Source limits: real supplied photographs are retained. Several mosaic faces offer only 49�220 pixels across, and Soreno 24x48 faces about 490x240. Larger PNG exports do not add source detail. These are photo-based visualization materials, not measured PBR scans. Bump/normal maps contain smooth estimated grout and bevel relief only, avoiding photographic noise being interpreted as geometry. This intentionally omits unmeasured fine glaze/stone relief. Gloss/roughness and mixed-finish assignment are estimates. Plain Scandinavian retains edge lighting from its source photograph.

Revit saved/reopened eight materials with zero warnings; all eight exported through Material Browser. V-Ray scene parsed 80 objects with zero warnings; render blocked by Chaos license -98. Native VRMAT import and final rendered appearance are unverified. Review.html provides flat previews, not renders.

Already created; not duplicated:
- [Adella Viso White](../adella_highres_review/MSI_Adella_HighRes_Review.zip)
- [Scandinavian Grey Decor](../scandinavian/Scandinavian_Decor_Grey_6x7_Materials.zip)

Existing links work in this workspace; if moving this package, use your previously downloaded archives. No PR or push was created.

## Updates since the eight-material delivery — 2026-09-20

- **ElmStone_Jute_24x48**: added a finely-ridged bump variant (`Bump_FinelyRidged16.png`,
  still sized to the original 48.0625x24.0625 in panel) and a corrected, genuinely
  non-repeating colour atlas (`Color_NonRepeating.png`, 144.1875x72.1875 in, 3x3 panel
  cells) — the shipped `Color.png` wraps but repeats one photo's recognizable vein
  pattern across every panel. Neither new file is wired into the VRMAT/VRSCENE or the
  shared ADSKLIB yet. See that folder's own `README.md` for what still needs
  reconciling before this is a drop-in replacement.
- **ElmStone_Jute_CrossCut_24x48** (new, not yet in the nine-material table above or in
  `manifest.json`/the ADSKLIB): a new finish of the same stone, cross-cut instead of
  vein-cut (no directional veining). Colour map only — no bump, normal, roughness,
  VRMAT, or Revit material yet. See its own `README.md`.
