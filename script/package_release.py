"""Package a reproducible Godot MCP add-on archive for GitHub and the Asset Library.

Usage: python script/package_release.py [--version 5.0.35]
"""

from __future__ import annotations

import argparse
import stat
import struct
import tomllib
import zipfile
from pathlib import Path

ADDON_NAMES = ("godot_omni", "godot_ai")
REQUIRED_ADDON_FILES = ("plugin.cfg", "README.md", "LICENSE", "icon.png")
EXCLUDED_SUFFIXES = (".uid", ".pyc", ".pyo", ".tmp")
EXCLUDED_NAMES = {"__pycache__", ".DS_Store", "Thumbs.db"}
ZIP_TIMESTAMP = (1980, 1, 1, 0, 0, 0)


def _default_version(repo_root: Path) -> str:
    with (repo_root / "pyproject.toml").open("rb") as metadata_file:
        return str(tomllib.load(metadata_file)["project"]["version"])


def _check_addon(addon_dir: Path) -> None:
    missing = [name for name in REQUIRED_ADDON_FILES if not (addon_dir / name).is_file()]
    if missing:
        missing_text = ", ".join(missing)
        raise FileNotFoundError(
            f"{addon_dir} is missing required Asset Library files: {missing_text}"
        )

    icon = (addon_dir / "icon.png").read_bytes()
    if len(icon) < 24 or icon[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"{addon_dir / 'icon.png'} is not a valid PNG")
    width, height = struct.unpack(">II", icon[16:24])
    if width == 0 or height == 0 or width != height:
        raise ValueError(f"{addon_dir / 'icon.png'} must be a non-empty square PNG")


def build_package(repo_root: Path, version: str, dist_dir: Path) -> Path:
    """Create an add-ons-only archive with stable paths and ZIP metadata."""
    repo_root = repo_root.resolve()
    dist_dir.mkdir(parents=True, exist_ok=True)
    zip_path = dist_dir / f"godot-mcp-v{version}.zip"

    for addon_name in ADDON_NAMES:
        _check_addon(repo_root / "addons" / addon_name)

    with zipfile.ZipFile(
        zip_path,
        "w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
    ) as archive:
        for addon_name in ADDON_NAMES:
            addon_dir = repo_root / "addons" / addon_name
            files = sorted(path for path in addon_dir.rglob("*") if path.is_file())
            for full_path in files:
                if full_path.name in EXCLUDED_NAMES or full_path.parent.name in EXCLUDED_NAMES:
                    continue
                if full_path.name.endswith(EXCLUDED_SUFFIXES):
                    continue

                relative_path = full_path.relative_to(repo_root).as_posix()
                info = zipfile.ZipInfo(relative_path, date_time=ZIP_TIMESTAMP)
                info.compress_type = zipfile.ZIP_DEFLATED
                mode = stat.S_IMODE(full_path.stat().st_mode) or 0o644
                info.external_attr = (stat.S_IFREG | mode) << 16
                info.create_system = 3
                archive.writestr(
                    info,
                    full_path.read_bytes(),
                    compress_type=zipfile.ZIP_DEFLATED,
                    compresslevel=9,
                )

    return zip_path


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--version",
        default=_default_version(repo_root),
        help=f"Release version used in the zip file name (default: {_default_version(repo_root)}).",
    )
    args = parser.parse_args()

    zip_path = build_package(repo_root, args.version, repo_root / "dist")
    print(f"Successfully built {zip_path} ({zip_path.stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    main()
