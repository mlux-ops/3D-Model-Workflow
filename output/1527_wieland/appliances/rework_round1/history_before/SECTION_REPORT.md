# 1527 Wieland - Appliances section report

Recorded 2026-10-02T14:36:37.480895+00:00.

**27 inventory rows processed; 21 unique native Revit 2025 working families. 18 rows are DOWNLOADED; 9 rows are BUILT_WITH_LIMITATIONS.** Two rows contain LG washer/dryer pairs, and duplicate selections reference the same canonical family.

All 21 working RFAs were saved, reopened and placed in Revit 2025. All 27 rows, including the nine originally marked Agent Ignore, have individual notes. No Smartsheet write or Drive upload was performed.

The final artifact audit passed **232 of 232 checks** covering row coverage, file hashes, native evidence, category, preview presence, dimension statements and custom finish-map dependencies. See `artifact_audit.json`. The review holds below remain in force.

**Delivery is not released.** Five custom models pass the full published-envelope dimensional comparison; two custom models pass body dimensions only. Fourteen downloaded manufacturer models have full-envelope differences against the referenced published dimensions. Their native files are available, but those comparisons are not approved by this report.

## Decisions and holds
- The Miele KM 3054-1 G and GE GFD55GSSNWW corrections govern the obsolete row model text. The Trade-Wind I32363RC model governs conflicting vendor wording.
- The cooktop casing is 53 mm high; the modeled full height is approximately 88 mm because grate height is inferred. The hood body is 330.2 mm high; modeled full height is 355.6 mm because collar extension is inferred. Neither full-height gate is represented as passed.
- Three ignored rows have incompatible description-versus-URL identities: T24UR905RP refrigerator versus warming drawer; PRD48WISGU 48-inch range versus 30-inch oven; WD30W warming drawer versus Zephyr hood. Working families follow the exact URLs and remain explicit design holds. T18IW905SP and MC30WP are separately documented model-selection assumptions.
- Manufacturer-family material editability is only proven for parameters with geometry evidence. Miele source materials remain nested; T24UR905RP and T42IT100NP expose unproven imported-material controls. See individual results rather than assuming downloaded content is fully parametric.

## Row register
Paths are relative to `output/1527_wieland/appliances/`. Native PASS means save/reopen, category, placement and actual exported preview; fit and material results remain separate.

