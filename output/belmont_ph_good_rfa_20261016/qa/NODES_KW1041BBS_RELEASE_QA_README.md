# Nodes KW1041BBS independent Revit 2025 QA

**Status:** script ready; local Python compilation passed; native Revit run reserved for prime. Prior September architectural appearance approval preserved.

Accepted file: `E:\Claude\3D-Model-Workflow\output\lightology_20260923\release\Lightology_14_Face_Based_RFAs_R2025_Rev1\RFAs\Visual_Comfort_Nodes_KW1041BBS_Burnished_Brass_R2025.rfa`, 479232 bytes, SHA256 `446223760904a196d04c30cdd9f8676b0f67d46c0e91516080a160e8db91879f`.

Original approval: `E:\Claude\3D-Model-Workflow\output\lightology_20260923\prime_visual_review.json` records Nodes KW1041BBS acceptance for visualization. Its render, brass finish, angled reflector, milk-glass shade, pivot and backplate should be preserved.

Official exact model spec: https://www.visualcomfort.com/media/docs/spec_sheet/k/w/ss_kw1041bbs.pdf . Source option: https://www.lightology.com/index.php?module=prod_detail&prod_id=833919&option_id=833918 . Original install sheet: https://www.lightology.com/img/prod/pdf/vcstud-ig_kw1041-instr-20230426.pdf . Previous first-hand capture: `E:\Claude\3D-Model-Workflow\output\lightology_20260923\f07_833919\sources_and_inferences.json`.

Specifications: width 8 in; approximately 7.62 in height current OEM / 7.63 in former retailer and existing validated model; projection 5.5 in; backplate diameter 5.25 in and depth ~.12 in; milk shade 3.5 in diameter and 3.25 in axial length; metal Burnished Brass; G9 LED base, current OEM 3W maximum / 120V. Lamp not included. Historical merchant 60W data, if encountered, are not a validated substitute for current OEM rating. Native Revit material appearance is verified independently from electrical load.

Runner: `D:\Games\pyRevit-Master\bin\pyrevit.exe run "E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016\qa\nodes_kw1041bbs_release_qa.py" --revit=2025`

Script: `E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016\qa\nodes_kw1041bbs_release_qa.py` . Receipt: `E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016\qa\nodes_kw1041bbs_release_native_qa.json`.

The QA opens the exact accepted RFA, checks SHA before/after, source model/type/manufacturer, category, face placement, 8 x 7.63 x 5.5 in positive-volume solid envelope (0.05 in tolerance), native materials, actual substituted-face reach, native warnings and source URL field. It creates a temporary unsaved project, a wall, and an actual wall-face-hosted family instance. It records available light-family/IES/connector fields without making up data. Only a new JSON QA receipt is written. The original RFA and user's RVT are never saved.

**Expected disposition:** `ARCHITECTURAL_NATIVE_PASS_MEP_HOLD` if technical checks succeed, preserving prior accepted appearance. MEP release needs exact installed G9 lamp characteristics (watts, dimming, lumens, CCT), a native electrical connector, and defensible photometric distribution. No verified exact-product IES was included with the prior model.
