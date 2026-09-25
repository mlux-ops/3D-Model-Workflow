# f03_1241670 - AERIN / Visual Comfort Brenta Single Sconce

Requested deliverable: native Revit 2025 face-based Lighting Fixtures family for the Bronze finish.

## Exact option

The assigned Lightology URL resolves to the Hand-Rubbed Antique Brass option (ARN 2473HAB-CG / VCG1241669). The requested Bronze option on the same Brenta product is ARN 2473BZ-CG / VCG1241668, and that Bronze option is the build target.

## Verified manufacturer data

- Overall: 3.5 in W x 18.5 in H x 3.75 in extension.
- Backplate: 3.5 in x 5.25 in rectangle.
- Finish: Bronze; white glass.
- Dedicated LED, 2700K, 750 delivered lumens.
- Materials: brass and glass.
- Fixture can be installed vertically or horizontally; the family is modeled vertically and can be rotated on its host face.

## Geometry interpretation

The overall envelope and backplate dimensions are manufacturer-defined. The Bronze product photo shows two elongated glass cylinders emerging from a dark bronze center sleeve. The glass tube diameter, center sleeve diameter/height, backplate thickness, standoff depth, and minor edge radii are not dimensioned in the retrieved spec; they are photo-derived/inferred and are explicitly identified as such in the builder and family accuracy notes.

The task-local builder creates the family independently from the native face-based template. The preserved manufacturer RFA/DWG are references for measurement/validation only and are not repackaged or renamed as the deliverable.

## Native builder

`build_brenta.py` creates a Lighting Fixtures family from the Revit 2025 Generic Model face based template, adds editable Bronze / Clear Glass / 2700K Diffuser material parameters, saves and reopens the RFA, loads it into a disposable native project, places it on an actual wall-face reference, checks host-face state and orientation, verifies nominal bounds, substitutes each material into geometry, requires zero warnings, and exports front/side/oblique/material/hosted review views.

Prepared command:

`D:\Games\pyRevit-Master\bin\pyrevit.exe run E:\Claude\3D-Model-Workflow\output\lightology_20260923\f03_1241670\build_brenta.py --revit=2025`

READY_REVIT has now been sent successfully to prime. Prime is correcting the front-camera definition and owns the serialized native execution/review; this worker will not launch a second Revit run. Do not treat pyRevit exit code as evidence; `validation.json`, its timestamp/content, saved/reopened RFA state, host/material/warning gates, and exported images are the acceptance evidence. See `SOURCE_REVIEW.md` for the expanded source classification and drawing-derived mounting-center datum.

