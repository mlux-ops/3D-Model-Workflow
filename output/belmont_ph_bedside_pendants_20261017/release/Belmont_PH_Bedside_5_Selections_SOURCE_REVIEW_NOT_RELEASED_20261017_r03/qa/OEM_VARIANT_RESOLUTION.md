# 651 Belmont PH bedside pendants — OEM variant and material reconciliation

**Audit date:** 2026-10-17 (America/Chicago). **Result:** preserve the four original OEM RFAs. Only the Milca Gold requested selection has an exact matching stored Revit family type and material parameter. Jarvis Brushed Gold, Malabar Brushed Gold, and Dipping Light 13 Cream 0–10V remain **variant verification holds**. No replacement manufacturer RFA proven to contain the missing exact variants was found in this bounded manufacturer/source review. This is not proof that one cannot be obtained from a manufacturer.

**Method/limits:** compared the saved Revit 2019 `PartAtom` type and material metadata of all four preserved CFB/RFA files, the original ZIP provenance and extracted Marset CAD, Kuzco's present product pages and manufacturer-linked Revit ZIPs, Marset's current USA pendant product/configuration and technical catalogue, and a separate third-party BIM listing. No family was opened/saved in Revit, no mesh/material/photometric binding was measured, and no native test was run. Saved `PartAtom` material fields are **type declarations**, not proof of actual geometric material association or appearance. Original OEM SHA-256 and ZIP byte comparisons were already confirmed in `MANIFEST.json` and `qa/OEM_BYTE_IDENTITY.json`; this report makes no change to them.

## Decision matrix and optional *external* type map

| Requested product/finish | Stored OEM RFA type | Source-backed mapping confidence | Decision |
| --- | --- | --- | --- |
| **Jarvis 41411-BG** (Brushed Gold) | **None.** Saved types: `41411-BK`, `41411-BN`, `41411-CH`, `41411-VB`, `41411-WH`. | Brushed Gold is a legitimate current manufacturer SKU and uses clear SSL suspension cord, but the saved type metadata has no `41411-BG` type or `JARVIS_BG_FINISH` type material assignment. Vintage Brass (`VB`) has a distinct assignment, `JARVIS_VB_FINISH`. | **HOLD exact BG.** Preserve family bytes; do not alias BG to VB. Ask Kuzco for revised BG-inclusive RFA/finish data if exact-finish family is essential. |
| **Malabar 402401BG-LED** | `4024014BG-LED` (extra `4` between `402401` and `BG`) | Plausible legacy family naming typo because the other type is `402401CH-LED` and Kuzco's exact public SKU is `402401BG-LED`. **No saved metal-finish material parameter** on either Malabar type; the BG appearance remains unproven. | **HOLD native visual/parameter check.** Maintain the literal name in untouched OEM. A downstream *selection manifest* may record `402401BG-LED => 4024014BG-LED (PROVISIONAL)`; never publish this as a verified finish or silently rename OEM types. |
| **Milca 494502M-GD** (Gold) | `494502M-GD` | **Exact stored SKU and dedicated type material:** `_494502_METAL_FINISH = 494502_GD_FINISH`; the `Model` field is `494502M`. Manufacturer specifies Gold stacked-slice shade and black braided cable. | **ACCEPT source/type identity, pending native QA.** Keep OEM unchanged; this is the sole stored exact type/finish match among four. |
| **Marset Dipping Light 13 Cream 0–10V A691-474-37-27K** | **None.** Closest *shape-only* old type: `A691-240` (13.5 cm White, 220–240 V TRIAC); `A691-250` is 13.5 cm White, 24 V/no driver. | Neither is Cream, current US 0–10V, or correct canopy. The manufacturer 2025 USA code matrix lists `A691-474-37-27K` for 13 Cream 0–10V, whereas the 2019 RFA lists only legacy White/Blue/Green/Amber/Pink colors for 13, 20 and 30. | **HOLD exact variant.** Retain OEM RFA and manufacturer 13 CAD as geometry references. Do not schedule `A691-240` as the selected product or pass its TRIAC/24V data to US 0–10V. |

External map is advisory metadata for specification/provenance; it **must not** become an automatic Revit type substitution. An exact scheduled selection remains the requested manufacturer SKU in each row, with held cases marked unresolved.

## Jarvis — BG type/finish conflict

**Unchanged RFA:** `E:\Claude\3D-Model-Workflow\output\belmont_ph_bedside_pendants_20261017\families\41411 - Jarvis.rfa`  
**Original manufacturer source ZIP:** `E:\Claude\3D-Model-Workflow\output\belmont_ph_bedside_pendants_20261017\sources\kuzco\REVIT-41411-Jarvis.zip`  
**RFA SHA-256:** `043b83525d3b4be656160d6ef0187a78d067eae0d9eec4a2e720a292b055deed`

