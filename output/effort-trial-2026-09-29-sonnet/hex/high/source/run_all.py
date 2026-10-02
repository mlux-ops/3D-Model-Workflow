"""Reproduce every map and report from the two input images. Run from this folder: python run_all.py
Total ~10 min (lattice fit 70 s, source caches ~2 min, atlas ~60 s, verification ~2 min)."""
import subprocess
import sys
import time

STEPS = [
    "s02_lattice.py",        # fit the flat-top hex lattice to the render -> work/render_lattice.json
    "s03_classify.py",       # per-hex texture statistics and face type -> work/render_hexes.json
    "s04_grooves.py",        # groove period/direction/contrast of chiseled hexes -> work/groove_meas.json
    "s06_raw_height_test.py",  # light axis for shape-from-shading -> work/raw_light_axis.json
    "s09_joint_colour.py",   # joint colour and width in the render -> work/joint_colour.json
    "layout.py",             # face-type layout (annealing) -> work/layout.json
    "build_atlas.py",        # builds source caches on first use, then Color/Bump16/face_ids
    "review.py",             # review images
    "verify.py",             # measurements -> textures/report.json
]

t0 = time.time()
for s in STEPS:
    print("=== %s (%.0fs)" % (s, time.time() - t0)); sys.stdout.flush()
    subprocess.run([sys.executable, s], check=True)
print("done in %.0fs" % (time.time() - t0))
