# Modern Forms Smooth FR-W2502-52L-SB/MB: partial finish candidate

**Status:** guarded native scripts prepared; Revit 2025 execution and visual inspection pending. Do not release the candidate as a fully finished SB/MB family yet.

## Official sources

- [Manufacturer Smooth product](https://modernforms.com/product/smooth/) establishes the 52-inch three-blade model and Soft Brass/Matte Black SB/MB finish.
- [Manufacturer exact Revit model download](https://modernforms.com/images/products/REVIT/FR-W2502_REVIT.zip) was acquired and checked: `FR-W2502-52L.rfa` is the included exact-model family, source ZIP SHA-256 `737e9edbe43f5be5561e2d47f915e5b033e14495643f6e5f623a56889d83f029`.
- [Manufacturer specification](https://modernforms.com/images/products/SPECSHEET_PDF/FR-W2502_SPSHT.pdf) defines dimensions, construction and finishes.
- [Manufacturer SB/MB finish swatch](https://modernforms.com/images/finishes/soft_brassmatte_black.jpg) saved locally to `E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016\sources\oem\MFR1415595_Smooth_SBMB_official_swatch.jpg`, SHA-256 `de2bb5517d6b23f9c23e467dad50000886823df6c43784336af97a91afc516c7`. Sample display RGB 175,156,113 for Soft Brass and 14,14,14 for Matte Black; these are manufacturer graphic samples, **not** measured PBR reflectances.

No separate exact-manufacturer FBX, SketchUp, Blender, OBJ or mesh download was substantiated during this investigation. The Revit RFA above is the documented manufacturer 3D source.

## Native source geometry map

Independently acquired evidence: `E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016\qa\inspect_oem_material_parts.json`, SHA-256 `2ee88654c081a629fa324681703497a72adff29a2481a676f51b98d03b2213b3`.

| Exact IDs | Observed geometry | Proposed treatment |
|---|---|---|
| 2997, 2998, 2999 | Three isolated long radial FreeFormElements, approx. 403×590×50.87, 405×589×50.87 and 645×129×50.87 mm | Assign provisional Matte Black to these complete native FreeFormElements only, 140 previously unassigned faces each |
| 3038, 3039, 3040, 3041, 3042 | Discrete central cylinder/motor cover, short cylinder, downrod, canopy, thin canopy trim; local radii within 179 mm, distinct from swept blades | Assign provisional Soft Brass to these five discrete housing/rod/canopy elements only |
| 3000 | Central 113.5×113.5×21.5 mm element near the LED lens | Preserve unassigned; lens/trim identity unresolved; optical shader not guessed |
| 2977, 2980, 2982, 2985–2989, 2990–2994 | 13 native `ImportInstance` CAD elements, numeric layers 0–20, material ID 2869 shared across category layers, all solid faces unassigned | **Preserve all**: imported geometry contains mixed unknown parts. Global import layer color would blanket-recolor unrelated surfaces |
| 1537 | 96-in template/reference extrusion | Exclude from physical fan sweep and finish conversion |

The part inference for 2997–2999 is strongly supported by spatial extents and exactly three radial elements; identification of all CAD import subparts remains unverified. The five brass assignments are **geometry-based component classifications**, with photo/Realistic visual verification still required before acceptance.

The existing official RFA in `E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016\families\ModernForms_Smooth_FR-W2502-52L_SBMB_R2025.rfa` has SHA-256 `45c76b46fba9daebcf5d0ebbedb7b5592d4eaa50cbbd4b5b59fe44321b7b8e18`. OEM R03 native QA confirmed independent placed positive-solid radial sweep 1321.692521 mm vs. nominal 1320.8 mm (difference 0.892521 mm, within the pre-established 1 mm gate). Material assignment does not edit native coordinates, tessellation or element geometry.

## Prime native commands

Create separate partial-finish R02 candidate and immutable build receipt:


```powershell
& 'D:\Games\pyRevit-Master\bin\pyrevit.exe' run 'E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016\scripts\build_smooth_sbmb_r02_partial.py' --revit=2025
```

Target: `E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016\candidates\ModernForms_Smooth_FR-W2502-52L_SBMB_R2025_R02_PARTIAL_UNAPPROVED.rfa`.

Build receipt: `E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016\qa\smooth_sbmb_r02_build.json`.

Only after build success, run independent native Revit 2025 face-material, face-host placement and 52-inch radial sweep QA:

```powershell
& 'D:\Games\pyRevit-Master\bin\pyrevit.exe' run 'E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016\qa\smooth_sbmb_r02_native_qa.py' --revit=2025
```

QA receipt: `E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016\qa\smooth_sbmb_r02_native_qa.json`.

Native gates: exact original-file hashes; unique source part element IDs/classes and face counts; each assigned part's native Material parameter; unassigned light lens/13 CAD imports untouched; saved-family face material readback; project face-host and true radial sweep; zero Revit family/project warnings. Neither run overwrites existing receipt/output files. Both save in isolated task folders only and leave the active project untouched.

**Holds:** manufacturer finish color gloss/roughness not PBR calibrated; imported CAD remains gray/unassigned; the opal lens part and other subparts require visual differentiation. A successful script run is a *partial finish validation* rather than final release approval.
