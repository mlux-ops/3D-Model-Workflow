"""Phase 13, step 13.1, off line and read-only: where the triangles of an earlier detailed building part lie,
in site feet, to decide which triangles stand on the planned development's land.

Reads the raw mesh data written by dump_r15_parts.py (our own project data, review/phase13/scratch).
Usage: python -B review/phase13/scripts/r15_parts_by_north.py <label> <location x> <location y> [cut north ft]
"""
import os
import sys

import numpy

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
SCRATCH = os.path.join(os.path.dirname(HERE), "scratch")
CM = 30.48006096

label = sys.argv[1]
offset = numpy.array([float(sys.argv[2]), float(sys.argv[3]), 0.0])
cut = float(sys.argv[4]) if len(sys.argv) > 4 else -24.75
data = numpy.load(os.path.join(SCRATCH, label + ".npz"), allow_pickle=True)
print("keys:", list(data.keys()))
positions = data["positions"] + offset
triangles = data["triangles"]
corners = positions[triangles]                     # triangles x 3 corners x 3 coordinates
north = -corners[:, :, 0] / CM
east = -corners[:, :, 1] / CM
up = corners[:, :, 2] / CM
low, high = north.min(axis=1), north.max(axis=1)
print("triangles %d; north %.1f..%.1f ft, east %.1f..%.1f ft, up %.1f..%.1f ft" % (
    len(triangles), north.min(), north.max(), east.min(), east.max(), up.min(), up.max()))
south_side = high <= cut
north_side = low >= cut
crossing = ~south_side & ~north_side
print("cut at north %.2f ft: wholly south %d, wholly north %d, crossing %d" % (
    cut, south_side.sum(), north_side.sum(), crossing.sum()))
if crossing.any():
    print("crossing triangles: north %.2f..%.2f, east %.1f..%.1f, up %.1f..%.1f" % (
        low[crossing].min(), high[crossing].max(), east[crossing].min(), east[crossing].max(),
        up[crossing].min(), up[crossing].max()))
    area = 0.5 * numpy.linalg.norm(numpy.cross(corners[:, 1] - corners[:, 0], corners[:, 2] - corners[:, 0]), axis=1)
    order = numpy.argsort(-area * crossing)[:12]
    for index in order:
        if crossing[index]:
            print("  triangle %d: %.0f sq ft, north %.1f..%.1f, east %.1f..%.1f, up %.1f..%.1f, slot %d" % (
                index, area[index] / CM / CM, low[index], high[index], east[index].min(), east[index].max(),
                up[index].min(), up[index].max(), int(data["material_ids"][index])))
# How much stands in each 5 ft strip going north, and how high it reaches there.
centre = north.mean(axis=1)
for start in numpy.arange(numpy.floor(north.min() / 5.0) * 5.0, north.max(), 5.0):
    chosen = (centre >= start) & (centre < start + 5.0)
    if chosen.any():
        print("north %6.1f..%6.1f: %6d triangles, east %6.1f..%6.1f, up %5.1f..%5.1f" % (
            start, start + 5.0, chosen.sum(), east[chosen].min(), east[chosen].max(), up[chosen].min(), up[chosen].max()))
