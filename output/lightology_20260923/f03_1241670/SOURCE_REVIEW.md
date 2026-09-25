# F03 source and inference review

## Exact product / option

- Product: Brenta Single Sconce by AERIN for Visual Comfort Signature.
- Requested finish: Bronze.
- Exact requested variant: ARN 2473BZ-CG / Lightology VCG1241668.
- The originally assigned Lightology URL uses option_id=1241669, which is the Hand-Rubbed Antique Brass variant ARN 2473HAB-CG. The build target remains the requested Bronze variant.

## Preserved source evidence

- `source/visualcomfort_bronze_official.jpg`: official high-resolution Bronze product image from Visual Comfort's image service. This is the primary finish and proportion reference.
- `source/lightology_bronze.jpg`: Lightology Bronze product image; consistent with the official Bronze image.
- `source/lightology_line_reference.jpg`: gallery line drawing showing 18.5 in overall height, 3.5 in width, 3.75 in projection, 5.25 in backplate height, and mounting-plate center 9.25 in from the fixture end.
- `source/lightology_additional_reference.jpg`: Polished Nickel gallery image shown horizontally. Use only for geometry/proportion and the horizontal-installation interpretation, not Bronze finish color.
- `source/visualcomfort_spec_bronze.pdf`: Bronze manufacturer specification sheet.
- `source/visualcomfort_install_bronze.pdf`: Bronze installation guide.
- `source/visualcomfort_cb_arn2473.dwg`: manufacturer CAD block.
- `source/visualcomfort_arn2473_reference.rfa`: manufacturer Revit reference; retained for inspection/measurement only.
- `source/lightology_spec.pdf`: Lightology specification sheet.

## Drawing-derived facts

- Overall envelope: 3.5 in W x 18.5 in H x 3.75 in extension.
- Rectangular backplate: 3.5 in W x 5.25 in H.
- Mounting plate center: 9.25 in from the fixture end, exactly half the 18.5 in overall height; the backplate is centered vertically on the fixture.
- Visual Comfort's product page explicitly exposes the Bronze offer as ARN 2473BZ-CG, with a Bronze-specific spec/install resource set and Bronze 3D-viewer asset path.

## Inferences that remain visual-review items

The retrieved dimension sources do not provide the glass tube outside diameter, center sleeve outside diameter/height, backplate thickness, standoff depth, glass wall thickness, diffuser diameter, or edge radii. Those remain photo-derived. The current builder uses 1.75 in glass OD, 2.0 in sleeve OD, 3.5 in sleeve height, 0.18 in backplate thickness, and a 2.75 in glass/sleeve axis offset from the host. Prime should judge those proportions against `visualcomfort_bronze_official.jpg` and the line drawing during the native visual gate.

The official image confirms a clear outer cylinder with a smaller warm-white internal diffuser and a dark living-Bronze central sleeve/backplate. The Polished Nickel horizontal image confirms the same body geometry can be installed horizontally.

## Source discrepancy with no geometry impact

Lightology describes two 9 W LED sources / 18 W total and 750 delivered lumens; the Visual Comfort product-page variant data displays `Wattage: 9w (750lm)`. This electrical metadata conflict does not affect the visualization geometry. The family intentionally carries no MEP connector or photometric source; 2700 K and 750 lm are retained from the selected Lightology option data.

## Native status

READY_REVIT was sent to prime with the exact command. Prime stated that it is correcting the front-camera definition and handling the serialized native execution/review. This worker will not launch a second Revit run.

## Manufacturer RFA measured solid sizes

The first native validation inspected the preserved manufacturer RFA and found four imported solids. Converting the recorded bounding boxes from feet to inches gives:

- Solid A: approximately 1.347 in x 1.347 in x 17.237 in. This is consistent with the long inner luminous diffuser.
- Solid B: approximately 2.024 in x 2.021 in x 18.577 in. This is consistent with the outer glass cylinder and is the strongest available evidence that the current 1.75 in glass OD is undersized.
- Solid C: approximately 3.665 in x 0.920 in x 5.367 in. This is consistent with the rectangular backplate mass.
- Solid D: approximately 1.914 in x 2.929 in x 3.611 in. This is consistent with the central sleeve/housing assembly.

The manufacturer RFA's outer dimensions slightly exceed the published 3.5 in W x 18.5 in H envelope, so published dimensions remain authoritative for final family bounds. Use these RFA solid sizes to correct internal proportions while constraining the finished family to the printed nominal envelope. The solid bounding boxes are reliable for component size; because the inspection records individual solid-local bounds and not a fully reconstructed component transform hierarchy, do not infer exact host offset/assembly position from their coordinate centers alone.

