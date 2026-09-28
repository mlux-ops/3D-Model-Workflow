"""Probe MSI CDN paths for every Soreno Ivory image variant and download the ones that exist.

Writes references/<name> for each hit and _work/fetch_log.json with every probed URL and status.
"""
import json
import sys
import urllib.error
import urllib.request

from guard import out_path

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/128.0 Safari/537.36")
CDN = "https://cdn.msisurfaces.com/images/"

bases = ["soreno-ivory-porcelain", "soreno-ivory-porcelain-24x48", "soreno-ivory-porcelain-24x24",
         "soreno-ivory", "soreno-ivory-paver-24x48"]
folders = ["porcelainceramic/", "porcelainceramic/large/", "porcelainceramic/detail/",
           "porcelainceramic/variations/", "porcelainceramic/iso/", "colornames/detail/",
           "hardscaping/detail/", "hardscaping/variations/"]
suffixes = ["", "-01", "-02", "-03", "-04", "-05", "-06", "-variation", "-variation-01", "-variation-02",
            "-variation-03", "-variations", "-detail", "-detail-01", "-closeup", "-iso", "-large", "-hr",
            "-face-01", "-face-02", "-v1", "-v2", "-v3", "-a", "-b", "-c"]
extra = [
    "hardscaping/soreno-ivory-paver-24x48.jpg", "hardscaping/soreno-ivory-paver-24x24.jpg",
    "hardscaping/detail/soreno-ivory-paver-24x48.jpg", "hardscaping/detail/soreno-ivory-paver-24x24.jpg",
    "hardscaping/detail/soreno-ivory-arterra-porcelain-copings.jpg",
    "hardscaping/variations/soreno-ivory-paver-24x48-01.jpg",
    "hardscaping/variations/soreno-ivory-paver-24x48-02.jpg",
    "hardscaping/iso/soreno-ivory-paver-iso.jpg", "hardscaping/iso/soreno-ivory-paver-24x48-iso.jpg",
]


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Referer": "https://www.msisurfaces.com/"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            data = r.read()
            return r.status, r.headers.get("Content-Type", ""), data
    except urllib.error.HTTPError as e:
        return e.code, "", b""
    except Exception as e:  # noqa: BLE001  network errors are logged, not fatal
        return str(e), "", b""


def main():
    urls = []
    for f in folders:
        for b in bases:
            for s in suffixes:
                urls.append(CDN + f + b + s + ".jpg")
    urls += [CDN + e for e in extra]
    if len(sys.argv) > 1:
        urls = sys.argv[1:]
    log, hits, seen = [], [], set()
    for u in urls:
        st, ct, data = get(u)
        log.append({"url": u, "status": st, "type": ct, "bytes": len(data)})
        if st == 200 and data[:2] == b"\xff\xd8":
            h = hash(data)
            name = "msi_" + u.replace(CDN, "").replace("/", "__")
            if h in seen:
                log[-1]["duplicate_bytes"] = True
            seen.add(h)
            open(out_path("references/" + name), "wb").write(data)
            hits.append((u, len(data), name))
            print("HIT", u, len(data))
    json.dump(log, open(out_path("_work/fetch_log%s.json" % ("_extra" if len(sys.argv) > 1 else "")), "w"), indent=1)
    print(len(urls), "probed,", len(hits), "hits")


if __name__ == "__main__":
    main()
