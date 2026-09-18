from __future__ import annotations

import os
import sys
import uuid
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GEN_DIR = ROOT / "output" / "model-transfer-tests" / "candidate-20260918-01" / "material" / "adsklib_generator"
sys.path.insert(0, str(GEN_DIR))
import adsklib_gen as G  # noqa: E402


OUT = ROOT / "output" / "kohler_vibrant_titanium"
OLD_LIB = OUT / "KOHLER_Vibrant_Titanium_TT_R2025.adsklib"
TEXTURE = OUT / "Textures" / "KOHLER_Vibrant_Titanium_TT_Color.png"
ADELLA = ROOT / "output" / "adella" / "MSI_Adella_Viso_White_R2025.adsklib"
NEW_LIB = OUT / "KOHLER_Vibrant_Titanium_TT_R2025.adsklib"


def read_parts(path: Path):
    z = zipfile.ZipFile(path)
    guid = next(n.split("/", 1)[0] for n in z.namelist() if "/AssetData/InstanceProperties.bin" in n)
    return z, guid


def replace_ascii(data: bytes, old: str, new: str) -> bytes:
    return data.replace(old.encode("ascii"), new.encode("ascii"))


def thumbnail_bytes() -> bytes:
    # A thumbnail entry only needs valid PNG bytes; the 512x512 solid color
    # map is already lightweight and avoids adding a Pillow dependency.
    return TEXTURE.read_bytes()


def main() -> int:
    if not TEXTURE.is_file():
        raise FileNotFoundError(TEXTURE)
    old_z, old_guid = read_parts(OLD_LIB)
    a_z, a_guid = read_parts(ADELLA)

    old_ip = old_z.read(f"{old_guid}/AssetData/InstanceProperties.bin")
    a_ip = a_z.read(f"{a_guid}/AssetData/InstanceProperties.bin")
    if len(old_ip) != 1376:
        raise ValueError(f"unexpected Titanium IP length: {len(old_ip)}")
    if len(a_ip) < 2150:
        raise ValueError(f"unexpected Adella IP length: {len(a_ip)}")

    package_guid = str(uuid.uuid4()).upper()
    creator_guid = str(uuid.uuid4()).upper()
    name = "KOHLER - Vibrant Titanium (TT) - Polished"
    desc = (
        "Independent visual approximation of polished dark titanium PVD; explicit seamless uniform color map; "
        "optical values inferred from product images."
    )

    # Use the known Revit-authored two-bitmap container shape from Adella for
    # schema/connection metadata, while preserving Titanium's first three
    # native asset instance records byte-for-byte. The first three asset GUID
    # records start at identical offsets in both native libraries; the
    # texture-enabled template extends the Generic record and appends the two
    # UnifiedBitmap records after the texture-free Titanium stream ends.
    ip = old_ip + a_ip[len(old_ip):]
    ip = replace_ascii(ip, old_guid, package_guid)
    ip = replace_ascii(ip, a_guid, package_guid)

    # Re-encode the two bitmap paths and scale using the validated codec
    # helper. The inherited bump amount remains 0, so the duplicated bitmap
    # connection has no geometric effect; it exists only because the proven
    # native two-texture container shape includes both bitmap assets.
    ip = G._rebuild_ip(
        ip, package_guid, package_guid,
        diffuse_path=str(TEXTURE), bump_path=str(TEXTURE),
        real_world_scale_in=(12.0, 12.0),
    )

    # Build DIP from the proven two-texture template so it carries all five
    # asset definitions, with the Titanium name/description and fresh GUID.
    a_dip = a_z.read(f"{a_guid}/AssetData/DefinitionIteratorProperties.bin")
    thumb_suffix = f"{uuid.uuid4().hex[:11]}_png"
    dip = G._rebuild_dip(a_dip, a_guid, package_guid, name.encode("ascii"), desc.encode("ascii"), thumb_suffix)
    atoc = replace_ascii(a_z.read(f"{a_guid}/AssetData/AssetTableOfContents.bin"), a_guid, package_guid)

    # Start from the proven two-texture container and substitute identifiers,
    # timestamps and thumbnail naming in its XML/resources.
    tmpl = G.Template(str(ADELLA))
    entries = {}
    new_thumb_key = None
    old_thumb_key = next(
        k for k in tmpl.order
        if k.startswith("{GUID}/Resources/PhysMat/thumbnail/0/") and not k.endswith("cnx.xml") and not k.endswith("core.xml")
    )
    for key, raw in tmpl.entries.items():
        if key == old_thumb_key:
            continue
        data = bytes(raw)
        if key.endswith(".xml"):
            text = data.decode("utf-8")
            text = text.replace(tmpl.package_guid, package_guid)
            if tmpl.creator_guid:
                text = text.replace(tmpl.creator_guid, creator_guid)
            text = text.replace(tmpl.thumb_entry_name, thumb_suffix)
            data = text.encode("utf-8")
        else:
            data = replace_ascii(data, tmpl.package_guid, package_guid)
        entries[key.replace("{GUID}", package_guid)] = data

    new_thumb_key = f"{package_guid}/Resources/PhysMat/thumbnail/0/{thumb_suffix}"
    entries[new_thumb_key] = thumbnail_bytes()
    entries[f"{package_guid}/AssetData/DefinitionIteratorProperties.bin"] = dip
    entries[f"{package_guid}/AssetData/InstanceProperties.bin"] = ip
    entries[f"{package_guid}/AssetData/AssetTableOfContents.bin"] = atoc

    tmp = OUT / "KOHLER_Vibrant_Titanium_TT_R2025.bitmap.tmp.adsklib"
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as z:
        for key, data in entries.items():
            z.writestr(key, data)
    with zipfile.ZipFile(tmp) as z:
        bad = z.testzip()
        if bad:
            raise ValueError(f"corrupt generated library member: {bad}")

    # Independent codec readback must see the two texture paths and the name.
    parsed = G.extract_params(str(tmp))
    if parsed["material_name"] != name:
        raise ValueError(parsed["material_name"])
    if Path(parsed["diffuse_path"]).resolve() != TEXTURE.resolve():
        raise ValueError(parsed["diffuse_path"])
    if Path(parsed["bump_path"]).resolve() != TEXTURE.resolve():
        raise ValueError(parsed["bump_path"])

    backup = OUT / "KOHLER_Vibrant_Titanium_TT_R2025.texturefree.superseded.adsklib"
    if not backup.exists():
        OLD_LIB.replace(backup)
    tmp.replace(NEW_LIB)
    print(f"library={NEW_LIB}")
    print(f"bytes={NEW_LIB.stat().st_size}")
    print(f"diffuse={parsed['diffuse_path']}")
    print(f"bump={parsed['bump_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
