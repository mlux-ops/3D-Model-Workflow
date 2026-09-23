from __future__ import annotations

import hashlib
import json
import pathlib
import zipfile

import numpy as np
from PIL import Image


ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "elm_bruges_antique_exa"
TEX = OUT / "textures"
COLOR = TEX / "ELM_Bruges_Antique_Exa_Rev5_Color.png"
BUMP = TEX / "ELM_Bruges_Antique_Exa_Rev5_Bump16.png"
README = OUT / "MAPS_ONLY_README.md"
ZIP = OUT / "ELM_Bruges_Antique_Exa_Rev5_Color_Bump_Maps.zip"
REPORT = OUT / "maps_only_validation.json"


def sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def inspect(path: pathlib.Path, expected_mode: str) -> dict:
    with Image.open(path) as image:
        array = np.asarray(image)
        assert image.size == (7168, 6984), (path.name, image.size)
        assert image.mode == expected_mode, (path.name, image.mode)
        assert np.array_equal(array[0], array[-1]), f"vertical wrap failed: {path.name}"
        assert np.array_equal(array[:, 0], array[:, -1]), f"horizontal wrap failed: {path.name}"
        detail = {
            "file": path.name,
            "pixels": list(image.size),
            "mode": image.mode,
            "horizontal_wrap_exact": True,
            "vertical_wrap_exact": True,
            "min": int(array.min()),
            "max": int(array.max()),
            "sha256": sha256(path),
        }
        if path == BUMP:
            strip_medians = [float(np.median(array[:, x:x + 512]))
                             for x in range(0, image.width, 512)]
            strip_medians += [float(np.median(array[y:y + 512, :]))
                              for y in range(0, image.height, 512)]
            assert min(strip_medians) > 50000, "bump face coverage is missing in a strip"
            detail["minimum_512px_strip_median"] = min(strip_medians)
        return detail


def main() -> None:
    report = {
        "color": inspect(COLOR, "RGB"),
        "bump": inspect(BUMP, "I;16"),
        "sample_size_inches": [185.8268, 180.7087],
        "atlas_sheet_count": [16, 18],
        "estimated_relief_mm": {
            "grout_step": 0.50,
            "diagonal_groove": 0.30,
            "microrelief_max": 0.02,
            "minimum_groove_to_grout_clearance": 0.18,
        },
    }
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    files = [COLOR, BUMP, README, REPORT]
    with zipfile.ZipFile(ZIP, "w", compression=zipfile.ZIP_STORED) as archive:
        for file in files:
            archive.write(file, arcname=file.name)
    with zipfile.ZipFile(ZIP) as archive:
        assert archive.testzip() is None
        assert set(archive.namelist()) == {file.name for file in files}
    print(json.dumps({"zip": str(ZIP), "size": ZIP.stat().st_size,
                      "sha256": sha256(ZIP), "entries": [file.name for file in files]}, indent=2))


if __name__ == "__main__":
    main()
