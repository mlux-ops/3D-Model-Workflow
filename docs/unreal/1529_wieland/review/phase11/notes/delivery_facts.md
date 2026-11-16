# Delivery facts: 1529 N. Wieland (Phase 11 input)

Read-only sweep, 2026-11-14. PF = `E:\Claude\3D-Model-Workflow\.claude\worktrees\1529-wieland-scene-plan-e84a03\docs\unreal\1529_wieland`.
Refs are `file:line`; for CSVs, `row` = file line number (header = row 1).
Only this file was written. No instruction-like text was found in the PF files read. Stills and frames were not opened; figures are from the JSON, CSV and Markdown records.

## 1. Licences

### 1.1 Third-party and unlicensed items in the Unreal project

NR = NO RECORD (no licence kept). Sizes and file counts from `asset_licence_groups.csv` (row numbers below).

| # | Asset or set | Unreal path / folder | Source / site | Licence (as recorded) | URL (if given) | Source (file:row) | Note |
|---|---|---|---|---|---|---|---|
| 1 | ambientCG surface sets: Bricks086, Carpet016, Concrete046, Fabric061, Leather031, Travertine009, Wood049, Wood090A, WoodFloor051 (9 in use) | `Content/Wieland1529/Materials/Textures/` | ambientCG | CC0 1.0 (licence page read 2026-11-11) | https://ambientcg.com/get?file=`<Set>`_2K-JPG.zip ; https://docs.ambientcg.com/license/ | asset_downloads.csv rows 2-11; phase5_results.md:44, 101; material_rebuild.csv col 16 (28 rows cite these sets; Wood090A not cited there) | Bricks085 downloaded, not used (phase5_results.md:120) |
| 2 | Poly Haven oak_veneer_02 | `Content/Wieland1529/Materials/Textures/` (`T_W1529_P12_OakVeneer02_C`, no longer used) | Poly Haven | CC0 1.0 (licence page read 2026-11-13) | https://polyhaven.com/a/oak_veneer_02 | asset_downloads.csv row 24; phase12_results.md:90; material_rebuild.csv col 16 (6 rows cite Poly Haven CC0; set not named there) | 27.2 MB downloaded |
| 3 | Poly Haven ash_veneer, white_maple_veneer | No Unreal path in any results file | Poly Haven | CC0 1.0 | https://polyhaven.com/a/ash_veneer ; https://polyhaven.com/a/white_maple_veneer | asset_downloads.csv rows 25-26 | Use in project not confirmed; check before delivery |
| 4 | Poly Haven earlier-project sets (13 sets, e.g. asphalt_03) | `Content/Wieland/R15_Materials/PolyHaven/` | Poly Haven | "CC0, as the earlier project's records state"; licence page not read then | https://polyhaven.com | asset_licence_groups.csv row 33; asset_licences.csv row 1038; SOURCES.md:98 | 55 files, 482.5 MB |
| 5 | ambientCG SurfaceImperfections015 (glass) | `Content/Wieland/R15_Materials/Glass/T_R15_GlassImperfection_SurfaceImperfections015_4K.uasset` | ambientCG | CC0, "as the earlier project's script states" (site not read) | https://ambientcg.com | asset_licence_groups.csv row 20; asset_licences.csv row 1017 | 2 files, 14.0 MB |
| 6 | Earlier-project production materials; TextureCan Metal0010, Rooftop0010, Limestone1 (M. Tolga Arslan); ambientCG Grass004 | `Content/Wieland/R15_Materials/Production/` | TextureCan; ambientCG | NR. Scripts say CC0; SOURCE_REPORT.md says no outside maps taken (contradiction) | - | asset_licence_groups.csv row 4; asset_licences.csv row 1093; r15_native_extras.py lines 13-16 | 53 files, 230.6 MB |
| 7 | Earlier-project landscape and grass texture | `Content/Wieland/R15_Landscape/` | Three conflicting sources: ambientCG Grass004, Poly Haven grass_medium_02, a Fab grass folder | NR | - | asset_licence_groups.csv row 2; asset_licences.csv row 961 | 52 files, 108.5 MB |
| 8 | Earlier-project other materials | `Content/Wieland/R15_Materials/` (outside named folders) | Earlier project | NR | - | asset_licence_groups.csv row 3; asset_licences.csv row 1019 | 19 files, 0.2 MB |
| 9 | Megascans worn brick | `Content/Wieland/R15_Materials/BrickWallWorn_sexkaitb/` | Quixel Megascans | NR (tied to the taking account) | - | asset_licence_groups.csv row 10; asset_licences.csv row 1013; SOURCES.md:99 | 8 files, 96.2 MB |
| 10 | Fab downloads (materials, textures, Megascans surfaces, grass material `Mat_025_grass`) | `Content/Fab/` | Fab (Epic) | NR; "Fab items carry the Fab licence of the account that took them" | https://www.fab.com | asset_licence_groups.csv row 6; asset_licences.csv rows 67-151; SOURCES.md:99 | 85 files, 158.6 MB |
| 11 | Megascans presets | `Content/MSPresets/` | Quixel Megascans plugin | NR; comes with the plugin | - | asset_licence_groups.csv row 9; asset_licences.csv row 510 | 59 files, 11.5 MB |
| 12 | Megaplant tree library | `Content/Megaplant_Library/` | Not recorded (earlier note: "UE-only or no-redistribution") | NR | - | asset_licence_groups.csv row 8; asset_licences.csv rows 162-509; SOURCES.md:99 | IN USE: all 34 trees use it as a placement test (phase7_results.md:152). 348 files, 1,651.9 MB |
| 13 | High-poly tree model (demo level) | `Content/HighPoly_Tree_Model/` | Not recorded | NR | - | asset_licence_groups.csv row 7; asset_licences.csv row 153 | 9 files, 37.1 MB; scene use not checked |
| 14 | Product configurator template content | `Content/ProductAssets/` | Not recorded; names match an Epic template | NR | - | asset_licence_groups.csv row 12; asset_licences.csv row 570 | 28 files, 4.3 MB; scene use not checked |
| 15 | Sample building content | `Content/Building/` | Not recorded; names match an Epic sample | NR | - | asset_licence_groups.csv row 19; asset_licences.csv row 2 | 65 files, 63.6 MB |
| 16 | Other grass assets | `Content/Grass.uasset`, `Content/NewLandscapeGrassType.uasset` | Not recorded | NR | - | asset_licence_groups.csv row 11; asset_licences.csv row 152 | 3 files, 0.0 MB |
| 17 | Revit export: light distribution (IES) files | `Content/Wieland/Revit1527/...` and `Content/Wieland1529/Building/...` (e.g. `.../Textures/12303-PC-30K-25-BK_IES.uasset`) | Lighting manufacturers, through Revit families | Manufacturer download terms; not recorded | - | asset_licence_groups.csv row 17; asset_licences.csv row 2635; SOURCES.md:100 | 22 files, 2.6 MB. Fixture table uses these (phase8_results.md:52) |
| 18 | Revit export: Autodesk library images | `Content/Wieland/Revit1527/...`; `Content/Wieland1529/Building/...` | Autodesk material library (via Revit) | Autodesk terms; use outside Autodesk programs not recorded | - | asset_licence_groups.csv row 14; asset_licences.csv row 2642 | 100 files, 8.0 MB |
| 19 | Revit export: generated surface images (online-editor naming) | same as 18 | Not recorded | NR | - | asset_licence_groups.csv row 15; asset_licences.csv row 2647 | 46 files, 19.2 MB; owner to identify |
| 20 | Revit export: Indiana limestone images | same as 18 | Not recorded (may be a stone supplier or generated) | NR | - | asset_licence_groups.csv row 16; asset_licences.csv row 2671 | 24 files, 3,522.4 MB (largest item) |
| 21 | Revit export: other images | same as 18 | Not recorded per image | NR | - | asset_licence_groups.csv row 18; asset_licences.csv row 2637 | 81 files, 25.0 MB |
| 22 | Revit export, earlier project | `Content/Wieland/Revit1527/` | Owner's Revit model | Owner's property; manufacturers' families: no record | - | asset_licence_groups.csv row 35; asset_licences.csv row 1208 | 1,619 files, 203.1 MB. Kept for comparison (OPEN_DECISIONS.md:143) |
| 23 | Revit export, Phase 1 pilot copy | `Content/Wieland1529/Scratch/` | Owner's model via Datasmith | Owner's property; manufacturers' families: no record | - | asset_licence_groups.csv row 36; asset_licences.csv row 4767 | 1,589 files, 100.9 MB |
| 24 | Revit export, Phase 3 | `Content/Wieland1529/Building/Datasmith/25-006_1527_N_Wieland-3DView-3D_View_188/` | Owner's Revit model 25-006 | Owner's property. Contains manufacturers' families (plumbing, appliances, windows, furniture, light fixtures); terms not recorded | - | asset_licence_groups.csv row 37; asset_licences.csv row 2928; SOURCES.md:32 | 1,584 files, 88.9 MB |
| 25 | Daltile Remedy Hydro 2x10 fluted tile package | `Content/Wieland1529/Materials/Library/MI_W1529_L_Daltile_Remedy_Hydro` | Colour image from the manufacturer's product pictures; relief and roughness made here | Colour: manufacturer's terms not recorded. Relief/roughness: own | - | asset_licence_groups.csv row 13; asset_licences.csv row 4717; material_library.csv row 2 | 4 files, 4.0 MB |
| 26 | Surroundings massing (Phase 4) | `Content/Wieland1529/Surroundings/` (`L_Surroundings.umap`, `Meshes/SG_*`) | Cook County building footprints 2022 (redistribution unclear); ISGS 2022 lidar | Footprints "provided as is"; lidar "No restrictions apply" | https://data.isgs.illinois.edu/arcgis/rest/services/Elevation/IL_Cook_DTM_2022/ImageServer/info/metadata | asset_licence_groups.csv row 39; asset_licences.csv row 6442; SOURCES.md:42, 44 | 182 files, 21.7 MB. In the scene |
| 27 | Earlier-project site model (neighbour buildings) | `Content/Wieland/R14/` | City of Chicago Building Footprints | "See Terms of Use"; terms page refused | https://data.cityofchicago.org/d/syp8-uezg | asset_licence_groups.csv row 5; asset_licences.csv rows 610-960; SOURCES.md:43 | NR. 351 files, 21.0 MB. Used by option "Earlier detailed buildings" (phase7_results.md:82) |
| 28 | Phase 12 rebuilt materials (22 Brizo/Hansgrohe/Kohler names among 122) | `Content/Wieland1529/Materials/Rebuilt/`, `.../Parents/`, `.../Textures/` | This project's own work (105 rows), "no image; values only" (53), Revit export's own image (11), CC0 sets (rows 1-3 above) | Per `material_rebuild.csv` col 16 | - | phase12_results.md:35, 90; material_rebuild.csv col 16 | Manufacturer images never used as textures (asset_downloads.csv row 27) |
| 29 | Phase 5 materials and candidates | `Content/Wieland1529/Materials/` | Own work; CC0 sets as above | - | - | asset_licence_groups.csv row 32; asset_licences.csv row 4601 | 162 files, 104.0 MB |
| 30 | Own work | `Content/Python/`; `Content/Wieland1529/L_Site_M1.umap` and the scene levels; `Content/Wieland/R15_Render/` (earlier render settings) | Own | - | - | asset_licence_groups.csv rows 21, 34, 38; asset_licences.csv rows 598, 1150, 4598 | No third-party licence needed |

