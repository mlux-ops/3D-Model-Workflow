## Acceptance: each line of the plan with its number

One lighting condition exists, the one the owner chose on 2026-11-10: the summer afternoon (15 August 2026, 15:30 Central Daylight Time) with every fixture on. The twelve views are S1 to S6, S9 and D1 to D5.

| Plan line | Result | Number or workaround | Where it is recorded |
|---|---|---|---|
| Sun: bearing and height within 0.5 degree of NOAA for every condition | Met | Bearing 241.72 degrees against NOAA 241.67 (0.05 off); height 46.40 against 46.34 (0.06 off). North offset 178.82 degrees. | J3; `review\phase8\sun` |
| Shadows: edges on the ground within 0.3 m of the owner's photograph taken at the same time | Workaround; the photograph part waits on the owner | No site photographs exist. In their place the shadow of a 3.00 m test pole was measured against the calculated shadow: 4.6 cm too long, about 3 cm off sideways at the tip. This proves the sun's direction and the scale, not the match with a real photograph. | J7; `review\phase8\shadow_check.json` |
| Exposure: sunlit sidewalk concrete within one third of a stop of the grey-card-balanced photograph | Workaround; the photograph part waits on the owner | No photograph exists. Exposure is fixed (automatic exposure off): EV 14.64 outdoors (ISO 100, f/8, 1/400 s), EV 9.0 in the rooms (ISO 100, f/8, 1/8 s). An 18 percent grey card in open sun reads 0.178 against 0.18. The sunlit sidewalk reads 0.09 stop over middle grey. A white card in open sun receives 91,086 lux (plan: 80,000 to 100,000); the sky alone gives 17,985 lux. | J3, J4; `review\phase8\brightness_readings_j4.json` |
| Fixtures: every interior and exterior fixture has a photometric file and a lumen value traceable to a data sheet, listed in a table | Met in part | All 571 lights are in the table, in 21 kinds (the J8 line says 22; the table has 21 rows and 21 is right). 11 kinds (230 lights) use the maker's photometric file. 9 kinds (339 lights) use a generic light shape made here, because the Revit family names no product or the maker's file could not be reached; each is marked as a placeholder with what it waits on. 1 kind (2 emergency lights) is off. 314 lights are lit, 257 are off (the second light of two-light fixtures, and the emergency lights). Every lit light has a colour temperature (2,700 to 4,000 K). Check of one fixture: 733.44 lux measured against 740.2 calculated (0.9 percent low). 28 fixture bodies have no light in the Revit export and stay dark. | J5, J6, J8; `review\phase8\fixture_table.csv`, `review\phase8\fixture_lights.csv`, `asset_downloads.csv` |
| Real-time against ground truth: mean brightness difference of 10 percent or less over facade and ground at each view, and no region larger than 2 percent of the frame off by more than one stop; failing regions listed with the cause | 9 of 12 views pass; 3 fail, each with its cause | See the table below. With the project's settings as they stood, 7 of 12 passed; with Lumen's "hit lighting" switched on in the lighting level (saved in J13), 9 of 12 pass. | J10, J11, J13; `review\phase8\compare\compare_hit1.csv` |
| A side-by-side sheet of ground truth and real-time for every view | Met | 12 sheets, each with ground truth, real-time and a difference map: `review\phase8\compare\<view>_sheet_hit1.jpg` (the saved state), and `<view>_sheet.jpg` (before the change). | J10, J11 |

Real-time against ground truth, per view, in the saved state (mean difference in percent; largest region off by more than one stop, in percent of the frame):

