"""Phase 17: fetch the ISGS 2022 surface (DSM) and ground (DTM) models over a box, at a chosen cell size.

Usage:
    python -I phase17_fetch_rasters.py <out folder> <name> <east min> <north min> <east max> <north max> <cell ft> [dsm|dtm|both]

Coordinates are Illinois State Plane East (NAD83 2011), US survey feet; heights US survey feet above NAVD 88.
The box is snapped outward to the cell size on the service's own grid origin. The request is split into strips
within the service's 15000 by 4100 pixel limit and joined into one float32 array saved as <name>_<dsm|dtm>.npz
(keys: z, x0, y1, cell) beside a .source.txt naming the requests, time, box and terms. Nearest-neighbour
sampling, so every value is a value of the source grid. Skips an output that exists.

Needs numpy and Pillow (both already installed). Writes nothing to the repository.
"""

import datetime
import hashlib
import io
import json
import math
import os
import sys
import time
import urllib.parse
import urllib.request

import numpy as np
from PIL import Image

SERVICES = {
    "dsm": "https://data.isgs.illinois.edu/arcgis/rest/services/Elevation/IL_Cook_DSM_2022/ImageServer",
    "dtm": "https://data.isgs.illinois.edu/arcgis/rest/services/Elevation/IL_Cook_DTM_2022/ImageServer",
}
TERMS = ("Illinois State Geological Survey, Illinois Height Modernization, Cook County lidar 2022 (Merrick & Company, "
         "published 2023-04-26). Service metadata: no restrictions, use constraints none. ISGS Clearinghouse terms of use "
         "(read 2026-11-14): cite \"Illinois State Geological Survey\" in any product that uses the data; no warranty stated.")
UA = "Wieland1529-site-model/1.0 (private architectural visualisation)"
MAX_W, MAX_H = 2000, 2000  # larger requests time out at the gateway after about 30 s (an HTML page comes back)


def get(url, binary=True):
    for attempt in range(6):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=300) as r:
                return r.read(), r.headers.get("Content-Type", "")
        except Exception:
            if attempt == 5:
                raise
            time.sleep(5 * (attempt + 1))


def decode(data):
    """Decode the service's tiled, uncompressed float32 TIFF. Tiles that lie wholly outside the data (over the lake)
    are left out of the file with offset 0, which Pillow reports as a truncated file; those become NaN."""
    picture = Image.open(io.BytesIO(data))
    w, h = picture.size
    out = np.full((h, w), np.nan, np.float32)
    for tile in picture.tile:
        if tile.codec_name != "raw" or tile.args[0] != "F;32F":
            return np.array(picture, dtype=np.float32)
        x0, y0, x1, y1 = tile.extents
        if tile.offset == 0:
            continue
        tw, th = int(picture.tag_v2[322]), int(picture.tag_v2[323])  # stored tile size; edge tiles are padded
        block = np.frombuffer(data, "<f4", tw * th, tile.offset).reshape(th, tw)
        out[y0:y1, x0:x1] = block[:y1 - y0, :x1 - x0]
    return out


def fetch(service, box, cell):
    info = json.loads(get(service + "?f=json")[0])
    ext = info["extent"]
    xr, yr = float(ext["xmin"]), float(ext["ymax"])
    x0 = xr + math.floor((box[0] - xr) / cell) * cell
    x1 = xr + math.ceil((box[2] - xr) / cell) * cell
    y1 = yr - math.floor((yr - box[3]) / cell) * cell
    y0 = yr - math.ceil((yr - box[1]) / cell) * cell
    w, h = int(round((x1 - x0) / cell)), int(round((y1 - y0) / cell))
    out = np.full((h, w), np.nan, np.float32)
    urls = []
    for r0 in range(0, h, MAX_H):
        for c0 in range(0, w, MAX_W):
            hh, ww = min(MAX_H, h - r0), min(MAX_W, w - c0)
            bx0, bx1 = x0 + c0 * cell, x0 + (c0 + ww) * cell
            by1, by0 = y1 - r0 * cell, y1 - (r0 + hh) * cell
            params = {"bbox": "%.4f,%.4f,%.4f,%.4f" % (bx0, by0, bx1, by1), "size": "%d,%d" % (ww, hh), "format": "tiff",
                      "pixelType": "F32", "interpolation": "RSP_NearestNeighbor", "noData": "-9999", "f": "image"}
            url = service + "/exportImage?" + urllib.parse.urlencode(params)
            for attempt in range(6):  # a response is sometimes cut short or replaced by an HTML error page
                data, ctype = get(url)
                try:
                    if "image" not in ctype:
                        raise RuntimeError("not an image: %s %s" % (ctype, data[:200]))
                    arr = decode(data)
                    break
                except Exception:
                    if attempt == 5:
                        raise
                    time.sleep(5 * (attempt + 1))
            if arr.shape != (hh, ww):
                raise RuntimeError("shape %s, expected %s" % (arr.shape, (hh, ww)))
            arr[arr < -1000] = np.nan
            out[r0:r0 + hh, c0:c0 + ww] = arr
            urls.append(url)
            time.sleep(1.0)
    return out, x0, y1, urls


def main(argv):
    folder, name = argv[1], argv[2]
    box = [float(v) for v in argv[3:7]]
    cell = float(argv[7])
    which = argv[8] if len(argv) > 8 else "both"
    os.makedirs(folder, exist_ok=True)
    for kind in (["dsm", "dtm"] if which == "both" else [which]):
        path = os.path.join(folder, "%s_%s.npz" % (name, kind))
        if os.path.exists(path):
            print("exists", path)
            continue
        z, x0, y1, urls = fetch(SERVICES[kind], box, cell)
        np.savez_compressed(path, z=z, x0=x0, y1=y1, cell=cell)
        digest = hashlib.sha256(open(path, "rb").read()).hexdigest()
        with open(path + ".source.txt", "w", encoding="utf-8") as handle:
            handle.write("\n".join([
                "file: " + os.path.basename(path), "service: " + SERVICES[kind],
                "fetched: " + datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
                "upper-left corner (east, north, US ft): %.4f, %.4f; cell %.3f ft; shape %s" % (x0, y1, cell, z.shape),
                "nan cells: %d" % int(np.isnan(z).sum()), "bytes: %d" % os.path.getsize(path), "sha256: " + digest,
                "sampling: nearest neighbour", "terms: " + TERMS, "requests:"] + urls) + "\n")
        print("saved", path, z.shape, "nan", int(np.isnan(z).sum()), os.path.getsize(path))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
