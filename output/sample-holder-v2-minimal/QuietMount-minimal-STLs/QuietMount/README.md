# QuietMount — minimal sample holder, version 2

Designed around a **95.25 × 95.25 mm (3¾ × 3¾ inch) square**, with interchangeable clips for thickness. This replaces TwinGrip's four exposed block assemblies with a concealed frame and **three 6 mm wide tabs**, overlapping the sample face by approximately 3 mm. Nominal face coverage is 54 mm², about **0.6%** of the sample face.

![Minimal installed appearance](minimal-preview.png)

The two bottom clips carry the sample; the top clip retains it. All screw heads and the frame are behind the sample in a straight-on view. The arms remain visible when viewed from above, below, or the side. The rear standoff is **10.5 mm (0.41 inch)**. This version prioritizes minimal visual obstruction; it is not a physically tested or load-rated product.

## Choose a thickness set

Measure the sample. Print ONE frame, ONE carriage, TWO matching lower clips, and ONE matching upper clip. There are five printed components per holder. The complete print plate for your thickness contains exactly this set.

| Nominal thickness | Individual clip filenames | Complete print plate |
|---|---|---|
| ½ inch / 12.7 mm | `lower_12.70mm.stl`, `upper_12.70mm.stl` | `plate_12.70mm.stl` |
| ⅝ inch / 15.875 mm | `lower_15.88mm.stl`, `upper_15.88mm.stl` | `plate_15.88mm.stl` |
| ¾ inch / 19.05 mm | `lower_19.05mm.stl`, `upper_19.05mm.stl` | `plate_19.05mm.stl` |
| ⅞ inch / 22.225 mm | `lower_22.23mm.stl`, `upper_22.23mm.stl` | `plate_22.23mm.stl` |
| 1 inch / 25.4 mm | `lower_25.40mm.stl`, `upper_25.40mm.stl` | `plate_25.40mm.stl` |

Common files: `01_concealed_frame.stl` and `02_top_carriage.stl`.

The pockets include 0.3 mm of nominal front clearance. Do not force a thicker sample into a smaller set. Intermediate measured thicknesses need a matching generated set; do not stretch or scale the entire model. `THICKNESSES` in the supplied source controls clip reach. This is **interchangeable thickness sizing**, not continuous thickness adjustment.

The fixed clear height is 96.05 mm: nominal sample height plus 0.8 mm. Squares approximately 94.75–95.75 mm high have 1.3–0.3 mm top clearance. Measure irregular or chamfered samples before relying on the 3 mm overlap. Width can vary modestly without changing the frame, provided the two lower clips stay fully beneath the sample.

## Hardware per holder

- 4 × **M2.5 × 8 mm, 90-degree countersunk/flat-head screws**, with head diameter no larger than 5.6 mm. Flat-head screw length includes the head.
- 4 × ordinary M2.5 hex nuts, approximately 5 mm across flats and 2 mm thick. These go in the frame's rear pockets before wall installation.
- 2 × **M3 × 25 mm socket-head screws** and 2 ordinary M3 nuts. One screw connects the top hook to its carriage; the other retains the carriage on its fixed stop.
- Optional thin M3 washer for the vertical retaining screw, outside diameter at most 7 mm. Do not add a large washer to the top hook's cross screw.
- 2 × wall screws, shank no larger than 4.5 mm, with appropriate anchors for the actual wall and load. Mounting holes are 4.8 mm diameter and 40 mm apart horizontally. Washer outside diameter up to 9 mm fits the frame.

The M2.5 screws allow the lower clips to remain only 6 mm wide. M3 screws are too large for these four lower-clip holes. Ordinary nuts are intended; nylon-insert nuts will not fit these pockets.

## Print settings and orientation

