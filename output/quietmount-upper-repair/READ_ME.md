# Upper keeper repair — 2026-09-14

Open QuietMount_BC_Replacement_READY.3mf to print only the two failed 19.05 mm upper keepers, B and C. H2D 0.4 mm / Textured PEI / PolyTerra settings retained. Both are tab-down with a 3 mm brim.

The previous tab-down upper keeper exports contain malformed mesh topology. This revision replaces the overlapping Boolean construction with directly connected surface rings. All ten upper keeper replacement STLs are included because the same topology problem affects the family. Do not reuse upper STLs from QuietMount_Tab_Down_READY.3mf. That earlier package is superseded for upper keepers only; lower bodies and covers are not validated or revised by this repair.

Envelope retained: 14 mm width, 15.8 mm tab footprint depth, 2.2 mm tab thickness, 8.6 mm head passage, 4.6 mm shaft passage, 4 mm mushroom bearing thickness. The nominal exterior is retained without the prior tiny edge bevel; the circular plan outlines remain. Head opening and nominal cover interface dimensions retained; physical fit still requires a test.

Each generated replacement has positive signed volume, nondegenerate faces, and exactly two incident faces per edge. Native slicer acceptance is recorded separately. Neither check establishes physical print success or anchor compatibility. The exact physical failure mechanism has not been independently observed.

The replacement script and both editable and sliced Bambu projects are included. No external textures are required. This package supersedes the upper keepers in the September 12 tab-down package.
