"""Standalone Headless Godot runner for cloud sandboxes and ChatGPT containers."""

from __future__ import annotations

import logging
import os
import shutil
import subprocess
import tempfile
import urllib.request
import zipfile
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Official Godot Linux headless binary URL for cloud containers
_DEFAULT_GODOT_LINUX_URL = (
    "https://github.com/godotengine/godot/releases/download/"
    "4.3-stable/Godot_v4.3-stable_linux.x86_64.zip"
)


class CloudSandbox:
    """Manages headless Godot execution inside cloud containers."""

    def __init__(
        self,
        binary_path: str | Path | None = None,
        cache_dir: str | Path = "/tmp/godot_sandbox",
    ) -> None:
        self.cache_dir = Path(cache_dir)
        self.binary_path = Path(binary_path) if binary_path else self._resolve_or_download_binary()

    def _resolve_or_download_binary(self) -> Path:
        """Find local binary or download headless Linux binary into cache."""
        # 1. Check PATH
        path_bin = shutil.which("godot") or shutil.which("godot4")
        if path_bin:
            return Path(path_bin)

        # 2. Check cache dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        cached_executables = list(self.cache_dir.glob("Godot*"))
        for candidate in cached_executables:
            if candidate.is_file() and os.access(candidate, os.X_OK):
                return candidate

        # 3. If running on Linux x86_64 in cloud container, auto-download
        return self.download_headless_binary()

    def download_headless_binary(
        self,
        url: str = _DEFAULT_GODOT_LINUX_URL,
    ) -> Path:
        """Download and extract official Godot headless binary into cache directory."""
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        zip_target = self.cache_dir / "godot_download.zip"

        logger.info("Downloading Godot headless binary from %s ...", url)
        urllib.request.urlretrieve(url, zip_target)

        logger.info("Extracting %s ...", zip_target)
        with zipfile.ZipFile(zip_target, "r") as zf:
            zf.extractall(self.cache_dir)

        if zip_target.exists():
            zip_target.unlink()

        # Find extracted binary and make executable
        for item in self.cache_dir.iterdir():
            if item.is_file() and ("linux" in item.name.lower() or "godot" in item.name.lower()):
                item.chmod(item.stat().st_mode | 0o755)
                return item

        raise RuntimeError("Failed to locate executable binary in extracted Godot archive.")

    def run_script(
        self,
        script_content: str,
        *,
        timeout: float = 30.0,
    ) -> dict[str, Any]:
        """Execute inline GDScript headlessly and return output."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".gd", delete=False) as f:
            f.write(script_content)
            script_file = f.name

        try:
            cmd = [
                str(self.binary_path),
                "--headless",
                "--script",
                script_file,
                "--quit",
            ]
            res = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )
            return {
                "success": res.returncode == 0,
                "returncode": res.returncode,
                "stdout": res.stdout,
                "stderr": res.stderr,
            }
        finally:
            if os.path.exists(script_file):
                os.remove(script_file)

    def validate_scene(
        self,
        scene_path: str,
        project_dir: str | Path | None = None,
        *,
        timeout: float = 30.0,
    ) -> dict[str, Any]:
        """Validate a Godot scene headlessly."""
        cwd = str(project_dir) if project_dir else os.getcwd()
        cmd = [
            str(self.binary_path),
            "--headless",
            "--path",
            cwd,
            "--check-only",
            scene_path,
        ]
        res = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        return {
            "valid": res.returncode == 0,
            "returncode": res.returncode,
            "stdout": res.stdout,
            "stderr": res.stderr,
        }
