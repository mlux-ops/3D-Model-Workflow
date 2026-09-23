# Cassia SF549315AGOP — measured, derived and inferred geometry

Units: inches. Drawing scale 22.03 px/in (7-5/8" line 168 px; Ø6" globe fits r = 2.990–2.994 in).
Station `a` = distance from a globe centre along its arm axis toward the hub.
Constants live in `source/cassia_geometry.py`; this table explains them.

| Feature | Model value | Class | Evidence | Conflict / uncertainty |
|---|---|---|---|---|
| Overall diameter | 17.75 | PUBLISHED | spec sheet D17-3/4 | drawing envelope Ø17.86 at globe scale, Ø17.72 at dimension-line scale |
| Overall height (ceiling → globe bottom) | 7.625 | PUBLISHED | spec sheet H7-5/8 | — |
| Canopy | Ø4.75 × 0.875 | PUBLISHED | spec sheet | plan circle fits Ø4.78 |
| Globe | Ø6.0 opal sphere | PUBLISHED | spec sheet | five circle fits 5.98–5.99 |
| Globe centre radius | 5.875 | DERIVED | 17.75/2 − 3 | drawing places centres at 5.94–5.95; printed values govern (≈1.5 px in the overlay) |
| Globe centre depth | 4.625 | DERIVED | 7.625 − 3 | drawing 4.61 |
| Arm azimuths | 0 / 120 / 240° | DRAWING | plan centres 119.7–120.3° apart | — |
| Arm slope | 30.0° below horizontal | DRAWING | elevation edges 29.9° / 30.1–30.8°; axis through globe centre within 1 px | — |
| Arm axis at hub axis | z = 1.233 | DERIVED | from 30° and centres | drawing 1.15 (0.08 in) |
| Arm | Ø0.50 | DRAWING + RENDER | drawing line centres 0.556 elev / 0.567 plan; renders 0.45–0.49 vs canopy | value chosen between the two sources |
| Hub | Ø1.16 × 1.18 | DRAWING + RENDER | drawing 1.18 elev / 1.235 plan wide, 1.18 tall; renders 1.12–1.16 wide | ± 0.05 |
| Fitter flange | Ø2.16 × 0.11, a 2.81–2.92 | DRAWING + RENDER | drawing Ø2.06, inner face a 2.82; renders Ø2.12–2.24 | sized to cover the glass opening, margin 0.024 |
| Fitter raised disk | Ø1.86 × 0.12, a 2.92–3.04 | RENDER + DRAWING | render step ring ≈ 0.87 × flange; drawing outer face a 3.05 | — |
| Arm collar | Ø0.62 × 0.40, a 3.04–3.44 | RENDER | collar/arm 1.17–1.24 in the ceiling render | length INFERRED (foreshortened in both renders) |
| Glass opening plane | a = 2.81 | DRAWING | fitter inner face a 2.82 | neck/thread hidden, not modelled |
| Glass wall | 0.10 | INFERRED | — | — |
| Socket sleeve | Ø0.74 × 1.50, a 1.45–2.95 | INFERRED | clear-glass SKU render (AGCL) | hidden behind opal |
| Candle lamp (E12) | max Ø0.97, a −1.05 → 1.50 | INFERRED | AGCL render, spec E12 40 W | hidden behind opal; no light source |
| Canopy screws | 2 domed heads Ø0.22 × 0.07 at 90° / 270°, 0.36 below ceiling | DRAWING + RENDER | elevation shows one head facing the viewer; render (viewed opposite a globe) shows one 30° left of centre — both fit a diametric pair 30° off the arms | pair and dome INFERRED |
| Edge rounds | canopy 0.04, hub 0.03 | INFERRED | renders show crisp, softened edges | — |
| Aged Gold | RGB 146/107/60, gloss 0.45, refl 0.30/0.80, metal flag on | RENDER-sampled | p60 of gold pixels (median 135/99/54, p90 232/185/119) | optical values inferred; brushing not modelled (texture-free) |
| Opal Matte Glass | RGB 244/240/234, gloss 0.30, opaque, unlit | RENDER-sampled | p10 of lit globe pixels 242/236/231 | both renders show unlit globes |
| Lamp | RGB 250/248/240, 35 % transparent | INFERRED | — | only visible if Glass Finish is swapped to clear |
| Not modelled | crossbar, mounting plate, wiring, threads, glass neck | — | hidden when installed | — |

Measured-gate targets and tolerances (±0.01 in, ±0.25°, hosted ±0.02 in) are defined in `measurement_rays()` and applied identically by the native builder, the offline dry-run and the verifier.
