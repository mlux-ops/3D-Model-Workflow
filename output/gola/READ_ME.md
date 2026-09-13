# Richelieu Gola profiles — Revit 2025

## Files

- `Richelieu_Gola_Channel_Profiles_2025.rfa` — loadable, native Revit 2025 Generic Model, line-based family.
- `Gola_2025_Placement_Examples.rvt` — four profile examples and a vertical face-placement demonstration. The wall is only a work-plane demonstration, not a cabinet construction detail.
- PNG previews — views exported directly from the sample Revit project.
- `validation.json` — measurements and checks performed in Revit 2025.

## Load, place and resize

1. In Revit 2025, use **Insert → Load Family** and select the RFA.
2. Use **Component → Place a Component**, then choose the required Gola type.
3. Set the intended work plane or choose **Place on Face**, as appropriate. Pick the two endpoints of the channel run. The section projects out from its work plane.
4. Select the placed channel in a view that looks at its work plane. Drag either endpoint grip to change the run length. For an exact length, use the selected line's temporary dimension.

`Length` in project Properties is Revit's measured, read-only line length. It updates automatically when you resize the line. It is not a separately editable Properties field. The grips belong to the native line-based placement; they are not custom graphic arrows. If grips are difficult to select, use a plan/elevation aligned with the work plane and ensure the instance is not pinned.

For a **horizontal** channel on the cabinet front, use a vertical cabinet-front face/work plane and draw a horizontal line. For a **vertical** channel, use a vertical face/work plane and draw the line vertically. Choosing a Vertical type changes the section; it does not rotate a horizontally drawn line automatically. Reverse the placement direction or use Revit's orientation tools if the single-grip section faces the wrong way.

The picked line locates the section's back datum and one section edge, not its center. Allow for the modeled depth and cabinet routing. This family does not cut cabinet openings automatically.

## Included types

| Type | Published section | Stock length metadata | Stainless-finish SKU |
| --- | --- | --- | --- |
| Horizontal - C - Double Grip | 26 mm depth × 72.7 mm height | 4,100 mm | 70010040410170 |
| Horizontal - L - Single Grip | 27 mm depth × 56 mm height | 4,100 mm | 70010050410170 |
| Vertical - Single Grip | 48.25 mm width × 36.6 mm depth | 4,400 mm | 70010200440170 |
| Vertical - Double Grip | 66.5 mm width × 36.6 mm depth | 4,400 mm | 70010190440170 |

Stock length is information, not a limit on placement. Vertical drawings state 4,400 mm; some website packaging text says 4.5 m. Confirm supply length when ordering.

Section sizes are fixed manufacturer profiles; the Width/Height fields are descriptive metadata, not controls that reshape the section. Select a family type to change the section. Do not change the internal `Type HC/HL/VS/VD` visibility flags.

## Finish

The default is **Gola - Brushed Stainless Finish**, using Revit's brushed stainless appearance asset. The actual catalog channel substrate is **anodized aluminum**, not solid stainless steel. Change `Profile Material` in Edit Type if required. `Cap Material`, `Mounting Clip Material` and `Bracket Material` are separate assignments. Clips are black plastic and brackets galvanized gray.

Realistic rendering uses the standard Autodesk Material Library brushed-metal texture. Keep that library installed on other computers. Shaded views use the material's gray display color.

## Optional accessories

All accessory switches are instance controls under Visibility. They operate only on compatible horizontal C/L types and are suppressed for the vertical types.

| Control | Modeled option and catalog reference |
| --- | --- |
| Show Mounting Clips | Two BP7001010 plastic clips, near the two ends; on by default for horizontal types |
| Accessory Offset | Moves the clips in from the run ends; nominal default 50 mm, internally limited to keep the clips near the run |
| Show Left / Right End Cap | Independent start/end caps; off by default |
| Left / Right End Cap Open | Off = closed; on = open. Requires the corresponding Show End Cap switch |
| Show Assembly Bracket | Schematic 70010999 galvanized bracket at the run end |
| Bracket As Linear Join | Off = 90° bracket; on = straight joint representation |
| Show Internal 90 Joint | Internal fitting at the START endpoint |
| Show External 90 Joint | External fitting at the END endpoint |

Left/right mean the start/end of the line as drawn; they do not always mean screen-left/screen-right. Turn the end cap off at an endpoint where a corner joint is enabled. Place the adjoining channel as a separate instance; a corner toggle does not generate or miter that adjoining run. Do not enable a bracket and a fitting in conflicting physical locations.

Accessory product numbers are also stored in each type:

| Fitting | C profile | L profile |
| --- | --- | --- |
| Closed, non-LED cap | 7001046170 | 7001044170 |
| Open cap | 7001045170 | 7001013170 |
| Internal 90° joint | 7001016I170 | 7001017I170 |
| External 90° joint | 7001016E170 | 7001015E170 |

The vertical profiles use direct fixing to cabinet panels in the manufacturer's installation detail. Horizontal clips/caps are not assigned to them. Individual screws, washers, holes and fixing centers are not modeled. The assembly bracket is shown at 90° or straight, not as a bendable 45° fitting. Clip quantities are illustrative, not a calculated fixing schedule.

## Accuracy and verification

This is an independently created architectural coordination/visualization family, not a manufacturer-issued fabrication model. The four overall section envelopes follow the published drawings. Grip contours are traced with native lines/arcs; undimensioned wall thicknesses, small radii and screw-receptacle details are approximate. End caps, clips, brackets and corner joints are schematic fittings. Do not fabricate, route cabinetry or derive purchasing quantities solely from this model. Use current manufacturer drawings and installation requirements.

The family was saved and reopened in Revit 2025, loaded into a project, and tested at 600, 1,000 and 2,400 mm. Both native placement-line endpoints were edited independently through Revit's API; actual solid lengths and end-cap positions were measured. Accessory visibility, vertical face placement and material reassignment were checked. The accompanying report records the results. A separate desktop UI check also dragged each C-profile grip: 1,000 → 1,160 → 1,560 mm, with caps following both edits. The sample was restored afterward. The tests do not certify every possible host, view, length or accessory combination.

## Manufacturer sources

- [Richelieu Gola profile category](https://www.richelieu.com/us/en/category/moldings-corbels-and-components/metal-and-pvc-moldings-profiles-and-rails/gola-cabinet-profiles/1182698)
- [Horizontal C drawing — Art. 1004](https://static.richelieu.com/documents/docsGr/117/877/4/1178774/1342363.pdf)
- [Horizontal L drawing — Art. 1005](https://static.richelieu.com/documents/docsGr/117/878/1/1178781/1342368.pdf)
- [Vertical single drawing — Art. 1020](https://static.richelieu.com/documents/docsGr/117/950/4/1179504/1343223.pdf)
- [Vertical double drawing — Art. 1019](https://static.richelieu.com/documents/docsGr/117/878/2/1178782/1342374.pdf)
- [Vertical installation detail](https://static.richelieu.com/documents/docsGr/117/950/4/1179504/1343332.pdf)
- [Mounting clip drawing](https://static.richelieu.com/documents/docsGr/118/269/0/1182690/1416084.pdf)
- [Assembly bracket sheet](https://static.richelieu.com/documents/docsGr/118/712/4/1187124/1357604.pdf)

Researched and generated September 7, 2026. Standard non-LED profiles only; LED and Zero-Radius systems are separate product families and are not included.
