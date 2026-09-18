# 700LSESF60 — 60-inch black linear pendant

## Load and place

Load `700LSESF60_Black_Adjustable_R2025.rfa` in Revit 2025 or later. Place on the underside of a native horizontal face, or use an appropriate overhead work plane. Local +Z points away from the mounting face, down into the room when ceiling mounted.

Select the placed fixture and edit **Total Drop** in instance Properties. This measures from the ceiling mounting face to the lowest glass surface. Default: **48 inches**. Use the source drawing's **13.2–67.2 inch** range. The two rods and the complete lower assembly move together. The family does not enforce the manufacturer's range; values outside it are unsupported. **Assembly Offset** is formula-driven.

Edit Type provides **Metal Finish**, **Glass Finish**, and **Diffuser Finish**. Appearance assets are embedded; no companion texture maps are required. The nested body is embedded in the main RFA; the separate body RFA is retained for editing and is not loaded separately for ordinary placement.

## Reference dimensions

Printed inch dimensions from the supplied outline are authoritative:

- Bar length: 60 inches.
- Complete lower body height: 4.8 inches.
- Glass/housing diameter: 2.5 inches.
- Canopy: 13.5 × 6.5 × 1.4 inches.
- Overall installed drop: 13.2–67.2 inches.

The six lights, slim rectangular bar, two suspension rods, black finish, clear outer glass, and pale inner diffusers follow the supplied photos. Warm diffuser appearance follows the illuminated detail references. It is an appearance glow, not a photometric light source.

## Inferred details and scope

Lamp centers are evenly spaced at 10.4 inches, with the end centers 4 inches from the ends. Rod center spacing is 7.6 inches. Bar cross section is 0.8 inches deep × 1.4 inches tall; rods are 0.48 inches diameter. These dimensions, housing overlap, glass wall/bottom thickness, diffuser inset, edge softening, and material optical properties are inferred from the pictures, not individually dimensioned manufacturer data. Small rod couplings and concealed mounting hardware are simplified.

This is an independently reconstructed Lighting Fixtures visualization family. No MEP connectors, electrical data, IES distribution, or fabrication-level internals are included. Revit 2025 is the oldest supported file version; it cannot be opened in earlier Revit releases.

## Validation

See `validation.json` for the actual native build status, reopening, ceiling face placement, drop flex checks, and material substitution results. Native PNG views support silhouette review; they are not a production renderer validation.

Original supplied images are preserved in `references`; builder source is included for reproducibility.