| View | Mean | Largest region | Result | Cause when failing |
|---|---|---|---|---|
| S1 | -1.9 | 1.14 | pass | |
| S2 | +2.0 | 0.15 | pass | |
| S3 | -1.0 | 0.35 | pass | |
| S4 | +2.2 | 0.06 | pass | |
| S5 | -2.9 | 1.16 | pass | |
| S6 | -0.1 | 0.37 | pass | |
| S9 | +31.3 | 2.06 and 2.01 | fail | The neighbouring houses are empty shells. The real-time picture shows bright sky through their upper windows; the path-traced picture shows them dark. Remedy: a dark backing behind the neighbours' windows (surroundings work, not a lighting setting). |
| D1 | -7.9 | 0.52 | pass | |
| D2 | +19.9 | 2.31 | fail | The bronze-tinted window glass dims the sunlight in the path-traced picture and does not dim it in real time (the sunlit floor is 1.1 stops brighter). The smoke-glass pendant shades are drawn milky in real time and dark in the path-traced picture. Both are glass-material questions for the material rebuild (Phase 12). |
| D3 | +27.7 | 2.80 | fail | The same tinted-glass cause as D2. |
| D4 | +3.2 | 0.19 | pass | |
| D5 | -9.9 | 0.15 | pass | |

Steps without an acceptance line:

| Step | Result |
|---|---|
| 8.5 street lights | Not set. No notes on the street lights' type or colour exist; this waits on the owner's site visit. Street lights are off in a summer afternoon in any case. |
| 8.6 clouds, haze, fog | Scattered fair-weather clouds (`LGT_Clouds`), haze 0.05, height fog 0.005 (`LGT_HeightFog`). Their cost at S1 is inside the run-to-run spread (13.5 to 14.8 ms with, 13.3 to 14.1 ms without). |
| 8.7 ground truth | 12 pictures, 3840 by 2160, 1,024 samples per pixel. Ten are inside the 10 minute budget (79 to 476 s); D2 took 662 s and D4 about 1,125 s. D4 is still visibly grainy. |
| 8.9 settings tried | Hit lighting: kept (2 more views pass). `r.RayTracing.Nanite.Mode 2`: no view changes side, about 1.4 ms and 840 MB dearer, and the editor crashed twice at the same engine check while it was on; not recommended. Ray-traced shadows: the editor fell under one frame a second and memory went under the floor; not usable. Front-layer reflections, translucent shadows, the newer handling of overlapping glass: no gain. Lumen World Cache: cannot be tried without changing a project settings file; not done. |
| 8.10 shadow edges against photographs | Waits on the owner's site visit and photographs. |
| 8.11 profile M6 | Saved in `profiles\2026-11-12_M6`. Conditions: summer afternoon lighting, all four unit levels loaded with 284 fixture lights lit and casting shadows, editor viewport 2,038 by 1,198 pixels at 100 percent screen size (profile M4 was 2,038 by 782, so M6 has 53 percent more pixels and the difference from M4 is lighting plus the larger picture), editor in the foreground for only part of some recordings (share between 0.27 and 1.0). Mean frame time (worst frame; graphics card time), in ms: exterior path 28.05 (51.8; 17.32), M4 was 9.18; triplex 17.71 (35.4; 16.14), M4 8.54; penthouse indoors 22.08 (32.0; 20.48), M4 8.44; roof deck 24.76 (42.9; 21.81), M4 8.69. Video memory at most 11,353 MB (budget 13,000; M4 5,991). Every path is over the 16.67 ms limit in these conditions; bringing it back inside is Phase 9's work. With hit lighting: exterior +2.2 ms, triplex -1.3, penthouse +0.5, roof deck +0.2. |

## What was saved or changed in the Unreal project

Nothing Datasmith created was edited, nothing was deleted, no project settings file was changed, "Save All" was never used and `/Game/Wieland/R15_Landscape/L_R15_Production` was never saved.

