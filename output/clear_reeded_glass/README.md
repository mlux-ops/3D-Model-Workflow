# Clear Reeded Glass, 1/2 in vertical reed — Revit 2025 material

Status, 2026-11-11: maps, Revit materials and the `.adsklib` are done. The library was exported from Revit's Material Browser by the owner and passes an archive readback (`source\adsklib_validation.json`). It has not been loaded into a second project by the builder, and no ray-traced scene render has been checked. Drive delivery is recorded in `PROJECT_MEMORY.md`.

Folder: `E:\Claude\3D-Model-Workflow\.claude\worktrees\revit-clear-reeded-glass-4376d3\output\clear_reeded_glass\` (branch `claude/revit-clear-reeded-glass-4376d3`).

## What the glass is

No product was specified. These are design defaults, not manufacturer data. They are named constants at the top of `source\build_maps.py`; change one and re-run.

| Property | Value |
|---|---|
| Reeds | vertical, convex, touching, sharp valley between them |
| Pitch | 1/2 in (12.7 mm) |
| Reed depth | 1.5 mm, shallow circular arc (radius 14.19 mm, flank 26.6 degrees at the valley) |
| Glass | nominal 1/4 in (6 mm), neutral clear |
| Grout joint, clearance | not applicable, there is no joint in glass |

## Maps

All three are 2048 x 2048 px, eight reeds across.

**Revit Sample Size: 0'-4" x 0'-4"** (8 reeds x 1/2 in; pixel aspect 1:1 equals physical aspect 1:1).

| File in `textures\` | Format (read from the PNG header) | Use |
|---|---|---|
| `Clear_Reeded_Glass_0p5in_Bump_16bit.png` | 16-bit grey | height map; black = valley, white = crest, full range = 1.5 mm |
| `Clear_Reeded_Glass_0p5in_Normal_16bit.png` | 16-bit RGB | tangent-space normal map; only red varies, green is flat mid-grey |
| `Clear_Reeded_Glass_0p5in_Color.png` | 8-bit sRGB | spatially uniform 250/250/250, the bound colour bitmap the repo requires |

The maps are procedural: the reed profile is computed analytically, and the normal map comes from the analytic slope, not from the quantised height. There is no manufacturer swatch, so there is no `SOURCE_SELECTION.md`. Reeds are a designed motif, so the regular repetition is intended; no noise or waviness was added. Checks in `source\map_validation.json` all pass: bit depths, exact one-reed periodicity (so the edges wrap), uniformity along the reed length, left/right symmetry, and normal-map red sign (left flank below mid, right flank above).

## Revit materials

Three materials were built in a disposable Revit 2025.4 project, saved, reopened and read back from disk (`source\revit_validation.json`, zero project warnings). The project is `qa\Clear_Reeded_Glass_QA_DISPOSABLE_R2025.rvt`. It is the source for the library export and is not a deliverable.

Common to all three, Identity and Graphics tabs: class **Glass**, shading colour RGB 225/236/238, **transparency 80%**, "Use Render Appearance" off, no surface or cut pattern.

### 1. `Clear Reeded Glass - 0.5in Vertical Reed` — the default

Appearance type **Solid Glass**. Chosen because it is the only glass type tested that draws the reeds in the Realistic viewport (see `evidence\revit_realistic_viewport_comparison.png`).

| Setting (Appearance tab) | Value | Basis |
|---|---|---|
| Color | Custom, image `..._Color.png`, fallback colour 0.98 neutral | bound colour bitmap rule |
| Reflectance | 0.05 | estimate; glass is about 4% at normal incidence |
| Refraction (index) | 1.52 | standard soda-lime glass |
| Roughness | 0.0 | library default for polished clear glass |
| Relief Pattern | Custom, image `..._Bump_16bit.png` | height map |
| Relief amount | 1.0 | estimate |
| Texture size, both images | 4 in x 4 in, repeat on, rotation 0 | Sample Size |

### 2. `Clear Reeded Glass - 0.5in Vertical Reed (PBR Height Map)`

Appearance type **Transparent** (physically based, API name `PrismTransparentSchema`).

| Setting | Value | Basis |
|---|---|---|
| Color | 0.98 neutral at a distance of 6 mm | estimate for clear glass |
| Index of refraction | 1.52 | standard |
| Roughness | 0.0 | polished |
| Surface albedo image | `..._Color.png`, 4 in x 4 in | bound colour bitmap rule |
| Relief | `..._Bump_16bit.png`, type Height, **depth 1.5 mm**, 4 in x 4 in | exact, from the profile |

### 3. `Clear Reeded Glass - 0.5in Vertical Reed (PBR Normal Map)`

Same as 2, except Relief is `..._Normal_16bit.png`, type Normal, scale 1.0.

Revit's relief slot holds one image, read as height or as normal, so the two maps cannot be bound at once. That is why 2 and 3 are separate materials: no swapping by hand is needed.

## What Revit actually showed

- **Realistic viewport:** the Solid Glass material draws faint vertical reeds over a dark background, with a light veil from the polished surface. Both Transparent (PBR) materials render as plain flat glass. They were pixel-identical to a pane with no relief at all, so the viewport ignores relief on that type.
- **The bound colour bitmap does no harm:** on both types, the pane with the bitmap was pixel-identical to the pane without it.
- **Revit's own material thumbnails show relief on all three materials.** The swatch previews stored inside the library (`evidence\adsklib_thumbnail_*.png`) have highlights broken into fine ribs on the Solid Glass vase and on both Transparent (PBR) spheres. So the PBR height and normal maps do respond in Revit's swatch renderer, even though the Realistic viewport ignores them. A swatch is not a scene render: it does not show a background bent through the reeds.
- **Texture scale and direction are right:** a diagnostic stripe on the backdrop showed 1/2 in vertical stripes at the expected spacing.

## What is not done or not verified

1. **The library has not been loaded into a second Revit project by the builder.** Revit has no API for material libraries, so opening it means the Material Browser. What is verified is the file itself: it is a clean archive holding exactly the three materials, none of the `QA` ones, with all five image bindings (`source\adsklib_validation.json`).
2. **No ray-traced scene render was run** (no API route). How the reeds bend what is seen through the glass is unverified for all three materials. The swatch thumbnails show the relief is active; they do not show refraction.
3. **The normal map's red-channel direction is verified on the image only**, not under a known light in Revit. If a render shows the reeds lit from the wrong side, tick Invert on the image in the Texture Editor.
4. Two Solid Glass values were set by number through the API and should be glanced at in the Appearance tab: Color should read **Custom** (stored as 6) and Relief Pattern should read **Custom** (stored as 3). Roughness should read **0**. The library does carry an image on the Color slot and on the Relief Pattern slot, which is consistent with both being Custom.
5. Reflectance, relief amount, transparency and shading colour are estimates to tune by eye.
6. No V-Ray assets: not requested.

## How the library was made

`Clear_Reeded_Glass_0p5in_R2025.adsklib` was created in Revit 2025's Material Browser (Create New Library, then Add to for the three materials) from `qa\Clear_Reeded_Glass_QA_DISPOSABLE_R2025.rvt`. It was not written by a script. Size 184,461 bytes, SHA-256 `b510d0263055c95f1520171ccdba802b00e611cbc5d3118969f595fbc53fb035`.

## Loading the library in a project

1. Unzip the package to a permanent folder.
2. In Revit: File, Options, Rendering, **Additional Render Appearance Paths**, add the package's `textures` folder. Do this first.
3. Manage, Materials, folder icon menu, **Open Existing Library**, pick `Clear_Reeded_Glass_0p5in_R2025.adsklib`.
4. Drag a material into the project.

Step 2 matters. The library stores each image by absolute path to the folder it was built in, `E:\Claude\3D-Model-Workflow\.claude\worktrees\revit-clear-reeded-glass-4376d3\output\clear_reeded_glass\textures\`. That folder is a temporary git worktree and will stop existing. With the `textures` folder on the render appearance path Revit finds the images by file name. If an image still shows as missing, re-pick it in the Appearance tab; the Sample Size is 4 in x 4 in.

## Files

| Path | What it is |
|---|---|
| `Clear_Reeded_Glass_0p5in_R2025.adsklib` | the material library, three materials |
| `textures\` | the three maps |
| `source\build_maps.py`, `source\map_validation.json` | map generator and its checks |
| `source\probe_revit_schemas.py`, `source\revit_probe.json` | which Revit appearance types accept which slots |
| `source\build_revit.py`, `source\revit_validation.json` | material builder, readback, test views |
| `source\verify_adsklib.py`, `source\adsklib_validation.json` | archive readback of the library |
| `evidence\` | grazing-light, wrap and section previews; Revit viewport comparison; Revit's swatch thumbnails from the library |
| `qa\` | disposable Revit project and raw view exports; not deliverables, not in the package ZIP |
