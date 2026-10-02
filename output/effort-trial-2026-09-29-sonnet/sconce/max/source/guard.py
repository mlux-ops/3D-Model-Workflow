# -*- coding: utf-8 -*-
"""Write guard shared by every script in this run. Works in CPython 3 and IronPython 2.7.

Every file write goes through safe(path): it refuses anything outside the run folder.
"""
import os

RUN = os.path.normcase(os.path.abspath(
    "E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce/max"))


def safe(path):
    full = os.path.normcase(os.path.abspath(path))
    if full != RUN and not full.startswith(RUN + os.sep):
        raise RuntimeError("write outside run folder refused: " + path)
    parent = os.path.dirname(full)
    if not os.path.isdir(parent):
        os.makedirs(parent)
    return path
