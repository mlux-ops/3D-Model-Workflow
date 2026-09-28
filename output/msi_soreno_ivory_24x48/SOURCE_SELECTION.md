# Source selection — MSI Soreno Ivory Matte 24x48 (NSORIVO2448)

All candidates are in `references/` (thumbnails in `references/_thumbs/`). Pixel sizes are native.
The MSI CDN was probed at 1,049 path variants (size folders `large/`, `detail/`, `variations/`,
`iso/`, `colornames/`, suffixes `-01`...`-06`, `-variation-0n`, `-detail`, `-v1`... ; see
`_work/fetch_log.json`). Only 8 URLs exist, none larger than 805 px, and there are **no variation /
multi-face images** for this colour.

## Duplicate test (a05_dupes.py, `_work/dupes.json`)

Every tile face (>= 30 % of a tile) was cut 5 px inside its joints, rescaled to one pitch, band-passed,
and slid over every other face (NCC, all translations, 0/180 deg, horizontal and vertical flips; 90/270
deg on square crops). Phase-randomised surrogates give a chance baseline of 0.03-0.15; a true match
gives 0.9-1.0. Result, face by face against the two full faces of the current MSI 24x48 swatch:

- **Face A** = top-right tile of `soreno-ivory-porcelain-24x48.jpg`. Matches at 0.93-0.98: the top-left
  partial of the same image, three faces of the paver swatch (one rotated 180 deg), five faces of the old
  Belmont reference (two mirrored), the flyer swatch, and **both** A-halves of the 24x24 swatch.
- **Face B** = middle tile of the same image. Matches at 0.92-0.97: the bottom tile of the same image
  (mirrored), the bottom-left partials, the rest of the paver/Belmont/flyer faces, and B's right half in
  the 24x24 swatch (twice, once rotated 90 deg).
- A vs B: 0.09-0.18 (independent).

**Independent real faces available: 2.** The 24x24 swatch shows A (both halves) and B's right half at
16.8 px/in, higher than the 11.2 px/in of the 24x48 swatch, so those regions were used at that
resolution (a06_master.py; registration NCC 0.75-0.84, colour fitted to the 24x48 swatch).

## Candidates

| File | Pixels | View | Decision | Reason |
|---|---|---|---|---|
| msi_porcelainceramic__soreno-ivory-porcelain-24x48.jpg | 805 x 805 | flat straight-on digital swatch, 24x48 half-bond | **ACCEPTED** (faces A, B) | Manufacturer swatch of the exact SKU size; 2 full faces, 11.2 px/in |
| msi_porcelainceramic__soreno-ivory-porcelain.jpg | 805 x 805 | flat straight-on, 24x24 2 x 2 | **ACCEPTED** (hi-res halves of A, B) | Same two print faces at 16.8 px/in; used only as resolution for regions of A and B |
| msi_hardscaping__detail__soreno-ivory-paver-24x24.jpg | 805 x 805 | flat, 24x24 | REJECTED | Byte-identical to the 24x24 porcelain swatch (same SHA) |
| msi_porcelainceramic__soreno-ivory-paver-24x48.jpg | 805 x 805 | flat, 24x48 half-bond | REJECTED | Arterra paver (different SKU); its faces are A and B again (NCC 0.95) |
| msi_hardscaping__detail__soreno-ivory-paver-24x48.jpg | 805 x 805 | flat | REJECTED | Byte-identical to the paver swatch above |
| msi_porcelainceramic__soreno-ivory-porcelain-2x2.jpg | 805 x 805 | flat, 2x2 mosaic | REJECTED | Different product (mosaic), chip-sized crops |
| msi_porcelainceramic__iso__soreno-ivory-porcelain-iso.jpg | 805 x 805 | flat, tiles at 45 deg | REJECTED | Rotated layout would need resampling; same print family, adds no face |
| msi_hardscaping__detail__soreno-ivory-arterra-porcelain-copings.jpg | 805 x 805 | angled product shot | REJECTED | Angled 3D view of a coping, not a flat face |
| msi_roomscene_soreno-ivory-porcelain-a...e.jpg, -living-1457-alt-02.jpg | 960-1200 px | room scenes | REJECTED | Room renders: perspective, lighting, furniture (rule: never room scenes) |
| pdf_images/msi_pdf_soreno-porcelain-flyer_03_439x439.png | 439 x 439 | flat Ivory swatch in MSI flyer | REJECTED | Lower-resolution copy of the 24x48 swatch (faces A, B) |
| pdf_images/..._00_2623x3391.png | 2623 x 3391 | flyer cover room scene (Grigio) | REJECTED | Room scene, different colour |
| pdf_images/..._01, _02, _04 | 439-633 px | Grigio / Taupe swatches | REJECTED | Different colours |
| aaaplus_ / gohardwood_ / mosaicmosaic_ soreno-ivory-porcelain-24x48.jpg | 805 x 805 | flat 24x48 | REJECTED | Older copy of the MSI 24x48 swatch (joint offset 95 vs 90 px); faces A, B (NCC 0.96-1.00) |
| tileplace_soreno-ivory-porcelain-24x48-1.jpg | 805 x 805 | flat 24x48 | REJECTED | Byte-identical to the current MSI 24x48 swatch |
| gohardwood_soreno-ivory-porcelain.jpg | 805 x 805 | flat 24x24 | REJECTED | Copy of the MSI 24x24 swatch |
| wallandtile_nsorivo2448_b.jpeg | 800 x 800 | flat, 24x48 at 45 deg | REJECTED | Rotated dealer composite; no new face expected, resampling loss |
| stoneandtileshoppe_soreno-ivory-porcelain-24x24.jpg | 255 x 255 | flat 24x24 | REJECTED | Tiny copy of the 24x24 swatch |
| villohome_soreno-ivory-24x24-angle-view.png | 2000 x 2000 | angled product shot | REJECTED | Angled view (rule: straight-on only) |
| repo_belmont_PrimaryBath_Floor_...NSORIVO2448.jpg | 1000 x 1000 | flat 24x48 half-bond (earlier supplied file) | REJECTED | Faces A and B again (NCC 0.92-0.95), 10.4 px/in; the superseded build's source |
| repo_belmont_soreno_original.jpg | 805 x 805 | flat 24x24 | REJECTED | Byte-identical to the MSI 24x24 swatch |

## Spec sources (facts, not colour)

| File / page | Fact used |
|---|---|
| msi_pdf_soreno-porcelain-flyer.pdf (MSI) | 1/8 in grout recommended; "less than 33% staggered brick lay" for rectangles; rectified; glazed; 3/8 in thickness; variation V4 |
| MSI product page `_work/page.html` | SKU NSORIVO2448, matte, shade variation "Low", limestone style |
| villohome.com product JSON/page | Country of origin Italy; edge rectified; thickness 0.39 in; box 48.4 x 24.4 x 3.75 in |
| wallandtile.com, shadesofstone.com, mosaicmosaic.com | 0.39 in thickness, rectified, 2 pcs / 16 sq ft per box |
| Home Depot (Browser pane; listing now titled "Sorena Cream NSORCREAM2448") | 9.90 mm thickness, rectified, 48 x 24 in (nominal restated) |
| msi_pdf_porcelain-installation-guide-v2.pdf, msi_pdf_soreno-dcof.pdf | No size data |

No source publishes the actual (calibrated) face size. See README for the size decision.
