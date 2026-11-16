"""Phase 11, step 11.7: write MANIFEST_SHA256.txt inside a package folder: one line per file, "<SHA-256>  <bytes>  <path>",
paths relative to the package folder with forward slashes, sorted; the manifest itself is not listed.
The same lines can be checked on any computer with: certutil -hashfile <file> SHA256 (Windows) or sha256sum (others).
    python -B review/phase11/scripts/manifest.py <package folder>
"""
import hashlib
import os
import sys

root = sys.argv[1]
lines, total = [], 0
for base, dirs, files in os.walk(root):
    dirs.sort()
    for name in sorted(files):
        full = os.path.join(base, name)
        rel = os.path.relpath(full, root).replace(os.sep, "/")
        if rel == "MANIFEST_SHA256.txt":
            continue
        h = hashlib.sha256()
        with open(full, "rb") as handle:
            for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
                h.update(block)
        size = os.path.getsize(full)
        total += size
        lines.append("%s  %d  %s" % (h.hexdigest(), size, rel))
with open(os.path.join(root, "MANIFEST_SHA256.txt"), "w", encoding="utf-8", newline="\r\n") as handle:
    handle.write("# SHA-256  bytes  path (relative to this folder); %d files, %d bytes\n" % (len(lines), total))
    handle.write("\n".join(lines) + "\n")
print({"files": len(lines), "bytes": total})