- Type-to-material metadata: `41411-BK = JARVIS-BK_FINISH`, `41411-BN = JARVIS_BN_FINISH`, `41411-CH = JARVIS-CH-FINISH`, `41411-VB = JARVIS_VB_FINISH`, `41411-WH = JARVIS_WH_FINISH`. No BG type or BG material *assignment* appears in `PartAtom`; the full internal material library was not enumerated. All list `METAL_FINISH` as a Revit Material parameter, though actual geometry linkage is unverified.
- Manufacturer's current design is a **clear glass cylinder around a separate aluminum socket housing**, body diameter 2.75 in × height 12.625 in, canopy diameter 4.75 in × height 0.25 in; GU10 bulb **not included** (up to 50 W) and max 120 in clear SSL wire for BG. A material substitution must retain clear glass and distinguish the metal body. The hanging wire length does not define rigid body height.
- All five saved types reference `ledspot_50w_gu10_865_36d-ies.ies`. This is a preselected generic GU10 photometric filename; **no specific supplied 2700 K lamp or light distribution is established**. It is not exact BG product photometry.
- The manufacturer's current public **REVIT Files** link resolves to the already preserved `REVIT-41411-Jarvis.zip`, containing the above original family. In this audit no later official BG-inclusive RFA or verified third-party exact BG RFA was established.

**Required native decision:** inspect OEM geometry and exposed material bindings in an isolated Revit 2025 project and request factory BG digital finish data/revised family if needed. Preserve `41411-VB` as a distinct Vintage Brass product; it cannot be assigned to BG by renaming or by resemblance alone.

## Malabar — probable typo plus incorrect photometry

**Unchanged RFA:** `E:\Claude\3D-Model-Workflow\output\belmont_ph_bedside_pendants_20261017\families\402401LED-Malabar.rfa`  
**Original manufacturer source ZIP:** `E:\Claude\3D-Model-Workflow\output\belmont_ph_bedside_pendants_20261017\sources\kuzco\REVIT-402401-LED-Malabar.zip`  
**Manufacturer BG IES archive:** `E:\Claude\3D-Model-Workflow\output\belmont_ph_bedside_pendants_20261017\sources\kuzco\IES-402401-LED-Malabar.zip`  
**RFA SHA-256:** `e580b3bc8d59392eb21a39ce409635fb0efed3a05f8339f3ac6e8f38aeef24da`

- Kuzco explicitly labels the product **`402401BG-LED`**, alongside CH, and specifies an integrated **6 W/3000 K/90 CRI** LED, **BG 248 delivered lumens**, optional ELV 100–10% dimming, body diameter 3 in × height 9.5 in, canopy 4.75 in × 0.375 in, and clear outer / frosted inner acrylic. The official prose sometimes describes default chrome trim; use variant-specific drawings/photographs when verifying the BG plating.
- The RFA's two saved types are exactly `4024014BG-LED` and `402401CH-LED`. The extra `4` in the first type likely reflects a saved-name error; this is **interpretation**, not a verified correction.
- **Confirmed metadata defect in both types:** `Photometric_Web_File = 401214WH-LED - Mina.IES`, which names a different Kuzco model (Mina 401214), not Malabar. Both types also list `Apparent_Load = 5 VA`, inconsistent with the manufacturer's current 6 W input. `saved_light_source_flag = Yes` does not prove the correct photometric web is attached to a live emitter.
- The preserved separate official Malabar IES ZIP contains **`IES-402401-LED-Malabar/402401BG-LED - Malabar.IES`**, 41,684 bytes (LM-63-2002; luminaire `Malabar - 402401BG - LED`; test 3021-25, 2025-01-31). The CH-specific IES is different and should not be substituted for BG.
- There is no material-typed `METAL_FINISH` property in the two saved `PartAtom` types. Appearance may be driven by geometry, hidden parameters or internal material assignment, which requires Revit inspection; the presence of `BG` in a misspelled type label is insufficient proof.

**Required native decision:** load literal `4024014BG-LED` in an **isolated disposable** Revit 2025 project; verify its actual plating, acrylic layering, globe/cone silhouette, ceiling host, material associations, and energy/photometric values. Audit the actual source, then if the prime authorizes a controlled **separate working copy**, bind the factory BG IES and fix the saved lighting metadata; no change is made to the OEM file here. Do not label the current archive as BG photometrically verified.

