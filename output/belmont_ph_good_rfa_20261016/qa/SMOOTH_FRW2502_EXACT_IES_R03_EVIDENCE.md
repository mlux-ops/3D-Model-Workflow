# Smooth FR-W2502-52L-SB/MB — exact official IES recovered

**2026-10-16 status:** Exact official WAC/Modern Forms LM-63 source VALIDATED. Native Revit R03 IES binding **not executed**; prime controls that gate. Existing R02 Soft Brass/Matte Black finish and 52-inch radial-sweep pass are preserved in the guarded script.

The current manufacturer [Smooth product](https://modernforms.com/product/smooth/) does not show a separate IES download, but the following **official manufacturer-hosted archive** exists:

- **Official source URL:** https://modernforms.com/images/products/IES_FILES/FR-W2502-52_IES.zip
- Local exact archive: `E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016\sources\photometry\MFR1415595_FR-W2502-52_IES_official.zip` — 10,345 bytes, SHA256 `c9efc10fbe0789df3e85759ba587572bff0fb13a69e4e966571ae25b374b170a`.
- The ZIP has **one member**, `FR-W2502-52L.IES`. CRC verified.
- Extracted exact file: `E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016\sources\photometry\FR-W2502-52L.IES` — 25,749 bytes, SHA256 `6044dda98294020d03decd14ad118be2717845536597d1ca9bb9cc296fdcda8e`.
- Independent validator: `E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016\qa\validate_smooth_frw2502_official_ies.py`; immutable PASS receipt `E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016\qa\smooth_frw2502_ies_source_validation_20261016.json`, SHA256 `b9d8836a641a1c4e6b912d5aabe36f7d738110a389e615f61e9f38c2c3b7c622`.

LM-63 test header: `IESNA:LM-63-2002`, `[TESTLAB] WAC Lighting`, `[MANUFAC] WAC Lighting`, `[LUMCAT] Ceiling Fans`, `[LUMINAIRE] FR-W2502-52L`; test 2024-11-25 and issue 2024-11-26. `TILT=NONE`, photometric Type C, one lamp, 181 vertical and 17 horizontal angles, **3,077 candela points**, valid ascending 0–180° and 0–360° grids. No negative candela. Measured input **16.7549 W**, lamp flux **707.09 lm**. Independent solid-angle integration yields **707.00955 lm**, a 0.011% difference. This agrees with the OEM specification's integrated 16 W LED / **707 delivered lm**, with photometric measured wattage differing by 4.72% from nominal. The photometry identifies the exact model family; **the IES does not separately identify SB/MB finish or selectable CCT**. No finish/CCT variant-specific performance is invented.

The OEM RFA's `Photometric Web File` type parameter already contains the text `FR-W2502-52L.IES`, and the native original QA detected a light-source `Element` 3044. These facts **do not independently verify** a Revit `LightFamily` or `PhotometricWebLightDistribution`. The R03 native script requires both objects and a writable `FBX_LIGHT_PHOTOMETRIC_FILE` string; it refuses to save if the actual source is not a real compatible emitter family. It preserves the R02 material/geometry fingerprint, stages the saved candidate, reopens and verifies the LightType *and* family parameter, and refuses overwrites. The exact companion IES file should accompany any candidate release until embedded cache/portability is proven.

## Prime-only native run

```powershell
& 'D:\Games\pyRevit-Master\bin\pyrevit.exe' run 'E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016\scripts\bind_smooth_frw2502_r03_exact_ies.py' --revit=2025
```

Source: `E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016\candidates\ModernForms_Smooth_FR-W2502-52L_SBMB_R2025_R02_PARTIAL_UNAPPROVED.rfa` (SHA256 `f1741c711a07a26101c550b580a2db6be99bc4d3689cb75104eaafb0834379db`).

On successful native capability and save/reopen gates, NEW candidate: `E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016\candidates\ModernForms_Smooth_FR-W2502-52L_SBMB_R2025_R03_IES_UNAPPROVED.rfa`.

NEW binder receipt whether success or blocker: `E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016\qa\smooth_sbmb_r03_ies_native_bind_receipt.json`.

Further required independent native acceptance: preserve the R02 measured **1321.692521 mm** radial sweep (nominal 1320.8 mm, tolerance 1 mm), correct ceiling-face hosting, 0 warnings, correct three matte-black blades and brass housing, photometric web display and lit preview, and no change to 13 unassigned mixed CAD import surfaces. Even a successful optical bind leaves BIM circuit connector creation and unverified hidden CAD finish identities unresolved.
