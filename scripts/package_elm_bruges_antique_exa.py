from __future__ import annotations

import hashlib
import json
import pathlib
import zipfile


ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "elm_bruges_antique_exa"
REF = ROOT / "references" / "elm_bruges_antique_exa"
ZIP = OUT / "ELM_Bruges_Antique_Exa_R2025_Rev4_Review_Package.zip"


def sha(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    qa = json.loads((OUT / "local_validation.json").read_text(encoding="utf-8"))
    assert qa["local_checks"] == "passed"
    files = [
        (OUT / "ELM_Bruges_Antique_Exa_R2025_Rev4.adsklib", "ELM_Bruges_Antique_Exa_R2025_Rev4.adsklib"),
        (OUT / "textures" / "ELM_Bruges_Antique_Exa_Color.png", "textures/ELM_Bruges_Antique_Exa_Color.png"),
        (OUT / "textures" / "ELM_Bruges_Antique_Exa_Bump16.png", "textures/ELM_Bruges_Antique_Exa_Bump16.png"),
        (OUT / "textures" / "_REVIEW_eight_by_eight_hexes.png", "review/_REVIEW_eight_by_eight_hexes.png"),
        (OUT / "textures" / "_REVIEW_grazing.jpg", "review/_REVIEW_grazing.jpg"),
        (OUT / "textures" / "_REVIEW_full_atlas_room.jpg", "review/_REVIEW_full_atlas_room.jpg"),
        (OUT / "textures" / "_REVIEW_full_atlas_three_by_three.jpg", "review/_REVIEW_full_atlas_three_by_three.jpg"),
        (OUT / "README.md", "README.md"),
        (OUT / "SOURCE_SELECTION.md", "SOURCE_SELECTION.md"),
        (OUT / "technical_validation.json", "technical_validation.json"),
        (OUT / "local_validation.json", "local_validation.json"),
        (REF / "grid_bruges_antique.jpg", "source_photos/grid_bruges_antique.jpg"),
        (REF / "antique_bruges_swatch.jpg", "source_photos/antique_bruges_swatch.jpg"),
        (REF / "kronos_bruges_exa_8521.jpg", "source_photos/kronos_bruges_exa_8521.jpg"),
        (ROOT / "scripts" / "build_elm_bruges_antique_exa.py", "source_code/build_elm_bruges_antique_exa.py"),
        (ROOT / "scripts" / "verify_elm_bruges_antique_exa.py", "source_code/verify_elm_bruges_antique_exa.py"),
    ]
    for path, _ in files:
        if not path.is_file():
            raise FileNotFoundError(path)
    manifest = {name: {"bytes": p.stat().st_size, "sha256": sha(p)} for p, name in files}
    manifest_bytes = json.dumps({"status": "review - native Revit check pending", "files": manifest}, indent=2).encode("utf-8")
    with zipfile.ZipFile(ZIP, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for p, name in files:
            z.write(p, name)
        z.writestr("PACKAGE_MANIFEST.json", manifest_bytes)
    with zipfile.ZipFile(ZIP) as z:
        assert z.testzip() is None
        assert set(z.namelist()) == set(manifest) | {"PACKAGE_MANIFEST.json"}
        for name, info in manifest.items():
            assert hashlib.sha256(z.read(name)).hexdigest() == info["sha256"]
    status = {"package": ZIP.name, "status": "review - native Revit import and render pending",
              "bytes": ZIP.stat().st_size, "sha256": sha(ZIP), "entries": len(files) + 1,
              "drive_upload": "pending"}
    (OUT / "package_validation.json").write_text(json.dumps(status, indent=2), encoding="utf-8")
    print(json.dumps(status))


if __name__ == "__main__":
    main()
