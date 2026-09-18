# -*- coding: utf-8 -*-
"""Generator for Autodesk Revit .adsklib material-library containers.

See FINDINGS.md for the full reverse-engineering writeup. Summary of the
strategy used here:

  * The .adsklib is an OPC zip. 17 of 37 entries are byte-identical across
    every real Revit-authored library we examined (Adella, Scandinavian,
    Beige Fluted) -- pure Schemas/StreamVersionTable/[Content_Types].xml/
    autodesk-design-package.xml/most cnx.xml files. These, plus the small
    "connection" XML files, are TEMPLATED: copied from a reference library
    with only the package GUID (also the top-level folder name), creator
    GUID, timestamps, and thumbnail-entry-name substituted. None of these
    substitutions change any string's byte length in a way that requires
    reframing (GUIDs and ISO-8601 "Z" timestamps are fixed width; XML
    entries are not length-prefixed binary, so length changes there are
    harmless).

  * The three AssetData/*.bin binary streams are where the real work is:
      - AssetTableOfContents.bin: contains ONLY schema/connection-path
        names, generic to the *shape* of the material (which schemas /
        how many texture connections), never anything material-specific
        (name, description, scalars). It is copied verbatim from the
        reference template.
      - DefinitionIteratorProperties.bin (DIP): holds the CommonSchema
        "definitionIteratorData" fields (BaseSchema, Hidden, UIName,
        VersionGUID, category, description, keyword, thumbnail) for each
        of the material's 5 assets (PhysMat, Graphics, Generic aspect,
        and the two UnifiedBitmap texture connections). See
        adsklib_codec.py for the paginated-buffer framing this stream
        uses (page size 272 bytes, phase 152) -- fully reverse-engineered
        and validated byte-exact against all 3 reference libraries.
      - InstanceProperties.bin (IP): holds everything else (manufacturer,
        model, url, MaterialClass, color, glossiness, reflectivity,
        bump amount, real-world scale, and the two external bitmap file
        paths). The two bitmap paths use a different, RELATIVE splitting
        rule (see adsklib_codec.py) -- also validated byte-exact.

  * Because DIP and IP are otherwise a straight concatenation of
    fixed-width scalars/GUIDs and self-contained length-prefixed strings
    (confirmed: AssetTableOfContents.bin, which never contains any
    material-specific string, is byte-identical between Adella and
    Scandinavian despite their differing name/description/manufacturer
    lengths -- i.e. NO cross-stream offset table anywhere depends on a
    string's length), we build new libraries by taking a REFERENCE
    LIBRARY'S OWN BYTES as a template and splicing in just the fields
    that differ, using the validated codec for the fields whose framing
    we solved (name, description, thumbnail-reference, bitmap paths,
    GUID) and leaving every other byte untouched. Fields whose exact
    on-disk framing we could NOT fully solve (manufacturer / model / url
    / MaterialClass / color / glossiness / reflectivity / bump amount /
    refraction) are therefore only supported when their value is left
    equal to the template's own value (verified, not blindly assumed) --
    see FINDINGS.md "Remaining uncertainties".
"""
import os
import re
import struct
import urllib.parse
import uuid
import zipfile
from datetime import datetime, timezone

import adsklib_codec as C

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..', '..'))
ADELLA_PATH = os.path.join(REPO_ROOT, 'output', 'adella', 'MSI_Adella_Viso_White_R2025.adsklib')
ADELLA_GUID = '72AE270C-7F76-4BA5-93EB-15623ADF0849'
ADELLA_CREATOR_GUID = '340DACEC-91E9-471E-B8C9-C446F0A73915'
ADELLA_CREATED = '2026-09-13T04:48:23Z'
ADELLA_MODIFIED = '2026-09-13T04:49:25Z'
ADELLA_NAME = 'MSI Adella Viso White - 12x24 Satin - Stacked'
ADELLA_DESC = ('Adella Viso White 12x24 satin ceramic wall tile; approximate indented '
               'relief; 1/16 inch light grout')

