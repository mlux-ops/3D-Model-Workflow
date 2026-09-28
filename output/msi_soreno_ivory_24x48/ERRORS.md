# Errors and findings — MSI Soreno Ivory 24x48 rebuild (2026-09-26)

Each entry: observed error, cause, fix, status. Mirrored in the root `PROJECT_MEMORY.md` under
"MSI Soreno Ivory 24x48 rebuild — 2026-09-26".

| # | Action | Observed | Cause | Fix / next step | Status |
|---|---|---|---|---|---|
| 1 | WebFetch of Home Depot, FloorBox and Zoro product pages | HTTP 403 Forbidden | Retailer bot protection | Home Depot read through the Browser pane (spec JSON in the page). FloorBox and Zoro not retried; other dealers covered the same facts | Resolved (HD); FloorBox/Zoro not needed |
| 2 | curl of Home Depot and Lowe's | HTTP 403 | Same | Browser pane for Home Depot | Resolved |
| 3 | Read tool on the MSI installation-guide PDF with a `pages` range | "pdftoppm is not installed" | Poppler not on this machine; the `pages` parameter needs it | Read the 2-page PDF without `pages` | Resolved |
| 4 | MSI room-scene images at the full-size CDN path (`/images/roomscenes/<name>.jpg`) | HTTP 404 | MSI only serves `medium` and `thumb` folders for these | Downloaded the `medium` 1200 px versions (rejected for colour anyway) | Resolved |
| 5 | Home Depot NSORIVO2448 / NSORIVO2448PP URLs | Redirect to "MSI Sorena Cream NSORCREAM2448C/P" (same Internet #) listing 48 x 24 in, 9.90 mm, V3 | HD re-labelled the listing; not confirmed to be the same product | Used only as corroboration of metric thickness; not used for size | Finding (data caveat) |
| 6 | Actual (calibrated) size search | Not published by MSI (page, flyer, installation guide, DCOF sheet) or by 11 dealers checked | MSI publishes nominal size only | Metric rectified convention 600 x 1200 mm used and disclosed (see README) | Limitation, disclosed |
| 7 | Bash `sleep 45; tail ...` to wait for the build | Harness blocked the chained sleep | Harness rule: waits must use Monitor / background until-loops | Used Monitor with an until-loop | Resolved |
| 8 | Source faces: NCC duplicate test | Every face in every 24x48, 24x24, paver and flyer swatch is one of only 2 printed faces (A, B), several of them mirrored | MSI builds its swatch renders from two print faces | Built the 18 atlas faces by min-cut quilting from A and B (see README) | Limitation, disclosed |
| 10 | b02_previews.py first run | `ValueError: cannot write empty image` | T-junction crop centred at x = 379 px, so `cx - 400 < 0` gave an empty slice; the same expression was in the e01 preview | Centre on the row-1 joint one module further (x = 1515 px) in both scripts | Resolved; previews regenerated and reviewed |
| 9 | First NCC clustering in a05 (high-pass sigma 4) | Union-find merged partial overlaps into 2 clusters without showing which faces were whole duplicates | Partial-overlap NCC (0.4-0.6) chained clusters | Re-tested each face against the two full representatives A and B in a DoG band; phase-randomised surrogates give 0.03-0.15 baseline | Resolved |
