"""Package Godot MCP release zip for GitHub releases and Godot Asset Library.

Usage: python script/package_release.py [--version 5.0.2]
"""
import argparse
import os
import zipfile
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--version",
        default="5.0.30",
        help="Release version used in the zip file name (default: 5.0.30).",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    dist_dir = repo_root / "dist"
    dist_dir.mkdir(exist_ok=True)

    zip_path = dist_dir / f"godot-mcp-v{args.version}.zip"

    exclude_suffixes = {".uid", ".pyc", ".pyo", ".tmp"}
    exclude_names = {"__pycache__", ".DS_Store", "Thumbs.db"}

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for addon_name in ["godot_omni", "godot_ai"]:
            addon_dir = repo_root / "addons" / addon_name
            if not addon_dir.exists():
                continue
            for root, dirs, files in os.walk(addon_dir):
                dirs[:] = [d for d in dirs if d not in exclude_names]
                for f in files:
                    if any(f.endswith(s) for s in exclude_suffixes) or f in exclude_names:
                        continue
                    full_p = Path(root) / f
                    rel_p = full_p.relative_to(repo_root)
                    zf.write(full_p, str(rel_p).replace("\\", "/"))

    print(f"Successfully built {zip_path} ({zip_path.stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    main()