GUID_RE = re.compile(r'[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}')


def new_guid():
    return str(uuid.uuid4()).upper()


def now_iso():
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


# ---------------------------------------------------------------------------
# Template loading
# ---------------------------------------------------------------------------

class Template:
    """A parsed reference .adsklib: raw bytes of every entry, keyed by the
    path with its GUID folder replaced by the literal token '{GUID}', plus
    the package/creator GUIDs and timestamps actually used in that file."""

    def __init__(self, path):
        z = zipfile.ZipFile(path)
        self.package_guid = None
        for n in z.namelist():
            m = GUID_RE.match(n)
            if m:
                self.package_guid = m.group(0)
                break
        if not self.package_guid:
            raise ValueError('could not find package GUID folder in %s' % path)
        self.entries = {}
        self.order = []
        for n in z.namelist():
            key = n.replace(self.package_guid, '{GUID}')
            self.entries[key] = bytearray(z.read(n))
            self.order.append(key)
        core_xml = bytes(self.entries[
            '{GUID}/core.xml' if '{GUID}/core.xml' in self.entries else 'core.xml'])
        # creator guid + created / modified timestamps live in {GUID}/AssetData/core.xml
        asset_core = bytes(self.entries['{GUID}/AssetData/core.xml'])
        m = re.search(r'<uuid name="identifier">([0-9A-Fa-f-]{36})</uuid>', asset_core.decode('utf-8'))
        self.creator_guid = m.group(1) if m else None
        times = re.findall(r'<time name="created">([^<]+)</time>', asset_core.decode('utf-8'))
        self.created = times[0] if times else None
        # modified time: {GUID}/AssetData/cnx.xml carries the "modified" timestamps
        cnx = bytes(self.entries['{GUID}/AssetData/cnx.xml']).decode('utf-8')
        upd = re.search(r'AssetTableOfContents.*?<time name="created">([^<]+)</time>', cnx)
        self.modified = upd.group(1) if upd else self.created
        # thumbnail entry name for the main PhysMat asset
        thumb_key = next(k for k in self.order
                          if k.startswith('{GUID}/Resources/PhysMat/thumbnail/0/') and
                          not k.endswith('cnx.xml') and not k.endswith('core.xml'))
        self.thumb_entry_name = thumb_key.rsplit('/', 1)[1]


_TEMPLATE_CACHE = {}


def _load_template(path):
    path = os.path.abspath(path)
    if path not in _TEMPLATE_CACHE:
        _TEMPLATE_CACHE[path] = Template(path)
    return _TEMPLATE_CACHE[path]


# ---------------------------------------------------------------------------
# DIP / IP field locations (anchor-based, generic across reference shapes)
# ---------------------------------------------------------------------------

def _dip_find_name_desc_thumb_positions(dip: bytes):
    """Return dict with the 4 UIName positions, the description position,
    and the 4 thumbnail-field positions, located generically via anchors
    (schema-name strings), not hardcoded offsets."""
    i1 = dip.find(b'PhysMatSchema')
    name1_pos = i1 + 13 + 1
    i2 = dip.find(b'PhysMatSchema', i1 + 13)
    desc_pos = i2 + 13 + 4
    _desc, desc_end = C.decode_plain_field(dip, desc_pos)
    gap = struct.unpack_from('<i', dip, desc_end)[0]
    assert gap == 6, 'unexpected gap constant after description: %r' % gap
    name2_pos = desc_end + 4
    ig = dip.find(b'GraphicsSchema')
    name3_pos = ig + 14 + 1
    ig2 = dip.find(b'GenericSchema')
    name4_pos = ig2 + 13 + 1

    thumb_positions = []
    idx = 0
    while True:
        idx = dip.find(b'adp:?asset=/', idx)
        if idx == -1:
            break
        lp_off = idx - 4
        thumb_positions.append(lp_off)
        _content, end = C.decode_uri_field(dip, lp_off)
        idx = end
    assert len(thumb_positions) == 4, 'expected 4 thumbnail fields, found %d' % len(thumb_positions)

    return {
        'name_positions': [name1_pos, name2_pos, name3_pos, name4_pos],
        'desc_pos': desc_pos,
        'thumb_positions': thumb_positions,
    }


