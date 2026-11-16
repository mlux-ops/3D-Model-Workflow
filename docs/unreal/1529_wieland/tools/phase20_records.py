"""Phase 20: download and licence rows for the reference photographs.

Usage: python -B -P phase20_records.py <commons_index.csv> <building_table.csv>

Appends to asset_downloads.csv one row per photograph used in the building table and one row for the whole fetched
set (every file with its author, licence and address is in review/phase20/commons_index.csv), and one group row to
asset_licence_groups.csv. Rows already present (same name) are not written twice.
"""

import csv
import os
import sys

DOCS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")


def main(argv):
    index, table = argv[1], argv[2]
    idx = list(csv.DictReader(open(index, encoding="utf-8")))
    used_text = " | ".join(r["photographs"] for r in csv.DictReader(open(table, encoding="utf-8")))
    used_titles = {x["title"] for x in idx if x["title"].replace("File:", "") + " (" in used_text}
    dl_path = os.path.join(DOCS, "asset_downloads.csv")
    have = {r["name"] for r in csv.DictReader(open(dl_path, encoding="utf-8"))}
    rows = []
    for x in idx:
        if x["title"] not in used_titles:
            continue
        name = "Phase 20 reference photograph: " + x["title"].replace("File:", "")
        if name in have:
            continue
        rows.append([name, 1, round(int(x["bytes"]) / 1e6, 2),
                     "Photograph used to judge cladding, colour and window grid (1,280 px thumbnail); reference only, never shipped or traced",
                     "Wikimedia Commons, %s (thumbnail %s), downloaded 2026-11-14" % (x["page_url"], x["thumb_url"]),
                     x["licence"] + (" (" + x["licence_url"] + ")" if x["licence_url"] else ""),
                     "Author: %s. %s" % (x["author"] or "not given on the file page", "Attribution kept here; share-alike does not attach because nothing is shipped or adapted." if "SA" in x["licence"] else "Attribution kept here."),
                     x["file"]])
    total = sum(int(x["bytes"]) for x in idx)
    summary = "Phase 20 reference photographs, whole fetched set (Wikimedia Commons)"
    if summary not in have:
        rows.append([summary, len(idx), round(total / 1e6, 1),
                     "Thumbnails (1,280 px) of the free-licence files found for the work list (text and geotag searches); reference only",
                     "Wikimedia Commons public interface, 2026-11-14; each file's address, author and licence in docs/unreal/1529_wieland/review/phase20/commons_index.csv",
                     "CC0, public domain, CC BY or CC BY-SA, per file", "Non-free, fair-use and Google-derived files refused by tools/phase20_commons.py",
                     "E:/Wieland1529_site_data/phase20/commons"])
    with open(dl_path, "a", newline="", encoding="utf-8") as h:
        csv.writer(h, lineterminator="\n").writerows(rows)
    lg_path = os.path.join(DOCS, "asset_licence_groups.csv")
    lg_have = {r["group"] for r in csv.DictReader(open(lg_path, encoding="utf-8"))}
    group = "Phase 20 reference photographs (Wikimedia Commons)"
    if group not in lg_have:
        with open(lg_path, "a", newline="", encoding="utf-8") as h:
            csv.writer(h, lineterminator="\n").writerow([
                group, "reference only, not shipped", len(idx), round(total / 1e6, 1),
                "Photographs of the skyline towers and of Old Town near the lot, looked at to set material colours and window grids",
                "Wikimedia Commons, 2026-11-14 (review/phase20/commons_index.csv)",
                "CC0, public domain, CC BY, CC BY-SA (per file)",
                "CC BY and CC BY-SA need attribution: author and file page are listed per file. No photograph is used as a texture or traced, so share-alike does not reach the delivery.",
                used_titles and sorted(used_titles)[0].replace("File:", "") or ""])
    print("download rows", len(rows), "used photographs", len(used_titles))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
