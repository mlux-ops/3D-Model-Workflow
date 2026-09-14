# TwinGrip — adjustable sample wall pegs

**Printable prototype, version 1. Dimensions are millimetres. Not load-rated or physically print-tested.**

Designed for approximately **3¾ inch (95.25 mm) square samples, ½–1 inch (12.7–25.4 mm) thick**. Use two pegs beneath the sample and two identical pegs inverted above it. Each front hook telescopes and locks with an M3 bolt and captive nut. Slots in the wall feet allow 8 mm of vertical adjustment.

![Assembled holder](assembly-preview.png)

## Why this mechanism

The lower pair bears the weight; the upper pair limits tipping and lift-out. A 5 mm front lip captures each edge. A rectangular sliding fit prevents the hook from rotating, and a small underside relief lets the locking bolt squeeze the fit. Metal hardware avoids printed screw threads and continuously stressed spring catches.

Independent pegs accept modest variation in sample width and height without reprinting a frame. They also leave mounting screws accessible. **The trade-off is visible mounting tabs above and below the sample.** This is a compact serviceable prototype, not a demonstrated global optimum for size or strength. A concealed rail would reduce visible hardware but require a different, more involved assembly.

The sample rear is 12 mm (0.47 inch) from the wall. The outermost printed lip is 28.4–41.1 mm (1.12–1.62 inches) from the wall over the supported thickness range. At maximum extension the sleeve overlaps the tongue by 9.1 mm. Overall installed height is approximately 177 mm (6.97 inches) for a nominal sample; the mounting feet account for the additional height.

## Print these parts for ONE sample

| File | Quantity | Supplied print orientation / size |
|---|---:|---|
| `01_wall_peg.stl` | 4 | Side down; 25 × 37 × 16 mm |
| `02_telescoping_hook.stl` | 4 | Side down; 25.2 × 24.2 × 26 mm |
| `03_rear_spacer.stl` | 2 | Flat down; 18 × 18 × 11.5 mm |
| `00_complete_print_plate.stl` | Alternative | All ten parts laid out together; do not also print the individual files |

All STLs use mm; import at 100%. The assembly `.blend` file includes the non-printable sample, wall, and illustrative hardware. **Do not print the assembled scene.**

## Starting print settings

- PETG, indoor use; 0.4 mm nozzle, 0.20 mm layers, 6 walls, 6 top/bottom layers, 50% gyroid or cubic infill. Use your filament maker's temperature profile.
- Retain the supplied orientations. The main load-bearing hook profiles lie in the layer planes.
- The hook contains an internal bridge across the 12.4 mm bore height. Inspect the slicer's bridge preview and use a proven PETG bridge profile. If your printer cannot bridge it cleanly, use removable support inside the bore, accessible from the open rear. Support-free printing is an intention, not physically verified.
- The wall foot's sideways mounting slot also has a short bridge. Check its roof in the slicer.
- The tongue is 16 × 12 mm; its bore is 16.4 × 12.4 mm. This is 0.2 mm clearance per side before locking. Print **one peg and one hook first**. Remove bridge droop and elephant foot until the hook moves by hand without forcing it. Clear the 3.5 mm bolt openings if needed. Do not scale the entire model to fix a sliding fit.
- Check that an M3 nut fits its 5.8 mm across-flats pocket before printing the remaining hooks. The nut pocket should face upward in the supplied hook orientation.

