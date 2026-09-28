"""Re-run the whole build in order (about 40 minutes). Every step reads the inputs or the
previous step's _work files and writes only inside the run folder (guard.out_path).

Measurement steps feeding the build:
  a03_fit_lattice   render hexagon lattice             -> _work/lattice.json
  a03b_refine...    sub-pixel refinement               -> _work/lattice.json
  a04_classify      per-face features / types          -> _work/cells_raw.json
  a05_grooves       groove angle, period, fold profile -> _work/grooves.json
  a08_measure_tone  lighting field, joint colour, groove phase, lifestyle tone -> _work/tone.json
Build:
  b01_sources  b02_layout  b03_quilt_raw  b04_build_maps  b05_previews
  a13_quilt_audit (reuse facts for the report)  b06_verify (gates, report.json)
Analysis-only scripts (evidence for decisions, not needed to reproduce the maps):
  a01_inspect_inputs, a02_zoom_probe, a06_light_fit, a07_dup_check, a09_pair_view,
  a10_view (review thumbnails), a11_contrast (relief calibration vs the lifestyle),
  a12_quilt_view (quilt seam views)
"""

import os
import subprocess
import sys
import time

STEPS = ["a03_fit_lattice.py", "a03b_refine_lattice.py", "a04_classify.py", "a05_grooves.py",
         "a08_measure_tone.py", "b01_sources.py", "b02_layout.py", "b03_quilt_raw.py",
         "b04_build_maps.py", "b05_previews.py", "a13_quilt_audit.py", "b06_verify.py"]


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    t0 = time.time()
    for s in STEPS:
        print("==> %s" % s, flush=True)
        r = subprocess.run([sys.executable, os.path.join(here, s)], cwd=here)
        if r.returncode != 0:
            print("step %s failed with exit code %d" % (s, r.returncode))
            return r.returncode
        print("    done at %.0fs" % (time.time() - t0), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
