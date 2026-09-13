# Gola profiles with cabinet-cutting recesses — Revit 2025

This revision adds a native unattached cutting void to the existing four-type Gola family. The void follows the selected profile type and both endpoints. It clears a rectangular recess including the finger-grip opening, without cutting the channel's own solids.

## Update your project

1. Load `Richelieu_Gola_Channel_Profiles_2025.rfa` from **this folder**. It has the same family name as the original, so Revit can update existing instances.
2. Choose **Overwrite the existing version** when prompted. Existing custom type/material values can be retained; the new recess controls are instance parameters.
3. Position the channel so its section is recessed into the cabinet as intended.
4. Use **Modify → Geometry → Cut**. Select the cabinet/cabinet-door solid first, then select the Gola instance.
5. Repeat for any other cabinet elements that need cutting. Revit does not automatically establish these cuts just by placing the family.

Once the cut relationship exists, drag either endpoint grip to resize the channel and its recess together. Revit's temporary length dimension provides exact numerical resizing; the measured `Length` field in Properties remains read-only.

## Recess controls — instance Properties

| Parameter | Default | Effect |
| --- | --- | --- |
| Recess Clearance | 0.5 mm | Clearance beyond each section edge and behind the channel; internally limited to at least 0.1 mm. |
| Extra Cut Depth | 0 mm | Extends the cut farther behind the back of the channel. Negative inputs are treated as zero. |
| Front Cut Extension | 50 mm | Extends the void out through material in front of the grip opening. Increase if the host face still covers a deeply recessed channel. Negative inputs are treated as zero. |

The cutting length ends at the picked channel endpoints. End caps, clips, corner joints and brackets do not enlarge the recess. The recess width changes automatically with the chosen profile type; do not edit the internal type flags or formula controls.

To remove an established recess, use **Uncut Geometry**, selecting the cabinet and channel. There is no instance on/off switch: Revit's internal void `Cuts Geometry` setting does not disable these external project cut relationships.

The opening is a coordination recess, not a certified cabinet routing detail. Check clearance, remaining panel thickness, accessory fixing and the manufacturer's installation drawings before fabrication. The front extension removes material only from elements to which you apply Cut Geometry, but review those cuts carefully if one cabinet family contains multiple solids.

## Horizontal and vertical placement

Both directions use the same cutting mechanism. Draw the channel run on the intended work plane/face. Vertical types change the section; draw their placement line vertically on a vertical plane/face. The channel projects from its back datum toward its front. Recess it using the appropriate placement offset or work plane, then apply Cut Geometry.

## Host compatibility

This is for Gola instances placed directly in the project, not nested into the cabinet in Family Editor. Native **Casework**, **Furniture** and **Generic Model** solids are suitable targets. Linked elements, imported mesh/DirectShape geometry and some separately shared nested components cannot be cut like native cabinet solids. A cabinet door modeled under the **Doors** category is not a supported target for this loaded-void workflow; cabinet panels are normally Casework or Generic Models.

If no cut appears, check that the void intersects the target, you selected the cabinet first and Gola second, and the target category/geometry supports loaded void cuts. If only some panels cut, apply Cut Geometry to the actual separately selectable panel elements.

## Included files

- `Richelieu_Gola_Channel_Profiles_2025.rfa` — revised four-type family with brushed stainless appearance and existing accessory options.
- `Gola_Recess_Cutting_Examples_2025.rvt` — demonstration/test cabinet blocks with established recess cuts. These blocks demonstrate cutting, not complete cabinet construction.
- `Gola_QA_Casework_Panel.rfa` — simple test host; not required to use the Gola family in your project.
- `Gola_QA_Vertical_Casework_Panel.rfa` — native vertical test host used in the demonstration project.
- `cutting_validation.json` — actual Revit test measurements and results.
- PNG views — visual review exports from the demonstration project.

The original non-cutting delivery is preserved in the neighboring `gola` folder. Profile geometry, finish, accessory details and manufacturer research remain as documented in that original delivery; accessories are schematic.

## Verification — September 8, 2026

Saved and reopened in Revit 2025. All four types passed actual Casework volume-removal checks at 600, 1,000 and 2,400 mm, both endpoint edits, clearance/depth changes, and native Uncut/re-cut checks. The original channel solids were measured before and after adding the void and remained unchanged. All four types were also recessed into native vertical Casework faces and resized to 1,200 mm. Both exported views were visually inspected. No family or sample-project warnings were reported.

## Reference

[Autodesk: Cutting with voids in families when loaded](https://help.autodesk.com/cloudhelp/2025/ENU/Revit-Customize/files/GUID-7C940A08-1F62-465F-89BF-3800E3446FC3.htm) describes supported target categories and the cabinet-first, cutting-family-second workflow.
