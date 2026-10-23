"""Append the MSI Soreno Ivory 24x48 rebuild section to the root PROJECT_MEMORY.md (append-only, LF),
then rescan the appended bytes for control characters. The only write outside the run dir; it is the
AGENTS.md-mandated project memory, not a deliverable."""
import os

PM = "E:/Claude/3D-Model-Workflow/PROJECT_MEMORY.md"
TEXT = """
## MSI Soreno Ivory 24x48 rebuild — 2026-09-26
- Artifact: `output/msi_soreno_ivory_24x48/` (colour, 16-bit bump, model .pat, notes zip). Supersedes `output/belmont_tiles/Soreno_Ivory_24x48/`.
- WebFetch/curl of Home Depot, Lowe's, FloorBox, Zoro returned HTTP 403. Cause: retailer bot protection. Fix: Home Depot read via the Browser pane (spec JSON in page); others not needed. Status: resolved.
- Home Depot NSORIVO2448 / NSORIVO2448PP URLs now redirect to "MSI Sorena Cream NSORCREAM2448C/P" (same Internet #), 48 x 24 in, 9.90 mm, V3. Cause: HD relabelled listing; sameness unconfirmed. Used only to corroborate the metric thickness. Status: data caveat.
- Actual (calibrated) size: still not published by MSI (page, Soreno flyer, install guide, DCOF sheet) or 11 dealers. Fix: used the evidenced metric rectified convention 600 x 1200 mm (Italian origin per villohome, 0.39 in = 10 mm body, HD 9.90 mm), disclosed in README. Status: limitation, disclosed. Prevention: MSI never publishes actual size on product pages; check the flyer PDF at cdn.msisurfaces.com/files/flyers/<collection>-porcelain-flyer.pdf for joint and bond guidance (Soreno: 1/8 in grout, < 33 % stagger).
- Read tool on a PDF with a `pages` range failed: "pdftoppm is not installed". Cause: no Poppler on this machine. Fix: read PDFs under 10 pages without `pages`. Status: resolved.
- MSI room scenes at `/images/roomscenes/<name>.jpg` returned 404. Cause: only `medium/` and `thumb/` exist. Fix: `medium/`. Status: resolved.
- CDN probe of 1,049 path variants (large/, detail/, variations/, -01..-06, -variation-0n, ...) found 8 images, all <= 805 px, no face variations. NCC duplicate test (DoG band, all translations, 0/180/flips, 90/270 on squares; phase-randomised surrogate baseline 0.03-0.15) shows every face in every Soreno Ivory swatch (24x48, 24x24, paver, flyer, dealer copies, old Belmont reference) is one of only 2 printed faces A/B, several mirrored. The 24x24 swatch holds A (both halves) and B's right half at 16.7 px/in vs 11.2 px/in in the 24x48 swatch. Fix: registered hi-res halves onto upsampled A/B; synthesised 18 atlas faces by min-cut quilting with usage penalty; measured max face-vs-face NCC 0.112. Status: limitation, disclosed.
- First union-find clustering of face NCC merged partial overlaps (0.4-0.6) into 2 clusters without separating whole duplicates. Cause: chaining through partial overlaps. Fix: match every face against the 2 full representatives. Status: resolved.
- Bash `sleep 45; tail` was blocked by the harness. Cause: chained sleeps are disallowed. Fix: Monitor with an until-loop. Status: resolved.
- b02_previews.py crashed: "ValueError: cannot write empty image". Cause: T-junction crop centred at x = 379 px, so cx - 400 < 0 gave an empty slice (same bug in e01 preview). Fix: use the row-1 joint at off + module (x = 1515). Status: resolved, previews regenerated.
- Size rule applied: true module 47.3691 x 23.747 in cannot reach a quarter-inch Sample Size; drawn 47.2083 x 23.625 in (-0.91 mm / +0.08 mm, < 0.1 %) with the 1/8 in joint kept gives 3 x 6 tiles = 142.00 x 142.50 in (11'-10" x 11'-10 1/2"). Verifier gate fails any non-quarter-inch value (negative-tested: 142.107 and 142.482 fail).
- Bump: full scale 1.592 mm, joint step 1.50 mm, eased edge 1.0 mm, micro-relief sd 0.028 bounded +/-0.10, clearance 1.408 mm. Revit amount 60 (= owner's 100 per 2.6 mm calibration scaled to 1.59 mm full scale).
"""


def main():
    before = os.path.getsize(PM)
    with open(PM, "rb") as f:
        f.seek(-1, 2)
        last = f.read(1)
    data = ("" if last == b"\n" else "\n") + TEXT
    with open(PM, "ab") as f:
        f.write(data.encode("utf-8"))
    with open(PM, "rb") as f:
        f.seek(before)
        new = f.read()
    bad = [b for b in new if b < 0x20 and b not in (0x0A,)]
    print("appended", len(new), "bytes; control chars:", len(bad))
    assert not bad


if __name__ == "__main__":
    main()
