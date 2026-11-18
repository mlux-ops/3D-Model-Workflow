"""Phase 5, step 5.4: unpack downloaded texture archives and write the download record.

Usage:
    python -I -B phase5_unpack.py <folder of downloads> <downloads.csv> <source name> <licence> <evidence> <url pattern>

The folder holds one sub-folder per set, each with one .zip archive. Only
image files at the top level of an archive are unpacked (no folders, no other
file types); anything else is listed and left packed. One row per set is
written to the downloads table that phase5_licences.py reads. The url pattern
holds {name} where the archive's file name goes.
"""

import csv
import hashlib
import os
import sys
import zipfile

IMAGES = (".jpg", ".jpeg", ".png")


def unpack(folder):
    archives = [name for name in os.listdir(folder) if name.lower().endswith(".zip")]
    if len(archives) != 1:
        raise RuntimeError("%s: expected one archive, found %d" % (folder, len(archives)))
    path = os.path.join(folder, archives[0])
    with open(path, "rb") as handle:
        digest = hashlib.sha256(handle.read()).hexdigest()
    unpacked, left = [], []
    with zipfile.ZipFile(path) as archive:
        for item in archive.infolist():
            name = item.filename
            plain = os.path.basename(name) == name and ".." not in name and ":" not in name
            if plain and name.lower().endswith(IMAGES):
                with open(os.path.join(folder, name), "wb") as handle:
                    handle.write(archive.read(item))
                unpacked.append(name)
            else:
                left.append(name)
    size = sum(os.path.getsize(os.path.join(folder, name)) for name in os.listdir(folder))
    return archives[0], digest, unpacked, left, size


def main(root, out_csv, source, licence, evidence, url):
    rows = []
    for name in sorted(os.listdir(root)):
        folder = os.path.join(root, name)
        if not os.path.isdir(folder):
            continue
        archive, digest, unpacked, left, size = unpack(folder)
        print("%s: %d images unpacked, left packed: %s" % (name, len(unpacked), ", ".join(left) or "none"))
        rows.append({
            "name": name,
            "files": len(unpacked) + 1,
            "size_mb": "%.1f" % (size / 1048576.0),
            "what_it_is": "Surface image set %s, 2,048 pixels, JPEG" % name,
            "source": source + " " + url.replace("{name}", archive),
            "licence": licence,
            "evidence_or_note": "%s Archive SHA-256 %s." % (evidence, digest),
            "kept_at": folder,
        })
    with open(out_csv, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print("%d sets, %.1f MB in all, written to %s" % (
        len(rows), sum(float(row["size_mb"]) for row in rows), out_csv))


if __name__ == "__main__":
    main(*sys.argv[1:7])