Summary: 38 groups (asset_licence_groups.csv rows 2-39). 18 groups are NR, totalling 1,357 files and 5,965 MB (phase5_results.md:73; the group rows add up to the same totals).

### 1.2 Hotel-related rows

- **None.** Searched `asset_licences.csv`, `asset_licence_groups.csv`, `asset_downloads.csv`, `material_library.csv` for hotel, Duke, 1520, 1528, ProposedHotel. The only hits are false positives inside numbers such as `A_wells_1559_815208_...` (asset_licences.csv rows 824-844, earlier-project neighbour buildings).
- Removed by Phase 15: the hotel level, its Variant Manager list and its assets. Count differs: "its 71 assets" (phase15_results.md:3) vs "72 hotel assets" (phase15_results.md:97). Reference downloads (78 files, 52.2 MB) went to the Recycle Bin of E: (phase15_results.md:41).
- Still in project, needs a check: 1520 N. Wells object `SB_782868` (earlier project; Visible override restored, phase15_results.md:40). Phase 15 says the model still shows 1520 N. Wells as surveyed, with a wrecking permit dated 1 May 2026 (phase15_results.md:82). This is an owner decision, not a licence row.

### 1.3 Listed but NOT in the Unreal project (per records)

- Brizo reference images (4 swatches, 4 photos): never imported into the Unreal project (asset_downloads.csv row 27).
- Fixture photometric downloads (rows 12-22: Alcon, EAE, Focal Point, Kohler, Kuzco, Lumenwerx, Simes, Visual Comfort, Zero Mist): kept outside the repository and not passed on (same rows). The scene uses the photometric file inside the Revit family (asset_downloads.csv rows 12-22, notes).
- Generic IES shapes made here, 4 files (asset_downloads.csv row 23): own work; in-project use not confirmed.
- Google Photorealistic 3D Tiles, Street View, Mapillary: looking only (SOURCES.md:63, 65, 84). The distant city is public laser massing (OPEN_DECISIONS.md:28). No Cesium plugin on 5.9 (OPEN_DECISIONS.md:67).

