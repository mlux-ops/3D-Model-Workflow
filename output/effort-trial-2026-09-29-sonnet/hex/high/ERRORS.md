# ERRORS.md - ELM Formed Hexagon Sand, high-effort arm (2026-09-29)

Every error hit while building this run, with cause, fix and status. All are resolved unless a line says otherwise.
The last section lists known limitations, which are not errors.

| # | Artifact / action | Observed error | Cause | Fix | Status |
|---|---|---|---|---|---|
| 1 | `facegen.py`, `from facegen import *` in a test script | `NameError: _sources` | `import *` skips names that start with an underscore | Call `import facegen; facegen._sources()` | Resolved, re-run OK |
| 2 | `chis.py` first run | `NameError: _im` | Helper defined in `srcs.py`, not imported | `from srcs import _im` | Resolved |
| 3 | Raw-face height, first view | Faces showed a dither or halftone pattern | Luminance pre-blur (sigma 0.9 px) was too small for the WebP source, so codec noise entered the shape-from-shading height | Pre-blur sigma raised to 1.3 px, source cache rebuilt | Resolved, pattern gone in `_REVIEW_crops_1to1.jpg` |
| 4 | Raw relief amplitude | Measured rms 0.134 mm instead of the design 0.17 mm | The unit-std normalisation was applied before the bicubic upsample and sharpening, which changed the variance | Re-normalise `zt` to unit std after upsampling, then scale | Resolved, measured rms 0.1674 mm |
| 5 | Chiseled residual | Grooves looked noisy under grazing light | Residual amplitude 0.045 mm was too high | 0.035 mm | Resolved |
| 6 | Chiseled colour | Texture energy about half of the render (1.59 vs 3.26) | Groove shading in colour was 3 % | Colour gain 0.06 | Resolved, now 3.15 vs 3.26 |
| 7 | First grazing preview | Chiseled grooves rendered near black | No ambient floor in the light model | Floor 0.45, gain 0.55 (`review.py`) | Resolved |
| 8 | Patching `facegen.py` from a bash heredoc | `SyntaxError` from nested quotes | Shell quoting | Redone with the Edit tool. One atlas was built in between without the shared usage dicts and was then rebuilt | Resolved |
| 9 | Debug snippet | `SyntaxError` on `import quilt if False else None` | Invalid statement | Removed the line | Resolved |
| 10 | Colour-fidelity check | Atlas read "11 levels brighter" than the render | `float32` `mean(0)` over 20 M pixels accumulated error. The atlas was correct | Use float64 for large means (`verify.py`, `cmp_stats.py`) | Resolved, means agree to about 0.5 level |
| 11 | Chiseled groove phase | Face 50 read 56.6 degrees of phase wobble | The 480 px source block leaked past the hex edge | Block reduced to 400 px | Resolved, wobble 8.8 to 14.1 degrees per face |
| 12 | Repetition, matte and raw | Same source clusters reused across faces in the earlier build (before the shared usage penalty; its NCC figures were not kept) | Quilting only avoided reuse inside one face | Shared `used` dict per type with a neighbour-weighted penalty (`REUSE_W = 0.3`) | Improved. Raw max 0.495, matte max 0.723, below the 0.9 copy level. Partial matte reuse remains, see limitations |
| 13 | PNG save | `OSError: [Errno 22]` (brief warning) | Not seen in the final runs | `save_img` retries anyway | Not reproduced |

## Known limitations (not errors)

- The y-wrap seam metric is small by construction: rows 0 and H-1 both lie in the joint centre line. Vertical joint runs measure [4, 8] px (4 + 4 across the wrap).
- The matte source has WebP block artefacts of 1 to 2 levels. They are invisible at normal contrast and are left in.
- Matte faces still occasionally reuse the same speckle cluster (max patch NCC 0.723).
- Session notice, not a build error: the MCP servers "claude.ai Devil's Advocate", "FormEdge" and "Meridian Connector for QuickBooks" need authorization (claude.ai connector settings or `/mcp`). They are unrelated to this task and were not used.