## Milca — correct GD finish type, fixture/lamp separate

**Unchanged RFA:** `E:\Claude\3D-Model-Workflow\output\belmont_ph_bedside_pendants_20261017\families\494502M-Milca.rfa`  
**Original manufacturer source ZIP:** `E:\Claude\3D-Model-Workflow\output\belmont_ph_bedside_pendants_20261017\sources\kuzco\REVIT-494502M-Milca.zip`  
**RFA SHA-256:** `a99377ec2f1a7204f336951bd92494889419d057ef420add2abf24606376f540`

- Exact type `494502M-GD` sets material `_494502_METAL_FINISH = 494502_GD_FINISH` and `Model = 494502M`. Other types are BK/BN/GY. One unrelated saved GY type says `Model = 494502L`; this metadata inconsistency does **not** change the exact GD type.
- Manufacturer's size for the *M* variant: body diameter 2.375 in × height 10.875 in; canopy diameter 4.75 in × height 0.375 in; black braided cord up to 120 in. Shade is gold stacked aluminum slices and an open downward GU10 lamp cavity. The GU10 bulb is **not included**.
- The saved GD type says `Lamp = Incandescent (Gu10)`, `Apparent_Load = 60 VA`, and `Photometric_Web_File = ledspotmv_4-6-50w_gu10_par16_827_36d_ies.ies`. These are model defaults **not evidence of an included/incandescent lamp or approved 2700 K bulb**; Kuzco lists GU10 50 W maximum with actual lamp selection pending.

**Required native decision:** confirm material is visibly bound to the stacked slices, black cable and downward aperture are accurate, source body/canopy bounds are correct, and face/ceiling host works. Preserve OEM family and keep bulb SKU/lighting performance as separate selection data.

## Marset Dipping Light 13 — old product variant in valid OEM geometry carrier

**Unchanged RFA:** `E:\Claude\3D-Model-Workflow\output\belmont_ph_bedside_pendants_20261017\families\MARSET_Interior-Lighting-Fixture-Suspended_Dipping-Light.rfa`  
**Manufacturer 13 3D CAD:** `E:\Claude\3D-Model-Workflow\output\belmont_ph_bedside_pendants_20261017\sources\premium\extracted_exact_candidates\lamp_marset_dipping_light_13.dwg`  
**Manufacturer 13 OBJ:** `E:\Claude\3D-Model-Workflow\output\belmont_ph_bedside_pendants_20261017\sources\premium\extracted_exact_candidates\lamp_marset_dipping_light_13.obj`  
**Factory UL/0–10 V installation:** `E:\Claude\3D-Model-Workflow\output\belmont_ph_bedside_pendants_20261017\sources\premium\extracted_exact_candidates\Assembly_Instructions_Dipping_Light_13_0-10_UL.pdf`  
**RFA SHA-256:** `c5b1206598b104caa8e1f23a555129c6c86f05e707f58ff1dc091c6bf23a6a74`

- Current Marset USA product configurator offers size **13 / Cream / LED Dimmable 0–10V**. Its USA specification/code matrix identifies **`A691-474-37-27K`** with a 5.3 in glass globe, 6 W, 2700 K / CRI 90 / 203 luminaire lumens; 0–10V canopy diameter `4.3 in and height `1.8 in. Confirm final canopy mounting and control topology against the UL instructions/electrical submittal.
- The saved Revit 2019 manufacturer family has **30 legacy types**. The ten 13 cm variants are `A691-240`–`244` (white/blue/green/amber/pink; 220–240 VAC TRIAC) and `A691-250`–`254` (same colors; 24 V/no driver). There is **no saved Cream**, `A691-474-37-27K`, or 0–10V type. The saved 13 cm White TRIAC `A691-240` has `Screen.Material = MARSET.Dipping.White`, `Diameter = 13.50 cm`, `Canopy.Diameter = 4.80 cm`, `Canopy.Height = 13.40 cm`, and `Photometric_Web_File = A691-240 (CL041A20F001G).IES`. These canopy **parameter labels/values** do not match the current USA 0–10V canopy; confirm actual solids before interpreting them as a geometry defect.
- Old type metadata has additional reliability issues: `A691-260` lists `Code = A691-270`; all legacy types list `Apparent_Load = 230 VA` despite much lower nominal LED watts. Do not reuse old electrical fields for the selected 0–10V product.
- The preserved OBJ geometry names a sidecar `lamp_marset_dipping_light_13.mtl` and has basic numeric `usemtl` assignments; the extracted OBJ itself does not identify a **Cream** finish. Its native geometry is still useful as a manufacturer-sourced silhouette reference. The saved 13 off-white `A691-240` IES is **not** a demonstrated photometric match for `A691-474-37-27K` Cream/0–10V.
- The manufacturer pendant product page's current **BIM-rvt** link returns the **same original official manufacturer archive URL** already captured. An additional manufacturer-authored BIMobject listing (`Dipping_Light_Pendant`, edition 1, published 2023-02-06) exists, but no downloadable bytes/variant table were examined there, so it is **not** an established later exact-version replacement.
- Marset exposes a separate official **Textures library** archive at https://www.marset.com/wp-content/uploads/MARSET-TEXTURES.zip . A lightweight HTTP HEAD request on 2026-10-17 returned **200**, `application/zip`, **94,277,867 bytes**. It was deliberately not transferred or unpacked in this low-resource audit. Whether it contains current Cream ring-paint textures is **unknown**. Manufacturer explicitly says the layered paint makes individual glass spheres vary; generic flat white is not an accurate Cream appearance.