PETG and orientation choices are informed by [Prusa's PETG guidance](https://help.prusa3d.com/article/petg_2059) and [modeling for 3D printing](https://help.prusa3d.com/article/modeling-with-3d-printing-in-mind_164135). The exact settings above are proposed starting settings for this prototype, not published load-test results.

## Hardware for ONE sample

- 4 × M3 × 30 mm socket-head machine screws.
- 4 × standard M3 hex nuts, approximately 5.5 mm across flats and 2.4 mm thick. Use ordinary nuts; the pocket is not sized for a nylon-insert locknut.
- 4 × M3 flat washers beneath the screw heads.
- 4 × wall screws with shanks no larger than 4.5 mm, plus flat washers about 10–12 mm outside diameter. The printed mounting slot is 4.8 mm wide. Select screw length and anchors for the actual wall and load; these are not specified without knowing the wall construction.
- Thin adhesive tape for the two rear spacers, approximately 0.5 mm installed thickness. **Spacer plus tape must total about 12 mm.** Use tape only to locate the spacers; screws carry the mounting load.

## Assemble and mount

1. Fit each nut in the outside hex pocket of a hook. Slide the hook onto a peg with its lip facing toward the sample. Feed the M3 screw and washer through the round hole, the peg's long slot, and into the nut. Leave it loose enough to slide. The full sample holder uses four identical assemblies.
2. Locate the lower peg centers about **56 mm apart**, each 28 mm from the sample centerline. Keep their support surfaces level. Secure the two lower wall screws near the **top ends of the slots**: this seats the feet against further downward movement. Use the actual parts to mark the wall, with an appropriate level and anchors.
3. Attach the rear spacers to the wall behind the sample, approximately 52 mm apart, away from the hooks. They establish a consistent rear plane; the sample rests against them.
4. Set the lower hook depth for the actual sample. The design includes approximately **0.5 mm front clearance** with a 12 mm rear setback. Tighten the M3 screws only until the hooks stop sliding. Tightening locks the slider; it must not crush the sample. Stop if the plastic distorts or a nut pocket cracks.
5. Place the sample on the two lower hooks. Install the upper assemblies upside down, with lips pointing down. For a nominal 95.25 mm sample, the upper and lower peg reference origins are **102.95 mm apart**. This places the upper support faces about 0.5 mm above the sample. Mark from the actual fitted parts, not solely from this nominal number.
6. Set each upper foot toward the **lower end of its wall slot** before tightening, leaving roughly 6 mm of upward opening travel. The nominal upper screw location is 129.45 mm above the lower peg origin, adjusted within the slot to leave that travel. Lower screws can sit at the upper slot endpoint, 22.5 mm below the lower peg origin. There is no single mandatory drill spacing because of the slots.
7. Adjust upper hook depth and tighten the M3 fasteners. Confirm both front lips overlap the sample, all feet resist rotation, and the lower pair supports its weight. Do not use pressure from the top pegs to clamp a brittle sample tightly.
8. To exchange a sample, support it, loosen the upper wall screws enough to move the upper feet, and lift both upper assemblies at least 6 mm before tipping the sample forward. Retighten after replacing it. Change hook depth when sample thickness changes.

**Edge geometry matters:** the retention calculation assumes reasonably square, intact edges. Rounded edges, deep bevels, soft material, or crumbly stone may require deeper lips or pads. The holder does not positively capture the left/right edges; it is for a stationary indoor wall display, not a moving or vibration-prone installation.

## Checks and limits

The generated source meshes are checked for one connected solid, positive volume, and zero non-manifold edges. The final STL triangles are independently checked during packaging. Assembly interference is tested at 12.7, 16, 19.05, 22, and 25.4 mm thickness; numerical Boolean residuals below 0.02 mm³ are tolerated and recorded. See `geometry_checks.json` and `stl_checks.json`.

These checks establish geometry, not strength. The heaviest sample, wall material, printer, and filament were not supplied when this version was created. There is **no safe working load claim**. Before placing a valuable sample on the wall, test a complete set with a non-fragile substitute matching its weight, near the floor, and inspect for hook movement, foot rotation, cracking, and loosening. Check again after sustained loading. Modify the design if it moves; do not solve slip by progressively overtightening plastic.

## Editable source

`TwinGrip-assembly.blend` is the editable assembled model. `build_model.py` reproduces the solid geometry, oriented STLs, mesh checks, and previews with Blender 5.x. `package_model.py` verifies the exported STLs and builds the complete plate and ZIP. No manufacturer model is used.

![Mechanism with sample removed](mechanism-preview.png)
