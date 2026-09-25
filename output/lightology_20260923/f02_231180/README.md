# f02_231180 - FLOS IC C/W1 Wall / Ceiling Light

Requested deliverable: native Revit 2025 face-based Lighting Fixtures family for the Brass / Opal Lightology 231180 option.

## Exact product and size

The assigned page identifies FLOS IC Wall / Ceiling Light by Michael Anastassiades, model / ID FU317859, Lightology spec FLO231180, Brass finish with Opal glass. The preserved Lightology line drawing explicitly dimensions the small option at 7.9 in globe diameter, 8.5 in overall height, 11 in projection, and 4.3 in wall-plate diameter. The larger Brass option FU317959 / FLO350493 is 11.8 x 12.4 x 15 in and is excluded.

## Preserved source evidence

source/lightology_231180_brass.jpg is the exact product side image and the main silhouette reference. It visibly establishes the spherical opal globe, shallow bell wall plate, vertical brass riser, rounded 90-degree elbow, long horizontal brass rail, and small brass contact cap at the globe. source/lightology_ic_wall_line.png supplies the printed dimensions. source/lightology_ic_wall_app1.jpg confirms the fixture can be installed in an equivalent rotated wall orientation. The Lightology specification PDF is preserved alongside them.

## Geometry interpretation

The printed dimensions are authoritative. Tube radius, backplate depth/profile, globe depth placement, elbow size and contact-cap dimensions are not numerically given in the retrieved sources; they are proportioned from the exact 231180 product image and recorded in sources_and_inferences.json.

The builder uses the Revit 2025 English-Imperial Generic Model face based template, switches the family to Lighting Fixtures, makes Brass Finish and Opal Glass Finish editable material parameters, and builds native Revit FreeFormElement solids for the globe, bell plate, riser, elbow, top rail and contact cap.

## Native and QA gates

build_ic_cw1.py saves and reopens the RFA, loads it into a disposable native Revit project, places it on an actual wall-face reference, records Host / HostFace and mounting-normal evidence, verifies the measured placed envelope, substitutes both material parameters and confirms the replacements reach geometry, requires zero family/project warnings, and exports front, side, oblique, material and hosted review images.

Prepared native command:

D:\Games\pyRevit-Master\bin\pyrevit.exe run E:\Claude\3D-Model-Workflow\output\lightology_20260923\f02_231180\build_ic_cw1.py --revit=2025

Native execution is centralized in prime's serialized recovery batch. Technical/native and final visual gates remain pending until prime runs the saved builder and returns the evidence.
