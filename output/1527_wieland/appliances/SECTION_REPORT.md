# 1527 Wieland - Appliances section report

## Result - orchestrator rework round 1

**All nine assigned dimensional failures have custom Revit 2025 working replacements. All 13 affected inventory rows are reconciled to those new files.**
Recorded 2026-10-03T00:01:40.135847+00:00. The section still contains all 27 inventory rows and 21 selected canonical families. Row status counts: 22 BUILT_WITH_LIMITATIONS and five DOWNLOADED.

The nine new families pass native save/reopen, model identity, Specialty Equipment category, complete overall dimensions within 1 mm, floor-face placement, material substitution/restoration, bitmap resolution and fresh preview generation. The largest measured overall-axis deviation is 0.000065613 mm. There are zero family and placed-project warnings.
The nine models provide 41 editable finish parameters: 41/41 substitutions passed in reopened families and another 41/41 passed in placed instances. All 27 native front/side/oblique previews were directly inspected.

**Delivery remains with the orchestrator.** No Drive upload or Smartsheet edit was performed. The five named selection/ambiguity holds remain NEEDS_USER and their files and row records are unchanged.

## Changes and preserved evidence

Replacement filenames end in `_Custom_R1_R2025.rfa`. They contain newly constructed native solids, not transformed manufacturer family instances or rescaled imported CAD. Each model has current validation, canonical NOTES, source_manifest and new source/rework_r1 evidence. All affected row NOTES point to the selected replacement.
All 515 protected pre-existing files are hash-checked, including manufacturer originals, prior working RFAs, prior previews and all non-target model/row files. Forty-four prior mutable notes/report/validation files are archived under `rework_round1/history_before/`. The previous failed working families remain available for audit and are no longer selected for the 13 corrected rows.

## Round-1 dimensional results

Measurements below are the complete default modeled W x D x H on the authoritative axes; no body-only subset was used for these nine results.

| Model | Complete measured W x D x H (mm) | Largest axis deviation (mm) | Native gates | Selected RFA |
|---|---|---:|---|---|
| H 7280 BP | 757.000 x 626.000 x 727.000 | 0.000028801 | PASS | `miele_h7280bp/miele_h7280bp_Custom_R1_R2025.rfa` |
| H 7270 BM | 757.000 x 573.000 x 479.000 | 0.000017452 | PASS | `miele_h7270bm/miele_h7270bm_Custom_R1_R2025.rfa` |
| G 5051 SCVi ADA | 598.000 x 550.000 x 815.000 | 0.000035286 | PASS | `miele_g5051scvi/miele_g5051scvi_Custom_R1_R2025.rfa` |
| KWT 6722 iS | 557.000 x 553.000 x 1770.000 | 0.000044632 | PASS | `miele_kwt6722is/miele_kwt6722is_Custom_R1_R2025.rfa` |
| KWTUS 7172 F | 597.000 x 563.000 x 859.000 | 0.000034142 | PASS | `miele_kwtus7172f/miele_kwtus7172f_Custom_R1_R2025.rfa` |
| KFMC 3858 FD | 1048.000 x 608.000 x 2125.000 | 0.000056458 | PASS | `miele_kfmc3858fd/miele_kfmc3858fd_Custom_R1_R2025.rfa` |
| T42IT100NP | 1048.000 x 608.000 x 2123.000 | 0.000065613 | PASS | `thermador_t42it100np/thermador_t42it100np_Custom_R1_R2025.rfa` |
| PODMC301W | 755.650 x 622.300 x 1244.600 | 0.000048447 | PASS | `thermador_podmc301w/thermador_podmc301w_Custom_R1_R2025.rfa` |
| PCG486WD | 1217.613 x 655.638 x 206.375 | 0.000024223 | PASS | `thermador_pcg486wd/thermador_pcg486wd_Custom_R1_R2025.rfa` |

## Assumptions retained with the replacements

The published appliance W/D/H values govern this requested coordination envelope. For the three wall-oven models, the modeled handles are included inside that complete envelope; the concealed body-depth partition is reconstructed and is not certified to the separate cabinet-installation section. These replacements do not certify cutouts or fabrication dimensions. This convention is stated in each affected canonical note.
Factory appliances use closed doors and the stated minimum foot setting where applicable. Separately supplied customer overlay panels, handles and optional accessory frame/backguard kits are not included. Local controls, concealed mechanisms, small radii and optical properties remain reference-derived approximations. Overall dimensions and editable-material operation are verified independently of those assumptions.
The T42 replacement uses the retained page-4 explicit metric dimensions and 2123 mm minimum height. Miele H7280BP dimensions were additionally confirmed on its exact-model official product page because the retained two-page fact sheet omits the overall-dimension row.

