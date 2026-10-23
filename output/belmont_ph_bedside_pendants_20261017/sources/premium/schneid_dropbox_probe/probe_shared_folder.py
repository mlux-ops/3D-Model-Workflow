"""Bounded, read-only probe of manufacturer-published Schneid Dropbox share.

Queries the shared-folder HTML, limited to two MiB, and checks range support
against the ZIP endpoint. No ZIP content is retained or extracted.
"""

from __future__ import annotations

import html
import json
import re
import struct
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "OEM_SOURCE_MANIFEST.json"
MAX_HTML = 2 * 1024 * 1024
MAX_HTML_MATCHES = 30
MATCH = re.compile(r"(?i)(stucco|[\\w.-]{1,120}\\.(?:rfa|rvt|dwg|obj|fbx|skp|blend|3ds|max|stl|step|stp|glb|gltf|zip))")


def change_query(url: str, key: str, value: str) -> str:
    parsed = urlsplit(url)
    args = [(k, v) for k, v in parse_qsl(parsed.query) if k != key]
    args.append((key, value))
    return urlunsplit((parsed.scheme, parsed.netloc, parsed.path, urlencode(args), ""))


def get_request(url: str, *, method: str = "GET", byte_range: str | None = None):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept-Encoding": "identity",
    }
    if byte_range:
        headers["Range"] = byte_range
    return urlopen(Request(url, headers=headers, method=method), timeout=15)


def folder_html(url: str) -> dict:
    with get_request(change_query(url, "dl", "0")) as response:
        data = response.read(MAX_HTML + 1)
        meta = {
            "status": response.status,
            "content_type": response.headers.get("Content-Type"),
            "bytes_captured": len(data),
            "truncated": len(data) > MAX_HTML,
            "final_hostname": urlsplit(response.url).hostname,
        }
    page = html.unescape(data[:MAX_HTML].decode("utf-8", "replace"))
    snippets = []
    for m in MATCH.finditer(page):
        start, end = max(0, m.start() - 115), min(len(page), m.end() + 115)
        s = re.sub(r"\s+", " ", page[start:end]).strip()
        if s not in snippets:
            snippets.append(s)
        if len(snippets) == MAX_HTML_MATCHES:
            break
    meta["matches"] = snippets
    meta["other_markers"] = {
        keyword: page.lower().count(keyword.lower())
        for keyword in (
            "folder_root", "shared_link", "file_info", "filename", "file_name",
            "file_count", "download_button", "preload", "bootstrap", "Stucco",
            "STUCCO II", "STUCCO 2", "dropbox.com/sh/",
        )
    }
    meta["html_context"] = {}
    for keyword in ("file_count", "filename", "shared_link", "preview", "api/2", "scl/fo/"):
        contexts = []
        for match in list(re.finditer(re.escape(keyword), page, flags=re.IGNORECASE))[:3]:
            a, b = max(0, match.start() - 95), min(len(page), match.end() + 155)
            contexts.append(re.sub(r"\s+", " ", page[a:b]))
        meta["html_context"][keyword] = contexts
    return meta


def range_probe(url: str) -> dict:
    zipurl = change_query(url, "dl", "1")
    with get_request(zipurl, method="HEAD") as response:
        head = {
            "status": response.status,
            "length": response.headers.get("Content-Length"),
            "type": response.headers.get("Content-Type"),
            "final_hostname": urlsplit(response.url).hostname,
        }
        direct = response.url
    with get_request(direct, byte_range="bytes=-65536") as response:
        ranged = {
            "status": response.status,
            "length": response.headers.get("Content-Length"),
            "content_range": response.headers.get("Content-Range"),
            "accept_ranges": response.headers.get("Accept-Ranges"),
        }
        # Preserve no ZIP bytes: do not read response stream at all.
    return {"head": head, "range": ranged}


def first_zip_headers(url: str) -> dict:
    # A bounded prefix can identify leading ZIP member paths without consuming
    # archive payloads. Dropbox's download endpoint does not honor Range.
    with get_request(change_query(url, "dl", "1")) as response:
        data = response.read(1024 * 1024)
    entries = []
    offset = 0
    while offset + 30 <= len(data) and data[offset:offset + 4] == b"PK\x03\x04":
        fields = struct.unpack_from("<IHHHHHIIIHH", data, offset)
        _sig, _vers, flags, method, _time, _date, _crc, compressed, expanded, nl, xl = fields
        namebytes = data[offset + 30:offset + 30 + nl]
        name = namebytes.decode("utf-8" if flags & 0x800 else "cp437", "replace")
        entries.append({"name": name, "packed": compressed, "unpacked": expanded, "method": method, "flags": flags})
        if flags & 8:
            break
        offset += 30 + nl + xl + compressed
    return {"prefix_downloaded_bytes_discarded": len(data), "entries": entries,
            "parsing_stopped_at_offset": offset, "cap": 1024 * 1024}


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8-sig"))
    source = next(x for x in manifest if x["id"] == "schneid_stucco_dropbox_3d")
    result = {"source_id": source["id"], "source_url": change_query(source["url"], "dl", "0")}
    for section, action in (("html", folder_html), ("archive_probe", range_probe), ("first_zip_headers", first_zip_headers)):
        try:
            result[section] = action(source["url"])
        except Exception as exc:
            result[section] = {"error": f"{type(exc).__name__}: {exc}"}
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
