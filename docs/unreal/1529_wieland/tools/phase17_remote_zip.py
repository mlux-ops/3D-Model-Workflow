"""Phase 17: read single members out of the ISGS Cook County 2022 LAS zips without downloading them whole.

The state serves the 2022 point cloud only as five zip files of 0.74 to 0.98 TB each
(https://chf.isgs.illinois.edu/distribute/district1/cook/2022/cook-las1.zip ... cook-las5.zip).
The server accepts HTTP range requests, so Python's zipfile can read the central directory and
one member at a time through a file-like object that fetches only the bytes asked for.

Usage:
    python -I phase17_remote_zip.py list <part 1-5> <out csv>
    python -I phase17_remote_zip.py get <part 1-5> <member name> <out folder>

Standard library only.
"""

import csv
import os
import shutil
import sys
import time
import urllib.request
import zipfile

BASE = "https://chf.isgs.illinois.edu/distribute/district1/cook/2022/cook-las%d.zip"
UA = "Wieland1529-site-model/1.0 (private architectural visualisation; contact info@shb.studio)"


class RangeFile:
    """Read-only, seekable file over HTTP range requests, with a small read-ahead buffer."""

    def __init__(self, url, block=1 << 20):
        self.url = url
        self.pos = 0
        self.block = block
        self.buf_start = -1
        self.buf = b""
        request = urllib.request.Request(url, method="HEAD", headers={"User-Agent": UA})
        with urllib.request.urlopen(request, timeout=60) as response:
            self.size = int(response.headers["Content-Length"])
        self.fetched = 0

    def _get(self, start, end):
        for attempt in range(6):
            try:
                request = urllib.request.Request(self.url, headers={"User-Agent": UA, "Range": "bytes=%d-%d" % (start, end - 1)})
                with urllib.request.urlopen(request, timeout=120) as response:
                    data = response.read()
                self.fetched += len(data)
                return data
            except Exception:
                if attempt == 5:
                    raise
                time.sleep(3 * (attempt + 1))

    def seekable(self):
        return True

    def readable(self):
        return True

    def tell(self):
        return self.pos

    def seek(self, offset, whence=0):
        if whence == 0:
            self.pos = offset
        elif whence == 1:
            self.pos += offset
        else:
            self.pos = self.size + offset
        return self.pos

    def read(self, n=-1):
        if n is None or n < 0:
            n = self.size - self.pos
        n = min(n, self.size - self.pos)
        if n <= 0:
            return b""
        if self.buf_start <= self.pos and self.pos + n <= self.buf_start + len(self.buf):
            i = self.pos - self.buf_start
            data = self.buf[i:i + n]
        elif n >= self.block:
            data = self._get(self.pos, self.pos + n)
        else:
            end = min(self.size, self.pos + max(n, self.block))
            self.buf = self._get(self.pos, end)
            self.buf_start = self.pos
            data = self.buf[:n]
        self.pos += len(data)
        return data

    def close(self):
        pass


def open_part(part):
    return zipfile.ZipFile(RangeFile(BASE % part))


def main(argv):
    mode, part = argv[1], int(argv[2])
    archive = open_part(part)
    if mode == "list":
        with open(argv[3], "w", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(["part", "name", "compressed_bytes", "bytes", "method"])
            for info in archive.infolist():
                writer.writerow([part, info.filename, info.compress_size, info.file_size, info.compress_type])
        print("listed", len(archive.infolist()), "members of part", part)
        return 0
    if mode == "get":
        name, folder = argv[3], argv[4]
        target = os.path.join(folder, os.path.basename(name))
        if os.path.exists(target) and os.path.getsize(target) == archive.getinfo(name).file_size:
            print("exists", target)
            return 0
        partial = target + ".partial"
        with archive.open(name) as source, open(partial, "wb") as out:
            shutil.copyfileobj(source, out, 1 << 22)
        os.replace(partial, target)
        print("got", target, os.path.getsize(target))
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
