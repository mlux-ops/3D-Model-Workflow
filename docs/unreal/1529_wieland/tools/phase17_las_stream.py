"""Phase 17: stream one 2022 Cook County LAS tile out of the state's remote zip and keep only points in given boxes.

Usage:
    python -B -P phase17_las_stream.py <part 1-5> <tile name e.g. 17259100> <boxes json> <out npz>

<boxes json>: {"<label>": [east min, north min, east max, north max], ...} in State Plane East feet.
Keeps every point inside any box except classes 7 (low noise) and 18 (high noise). The whole tile is read once
from its start (a deflate member cannot be entered in the middle), in chunks of one million points, and never
stored. The npz holds x, y, z (float64 feet, NAVD 88 feet), cls (uint8), ret (return number), nret (number of
returns), box (int16 index into the labels), labels, and the header facts. A .source.txt records streamed and
stored bytes.

LAS 1.4, point format 6 (30 bytes): X, Y, Z int32 scaled; intensity; return byte (return number bits 0-3,
number of returns bits 4-7); flags; classification; user data; scan angle; point source; GPS time.
"""

import datetime
import json
import os
import struct
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import phase17_remote_zip as rz  # noqa: E402

DT6 = np.dtype([("X", "<i4"), ("Y", "<i4"), ("Z", "<i4"), ("I", "<u2"), ("R", "u1"), ("F", "u1"), ("C", "u1"),
                ("U", "u1"), ("A", "<i2"), ("S", "<u2"), ("T", "<f8")])


def main(argv):
    part, tile, boxes_path, out = int(argv[1]), argv[2], argv[3], argv[4]
    if os.path.exists(out):
        print("exists", out)
        return 0
    with open(boxes_path) as handle:
        boxes = json.load(handle)
    labels = list(boxes.keys())
    bx = np.array([boxes[k] for k in labels], dtype=np.float64)
    archive = rz.open_part(part)
    archive.fp.block = 64 << 20
    names = [n for n in archive.namelist() if n.endswith("/%s.las" % tile) or n == "%s.las" % tile]
    if not names:
        raise RuntimeError("tile %s not in part %d" % (tile, part))
    info = archive.getinfo(names[0])
    started = time.time()
    with archive.open(names[0]) as f:
        h = f.read(375)
        if h[:4] != b"LASF":
            raise RuntimeError("not a LAS file")
        off = struct.unpack("<I", h[96:100])[0]
        fmt = h[104] & 0x3F
        rl = struct.unpack("<H", h[105:107])[0]
        scale = struct.unpack("<3d", h[131:155])
        offs = struct.unpack("<3d", h[155:179])
        count = struct.unpack("<Q", h[247:255])[0]
        if fmt != 6 or rl != 30:
            raise RuntimeError("point format %d record %d not handled" % (fmt, rl))
        f.read(off - 375)
        keep = {k: [] for k in ("x", "y", "z", "cls", "ret", "nret", "box")}
        read = 0
        chunk = 1_000_000
        while read < count:
            n = min(chunk, count - read)
            raw = f.read(n * rl)
            pts = np.frombuffer(raw, DT6, len(raw) // rl)
            read += len(pts)
            x = pts["X"] * scale[0] + offs[0]
            y = pts["Y"] * scale[1] + offs[1]
            cls = pts["C"]
            ok = (cls != 7) & (cls != 18)
            which = np.full(len(pts), -1, np.int16)
            for i, b in enumerate(bx):
                inside = ok & (which < 0) & (x >= b[0]) & (x <= b[2]) & (y >= b[1]) & (y <= b[3])
                which[inside] = i
            sel = which >= 0
            if sel.any():
                keep["x"].append(x[sel])
                keep["y"].append(y[sel])
                keep["z"].append(pts["Z"][sel] * scale[2] + offs[2])
                keep["cls"].append(cls[sel])
                keep["ret"].append(pts["R"][sel] & 0x0F)
                keep["nret"].append(pts["R"][sel] >> 4)
                keep["box"].append(which[sel])
            if len(pts) < n:
                break
    arrays = {k: (np.concatenate(v) if v else np.zeros(0)) for k, v in keep.items()}
    np.savez_compressed(out, labels=np.array(labels), tile=tile, part=part, scale=scale, offset=offs, count=count, **arrays)
    with open(out + ".source.txt", "w", encoding="utf-8") as handle:
        handle.write("\n".join([
            "tile: %s (member %s of %s)" % (tile, names[0], rz.BASE % part),
            "fetched: " + datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
            "points in tile: %d; points kept: %d; boxes: %d" % (count, len(arrays["x"]), len(labels)),
            "streamed bytes (compressed member): %d; stored bytes: %d" % (info.compress_size, os.path.getsize(out)),
            "seconds: %.0f" % (time.time() - started),
            "coordinates: Illinois State Plane East, NAD83(2011), US survey feet; heights NAVD 88 feet (ISGS metadata)",
            "terms: ISGS, no restrictions; cite Illinois State Geological Survey",
        ]) + "\n")
    print("kept", len(arrays["x"]), "of", count, "in %.0f s" % (time.time() - started))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
