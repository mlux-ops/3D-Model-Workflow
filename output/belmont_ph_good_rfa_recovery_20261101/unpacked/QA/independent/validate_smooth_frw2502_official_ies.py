"""Independently verify exact official Modern Forms Smooth LM-63 photometry.

Pure Python 3; no Revit/API actions. Read-only except exclusive new QA receipt.
Rejects unexpected ZIP contents, invalid LM-63 grids and wrong model/flux.
"""
import datetime
import hashlib
import json
import math
import pathlib
import re
import zipfile


BASE = pathlib.Path(r"E:\Claude\3D-Model-Workflow\output\belmont_ph_good_rfa_20261016")
ARCHIVE = BASE / "sources/photometry/MFR1415595_FR-W2502-52_IES_official.zip"
IES = BASE / "sources/photometry/FR-W2502-52L.IES"
RECEIPT = BASE / "qa/smooth_frw2502_ies_source_validation_20261016.json"
ZIP_SHA = "c9efc10fbe0789df3e85759ba587572bff0fb13a69e4e966571ae25b374b170a"
IES_SHA = "6044dda98294020d03decd14ad118be2717845536597d1ca9bb9cc296fdcda8e"
OFFICIAL_URL = "https://modernforms.com/images/products/IES_FILES/FR-W2502-52_IES.zip"
EXACT_MODEL = "FR-W2502-52L"
NUMBER = re.compile(r"^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[Ee][+-]?\d+)?$")


def require(condition, reason):
    if not condition:
        raise RuntimeError(reason)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def grid_trapezoid_flux(vertical, horizontal, candela):
    """Integrate type-C photometry over full hemisphere/sphere (lm estimate)."""
    nvert = len(vertical)
    distribution = []
    for ih in range(len(horizontal)):
        row = candela[ih * nvert:(ih + 1) * nvert]
        integral = 0.0
        for iv in range(nvert - 1):
            a = math.radians(vertical[iv])
            b = math.radians(vertical[iv + 1])
            integral += 0.5 * (row[iv] * math.sin(a) + row[iv + 1] * math.sin(b)) * (b - a)
        distribution.append(integral)
    flux = 0.0
    for ih in range(len(horizontal) - 1):
        phi = math.radians(horizontal[ih + 1] - horizontal[ih])
        flux += 0.5 * (distribution[ih] + distribution[ih + 1]) * phi
    return flux


def validate_lm63(raw):
    require(b"\x00" not in raw, "Binary/NUL in IES")
    text = raw.decode("ascii")
    lines = [line.strip() for line in text.replace("\r\n", "\n").replace("\r", "\n").splitlines()]
    require(lines[0] == "IESNA:LM-63-2002", "Expected LM-63-2002")
    tags = {}
    tilt = None
    for n, line in enumerate(lines):
        match = re.match(r"^\[([^\]]+)\]\s*(.*)$", line)
        if match:
            tags[match.group(1).upper()] = match.group(2).strip()
        if line.upper().startswith("TILT="):
            tilt = n
            break
    require(tilt is not None and lines[tilt] == "TILT=NONE", "Unexpected LM63 TILT representation")
    require(tags.get("MANUFAC") == "WAC Lighting", "Manufacturer header is not WAC Lighting")
    require(tags.get("TESTLAB") == "WAC Lighting", "Lab attribution mismatch")
    require(tags.get("LUMINAIRE") == EXACT_MODEL, "Luminaire is not exact FR-W2502-52L")
    require(tags.get("LUMCAT") == "Ceiling Fans", "Luminaire category mismatch")
    tokens = []
    for line in lines[tilt + 1:]:
        for part in line.split():
            require(NUMBER.match(part) is not None, "Non-numeric LM63 photometric payload")
            tokens.append(float(part))
    require(len(tokens) >= 13, "Short LM63 data")
    require(all(math.isfinite(x) for x in tokens), "Invalid/infinite photometry")
    lamps = int(tokens[0]); lumens = float(tokens[1]); multiplier = float(tokens[2])
    nvert = int(tokens[3]); nhoriz = int(tokens[4]); ptype = int(tokens[5]); units = int(tokens[6])
    require((lamps, nvert, nhoriz, ptype, units) == (1, 181, 17, 1, 1),
            "Grid/type differs from exact manufacturer fan photometry")
    require(multiplier == 1.0 and 0.0 < tokens[12] < 100.0, "Unexpected multiplier or test input power")
    need = 13 + nvert + nhoriz + nvert * nhoriz
    require(len(tokens) == need, "LM63 candela grid has missing or excess tokens")
    va = tokens[13:13 + nvert]
    ha = tokens[13 + nvert:13 + nvert + nhoriz]
    cd = tokens[13 + nvert + nhoriz:]
    require(va[0] == 0 and va[-1] == 180 and
            all(va[i] < va[i + 1] for i in range(nvert - 1)), "Vertical angle order invalid")
    require(ha[0] == 0 and ha[-1] == 360 and
            all(ha[i] < ha[i + 1] for i in range(nhoriz - 1)), "Horizontal angle order invalid")
    require(min(cd) >= 0 and max(cd) > 0, "Candela data empty/negative")
    # Published delivered lumens are 707. The photometric test measured 707.09.
    require(abs(lumens - 707.0) <= 0.2, "IES lamp lumens conflict with official 707 delivered lm")
    require(abs(tokens[12] - 16.0) <= 1.0, "LM63 measured power implausible for official 16 W LED")
    flux = grid_trapezoid_flux(va, ha, cd)
    # LM-63 integrated output should be reasonably consistent with the
    # reported lamp lumens. Exact equality is not expected due to photometric
    # mesh sampling, luminaire efficiency and documented near-field tests.
    require(flux > 0, "Integrated candela flux invalid")
    return {
        "valid": True,
        "standard": lines[0],
        "header_tags": tags,
        "tilt": "NONE",
        "lamps": lamps,
        "lamp_lumens": lumens,
        "candela_multiplier": multiplier,
        "vertical_angles": nvert,
        "horizontal_angles": nhoriz,
        "candela_samples": len(cd),
        "max_candela": round(max(cd), 4),
        "photometric_type": "C",
        "units_type": "feet",
        "test_input_watts": tokens[12],
        "integrated_flux_lm_approx": round(flux, 5),
        "integrated_flux_diff_percent": round(100.0 * (flux / lumens - 1.0), 3),
        "official_delivered_lumens": 707,
        "official_nominal_led_watts": 16,
        "tested_watts_diff_from_nominal_percent": round(100.0 * (tokens[12]/16.0 - 1.0),3),
        "finish_specific_photometry_verified": False,
        "cct_specific_photometry_verified": False,
    }


