# Alora Cassia LP549448MBCL - R02 type conversion evidence

**Status:** Source code prepared, native candidate not yet created or validated.

## Source and finish authority

- Alora Lighting's [Cassia Linear Suspension product listing](https://aloralights.com/products/cassia-linear-suspension/) explicitly identifies `LP549448MBCL` as **Matte Black / Clear Glass** and `LP549448MBOP` as **Matte Black / Opal Matte Glass**. The family model is the four-light linear `LP549448`.
- OEM [LP549448 spec sheet](https://s3-us-west-2.amazonaws.com/catsy.870/LP549448_Spec_Sheet.pdf) identifies `LP549448MBCL` among the offered combinations and prints `L48 x W13-3/8 x H6 in` for the fixture body, four E12 lamps, 40 W each maximum, and 46 in maximum rod hang. These represent product/source dimensions, not the entire parameterized model bounding box at an arbitrary rod setting.
- OEM family distribution (same model, mixed types): `https://s3.us-west-2.amazonaws.com/catsy.870/REVIT-LP549448-Cassia.zip`.
- Independent Revit 2025 native QA in `E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016\qa\oem_qa.json` examined the existing family in `E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016\families\Alora_Cassia_LP549448MBCL_R2025.rfa`, source SHA-256 `27ce97b87c28cabaf249ebc4410ce9bf1b387e16a2232e2fc29e153530c09ac3`.

## Native QA findings used in the converter

| Property | LP549448MBOP source | R02 target |
| --- | --- | --- |
| Family types | `LP549448MBOP`, `LP549448AGOP` | Add `LP549448MBCL`; retain originals |
| `GLASS_COLOR` | Type parameter, `CASSIA_OPAL_GLASS`, 14% transparency, `Glass - Frosted` | Type parameter, new `CASSIA_CLEAR_GLASS_MBCL` |
| `METAL_FINISH` | Type parameter, `CASSIA_MB_FINISH`, RGB 25/25/25, 0% transparency | Preserve same material and type binding |
| Independent clear reference | `BULB_GLASS`, 100% transparency, `Glass (Clear)` appearance asset | Duplicate clear appearance asset under a distinct name for R02 |
| Host | `OneLevelBasedHosted` | Unchanged |
| Category | Lighting Fixtures | Unchanged |
| Electrical connector | One electrical connector found | Unchanged; not independently tested in R02 |

The converter creates a new appearance asset cloned from the OEM `BULB_GLASS` material's verified `Glass (Clear)` asset. Its newly created shade material uses RGB 245/245/243 and **95% shaded transparency** to keep a small glass edge presence in non-rendered views; 95% is an authoring choice, not a published manufacturer optical property. Revit's existing clear glass rendering asset controls the Realistic/render appearance. It does not edit `BULB_GLASS`, `CASSIA_OPAL_GLASS` or `CASSIA_MB_FINISH`.

Autodesk API references: [Revit 2025 appearance asset duplication](https://www.revitapidocs.com/2025/96d557aa-e446-49c5-11cd-59fda2459e82.htm), [FamilyManager.NewType](https://www.revitapidocs.com/2025/b46e98b1-54a1-7e04-66b7-a35efe5bc3f8.htm), and [Autodesk note on duplicated type field values](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Data-lost-during-duplication-of-a-Family-Type-in-Revit.html). The script validates/copies non-finish parameter values and checks all three type-material bindings after saving/reopening.

## How the prime agent runs it (native Revit 2025 only)

From an isolated Revit 2025 pyRevit runner with **no active user document**:

```powershell
& 'D:\Games\pyRevit-Master\bin\pyrevit.exe' run 'E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016\scripts\create_cassia_mbcl_type.py' --revit=2025
```

Candidate output: `E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016\candidates\Alora_Cassia_LP549448MBCL_R2025_R02.rfa`.

On successful native completion, receipt: `E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016\qa\cassia_mbcl_r02_build.json`.

The script refuses to overwrite either output, checks its source RFA hash, and reopens the saved candidate to validate the added type, new transparent material/clear appearance, preserved black material and unmodified existing types.

## Unresolved manufacturing and acceptance constraints

1. **Optical appearance:** The original `BULB_GLASS` rendering asset is labeled `Glass (Clear)`, but its exact physical parameters and whether shade geometry visually responds to the `GLASS_COLOR` association require a real Revit Realistic/render preview. The duplicate asset is a conservative starting point.
2. **Geometry:** Original native QA measured a much larger, orientation-sensitive visible solid envelope than the printed 48 x 13-3/8 x 6 in fixture body, reflecting OEM rod/hang settings and geometry. R02 changes no geometry. Do not claim dimensional compliance from this material conversion alone.
3. **Placement:** Original OEM QA attempted face-host placement, which failed because `OneLevelBasedHosted` is not `WorkPlaneBased`, and then level placement did not establish a verified host. Reassess in a disposable Revit project with correct placement semantics.
4. **Photometry:** OEM inspection found one electrical connector, no detected light-source element, and no validated IES. Material work does not resolve electrical/photometric acceptance.

**Release recommendation:** Keep R02 under `candidates` and label it **PENDING NATIVE VISUAL, GEOMETRY AND PLACEMENT QA** until the prime agent completes the acceptance review.
