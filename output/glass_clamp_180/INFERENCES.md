# SHB_Glass Clamp 180 Square — values, sources, deviations

Task sheet: [TASK_Glass_Clamp_180_Family_Build_1.md](TASK_Glass_Clamp_180_Family_Build_1.md). CRL sources: [references/crl_sgc180/](../../references/crl_sgc180/README.md). Constants: `source/clamp_spec.py`.

## Values

| Parameter | Task sheet | Built | Source class | Evidence |
|---|---|---|---|---|
| Clamp_Height | 2" | 2" | VERIFIED CRL | product page, template p1 |
| Clamp_Width | 5" | 5" | VERIFIED CRL | product page, template p1 |
| Glass range | 3/8–1/2" | types 3/8, 1/2 | VERIFIED CRL | product page, template |
| Glass_Thickness default | 1/2" | 1/2" (`1-2 Glass`) | PROJECT | finish DB Primary Bathroom enclosure rows (Duplex Down, Penthouse, Simplex): IFC A0.2 General Note 45, 1/2" minimum tempered |
| Joint_Gap | 1/8" ASSUMED | **1/16"** | VERIFIED CRL | template p2 "1/16" Gap (1.5mm)" |
| Hole_Edge_Distance | — | 1-19/32" (added) | VERIFIED CRL | template p2 |
| Cap_Spacing | Clamp_Width − 2" = 3" | **2 × Hole_Edge_Distance + Joint_Gap = 3-1/4"** | DERIVED | screws pass through the glass holes |
| Screw count / side | 2 per side, 4 front caps | **2 total, rear plate only; front plain** | VERIFIED CRL | template p1 front vs rear view |
| Cap_Diameter | 3/4" ASSUMED | 1/2" | ASSUMED | rear isometric scales ≈ 0.46" |
| Cap_Height | 1/8" ASSUMED | 1/16" | ASSUMED | CRL draws heads flush; 1/16" is a visible reveal; ≥ 1/32" keeps clear of Revit short-curve tolerance |
| Plate_Thickness | 1/8" ASSUMED | 1/8" | ASSUMED | not printed; schematic section scales 0.14–0.18" (unreliable, section drawn 12 % long) |
| Corner fillet | 1/8" optional | none | VERIFIED CRL | "sharp squared off corners" |
| Gaskets | not modelled | not modelled | — | CRL includes gaskets (≈ 0.05" per side in the section); plates sit on the glass faces |
| Material | `Brushed Bronze` or finish-DB name | `Vibrant Brushed Bronze`, RGB 110/86/62, glossiness 0.65, metal | PROJECT | finish DB: every primary-bath bronze row is Kohler "Vibrant Brushed Bronze" (BV); Simplex Good tier is "Champagne Bronze" (tier candidate) |

## Deviations from the task sheet, and why

1. **Screw heads: 2 on the rear plate, not 4 on the front.** CRL's front view is a plain face; the rear view shows one Phillips head per panel. The heads face the −Y (shower) side; the room side (+Y, task-sheet "Front") is plain. Swap sides by mirroring the placed instance.
2. **Joint gap 1/16" and screw spacing 3-1/4"** replace the assumed 1/8" and `Clamp_Width − 2"`. Screw spacing no longer changes with Clamp_Width; the Clamp_Width 4↔6 flex checks the heads stay put and stay on the plate.
3. **Screw heads are 24-sided prisms locked to reference planes (design change after native runs 2 and 3, 2026-10-02).** The first design dimensioned each round head's sketch with `SketchEditScope`; Revit refuses it in a family ("document is not a project document"). Leaving round heads unconstrained failed too: in the Clamp_Width flex they drifted with the plate ends. A cylinder has no flat face to lock, so each head is a 24-sided prism (1/2" across flats; visually round, and FBX tessellates a cylinder anyway) whose +-X and +-Z flats are locked to `Screw L/R Left/Right` and `Screw Top/Bottom`, placed by `Cap_Spacing` about Joint CL. This meets "lock centers to dimension Cap_Spacing". `Cap_Spacing` is a constant (3-1/4", from the CRL template) instead of `Clamp_Width - 2"`; all formula parameters are constants because a dependent formula evaluated wrongly natively. Changing `Cap_Diameter` is not supported (the prism would distort); it stays a locked constant. `Hole_Edge_Distance` is an added, documenting parameter.
4. **Extrusion work planes.** Plates are sketched on Glass Face Front/Back and extruded outward by `Plate_Thickness`; heads on Plate Outer Back, outward by `Cap_Height`. Same solids as "sketch on Plate Outer, extrude to Glass Face", with positive depths only.
5. **Plane names.** The sheet lists `Glass Mid` as Z = 0 but mirrors the back plate "about Glass Mid-plane Y = 0". Built: `Glass Mid` = Z = 0 (locked to Ref. Level); the Y = 0 glass centre plane is the template's `Center (Front/Back)`. `Joint CL` is the template's `Center (Left/Right)` renamed (still defines the origin). Four clamp-edge planes are added so every plate edge is locked.
6. **Manufacturer / Model / Description / Type Comments / URL** use the family's built-in identity parameters; custom parameters with those names would collide.
7. **Revit elevation naming.** Revit's `Front` elevation looks toward +Y from the −Y side, so in Revit's own Front view you see the screw side. The task-sheet convention (+Y = room) is kept.

## Not done here, and why

- **Load and place in the Belmont model** (task sheet § Load and Place): the Belmont RVT is not in this repository or container. Glass is resolved (1/2"); joint count and clamp heights remain open (see README).
- **Belmont material check**: the family carries `Vibrant Brushed Bronze`; on load, a project material of the same name wins and is not overwritten.
- **Brushed grain**: Generic appearance with `generic_is_metal`, no bitmap (family-embedded finish convention, Cassia precedent; no ADSKLIB is shipped). The ADSKLIB bitmap rule does not apply.
