# -*- coding: utf-8 -*-
"""Low-level byte codec for Autodesk .adsklib DefinitionIteratorProperties.bin
and InstanceProperties.bin binary streams.

See FINDINGS.md in this directory for the full reverse-engineering writeup.

Key discovery: DefinitionIteratorProperties.bin (DIP) is written through a
paginated buffer that flushes every 272 bytes (at absolute stream offsets
== 152 mod 272), splicing in an out-of-band marker whenever a string's
content would straddle that boundary. Two marker shapes were observed:
  - plain "local" string fields (UIName, description, ...): fixed 8-byte
    marker `02 00 00 00 80 00 00 00`, not counted in the field's declared
    length.
  - "adp:?asset=/..." internal asset-URI fields (thumbnail): marker
    `FF FF FF FF` + int32(len(remaining bytes)), also not counted in the
    field's declared length.

InstanceProperties.bin (IP) external bitmap file-path URIs use a different,
RELATIVE mechanism: the string is always split at a FIXED CHARACTER OFFSET
counted from the *start of that field's own content* (90 for the first
texture connection encountered in the file, 91 for the second), regardless
of the string's total length or absolute file position. The marker is
`FF FF FF FF` + int32(len(remaining bytes) + 37). The "+37" constant was
empirically derived from six independent samples (2 connections x 3
reference libraries) and its root cause is not understood -- see
FINDINGS.md.
"""
import struct

PAGE_MOD = 272
PAGE_PHASE = 152

PLAIN_MARKER = bytes.fromhex('0200000080000000')
BITMAP_PATH_K = 37


def next_boundary(pos: int) -> int:
    """Smallest b >= pos such that b % PAGE_MOD == PAGE_PHASE."""
    r = (PAGE_PHASE - pos) % PAGE_MOD
    return pos + r


def _next_boundary_gapped(pos: int, start_pos: int, min_gap: int) -> int:
    """Like next_boundary(pos), but never returns a crossing point closer
    than `min_gap` bytes to `start_pos` -- used so a freshly-synthesized
    field's own fixed literal prefix (e.g. "adp:?asset=/", used as a search
    anchor by our own extractor) never gets split by an injected marker.
    All 6 real-library samples we measured this rule against had their
    marker at >=19 bytes in, so this is a conservative, evidence-consistent
    floor, not an invented one."""
    b = next_boundary(pos)
    while b - start_pos < min_gap:
        b = next_boundary(b + 1)
    return b


def _paginate(start_pos: int, content: bytes, marker_fn, min_gap: int = 0) -> bytes:
    """Split `content` (whose first byte sits at absolute position
    `start_pos`) at every page boundary crossed, inserting marker_fn(remaining)
    bytes at each crossing. marker_fn bytes do not count toward the caller's
    declared length and do not themselves get re-scanned for boundaries."""
    out = bytearray()
    pos = start_pos
    remaining = content
    while True:
        b = _next_boundary_gapped(pos, start_pos, min_gap) if min_gap else next_boundary(pos)
        if b >= pos + len(remaining):
            out += remaining
            break
        cut = b - pos
        out += remaining[:cut]
        remaining = remaining[cut:]
        marker = marker_fn(remaining)
        out += marker
        pos = b + len(marker)
    return bytes(out)


def encode_plain_field(start_pos: int, content: bytes) -> bytes:
    """DIP plain 'local' string field: 4-byte length (real content length,
    excluding any injected marker bytes) + paginated content."""
    body = _paginate(start_pos + 4, content, lambda rem: PLAIN_MARKER)
    return struct.pack('<i', len(content)) + body


URI_MIN_GAP = 12  # len("adp:?asset=/") -- never split inside our own search anchor


def encode_uri_field_dip(start_pos: int, content: bytes) -> bytes:
    """DIP 'adp:?asset=/...' internal asset-URI field."""
    def marker_fn(rem):
        return b'\xff\xff\xff\xff' + struct.pack('<i', len(rem))
    body = _paginate(start_pos + 4, content, marker_fn, min_gap=URI_MIN_GAP)
    return struct.pack('<i', len(content)) + body


def encode_bitmap_path(content: bytes, char_split: int, k=BITMAP_PATH_K) -> bytes:
    """IP external bitmap file-path field. `char_split` is 90 for the first
    texture connection encountered in the stream (generic_bump_map in our
    reference materials), 91 for the second (generic_diffuse)."""
    L = len(content)
    if L <= char_split:
        return struct.pack('<i', L) + content
    chunk1 = content[:char_split]
    chunk2 = content[char_split:]
    return (struct.pack('<i', L) + chunk1 + b'\xff\xff\xff\xff' +
            struct.pack('<i', len(chunk2) + k) + chunk2)


def decode_plain_field(buf: bytes, start_pos: int, min_gap: int = 0):
    """Inverse of encode_plain_field / encode_uri_field_dip. Returns
    (content_bytes, end_pos). `min_gap` must match whatever the field was
    encoded with (0 for plain fields, URI_MIN_GAP for uri fields)."""
    L = struct.unpack_from('<i', buf, start_pos)[0]
    content_start = start_pos + 4
    pos = content_start
    out = bytearray()
    while len(out) < L:
        b = (_next_boundary_gapped(pos, content_start, min_gap) if min_gap
             else next_boundary(pos))
        take = min(b - pos, L - len(out))
        out += buf[pos:pos + take]
        pos += take
        if len(out) < L and pos == b:
            # a marker sits here; skip it
            if buf[pos:pos + 4] == b'\xff\xff\xff\xff':
                pos += 8  # FF FF FF FF + int32 remaining-len
            else:
                pos += 8  # fixed 8-byte plain marker
    return bytes(out), pos


def decode_uri_field(buf: bytes, start_pos: int):
    """DIP 'adp:?asset=/...' internal asset-URI field (inverse of
    encode_uri_field_dip)."""
    return decode_plain_field(buf, start_pos, min_gap=URI_MIN_GAP)


def decode_bitmap_path(buf: bytes, start_pos: int, k=BITMAP_PATH_K):
    """Inverse of encode_bitmap_path. Returns (content_bytes, end_pos)."""
    L = struct.unpack_from('<i', buf, start_pos)[0]
    pos = start_pos + 4
    ff = buf.find(b'\xff\xff\xff\xff', pos, pos + L + 8)
    if ff == -1 or ff - pos >= L:
        content = buf[pos:pos + L]
        return content, pos + L
    chunk1 = buf[pos:ff]
    L2 = struct.unpack_from('<i', buf, ff + 4)[0]
    chunk2_len = L2 - k
    chunk2_start = ff + 8
    chunk2 = buf[chunk2_start:chunk2_start + chunk2_len]
    content = chunk1 + chunk2
    assert len(content) == L, (len(content), L)
    return content, chunk2_start + chunk2_len
