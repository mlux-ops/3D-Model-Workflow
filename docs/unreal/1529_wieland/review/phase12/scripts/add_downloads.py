"""Phase 12, step 12.3: adds this phase's downloads to the end of asset_downloads.csv.

    python -P -B add_downloads.py <asset_downloads.csv> <site data folder>
"""
import csv
import hashlib
import os
import sys

READ = "2026-11-13"
PH_LICENCE = "Creative Commons CC0 1.0 Universal"
PH_NOTE = ("Licence page https://polyhaven.com/license read on %s: Poly Haven's assets are CC0, free for any purpose "
           "without attribution. No account, no cost. SHA-256 of the colour image %s.")


def folder_facts(folder):
    files = sorted(os.path.join(base, name) for base, _, names in os.walk(folder) for name in names)
    return files, sum(os.path.getsize(path) for path in files) / 1048576.0


def sha(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def main(table, site):
    with open(table, encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    columns = list(rows[0].keys())
    have = {row["name"] for row in rows}
    new = []
    for set_id, pixels, what in (("oak_veneer_02", "4,096", "oak veneer, straight tight grain"),
                                 ("ash_veneer", "2,048", "ash veneer"),
                                 ("white_maple_veneer", "2,048", "white maple veneer")):
        folder = "%s/textures_cc0/PolyHaven/%s" % (site, set_id)
        files, size = folder_facts(folder)
        colour = [path for path in files if "_diff_" in path][0]
        new.append({"name": "Poly Haven " + set_id, "files": len(files), "size_mb": "%.1f" % size,
                    "what_it_is": "Surface image set %s (%s): colour, relief and roughness, %s pixels, JPEG" % (set_id, what, pixels),
                    "source": "Poly Haven, downloaded %s; asset page https://polyhaven.com/a/%s, file list from "
                              "https://api.polyhaven.com/files/%s" % (READ, set_id, set_id),
                    "licence": PH_LICENCE, "evidence_or_note": PH_NOTE % (READ, sha(colour)), "kept_at": folder})
    folder = site + "/manufacturer_reference"
    files, size = folder_facts(folder)
    new.append({"name": "Manufacturer reference Brizo (Phase 12)", "files": len(files), "size_mb": "%.2f" % size,
                "what_it_is": "Four finish swatches and four product photographs from brizo.com (Matte Black, Brilliance Black "
                              "Onyx, Polished Chrome, Brilliance Stainless), with a manifest of addresses and SHA-256 sums",
                "source": "Brizo (brizo.com and media.brizo.com), downloaded %s; every address is in %s/manifest.csv" % (READ, folder),
                "licence": "No licence. The manufacturer's copyright. Reference only: read for colour and gloss, never "
                           "imported into the Unreal project, never used as a texture, kept outside the repository and not passed on.",
                "evidence_or_note": "No cost, no account. The cap for manufacturer reference is 500 MB; this is %.2f MB. "
                                    "kohler.com and hansgrohe.com refused direct file requests (HTTP 403), so nothing was saved "
                                    "from them; their pages were read through web search only." % size,
                "kept_at": folder})
    added = [row for row in new if row["name"] not in have]
    # Rows are added at the end; the rows already there are not rewritten.
    with open(table, "a", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, columns, lineterminator="\n")
        writer.writerows(added)
    total = sum(float(row["size_mb"] or 0) for row in rows + added)
    print("added %d rows; the list now holds %d rows, %.1f MB in all" % (len(added), len(rows) + len(added), total))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
