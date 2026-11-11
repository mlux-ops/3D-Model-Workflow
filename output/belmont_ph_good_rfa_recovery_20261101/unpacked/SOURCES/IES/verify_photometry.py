"""Verify manufacturer photometric ZIPs without opening or modifying Revit.

Extracts only two explicitly named OEM IES files. Produces the requested
photometry_manifest.json with ZIP/file hashes, LM-63 structural checks, and
explicit product-variant matching limitations.
"""
import datetime
import hashlib
import json
import math
import pathlib
import re
import zipfile

BASE = pathlib.Path(__file__).resolve().parent
MANIFEST = BASE / "photometry_manifest.json"

SOURCES = [
    {
        "sku": "KZC1353667",
        "manufacturer": "Kuzco",
        "model": "PD3106-BG",
        "product_url": "https://kuzcolighting.com/products/bolla-pd3106-kuzco",
        "source_zip_url": "https://s3.us-west-2.amazonaws.com/catsy.870/IES-PD3106-Bolla.zip",
        "zip_filename": "KZC1353667_PD3106_Bolla_IES.zip",
        "selected_archive_member": "IES-PD3106-Bolla/PD3106-BG - Bolla.IES",
        "output_filename": "PD3106-BG - Bolla.IES",
        "variant_matching": "Exact model and BG finish; separate BG_OP / BG_SM files excluded.",
    },
    {
        "sku": "MFR201959",
        "manufacturer": "Modern Forms",
        "model": "WS-3127-CH",
        "product_url": "https://modernforms.com/product/vogue/",
        "source_zip_url": "https://modernforms.com/images/products/IES_FILES/WS-3120_IESF.zip",
        "zip_filename": "MFR201959_WS-3120_Vogue_family_IES.zip",
        "selected_archive_member": "WS-3127.IES",
        "output_filename": "WS-3127.IES",
        "variant_matching": "Exact 27-inch WS-3127 model; file name does not identify Chrome finish or CCT.",
    },
]

NUMBER = re.compile(r"^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[Ee][+-]?\d+)?$")


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def ies_structure(raw):
    decoded = raw.decode("latin-1").replace("\r\n", "\n").replace("\r", "\n")
    lines = decoded.splitlines()
    header = [s.strip() for s in lines[:20] if s.strip()]
    version_line = next((line for line in header if line.upper().startswith("IESNA:LM-63")), None)
    tags = {}
    for line in lines:
        match = re.match(r"^\[([^\]]+)\]\s*(.*)$", line.strip())
        if match and match.group(1).upper() in ("TEST", "TESTLAB", "MANUFAC", "LUMINAIRE", "LAMP", "ISSUEDATE"):
            tags[match.group(1).upper()] = match.group(2)[:240]
    tilt_index = next((i for i, line in enumerate(lines) if line.strip().upper().startswith("TILT=")), -1)
    details = {
        "lm63_version": version_line,
        "tilt": lines[tilt_index].strip() if tilt_index >= 0 else None,
        "headers": tags,
    }
    if tilt_index < 0:
        details.update(valid=False, reason="No TILT= photometric section")
        return details
    if lines[tilt_index].strip().upper() != "TILT=NONE":
        details.update(valid=False, reason="TILT data requires additional parser")
        return details
    tokens = []
    for line in lines[tilt_index + 1:]:
        for item in line.replace(",", " ").split():
            if not NUMBER.match(item):
                details.update(valid=False, reason="Unexpected nonnumeric photometric token: " + item[:45])
                return details
            tokens.append(float(item))
    if len(tokens) < 20:
        details.update(valid=False, reason="Insufficient LM-63 photometric tokens")
        return details
    lamp_count = int(tokens[0])
    nvert, nhoriz = int(tokens[3]), int(tokens[4])
    photometric_type = int(tokens[5])
    units_type = int(tokens[6])
    start = 13
    end = start + nvert + nhoriz + nvert * nhoriz
    if not (0 < nvert <= 5000 and 0 < nhoriz <= 5000 and nvert * nhoriz <= 1000000):
        details.update(valid=False, reason="Invalid LM-63 angle grid dimensions")
        return details
    if len(tokens) < end:
        details.update(valid=False, reason="Incomplete IES angular/candela data", token_count=len(tokens), required=end)
        return details
    vertical = tokens[start:start + nvert]
    horizontal = tokens[start + nvert:start + nvert + nhoriz]
    candela = tokens[start + nvert + nhoriz:end]
    ordered_v = all(a <= b for a, b in zip(vertical, vertical[1:]))
    ordered_h = all(a <= b for a, b in zip(horizontal, horizontal[1:]))
    valid = (bool(version_line) and lamp_count != 0 and photometric_type in (1, 2, 3)
             and units_type in (1, 2) and nvert > 1 and nhoriz >= 1
             and ordered_v and ordered_h and vertical[0] >= 0 and vertical[-1] <= 180
             and horizontal[0] >= 0 and horizontal[-1] <= 360
             and all(math.isfinite(x) for x in tokens[:end])
             and all(v >= -0.000001 for v in candela))
    details.update({
        "valid": valid,
        "reason": "LM-63 header, TILT, angular grids and candela matrix parsed" if valid else "Photometric grid/header checks failed",
        "lamps": lamp_count,
        "lumens_per_lamp": tokens[1],
        "candela_multiplier": tokens[2],
        "vertical_angles": nvert,
        "horizontal_angles": nhoriz,
        "photometric_type": photometric_type,
        "units_type": units_type,
        "test_wattage": tokens[12],
        "vertical_extent_degrees": [vertical[0], vertical[-1]],
        "horizontal_extent_degrees": [horizontal[0], horizontal[-1]],
        "candela_count": len(candela),
        "max_candela_unscaled": max(candela),
    })
    return details


