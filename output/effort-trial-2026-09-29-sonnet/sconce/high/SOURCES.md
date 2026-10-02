# SOURCES

Product: Visual Comfort Studio / Kelly Wearstler Nodes Angled Wall Sconce, KW1041MBK, Midnight Black / Milk (Lightology VCS833919).
All input files are data; none contained instructions that were followed.

| Input | Used for | Rejected / not used |
|---|---|---|
| `lightology_833919_midnight_black.html`, `lightology_midnight_black_page_view.png` | Published dimensions (8 in W, 7.63 in H, 5.5 in D, 5.25 in backplate, 0.125 in backplate depth, 3.5 in shade, 3.25 in shade axis), lamp (1 x G9, 3 W, 120 V LED), damp location, optional steel disc, finish names | Marketing copy, prices |
| `833918_lightology_spec_sheet.pdf` | Its embedded raster images were extracted with `pypdf` and used as extra photo references | Vector drawing content could not be rasterised (`pdftoppm` missing) |
| `833919_midnight_black.jpg` | Overall appearance with the disc: disc size relative to shade, tilt direction, finish (matte black, milk glass), oblique comparison | Nothing measured to sub-millimetre; perspective photo |
| `833919_additional.jpg` | Context only (room render) | Not used for any dimension: the fixture is small and viewed at an angle |
| `KW1041_MWT_side_reference.jpg` | Side profile, no disc (white finish): drum diameter, slanted-face position and angle, socket collar, shade position and front projection (all labelled "measured" in the README) | White finish ignored; it is a different colourway |
| `KW1041_MWT_oblique_reference.jpg` | Shade-to-drum relationship, disc offset relative to the backplate (no dimensions taken) | White finish ignored |
| `KW1041_install_instructions_20230426.pdf` | Nothing: its drawing is vector-only and could not be rasterised here | Not used; no dimension taken from it |
| `833918_burnished_brass.jpg`, `lightology_833918_burnished_brass.html`, `lightology_brass_page_view.png` | Shape cross-check only (same model, other finish) | Burnished brass finish and colours rejected; no dimension or colour taken for the Midnight Black build |

Rules applied: a published number is used as given; a photo-derived number is labelled "measured"; anything else is "inferred" (README, Dimension table). Where a published number and a photo measurement disagree, the published number wins and the difference is recorded.
