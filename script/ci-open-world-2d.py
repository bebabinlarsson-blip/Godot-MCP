#!/usr/bin/env python3
"""Open both addons in a disposable Godot 2D exploration project."""

from __future__ import annotations

import argparse
import json
import os
import secrets
import shutil
import socket
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


def _wait_for_http_health(timeout: float, token: str) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            request = urllib.request.Request(
                "http://127.0.0.1:8000/health",
                headers={"Authorization": f"Bearer {token}"},
            )
            with urllib.request.urlopen(request, timeout=1) as response:
                if response.status == 200:
                    return True
        except (OSError, urllib.error.URLError):
            time.sleep(0.25)
    return False


def _wait_for_core_tools(timeout: float, token: str) -> list[str] | None:
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
            request = urllib.request.Request(
                "http://127.0.0.1:8000/api/v1/tools",
                headers={"Authorization": f"Bearer {token}"},
            )
            with urllib.request.urlopen(request, timeout=1) as response:
                payload = json.loads(response.read().decode("utf-8"))
            names = [tool.get("name") for tool in payload.get("tools", [])]
            if required.issubset(names):
                return names
        except (OSError, urllib.error.URLError, ValueError, json.JSONDecodeError):
            pass
        time.sleep(0.25)
    return None


def _mcp_post(token: str, session_id: str | None, body: dict, timeout: float = 5.0) -> dict:
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    }
    if session_id:
        headers["Mcp-Session-Id"] = session_id
    request = urllib.request.Request(
        "http://127.0.0.1:8000/mcp",
        data=json.dumps(body).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        raw = response.read().decode("utf-8", errors="replace")
        response_session = response.headers.get("Mcp-Session-Id")
    payload = {}
    for line in raw.splitlines():
        if line.startswith("data: "):
            payload = json.loads(line[6:])
            break
    if not payload and raw.strip():
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            pass
    payload["_session_id"] = response_session
    return payload


def _mcp_initialize(token: str) -> str:
    response = _mcp_post(
        token,
        None,
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-03-26",
                "capabilities": {},
                "clientInfo": {"name": "ci-open-world-smoke", "version": "1.0"},
            },
        },
    )
    session_id = response.get("_session_id")
    if not session_id:
        raise RuntimeError("MCP initialize did not return a session id")
    _mcp_post(token, session_id, {"jsonrpc": "2.0", "method": "notifications/initialized"})
    return session_id


def _mcp_tool_call(token: str, session_id: str, name: str, arguments: dict) -> dict:
    response = _mcp_post(
        token,
        session_id,
        {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {"name": name, "arguments": arguments},
        },
    )
    if response.get("error"):
        raise RuntimeError(f"MCP {name} call failed: {response['error']}")
    result = response.get("result", {})
    if result.get("isError"):
        raise RuntimeError(f"MCP {name} call returned an error: {result}")
    structured = result.get("structuredContent")
    if isinstance(structured, dict):
        return structured
    for item in result.get("content", []):
        if item.get("type") == "text":
            try:
                decoded = json.loads(item.get("text", ""))
                if isinstance(decoded, dict):
                    return decoded
            except json.JSONDecodeError:
                pass
    return {}


def _wait_for_ports_to_close(timeout: float = 10.0) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        listening = []
        for port in (8000, 9500):
            with socket.socket() as probe:
                probe.settimeout(0.25)
                try:
                    if probe.connect_ex(("127.0.0.1", port)) == 0:
                        listening.append(port)
                except OSError:
                    pass
        if not listening:
            return True
        time.sleep(0.2)
    return False


def _stop_editor(editor: subprocess.Popen, stdout_log, token: str) -> None:
    """Ask Godot to shut down cleanly so its child MCP server is reaped."""
    graceful_error = None
    if editor.poll() is None:
        try:
            session_id = _mcp_initialize(token)
            sessions = _mcp_tool_call(token, session_id, "session_manage", {"op": "list"})
            active_session = sessions.get("active_session_id")
            args = {"op": "quit"}
            if active_session:
                args["session_id"] = active_session
            quit_result = _mcp_tool_call(token, session_id, "editor_manage", args)
            if quit_result.get("status") != "quitting":
                raise RuntimeError(
                    "editor_manage(op='quit') did not confirm shutdown: "
                    f"{quit_result}"
                )
            editor.wait(timeout=15)
        except Exception as exc:
            graceful_error = exc
        if editor.poll() is None:
            editor.terminate()
            try:
                editor.wait(timeout=10)
            except subprocess.TimeoutExpired:
                editor.kill()
                editor.wait()
    stdout_log.close()
    if not _wait_for_ports_to_close():
        detail = f"; graceful-quit error: {graceful_error}" if graceful_error else ""
        raise RuntimeError(
            "Godot exited, but its plugin-owned server kept ports 8000/9500 open" + detail
        )


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
            # Release archives and installed projects use addons/ as the
            # canonical source; plugin/addons is an old development mirror.
            source = repo_root / "addons" / addon_name
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
                "GODOT_AI_AUTH_TOKEN": secrets.token_urlsafe(32),
            }
        )
        auth_token = env["GODOT_AI_AUTH_TOKEN"]
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
        if not _wait_for_http_health(30, auth_token):
            _stop_editor(editor, editor_stdout, auth_token)
            output = _editor_output(editor_stdout_log, editor_log)
            raise RuntimeError(
                "Godot Core did not start its local MCP health endpoint:\n" + output[-12000:]
            )
        available_tools = _wait_for_core_tools(30, auth_token)
        if available_tools is None:
            _stop_editor(editor, editor_stdout, auth_token)
            output = _editor_output(editor_stdout_log, editor_log)
            raise RuntimeError(
                "The MCP gateway did not advertise its required core tools:\n"
                + output[-12000:]
            )
        _stop_editor(editor, editor_stdout, auth_token)
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
