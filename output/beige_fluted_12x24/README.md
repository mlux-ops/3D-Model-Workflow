# Beige fluted tile — 12 x 24 inches

Includes a native Revit 2025 ADSKLIB material library, companion RVT material source, original color texture, 16-bit bump map, validation reports, and source scripts. The RVT was saved and reopened through Revit 2025 with zero warnings. The ADSKLIB was created, populated, and released in Revit's Material Browser; its stored material row and container integrity were verified. The Texture Editor visually confirmed 1 foot width x 2 feet height. Material Browser preview was inspected; a full room render has not been performed.

The supplied IMG_0786.jpeg is the color source, retained byte-for-byte as textures/Beige_Fluted_Color.jpeg. It has 1200 x 2400 native pixels, equivalent to 100 pixels per inch at the requested tile size. It has not been enlarged, recolored, or replaced by generated artwork.

Mapping: 12 inches wide x 24 inches high, rotation 0 degrees, repeating horizontally and vertically. Flutes run vertically along the long edge. No grout has been added: joint width and installation layout were not specified. This is a single-tile surface, not a randomized multi-tile installation.

Appearance: opaque Generic ceramic asset, glossiness 0.25, reflectivity 0.04 at normal incidence and 1.0 at grazing incidence, index 1.5. These are estimated matte dielectric settings, not manufacturer measurements. Average shaded-display color is RGB 208,188,164.

textures/Beige_Fluted_Bump16.png is a 16-bit grayscale HEIGHT/BUMP map, not a tangent-space normal map. It follows a smoothed, column-averaged photographic profile. Intermediate calculations use floating point. Native Revit bump amount is set conservatively to 0.015; that setting is not a measured physical relief depth. No displacement or modeled ribs are included. The original color image retains photographed light and shadow, so relief depth, sign and sheen require scene review. Disable bump for an exact flat photographic appearance if needed.

Extract the complete package to a permanent folder. In Revit Manage > Materials, use the library menu at the lower left > Open Existing Library, open Beige_Fluted_12x24_R2025.adsklib, and add "Beige Fluted Stone Tile - 12x24 Portrait" to the project. Repath the color and bump images in Appearance to the extracted textures folder if the original absolute paths do not resolve. Set BOTH bitmap scales to 12 x 24 inches and keep their rotations aligned. The companion RVT can also serve as the material source through Transfer Project Standards > Materials. An empty plan is expected when opening that RVT: it is a material source, not a building model.

Physical finish, calibrated color under neutral lighting, and true flute cross-section cannot be established from a single photograph. Native load/reopen validation and rendered appearance validation are separate checks.
