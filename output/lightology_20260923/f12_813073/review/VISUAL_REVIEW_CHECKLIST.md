# F12 visual review checklist

Reference evidence:
- `references/lightology_1279684_natural_brass.jpg` — exact Natural Brass selected option.
- `references/orbel_installation_reference_aged_brass.jpg` — same geometry in installed context; finish comparison only.
- `references/lightology_1279684_spec.pdf` / `.txt` — printed selected-option dimensions and finish.
- `references/vcmod_orbel_installation.pdf` / `.txt` — mounting, removable shade/socket, up/down orientation.

Native review requirements:
- Front: confirm 5 in plate width, 12.9 in height, lower-half globe, thin central vertical blade, subtle rounded plate edges.
- Side: confirm 6.7 in maximum projection and proportions among 0.7 in backplate, blade, socket stalk, and globe.
- Oblique: compare sculptural blade/globe silhouette against the exact Natural Brass product image.
- Material: Natural Brass should read warm and muted; frosted sphere distinct and translucent.
- Hosted Wall: plate flush to host, outward orientation, no embedded/reversed geometry.

Geometry/source checks:
- Printed envelope: 5.0 W x 12.9 H x 6.7 D; backplate 5.0 W x 12.9 H x 0.7 D.
- Blade thickness/projection, globe diameter/center, glass thickness/opening, and socket geometry remain inferred.
- Preserve short cylindrical socket/stalk visible behind globe.
- Glass must be a hollow shell with a rear opening consistent with the threaded-shade installation instructions.
- Small Allen screw/mounting hardware is omitted as non-silhouette room-scale detail.
- Up/down installation is supported by instance rotation rather than a second family geometry state.

Technical checks:
- Saved RFA reopens in Revit 2025 as Lighting Fixtures and retains face-based placement.
- Hosted instance has non-null wall host and mounting-normal dot magnitude near 1.0.
- `Metal Finish` and `Glass Finish` substitutions reach geometry.
- Family/project warning lists are empty.
- `validation.json` reports `technical_pass: true` only after all required gates pass.
