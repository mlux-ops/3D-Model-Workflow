# Extended native family acceptance — October 14, 2026

Executed only through authenticated loopback bridge in isolated Revit process **27208**. Every native request verified that process identity and targeted a family created by this run or the explicitly saved/reopened owned RFA. Existing production models, add-in binaries and shared parameter files were untouched.

**True Width/Depth/Height parametric synthetic Casework passed on the initial attempt.** Width and Depth labels constrain native extrusion faces through real family dimensions; Height associates the native extrusion-end parameter. No mesh/DirectShape or rebuilding between scenarios was used.

| Native case | Width (ft) | Depth (ft) | Height (ft) | Native solid volume (ft³) |
| --- | ---: | ---: | ---: | ---: |
| Flex A | 2.5 | 1.75 | 3.5 | 15.3125 |
| Flex B | 1.25 | 1 | 2 | 2.5 |
| Restored default | 2 | 1.5 | 3 | 9 |

Each flex case verified all three actual native bounds, parameter readbacks and volume. The transaction group rolled back and restored the original dimensions. The family saved to `cabinet-attempt-1-Codex_Parametric_Casework.rfa`, then explicitly closed and reopened. Native three-axis parameter/bounds/volume readbacks passed again; SHA-256 remained unchanged across reopen.

Basic native **blend, sweep, void, reference plane, formula, and nested family-definition loading** passed on their first attempts. Revolution creation and bounds also succeeded initially; its native curved volume was **9.42476415120661 ft³**, compared with analytic **9.42477796076938 ft³**. The initial `1e-6` absolute-volume gate failed. One assisted, read-only verification repair applied explicit `1e-4 ft³` tolerance, justified by installed Autodesk `RevitAPI.xml` Solid.Volume remarks (lines 176602–176604): native volumes can approximate curved surfaces through tessellation. Original failed gate remains in the report; no geometry was changed to pass it.

Material parameter creation initially rolled back because `Material` is a nested `SpecTypeId.Reference` property, unavailable through the root-property shorthand. One assisted argument repair used full `autodesk.spec.aec:material-1.0.0`. The native form material association and actual form Material parameter readback both passed with the assigned native material. The original rejected operation UUID and receipt remain intact.

`extended-family-report.json` and `controller-receipts/` retain every original operation UUID, native request, status and result. `verify_evidence.py` independently re-derives geometry gates from native receipts and request values without calling Revit; `independent-verification.json` records that result. Successful repaired outcomes remain distinguished from unaided first-attempt outcomes.

These are numerical tests of synthetic native families. The box has no detailed cabinet components or manufacturer fidelity. Void creation does not prove a cutting relationship. A loaded nested definition does not prove nested instance placement. Material readback does not prove appearance or rendered fidelity. Visual, production-design, hosting, clearance and delivery acceptance remain separate gates.
