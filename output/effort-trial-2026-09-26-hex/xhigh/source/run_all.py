"""Reproduce the whole build from the two inputs, in order.

  analyze_render.py   joint-row detection (diagnostic prints)
  analyze_lattice.py  first lattice estimate from the horizontal joints
  fit_lattice.py      2D refit of the render lattice (column phase / pitch) -- authoritative
  classify_render.py  per-cell texture statistics -> Matte / Raw / Chiseled
  measure_fft.py      chiseled angles and pitch from the 2D spectrum, joint colour, pools
  prepare_pools.py    detrended colour residual, relief sources, pool masks, profile fit
  prepare_chiseled.py Chiseled roughness / modulation pools (grooves notched out), per orientation
  build_maps.py       layout, quilting, relief, Color / Bump16 / face_ids / report.json
  verify.py           independent gate measurements -> report.json["verification"]
  make_previews.py    review images

Diagnostics that informed constants but are not needed to reproduce the maps:
  inspect_inputs.py, inspect_lifestyle.py, crops_sheet.py, check_lattice.py, measure_chiseled.py,
  measure_chiseled_rough.py, calibrate_relief.py, calibrate_raw_band.py, compare_lifestyle.py,
  ghost_locate.py
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STEPS = ["analyze_render.py", "analyze_lattice.py", "fit_lattice.py", "classify_render.py", "measure_fft.py",
         "prepare_pools.py", "prepare_chiseled.py", "build_maps.py", "verify.py", "make_previews.py"]
start = sys.argv[1] if len(sys.argv) > 1 else STEPS[0]
for s in STEPS[STEPS.index(start):]:
    print("=== %s" % s, flush=True)
    r = subprocess.run([sys.executable, os.path.join(HERE, s)], cwd=HERE)
    if r.returncode != 0:
        sys.exit("step failed: %s (exit %d)" % (s, r.returncode))
print("all steps completed")
