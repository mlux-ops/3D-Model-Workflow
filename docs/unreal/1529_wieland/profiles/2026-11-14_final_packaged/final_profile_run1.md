# Final profile, packaged build (run1)

Record: `Profile(20261114_065737).csv`, 60000 frames, passes started 4, complete passes [1, 2, 3]; the profile is pass 2.

## Pass 1

| Path or hold | Frames | Mean (ms) | 95th percentile (ms) | Worst (ms) | Over 16.67 ms | Over 33.3 ms | Graphics card mean (ms) | Game thread mean (ms) | Render thread mean (ms) | Video memory peak, engine (MB) |
|---|---|---|---|---|---|---|---|---|---|---|
| settle_exterior | 580 | 18.66 | 14.8 | 2778.0 | 16 | 4 | 11.33 | 1.67 | 15.36 | 5340 |
| exterior_path | 4317 | 13.9 | 15.28 | 25.36 | 8 | 0 | 12.24 | 1.13 | 13.89 | 5383 |
| hold_S1 | 702 | 14.26 | 15.36 | 22.95 | 2 | 0 | 12.67 | 1.05 | 14.26 | 5384 |
| hold_S2 | 729 | 13.71 | 14.84 | 21.17 | 2 | 0 | 12.06 | 1.04 | 13.7 | 5387 |
| hold_S6 | 746 | 13.41 | 14.51 | 21.05 | 2 | 0 | 11.86 | 1.05 | 13.41 | 5387 |
| settle_triplex | 853 | 9.37 | 10.36 | 29.07 | 4 | 0 | 7.86 | 1.06 | 9.34 | 5387 |
| triplex_path | 2482 | 12.09 | 15.4 | 22.15 | 70 | 0 | 10.61 | 1.01 | 12.08 | 5426 |
| hold_D5 | 867 | 11.53 | 12.55 | 18.04 | 1 | 0 | 9.95 | 0.97 | 11.53 | 5426 |
| settle_penthouse | 740 | 10.81 | 12.0 | 25.89 | 1 | 0 | 9.28 | 1.01 | 10.79 | 5426 |
| penthouse_path_indoors | 1507 | 13.27 | 15.78 | 22.16 | 26 | 0 | 11.71 | 0.99 | 13.27 | 5426 |
| hold_D2 | 762 | 13.12 | 14.43 | 21.88 | 1 | 0 | 11.55 | 1.0 | 13.12 | 5429 |
| settle_roofdeck | 617 | 12.97 | 14.22 | 17.28 | 2 | 0 | 11.46 | 1.22 | 12.97 | 5450 |
| roof_deck_path | 759 | 13.17 | 14.73 | 15.98 | 0 | 0 | 11.61 | 1.04 | 13.16 | 5432 |
| ALL_PATHS_AND_HOLDS | 12871 | 13.21 | 15.19 | 25.36 | 112 | 0 | 11.62 | 1.05 | 13.2 | 5432 |

## Pass 2 (the profile)

| Path or hold | Frames | Mean (ms) | 95th percentile (ms) | Worst (ms) | Over 16.67 ms | Over 33.3 ms | Graphics card mean (ms) | Game thread mean (ms) | Render thread mean (ms) | Video memory peak, engine (MB) |
|---|---|---|---|---|---|---|---|---|---|---|
| settle_exterior | 616 | 12.98 | 13.98 | 20.85 | 1 | 0 | 11.41 | 1.02 | 12.97 | 5432 |
| exterior_path | 4300 | 13.96 | 15.19 | 24.2 | 4 | 0 | 12.35 | 1.06 | 13.95 | 5432 |
| hold_S1 | 695 | 14.39 | 15.45 | 23.39 | 2 | 0 | 12.79 | 1.07 | 14.38 | 5436 |
| hold_S2 | 725 | 13.78 | 14.94 | 20.56 | 2 | 0 | 12.13 | 1.08 | 13.78 | 5437 |
| hold_S6 | 750 | 13.33 | 14.47 | 20.44 | 2 | 0 | 11.78 | 1.05 | 13.33 | 5437 |
| settle_triplex | 853 | 9.38 | 10.26 | 25.64 | 3 | 0 | 7.87 | 1.0 | 9.35 | 5437 |
| triplex_path | 2485 | 12.07 | 15.47 | 21.87 | 65 | 0 | 10.57 | 0.98 | 12.07 | 5442 |
| hold_D5 | 857 | 11.67 | 12.88 | 19.99 | 2 | 0 | 10.08 | 0.96 | 11.67 | 5442 |
| settle_penthouse | 738 | 10.84 | 12.03 | 25.75 | 2 | 0 | 9.3 | 1.01 | 10.82 | 5442 |
| penthouse_path_indoors | 1506 | 13.28 | 15.84 | 18.76 | 31 | 0 | 11.73 | 0.98 | 13.27 | 5441 |
| hold_D2 | 756 | 13.24 | 14.46 | 17.24 | 2 | 0 | 11.63 | 0.95 | 13.23 | 5441 |
| settle_roofdeck | 608 | 13.16 | 14.3 | 18.22 | 1 | 0 | 11.63 | 1.21 | 13.16 | 5461 |
| roof_deck_path | 757 | 13.21 | 14.71 | 15.94 | 0 | 0 | 11.66 | 1.04 | 13.2 | 5442 |
| ALL_PATHS_AND_HOLDS | 12831 | 13.25 | 15.19 | 24.2 | 110 | 0 | 11.68 | 1.02 | 13.24 | 5442 |

