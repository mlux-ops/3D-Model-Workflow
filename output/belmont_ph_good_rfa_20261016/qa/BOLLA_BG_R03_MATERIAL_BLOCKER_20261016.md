# Bolla PD3106-BG — final material identity gate (2026-10-16)

**Status: HOLD; no Brushed Gold R03 candidate RFA or converter released.**

## Verified source

The saved official-BG-IES native candidate is
`E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016\candidates\Kuzco_Bolla_PD3106_BG_R2025_IES_R02.rfa`,
SHA256 `1d107108de7cf0a40562e764e5e73c8a4ae935861b1a3fc86f0e60a481b86c5d`.
Its receipt at
`E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016\qa\bolla_bg_ies_r02_native_receipt.json`
confirms the OEM `PD3106-BG - Bolla.IES` filename after native reopen, but
does **not** verify portable embedded photometric caching or a rendered
distribution. Preserve companion IES
`E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016\sources\photometry\PD3106-BG - Bolla.IES`
(SHA256 `9e9f70e2eecc3b1c4130bea2f3fcb3c5a1798fb61363185348b635cd71737ce4`).

Official manufacturer: https://kuzcolighting.com/products/bolla-pd3106-kuzco
The Brushed Gold variant uses a gold-finish steel canopy/hardware, black
suspension cord, clear outer glass and opal inner glass.

## Native geometry and current exact limits

| ID | Existing native material | Component identity | Action |
|---|---|---|---|
| 4435 | Material 1742, `Glass`, six faces | Clear outer glass | Preserve |
| 5101 | Material 8722, `Glass Frosted`, 16 faces | Frosted/opal inner glass | Preserve |
| 4715 | Eight unassigned faces | Small metal neck adjacent to glass | Gold assignment plausible, **not** yet tested |
| 7721 | Fourteen unassigned faces, one Revit Revolution | Mixed 510 mm canopy/suspension component | **No gold blanket material**; black wire must be separated |

Original native material probe:
`E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016\qa\inspect_oem_material_parts.json`,
SHA256 `2ee88654c081a629fa324681703497a72adff29a2481a676f51b98d03b2213b3`.

The two failed neck converter attempts had mismatched **measurement
algorithms**. The probe's sparse face triangulation produced neck 4715 XY
14.8 × 17.09 mm, while its separate analytic-edge channel produced
17.07 × 17.09 mm. Revit's subsequent analytic Revolution measurement
17.086 × 17.086 mm agrees with the latter, rather than establishing a
changed solid. This does not justify any arbitrary tolerance increase.
Original `build_bolla_pd3106_bg_neck_r02.py` and
`build_bolla_pd3106_bg_neck_r02_fix01.py` remain historical failed scripts.
Both stopped before SaveAs. The IES R02 candidate remains unchanged.

For 7721 the old probe only records one aggregate volume, face count,
materials (all unassigned) and overall bounds. It records neither the
individual face surface classifications nor each face's axial/radial
bounds, so a particular face cannot yet be verified as gold canopy
versus black cable. Face-index assignment without a fresh deterministic
native signature and source/photo confirmation would be speculative.

## Prepared next evidence gate, not executed

Read-only native IronPython script:
`E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016\qa\inspect_bolla_bg_r03_face_signatures.py`.
When prime runs in **isolated** Revit 2025, it creates a fresh no-overwrite
JSON at
`E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016\qa\bolla_bg_r03_face_signatures.json`.
It fingerprints the IES R02 family and original probe, then inspects each
of the 44 native faces for mesh/analytic bounds, surface type, area,
paint/material IDs and stable face references where supported.
This is a **probe only**; the resulting report requires review. It cannot
declare canopy/black cable surfaces independently of geometry evidence.
Python 3.14 compilation passed. No native execution occurred.

**Full R03 release gate:** prove a stable exact face-to-part assignment
for the 14-face 7721 Revolution, match the manufacturer's metal/cord
picture, verify separate Brushed Gold and black appearances, preserve
both glass elements and the BG IES, then run independently guarded native
reopen, face/material, host, visual and photometric QA.
