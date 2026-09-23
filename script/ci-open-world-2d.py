#!/usr/bin/env python3
"""Open both addons in a disposable Godot 2D exploration project."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path


def _run(command: list[str], env: dict[str, str], timeout: int, label: str) -> str:
    result = subprocess.run(
        command,
        env=env,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )
    output = result.stdout + result.stderr
    if result.returncode:
        raise RuntimeError(f"{label} exited {result.returncode}:\n{output[-12000:]}")
    if "SCRIPT ERROR:" in output or "Parse Error" in output:
        raise RuntimeError(f"{label} reported a GDScript error:\n{output[-12000:]}")
    return output


def _wait_for_http_health(timeout: float) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen("http://127.0.0.1:8000/health", timeout=1) as response:
                if response.status == 200:
                    return True
        except (OSError, urllib.error.URLError):
            time.sleep(0.25)
    return False


def _wait_for_core_tools(timeout: float) -> list[str] | None:
    """Wait until the HTTP gateway advertises every always-on core tool."""
    required = {
        "session_activate",
        "editor_state",
        "scene_get_hierarchy",
        "node_get_properties",
    }
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(
                "http://127.0.0.1:8000/api/v1/tools", timeout=1
            ) as response:
                payload = json.loads(response.read().decode("utf-8"))
            names = [tool.get("name") for tool in payload.get("tools", [])]
            if required.issubset(names):
                return names
        except (OSError, urllib.error.URLError, ValueError, json.JSONDecodeError):
            pass
        time.sleep(0.25)
    return None


def _stop_editor(editor: subprocess.Popen, stdout_log) -> None:
    """Stop the smoke-test editor after assertions and close its log handle."""
    if editor.poll() is None:
        editor.terminate()
        try:
            editor.wait(timeout=10)
        except subprocess.TimeoutExpired:
            editor.kill()
            editor.wait()
    stdout_log.close()


def _editor_output(editor_stdout_log: Path, editor_log: Path) -> str:
    output = editor_stdout_log.read_text(encoding="utf-8", errors="replace")
    if editor_log.exists():
        output += editor_log.read_text(encoding="utf-8", errors="replace")
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("godot", nargs="?", default="godot", help="Godot executable")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    fixture = repo_root / "tests/fixtures/open_world_2d"
    with tempfile.TemporaryDirectory(prefix="godot-mcp-open-world-") as temp:
        project = Path(temp) / "project"
        shutil.copytree(fixture, project)
        addons_dir = project / "addons"
        addons_dir.mkdir()
        for addon_name in ("godot_ai", "godot_omni"):
            source = repo_root / "plugin/addons" / addon_name
            target = addons_dir / addon_name
            try:
                target.symlink_to(source, target_is_directory=True)
            except OSError:
                shutil.copytree(source, target, ignore=shutil.ignore_patterns("*.uid"))

        env = os.environ.copy()
        env.update(
            {
                "GODOT_AI_ALLOW_HEADLESS": "1",
                "GODOT_AI_DISABLE_TELEMETRY": "true",
                "GODOT_AI_MODE": "dev",
                "GODOT_AI_VENV_PYTHON": sys.executable,
            }
        )
        env.pop("GODOT_AI_AUTH_TOKEN", None)
        editor_log = Path(temp) / "editor.log"
        game_log = Path(temp) / "game.log"
        editor_stdout_log = Path(temp) / "editor-stdout.log"
        editor_stdout = editor_stdout_log.open("w", encoding="utf-8")
        editor = subprocess.Popen(
            [
                args.godot,
                "--headless",
                "--editor",
                "--path",
                str(project),
                "--log-file",
                str(editor_log),
            ],
            env=env,
            stdout=editor_stdout,
            stderr=subprocess.STDOUT,
        )
        if not _wait_for_http_health(30):
            _stop_editor(editor, editor_stdout)
            output = _editor_output(editor_stdout_log, editor_log)
            raise RuntimeError(
                "Godot Core did not start its local MCP health endpoint:\n" + output[-12000:]
            )
        available_tools = _wait_for_core_tools(30)
        if available_tools is None:
            _stop_editor(editor, editor_stdout)
            output = _editor_output(editor_stdout_log, editor_log)
            raise RuntimeError(
                "The MCP gateway did not advertise its required core tools:\n"
                + output[-12000:]
            )
        _stop_editor(editor, editor_stdout)
        editor_output = _editor_output(editor_stdout_log, editor_log)
        if "SCRIPT ERROR:" in editor_output or "Parse Error" in editor_output:
            raise RuntimeError(
                "Godot editor reported a GDScript error while loading the addons:\n"
                + editor_output[-12000:]
            )
        if "[Godot MCP Omni] Omni services initialized." not in editor_output:
            raise RuntimeError(
                "Godot MCP Omni did not initialize in the editor:\n" + editor_output[-12000:]
            )
        if "plugin loaded" not in editor_output.lower():
            raise RuntimeError(
                "Godot MCP Core did not report plugin startup:\n" + editor_output[-12000:]
            )

        game_output = _run(
            [
                args.godot,
                "--headless",
                "--path",
                str(project),
                "--quit-after",
                "30",
                "--log-file",
                str(game_log),
            ],
            env,
            timeout=60,
            label="Open-world game smoke",
        )
        if game_log.exists():
            game_output += game_log.read_text(encoding="utf-8", errors="replace")
        if "OPEN_WORLD_2D_READY" not in game_output:
            raise RuntimeError("Open-world scene did not reach _ready():\n" + game_output[-12000:])

    print(
        "PASS: both editor addons loaded, MCP core tools were advertised, "
        "and the open-world 2D scene started"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