| What | Change | How to undo |
|---|---|---|
| `/Game/Wieland1529/Lighting/L_Light_SummerAfternoon` (new level) | Holds the sun `LGT_Sun` (160,000 lux), `LGT_SkyAtmosphere`, `LGT_SkyLight`, `LGT_HeightFog`, `LGT_Clouds` and three exposure volumes: `LGT_Exposure_Outdoors`, `LGT_Exposure_Interior_LowerTo3rd`, `LGT_Exposure_Interior_4th`. `LGT_Exposure_Outdoors` also switches Lumen's hit lighting on. | Remove the level from the top levels. For hit lighting alone: switch the override "Lumen ray lighting mode" off on `LGT_Exposure_Outdoors` and save the lighting level by name. |
| `/Game/Wieland1529/L_Site_M4` and `/Game/Wieland1529/L_Site_M2` (top levels) | Each loads the lighting level; each one's three placeholder objects (sun, sky, sky light) are made not visible, not deleted. | `review\phase8\placeholder_overrides.csv`: `wieland_lighting.placeholders(True)`, then save the level by name. |
| `/Game/Wieland1529/Lighting/Photometric` (new folder) | 12 photometric assets imported from the files in the fixture table. | Not used by anything but the lights below. |
| The four unit levels (north triplex, north penthouse, south triplex, south penthouse) | The 571 imported lights are set as overrides: 314 lit with output, colour temperature, photometric file, reach and direction from the fixture table (198 aimed straight down); 257 off. 322 fixture body meshes no longer cast shadows, so that a body does not shade its own light. | `review\phase8\fixture_lights_before.csv` holds every light's values before the change; a Datasmith reimport also puts them back. |

## For the owner

Decisions and items that wait on the owner:

1. Site visit and photographs: the shadow check against a photograph, the exposure check against a grey-card photograph, and the street lights' type and colour all wait on them.
2. Nine kinds of fixture (339 lights) use a generic light shape. `review\phase8\fixture_table.csv`, column `waits_on`, says per kind what is missing: a product name for the Revit family "Recessed Can Light" (282 lights), the lamp for the Kohler Purist sconces, and files the makers' sites would not hand over to a script (XAL, Kohler, Kuzco, Simes, Visual Comfort, Alcon; refused, behind a login, or not found). The EAE archive is 149 MB, over the 50 MB approval. Downloading these by hand would replace the placeholders.
3. Licences: the makers' photometric files carry no licence statement. They are kept outside the repository in `E:\Wieland1529_site_data\photometry\` and listed in `asset_downloads.csv` with that note.
4. 28 fixture bodies have no light in the Revit export (Kuzco Trinity 12, Hollis Morris Oyster 4, DVI Courcelette 2, DCW Focus 2, Pablo Sky Dome 1, 7 without a family name). They stay dark until a light source is added to the Revit families or the owner approves adding lights in Unreal.
5. Fixture lenses do not glow; a lit fixture looks dark where the lamp is. A glowing lens material belongs to the material rebuild.
6. The sidewalk material reflects about 18 percent; broom-finished concrete usually reflects 25 to 35 percent. A material decision.
7. Hit lighting was saved in the lighting level (an override in one object, not a project setting). It makes two more views pass and costs up to 2.2 ms on the exterior path. The undo is in the table above.
8. `r.RayTracing.Nanite.Mode 2` in real time is not recommended: no view passes because of it, it costs about 1.4 ms and 840 MB, and the editor crashed twice at the same engine check while it was on (22:36 and 00:24). It stays 0. It is still used for the path-traced pictures only, set and put back by the render script.
9. The graphics card time limit of 60 seconds (set by the owner at 22:43) did not prevent the 00:24 crash. The owner may put it back or keep it.
10. Profile M6 is over the frame limit on every path and all 284 lit lights cast shadows. Phase 9 has to decide which lights cast shadows and at what screen size the walk-through runs. A MegaLights variant (Unreal's method for many shadow-casting lights) was not measured.
11. D2 and D4 take longer than 10 minutes to path trace, and D4 is grainy at 1,024 samples.
12. The three failing views: the neighbours' windows need a dark backing (S9); the bronze-tinted glass and the smoke-glass pendant shades need material work so that both renderers treat them alike (D2, D3). The Phase 12 re-render will re-measure them.
13. Lumen World Cache can only be tried by changing a project settings file; it was left alone.
14. The advisor tool named in the owner's global rules does not exist in this session; its checkpoints were replaced by written checks of my own.
15. The full-size pictures (`review\phase8\ground_truth\*.png`, `review\phase8\realtime\*.png`) are on disk but not committed, as in earlier phases. The sheets, tables and scripts are committed.
16. Nothing was pushed.

