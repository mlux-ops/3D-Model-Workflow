"""Phase 13: append the reference downloads of the proposed hotel to asset_downloads.csv (append only).

Usage, from the plan folder: python -B review/phase13/scripts/append_downloads.py
Running it twice does nothing the second time (rows are recognised by name).
"""
import csv
import os

HERE = os.path.dirname(os.path.abspath(__file__))
PLAN = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
TARGET = os.path.join(PLAN, "asset_downloads.csv")
KEPT = "E:/Wieland1529_site_data/proposed_hotel"
REFERENCE = ("No licence. The publisher's copyright. Reference only: read for shape and colour, never imported "
             "into the Unreal project, never used as a texture, kept outside the repository and not passed on.")
NOTE = ("No cost, no account. The cap for Phase 13 reference downloads is 500 MB; the whole folder is 53 MB. "
        "Every address, size and SHA-256 sum is in " + KEPT + "/manifest.csv.")

ROWS = [
    ["Proposed hotel reference: planned development ordinance (Phase 13)", 57, 44.0,
     "City of Chicago Residential-Business Planned Development No. 1335 as amended (PD1335.pdf, 43 pages: letter of "
     "8 Oct 2026, the 2020 ordinance with site plan, floor plans, roof plan and four elevations, and the superseded "
     "2016 version), with our own page pictures made from it (43 pages at screen size, 3 elevation enlargements, "
     "10 pages at 250 dots per inch in pd_hires)",
     "City of Chicago, https://gisapps.chicago.gov/gisimages/zoning_pds/PD1335.pdf, downloaded 2026-11-13",
     "Public record of the City of Chicago (Journal of the Proceedings of the City Council, 9 Sept 2020, "
     "pp. 20742-20760). The drawings in it are by Pappageorge Haymes Partners. Reference only: read for dimensions, "
     "never imported into the Unreal project, never used as a texture.",
     NOTE, KEPT],
    ["Proposed hotel reference: building permits (Phase 13)", 1, 0.1,
     "Building permit records for 1518-1530 N. Wells Street as JSON (foundation permit 100966661 and its "
     "reinstatements, wrecking permit B101080797 for 1520 N. Wells)",
     "City of Chicago Data Portal, data set Building Permits, https://data.cityofchicago.org/resource/ydr8-5enu.json, "
     "downloaded 2026-11-13",
     "Open data of the City of Chicago under the Data Portal's terms of use (free to use, no warranty).",
     NOTE, KEPT],
    ["Proposed hotel reference: published renderings (Phase 13)", 17, 8.6,
     "Renderings and drawings of the proposed hotel as published: ten pictures of 2022 (six exterior renderings, a "
     "flat Wells Street elevation, a site plan, a typical floor plan), four pictures and one page picture of the "
     "11 Feb 2024 article, one lead picture from Urbanize Chicago, one picture from the architect's page",
     "Chicago YIMBY (chicagoyimby.com, articles of 2022 and of 2024-02-11), Urbanize Chicago (October 2022), "
     "Pappageorge Haymes Partners (pappageorgehaymes.com); downloaded 2026-11-13; every address is in the manifest",
     REFERENCE, NOTE, KEPT],
    ["Proposed hotel reference: county address list (Phase 13)", 1, 0.3,
     "Cook County Assessor 'Parcel Addresses' rows of block 17-04-203 as JSON, used to tie parcel numbers to street "
     "addresses. It holds owner names and mailing addresses, so only parcel number and property address were "
     "copied into the repository",
     "Cook County Open Data, https://datacatalog.cookcountyil.gov/resource/3723-97qp.json, downloaded 2026-11-13",
     "Open data of Cook County under the portal's terms of use (free to use, no warranty).",
     NOTE, KEPT + "/county"],
]

with open(TARGET, newline="", encoding="utf-8") as handle:
    present = {row[0] for row in csv.reader(handle) if row}
with open(TARGET, "rb") as handle:
    handle.seek(-1, os.SEEK_END)
    ends_with_newline = handle.read(1) == b"\n"
added = 0
with open(TARGET, "a", newline="", encoding="utf-8") as handle:
    if not ends_with_newline:
        handle.write("\r\n")
    writer = csv.writer(handle)
    for row in ROWS:
        if row[0] not in present:
            writer.writerow(row)
            added += 1
print("rows added:", added)