### 1.4 Unreal content folders to check in a cooked package

- `Content/Fab/`
- `Content/Megaplant_Library/`
- `Content/HighPoly_Tree_Model/`
- `Content/MSPresets/`
- `Content/ProductAssets/`
- `Content/Building/`
- `Content/Grass.uasset`, `Content/NewLandscapeGrassType.uasset`
- `Content/Wieland/R14/`
- `Content/Wieland/R15_Landscape/`
- `Content/Wieland/R15_Materials/` (incl. `PolyHaven/`, `Glass/`, `Production/`, `BrickWallWorn_sexkaitb/`)
- `Content/Wieland/R15_Render/`
- `Content/Wieland/Revit1527/`
- `Content/Wieland1529/Materials/` (incl. `Textures/`, `Library/`, `Rebuilt/`, `Parents/`, `Variants/`)
- `Content/Wieland1529/Building/`
- `Content/Wieland1529/Scratch/`
- `Content/Wieland1529/Surroundings/`
- `Content/Python/`

## 2. Accepted differences and known limitations

### 2.1 Accepted

| Item | Accepted by | Source |
|---|---|---|
| None of the 9 reality-match failures (F1 to F9) is marked yet: 0 of 9 | Owner, pending | phase10_results.md:81; REVIEW.md:103 |
| Proposed "accept" options, not yet accepted: F2 (accept the rest), F6 (or accept), F7 (or accept, 1.9% over), F8 (or accept), F9 (accept, use path-traced) | Proposal only | REVIEW.md:108-115 |
| Commit to 5.9: no DLSS, no Cesium/Google city backdrop, risk of preview defects accepted, no return to 5.8 | Owner (interview) | OPEN_DECISIONS.md:28-29, 69 |
| Distant city = public laser massing (decision 6 superseded) | Owner (interview) | OPEN_DECISIONS.md:28 |
| Lot lines: Revit model's property lines govern (decision 7 settled) | Owner (interview) | OPEN_DECISIONS.md:31 |
| Lot width still listed as open in phase 10 (survey 50.18 ft vs record 49.50 ft) | Conflicts with the row above | phase10_results.md:110 |
| REFERENCE_VIEWS.md tolerances accepted as written until Phase 2 measured | Plan default | OPEN_DECISIONS.md:140 |
| Soak shortened to 42 of 120 walks | Owner decision | phase9_results.md:3, 230 |
| Phase 9 count corrected: 8 of 12 views pass, not 9 | Plan | phase10_results.md:107 |
| Phase 11 decisions taken in the owner's absence: delivery to E: (H: missing); S7 not rendered (12 stills, not 13); no finish-alternative stills | Plan | phase11_results.md:68-70 |
| Phase 2: two of four acceptance lines met by a route that differs from the plan's wording | Plan | phase2_results.md status paragraph (top); acceptance table rows 24-27 |

