# 651 Belmont — Kuzco Bolla PD3106-BG, Revit 2025 project-load recovery

**Use `PD3106 - Bolla.rfa`.** This is the unmodified native RFA from Kuzco Lighting's official `REVIT-PD3106-Bolla.zip` download. The failed custom R05 family is excluded from this replacement package.

## Native Revit verification, November 1, 2026

- Opened original manufacturer RFA in Revit 2025.
- Loaded into a new, disposable Revit 2025 project using `FamilyDocument.LoadFamily(project)`.
- Placed one `Lighting Fixtures` instance using the supported `OneLevelBasedHosted` level-point placement route.
- Placement transaction committed; instance persisted in the document; no Revit warnings.
- This is verified in `E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_recovery_20261101\bolla_oem_clean\bolla_official_project_placement.json`.
- The live `25-012 651 W. Belmont_Issue for Construction_.rvt` was **not changed**.

## Revit usage

1. In Revit 2025, use **Insert > Load Family** and select this folder's `PD3106 - Bolla.rfa`.
2. Under **Architecture > Component > Place a Component**, select the `PD3106 - Bolla` family, `Type 1`.
3. Place it using the level-based placement method. This OEM model has `OneLevelBasedHosted` placement; do not attempt to host it directly to a ceiling face with a WorkPlaneBased API call.
4. Set and verify the required elevation, suspension/drop, and glass/hardware finishes in the project. The supplied RFA is unmodified manufacturer geometry; `Type 1` is the manufacturer type, not a separately proven customized Brushed Gold appearance.
5. `PD3106-BG - Bolla.IES` is the verified exact variant photometric companion. Configure/test its path separately if photometric rendering is needed; distributing the IES beside the RFA does not alone establish an embedded portable Revit photometric link.

## Source and verification

- Official Kuzco product: https://kuzcolighting.com/products/bolla-pd3106-kuzco
- Official manufacturer BIM archive: https://s3.us-west-2.amazonaws.com/catsy.870/REVIT-PD3106-Bolla.zip
- Exact `PD3106 - Bolla.rfa` SHA256: `8D84D0A6842B26CA3B8686F86948172349D1D1AEC04A75A2B68AF4463EF5C98A`.
- Exact `PD3106-BG - Bolla.IES` SHA256: `9E9F70E2EECC3B1C4130BEA2F3FCB3C5A1798FB61363185348B635CD71737CE4`.

## Earlier failed R05 diagnostic

The October customized `Kuzco_Bolla_PD3106_BG_R2025_R05_REPAINT_OPTICAL_DIAGNOSTIC_UNAPPROVED.rfa` opens standalone and can be transferred into a fresh project through the family-document API, but its freshly created level-point instance does **not persist after the placement transaction commits**. The manufacturer original **does** persist in the same test. This establishes a project-placement regression in the customized candidate; root cause within the custom material/paint/photometric changes has not been isolated to a single edit. Do not deliver the R05 as a functional replacement.
