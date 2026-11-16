"""Fetch the public map data Phase 2 uses, for one square around the lot.

Usage:
    python fetch_site_data.py <output folder> [--half-side-ft 492.125]
        [--centre-east-ft E] [--centre-north-ft N]

Fetches five extracts and writes each beside a ".source.txt" file that names
its address, the time it was fetched, the box it covers, its size, its
checksum and the terms it is offered under:

    county_parcels_2025.json     Cook County parcel outlines (Esri JSON, EPSG 3435)
    county_footprints_2022.json  Cook County building footprints (Esri JSON, EPSG 6455)
    county_ortho_2025.tif        Cook County aerial photograph, 0.5 ft pixels
    isgs_dsm_2022.tif            Illinois State Geological Survey, top surface, 1 ft cells
    isgs_dtm_2022.tif            the same survey, bare ground, 1 ft cells

All coordinates are Illinois State Plane East in US survey feet. The image
requests are snapped outward to each service's own pixel grid and use
nearest-neighbour sampling, so every pixel that arrives is a pixel of the
source and none is interpolated. The vector requests keep the service's own
coordinates (no reprojection by the server).

Nothing is fetched until the owner has approved the download (PLAN.md, "Ask
first"). The folder must be outside every git repository: the county's terms
leave redistribution unclear.

Needs the requests package.
"""

import datetime
import hashlib
import json
import math
import os
import sys

import requests

COUNTY_TERMS = ('Cook County: "While efforts have been made to be as accurate as possible, Cook County provides the data '
                'for use \'as is\'." The county site also says its content is copyrighted; redistribution is unclear. '
                'Kept for private use in this model only (SOURCES.md).')
ISGS_TERMS = ('Illinois State Geological Survey, Illinois Height Modernization: "No restrictions apply to these data." '
              'Use constraints: "None." (service metadata, as recorded in SOURCES.md).')

PARCELS = "https://gis.cookcountyil.gov/traditional/rest/services/parcelHistorical/MapServer/2025"
FOOTPRINTS = "https://gis.cookcountyil.gov/traditional/rest/services/buildingFootprint_2022/MapServer/0"
ORTHO = "https://gis.cookcountyil.gov/imagery/rest/services/CookOrtho2025/ImageServer"
DSM = "https://data.isgs.illinois.edu/arcgis/rest/services/Elevation/IL_Cook_DSM_2022/ImageServer"
DTM = "https://data.isgs.illinois.edu/arcgis/rest/services/Elevation/IL_Cook_DTM_2022/ImageServer"

# Midpoint of the county's two parcel centres (SOURCES.md), State Plane East, US survey feet.
DEFAULT_CENTRE = (1174227.19, 1910645.18)
DEFAULT_HALF_SIDE_FT = 492.125  # 150 m

SESSION = requests.Session()
SESSION.headers["User-Agent"] = "python-requests site-data-fetch"


def option(argv, name, default):
    if name in argv:
        return float(argv[argv.index(name) + 1])
    return default


