# -*- coding: utf-8 -*-
"""Copies the validated outputs into _work/<tag>/ (all writes through safe()) so a rebuild can be reverted.
usage: python snapshot.py <tag>"""
import os
import shutil
import sys

sys.path.insert(0, "E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce/max/source")
from guard import safe

RUN = "E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce/max"
tag = sys.argv[1]
dst = RUN + "/_work/" + tag + "/"
items = ["Visual_Comfort_Nodes_KW1041MBK_Midnight_Black_R2025.rfa", "validation.json", "_work/build_result.json"]
for f in sorted(os.listdir(RUN + "/views")):
    items.append("views/" + f)
n = 0
for it in items:
    src = RUN + "/" + it
    if os.path.isfile(src):
        out = safe(dst + it.replace("/", "__"))
        shutil.copy2(src, out)
        n += 1
print("copied", n, "files to", dst)
