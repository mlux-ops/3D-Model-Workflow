from __future__ import annotations

import hashlib
import json
import pathlib
import sys
import zipfile

from PIL import Image


ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "elm_bruges_antique_exa"
GEN = ROOT / "output" / "model-transfer-tests" / "candidate-20260918-01" / "material" / "adsklib_generator"
sys.path.insert(0, str(GEN))
import adsklib_gen as codec


def sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def wrapped_edges(im: Image.Image) -> bool:
    w, h = im.size
    return (im.crop((0, 0, w, 1)).tobytes() == im.crop((0, h - 1, w, h)).tobytes()
            and im.crop((0, 0, 1, h)).tobytes() == im.crop((w - 1, 0, w, h)).tobytes())


def main() -> None:
    build = json.loads((OUT / "technical_validation.json").read_text(encoding="utf-8"))
    expected = (7168, 6984)
    colors = OUT / "textures" / "ELM_Bruges_Antique_Exa_Color.png"
    bump = OUT / "textures" / "ELM_Bruges_Antique_Exa_Bump16.png"
    library = OUT / "ELM_Bruges_Antique_Exa_R2025_Rev4.adsklib"
    for p in (colors, bump, library):
        if not p.is_file():
            raise AssertionError("missing output: " + str(p))
    with Image.open(colors) as c, Image.open(bump) as b:
        assert c.size == b.size == expected
        assert c.mode == "RGB"
        assert b.mode == "I;16"
        assert wrapped_edges(c) and wrapped_edges(b)
    with zipfile.ZipFile(library) as z:
        assert z.testzip() is None
        assert len(z.namelist()) > 20
    data = codec.extract_params(str(library))
    assert data["material_name"] == build["material"]
    assert pathlib.Path(data["diffuse_path"]).resolve() == colors.resolve()
    assert pathlib.Path(data["bump_path"]).resolve() == bump.resolve()
    assert all(abs(a - b) < .001 for a, b in zip(data["real_world_scale_in"], build["atlas_inches"]))
    assert build["unique_face_patches"] == sum(build["hex_counts"].values()) == 4608
    assert build["clearance_mm"] > 0.0
    assert sha256(colors) == build["maps"]["color"]["sha256"]
    assert sha256(bump) == build["maps"]["bump"]["sha256"]
    assert sha256(library) == build["adsklib"]["sha256"]
    report = {
        "local_checks": "passed", "native_revit_import": "pending: Autodesk device limit reached",
        "material": data["material_name"], "atlas_pixels": list(expected),
        "atlas_inches": list(data["real_world_scale_in"]), "color_mode": "RGB", "bump_mode": "I;16",
        "opposite_edges_pixel_identical": True, "unique_hex_face_crops": 4608,
        "hex_count": 4608, "library_readback": "passed", "bitmap_paths_resolve_locally": True,
        "grout_step_mm_estimated": build["grout_step_mm_estimated"],
        "groove_relief_mm_estimated": build["groove_relief_mm_estimated"],
        "minimum_clearance_mm": build["clearance_mm"],
        "files": {p.name: {"bytes": p.stat().st_size, "sha256": sha256(p)} for p in (colors, bump, library)},
    }
    (OUT / "local_validation.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"status": "passed", "native_revit_import": report["native_revit_import"], "hexes": report["hex_count"]}))


if __name__ == "__main__":
    main()
