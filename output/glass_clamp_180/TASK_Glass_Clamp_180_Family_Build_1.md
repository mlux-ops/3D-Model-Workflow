# TASK: Build Revit family "SHB_Glass Clamp 180 Square"

## Purpose
- Generic 180° glass-to-glass clamp joining two coplanar frameless panels.
- Stand-in for CRL SGC180BBRZ (Brushed Bronze, Square profile).
- Project: 651 W Belmont (25-012), primary bath enclosure.
- Output: `SHB_Glass Clamp 180 Square.rfa`, FBX-clean (no nested junk, one material slot per part).

## Source Constraints
| Item | Value | Status |
|---|---|---|
| Product | CRL SGC180BBRZ, Square 180° Glass-to-Glass Clamp | verified |
| Finish | Brushed Bronze | verified |
| Overall height | 2" (51 mm) | verified |
| Overall width | 5" (127 mm) | verified |
| Glass thickness range | 3/8"–1/2" (10–12 mm) | verified |
| Plate thickness | 1/8" | ASSUMED, check CRL drawing |
| Joint gap between panels | 1/8" | ASSUMED, check job glass detail |
| Screw cap Ø / height | 3/4" / 1/8" | ASSUMED |
| Screw count | 2 per side (4 caps front) | ASSUMED |
- CRL page: https://www.crlaurence.com/All-Products/Shower-Hardware/Glass-Shower-Clamps-and-Brackets/Glass-to-Glass-Clamps/Square-Profile-Clamps---Glass-To-Glass/CRL-Brushed-Bronze-Square-180-Degree-Glass-to-Glass-Clamp/p/SGC180BBRZ
- Section "Technical References & CAD Drawings" on that page may hold the true profile. Check before finalizing assumed values.
- Never claim dimensions marked ASSUMED are manufacturer data.

## Family Setup
1. Template: `Generic Model.rft` (imperial, non-hosted).
2. Category: Generic Model.
3. Family parameter: `Always vertical` = ON.
4. Family parameter `Work Plane-Based` = OFF.
5. Origin: center of joint gap at mid-height. Front = +Y (toward room), back = -Y.

## Reference Planes (name exactly)
| Name | Orientation | Position |
|---|---|---|
| Joint CL | vertical, plane normal X | X = 0 |
| Glass Mid | horizontal, plane normal Z | Z = 0 |
| Glass Face Front | vertical, plane normal Y | Y = +Glass_Thickness/2 |
| Glass Face Back | vertical, plane normal Y | Y = -Glass_Thickness/2 |
| Plate Outer Front | vertical, plane normal Y | Y = Glass Face Front + Plate_Thickness |
| Plate Outer Back | vertical, plane normal Y | Y = Glass Face Back − Plate_Thickness |
- Lock/align each plane to its dimension. Dimensions drive parameters below.
- Do not use type-level formulas for planes. Use dimension labels only.

## Type Parameters
| Name | Type | Default | Formula |
|---|---|---|---|
| Glass_Thickness | Length | 1/2" | none (type catalog varies 3/8", 1/2") |
| Plate_Thickness | Length | 1/8" | none |
| Clamp_Width | Length | 5" | none |
| Clamp_Height | Length | 2" | none |
| Joint_Gap | Length | 1/8" | none |
| Cap_Diameter | Length | 3/4" | none |
| Cap_Height | Length | 1/8" | none |
| Cap_Spacing | Length | Clamp_Width − 2 in | = Clamp_Width - 2" |
| Clamp_Material | Material | Brushed Bronze | none |
| Manufacturer | Text | CRL | none |
| Model | Text | SGC180BBRZ | none |
| Description | Text | Square 180 Deg Glass-to-Glass Clamp | none |
- Assign Type Comments = `SGC180BBRZ - Brushed Bronze`.

## Geometry
Build all solids as extrusions. Sketch on the plane given, extrude between the given planes.