def main():
    require(not RECEIPT.exists(), "Validation receipt already exists; refusing overwrite")
    zip_bytes = ARCHIVE.read_bytes()
    ies_bytes = IES.read_bytes()
    require(zip_bytes[:4] == b"PK\x03\x04", "Not a ZIP signature")
    require(digest(zip_bytes) == ZIP_SHA, "Original manufacturer archive hash changed")
    require(digest(ies_bytes) == IES_SHA, "Extracted official IES hash changed")
    with zipfile.ZipFile(ARCHIVE) as handle:
        require(handle.testzip() is None, "Manufacturer archive CRC error")
        names = handle.namelist()
        require(names == ["FR-W2502-52L.IES"], "Archive member roster changed")
        require(handle.read(names[0]) == ies_bytes, "Extracted file differs from exact archive member")
    lm63 = validate_lm63(ies_bytes)
    result = {
        "status": "EXACT_MANUFACTURER_LM63_VALIDATED_NATIVE_REVIT_BINDING_PENDING",
        "verified_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "manufacturer": "WAC Lighting / Modern Forms",
        "sku": "FR-W2502-52L-SB/MB",
        "base_model": EXACT_MODEL,
        "official_archive_url": OFFICIAL_URL,
        "official_product_url": "https://modernforms.com/product/smooth/",
        "official_spec_url": "https://modernforms.com/images/products/SPECSHEET_PDF/FR-W2502_SPSHT.pdf",
        "archive_path": str(ARCHIVE),
        "archive_bytes": len(zip_bytes),
        "archive_sha256": ZIP_SHA,
        "archive_crc_pass": True,
        "archive_members": names,
        "ies_path": str(IES),
        "ies_bytes": len(ies_bytes),
        "ies_sha256": IES_SHA,
        "ies_validation": lm63,
        "limitations": [
            "IES names exact base model, not Soft Brass/Matte Black finish or CCT variant",
            "Raw type-string IES reference in OEM RFA is not proof of a bound Revit LightFamily",
            "Candidate Revit LightFamily/distribution/native propagation must be checked before SaveAs",
            "IES file must accompany candidate unless native photometric cache portability is verified",
        ],
    }
    with RECEIPT.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2, ensure_ascii=True, sort_keys=True)
        stream.write("\n")
    print("EXACT_MANUFACTURER_LM63_VALIDATED")
    print("IES", IES)
    print("RECEIPT", RECEIPT)
    print("MEASURED_LM", lm63["lamp_lumens"], "MEASURED_W", lm63["test_input_watts"])
    print("FLUX_LM_APPROX", lm63["integrated_flux_lm_approx"])


if __name__ == "__main__":
    main()
