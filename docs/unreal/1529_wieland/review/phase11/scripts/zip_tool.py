"""Phase 11, steps 11.7 and 11.9: make a zip with a manifest, and verify it.

    python -B zip_tool.py make <zip> <source folder> <top folder name inside the zip> [--only a,b,c] [--skip x,y]
    python -B zip_tool.py verify <zip> <manifest .json>
    python -B zip_tool.py sha256 <file>

make: walks the source folder (only the named top-level entries with --only; never the top-level names in --skip),
writes every file into the zip under <top folder>/<relative path> (Zip64, so files and zips over 4 GB are fine).
Files that are already compressed (pictures, video, packaged data) are stored; others are deflated. Writes
<zip>.manifest.json: for every file its path inside the zip, size and SHA-256 read from the source; then the zip's
own size and SHA-256.
verify: opens the zip again, checks that the entries are exactly those of the manifest with the same sizes, reads
every entry back and compares its SHA-256 with the manifest (this also checks the zip's own CRC of each entry), and
recomputes the zip's SHA-256. Exit code 0 only if everything matches.
"""
import hashlib
import json
import os
import sys
import time
import zipfile

STORED = {".png", ".jpg", ".jpeg", ".mp4", ".mov", ".zip", ".pak", ".utoc", ".ucas", ".exr", ".gz", ".7z", ".webm"}
CHUNK = 8 * 1024 * 1024


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as handle:
        while True:
            block = handle.read(CHUNK)
            if not block:
                break
            h.update(block)
    return h.hexdigest()


def make(zip_path, source, top, only=None, skip=None):
    entries = []
    for name in sorted(os.listdir(source)):
        if only and name not in only:
            continue
        if skip and name in skip:
            continue
        full = os.path.join(source, name)
        if os.path.isdir(full):
            for root, dirs, files in os.walk(full):
                dirs.sort()
                for f in sorted(files):
                    entries.append(os.path.join(root, f))
        else:
            entries.append(full)
    manifest = {"zip": zip_path, "source": source, "top": top, "made": time.strftime("%Y-%m-%d %H:%M:%S"), "files": []}
    started = time.time()
    total = 0
    with zipfile.ZipFile(zip_path, "w", allowZip64=True) as archive:
        for path in entries:
            rel = os.path.relpath(path, source).replace(os.sep, "/")
            arc = top + "/" + rel
            ext = os.path.splitext(path)[1].lower()
            method = zipfile.ZIP_STORED if ext in STORED else zipfile.ZIP_DEFLATED
            digest = sha256_file(path)
            size = os.path.getsize(path)
            archive.write(path, arc, compress_type=method, compresslevel=6 if method == zipfile.ZIP_DEFLATED else None)
            manifest["files"].append({"path": arc, "size": size, "sha256": digest})
            total += size
    manifest["file_count"] = len(manifest["files"])
    manifest["content_bytes"] = total
    manifest["zip_bytes"] = os.path.getsize(zip_path)
    manifest["zip_sha256"] = sha256_file(zip_path)
    manifest["seconds"] = round(time.time() - started)
    with open(zip_path + ".manifest.json", "w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=1)
    print(json.dumps({k: manifest[k] for k in ("zip", "file_count", "content_bytes", "zip_bytes", "zip_sha256", "seconds")}))


def verify(zip_path, manifest_path):
    with open(manifest_path, encoding="utf-8") as handle:
        manifest = json.load(handle)
    expected = {f["path"]: f for f in manifest["files"]}
    problems = []
    with zipfile.ZipFile(zip_path) as archive:
        infos = {i.filename: i for i in archive.infolist() if not i.is_dir()}
        for name in sorted(set(expected) - set(infos)):
            problems.append("missing in zip: " + name)
        for name in sorted(set(infos) - set(expected)):
            problems.append("not in manifest: " + name)
        for name, info in infos.items():
            if name not in expected:
                continue
            if info.file_size != expected[name]["size"]:
                problems.append("size differs: %s %d != %d" % (name, info.file_size, expected[name]["size"]))
                continue
            h = hashlib.sha256()
            with archive.open(info) as handle:  # reading to the end checks the entry's CRC as well
                while True:
                    block = handle.read(CHUNK)
                    if not block:
                        break
                    h.update(block)
            if h.hexdigest() != expected[name]["sha256"]:
                problems.append("content differs: " + name)
    size = os.path.getsize(zip_path)
    digest = sha256_file(zip_path)
    if size != manifest["zip_bytes"]:
        problems.append("zip size differs: %d != %d" % (size, manifest["zip_bytes"]))
    if digest != manifest["zip_sha256"]:
        problems.append("zip SHA-256 differs")
    result = {"zip": zip_path, "entries_checked": len(expected), "zip_bytes": size, "zip_sha256": digest,
              "problems": problems[:20], "problem_count": len(problems), "ok": not problems}
    print(json.dumps(result))
    return 0 if not problems else 1


if __name__ == "__main__":
    command = sys.argv[1]
    if command == "make":
        only = skip = None
        if "--only" in sys.argv:
            only = set(sys.argv[sys.argv.index("--only") + 1].split(","))
        if "--skip" in sys.argv:
            skip = set(sys.argv[sys.argv.index("--skip") + 1].split(","))
        make(sys.argv[2], sys.argv[3], sys.argv[4], only, skip)
    elif command == "verify":
        sys.exit(verify(sys.argv[2], sys.argv[3]))
    elif command == "sha256":
        print(sha256_file(sys.argv[2]))
