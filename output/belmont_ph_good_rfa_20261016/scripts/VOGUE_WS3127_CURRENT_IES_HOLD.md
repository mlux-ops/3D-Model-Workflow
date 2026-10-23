# WS-3127-CH PH GOOD photometry release hold — October 16, 2026

**Decision: do not publish R03 yet.** No current manufacturer-certified
IES matching 40.6 W / 2993 delivered lm has been found. The official live
Modern Forms product page still links an older IES family ZIP.

Official page: https://modernforms.com/product/vogue/

Current official specification:
https://modernforms.com/dynamic-specsheet/?download=specs5&ppid=1546

Official IES download (stale test):
https://modernforms.com/images/products/IES_FILES/WS-3120_IESF.zip

| Item | Source and value |
| --- | --- |
| Current fixture | WS-3127-CH, 27 inches, Chrome / mouth-blown opal |
| Current electrical | 120 VAC, 50/60Hz, 40.6 W integrated ACLED; 277V special order |
| Current CCT | 3000K standard CH; 2700K/3000K/3500K selectable |
| Current output | 3895 LED lm, 2993 delivered lm, CRI 90 |
| Legacy official WS-3127.IES | TESTDATE 2017-11-09; 38.9472W, 2424.9 lm |
| Legacy IES SHA256 | 6c0a0da084b9fde830f254d8afff7d7b92df1a8e13cca7334e2c4e7e92c4837d |
| Existing Chrome/opal R02 SHA256 | e5d49df849079974e7e1e3e3718a898e7f9671d0ca03633f4dead35fc1c0d9b8 |

Native original family QA in
`E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016\qa\oem_qa_r03.json`
reports one Light Source (ID 3653), **zero electrical connectors** and
`Photometric Web File = WS-3127.IES`. The Chrome/opal R02 material
candidate was saved/reopened separately; its maker did not alter connector
or photometry. No Revit R03 execution occurred in this task.

Two source-only scripts were prepared:

- `E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016\scripts\prepare_vogue_ws3127_current_ies_r03.py`:
  explicitly fails until manufacturer current-IES verification is provided,
  then binds via Revit Lighting.LightFamily/LightType and the family type
  photometric parameter. It preserves R02 chrome/opal material bindings.
- `E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016\qa\qa_vogue_ws3127_r03_photometry.py`:
  standalone read-only Revit 2025 QA for photometric source, connector
  presence, CCT/intensity, and electrical type values.

**Unresolved:** verified current 40.6W / 2993 lm IES, family electrical
connector, electrical apparent-power semantics, and IES emitter intensity
configuration. Do not adjust candela by 2993/2424.9 or call the old 2017
IES a current measured photometric distribution.

Feasible next steps: ask Modern Forms/WAC technical support for the
current exact WS-3127-CH default 3000K LM-63 file (including test date,
input wattage and manufacturer luminaire data). If no new file exists,
retain R02 with explicit photometric hold and use an independent lighting
calculation pending verified photometry. A new R03 should only be made
after source/version reconciliation. Missing MEP connector requires a
separately reviewed native geometry/electrical scope.
