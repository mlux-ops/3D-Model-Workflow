# M01 — Adella photographic material

## Worked example and source priority

1. `references/adella/crawl2.jpg`: the selected single-tile photograph.
2. `scripts/rebuild_adella_precision.py` and `output/adella_highres_review/VALIDATION.json`: authoritative processing example for this test.
3. `output/adella_highres_review/README.md`: map interpretation and native-render limitation.
4. `scripts/build_adella_revit.py`, `scripts/build_adella_vrmat.py`, and `output/adella/README.md`: native integration examples, subject to the corrections below.

The precision rebuild uses a **2560 x 1269** source, crop rectangle **(12, 12, 2548, 1257)**, 4096 x 2048 exported maps and an inferred **0.6 mm full height range**. Older notes describing a square 2560 source or 1.5 mm range are superseded for this test. The photo is not calibrated albedo or measured relief. Enlarging it does not create native 4K detail.

Historical evidence supports map integrity and prior Revit project reopen. It does not establish native V-Ray import/render success or eliminate observed render artifacts. Never use the existing files as an unquestioned visual gold standard.

## A — Reproduction

Generate new maps from the source photo using the corrected floating-point processing pipeline. Preserve horizontal nominal 24 x 12 in tiles, stacked layout, light grout and a **1/16 in joint**, yielding **24.0625 x 12.0625 in per repeat** (611.1875 x 306.3875 mm).

Required maps, all 4096 x 2048:

- Base color: RGB, 8-bit acceptable, interpreted as sRGB color.
- Bump/height: 16-bit grayscale; linear data, not gamma-corrected color.
- Normal: RGB16 PNG, tangent-space OpenGL convention, linear data. Verify bit depth from the PNG header, since some image libraries expose RGB16 as an 8-bit view.
- Roughness: grayscale or RGB data map; linear, with ceramic/grout response documented.

Keep floating-point values through filtering, resampling and gradient generation; quantize only on export. Report source and crop dimensions, output dimensions, height minimum/maximum and unique values. More than 1,000 height values is a useful quantization smoke check, not proof of smooth native rendering. The old 29,454 value count is historical evidence, not a required checksum.

Build a new Revit 2025 material in an RVT, with appearance color/bump connected to the new maps and matching physical scale. Provide an ADSKLIB through the native Material Browser, or disclose reuse of an existing library followed by an actual native update. **Library creation and library reuse are separate scorecard items.** Supply VRMAT and material-only VRSCENE with matching texture references and documented mapping.

## B — Controlled variation

Create a separately named **1/8 in grout** version, preserving the nominal tile size and photographic artwork. New repeat is **24.125 x 12.125 in** (612.775 x 307.975 mm). Update the generated grout region, height edge treatment, normal gradients, Revit color/bump repeat and V-Ray mapping instructions together. Changing only the README or UV scale does not satisfy the test.

In the example, `edge`, `mask` and gradient spacing determine joint treatment and surface normals. Review their physical meaning: do not simply substitute numbers without measuring the resulting border. A repeat with a centered boundary joint has half the joint on each opposite edge. Account for a separately documented bevel transition. At these dimensions, the grayscale grout core should total approximately 21 horizontal pixels and 21 vertical pixels across opposing edges at 4096 x 2048; allow 2 pixels for rasterization and report the measurement method. Do not count the wider bevel as grout.

## Required evidence and acceptance

1. **Maps:** source provenance, physical units, PNG dimensions/type/depth, finite processing values, precision checks, edge/grout measurements and a 2 x 2 repeat preview for each variant. Preview labels must identify illustrative shading versus a native render.
2. **Revit:** save/reopen new RVT; inspect connected bitmap paths and physical scales; create/update ADSKLIB; import into a second blank project and apply to a test face. Confirm both color and bump use the intended version's files, with no silent fallback to original directories.
3. **V-Ray:** import the VRMAT in a licensed native host, confirm material presence and bitmap resolution, and render. Parse XML/VRSCENE as additional checks only. Do not substitute a parsing pass for native import.
4. **Visual review:** render a surface spanning at least 2 x 2 repeats, at a frontal view and a grazing view under neutral lighting. Review tile scale, seams, relief banding, excessive/doubled bump and surface response. Record reviewer judgment separately from map statistics. Exact physical relief and calibrated color are not claimed.
5. **Portability:** extract the package into a different run subdirectory; explicitly repath native assets if necessary, reopen, and verify the effective paths. Do not delete or alter original maps to perform this test. Document required manual repathing honestly.
6. **Delivery:** baseline and variation maps, RVT, ADSKLIB, VRMAT, VRSCENE, adapted sources, setup notes, validation records and native evidence. Check ZIP integrity and file hashes; verify Drive metadata for final packages.

If V-Ray licensing/UI access blocks rendering, complete available work and record **maps pass / Revit pass or blocked / V-Ray blocked / overall partial** as appropriate. No complete material pass without native render review. This distinguishes infrastructure limitations from candidate reasoning errors.