| Row ID | Item / working model | Status | RFA path | Gate results | Note |
|---|---|---|---|---|---|
| 3292695531945860 | WM4000HBA / DLGX4001B | BUILT_WITH_LIMITATIONS | `lg_wm4000hba/lg_wm4000hba_R2025.rfa`<br>`lg_dlgx4001b/lg_dlgx4001b_R2025.rfa` | WM4000HBA: Native PASS; fit PASS; material 5/5; warnings 0; DLGX4001B: Native PASS; fit PASS; material 5/5; warnings 0 | One row is a washer/dryer pair: both separate native families are provided. Black Steel follows the B model suffix. |
| 7384660666023812 | KWT 6722 iS | DOWNLOADED | `miele_kwt6722is/miele_kwt6722is_R2025.rfa` | KWT 6722 iS: Native PASS; fit HOLD; material 0/0; warnings 0 | Exact specified or linked model retained; see canonical notes for measured fit and finish limits. |
| 3328172767117188 | G 5051 SCVi ADA | DOWNLOADED | `miele_g5051scvi/miele_g5051scvi_R2025.rfa` | G 5051 SCVi ADA: Native PASS; fit HOLD; material 0/0; warnings 0 | Exact specified or linked model retained; see canonical notes for measured fit and finish limits. |
| 4418595438788484 | H 7280 BP | DOWNLOADED | `miele_h7280bp/miele_h7280bp_R2025.rfa` | H 7280 BP: Native PASS; fit HOLD; material 0/0; warnings 0 | Exact specified or linked model retained; see canonical notes for measured fit and finish limits. |
| 8816514970877828 | H 7270 BM | DOWNLOADED | `miele_h7270bm/miele_h7270bm_R2025.rfa` | H 7270 BM: Native PASS; fit HOLD; material 0/0; warnings 0 | Exact specified or linked model retained; see canonical notes for measured fit and finish limits. |
| 6670395252473732 | KM 3054-1 G | BUILT_WITH_LIMITATIONS | `miele_km3054_1g/miele_km3054_1g_R2025.rfa` | KM 3054-1 G: Native PASS; fit PASS body only; material 3/3; warnings 0 | The supplied correction KM 3054-1 G governs the older KM2355G row wording. |
| 2166795625103236 | KFMC 3858 FD | DOWNLOADED | `miele_kfmc3858fd/miele_kfmc3858fd_R2025.rfa` | KFMC 3858 FD: Native PASS; fit HOLD; material 0/0; warnings 0 | Exact specified or linked model retained; see canonical notes for measured fit and finish limits. |
| 7796295159316356 | I32363RC | BUILT_WITH_LIMITATIONS | `tradewind_i32363rc/tradewind_i32363rc_R2025.rfa` | I32363RC: Native PASS; fit PASS body only; material 3/3; warnings 0 | The explicit Trade-Wind I32363RC model governs the conflicting Zephyr vendor/description text. |
| 8923394272198532 | GFW550SSNWW | BUILT_WITH_LIMITATIONS | `ge_gfw550ssnww/ge_gfw550ssnww_R2025.rfa` | GFW550SSNWW: Native PASS; fit PASS; material 5/5; warnings 0 | Exact specified or linked model retained; see canonical notes for measured fit and finish limits. |
| 5407997394747268 | GFD55GSSNWW | BUILT_WITH_LIMITATIONS | `ge_gfd55gssnww/ge_gfd55gssnww_R2025.rfa` | GFD55GSSNWW: Native PASS; fit PASS; material 5/5; warnings 0 | The supplied correction GFD55GSSNWW gas dryer governs the obsolete electric-model wording. |
| 4443914724376452 | WM4000HBA / DLGX4001B | BUILT_WITH_LIMITATIONS | `lg_wm4000hba/lg_wm4000hba_R2025.rfa`<br>`lg_dlgx4001b/lg_dlgx4001b_R2025.rfa` | WM4000HBA: Native PASS; fit PASS; material 5/5; warnings 0; DLGX4001B: Native PASS; fit PASS; material 5/5; warnings 0 | One row is a washer/dryer pair. The stated WM4000HBA model controls the conflicting 5.0-cu-ft wording; no alternate washer was substituted. |
| 904397767376772 | G 5051 SCVi ADA | DOWNLOADED | `miele_g5051scvi/miele_g5051scvi_R2025.rfa` | G 5051 SCVi ADA: Native PASS; fit HOLD; material 0/0; warnings 0 | Exact specified or linked model retained; see canonical notes for measured fit and finish limits. |
| 4666245805309828 | KWTUS 7172 F | DOWNLOADED | `miele_kwtus7172f/miele_kwtus7172f_R2025.rfa` | KWTUS 7172 F: Native PASS; fit HOLD; material 0/0; warnings 0 | Exact specified or linked model retained; see canonical notes for measured fit and finish limits. |
| 3025963735121796 | H 7280 BP | DOWNLOADED | `miele_h7280bp/miele_h7280bp_R2025.rfa` | H 7280 BP: Native PASS; fit HOLD; material 0/0; warnings 0 | Exact specified or linked model retained; see canonical notes for measured fit and finish limits. |
| 6403663455649668 | H 7270 BM | DOWNLOADED | `miele_h7270bm/miele_h7270bm_R2025.rfa` | H 7270 BM: Native PASS; fit HOLD; material 0/0; warnings 0 | Exact specified or linked model retained; see canonical notes for measured fit and finish limits. |
| 7831772394487684 | KM 3054-1 G | BUILT_WITH_LIMITATIONS | `miele_km3054_1g/miele_km3054_1g_R2025.rfa` | KM 3054-1 G: Native PASS; fit PASS body only; material 3/3; warnings 0 | The supplied correction KM 3054-1 G governs the older KM2355G row wording. |
| 1900063828279172 | KFMC 3858 FD | DOWNLOADED | `miele_kfmc3858fd/miele_kfmc3858fd_R2025.rfa` | KFMC 3858 FD: Native PASS; fit HOLD; material 0/0; warnings 0 | Exact specified or linked model retained; see canonical notes for measured fit and finish limits. |
| 162646177939332 | I32363RC | BUILT_WITH_LIMITATIONS | `tradewind_i32363rc/tradewind_i32363rc_R2025.rfa` | I32363RC: Native PASS; fit PASS body only; material 3/3; warnings 0 | The explicit Trade-Wind I32363RC model governs the conflicting Zephyr vendor/description text. |
| 6521680267116420 | SDHWC98PNR | BUILT_WITH_LIMITATIONS | `summit_sdhwc98pnr/summit_sdhwc98pnr_R2025.rfa` | SDHWC98PNR: Native PASS; fit PASS; material 5/5; warnings 0 | Exact specified or linked model retained; see canonical notes for measured fit and finish limits. |
| 2705397813673860 | T18IW905SP | DOWNLOADED | `thermador_t18iw905sp/thermador_t18iw905sp_R2025.rfa` | T18IW905SP: Native PASS; fit HOLD; material 4/5; warnings 0 | ASSUMPTION: abbreviated T18IW905S link resolves to the official panel-ready T18IW905SP model. The full suffix is a working selection requiring design confirmation. |
| 6703228487401348 | T24UR905RP | DOWNLOADED | `thermador_t24ur905rp/thermador_t24ur905rp_R2025.rfa` | T24UR905RP: Native PASS; fit HOLD; material 0/2; warnings 0 | ASSUMPTION / IDENTITY HOLD: the exact T24UR905RP product URL governs the working family. It is a 24-inch undercounter refrigerator; the row says 30-inch warming drawer. These are different appliances. |
| 7829128394243972 | T42IT100NP | DOWNLOADED | `thermador_t42it100np/thermador_t42it100np_R2025.rfa` | T42IT100NP: Native PASS; fit HOLD; material 0/2; warnings 0 | Exact specified or linked model retained; see canonical notes for measured fit and finish limits. |
| 2018080639745924 | MC30WP | DOWNLOADED | `thermador_mc30wp/thermador_mc30wp_R2025.rfa` | MC30WP: Native PASS; fit HOLD; material 6/6; warnings 0 | ASSUMPTION: MC30WP is the manufacturer Professional-series 30-inch 1.6-cu-ft speed oven matching the description. The row has no exact SKU or URL. |
| 2199628860030852 | PODMC301W | DOWNLOADED | `thermador_podmc301w/thermador_podmc301w_R2025.rfa` | PODMC301W: Native PASS; fit HOLD; material 4/4; warnings 1 | Exact specified or linked model retained; see canonical notes for measured fit and finish limits. |
| 7647580173959044 | PRD48WISGU | DOWNLOADED | `thermador_prd48wisgu/thermador_prd48wisgu_R2025.rfa` | PRD48WISGU: Native PASS; fit HOLD; material 6/6; warnings 0 | ASSUMPTION / IDENTITY HOLD: exact URL model PRD48WISGU governs the working family. It is a 48-inch range with steam and induction; the row describes a 30-inch double/triple oven. |
| 8955028301086596 | PCG486WD | DOWNLOADED | `thermador_pcg486wd/thermador_pcg486wd_R2025.rfa` | PCG486WD: Native PASS; fit HOLD; material 3/3; warnings 0 | Exact specified or linked model retained; see canonical notes for measured fit and finish limits. |
| 4451428673716100 | WD30W | DOWNLOADED | `thermador_wd30w/thermador_wd30w_R2025.rfa` | WD30W: Native PASS; fit HOLD; material 2/2; warnings 0 | ASSUMPTION / IDENTITY HOLD: exact URL and manufacturer indicate Thermador WD30W warming drawer; the row description instead identifies a Zephyr 47-inch hood. The family is explicitly WD30W, not a hood. |