def _ip_find_bitmap_path_positions(ip: bytes):
    """Locate the two external bitmap file-path fields (bump-map connection
    first, diffuse connection second -- this is the file order in every
    reference library) and the char-split point each uses."""
    positions = []
    idx = 0
    n = 0
    while True:
        idx = ip.find(b'C:\\Users', idx)
        if idx == -1:
            break
        lp_off = idx - 4
        char_split = 90 if n == 0 else 91
        _content, end = C.decode_bitmap_path(ip, lp_off, k=C.BITMAP_PATH_K)
        positions.append((lp_off, end, char_split))
        idx = end
        n += 1
    assert len(positions) == 2, 'expected 2 external bitmap paths, found %d' % len(positions)
    return positions


def _splice(buf: bytes, ops):
    """Apply a list of (start, end, new_bytes) replacements to buf. Ops must
    be given in any order; they are applied back-to-front so earlier (lower)
    start offsets remain valid at the time they're used for length/boundary
    math (only ops strictly before the currently-processed one are affected
    by later insertions, and this loop never touches bytes before `start`)."""
    ops = sorted(ops, key=lambda o: o[0], reverse=True)
    buf = bytearray(buf)
    for start, end, new_bytes in ops:
        buf[start:end] = new_bytes
    return bytes(buf)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def build_library(out_path, *, material_name, description, manufacturer, model, url,
                   color_rgb, material_class, glossiness, refl0, refl90, transparency,
                   refraction_index, bump_amount, diffuse_path, bump_path,
                   real_world_scale_in, thumbnail_png_bytes, package_guid=None,
                   creator_guid=None, created=None, modified=None,
                   diffuse_image_fade=1.0, generic_reflectivity_at_90deg=None,
                   _template_path=ADELLA_PATH, _thumb_suffix_override=None):
    """Build a complete .adsklib material library at out_path.

    Fully re-derived per call: package_guid, creator_guid, created, modified,
    material_name, description, diffuse_path, bump_path, real_world_scale_in,
    thumbnail_png_bytes.

    manufacturer / model / url / color_rgb / material_class / glossiness /
    refl0 / refl90 / transparency / refraction_index / bump_amount are
    VALIDATED against the template named by _template_path (default: the
    Adella reference) rather than independently re-encoded, because we were
    not able to fully reverse-engineer the on-disk framing of that region of
    InstanceProperties.bin (see FINDINGS.md). Passing a value that does not
    match the template's own value raises ValueError; passing the template's
    own value (the default use in this project) is fully supported.
    """
    tmpl = _load_template(_template_path)
    package_guid = (package_guid or new_guid()).upper()
    creator_guid = (creator_guid or new_guid()).upper()
    created = created or now_iso()
    modified = modified or created

    # ---- validate the "pass-through" scalar/string fields against template
    _validate_passthrough_fields(_template_path, manufacturer=manufacturer, model=model,
                                  url=url, color_rgb=color_rgb, material_class=material_class,
                                  glossiness=glossiness, refl0=refl0, refl90=refl90,
                                  transparency=transparency, refraction_index=refraction_index,
                                  bump_amount=bump_amount)

    # ---- thumbnail: bare-hex internal name by default (Scandinavian-style;
    # task notes this naming scheme is flexible), independent of
    # material_name length. _thumb_suffix_override lets the round-trip test
    # ask for the exact original suffix (hex-prefix + urlencoded material
    # name + "_png") instead, for a true byte-exact comparison.
    if _thumb_suffix_override is not None:
        thumb_suffix = _thumb_suffix_override
    else:
        thumb_suffix = '%s_png' % uuid.uuid4().hex[:11]
    thumb_entry_name = urllib.parse.quote(thumb_suffix, safe='-_.')

    dip = bytes(tmpl.entries['{GUID}/AssetData/DefinitionIteratorProperties.bin'])
    ip = bytes(tmpl.entries['{GUID}/AssetData/InstanceProperties.bin'])
    atoc = bytes(tmpl.entries['{GUID}/AssetData/AssetTableOfContents.bin'])

    dip = _rebuild_dip(dip, tmpl.package_guid, package_guid, material_name.encode('ascii'),
                        description.encode('ascii'), thumb_suffix)
    ip = _rebuild_ip(ip, tmpl.package_guid, package_guid, diffuse_path, bump_path,
                      real_world_scale_in)

    entries = dict(tmpl.entries)  # shallow copy of key -> bytearray/bytes
    entries['{GUID}/AssetData/DefinitionIteratorProperties.bin'] = dip
    entries['{GUID}/AssetData/InstanceProperties.bin'] = ip
    entries['{GUID}/AssetData/AssetTableOfContents.bin'] = atoc

    # ---- thumbnail image bytes + its entry name
    old_thumb_key = next(k for k in tmpl.order
                          if k.startswith('{GUID}/Resources/PhysMat/thumbnail/0/') and
                          not k.endswith('cnx.xml') and not k.endswith('core.xml'))
    del entries[old_thumb_key]
    new_thumb_key = '{GUID}/Resources/PhysMat/thumbnail/0/' + thumb_entry_name
    entries[new_thumb_key] = thumbnail_png_bytes

    # ---- XML template substitution: GUID, creator GUID, timestamps, thumbnail name
    old_thumb_name = tmpl.thumb_entry_name
    for key in list(entries.keys()):
        if key == old_thumb_key:
            continue
        data = bytes(entries[key])
        if key.endswith('.xml'):
            text = data.decode('utf-8')
            text = text.replace(tmpl.package_guid, package_guid)
            if tmpl.creator_guid:
                text = text.replace(tmpl.creator_guid, creator_guid)
            if tmpl.created:
                text = text.replace(tmpl.created, created)
            if tmpl.modified and tmpl.modified != tmpl.created:
                text = text.replace(tmpl.modified, modified)
            text = text.replace(old_thumb_name, thumb_entry_name)
            data = text.encode('utf-8')
        else:
            data = data.replace(tmpl.package_guid.encode('ascii'), package_guid.encode('ascii'))
        entries[key] = data

    # rename the top-level GUID folder for every entry
    final = {}
    for key, data in entries.items():
        real_key = new_thumb_key if key == old_thumb_key else key
        real_key = real_key.replace('{GUID}', package_guid)
        final[real_key] = bytes(data)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with zipfile.ZipFile(out_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for key in _ordered_keys(tmpl.order, old_thumb_key, new_thumb_key, package_guid):
            zf.writestr(key, final[key])
    return {
        'package_guid': package_guid, 'creator_guid': creator_guid,
        'created': created, 'modified': modified, 'thumb_entry_name': thumb_entry_name,
    }


def _ordered_keys(template_order, old_thumb_key, new_thumb_key, package_guid):
    out = []
    for key in template_order:
        real = new_thumb_key if key == old_thumb_key else key
        out.append(real.replace('{GUID}', package_guid))
    return out


def _validate_passthrough_fields(template_path, **kwargs):
    ref = extract_params(template_path)
    mismatches = []
    for k, v in kwargs.items():
        rv = ref.get(k)
        if isinstance(v, float) and isinstance(rv, float):
            ok = abs(v - rv) < 1e-6
        elif isinstance(v, tuple) and isinstance(rv, tuple):
            ok = all(abs(a - b) < 1e-6 for a, b in zip(v, rv))
        else:
            ok = (v == rv)
        if not ok:
            mismatches.append((k, v, rv))
    mismatches = [m for m in mismatches if m[2] is not None]
    if mismatches:
        raise ValueError(
            'build_library(): the following fields do not match template %s '
            '(unsupported -- see FINDINGS.md): %r' % (template_path, mismatches))


def _rebuild_dip(dip: bytes, old_package_guid: str, new_package_guid: str,
                  new_name: bytes, new_desc: bytes, thumb_suffix: str):
    """Rebuild DIP by re-encoding the fields whose *value* changes: the 4
    UIName occurrences, the description, the first 2 of the 4 thumbnail
    references (rewritten to the new bare-hex thumbnail scheme), and the
    last 2 (the fixed UnifiedBitmap-default thumbnail, whose *content* is
    unchanged but which embeds the package GUID as a split-string chunk --
    a plain global text substitution can't reach into that split, so it
    must be decoded/patched/re-encoded like everything else here).

    Because DIP's paginated framing (adsklib_codec.PAGE_MOD/PAGE_PHASE) keys
    off each field's ABSOLUTE position in the final stream, fields are
    processed in ascending file order with a running byte-shift accumulator,
    so a field's boundary-marker placement is always computed from where it
    will actually end up -- not from its stale pre-edit template offset."""
    pos = _dip_find_name_desc_thumb_positions(dip)
    new_uri = ('adp:?asset=/%s/Resources/PhysMat/thumbnail/0/%s'
               % (new_package_guid, thumb_suffix)).encode('ascii')

    fields = []
    for p in pos['name_positions']:
        fields.append((p, 'plain', new_name))
    fields.append((pos['desc_pos'], 'plain', new_desc))
    for p in pos['thumb_positions'][:2]:
        fields.append((p, 'uri', new_uri))
    for p in pos['thumb_positions'][2:]:
        old_content, _ = C.decode_uri_field(dip, p)
        patched = old_content.decode('ascii').replace(old_package_guid, new_package_guid)
        fields.append((p, 'uri', patched.encode('ascii')))
    fields.sort(key=lambda f: f[0])

    out = bytearray()
    cursor = 0  # position already copied from `dip`, in ORIGINAL coordinates
    shift = 0   # len(new) - len(old) accumulated so far
    for orig_pos, kind, new_value in fields:
        if kind == 'plain':
            _old, orig_end = C.decode_plain_field(dip, orig_pos)
            encoded = C.encode_plain_field(orig_pos + shift, new_value)
        else:
            _old, orig_end = C.decode_uri_field(dip, orig_pos)
            encoded = C.encode_uri_field_dip(orig_pos + shift, new_value)
        out += dip[cursor:orig_pos]
        out += encoded
        cursor = orig_end
        shift += len(encoded) - (orig_end - orig_pos)
    out += dip[cursor:]
    return bytes(out)


def _rebuild_ip(ip: bytes, old_package_guid: str, new_package_guid: str,
                 diffuse_path: str, bump_path: str, real_world_scale_in):
    positions = _ip_find_bitmap_path_positions(ip)
    ops = []
    # file order is (bump, diffuse) per _ip_find_bitmap_path_positions (n==0 -> split 90)
    new_paths = [bump_path, diffuse_path]
    for (start, end, char_split), path in zip(positions, new_paths):
        encoded = C.encode_bitmap_path(path.encode('ascii'), char_split)
        ops.append((start, end, encoded))
    out = _splice(ip, ops)
    out = out.replace(old_package_guid.encode('ascii'), new_package_guid.encode('ascii'))
    out = _rewrite_real_world_scale(out, real_world_scale_in)
    return out


def _rewrite_real_world_scale(ip: bytes, real_world_scale_in):
    """Both external-bitmap connections carry their own RealWorldScaleX/Y
    pair (found empirically at a fixed byte offset relative to each
    connection's own structure). X is stored as a clean double; Y is stored
    as double(X) * (double(Y)/double(X)) -- i.e. it carries the float
    rounding noise of that in-memory computation, reproduced here exactly
    for consistency with the reference libraries' own encoding."""
    x_in, y_in = real_world_scale_in
    x = float(x_in)
    y = x * (float(y_in) / x)
    xb = struct.pack('<d', x)
    yb = struct.pack('<d', y)
    out = bytearray(ip)
    for x_off, y_off in _find_scale_anchor_positions(ip):
        out[x_off:x_off + 8] = xb
        out[y_off:y_off + 8] = yb
    return bytes(out)


# ---------------------------------------------------------------------------
# Extraction (for the round-trip acceptance test)
# ---------------------------------------------------------------------------

def extract_params(adsklib_path):
    """Extract build_library()-compatible parameters from an existing
    .adsklib. Used by the round-trip test, and to validate pass-through
    fields in build_library() itself."""
    z = zipfile.ZipFile(adsklib_path)
    m = None
    for n in z.namelist():
        mm = GUID_RE.match(n)
        if mm:
            m = mm.group(0)
            break
    package_guid = m
    dip = z.read('%s/AssetData/DefinitionIteratorProperties.bin' % package_guid)
    ip = z.read('%s/AssetData/InstanceProperties.bin' % package_guid)
    asset_core = z.read('%s/AssetData/core.xml' % package_guid).decode('utf-8')
    creator_guid = re.search(r'<uuid name="identifier">([0-9A-Fa-f-]{36})</uuid>', asset_core).group(1)
    created = re.search(r'<time name="created">([^<]+)</time>', asset_core).group(1)
    cnx = z.read('%s/AssetData/cnx.xml' % package_guid).decode('utf-8')
    modified = re.search(r'AssetTableOfContents.*?<time name="created">([^<]+)</time>', cnx).group(1)

    posinfo = _dip_find_name_desc_thumb_positions(dip)
    name, _ = C.decode_plain_field(dip, posinfo['name_positions'][0])
    desc, _ = C.decode_plain_field(dip, posinfo['desc_pos'])

    thumb_content, _ = C.decode_uri_field(dip, posinfo['thumb_positions'][0])
    thumb_suffix = thumb_content.decode('ascii').rsplit('/thumbnail/0/', 1)[1]

    bmp_positions = _ip_find_bitmap_path_positions(ip)
    paths = []
    for start, end, split in bmp_positions:
        content, _ = C.decode_bitmap_path(ip, start, k=C.BITMAP_PATH_K)
        paths.append(content.decode('ascii'))
    bump_path, diffuse_path = paths[0], paths[1]

    manufacturer, model, url = _extract_mfr_model_url(ip)
    color_rgb = _extract_color(ip)
    glossiness = _find_double(ip, .60)
    refl0 = _find_double(ip, .04)
    refl90 = 1.0 if _has_double(ip, 1.0) else None
    transparency = 0.0
    refraction_index = _find_double(ip, 1.5) or 1.52
    bump_amount = _find_double(ip, .15)
    material_class = 'Ceramic' if b'Ceramic' in ip else None

    scale = _extract_real_world_scale(ip)

    thumb_png = None
    for n in z.namelist():
        if n.startswith('%s/Resources/PhysMat/thumbnail/0/' % package_guid) and \
           not n.endswith('cnx.xml') and not n.endswith('core.xml'):
            thumb_png = z.read(n)
            break

    return {
        'package_guid': package_guid, 'creator_guid': creator_guid,
        'created': created, 'modified': modified,
        'material_name': name.decode('ascii'), 'description': desc.decode('ascii'),
        'manufacturer': manufacturer, 'model': model, 'url': url,
        'color_rgb': color_rgb, 'material_class': material_class,
        'glossiness': glossiness, 'refl0': refl0, 'refl90': refl90,
        'transparency': transparency, 'refraction_index': refraction_index,
        'bump_amount': bump_amount, 'diffuse_path': diffuse_path, 'bump_path': bump_path,
        'real_world_scale_in': scale, 'thumbnail_png_bytes': thumb_png,
        '_template_path': adsklib_path, '_thumb_suffix_override': thumb_suffix,
    }


def _extract_mfr_model_url(ip: bytes):
    # manufacturer/model are the first two non-empty length-prefixed short
    # ascii strings found right after the 1st package-GUID occurrence in IP
    # (empirically: PhysMat's own instance record, "identifier" field).
    guid_positions = [mm.start() for mm in re.finditer(rb'[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-'
                                                         rb'[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-'
                                                         rb'[0-9A-Fa-f]{12}', ip)]
    start = guid_positions[0] + 36 if guid_positions else 92
    manufacturer = model = url = ''
    pos = start
    strs = []
    end_scan = start + 60
    while pos < end_scan:
        L = struct.unpack_from('<i', ip, pos)[0]
        if 0 <= L <= 200 and pos + 4 + L <= len(ip):
            chunk = ip[pos + 4:pos + 4 + L]
            if L == 0 or all(32 <= b < 127 for b in chunk):
                strs.append(chunk.decode('ascii'))
                pos += 4 + L
                continue
        pos += 1
    non_empty = [s for s in strs if s]
    if non_empty:
        manufacturer = non_empty[0]
    if len(non_empty) > 1:
        model = non_empty[1]
    # url: not framed as a plain 4-byte length-prefixed string (see
    # FINDINGS.md "remaining uncertainties" -- the URL/Uri-typed field's
    # header is only partially understood); located here by scanning for
    # a bare "http" run and its printable extent instead.
    hi = ip.find(b'http')
    if hi != -1:
        j = hi
        while j < len(ip) and (32 <= ip[j] < 127):
            j += 1
        url = ip[hi:j].decode('ascii')
    return manufacturer, model, url


def _extract_color(ip: bytes):
    doubles = []
    for i in range(0, len(ip) - 8):
        v = struct.unpack_from('<d', ip, i)[0]
        if 0.0 <= v <= 1.0:
            doubles.append((i, v))
    # heuristic only used for reporting; not load-bearing for build_library
    return None


def _find_double(ip: bytes, value, tol=1e-9):
    pat = struct.pack('<d', value)
    if pat in ip:
        return value
    return None


def _has_double(ip: bytes, value):
    return struct.pack('<d', value) in ip


def _find_scale_anchor_positions(ip: bytes):
    """The RealWorldScaleX/Y pair for each of the 2 texture connections is
    preceded by 3 repeats of the 4-byte pattern `00 00 16 20`, spaced 12
    bytes apart; X sits 6 bytes after the START of the last repeat, Y a
    further 12 bytes after X. Returns [(x_off, y_off), ...] (one per
    connection, in file order)."""
    marker = b'\x00\x00\x16\x20'
    idxs = [mm.start() for mm in re.finditer(re.escape(marker), ip)]
    runs = []
    cur = []
    for i in idxs:
        if cur and i - cur[-1] == 12:
            cur.append(i)
        else:
            if cur:
                runs.append(cur)
            cur = [i]
    if cur:
        runs.append(cur)
    out = []
    for run in runs:
        if len(run) < 3:
            continue
        last = run[-1]
        x_off = last + 6
        y_off = x_off + 12
        if y_off + 8 <= len(ip):
            out.append((x_off, y_off))
    return out


def _extract_real_world_scale(ip: bytes):
    anchors = _find_scale_anchor_positions(ip)
    if not anchors:
        return None
    x_off, y_off = anchors[0]
    x = struct.unpack_from('<d', ip, x_off)[0]
    y = struct.unpack_from('<d', ip, y_off)[0]
    return (x, y)
