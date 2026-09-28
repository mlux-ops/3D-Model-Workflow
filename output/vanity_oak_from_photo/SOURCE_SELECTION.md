# Source selection: Vanity Oak colour map

The only source is `references/u12_vanity_product_photo.jpg`: 1600 x 1600 px, supplied by the user. It is a 3/4 product photo or render of a white-oak vanity with a white top, rounded corner posts, 6 drawers, 2 doors, a top apron and a bottom rail.

**Is the render built from one repeated texture?** No. `_work/source_dupes.json` tested 184 windows of 6 x 3 in (6 x 2 in on the rails) under 4 grain-preserving transforms:
- the highest match between any two source regions is NCC 0.26 (median 0.18);
- a planted copy scores 1.00;
- a phase-randomised surrogate scores 0.16.

So every panel is distinct real content.

## Panels

The density column is native px/in on the front plane, assuming a 48 in wide vanity.

| Region | Density | Decision | Reason / use |
|---|---|---|---|
| Door L (10.74 x 28.33 in) | 24.9 | **Accepted** | Flat and evenly lit. Rotated 90° and cropped to 27.88 x 10.22 in. Anchors leaves B2 and B3. |
| Door R | 24.0 | **Accepted** | As above. Anchors leaves B5 and B6. |
| Drawer L1, L2, L3 (10.73 x 9.45 in) | 25.9 | **Accepted** | Horizontal grain. Cropped to 10.28 x 8.97 in. Extend the left-door leaves; the L2 remainder supplies strips for the apron and left-door-remainder leaves. |
| Drawer R1 | 23.1 | **Accepted, corrected** | Carried a specular veil: brighter, greyer and flatter than the rest. A neutral veil of 0.053 (linear) was removed, which brought G/B from 1.72 to 1.98 against the reference 1.91. Extends the right-door leaf. |
| Drawer R2 | 23.1 | **Accepted, corrected** | Slight veil (0.018) removed. Extends the right-door leaf; the remainder supplies strips for the rail and right-door-remainder leaves. |
| Drawer R3 | 23.1 | **Accepted** | Softest crop (grain contrast 0.046 against a median of about 0.075). Used as one full piece in the right-door leaf, with detail gain capped at 1.4. |
| Top apron (43.0 x 2.70 in) | 24.4 | **Accepted, trimmed** | Veil of 0.050 removed. Rows 65–69 of the crop dropped: reveal shadow near the left post. Each row flattened along the grain to remove the counter shadow and post shading. Full-length leaf B1. |
| Bottom rail | 24.5 | **Accepted, trimmed** | Top 2 rows dropped (edge highlight, +15 %). Row-flattened as above. Full-length leaf B4. |
| Left side panel | about 10 across the grain | **Rejected** | Strongly foreshortened (22 in deep over about 220 px). Across-grain resolution is less than half that of the front, so the grain would be visibly blurred. |
| Rounded corner posts | n/a | **Rejected** | Curved surfaces with strong shading gradients; not flat and not recoverable by a homography. |
| Right side / right post | n/a | **Rejected** | Seen nearly edge-on. |
| White top, sink, wall, floor shadow, toe space | n/a | **Rejected** | Not wood, or in cast shadow. |

## Material budget

The accepted crops hold 1,340,948 px at 32 px/in. The map uses 1,179,648 distinct source pixels (1536 x 768), which is 88 %. The remainder was used in overlaps and cut away, or is spare alignment slack. That is why the full 48 x 24 in is possible without reusing any pixel, but no larger.
