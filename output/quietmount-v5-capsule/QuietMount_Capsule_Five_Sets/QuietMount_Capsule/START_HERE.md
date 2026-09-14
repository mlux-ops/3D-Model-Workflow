# QuietMount Capsule — five sample sets

One rounded lower cradle supports each sample. A smaller upper keeper prevents forward tipping. Each uses one concealed screw; neither has a plate or spacer behind the transparent sample. Removing the upper cover and loosening its screw allows the keeper to turn sideways for removal.

The lower capsule is 29 mm wide × 12 mm high, and the upper capsule is 13 × 12 mm. These are slightly larger vertically than the concept so a real screw head, a removable cover and surrounding plastic can fit. The nominal front overlap is 2.6 mm at both edges. Lip outlines taper at the ends for printing. Bodies extend under/over the sample's thickness; the supports remain visible from the side. Covers have a fine perimeter seam and a hidden fingernail notch.

## Open and print

Open **QuietMount_Capsule_H2D_READY.3mf** in Bambu Studio. The editable project is also included as **QuietMount_Capsule_H2D_Project.3mf**.

Open the 3MF as a **project**, not as geometry only. It contains the printer, process, filament and object settings; importing separate JSON presets is optional.

To install reusable presets, use **File → Import → Import Configs** and select the two JSON files in `presets`: `QuietMount_Process.json` and `QuietMount_PolyTerra_PLA.json`. The process appears as **QuietMount Capsule - PolyTerra 0.08 @H2D**, and the filament as **QuietMount Capsule - PolyTerra PLA @H2D**. For the printer, select the built-in **Bambu Lab H2D 0.4 nozzle**; no custom printer import is needed. If H2D is absent, enable it through Bambu Studio's printer selection. An internal printer configuration file was mistakenly included in the first ZIP; it has been removed from the updated package.

- Plate 1: optional small cover-fit check. Left to right: gauge, easy cover, standard cover, snug cover. This tests only the removable screw cover, not the sample fit or load capacity.
- Plate 2: all five sets, four parts per set. Columns A–E, left to right: **12.7, 19.05, 19.05, 20, 22.225 mm**. Rows contain lower cradles, upper keepers, lower covers, upper covers. The 20 mm set is for the measured terrazzo sample.

Bambu Studio's estimates: **42 minutes / 2.0 g** for the optional fit plate; **11 hours 17 minutes / 63.9 g** for all five sets. Both plates sliced successfully without warnings. Actual time and consumption can vary.

The main plate uses standard covers. If the fit coupon shows that easy or snug fits better, replace the covers with the corresponding optional STLs and re-slice. They use identical attachment geometry in both sizes. Choose a cover that presses in and pulls out by hand; do not force or glue it. If none fits properly, adjust the cover dimensions before using the full batch.

Printer: Bambu H2D, 0.4 mm standard nozzle, Textured PEI. Process: 0.08 mm layers, six walls, 100% rectilinear infill; 220°C first layer / 215°C thereafter, bed 55°C, 8 mm³/s flow limit, auxiliary fan off. These are conservative starting settings for PolyTerra PLA, not a calibration for your spool. The two nozzles are configured as Standard, with all parts assigned to filament 1. Select your actual loaded PolyTerra spool when mapping filament to the printer.

Bodies are laid on a small flat side with a 3 mm brim. Preserve that orientation: it keeps the cradle continuous within each layer. Screw bores have 45-degree roofs, and front lips have tapered ends, to avoid supports. Covers print face-down with their split retaining petals pointing upward. The textured plate gives the cover faces a consistent matte texture. Remove brims and any burrs before fitting parts together.

## Hardware

Buy **10 #6 pan-head screws and 10 matching painted-drywall anchors**: one screw for each lower cradle and each upper keeper. Screw shaft diameter must be no more than 3.5 mm, head diameter no more than 7.5 mm, and head height no more than 2.8 mm. Check the actual hardware against the fit gauge. Use pan heads with a flat underside; countersunk heads do not match these bearing surfaces.

Choose screw length from the anchor manufacturer's required engagement **plus the printed thickness under the screw head**:

| Sample thickness | Printed thickness under head |
|---|---:|
| 12.7 mm | 9.95 mm |
| 19.05 mm | 16.30 mm |
| 20 mm | 17.25 mm |
| 22.225 mm | 19.48 mm |

The screws often bundled with drywall anchors may be too short once this printed thickness is added. Follow the anchor's specified diameter, length and installation method; the printed fit gauge does not verify anchor compatibility. A narrow screwdriver shaft must reach through the 8 mm head recess. Do not use countersunk/bugle drywall screws.

## Install one set first

1. Match a lower cradle and upper keeper to the sample's actual thickness. Keep the caps off. Verify the sample seats on the lower cradle, the lip reaches its front, and nothing presses tightly on the sample.
2. Mark the bottom edge of the sample. The lower screw center is **6 mm below that edge**, centered horizontally on the sample. Install its anchor and lower cradle. Snug the screw by hand until the cradle cannot rotate. Stop if the plastic distorts; the cover must still seat. The lower cradle relies on this clamping friction to resist rotation.
3. Rest the sample on the lower cradle and locate the upper keeper. The circular bore is the pivot. The top keeper's lowest body edge should sit approximately **1.2 mm above the sample's top edge**, with its front lip pointing down. Mark the screw center **7.2 mm above the actual sample top**. For an exact 95.25 mm square, the two screw centers are **108.45 mm apart vertically**. Mark using the actual sample; this is not an adjustable-height holder.
4. Remove the sample before drilling. Install the upper keeper. Its screw should be snug enough to prevent rotation in service, but accessible when the cover is removed. To insert the sample, loosen the screw slightly and rotate the keeper 90° sideways, place the sample on the lower cradle, rotate the keeper down, then snug the screw. Do not use the keeper to compress brittle material.
5. Press each cover in by hand, keeping the fingernail notch at the outer edge away from the sample. The cover's split petals enter the head recess and sit in front of the screw head. The cover is cosmetic and does not carry the sample's weight. Remove the upper cover before loosening that screw to remove a sample.

Allow approximately 1.2 mm nominal clearance from the wall; there is no rear spacer to maintain that gap. The sample can move closer to the wall. The lower cradle does not have side stops: center the square and avoid sideways knocks. If the wall is uneven or the cradle can rotate when gently handled, correct the mounting before displaying the sample.

## Validation and limits

See geometry_checks.json and stl_checks.json for digital checks. These cover closed geometry, sample clearance, the upper keeper's release movement, and the specified screw/head envelope. They do not establish strength, long-term retention or a load rating. The covers intentionally have slight interference and need the fit check on your printer.

This is a prototype without physical fit, pull-out, impact, creep or wall-anchor testing. Your terrazzo estimate is approximately **443 g** from the stated 10 lb/ft² and 3¾-inch square size. Test its 20 mm set in a low, protected location before displaying it higher. Check for movement, cracks and loosening. Keep PLA away from heat and direct sun. All five sets should be tested with their actual samples; only the terrazzo sample has an estimated weight here.

Do not treat the earlier independent-peg or adhesive-frame packages as parts of this design. This package contains the complete capsule system.
