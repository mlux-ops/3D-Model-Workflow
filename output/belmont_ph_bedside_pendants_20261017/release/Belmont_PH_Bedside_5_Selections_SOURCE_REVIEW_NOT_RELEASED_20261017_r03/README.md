# Belmont PH bedside pendants — R03 SOURCE REVIEW, NOT RELEASED

This review covers all five selections using four untouched OEM RFAs plus official Schneid No.2 CAD. It is not a completed five-RFA package. No family passed native Revit 2025 QA in this task and no Stucco RFA was created.

Root: `E:\Claude\3D-Model-Workflow\output\belmont_ph_bedside_pendants_20261017`.

| Selection | Included original family / CAD | Current hold |
| --- | --- | --- |
| 41411-BG | `E:\Claude\3D-Model-Workflow\output\belmont_ph_bedside_pendants_20261017\families\41411 - Jarvis.rfa` | FINISH_HOLD: stored types BK, BN, CH, VB and WH; BG absent. Do not substitute VB for BG. |
| 402401BG-LED | `E:\Claude\3D-Model-Workflow\output\belmont_ph_bedside_pendants_20261017\families\402401LED-Malabar.rfa` | FINISH_HOLD: literal saved type 4024014BG-LED contains an extra 4; actual metal/optic assignments unverified. PHOTOMETRY_HOLD: saved file names Mina 401214WH-LED, not Malabar. |
| 494502M-GD | `E:\Claude\3D-Model-Workflow\output\belmont_ph_bedside_pendants_20261017\families\494502M-Milca.rfa` | STORED_TYPE_MATCH: exact 494502M-GD with 494502_GD_FINISH; native geometry/finish QA pending. |
| A691-474-37-27K | `E:\Claude\3D-Model-Workflow\output\belmont_ph_bedside_pendants_20261017\families\MARSET_Interior-Lighting-Fixture-Suspended_Dipping-Light.rfa` | VARIANT_HOLD: 30 legacy types; no exact requested SKU, no Cream material or 0-10V type. 13 cm types show 13.5 cm diameter, Triac or 24V, White/Blue/Green/Amber/Pink; stored canopy 4.8 cm diameter x 13.4 cm height differs from current US 0-10V canopy. |
| STUCCO-II-CLAY-UL | `E:\Claude\3D-Model-Workflow\output\belmont_ph_bedside_pendants_20261017\sources\premium\schneid_official_no2` | Five original CAD formats; no RFA in factory archive; native import/build/QA pending. |

Schneid dimensions are corrected from the preserved manufacturer PDF: ceramic body D105 × H265 mm, ceiling rose D140 × H140 mm. Earlier 100 mm body/105 × 125 mm rose notes mixed No.1 and No.2. The OEM STL whole assembly is approximately 139.934 × 139.867 × 1309.000 source units, including the factory default suspension and bulb; this is not a body measurement. STEP explicitly declares millimetres. STL units are inferred from that same-package STEP and physical component sizes.

The official 19-member Schneid ZIP has no RFA. All five No.2 CAD extracts were re-compared byte-for-byte with that archive and their recorded SHA-256. The full 186,260,124-byte archive remains intact locally at `E:\Claude\3D-Model-Workflow\output\belmont_ph_bedside_pendants_20261017\sources\premium\originals\SCHNEID_Stucco_Share_3D.zip`. This review ZIP includes the five exact No.2 files and provenance receipt, not the unrelated No.1/No.3 CAD or the complete multi-product archive.

Factory STL front/oblique previews were visually inspected: they show the No.2 paired sculpted pieces, suspension and exposed bulb. Neutral schematic shading does not establish the Clay finish, E26 UL socket, photometry, or a native solid. The STL has many disconnected topological pieces; they are not semantic CAD parts. Prefer the original Rhino/STEP for native import instead of manufacturing new geometry from those triangles.

Native recovery is unresolved. The previous probe crashed before its script. An existing Revit process (PID 11796, started 01:54 local, parent explorer.exe) is not owned by this worker; its document state is unknown. It was not attached to or stopped. No new resource-heavy launch was attempted. Native QA preparation and process evidence are described in `E:\Claude\3D-Model-Workflow\output\belmont_ph_bedside_pendants_20261017\runner\RECOVERY_COORDINATION_R02.md`.

The prepared read-only validator requires a newly owned, document-free Revit 2025 process. It never saves OEM RFAs, hashes originals before/after, creates real ceiling hosts in disposable unsaved projects, and records types, materials, physical solid bounds and true LightFamily sources. It has passed compilation and offline safety checks only. Real native API calls and visual/source fidelity gates remain untested.

Native type/geometry/material/host/light checks, exact variant verification and product visual approval must pass before release. Jarvis BG and Marset Cream 0–10V are absent from saved OEM types. Malabar has a probable name typo, unverified plating and a saved IES filename for a different fixture. No type was renamed, substituted, repainted or rebuilt to hide these holds.

No user Revit model or external settings were changed. No Drive upload was attempted because full QA has not passed. R01/R02 archives are retained as superseded source-review history; R03 corrects the metadata count to distinguish 19 source downloads from 11 ZIP archives.

Selection/provenance: `E:\Claude\3D-Model-Workflow\output\belmont_ph_bedside_pendants_20261017\SOURCE_SELECTION.md`.
Machine manifest: `E:\Claude\3D-Model-Workflow\output\belmont_ph_bedside_pendants_20261017\MANIFEST.json`.
Independent source review: `E:\Claude\3D-Model-Workflow\output\belmont_ph_bedside_pendants_20261017\qa\SCHNEID_OEM_CAD_REVIEW_R02.json`.
Independent type audit: `E:\Claude\3D-Model-Workflow\output\belmont_ph_bedside_pendants_20261017\qa\OEM_VARIANT_RESOLUTION.md`.

Offline reproduction:

```powershell
python.exe 'E:\Claude\3D-Model-Workflow\output\belmont_ph_bedside_pendants_20261017\scripts\extract_oem_unchanged.py'
python.exe 'E:\Claude\3D-Model-Workflow\output\belmont_ph_bedside_pendants_20261017\scripts\inspect_saved_oem_metadata.py'
python.exe 'E:\Claude\3D-Model-Workflow\output\belmont_ph_bedside_pendants_20261017\scripts\check_native_readonly_safety_r02.py'
python.exe 'E:\Claude\3D-Model-Workflow\output\belmont_ph_bedside_pendants_20261017\scripts\verify_source_review_r02.py'
```

The factory STL preview script additionally uses locally available trimesh/numpy/Pillow/pypdf. Native Revit scripts are preparation artifacts, not completed RFAs. Source paths refer to this task root; internal ZIP members retain their normal archive-relative names.
