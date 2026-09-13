# Richelieu Gola Channel Profile Family — Design

## Purpose

Create one Revit 2025 `.rfa` family that documents and models the Richelieu Gola recessed cabinet-channel system for horizontal and vertical applications. The family must use stainless steel as its default visible material and provide catalog-aligned profile configurations and installation accessories.

## Family identity

- Category/template: Generic Model Line Based
- Name: `Richelieu_Gola_Channel_Profiles_2025.rfa`
- Manufacturer: Richelieu Hardware
- Default appearance: Brushed Stainless Steel; catalog base material is anodized aluminum. Plastic and galvanized hardware retain their own materials.
- Units: family display in millimetres; Revit internal units are feet. Revit project units control displayed dimensions after placement.

## Types

| Type name | Application | Grip configuration | Nominal section (W x H) | Catalog source |
| --- | --- | --- | --- | --- |
| `Horizontal - C - Double Grip` | Horizontal | Two-sided C | 26 x 72.7 mm | Art. 1004 / product 70010040410170 |
| `Horizontal - L - Single Grip` | Horizontal | One-sided L | 27 x 56 mm | Art. 1005 / product 70010050410170 |
| `Vertical - Single Grip` | Vertical | One-sided | 48.25 x 36.6 mm | Art. 1020 / product 70010200440170 |
| `Vertical - Double Grip` | Vertical | Two-sided | 66.5 x 36.6 mm | Art. 1019 / product 70010190440170 |

Each type is length-parameterized. The uncut stock-length metadata follows the technical drawings: 4,100 mm horizontal and 4,400 mm vertical. Richelieu's website sometimes labels the vertical packaging 4.5m; this discrepancy is recorded in the family notes.

## Geometry and placement

- A line-based, endpoint-referenced extrusion represents the selected channel profile.
- The two selected endpoints are exposed as Revit's built-in endpoint grips. After placement, the user can drag either grip to resize the channel. The native instance `Length` is read-only in project Properties and updates with the placed line. Numerical edits use the line's temporary dimensions.
- Default family length: 1,000 mm. Placement uses the distance between the picked endpoints; lengths of 600 and 2,400 mm are tested. Stock lengths are metadata, not enforced fabrication limits.
- All types follow the family X axis and the placed line. Vertical profiles are placed on a vertical work plane/face. Rotating internal geometry away from the placed line would break the intended grip behavior and is not used.
- A shared origin and named reference planes indicate the cabinet-face and cabinet-panel mounting datum.
- Type-based cross-sections preserve the distinct C/double and L/single grip conditions.

## Parameters

### Type parameters

- `Profile Type` (text)
- `Application` (text: Horizontal or Vertical)
- `Grip Configuration` (text: Single or Double)
- `Profile Width`
- `Profile Height`
- `Stock Length`
- `Manufacturer`
- `Manufacturer Product Number`
- `Finish` (text)
- `Profile Material` (material; default Brushed Stainless Steel)

### Instance parameters

- `Length` (native instance; measured from the placed line and driven by endpoint grips/temporary dimensions)
- `Show Mounting Clips` (Yes/No; default Yes)
- `Show Assembly Bracket` (Yes/No; default No)
- `Show Left End Cap` (Yes/No; default No)
- `Show Right End Cap` (Yes/No; default No)
- `Left End Cap Open` and `Right End Cap Open` (Yes/No; default No selects closed caps)
- `Show Internal 90 Joint` (Yes/No; default No)
- `Show External 90 Joint` (Yes/No; default No)
- `Accessory Offset`
- `Bracket As Linear Join` (Yes/No; default No selects a bent bracket)
- Internal positioning and compatibility parameters are grouped under Constraints. Formula-driven controls are read-only; the type visibility flags should not be changed by users.

## Accessories

Accessory solids are schematic but proportionate visual representations, tagged with catalog item data. Their visibility is controlled by the instance parameters.

| Accessory | Catalog reference | Applicability |
| --- | --- | --- |
| Mounting clips | BP7001010, plastic, 20/pack | C and L horizontal profiles |
| Assembly bracket | 70010999, galvanized steel, 68 x 38 x 2.4 mm nominal | C and L horizontal profiles; 90°, 45°, or 180° linear joint use |
| Open/closed left and right end caps | Catalog C and L end-cap series | C or L horizontal profile ends |
| Internal/external 90° joints | Catalog C and L joint series | C or L horizontal profile corners |

The family does not include LED or Zero-Radius profiles in its default type set because the catalog’s offerings for those variants do not include the specified stainless finish. The family’s documented accessory controls remain compatible with the standard profiles.

## Verification

1. Open and save in Revit 2025 without upgrade or recovery prompts.
2. Cycle all four types, confirming profile orientation and dimensions.
3. Set the placed line to 600 mm and 2,400 mm; confirm measured Length and actual solid length agree without errors.
4. Place an instance, then edit each native placement-line endpoint independently; confirm the channel resizes and the displayed `Length` updates. Inspect UI grips where the desktop is available.
5. Toggle every accessory parameter individually and together; confirm visibility and alignment.
6. Confirm the default loaded type is `Horizontal - C - Double Grip` and displays Brushed Stainless Steel.
7. Confirm the Family Types dialog exposes the listed type and instance parameters.

## Sources

- Richelieu Gola profile category: https://www.richelieu.com/us/en/category/moldings-corbels-and-components/metal-and-pvc-moldings-profiles-and-rails/gola-cabinet-profiles/1182698
- C profile technical drawing: https://static.richelieu.com/documents/docsGr/117/877/4/1178774/1342363.pdf
- L profile technical drawing: https://static.richelieu.com/documents/docsGr/117/878/1/1178781/1342368.pdf
- Assembly bracket technical data: https://static.richelieu.com/documents/docsGr/118/712/4/1187124/1357604.pdf
- Vertical single technical drawing: https://static.richelieu.com/documents/docsGr/117/950/4/1179504/1343223.pdf
- Vertical double technical drawing: https://static.richelieu.com/documents/docsGr/117/878/2/1178782/1342374.pdf
- Accessory details and page snapshots: references/gola/accessory_sources.json