**Required native decision:** compare 13 RFA and exact manufacturer DWG/OBJ shapes, then obtain either a revised Cream 0–10V RFA from Marset or an explicitly approved, separate *derivative* visualization type with factory-fidelity Cream appearance and correct US canopy/control metadata. Maintain original OEM untouched and identify the derivative distinctly. No such derivative is requested or built by this worker.

## Revit 2025 isolation/acceptance requirements for prime

1. **Do not modify the active 651 Belmont project or save OEM copies in place.** Previous isolated Revit 2025.4.5 startup crashed before the test script (`qa/NATIVE_RUNTIME_HOLD.json`). Resolve startup isolation before accepting any family as native-verified.
2. In a disposable Revit project, open each original, enumerate native `FamilyManager.Types` and parameters, confirm material assignment to solids/surfaces and compare actual 3D size against manufacturer body and canopy separately. Native warning/open/reopen, ceiling/face placement and cord adjustment are independent gates.
3. For Malabar specifically, inspect live `Photometric_Web_File`, embedded/web file resolution and emitted source values, with **factory BG IES** as the authority. For Jarvis/Milca, specify the separate GU10 lamp before requiring 2700 K glare/beam or lumen accuracy. For Marset, check actual voltage/dimming, Cream appearance and canopy on US UL 0–10V, not legacy 220–240 V TRIAC metadata.
4. Any authorized corrected copy must carry its own filename/hash and provenance. Keep current manufacturer source RFAs and ZIP members unchanged, and preserve `MANIFEST.json` source hashes. Release/Drive delivery still requires native load, visual verification and package readback.

## Primary public references and source receipts

- Kuzco Jarvis current product and REVIT Files: https://kuzcolighting.com/products/jarvis-41411-kuzco ; exact saved metadata `E:\Claude\3D-Model-Workflow\output\belmont_ph_bedside_pendants_20261017\qa\OEM_STORED_METADATA.json`.
- Kuzco Malabar current product and REVIT/IES links: https://kuzcolighting.com/products/malabar-402401-led-kuzco ; source photometric identification `E:\Claude\3D-Model-Workflow\output\belmont_ph_bedside_pendants_20261017\sources\kuzco\OEM_SOURCE_RESEARCH.md`.
- Kuzco Milca M current product: https://kuzcolighting.com/products/milca-494502m-kuzco .
- Marset USA pendant, current BIM and texture links: https://www.marset.com/usa/indoor-lighting/pendant-light-fixtures/dipping-light-pendant/ ; code/photometric matrix in Marset USA catalogue https://www.marset.com/wp-content/uploads/catalogos/working-catalogue-usa-2023/MARSET_WORKING_CATALOGUE_2025_USA.pdf .
- Additional manufacturer BIMobject listing, **not inspected as an alternate RFA**: https://www.bimobject.com/en-us/marset/product/Dipping_Light_Pendant .
- Full provenance, SHA-256 and all downloaded manufacturer filenames: `E:\Claude\3D-Model-Workflow\output\belmont_ph_bedside_pendants_20261017\MANIFEST.json`, `E:\Claude\3D-Model-Workflow\output\belmont_ph_bedside_pendants_20261017\sources\kuzco\SOURCE_MANIFEST.json`, `E:\Claude\3D-Model-Workflow\output\belmont_ph_bedside_pendants_20261017\sources\premium\OEM_SOURCE_MANIFEST.json`.

**Audit status:** `OFFLINE_RECONCILIATION_COMPLETE; OEM_ORIGINALS_UNMODIFIED; NATIVE_2025_VARIANT_VERIFICATION_PENDING`.