## Complete row register

Paths are relative to `output/1527_wieland/appliances/`. Status describes provenance/construction, and the gate column records the applicable technical outcome.

| Row ID | Item / selected model | Status | RFA path | Gate results | Note |
|---|---|---|---|---|---|
| 3292695531945860 | WM4000HBA / DLGX4001B | BUILT_WITH_LIMITATIONS | `lg_wm4000hba/lg_wm4000hba_R2025.rfa`<br>`lg_dlgx4001b/lg_dlgx4001b_R2025.rfa` | WM4000HBA: open/save/reopen/category/place/preview PASS; fit PASS (overall); material 5/5; warnings 0<br>DLGX4001B: open/save/reopen/category/place/preview PASS; fit PASS (overall); material 5/5; warnings 0 | One row is a washer/dryer pair: both separate native families are provided. Black Steel follows the B model suffix. |
| 7384660666023812 | KWT 6722 iS | BUILT_WITH_LIMITATIONS | `miele_kwt6722is/miele_kwt6722is_Custom_R1_R2025.rfa` | KWT 6722 iS: open/save/reopen/category/place/preview PASS; fit PASS (complete overall); material 6/6 family and 6/6 placed; warnings 0 | Round-1 custom replacement: complete overall dimensions and all native gates pass. Prior source/working RFAs retained; local geometry and finish assumptions remain documented. |
| 3328172767117188 | G 5051 SCVi ADA | BUILT_WITH_LIMITATIONS | `miele_g5051scvi/miele_g5051scvi_Custom_R1_R2025.rfa` | G 5051 SCVi ADA: open/save/reopen/category/place/preview PASS; fit PASS (complete overall); material 4/4 family and 4/4 placed; warnings 0 | Round-1 custom replacement: complete overall dimensions and all native gates pass. Prior source/working RFAs retained; local geometry and finish assumptions remain documented. |
| 4418595438788484 | H 7280 BP | BUILT_WITH_LIMITATIONS | `miele_h7280bp/miele_h7280bp_Custom_R1_R2025.rfa` | H 7280 BP: open/save/reopen/category/place/preview PASS; fit PASS (complete overall); material 5/5 family and 5/5 placed; warnings 0 | Round-1 custom replacement: complete overall dimensions and all native gates pass. Prior source/working RFAs retained; local geometry and finish assumptions remain documented. |
| 8816514970877828 | H 7270 BM | BUILT_WITH_LIMITATIONS | `miele_h7270bm/miele_h7270bm_Custom_R1_R2025.rfa` | H 7270 BM: open/save/reopen/category/place/preview PASS; fit PASS (complete overall); material 5/5 family and 5/5 placed; warnings 0 | Round-1 custom replacement: complete overall dimensions and all native gates pass. Prior source/working RFAs retained; local geometry and finish assumptions remain documented. |
| 6670395252473732 | KM 3054-1 G | BUILT_WITH_LIMITATIONS | `miele_km3054_1g/miele_km3054_1g_R2025.rfa` | KM 3054-1 G: open/save/reopen/category/place/preview PASS; fit PASS (body); material 3/3; warnings 0 | The supplied correction KM 3054-1 G governs the older KM2355G row wording. |
| 2166795625103236 | KFMC 3858 FD | BUILT_WITH_LIMITATIONS | `miele_kfmc3858fd/miele_kfmc3858fd_Custom_R1_R2025.rfa` | KFMC 3858 FD: open/save/reopen/category/place/preview PASS; fit PASS (complete overall); material 3/3 family and 3/3 placed; warnings 0 | Round-1 custom replacement: complete overall dimensions and all native gates pass. Prior source/working RFAs retained; local geometry and finish assumptions remain documented. |
| 7796295159316356 | I32363RC | BUILT_WITH_LIMITATIONS | `tradewind_i32363rc/tradewind_i32363rc_R2025.rfa` | I32363RC: open/save/reopen/category/place/preview PASS; fit PASS (body); material 3/3; warnings 0 | The explicit Trade-Wind I32363RC model governs the conflicting Zephyr vendor/description text. |
| 8923394272198532 | GFW550SSNWW | BUILT_WITH_LIMITATIONS | `ge_gfw550ssnww/ge_gfw550ssnww_R2025.rfa` | GFW550SSNWW: open/save/reopen/category/place/preview PASS; fit PASS (overall); material 5/5; warnings 0 | Exact specified or linked model retained; see canonical notes for measured fit and finish limits. |
| 5407997394747268 | GFD55GSSNWW | BUILT_WITH_LIMITATIONS | `ge_gfd55gssnww/ge_gfd55gssnww_R2025.rfa` | GFD55GSSNWW: open/save/reopen/category/place/preview PASS; fit PASS (overall); material 5/5; warnings 0 | The supplied correction GFD55GSSNWW gas dryer governs the obsolete electric-model wording. |
| 4443914724376452 | WM4000HBA / DLGX4001B | BUILT_WITH_LIMITATIONS | `lg_wm4000hba/lg_wm4000hba_R2025.rfa`<br>`lg_dlgx4001b/lg_dlgx4001b_R2025.rfa` | WM4000HBA: open/save/reopen/category/place/preview PASS; fit PASS (overall); material 5/5; warnings 0<br>DLGX4001B: open/save/reopen/category/place/preview PASS; fit PASS (overall); material 5/5; warnings 0 | One row is a washer/dryer pair. The stated WM4000HBA model controls the conflicting 5.0-cu-ft wording; no alternate washer was substituted. |
| 904397767376772 | G 5051 SCVi ADA | BUILT_WITH_LIMITATIONS | `miele_g5051scvi/miele_g5051scvi_Custom_R1_R2025.rfa` | G 5051 SCVi ADA: open/save/reopen/category/place/preview PASS; fit PASS (complete overall); material 4/4 family and 4/4 placed; warnings 0 | Round-1 custom replacement: complete overall dimensions and all native gates pass. Prior source/working RFAs retained; local geometry and finish assumptions remain documented. |
| 4666245805309828 | KWTUS 7172 F | BUILT_WITH_LIMITATIONS | `miele_kwtus7172f/miele_kwtus7172f_Custom_R1_R2025.rfa` | KWTUS 7172 F: open/save/reopen/category/place/preview PASS; fit PASS (complete overall); material 6/6 family and 6/6 placed; warnings 0 | Round-1 custom replacement: complete overall dimensions and all native gates pass. Prior source/working RFAs retained; local geometry and finish assumptions remain documented. |
| 3025963735121796 | H 7280 BP | BUILT_WITH_LIMITATIONS | `miele_h7280bp/miele_h7280bp_Custom_R1_R2025.rfa` | H 7280 BP: open/save/reopen/category/place/preview PASS; fit PASS (complete overall); material 5/5 family and 5/5 placed; warnings 0 | Round-1 custom replacement: complete overall dimensions and all native gates pass. Prior source/working RFAs retained; local geometry and finish assumptions remain documented. |
| 6403663455649668 | H 7270 BM | BUILT_WITH_LIMITATIONS | `miele_h7270bm/miele_h7270bm_Custom_R1_R2025.rfa` | H 7270 BM: open/save/reopen/category/place/preview PASS; fit PASS (complete overall); material 5/5 family and 5/5 placed; warnings 0 | Round-1 custom replacement: complete overall dimensions and all native gates pass. Prior source/working RFAs retained; local geometry and finish assumptions remain documented. |
| 7831772394487684 | KM 3054-1 G | BUILT_WITH_LIMITATIONS | `miele_km3054_1g/miele_km3054_1g_R2025.rfa` | KM 3054-1 G: open/save/reopen/category/place/preview PASS; fit PASS (body); material 3/3; warnings 0 | The supplied correction KM 3054-1 G governs the older KM2355G row wording. |
| 1900063828279172 | KFMC 3858 FD | BUILT_WITH_LIMITATIONS | `miele_kfmc3858fd/miele_kfmc3858fd_Custom_R1_R2025.rfa` | KFMC 3858 FD: open/save/reopen/category/place/preview PASS; fit PASS (complete overall); material 3/3 family and 3/3 placed; warnings 0 | Round-1 custom replacement: complete overall dimensions and all native gates pass. Prior source/working RFAs retained; local geometry and finish assumptions remain documented. |
| 162646177939332 | I32363RC | BUILT_WITH_LIMITATIONS | `tradewind_i32363rc/tradewind_i32363rc_R2025.rfa` | I32363RC: open/save/reopen/category/place/preview PASS; fit PASS (body); material 3/3; warnings 0 | The explicit Trade-Wind I32363RC model governs the conflicting Zephyr vendor/description text. |
| 6521680267116420 | SDHWC98PNR | BUILT_WITH_LIMITATIONS | `summit_sdhwc98pnr/summit_sdhwc98pnr_R2025.rfa` | SDHWC98PNR: open/save/reopen/category/place/preview PASS; fit PASS (overall); material 5/5; warnings 0 | Exact specified or linked model retained; see canonical notes for measured fit and finish limits. |
| 2705397813673860 | T18IW905SP | DOWNLOADED | `thermador_t18iw905sp/thermador_t18iw905sp_R2025.rfa` | T18IW905SP: open/save/reopen/category/place/preview PASS; fit HOLD (full native geometry versus published appliance envelope); material 4/5; warnings 0 | ASSUMPTION: abbreviated T18IW905S link resolves to the official panel-ready T18IW905SP model. The full suffix is a working selection requiring design confirmation. |
| 6703228487401348 | T24UR905RP | DOWNLOADED | `thermador_t24ur905rp/thermador_t24ur905rp_R2025.rfa` | T24UR905RP: open/save/reopen/category/place/preview PASS; fit HOLD (full native geometry versus published appliance envelope); material 0/2; warnings 0 | ASSUMPTION / IDENTITY HOLD: the exact T24UR905RP product URL governs the working family. It is a 24-inch undercounter refrigerator; the row says 30-inch warming drawer. These are different appliances. |
| 7829128394243972 | T42IT100NP | BUILT_WITH_LIMITATIONS | `thermador_t42it100np/thermador_t42it100np_Custom_R1_R2025.rfa` | T42IT100NP: open/save/reopen/category/place/preview PASS; fit PASS (complete overall); material 3/3 family and 3/3 placed; warnings 0 | Round-1 custom replacement: complete overall dimensions and all native gates pass. Prior source/working RFAs retained; local geometry and finish assumptions remain documented. |
| 2018080639745924 | MC30WP | DOWNLOADED | `thermador_mc30wp/thermador_mc30wp_R2025.rfa` | MC30WP: open/save/reopen/category/place/preview PASS; fit HOLD (full native geometry versus published appliance envelope); material 6/6; warnings 0 | ASSUMPTION: MC30WP is the manufacturer Professional-series 30-inch 1.6-cu-ft speed oven matching the description. The row has no exact SKU or URL. |
| 2199628860030852 | PODMC301W | BUILT_WITH_LIMITATIONS | `thermador_podmc301w/thermador_podmc301w_Custom_R1_R2025.rfa` | PODMC301W: open/save/reopen/category/place/preview PASS; fit PASS (complete overall); material 5/5 family and 5/5 placed; warnings 0 | Round-1 custom replacement: complete overall dimensions and all native gates pass. Prior source/working RFAs retained; local geometry and finish assumptions remain documented. |
| 7647580173959044 | PRD48WISGU | DOWNLOADED | `thermador_prd48wisgu/thermador_prd48wisgu_R2025.rfa` | PRD48WISGU: open/save/reopen/category/place/preview PASS; fit HOLD (full native geometry versus published appliance envelope); material 6/6; warnings 0 | ASSUMPTION / IDENTITY HOLD: exact URL model PRD48WISGU governs the working family. It is a 48-inch range with steam and induction; the row describes a 30-inch double/triple oven. |
| 8955028301086596 | PCG486WD | BUILT_WITH_LIMITATIONS | `thermador_pcg486wd/thermador_pcg486wd_Custom_R1_R2025.rfa` | PCG486WD: open/save/reopen/category/place/preview PASS; fit PASS (complete overall); material 4/4 family and 4/4 placed; warnings 0 | Round-1 custom replacement: complete overall dimensions and all native gates pass. Prior source/working RFAs retained; local geometry and finish assumptions remain documented. |
| 4451428673716100 | WD30W | DOWNLOADED | `thermador_wd30w/thermador_wd30w_R2025.rfa` | WD30W: open/save/reopen/category/place/preview PASS; fit HOLD (full native geometry versus published appliance envelope); material 2/2; warnings 0 | ASSUMPTION / IDENTITY HOLD: exact URL and manufacturer indicate Thermador WD30W warming drawer; the row description instead identifies a Zephyr 47-inch hood. The family is explicitly WD30W, not a hood. |

## Unchanged decisions and other scope

T18IW905SP, T24UR905RP, MC30WP, PRD48WISGU and WD30W remain orchestrator NEEDS_USER. Round 1 did not alter their families, source evidence, validation, canonical notes, row notes or selected model records.
The seven earlier custom models are unchanged. Five retain full-envelope passes; KM3054-1G and I32363RC retain their explicitly limited body-only dimensional passes. No round-1 claim promotes those two results to complete overall passes.

## Validation records

`section_manifest.json` identifies all selected files. `artifact_audit.json` records current completeness and hash verification. `rework_round1/completion_receipt.json` and `rework_round1/round1_audit.json` record the nine-model rework result and preservation checks. `visual_review.json` records actual reviewed-image hashes and observations. Native source records remain under each target/source/rework_r1; current reviewed records are each target/validation.json.

## Blockers

No technical blocker remains in the assigned nine-model rework scope. The five unchanged user-decision holds and final orchestrator delivery decision remain outside this worker assignment.