## Pass 3

| Path or hold | Frames | Mean (ms) | 95th percentile (ms) | Worst (ms) | Over 16.67 ms | Over 33.3 ms | Graphics card mean (ms) | Game thread mean (ms) | Render thread mean (ms) | Video memory peak, engine (MB) |
|---|---|---|---|---|---|---|---|---|---|---|
| settle_exterior | 612 | 13.06 | 14.22 | 22.17 | 1 | 0 | 11.48 | 1.01 | 13.06 | 5442 |
| exterior_path | 4282 | 14.01 | 15.28 | 22.41 | 6 | 0 | 12.4 | 1.05 | 14.01 | 5443 |
| hold_S1 | 699 | 14.3 | 15.36 | 22.42 | 3 | 0 | 12.7 | 1.04 | 14.29 | 5443 |
| hold_S2 | 728 | 13.73 | 14.81 | 22.26 | 1 | 0 | 12.1 | 1.03 | 13.72 | 5443 |
| hold_S6 | 744 | 13.45 | 14.66 | 18.58 | 1 | 0 | 11.87 | 1.03 | 13.44 | 5443 |
| settle_triplex | 860 | 9.3 | 10.24 | 29.23 | 4 | 0 | 7.79 | 1.02 | 9.27 | 5443 |
| triplex_path | 2501 | 11.99 | 15.05 | 20.57 | 53 | 0 | 10.5 | 0.97 | 11.99 | 5447 |
| hold_D5 | 862 | 11.61 | 12.74 | 15.14 | 0 | 0 | 10.0 | 0.94 | 11.6 | 5447 |
| settle_penthouse | 742 | 10.78 | 11.93 | 26.48 | 1 | 0 | 9.28 | 1.01 | 10.77 | 5479 |
| penthouse_path_indoors | 1511 | 13.24 | 15.83 | 23.49 | 38 | 0 | 11.69 | 0.98 | 13.23 | 5446 |
| hold_D2 | 762 | 13.13 | 14.41 | 17.28 | 1 | 0 | 11.53 | 1.0 | 13.12 | 5446 |
| settle_roofdeck | 608 | 13.15 | 14.47 | 21.91 | 4 | 0 | 11.57 | 1.21 | 13.15 | 5466 |
| roof_deck_path | 764 | 13.09 | 14.66 | 21.77 | 1 | 0 | 11.6 | 1.04 | 13.09 | 5447 |
| ALL_PATHS_AND_HOLDS | 12853 | 13.23 | 15.17 | 23.49 | 104 | 0 | 11.66 | 1.01 | 13.22 | 5447 |

Video memory, whole graphics card as Windows reports it (dedicated): peak 11785 MB, 6258.0 MB in use before the program started (the editor on an empty level and the desktop), difference 5527 MB. The engine's own budget for the program: [0, 15280] MB.

Acceptance: {"p95_all_paths_ms": 15.19, "p95_limit_ms": 16.67, "p95_met": true, "worst_path_p95_ms": 15.84, "vram_peak_mb_engine_profile_pass": 5461, "vram_peak_mb_engine_whole_record": 5479, "card_peak_minus_baseline_mb": 5527, "vram_limit_mb": 13312.0, "vram_met": true}
