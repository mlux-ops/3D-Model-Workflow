# -*- coding: utf-8 -*-
"""Standalone entry point: validate the saved RFA without rebuilding it (run through the serialized runner)."""
import sys

RUN = "E:/Claude/3D-Model-Workflow/output/effort-trial-2026-09-29-sonnet/sconce/max"
if RUN + "/source" not in sys.path:
    sys.path.insert(0, RUN + "/source")
import validate_sconce

validate_sconce.run_all(__revit__.Application)