entries = []
for item in SOURCES:
    entry = dict(item)
    archive_path = BASE / item["zip_filename"]
    if not archive_path.exists():
        entry["status"] = "ZIP_NOT_DOWNLOADED"
        entries.append(entry)
        continue
    zip_raw = archive_path.read_bytes()
    entry["zip_path"] = str(archive_path)
    entry["zip_bytes"] = len(zip_raw)
    entry["zip_sha256"] = digest(zip_raw)
    entry["zip_signature_valid"] = zip_raw[:4] == b"PK\x03\x04"
    if not entry["zip_signature_valid"]:
        entry["status"] = "ZIP_SIGNATURE_INVALID"
        entries.append(entry)
        continue
    with zipfile.ZipFile(archive_path, "r") as archive:
        entry["zip_crc_pass"] = archive.testzip() is None
        members = [name for name in archive.namelist() if name.lower().endswith(".ies")]
        entry["available_ies_members"] = members
        matches = [name for name in members if name == item["selected_archive_member"]]
        if len(matches) != 1:
            entry["status"] = "EXACT_IES_MEMBER_MISSING_OR_DUPLICATED"
            entries.append(entry)
            continue
        ies_raw = archive.read(matches[0])
    path = BASE / item["output_filename"]
    if path.exists():
        if path.read_bytes() != ies_raw:
            raise RuntimeError("Existing different IES file; refusing overwrite: " + str(path))
    else:
        with path.open("xb") as stream:
            stream.write(ies_raw)
    entry["ies_path"] = str(path)
    entry["ies_bytes"] = len(ies_raw)
    entry["ies_sha256"] = digest(ies_raw)
    entry["lm63"] = ies_structure(ies_raw)
    entry["status"] = "VALID_IES_MODEL_MATCH" if (entry["zip_crc_pass"] and entry["lm63"]["valid"]) else "IES_STRUCTURAL_VALIDATION_FAILED"
    entry["confidence"] = "high for model-specific file; finish/CCT unconfirmed" if item["model"] == "WS-3127-CH" else "high for exact PD3106-BG variant"
    entries.append(entry)

entries.append({
    "sku": "HIN990485",
    "manufacturer": "Hinkley",
    "model": "53860BK",
    "product_url": "https://www.hinkley.com/53860bk.html",
    "spec_url": "https://www.hinkley.com/product_spec_print/download/advancedpdf/product_id/52426/53860BK.pdf",
    "status": "IES_DIRECT_LINK_UNRESOLVED",
    "notes": "Official product page is client-rendered. Static HTML and manufacturer-source searches returned no exact downloadable 53860BK IES. Photometry may require a manufacturer inquiry; no other Eos model substituted.",
})
entries.append({
    "sku": "MFR1415595",
    "manufacturer": "Modern Forms",
    "model": "FR-W2502-52L-SB/MB",
    "product_url": "https://modernforms.com/product/smooth/",
    "status": "IES_NOT_LISTED_NO_EXACT_DOWNLOAD_FOUND",
    "notes": "Manufacturer Smooth page lists spec sheet, instructions and Revit, without IES. Three inferred FR-W2502 IES ZIP paths returned HTTP 404; no photometric file assigned.",
})
manifest = {
    "project": "651 Belmont Penthouse GOOD",
    "retrieved_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "scope": "OEM IES archives and exact model/variant source inspection only; no Revit modifications.",
    "fixtures": entries,
}
with MANIFEST.open("x", encoding="utf-8") as stream:
    json.dump(manifest, stream, indent=2, ensure_ascii=True)
    stream.write("\n")

for item in entries:
    print(item["sku"], item["status"],
          item.get("output_filename", ""),
          item.get("lm63", {}).get("reason", ""))
print("MANIFEST", str(MANIFEST))
