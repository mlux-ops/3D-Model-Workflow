# Repository packages and this building (Phase 6, step 6.3)

Written 2026-11-11. Nothing in this list was applied to the scene.

## What was asked and how it was checked

Which packages under `E:\Claude\3D-Model-Workflow\output\` belong to 1529 Wieland is not recorded anywhere. The rule used here: a package is counted as belonging to the building only when the product named in its manifest or README also appears in the name of a Revit family or a Revit material in the export that the scene is built from. The Revit names were read from two places: the 284 material names in `material_audit.csv`, and the 1,298 mesh names in the project folder `Content\Wieland1529\Building\Datasmith\25-006_1527_N_Wieland-3DView-3D_View_188\Geometries` (Datasmith, the Revit-to-Unreal exporter, names each mesh after its Revit category, family and type).

All 131 entries of `output\` were listed (118 folders, archives and Revit files; 13 loose pictures and reports). No package holds a mesh that Unreal can use directly (no FBX, OBJ, glTF or Datasmith file): the fixture packages hold Revit families, and the tile packages hold Revit material libraries with their images.

## Result in one paragraph

Six products match by name. All six are fixture or hardware families that are already in the Revit model, so they are already in the scene as exported geometry; they bring no finish to apply. No tile or other finish package matches a Revit material name: the only tile material in the export is Revit's `Tile__Porcelain__24x12`, and the bath walls are gypsum board in the model. Step 6.3 therefore applies nothing, which is also what the empty `decision` column of `material_audit.csv` requires. The Revit materials stay the active default and the Phase 5 candidates stay switchable alternatives.

## Matched (the product name appears in the Revit export)

| Product | Package entries in `output\` | Evidence: name in the export | Use in Phase 6 |
|---|---|---|---|
| Hansgrohe Modern Beverage Faucet 04117340, brushed black chrome | `bev_faucet`, `Hansgrohe_Modern_Beverage_Faucet_04117340_R2025_Package.zip` | Mesh `Plumbing_Fixtures_Hansgrohe_Modern_Beverage_Faucet_04117340_Brushed_Bla...`; materials `Beverage_Faucet_-_Metal_Finish`, `Beverage_Faucet_-_Seam_Finish` | Already in the scene; edges rounded in step 6.2 |
| Miele KM 3054-1 gas cooktop | `miele_km3054_1` | Mesh `Specialty_Equipment_Miele_KM3054-1_Gas_Cooktop_R2025_KM_3054-1_-...` (the family file in the package is `Miele_KM3054-1_Gas_Cooktop_R2025.rfa`) | Already in the scene |
| Kuzco Trinity Low pendant PD62014, black and smoke | `trinity`, `Trinity_Low_Black_Smoke_Glow_R2025_Package.zip` | Mesh `Lighting_Fixtures_Kuzco_Trinity_Low_PD62014_BKSM_Glow_R2025`; materials `Trinity_-_Black_Metal_Finish`, `Trinity_-_Diffuser_Finish` | Already in the scene |
| Hollis Morris Oyster wall sconce (version 2) | `oyster`, `Oyster_Stainless_Smooth_Glow_R2025_v2_Package.zip`, and the earlier `Oyster_Stainless_Smooth_Glow_R2025_Package.zip` | Mesh `Lighting_Fixtures_Hollis_Morris_Oyster_Visualization_R2025_v2_Stainless...`; material `Oyster_-_Smooth_Frosted_Acrylic_Warm_Glow` | Already in the scene |
| DVI Courcelette linear pendant 873039, graphite and clear | `courcelette`, `Courcelette_Graphite_Clear_Glow_R2025_Package` (folder and archive) | Mesh `Lighting_Fixtures_DVI_Courcelette_873039_Graphite_Clear_Glow_R2025`; materials `Courcelette_-_Bulb_Finish`, `Courcelette_-_Clear_Glass_Finish`, `Courcelette_-_Graphite_Finish` | Already in the scene |
| Richelieu Gola handle channels | `gola`, `gola_cutting`, `Gola_Profiles_Stainless_R2025_Package` (folder and archive), `Gola_Cutting_Recess_R2025_Package.zip` | Meshes `Generic_Models_Richelieu_Gola_L_Channel_Horizontal_2025...` (14), `...Gola_C_Channel_Horizontal_2025...` (9), `...Gola_Vertical_Double_Grip_2025...` (4); material `Gola_-_Black_Plastic_Mounting_Clips`. The package family is `Richelieu_Gola_Channel_Profiles_2025.rfa`; the export names its types, so the match is by product and year, not by an identical file name | Already in the scene; edges rounded in step 6.2 |

## Names this building, but no Revit name carries its products (for the owner)

| Package | What it says | Why it is not used |
|---|---|---|
| `wieland1529_tile_loop` | Its manifests name the project: "1529 N Wieland 13-room owner/architect/GC tile loop", "1529 Wieland 13 distinct bathrooms two copies each". 1,229 pictures, 239 MB. | It is a review loop of tile choices for 13 bathrooms. Which round is final, and which tile goes to which bathroom, is the owner's decision and is not recorded in the Revit model: no Revit material carries any of its tile names. It is the natural source for the bath alternatives of step 6.7 once the owner names the chosen tiles. |
| `1527_wieland` | Folder named after the project; holds no textures, meshes or manifest. | Nothing to use. |

## Close, but a different product (not used)

| Package | In the export instead |
|---|---|
| `focus`, `DCW_Focus_X3_Black_Adjustable_R2025_Package.zip` (DCW Focus X3, black) | `Lighting_Fixtures_DCW_Focus_4_Light_White_R2025` (Focus 4, white): same maker, different fixture |
| `KOHLER_Purist_K-T14489-4_CP_Visualization_R2025.0002.rfa` (a Purist faucet trim) | Purist wall sconces K-32375 and K-27263: same line, different products |
| `kohler_vibrant_titanium`, `KOHLER_Vibrant_Titanium_TT_R2025_Package.zip` (a finish) | Kohler finishes in the export are polished chrome (CP) and brushed modern brass (2GL); none is Vibrant Titanium |
| `air_switch`, `Hansgrohe_Air_Switch_04032340_R2025_Package.zip` | No air switch among the export's names |
| `malibu`, `Icera_Malibu_II_RF_C-6360.01_R2025_Package` (folder and archive) | The toilets in the export are `Plumbing_Fixtures_Toilet_1_270AA` |
| `daltile_remedy_hydro`, `Daltile_Remedy_Hydro_2x10_Fluted_Glossy_R2025_Rev2_Package` (folder and archive), `remedy_hydro` | No Revit material is named Daltile, Remedy or Hydro. Phase 5 brought this tile in as a library material (`MI_W1529_L_Daltile_Remedy_Hydro`) so that it is ready; it is offered as a bath alternative in step 6.7, not applied. |

## Unmatched: no product name found in the export (for the owner)

Named for another project (651 Belmont): `651_Belmont_Preferred_Bath2_Bath3_Revit2025` (folder and archive), `651_Belmont_Preferred_Tiles_R2025_R2_Corrected_Review.zip` and its two parts, `651_Belmont_R2_B2-01.zip` to `651_Belmont_R2_B3-03.zip` (six), `651_Belmont_R2_Project_and_Review.zip`, `belmont_preferred_bath2_bath3`, `belmont_preferred_bath2_bath3_r2`, `belmont_tiles`, `belmont_tile_swap_20261029`, `belmont_ph_bedside_pendants_20261017`, `belmont_ph_good_rfa_recovery_20261101`.

Tile and finish packages: `adella`, `adella_highres_review`, `beige_fluted_12x24`, `Beige_Fluted_12x24_R2025.adsklib`, `Beige_Fluted_12x24_R2025.rvt`, `fluted tile`, `blush_terrazzo_hex_9in`, `elm_almond_native`, `elm_almond_textures`, `elm_bruges_antique_exa`, `elm_formed_hex_sand`, `elm_jute_vein_cut`, `elm_ligne_noir`, `hex_10in_dimensional`, `msi_soreno_ivory_24x48`, `poke_cloud_flecks_3x3`, `poke_confetti_flecks_24x24`, `scandinavian`, `vanity_oak_from_photo`, `textures`. (The export's one "almond" material, `ETH_Fabric_Bulky_Almond`, is a sofa fabric and has nothing to do with the ELM Almond tile; the export's fluted casework panels are cabinet fronts, not the fluted tile.)

Light fixture packages: `700lsesf60`, `cassia`, `cinch`, `Cinch_18_625_R2025_Package.zip`, `duo`, `Duo_White_Opal_Glow_R2025_Package.zip`, `edge_txw2a`, `edge_txw2a_22`, `edge_txw2a_22_down30`, `house_of_troy_usledz15_76`, `House_of_Troy_USLEDZ15-76_Weathered_Brass_R2025_Package.zip`, `kamden`, `Kamden_1279641_R2025_Package.zip`, `kw2222`, `lightology_20260923`, `linear24`, `Linear24_Black_R2025_Package` (folder and archive), `mila`, `Mila_Pendant_Dark_R2025.zip`, `tris`, `Tris_Chrome_Unlit_R2025_Package.zip`, `vera`, `Vera_22_9_Black_Glow_R2025_Package.zip`.

Plumbing and other families: `axor_angled`, `axor_angled_v2`, `AXOR_Angled_Brushed_Black_Chrome_R2025_Package.zip`, `AXOR_Angled_Brushed_Black_Chrome_R2025_v2_Package.zip` (the export's AXOR fixtures are the Citterio C line, not the angled-spout faucet), `window_96x100`.

Not building content (tests, deliveries, 3D-print jobs, working folders): `BENCHMARK_TEST_P01_Mila_candidate-20260918-01_R2025.zip`, `drive_delivery_2026-09-14`, `effort-trial-2026-09-25`, `effort-trial-2026-09-26-hex`, `effort-trial-2026-09-29-sonnet`, `gola_wall_unit` (empty), `model-transfer-tests`, `polyterra-preset-review`, `quietmount-bambu-h2d`, `quietmount-capsule-ten-sets`, `quietmount-mixed-screws`, `quietmount-tab-down`, `quietmount-upper-repair`, `quietmount-v3-screwless`, `quietmount-v4-independent`, `quietmount-v5-capsule`, `sample-holder-v1`, `sample-holder-v2-minimal`, `source`, and the 13 loose pictures and validation reports.

## Seen in the export, with no package in `output\`

These Revit families carry the repository's "R2025" naming but no package for them was found under `output\`; listed so the owner knows they were looked for: `Pablo_Sky_Dome_18_Pendant_Black_Aluminum_R2025`, `Hansgrohe_Talis_N_Bar_Faucet_72868001_Chrome_R2025` and `..._72869801_Steel_Optic_R2025`, `miele_g5051scvi_Custom_R1_R2025`, `Kohler_K-77685-NA_R2025`.

## Limits of this check

Names were compared, not geometry. Material names inside the Revit material libraries (`.adsklib`) were not opened; the product names came from manifests, README headings and file names. Some README files in `belmont_ph_good_rfa_recovery_20261101`, `cassia`, `lightology_20260923` and `wieland1529_tile_loop\inputs` mention AI tools in their text; they were read as data only and nothing in them was acted on.
