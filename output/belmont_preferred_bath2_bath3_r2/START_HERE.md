# 651 Belmont preferred tiles — corrected R2

Open `651_Belmont_Preferred_Tiles_R2025.rvt` from this R2 folder in Revit 2025 or newer. This revision supersedes the original preferred-tile material source, preserving the six product assignments and nominal dimensions. The original remains available in the sibling folder for comparison.

## What changed

The repeating four-tile blocks were replaced with 64–1,280 independently sampled tile faces per material and approximately 16-foot atlases. Color, 16-bit bump and companion roughness maps have matching layout and seamless grout boundaries. Caraibi retains its pale scored divisions; Ligne Noir retains ten vertical flutes in its bump map. Wall and floor Alabaster have different layout seeds.

Variation uses AI-derived glaze fields based on the supplied real photographs. These are visualization variants, not additional manufacturer scans or measured PBR data. Original photographs are preserved alongside the derived fields. Physical size, source resolution, field resolution, crop layout and random seed are recorded in manifest.json and per-material notes.

## Update an existing project

Open this RVT and the destination RVT. Transfer Project Standards > Materials, selecting overwrite for these six existing `651 Belmont` materials when prompted. Work from a saved copy of the destination when replacing existing materials. Copying swatches alone may retain conflicting older materials, so verify the Appearance texture path after transfer.

All twelve bound color/bump paths point to this R2 directory. Keep it in place. On another machine, extract the complete package, then relink each material's Color and Bump maps to its matching ID/textures folder. Use the atlas dimensions in manifest.json for BOTH maps; do not scale the whole atlas to one tile. Do not use the old package's small repeat dimensions. Companion Roughness maps are for explicit renderer setup, linear/raw; they are not bound to Revit Generic's scalar glossiness.

## Review status and extent

Review targets are 15 x 15-foot uninterrupted surfaces, close-ups, and 3 x 3 repeated atlas previews. These are finite bitmap atlases: mathematically they repeat at the listed physical dimensions. They are not an infinite stochastic shader. For larger surfaces, extend the layout and review again.

Native `Realistic` view exports establish Revit mapping and color appearance, not a ray-traced rendering. They do not reliably demonstrate bump relief. Full photorealistic material/relief acceptance remains pending a supported production renderer; do not treat the neutral/grazing view names as proof of a completed optical render. See REVIEW.md for evidence and limitations.

No ADSKLIB or native V-Ray preset is included; the RVT is the native transfer source. All needed color/bump files, optional roughness maps, original references, derived fields and setup notes are included.