- Import at **100%, millimetres**. All individual STLs and plates are already oriented for printing.
- Starting point: PETG, 0.4 mm nozzle, 0.20 mm layers, 6 walls, 6 top/bottom layers. Use 100% infill for the three small hooks, and 40–50% for the frame/carriage. Use your filament manufacturer's temperature profile.
- The narrow hook profiles lie flat on their sides, with their cantilevers running within the layers. Do not rotate them to print the hook upright.
- The frame lies with its wall face down. Rear nut pockets bridge about 5 mm. The guide flange has short underside overhangs: inspect the slicer and support these if needed. Keep support away from the rear nut pockets where possible, or clean the pockets thoroughly.
- The carriage prints on its side. Its internal slots include short bridges. Inspect these surfaces before assembly. Support-free printing has not been physically demonstrated.
- Nominal sliding clearance is 0.2 mm per side. Start by printing the frame and carriage to test the slide; remove bridge droop/elephant foot rather than forcing the parts. The upper hook's keyed socket also has 0.2 mm side clearance.
- Clear M2.5 openings to 2.8 mm and M3 openings to 3.4 mm if your printer makes tight holes. Use hand tools gently. Confirm nuts fit before assembling.

## Assemble

1. Insert four M2.5 nuts into the frame's rear pockets. Bolt two matching lower clips to its front using the four M2.5 flat-head screws. Each clip uses two screws; the heads must sit flush. Do this before mounting the frame so the nuts remain accessible.
2. Insert an M3 nut into the frame boss beside the top guide. Its pocket opens upward. Hold it in place while starting the vertical screw during assembly.
3. Seat the matching upper hook in the small keyed socket at the top of the carriage. Insert an M3 nut in the side pocket and fit the M3 × 25 cross screw. Snug it gently. The rectangular socket prevents rotation; it is not a hinge.
4. Slide the carriage down from the top of the T guide until it rests on its hard stop. Feed the second M3 × 25 screw downward through the side lug and engage the nut in the frame boss. This screw retains the carriage; it does **not** set the sample height.
5. Position and level the frame on the wall. The two wall holes are 40 mm apart, at Y=38.5 mm above the sample's lower edge. Mount with suitable anchors and screws. Check that the frame stays flat and the front of every wall screw clears the 10.5 mm rear sample plane.
6. Loosen the vertical M3 screw by approximately 12 turns (6 mm for standard M3 × 0.5 thread), keeping it engaged. Lift the carriage approximately 6 mm by hand. The screw loosening permits the lift; it does not automatically raise the carriage.
7. Place the sample on the lower hooks and against the frame's three rear pads. Lower the top carriage onto its stop, then snug the vertical retaining screw. The upper arm should have slight clearance over the sample and its lip should overlap the front. Never tighten a too-large sample into place.
8. To remove the sample, support it, loosen the vertical retaining screw, lift the carriage 6 mm, tip the sample forward, then lift it clear of the lower lips. The screw is reached from above through the gap behind the sample, to the right of the top tab.

Changing thickness requires exchanging the three small hooks. The frame and carriage are reused. The lower hooks' front screws are accessible after removing the sample; the nuts remain captive against the wall.

## Verification and limits

Source solids and exported STLs are checked separately for mesh closure and degenerate faces. Assembly checks cover every supplied thickness, sample contact, and the 6 mm top opening motion. Floating-point intersection residuals below 0.04 mm³ are recorded as numerical tolerance. See the included JSON reports.

**No physical print test, strength test, or safe working load rating has been established.** Narrower visible hooks necessarily reduce the structural margin relative to version 1. The heaviest sample and printer/material remain unspecified. Test with a non-fragile substitute matching the actual weight, close to the floor, before displaying valuable samples; inspect again after sustained loading. If it slips, cracks, or permanently bends, stop using it and increase hook dimensions. The design is for stationary indoor display and does not positively capture the left/right edges. Deep bevels, fragile edges, heat, and impact are outside the verified geometry assumptions.

## Editable files

`QuietMount-assembly.blend` contains the editable assembly. `build_model.py` regenerates the solids, STLs and previews in Blender 5.x. `package_model.py` validates the exported STLs, assembles the print plates and creates the ZIP. The illustrated wall, sample and hardware are reference objects and are not included in the printable STLs.

![Hidden mechanism with sample removed](concealed-mechanism.png)
