# Inferences and conflicts: Miele KM 3054-1

Every dimension in `source/km3054_geometry.py` carries one of PUBLISHED, DRAWING, PHOTO or
INFERRED. This file lists what is not printed by Miele and every conflict between sources.
Sources and hashes: `references/miele_km3054_1/SOURCE_MANIFEST.md`.

## Conflicts between sources

| Item | Values | Used | Why |
|---|---|---|---|
| Width | 942 mm vs 37 1/8 in (= 942.98 mm) | 942 mm | Miele quotes the inch value as a rounded conversion of the mm value; the drawing prints 942. |
| Depth | 526 mm vs 20 3/4 in (= 527.05 mm) | 526 mm | Same reason; drawing prints 526. |
| Height | 53 mm vs 2 1/8 in (= 53.98 mm) | 53 mm | Drawing: 7 above + 46 below the countertop = 53. |
| Cut-out depth | page 19 3/4 in (500 mm); drawing 490-500 | casing 490 deep, parameter `Cutout Depth` 500 | Casing must fit the smallest permitted cut-out. |
| User wording | "rangetop" | built-in gas cooktop | The linked page and drawings show a drop-in cooktop on glass, not a rangetop with a front control panel. Modelled as the page shows. |
| Gas connection side | page "Hinten rechts" (German, rear right) | rear right | Untranslated field on the US page; drawing agrees. |

## Not published (INFERRED or PHOTO)

| Item | Value | Basis |
|---|---|---|
| Grate (pan-support) height | 30 mm above the glass (37 mm above the counter) | Oblique photo 20000146968; Miele does not include grates in the published 53 mm height. |
| Grate ring height | 20 mm above the glass | Oblique photos. |
| Grate bar section | 8 mm wide, full 30 mm tall plates | Top view bar width 22-25 px (7.5-8.5 mm); oblique photo shows tall plates. Real bars taper; modelled as plates. |
| Grate layout | four right-hand grates plus one wok grate; bar offsets +78 / -72 mm, 45 degree diagonals | Top view 20000084693 (overlay check `logs/offline_plan_overlay.png`). Real castings have curved transitions and feet; modelled as straight plates. |
| Knob height | 15 mm body + 8 mm grip fin (23 mm above glass) | Oblique photos; diameter 36.7 mm is PHOTO. |
| Burner heights | bowl 4 mm, head to 12 mm, cap to 17 mm above the glass | Oblique photos; cap diameters are PHOTO. |
| Burner head and bowl radii | cap + 3 mm; bowls 52-82 mm | Top view, approximate. |
| Wok burner | inner cap r 22, inner head r 33, outer flame ring r 36-72, bowl r 82 | Top view crop; wok ring accessory (loose) not modelled. |
| Casing plan | 914 x 490 mm, 14 mm side insets, 16 mm front inset | Drawing insets 14/16; rear inset not printed, depth set to the 490 minimum cut-out. |
| Electronics housing | 207 x 86 mm at 379 mm from the left edge and 226 mm from the front, bottom 78 mm below the top | Drawing values; which value is length and which is offset is my reading of a crowded drawing. Only the 78 mm built-in height is a published gate. |
| Gas connection stub | r 10.5 mm, bottom 71 mm below the top, 86 mm from the right and 61 mm from the rear edge | Drawing values "71", "86", "61"; position assignment inferred. |
| Mains connection box (63) and cable | not modelled | Small, below the counter, position ambiguous. |
| Countertop cut-out | not cut in the host | The family does not void the host; the casing passes through the disposable floor host in QA. |
| Printed glass graphics, Miele logo, SCHOTT CERAN mark, timer touch controls | not modelled | Surface print only. |
| Frame band | 7.5 mm stainless band, flush with the glass top | Top view 22-24 px; flush top inferred from the low oblique photo. |

## Materials (sampled from 20000084693)

Metals use a percentile below the pixel median so that Revit's specular lift is not counted
twice; nothing is self-illuminated and no bitmaps are bound.

| Parameter | RGB | Sample |
|---|---|---|
| Top Finish | 0, 0, 0, glossiness 1.00, reflectivity 0.08 / 0.95 | USER REVIEW 2026-10-22: pitch black polished glass. The photo median (0,18,28) carries a blue tint from the studio lighting that the user rejected. |
| Frame Finish | 120, 122, 125 | frame p40 (median 122, 122, 129) |
| Grate Finish | 73, 72, 77 | bar p25 (median 90, 90, 100); product: matte black enamel |
| Burner Finish | 78, 74, 75 | power-burner cap p40 (median 79, 76, 77) |
| Burner Ring Finish | 183, 180, 188 | wok head p25 (median 231, 230, 233) |
| Knob Finish | 184, 185, 187 | knob p40 (median 192, 192, 193) |
| Housing Finish | 150, 152, 155 | INFERRED, not visible in any source |
