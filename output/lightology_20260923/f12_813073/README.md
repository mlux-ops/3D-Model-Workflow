# F12 — Visual Comfort Modern Orbel Wall Sconce

Selected configuration: **TLG1279684 / 700WSOBLNB, Natural Brass, Frosted, bulb not included**. The provided base product URL defaults to Aged Brass; CoS fetch of `option_id=1279684` verified the Natural Brass selection.

Authoritative Lightology dimensions are 5 in W × 12.9 in H × 6.7 in D, with a 5 in W × 12.9 in H × 0.7 in D rectangular backplate. The source PDF also specifies Glass/Brass/Steel, one JCD/G9/5W/120V LED lamp (not included), and up-or-down installation.

The family builder uses the actual Revit 2025 `Generic Model face based.rft`, changes category to Lighting Fixtures, creates editable `Metal Finish` and `Glass Finish` material parameters, models a rounded rectangular backplate, full-height perpendicular brass blade, concealed socket boss, and a true hollow frosted-glass sphere with a rear shell opening. It includes no MEP connector and no photometric source.

The 5 in globe diameter, lower globe center, blade thickness/projection, 0.14 in glass thickness, rear opening, and concealed socket dimensions are inferred from the preserved Natural Brass product photograph. They are not manufacturer dimensions. Printed overall dimensions control the family envelope.

Native Revit build/QA is pending PRIME's exclusive slot grant. Required command:

`D:\Games\pyRevit-Master\bin\pyrevit.exe run E:\Claude\3D-Model-Workflow\output\lightology_20260923\f12_813073\build_f12_orbel.py --revit=2025`

Native acceptance requires: saved RFA reopen, Lighting Fixtures category, true native wall-face host, mounting-normal record, 5 × 12.9 × 6.7 in geometry envelope, both material substitutions reaching geometry, zero family/project warnings, and exported front/side/oblique/material PNGs.