### 2.2 Known limitations

| # | Limitation | Source |
|---|---|---|
| L1 | Neighbours' heights fail: 3 of 19 within 0.3 m; overall up to 12.07 m (F1) | REVIEW.md:107 |
| L2 | Neighbours' walls: 26 of 76 sides in Zone 1 over 0.5 m from county outline, largest 3.0 m (F2) | REVIEW.md:108 |
| L3 | Roadway 13.1 cm under laser ground; kerb height not taped (F3) | REVIEW.md:109; phase10_results.md:105 |
| L4 | Real-time vs path-traced: S9 +26.2%, D3 +18.0%, D4 -42.4%, D5 -11.9%, S8 plan +38.5% (F4-F7, F9) | REVIEW.md:110-115 |
| L5 | Sharp edges at D2, D3, D4: 569, 451, 328 left (F8) | REVIEW.md:114 |
| L6 | Nine of 19 tolerances not checked: no site photographs | REVIEW.md:32, 117-133 |
| L7 | Tree species unknown; models chosen by shape (19 ginkgo, 9 Norway maple, 5 English oak, 1 silver birch) | REVIEW.md:52 |
| L8 | Trees read as conifers in real-time from above; path-traced pictures use fallback meshes (Nanite mode 0) | REVIEW.md:137; phase10_results.md:108; phase11_results.md:81 |
| L9 | The 12 Phase 12 path-traced pictures used Nanite mode 2 and were not remade | REVIEW.md:138 |
| L10 | Station cameras: all tilted up 8 degrees, 24 mm lens, against the REFERENCE_VIEWS.md table | phase10_results.md:109 |
| L11 | Design views not checked against Revit (no export) | REVIEW.md:132; phase10_results.md:111 |
| L12 | S8 plan picture vs county aerial: no number | phase10_results.md:112 |
| L13 | Real-time tier at 2,560 by 1,440 not measured on a packaged build | phase10_results.md:118 |
| L14 | Soak: 42 of 120 walks, not two hours | phase9_results.md:216, 230 |
| L15 | Far city behind roof deck (D1) is a stand-in | REVIEW.md:139; site_gaps.md gap 12 |
| L16 | Lawn is a green-tinted stand-in; fails the material gate closer than 1 m | REVIEW.md:140; phase7_results.md:88, 153 |
| L17 | Furniture is labelled grey stand-ins, not approved | REVIEW.md:140; placeholders.csv |
| L18 | No cars, road markings or people | REVIEW.md:141 |
| L19 | No finish alternative rendered; names not given by owner | phase11_results.md:70; OPEN_DECISIONS.md:36 |
| L20 | S7 cannot exist (no alley; point inside rear neighbour's lot) | phase11_results.md:69; site_gaps.md gap 6 |
| L21 | Site visit not made; site data is spring 2022 | site_gaps.md top; site_gaps.md gap 9 |
| L22 | Editor closes with unsaved `L_Site_M4`: answer "do not save" | phase10_results.md:114 |
| L23 | Nanite ray tracing mode 2 switched off for good | phase10_results.md:108 |

## 3. Measured vs assumed

### 3.1 Measured (with the data behind it)

| Item | Data | Source |
|---|---|---|
| Lot: 49.50 by 102.20 ft record (15.088 by 31.151 m); governs | Record rectangle; county parcel 1.1-1.2 ft deeper, not used for depth | phase2_results.md:11; site_survey.csv row 3 |
| Street right-of-way 50 ft (plan had 66 ft) | Plat of survey T1.1, 2025-08-18 | site_survey.csv row 2; phase2_results.md:14; site_gaps.md "What is not a gap any more" |
| No alley behind the lot | Plat of survey | site_survey.csv row 26; site_gaps.md "What is not a gap any more" |
| Ground heights, 1 ft cells | 2022 ground surface, Illinois State Geological Survey | site_survey.csv rows 8-14 |
| Tree heights (crown), leafless | 2022 top surface minus ground | site_survey.csv rows 15-18 (12.7, 15.9, 17.8, 11.6 m) |
| 34 tall objects as trees | 2022 laser scan | phase2_results.md acceptance table row 27; REVIEW.md:51 |
| Neighbour positions and heights | Plat of survey (positions); county footprints and lidar 2022 (heights) | site_survey.csv rows 22-25; site_gaps.md gap 13 |
| True north 1.17 / 1.14 / 1.18 deg (within 0.03 deg) | Parcel lines, building walls, lot front line | phase2_results.md acceptance table row 25 |
| Lot corners to level coordinates | Round trip 0.000 m | phase2_results.md acceptance table row 24 |
| Building on its lot: 0.1-0.3 mm | Revit export vs lot | REVIEW.md:43 |
| Tree height: 34 of 34 at scan height | Laser scan | REVIEW.md:51 |
| Sun direction: 0.05 deg | Engine sun vs computed | REVIEW.md "Per tolerance" table (lines 39-61) |
| Transfer from Revit: 0.1-0.4 mm | Revit export | REVIEW.md:56 |
| Real-time vs path-traced, per view | Renders | REVIEW.md:110-115 |
| Demolition June 2026; new-construction permit 2026-09-03 | City permits | OPEN_DECISIONS.md:61 |
| Existing site model audit (partly live, read-only) | Editor read-only | SITE_MODEL_AUDIT.md:9-19, 84 |
| Existing model sun at template values (lat 45, lon -73) | Read live | SITE_MODEL_AUDIT.md:40 (A2) |

### 3.2 Assumed or stand-in

| Item | Status | Source |
|---|---|---|
| Tree species | Assumed by shape; not known | REVIEW.md:52 |
| Trunk positions and sizes | Not measured; crown centres used | site_survey.csv rows 15-16 notes; site_gaps.md gap 1 |
| Street furniture (hydrant, poles, signs, bins) | Left out | site_gaps.md gap 2 |
| Parkway planters, iron fence | Left out, or sod shown as designed | site_gaps.md gap 3 |
| Neighbour facades | Plain walls, neutral grey | site_gaps.md gap 4 |
| Parapets and roof edges of neighbours | Not resolved by 1 ft lidar cells | site_gaps.md gap 13 |
| Sidewalk and kerb materials | Plain concrete | site_gaps.md gap 8 |
| Car park south of 1525 | Flat asphalt at measured ground height | site_gaps.md gap 7 |
| Building behind the lot | Not in the existing site model; a gap | site_gaps.md gap 5 |
| Anything built or planted after spring 2022 | 2022 state used | site_gaps.md gap 9 |
| Leaf-on appearance | Crowns filled to measured spread | site_gaps.md gap 11 |
| Far city | Stand-in | site_gaps.md gap 12; REVIEW.md:139 |
| Daylight placeholders (Placeholder_Sun 10 lux, sky atmosphere, skylight) | Phase 2 state; later phases set the sun (summer afternoon, bearing 241.72, height 46.40); replacement of the placeholders not checked | site_gaps.md gap 16; phase11_results.md:81 |
| Lawn | Green-tinted stand-in | phase7_results.md:88 |
| Furniture | Grey stand-ins, 81 objects | placeholders.csv |
| Finish values with no image | "No image; values only" on 53 rows | material_rebuild.csv col 16 |
| Finish gloss (Hansgrohe coating) | Assumed matte | material_candidates.csv row 2 |
| Finish colour (RNT_Material) | Guess from object name; owner to specify | material_candidates.csv row 3 |
| Kohler K-27263 lumens | Generic 800 lm lamp | asset_downloads.csv row 15 |
| Generic IES shapes (4) | Stand-ins for fixture kinds with no published file | asset_downloads.csv row 23 |
| Camera stations | Checked against the surveyed station list, not reality | REVIEW.md:54 |
| Colour of principal materials; photographs | Not measured | REVIEW.md:55, 59 |

### 3.3 Site survey file

- `site_survey.csv`: 26 data rows (27 lines with header).
- Header (row 1): item, kind, metres_north_of_sw_lot_corner, metres_east_of_sw_lot_corner, value, unit, source, date_of_source, note.
- Kinds in the rows: street, kerb, ground height, tree, street furniture, fence, neighbour.

## 4. Open owner decisions

### 4.1 OPEN_DECISIONS.md (written 2026-11-10; later answers in the interview table, lines 22-46)

| No. | Title | Current state / default in force | Source |
|---|---|---|---|
| 1 | Confirm new construction | Settled: new construction | OPEN_DECISIONS.md:15 |
| 2 | Engine version | Settled: commit to 5.9 (decision 2 superseded) | :28-29 |
| 3 | How build sessions reach the editor | Settled: Fable 5.2 in the editor terminal; settings file placed | :35, :16 |
| 4 | Keep and correct the existing site model | Settled: same project, new surroundings one object per building | :33 |
| 5 | One site visit now, or also in summer | Settled "once now"; visit NOT done (owner's step) | :32; phase10_results.md:102 |
| 6 | Distant city stand-in | Superseded: public laser massing; stand-in in scene | :28; REVIEW.md:139 |
| 7 | Which lot width governs | Settled: Revit lot lines govern; phase 10 still lists the 50.18 vs 49.50 ft frontage as open | :31; phase10_results.md:110 |
| 8 | Trees, furniture and textures: sources | Open; default: owner photographs, then CC0, then authored | :102-105 |
| 9 | Disk layout | Settled (UE-LocalDataCachePath to D:); H: missing per phase 11 | :44; phase11_results.md:68 |
| 10 | Records left by earlier work | Settled except the access key (owner) | :46 |
| 11 | Rooms for interior views | Superseded: all four units | :34 |
| 12 | What is delivered, and where | Settled | :45; :125-127 |
| 13 | How the animation is rendered | Settled | :42 |
| 14 | Smaller decisions (Blender, Mapillary, tolerances, Revit import kept until accepted) | Defaults in force | :138-143 |
| 15 | Decisions raised by Phase 1 (Nanite RT mode, Lumen World Cache off, scratch content, 8 texture files disregarded per owner 2026-11-11) | Defaults in force | :147-157 |

### 4.2 Later open items (not numbered)

- Mark F1 to F9 "fix" or "accept" in review\phase10\owner_marks.csv: 0 of 9 marked (phase10_results.md:101; REVIEW.md:103).
- Site photographs and the visit (REFERENCE_VIEWS.md shot list; phase10_results.md:102).
- Look at street imagery in a browser (phase10_results.md:103).
- Keep-or-rebuild per material; names of finish alternatives (up to two per surface, OPEN_DECISIONS.md:36); furniture; far city (phase10_results.md:113).
- Megaplant tree library licence: confirm, or choose another vegetation option (phase7_results.md:152).
- Lawn: no licensed grass image (phase7_results.md:153).
- 1520 N. Wells: wrecking permit 1 May 2026; model may be out of date (phase15_results.md:82).
- Fab and Megascans licence records (SOURCES.md:99).
- Fixture manufacturers' terms per file (SOURCES.md:100; asset_licence_groups.csv row 17).

### 4.3 Switchable options (Variant Manager lists as recorded)

| List | Options | Source |
|---|---|---|
| LVS_W1529_Surroundings: "Surroundings" | "Earlier detailed buildings"; "Phase 4 survey massing" | phase7_results.md:82 |
| LVS_W1529_Surroundings: "Revit site objects" | "Hidden (site view)"; "Shown (as exported from Revit)" | phase7_results.md:84 |
| LVS_W1529_Surroundings: "Site ground" | Options not recorded | phase15_results.md:22 |
| LVS_W1529_Surroundings: "Season" | "Leaf-on (summer)"; "Leaf-off (November)" | phase7_results.md:89 |
| LVS_W1529_Phase12_Materials (Variants folder) | "Revit as exported"; "Phase 12 active" (3,176 surfaces) | phase12_results.md:49, 62 |
| "Neighbour development" (hotel list) | Removed by Phase 15 | phase15_results.md:39 |
| Finish alternatives (owner's switchable alternatives) | None named or rendered | OPEN_DECISIONS.md:26, 36; phase11_results.md:70 |

### 4.4 Labelled stand-ins and placeholders

- placeholders.csv: 81 rows (lines 2-82). All are SM_W1529 grey stand-ins in /Game/Wieland1529/Interiors/Generated/Placeholders/. Note on every row: "grey stand-in (step 6.5); furniture is not approved".
  - By kind: planters with shrubs 24; outdoor dining table for six 14; display shelves 11; outdoor sectional sofa 6; other 26.
  - By floor: Roof 34, Floor4 18, Floor3 13, Floor2 6, Lower 6, Floor1 4.
  - By unit: NorthPenthouse 33, SouthPenthouse 32, SouthTriplex 9, NorthTriplex 7.
- Labelled markers left as exported (material_rebuild.csv, action "left as exported", 8 rows): EAE_Logo, Generic_Clearance_Area, Generic_Warning, MI_CineMat_CamViewFinder, MI_CineMat_CameraBody, and 3 z_Miele_Connection rows.
- Site stand-ins (site_gaps.md): far city (gap 12); placeholder sun, sky atmosphere and skylight (gap 16, Phase 2 state; not checked against later phases).

## 5. Phase 9 final real-time tier, profile M7

Source: phase9_results.md lines 176-186 (header line 176; separator line 177; rows 178-186). Rows copied verbatim; the 4-space list indentation is removed for markdown.

| Recording | Frame mean (ms) | 95th percentile | Worst | Frames over 33.3 ms | Graphics card mean | Game thread mean | Video memory peak (MB) |
|---|---|---|---|---|---|---|---|
| Exterior path, 60 s | 11.50 | 12.82 | 22.11 | 0 of 5,217 | 10.07 | 7.23 | 9,076 |
| Triplex path, 30 s | 9.81 | 12.62 | 20.40 | 0 of 3,059 | 8.47 | 6.57 | 8,933 |
| Penthouse path indoors, 20 s | 12.04 | 14.55 | 32.57 | 0 of 1,661 | 10.51 | 7.07 | 9,391 |
| Penthouse path roof deck, 10 s | 11.65 | 13.69 | 19.53 | 0 of 859 | 10.13 | 7.25 | 9,429 |
| Hold S1 | 13.61 | 13.42 | 1,123.2 | 3 of 735 | 10.42 | 9.11 | 9,078 |
| Hold S2 | 11.71 | 13.10 | 14.68 | 0 | 10.25 | 7.19 | 8,950 |
| Hold S6 | 11.19 | 12.45 | 20.06 | 0 | 9.76 | 7.10 | 8,936 |
| Hold D5 | 9.75 | 10.94 | 17.44 | 0 | 8.38 | 6.65 | 8,859 |
| Hold D2 | 12.23 | 13.94 | 19.64 | 0 | 10.69 | 6.83 | 9,388 |

Notes:
- Recorded 06:18 to 06:22, editor in front for every recording (phase9_results.md:174).
- The 1.1 s stall in Hold S1 is the editor's autosave, not the scene (phase9_results.md:188).
- Acceptance line for the exterior path, 95th percentile: 12.82 ms vs 16.67 ms limit (phase9_results.md:239).

## 6. Phase 11 stills and the J3 memory note

### 6.1 Stills in delivery\stills\ (12 files)

Location: PF\delivery\stills\. Sizes and timestamps: review/phase11/stills_checksums.json. Render seconds: review/phase11/stills_runs.jsonl (seconds_to_file). All 3,840 by 2,160, path-traced, 1,024 samples, 64 warm-up frames.

| View | File | Bytes | Render (s) | Written (2026-11-13) |
|---|---|---|---|---|
| S1 | S1_pathtraced.0000.png | 12,544,569 | 189.3 | 08:35 |
| S2 | S2_pathtraced.0000.png | 12,766,979 | 86.2 | 08:38 |
| S3 | S3_pathtraced.0000.png | 13,111,435 | 98.0 | 08:41 |
| S4 | S4_pathtraced.0000.png | 12,063,233 | 68.2 | 08:43 |
| S5 | S5_pathtraced.0000.png | 12,960,405 | 64.9 | 08:45 |
| S6 | S6_pathtraced.0000.png | 14,138,250 | 102.3 | 08:48 |
| S9 | S9_pathtraced.0000.png | 13,847,386 | 113.3 | 08:51 |
| D1 | D1_pathtraced.0000.png | 11,763,423 | 135.6 | 08:55 |
| D2 | D2_pathtraced.0000.png | 15,311,625 | 644.4 | 10:46 |
| D3 | D3_pathtraced.0000.png | 19,724,698 | 471.6 (journal says 541 s, phase11_results.md:79) | 11:25 |
| D4 | D4_pathtraced.0000.png | 22,281,646 | No run-log row; journal says 1,666 s (phase11_results.md:79) | 11:53 |
| D5 | D5_pathtraced.0000.png | 17,581,808 | 169.4 | 11:57 |

Flags:
- phase11_results.md:79 says the "table of all twelve stills" closes J1, but no such table exists in phase11_results.md. The table above is built from the JSON and JSONL files.
- D4 has no row in stills_runs.jsonl.
- phase9_results.md:172 and :264 call S9 the dusk view; phase11 J6 (phase11_results.md:81) lists S9 at the saved summer-afternoon sun (bearing 241.72, height 46.40). Conflict, not resolved here.
- All twelve decode at full size; SHA-256 of each is in stills_checksums.json (phase11_results.md:81).

### 6.2 J3 note on free commit memory

phase11_results.md:78 (J3, 10:56), quoted:

> Free commit memory has stayed at 27 GB, under the 30 GB line, since D2: the editor holds 20.5 GB where a freshly started editor holds 17.8 GB, and a garbage collection gave nothing back.

Action taken: close the editor (nothing unsaved mattered), start it again, close the "Restore" window, then render. D3-D5 ran at a lowered line of 26 GB (phase11_results.md:79). The animation runs start at 30 GB, with 26 GB only if a fresh editor cannot reach 30 (phase11_results.md:80).

## 7. Other conflicts found in the sweep

- Phase 15 hotel asset count: 71 (phase15_results.md:3) vs 72 (phase15_results.md:97).
- D3 render time: 471.6 s in the run log vs 541 s in the journal (see 6.1).
- Lot width: OPEN_DECISIONS.md:31 says settled; phase10_results.md:110 says open.
- Nanite mode: REVIEW.md:138 says the 12 Phase 12 pictures used mode 2; the Phase 11 stills use mode 0 (phase11_results.md:76).
- Ten ambientCG sets downloaded, nine in use (phase5_results.md:44, 76, 120).
- Earlier-project grass source recorded three ways (asset_licence_groups.csv row 2).
