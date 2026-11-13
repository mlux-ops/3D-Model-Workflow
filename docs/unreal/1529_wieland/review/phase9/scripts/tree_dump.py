"""Phase 9: print the render passes of one GPU profiler sample that take at least a given time.

Usage:
    python -B tree_dump.py <gpu_passes_*.json> <station> [<minimum ms, default 0.3>] [<sample number, default 2>]
"""

import json
import sys


def walk(node, depth, minimum, max_depth=9):
    if node["InclusiveMs"] < minimum:
        return
    children = node.get("Children") or []
    same = {}
    for child in children:
        same.setdefault(child["Name"], []).append(child)
    print("%s%-70s %7.3f" % ("  " * depth, node["Name"][:70], node["InclusiveMs"]))
    if depth >= max_depth:
        return
    for name, group in same.items():
        if len(group) > 3:
            total = sum(child["InclusiveMs"] for child in group)
            if total >= minimum:
                print("%s%-70s %7.3f  (%d passes of this name)" % ("  " * (depth + 1), name[:70], total, len(group)))
        else:
            for child in group:
                walk(child, depth + 1, minimum, max_depth)


def main(argv):
    with open(argv[1], encoding="utf-8") as handle:
        data = json.load(handle)
    station = argv[2]
    minimum = float(argv[3]) if len(argv) > 3 else 0.3
    number = int(argv[4]) if len(argv) > 4 else 2
    for sample in data["samples"]:
        if sample["station"] == station and sample["sample"] == number:
            print(station, sample["frame_timings"])
            for queue in sample["tree"]:
                walk(queue, 0, minimum)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
