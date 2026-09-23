#!/usr/bin/env python3
"""Prepare a real Godot project for CI smoke jobs in a clean checkout.

``test_project/`` is intentionally git-ignored because it is a developer's
working project. Hosted CI therefore bootstraps a disposable project from the
checked-in 2D fixture instead of trying to open an empty directory.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path


def _ensure_addon(project: Path, repo_root: Path, name: str) -> None:
    source = (repo_root / "addons" / name).resolve()
    target = project / "addons" / name
    if target.exists() or target.is_symlink():
        try:
            resolved = target.resolve(strict=True)
        except OSError as exc:
            raise RuntimeError(f"broken add-on path: {target}") from exc
        if resolved != source:
            raise RuntimeError(f"{target} does not point to the shipped add-on at {source}")
        return

    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        target.symlink_to(source, target_is_directory=True)
    except OSError:
        shutil.copytree(source, target, ignore=shutil.ignore_patterns("*.uid"))


def prepare(project: Path, repo_root: Path) -> None:
    """Create fixture files without replacing an existing developer project."""
    project = project.resolve()
    repo_root = repo_root.resolve()
    fixture = repo_root / "tests" / "fixtures" / "open_world_2d"
    if not (fixture / "project.godot").is_file():
        raise FileNotFoundError(f"open-world fixture is missing: {fixture}")

    if (project / "project.godot").exists():
        raise RuntimeError(
            f"refusing to overwrite existing Godot project: {project / 'project.godot'}"
        )

    project.mkdir(parents=True, exist_ok=True)
    for item in fixture.iterdir():
        destination = project / item.name
        if destination.exists():
            raise RuntimeError(f"refusing to overwrite existing fixture path: {destination}")
        if item.is_dir():
            shutil.copytree(item, destination)
        else:
            shutil.copy2(item, destination)

    # The legacy handler-test runner opens this path explicitly. Keeping it an
    # alias of the fixture's scene lets the same project serve old smoke tools.
    shutil.copy2(project / "scenes" / "open_world.tscn", project / "main.tscn")
    for name in ("godot_ai", "godot_omni"):
        _ensure_addon(project, repo_root, name)


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    project = Path(sys.argv[1]) if len(sys.argv) > 1 else repo_root / "test_project"
    try:
        prepare(project, repo_root)
    except Exception as exc:
        print(f"Could not prepare CI Godot project: {exc}", file=sys.stderr)
        return 1
    print(f"Prepared Godot smoke project at {project.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