def now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def write_source(path, lines):
    with open(path + ".source.txt", "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def fetch_vector(service, well_known_id, box, out_path, terms):
    features = []
    offset = 0
    first = None
    addresses = []
    while True:
        params = {
            "where": "1=1",
            "geometry": "%.4f,%.4f,%.4f,%.4f" % box,
            "geometryType": "esriGeometryEnvelope",
            "inSR": well_known_id,
            "outSR": well_known_id,
            "spatialRel": "esriSpatialRelIntersects",
            "outFields": "*",
            "returnGeometry": "true",
            "orderByFields": "OBJECTID",
            "resultOffset": offset,
            "f": "json",
        }
        response = SESSION.get(service + "/query", params=params, timeout=120)
        response.raise_for_status()
        addresses.append(response.url)
        page = response.json()
        if "error" in page:
            raise RuntimeError("%s answered: %s" % (service, json.dumps(page["error"])))
        if first is None:
            first = page
        got = page.get("features", [])
        features.extend(got)
        if not page.get("exceededTransferLimit") or not got:
            break
        offset += len(got)
    first["features"] = features
    first.pop("exceededTransferLimit", None)
    with open(out_path, "w", encoding="utf-8") as handle:
        json.dump(first, handle)
    write_source(out_path, [
        "file: " + os.path.basename(out_path),
        "service: " + service,
        "request(s): " + " ; ".join(addresses),
        "fetched: " + now(),
        "box (east min, north min, east max, north max, US survey ft): %.4f, %.4f, %.4f, %.4f" % box,
        "coordinate system asked for and returned: EPSG %s; as the file states it: %s" % (well_known_id, json.dumps(first.get("spatialReference"))),
        "features: %d" % len(features),
        "bytes: %d" % os.path.getsize(out_path),
        "sha256: " + sha256(out_path),
        "terms: " + terms,
    ])
    return {"file": out_path, "features": len(features), "bytes": os.path.getsize(out_path), "spatialReference": first.get("spatialReference")}


def fetch_image(service, box, out_path, pixel_type, terms):
    info = SESSION.get(service, params={"f": "json"}, timeout=120).json()
    if "error" in info:
        raise RuntimeError("%s answered: %s" % (service, json.dumps(info["error"])))
    px, py = float(info["pixelSizeX"]), float(info["pixelSizeY"])
    extent = info["extent"]
    x_ref, y_ref = float(extent["xmin"]), float(extent["ymax"])
    x0 = x_ref + math.floor((box[0] - x_ref) / px) * px
    x1 = x_ref + math.ceil((box[2] - x_ref) / px) * px
    y1 = y_ref - math.floor((y_ref - box[3]) / py) * py
    y0 = y_ref - math.ceil((y_ref - box[1]) / py) * py
    width = int(round((x1 - x0) / px))
    height = int(round((y1 - y0) / py))
    params = {
        "bbox": "%.6f,%.6f,%.6f,%.6f" % (x0, y0, x1, y1),
        "size": "%d,%d" % (width, height),
        "format": "tiff",
        "pixelType": pixel_type,
        "interpolation": "RSP_NearestNeighbor",
        "f": "image",
    }
    response = SESSION.get(service + "/exportImage", params=params, timeout=300)
    response.raise_for_status()
    content_type = response.headers.get("Content-Type", "")
    if "image" not in content_type:
        raise RuntimeError("%s did not return an image: %s %s" % (service, content_type, response.text[:300]))
    with open(out_path, "wb") as handle:
        handle.write(response.content)
    reference = extent.get("spatialReference", {})
    write_source(out_path, [
        "file: " + os.path.basename(out_path),
        "service: " + service,
        "request: " + response.url,
        "fetched: " + now(),
        "box as snapped to the service's pixel grid (east min, north min, east max, north max, US survey ft): %.6f, %.6f, %.6f, %.6f" % (x0, y0, x1, y1),
        "pixel size (ft): %s by %s; size (pixels): %d by %d; pixel type: %s; bands: %s" % (px, py, width, height, pixel_type, info.get("bandCount")),
        "upper-left corner of the upper-left pixel (east, north): %.6f, %.6f" % (x0, y1),
        "coordinate system as the service states it: %s" % (json.dumps(reference)[:900]),
        "height units as the service states them: %s" % json.dumps(info.get("heightModelInfo")),
        "sampling: nearest neighbour, on the service's own grid",
        "bytes: %d" % os.path.getsize(out_path),
        "sha256: " + sha256(out_path),
        "terms: " + terms,
    ])
    return {"file": out_path, "bytes": os.path.getsize(out_path), "box": [x0, y0, x1, y1], "size": [width, height], "pixel": [px, py]}


def main(argv):
    if len(argv) < 2 or argv[1].startswith("--"):
        print(__doc__)
        return 2
    folder = argv[1]
    half = option(argv, "--half-side-ft", DEFAULT_HALF_SIDE_FT)
    east = option(argv, "--centre-east-ft", DEFAULT_CENTRE[0])
    north = option(argv, "--centre-north-ft", DEFAULT_CENTRE[1])
    box = (east - half, north - half, east + half, north + half)
    os.makedirs(folder, exist_ok=True)
    results = {}
    jobs = (
        ("county_parcels_2025.json", lambda path: fetch_vector(PARCELS, "3435", box, path, COUNTY_TERMS)),
        ("county_footprints_2022.json", lambda path: fetch_vector(FOOTPRINTS, "6455", box, path, COUNTY_TERMS)),
        ("isgs_dsm_2022.tif", lambda path: fetch_image(DSM, box, path, "F32", ISGS_TERMS)),
        ("isgs_dtm_2022.tif", lambda path: fetch_image(DTM, box, path, "F32", ISGS_TERMS)),
        ("county_ortho_2025.tif", lambda path: fetch_image(ORTHO, box, path, "U8", COUNTY_TERMS)),
    )
    failed = 0
    for name, job in jobs:
        path = os.path.join(folder, name)
        if os.path.exists(path):
            results[name] = {"skipped": "already present"}
            print("%-28s already present; not fetched again" % name)
            continue
        try:
            results[name] = job(path)
            print("%-28s %s" % (name, json.dumps({k: v for k, v in results[name].items() if k != "file"})))
        except Exception as exc:
            failed += 1
            results[name] = {"error": repr(exc)}
            print("%-28s FAILED: %r" % (name, exc))
    with open(os.path.join(folder, "fetch_record.json"), "w", encoding="utf-8") as handle:
        json.dump({"fetched": now(), "box": box, "results": results}, handle, indent=1)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
