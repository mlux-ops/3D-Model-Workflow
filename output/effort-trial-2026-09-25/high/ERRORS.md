# Errors log — high arm, 2026-09-25

| # | Action | Observed error | Cause | Fix | Status |
|---|---|---|---|---|---|
| 1 | Library check `import cv2` | `ModuleNotFoundError: No module named 'cv2'` | OpenCV not installed in this Python | Implemented homography/rectification with numpy + `scipy.ndimage.map_coordinates` | Resolved |
| 2 | Library check `import skimage` | `ModuleNotFoundError: No module named 'skimage'` | scikit-image not installed | Not needed; min-cut and matching written in numpy/scipy | Resolved |
| 3 | First automatic joint detection (row minima of high-pass image) | Noisy, inconsistent joint positions (stone cracks as dark as joints) | Per-row local minima cannot separate joints from dark mottle | Replaced with a line search maximizing darkness along whole straight lines; spacing then consistent to ±1.5 px per row | Resolved |
| 4 | First isotropy estimate of forward scale (rectified at 4 px/in, no prefilter) | Across-direction autocorrelation collapsed (lag-1 ≈ 0.2) → misleading anisotropy | Aliasing: sampling below the across resolution without low-pass | Rectified at 16 px/in, Gaussian prefilter, then spectral-moment isotropy; results consistent across 3 tiles | Resolved |
| 5 | Writing `build_atlas.py` through a Bash heredoc | `bash: -c: line 150: unexpected EOF while looking for matching ''` | Shell quoting of the long heredoc command failed in Git Bash (exact trigger not identified) | Wrote the file with the Write tool instead | Resolved |
| 6 | Swatch inspection (bad source content, not a tool error) | Periodic horizontal scan lines, period 3.77 px, row-mean amplitude 2.14 | Artifact in the supplied swatch image | Narrow vertical-frequency notch filter; residual 0.39 | Resolved (documented as a modification in README) |
| 7 | Rectified floor at 64 px/in (quality check) | Visible smearing/stretching at 1:1 | Native resolution only 5.6–10.3 px/in forward, 16–22 across | Floor pixels excluded from the atlas; floor used for validation only | Resolved by design choice; limitation in README |
| 8 | First atlas review (repeat check) | 24/54 random 5 in blocks had an exact (>0.9 NCC) match in another cell; bright flake reused ~13× | Single small swatch; distinctiveness penalty too weak | Added rare-flake reuse weight (W_RARE = 6): 15/54 >0.9, max cell NCC 0.125 | Partially resolved — inherent source limit, documented |
| 9 | `validate_floor.py` run | `RuntimeWarning: Mean of empty slice` | One 4-in band lies outside the rectified coverage for some columns (all-NaN) | Harmless; band skipped by the NaN check. Left as is | Known warning |

No PNG save `OSError` (errno 22) occurred in any run (0 retries recorded); the save routine retries up to 3 times.
