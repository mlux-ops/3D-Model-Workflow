# Clear Reeded Glass, 1/2 in vertical reed — Revit 2025 material

Status, 2026-11-11: maps and Revit materials are built and verified. **The `.adsklib` is not made yet.** A material library can only be created in Revit's Material Browser, and that step could not be automated here (see "What is not done"). Nothing is on Google Drive yet.

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
- **Texture scale and direction are right:** a diagnostic stripe on the backdrop showed 1/2 in vertical stripes at the expected spacing.

## What is not done or not verified

1. **The `.adsklib` does not exist.** Revit has no API for material libraries. UI Automation reached the Manage tab of a separate Revit window, but Revit does not expose the ribbon buttons to it, and driving the Material Browser would have meant taking over the mouse and keyboard. Steps to make it by hand are below.
2. **No ray-traced render was run** (no API route). How the reeds bend what is seen through the glass is therefore unverified for all three materials. This is the main open question; the PBR materials exist because they are expected to render best, but that is an expectation, not a result.
3. **The normal map's red-channel direction is verified on the image only**, not under a known light in Revit. The viewport does not respond to the PBR normal map, so it could not be checked there. If a render shows the reeds lit from the wrong side, tick Invert on the image in the Texture Editor.
4. Two Solid Glass values were set by number through the API and should be glanced at in the Appearance tab: Color should read **Custom** (stored as 6) and Relief Pattern should read **Custom** (stored as 3). Roughness should read **0**.
5. Reflectance, relief amount, transparency and shading colour are estimates to tune by eye.
6. No V-Ray assets: not requested.

## Making the library (about a minute)

1. In Revit 2025 open `E:\Claude\3D-Model-Workflow\.claude\worktrees\revit-clear-reeded-glass-4376d3\output\clear_reeded_glass\qa\Clear_Reeded_Glass_QA_DISPOSABLE_R2025.rvt`.
2. Manage tab, Materials.
3. Bottom-left of the Material Browser, the folder icon menu, **Create New Library**. Save as `E:\Claude\3D-Model-Workflow\.claude\worktrees\revit-clear-reeded-glass-4376d3\output\clear_reeded_glass\Clear_Reeded_Glass_0p5in_R2025.adsklib`.
4. In the project materials list, type `Clear Reeded` in the search box. Right-click each of the three `Clear Reeded Glass - 0.5in Vertical Reed...` materials, **Add to**, the new library. Skip the materials whose names start with `QA`.
5. Click OK and close the project without saving.

## Loading the library in a project

Manage, Materials, folder icon menu, **Open Existing Library**, pick the `.adsklib`. Drag a material into the project. If an image shows as missing, either re-pick it in the Appearance tab or add the package's `textures` folder under File, Options, Rendering, Additional Render Appearance Paths. The images are bound by absolute path to this worktree's `textures` folder, which stops existing if the worktree is removed.

## Files

| Path | What it is |
|---|---|
| `textures\` | the three maps |
| `source\build_maps.py`, `source\map_validation.json` | map generator and its checks |
| `source\probe_revit_schemas.py`, `source\revit_probe.json` | which Revit appearance types accept which slots |
| `source\build_revit.py`, `source\revit_validation.json` | material builder, readback, test views |
| `evidence\` | grazing-light, wrap and section previews; Revit viewport comparison |
| `qa\` | disposable Revit project and raw view exports; not deliverables |