## Measured canonical geometry
All dimensions below are millimetres, W x D x H. Values are actual placed geometry, not parameter labels.

| Model | Measured full bounds | Comparison target | Scope / result |
|---|---|---|---|
| H 7280 BP | 757.000 x 671.000 x 727.000 mm | 757.000 x 626.000 x 727.000 mm | full native geometry versus published appliance envelope / HOLD |
| H 7270 BM | 757.000 x 619.000 x 479.000 mm | 757.000 x 573.000 x 479.000 mm | full native geometry versus published appliance envelope / HOLD |
| G 5051 SCVi ADA | 598.000 x 551.000 x 805.000 mm | 598.000 x 550.000 x 815.000 mm | full native geometry versus published appliance envelope / HOLD |
| KWT 6722 iS | 558.500 x 560.000 x 1770.000 mm | 557.000 x 553.000 x 1770.000 mm | full native geometry versus published appliance envelope / HOLD |
| KWTUS 7172 F | 597.000 x 588.200 x 859.000 mm | 597.000 x 563.000 x 859.000 mm | full native geometry versus published appliance envelope / HOLD |
| KFMC 3858 FD | 1067.000 x 610.636 x 2124.551 mm | 1048.000 x 608.000 x 2125.000 mm | full native geometry versus published appliance envelope / HOLD |
| T18IW905SP | 451.000 x 643.510 x 2134.000 mm | 450.850 x 609.600 x 2127.250 mm | full native geometry versus published appliance envelope / HOLD |
| T42IT100NP | 1110.430 x 684.136 x 2145.254 mm | 1048.000 x 608.000 x 2123.000 mm | full native geometry versus published appliance envelope / HOLD |
| T24UR905RP | 607.637 x 668.439 x 871.466 mm | 606.425 x 600.075 x 873.125 mm | full native geometry versus published appliance envelope / HOLD |
| MC30WP | 755.650 x 549.383 x 498.475 mm | 755.650 x 568.325 x 498.475 mm | full native geometry versus published appliance envelope / HOLD |
| PODMC301W | 755.650 x 684.314 x 1244.600 mm | 755.650 x 622.300 x 1244.600 mm | full native geometry versus published appliance envelope / HOLD |
| PCG486WD | 1219.250 x 685.875 x 223.535 mm | 1217.612 x 655.638 x 206.375 mm | full native geometry versus published appliance envelope / HOLD |
| PRD48WISGU | 1217.613 x 777.955 x 1035.050 mm | 1217.612 x 708.025 x 908.050 mm | full native geometry versus published appliance envelope / HOLD |
| WD30W | 755.650 x 681.287 x 239.712 mm | 755.650 x 622.300 x 239.713 mm | full native geometry versus published appliance envelope / HOLD |
| WM4000HBA | 685.800 x 768.350 x 990.600 mm | 685.800 x 768.350 x 990.600 mm | overall / PASS |
| DLGX4001B | 685.800 x 765.175 x 990.600 mm | 685.800 x 765.175 x 990.600 mm | overall / PASS |
| GFW550SSNWW | 711.200 x 812.800 x 1009.650 mm | 711.200 x 812.800 x 1009.650 mm | overall / PASS |
| GFD55GSSNWW | 711.200 x 812.800 x 1009.650 mm | 711.200 x 812.800 x 1009.650 mm | overall / PASS |
| KM 3054-1 G | 942.000 x 526.000 x 88.000 mm | 942.000 x 526.000 x 53.000 mm | body / PASS |
| I32363RC | 873.125 x 266.700 x 355.600 mm | 873.125 x 266.700 x 330.200 mm | body / PASS |
| SDHWC98PNR | 596.900 x 457.200 x 1822.450 mm | 596.900 x 457.200 x 1822.450 mm | overall / PASS |

## Evidence and use
`section_manifest.json` maps all rows to canonical RFAs, SHA-256 hashes, notes and evidence. Every canonical folder contains `NOTES.md`, `validation.json`, `source_manifest.json`, sources and native views. Each inventory item-key folder has its own row-level `NOTES.md`.
Custom build entry points are under each model `source/` directory. Manufacturer originals remain under `source/original/`. GE CAD trial RFAs are research evidence under `source/` and are not the delivered working families. Historical initial audit files are superseded by each canonical `validation.json`.
Keep the companion material PNG files with the custom families when copying the package. Uniform finish maps are project visualization approximations. Imported/nested manufacturer textures and exact optical equivalence are not universally validated.
The coordinator owns delivery, design identity resolution and acceptance of the listed visual/dimensional limits. No fabrication, installation-clearance or procurement acceptance is implied.
