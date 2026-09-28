"""Rebuild everything in order. Deterministic (fixed RNG seeds); about 12 minutes,
most of it the repetition patch search in check_outputs.py."""

import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STEPS = [
    "analyse_render.py",          # lattice fit of the layout render -> data/render_lattice.json
    "classify_render_faces.py",   # per-face metrics + contact sheet -> data/render_face_metrics.json
    "check_source_duplicates.py", # are render faces copies of each other? -> data/source_duplicate_check.json
    "source_layers.py",           # pool, chiseled geometry -> data/render_pool.json
    "build_atlas.py",             # Color.png, Bump16.png, face_ids.png, report.json
    "make_previews.py",           # review images
    "check_outputs.py",           # headers, repetition checks -> report.json "checks"
]
for s in STEPS:
    print("==>", s, flush=True)
    subprocess.run([sys.executable, s], cwd=HERE, check=True)
