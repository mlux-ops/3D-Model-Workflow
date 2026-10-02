"""Design constants shared by the relief calibration (s10c), the atlas build (s10b) and the verifier (s11).

Heights are millimetres above the joint floor. No depth reference exists in the two source images,
so every value here is a design value, not a measurement (see README limitations)."""

import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from guard import out_path  # noqa: E402

JOINT_RGB = np.array([211.0, 202.0, 188.0], np.float32)
JOINT_DEPTH_MM = 1.6          # face plane above the joint floor
FULL_SCALE_MM = 2.2           # Bump16 full range (white) in mm above the joint floor
CHIS_DEPTH_MM = 0.5           # Chiseled groove floor below the land plane (peak to peak of the groove profile)
RAW_CLIP_MM = 0.55            # soft clip of Raw relief (tanh) around the face plane
EDGE_WIDTH_PX = 1.5           # smoothstep width of the joint edge, pixels
SQRT2 = float(np.sqrt(2.0))


def calibration():
    """work/relief_calibration.json written by s10c_relief_calibration.py."""
    return json.load(open(out_path("work", "relief_calibration.json")))
