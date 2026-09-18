"""Package the verified Kohler Vibrant Titanium Revit material library.

This script intentionally packages an explicit allow-list.  Temporary RVT files,
Revit backups, and other workspace artifacts cannot enter the deliverable.
"""

from __future__ import annotations

import hashlib
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "output" / "kohler_vibrant_titanium"
LIBRARY = SOURCE / "KOHLER_Vibrant_Titanium_TT_R2025_Bitmap.adsklib"
QA = SOURCE / "_qa"
PACKAGE = ROOT / "output" / "KOHLER_Vibrant_Titanium_TT_R2025_Package.zip"
NATIVE_SURFACE = QA / "native_surface - 3D View - Titanium - 12ft surface and fixture samples.png"
COLOR_MAP = SOURCE / "Textures" / "KOHLER_Vibrant_Titanium_TT_Color.png"


def require_file(path: Path) -> None:
    if not path.is_file():
        raise FileNotFoundError(f"required file is missing: {path}")
    if path.stat().st_size == 0:
        raise ValueError(f"required file is empty: {path}")


def verify_library(path: Path) -> None:
    require_file(path)
    if not zipfile.is_zipfile(path):
        raise ValueError(f"ADSKLIB is not a readable ZIP container: {path}")
    with zipfile.ZipFile(path) as library_zip:
        members = [entry for entry in library_zip.infolist() if not entry.is_dir()]
        if not members:
            raise ValueError(f"ADSKLIB contains no files: {path}")
        bad = library_zip.testzip()
        if bad is not None:
            raise ValueError(f"ADSKLIB contains a corrupt member: {bad}")


def main() -> int:
    verify_library(LIBRARY)
    required = {
        "KOHLER_Vibrant_Titanium_TT_R2025_Bitmap.adsklib": LIBRARY,
        "README.md": SOURCE / "README.md",
        "REVIEW.md": SOURCE / "REVIEW.md",
        "Textures/KOHLER_Vibrant_Titanium_TT_Color.png": COLOR_MAP,
        "_qa/validation.json": QA / "validation.json",
        "_qa/native_surface - 3D View - Titanium - 12ft surface and fixture samples.png": NATIVE_SURFACE,
    }
    for path in required.values():
        require_file(path)

    PACKAGE.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(PACKAGE, "w", compression=zipfile.ZIP_DEFLATED) as package_zip:
        for archive_name, path in required.items():
            package_zip.write(path, archive_name)

    with zipfile.ZipFile(PACKAGE) as package_zip:
        if package_zip.testzip() is not None:
            raise ValueError("written package contains a corrupt member")
        if not package_zip.infolist():
            raise ValueError("written package is empty")

    digest = hashlib.sha256(PACKAGE.read_bytes()).hexdigest()
    print(f"package={PACKAGE}")
    print(f"entries={len(required)}")
    print(f"bytes={PACKAGE.stat().st_size}")
    print(f"sha256={digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
