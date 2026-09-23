# ELM Colorado Bruges Antique — Exa mosaic maps (Rev5)

This package supplies two matching, seamless PNG maps for a Revit Generic material:

- `ELM_Bruges_Antique_Exa_Rev5_Color.png` — 8-bit RGB color/diffuse image.
- `ELM_Bruges_Antique_Exa_Rev5_Bump16.png` — 16-bit grayscale height/bump image. Light is high tile face; dark is recessed joint or groove.

In Revit, create a Generic material, load the color image in **Appearance > Generic > Image** and the grayscale image in **Appearance > Bump > Image**. Enable Bump, start with **Amount 50**, and use a low-gloss matte finish (the Revit draft used Glossiness 15). Set **both image sample sizes to 185.8268 in wide × 180.7087 in high** with the same rotation and offset. Keep the map files in a permanent location so Revit can resolve their paths.

Each map is 7168 × 6984 pixels. One full image covers 16 × 18 manufacturer mosaic sheets, each 29.5 × 25.5 cm (11.6142 × 10.0394 in). Opposite bitmap edges match exactly. The surface contains point-up hexagons, muted warm Antique stone variation, a limited number of worn and diagonally grooved faces, and continuous joints. The color and bump maps are aligned.

The modeled grout step is 0.50 mm, diagonal groove relief is 0.30 mm, and surface microrelief is at most 0.02 mm, leaving at least 0.18 mm between the deepest groove and the joint floor. These are appearance estimates, not manufacturer measurements. A straight-on product photo of the exact Antique Exa combination was unavailable; the maps combine the manufacturer's Antique finish swatch with its Exa geometry and motif reference. See the local project `SOURCE_SELECTION.md` for sourcing details. A finite atlas repeats after its 185.8268 × 180.7087 in period; check larger installations for visible repetition.