### Front plate
1. Work plane: Plate Outer Front.
2. Sketch rectangle: X from −Clamp_Width/2 to +Clamp_Width/2, Z from −Clamp_Height/2 to +Clamp_Height/2.
3. Extrude: start Plate Outer Front, end Glass Face Front.
4. Lock all four sketch lines to reference planes or dimension parameters.
5. Fillet the four corners at 1/8" (optional, cosmetic only; skip if regenerate errors).

### Back plate
1. Mirror of front plate about Glass Mid-plane Y=0.
2. Extrude from Plate Outer Back to Glass Face Back.
3. Same sketch dimensions.

### Screw caps (front)
1. Work plane: Plate Outer Front.
2. Two circles, Ø Cap_Diameter, centers at X = ±Cap_Spacing/2, Z = 0.
3. Extrude outward +Y by Cap_Height.
4. Lock centers to dimension Cap_Spacing.

### Screw caps (back)
1. Same on Plate Outer Back, extrude −Y by Cap_Height.

### Joint gap spacer
- Omit. The gap is empty space between panels. Do not model glass in this family.

## Materials and Subcategories
1. Create subcategory `Clamp Plate` and `Clamp Cap` under Generic Models.
2. Assign plates to `Clamp Plate`, caps to `Clamp Cap`.
3. Bind each solid's Material to `Clamp_Material` (Material parameter association via "Associate Family Parameter" on the solid's Material field).
4. Project must contain a material named `Brushed Bronze` (or the finish-database name for the primary bath bronze). Look the name up in the project. Do not invent one.
   - If absent: duplicate the closest bronze material, name it `Brushed Bronze`, set Appearance to a brushed metal asset, color RGB 110/86/62, roughness ~0.35, metallic 1.0.
   - Confirm the exact name from the Smartsheet FINISH DATABASE (id 6391628162879364) before creating it.
5. Graphics: set Shading color to match, Surface pattern none.

## Visibility
1. Detail level: Coarse = plates only. Medium/Fine = plates and caps.
   - Select cap solids > Visibility Settings > uncheck Coarse.
2. Views: Plan/RCP, Front/Back, Left/Right, 3D all ON.
3. No symbolic lines needed.

## Type Catalog (optional)
- File: `SHB_Glass Clamp 180 Square.txt` beside the RFA.
- Row values: `Glass_Thickness##length##inches`, one type per glass thickness.

| Type | Glass_Thickness |
|---|---|
| 3-8 Glass | 3/8" |
| 1-2 Glass | 1/2" |

## Verify Before Save
1. Flex Glass_Thickness 3/8" ↔ 1/2". Plates stay 1/8" thick and move outward. No errors.
2. Flex Clamp_Width 4" ↔ 6". Caps stay centered per formula.
3. Open in 3D. Front plate, back plate and four caps are separate solids with the bronze material.
4. Purge unused (Manage > Purge Unused).
5. Save with compact file option.
6. File size under 500 KB.

## Load and Place in Project
1. Load into the Belmont model. Choose type by the actual glass thickness (check the primary bath glass type).
2. Place at each panel-to-panel joint of the primary bath enclosure.
3. Placement Z: assumed three clamps per joint at 6" from top, mid-height and 6" from bottom. Verify with job hardware layout.
4. Placement XY: on the joint centerline; rotate so the plate faces align with the glass faces.
5. Set instance/type comments to `SGC180BBRZ`.
6. Add clamps to the hardware schedule if one exists (Manufacturer, Model).

## FBX Notes (Blender walkthrough)
- Solids keep the `Clamp_Material` name on export; Blender will show one material per part.
- Confirm the material name has no special characters.
- Keep the caps as real geometry; do not use a decal or texture.

## Do Not
- Do not model threads, hinges or gasket detail.
- Do not download or repackage third-party RFAs.
- Do not overwrite existing project materials.
- Do not publish specs as CRL-verified; only height, width and glass range are verified.

## Open Questions for Max
- Actual plate thickness and cap size from CRL drawing.
- Bath glass thickness (3/8" or 1/2").
- Number of panels and joints in the primary bath enclosure.
