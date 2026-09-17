"""Client detection, status check, configuration, and doctor management for Godot Omni."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

from godot_omni.clients.models import (
    ClientDescriptor,
    ClientReport,
    ClientStatus,
    ConfigFormat,
)
from godot_omni.clients.registry import get_known_client_descriptors


def _resolve_binary(names: list[str]) -> Path | None:
    for name in names:
        resolved = shutil.which(name)
        if resolved:
            return Path(resolved)
    return None


def _get_target_command() -> tuple[str, list[str]]:
    """Returns the executable command and args for the attach bridge."""
    # Preferred: current python interpreter running godot_omni.cli attach
    py_exe = sys.executable
    return py_exe, ["-m", "godot_omni.cli", "attach"]


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _write_json_atomic(path: Path, data: dict[str, Any]) -> bool:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_fd, temp_path_str = tempfile.mkstemp(
        dir=str(path.parent), prefix=f".{path.name}.tmp."
    )
    temp_path = Path(temp_path_str)
    try:
        with os.fdopen(temp_fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
            f.write("\n")
        
        # Atomic replace with retry for Windows
        for attempt in range(5):
            try:
                os.replace(temp_path, path)
                return True
            except OSError:
                time.sleep(0.05 * (attempt + 1))
        os.replace(temp_path, path)
        return True
    except Exception as exc:
        if temp_path.exists():
            temp_path.unlink(missing_ok=True)
        raise exc


class ClientManager:
    """Manages AI client discovery, status verification, configuration, and diagnostics."""

    def __init__(self, descriptors: list[ClientDescriptor] | None = None) -> None:
        self.descriptors = descriptors or get_known_client_descriptors()

    def get_descriptor(self, client_id: str) -> ClientDescriptor | None:
        for d in self.descriptors:
            if d.id.lower() == client_id.lower() or d.display_name.lower() == client_id.lower():
                return d
        return None

    def detect_all(self) -> list[ClientReport]:
        """Detects presence and status of all known clients on the system."""
        reports: list[ClientReport] = []
        for desc in self.descriptors:
            reports.append(self.inspect_client(desc))
        return reports

    def inspect_client(self, desc: ClientDescriptor) -> ClientReport:
        binary_path = _resolve_binary(desc.binary_names)
        config_path: Path | None = None
        for p in desc.config_paths:
            if p.exists():
                config_path = p
                break

        installed = (binary_path is not None) or (config_path is not None)
        target_cmd, target_args = _get_target_command()
        expected = [target_cmd] + target_args

        if not installed:
            return ClientReport(
                client_id=desc.id,
                display_name=desc.display_name,
                installed=False,
                status=ClientStatus.NOT_INSTALLED,
                details=f"No binary or config directory found ({', '.join(desc.binary_names) or 'path checks'}).",
                expected_command=expected,
            )

        # Target config file fallback to first candidate if none exists yet
        active_config = config_path or (desc.config_paths[0] if desc.config_paths else None)

        if desc.config_format == ConfigFormat.JSON or desc.config_format == ConfigFormat.CLI:
            return self._check_json_status(desc, active_config, binary_path, expected)
        elif desc.config_format == ConfigFormat.TOML:
            return self._check_toml_status(desc, active_config, binary_path, expected)

        return ClientReport(
            client_id=desc.id,
            display_name=desc.display_name,
            installed=True,
            status=ClientStatus.NOT_CONFIGURED,
            config_path=active_config,
            binary_path=binary_path,
            expected_command=expected,
            details="Unsupported configuration format.",
        )

    def _check_json_status(
        self,
        desc: ClientDescriptor,
        config_path: Path | None,
        binary_path: Path | None,
        expected: list[str],
    ) -> ClientReport:
        if not config_path or not config_path.is_file():
            return ClientReport(
                client_id=desc.id,
                display_name=desc.display_name,
                installed=True,
                status=ClientStatus.NOT_CONFIGURED,
                config_path=config_path,
                binary_path=binary_path,
                expected_command=expected,
                details=f"Config file not yet created at {config_path}.",
            )

        data = _read_json(config_path)
        if data is None:
            return ClientReport(
                client_id=desc.id,
                display_name=desc.display_name,
                installed=True,
                status=ClientStatus.NOT_CONFIGURED,
                config_path=config_path,
                binary_path=binary_path,
                expected_command=expected,
                details=f"Malformed or unreadable JSON in {config_path}.",
            )

        # Traverse key path, e.g. ["mcpServers"]
        curr: Any = data
        for k in desc.key_path:
            if isinstance(curr, dict) and k in curr:
                curr = curr[k]
            else:
                curr = None
                break

        if not isinstance(curr, dict):
            return ClientReport(
                client_id=desc.id,
                display_name=desc.display_name,
                installed=True,
                status=ClientStatus.NOT_CONFIGURED,
                config_path=config_path,
                binary_path=binary_path,
                expected_command=expected,
                details=f"Section {'.'.join(desc.key_path)} not present in {config_path}.",
            )

        # Check for either godot-omni or godot-ai server entry
        entry = curr.get(desc.server_key) or curr.get("godot-ai")
        server_key_used = desc.server_key if desc.server_key in curr else ("godot-ai" if "godot-ai" in curr else desc.server_key)

        if not isinstance(entry, dict):
            return ClientReport(
                client_id=desc.id,
                display_name=desc.display_name,
                installed=True,
                status=ClientStatus.NOT_CONFIGURED,
                config_path=config_path,
                binary_path=binary_path,
                server_key=desc.server_key,
                expected_command=expected,
                details=f"No '{desc.server_key}' entry in {config_path}.",
            )

        cmd = entry.get("command", "")
        args = entry.get("args", [])
        configured = [cmd] + (args if isinstance(args, list) else [str(args)])

        # Determine match
        is_match = False
        if cmd == expected[0] and args == expected[1:]:
            is_match = True
        elif "godot_omni" in " ".join(configured) or "godot-omni" in " ".join(configured) or "godot-ai" in " ".join(configured):
            is_match = True

        return ClientReport(
            client_id=desc.id,
            display_name=desc.display_name,
            installed=True,
            status=ClientStatus.CONFIGURED if is_match else ClientStatus.CONFIGURED_MISMATCH,
            config_path=config_path,
            binary_path=binary_path,
            server_key=server_key_used,
            configured_command=configured,
            expected_command=expected,
            details="Active and verified" if is_match else f"Command differs from recommended {expected}",
        )

    def _check_toml_status(
        self,
        desc: ClientDescriptor,
        config_path: Path | None,
        binary_path: Path | None,
        expected: list[str],
    ) -> ClientReport:
        if not config_path or not config_path.is_file():
            return ClientReport(
                client_id=desc.id,
                display_name=desc.display_name,
                installed=True,
                status=ClientStatus.NOT_CONFIGURED,
                config_path=config_path,
                binary_path=binary_path,
                expected_command=expected,
                details=f"Config file not yet created at {config_path}.",
            )

        try:
            import tomllib
            with open(config_path, "rb") as f:
                data = tomllib.load(f)
        except Exception as exc:
            return ClientReport(
                client_id=desc.id,
                display_name=desc.display_name,
                installed=True,
                status=ClientStatus.NOT_CONFIGURED,
                config_path=config_path,
                binary_path=binary_path,
                expected_command=expected,
                details=f"Could not parse TOML in {config_path}: {exc}",
            )

        mcp_servers = data.get("mcp_servers", {})
        entry = mcp_servers.get(desc.server_key) or mcp_servers.get("godot-ai") or mcp_servers.get("godot_ai")
        server_key_used = desc.server_key if desc.server_key in mcp_servers else ("godot-ai" if "godot-ai" in mcp_servers else desc.server_key)

        if not isinstance(entry, dict):
            return ClientReport(
                client_id=desc.id,
                display_name=desc.display_name,
                installed=True,
                status=ClientStatus.NOT_CONFIGURED,
                config_path=config_path,
                binary_path=binary_path,
                server_key=desc.server_key,
                expected_command=expected,
                details=f"No '{desc.server_key}' entry in {config_path}.",
            )

        cmd = entry.get("command", [])
        configured = cmd if isinstance(cmd, list) else [str(cmd)]
        is_match = configured == expected or any("godot_omni" in x or "godot-omni" in x or "godot_ai" in x for x in configured)

        return ClientReport(
            client_id=desc.id,
            display_name=desc.display_name,
            installed=True,
            status=ClientStatus.CONFIGURED if is_match else ClientStatus.CONFIGURED_MISMATCH,
            config_path=config_path,
            binary_path=binary_path,
            server_key=server_key_used,
            configured_command=configured,
            expected_command=expected,
            details="Active and verified" if is_match else f"Command differs from recommended {expected}",
        )

    def configure(self, client_id: str) -> tuple[bool, str]:
        """Configures a client by client_id."""
        desc = self.get_descriptor(client_id)
        if not desc:
            return False, f"Unknown client: {client_id}. Available: {', '.join(d.id for d in self.descriptors)}"

        target_cmd, target_args = _get_target_command()

        # Check if client has preferred CLI registration (e.g. claude mcp add)
        if desc.supports_cli_registration and _resolve_binary(desc.binary_names):
            cli_bin = str(_resolve_binary(desc.binary_names))
            cmd_args = [cli_bin, "mcp", "add", "--scope", "user", desc.server_key, "--", target_cmd] + target_args
            try:
                res = subprocess.run(cmd_args, capture_output=True, text=True, timeout=10)
                if res.returncode == 0:
                    return True, f"Successfully registered '{desc.server_key}' with {desc.display_name} via CLI."
            except Exception:
                pass  # Fallback to file write below

        # Fallback to file configuration
        target_path = desc.config_paths[0] if desc.config_paths else None
        if not target_path:
            return False, f"No configuration path defined for client {desc.id}."

        if desc.config_format == ConfigFormat.JSON or desc.config_format == ConfigFormat.CLI:
            return self._configure_json(desc, target_path, target_cmd, target_args)
        elif desc.config_format == ConfigFormat.TOML:
            return self._configure_toml(desc, target_path, target_cmd, target_args)

        return False, f"Unsupported format {desc.config_format} for {desc.id}."

    def _configure_json(
        self,
        desc: ClientDescriptor,
        path: Path,
        target_cmd: str,
        target_args: list[str],
    ) -> tuple[bool, str]:
        data = _read_json(path) or {}
        curr = data
        for k in desc.key_path:
            if k not in curr or not isinstance(curr[k], dict):
                curr[k] = {}
            curr = curr[k]

        entry = {
            "command": target_cmd,
            "args": target_args,
        }
        entry.update(desc.extra_fields)
        curr[desc.server_key] = entry

        try:
            _write_json_atomic(path, data)
            return True, f"Configured '{desc.server_key}' in {path} successfully."
        except Exception as exc:
            return False, f"Failed to write configuration to {path}: {exc}"

    def _configure_toml(
        self,
        desc: ClientDescriptor,
        path: Path,
        target_cmd: str,
        target_args: list[str],
    ) -> tuple[bool, str]:
        path.parent.mkdir(parents=True, exist_ok=True)
        content = ""
        if path.is_file():
            try:
                content = path.read_text(encoding="utf-8")
            except Exception:
                content = ""

        section_header = f'[mcp_servers."{desc.server_key}"]'
        command_list = [target_cmd] + target_args
        formatted_cmd = json.dumps(command_list)

        new_section = (
            f'\n{section_header}\n'
            f'command = {formatted_cmd}\n'
            f'enabled = true\n'
            f'startup_timeout_sec = 60\n'
            f'tool_timeout_sec = 360\n'
        )

        if section_header in content:
            # Replace existing section
            lines = content.splitlines()
            out_lines = []
            in_section = False
            for line in lines:
                if line.strip() == section_header:
                    in_section = True
                    out_lines.append(new_section.strip())
                    continue
                if in_section:
                    if line.strip().startswith("[") and line.strip().endswith("]"):
                        in_section = False
                        out_lines.append(line)
                    continue
                out_lines.append(line)
            content = "\n".join(out_lines) + "\n"
        else:
            content = content.rstrip() + "\n" + new_section

        temp_fd, temp_path_str = tempfile.mkstemp(
            dir=str(path.parent), prefix=f".{path.name}.tmp."
        )
        temp_path = Path(temp_path_str)
        try:
            with os.fdopen(temp_fd, "w", encoding="utf-8") as f:
                f.write(content)
            os.replace(temp_path, path)
            return True, f"Configured '{desc.server_key}' in {path} successfully."
        except Exception as exc:
            if temp_path.exists():
                temp_path.unlink(missing_ok=True)
            return False, f"Failed to write TOML configuration to {path}: {exc}"

    def remove(self, client_id: str) -> tuple[bool, str]:
        """Removes server configuration from client."""
        desc = self.get_descriptor(client_id)
        if not desc:
            return False, f"Unknown client: {client_id}."

        if desc.supports_cli_registration and _resolve_binary(desc.binary_names):
            cli_bin = str(_resolve_binary(desc.binary_names))
            cmd_args = [cli_bin, "mcp", "remove", "--scope", "user", desc.server_key]
            try:
                subprocess.run(cmd_args, capture_output=True, text=True, timeout=10)
            except Exception:
                pass

        for path in desc.config_paths:
            if not path.is_file():
                continue
            if desc.config_format == ConfigFormat.JSON or desc.config_format == ConfigFormat.CLI:
                data = _read_json(path)
                if not data:
                    continue
                curr = data
                for k in desc.key_path:
                    if isinstance(curr, dict) and k in curr:
                        curr = curr[k]
                    else:
                        curr = None
                        break
                if isinstance(curr, dict) and desc.server_key in curr:
                    del curr[desc.server_key]
                    _write_json_atomic(path, data)
            elif desc.config_format == ConfigFormat.TOML:
                try:
                    content = path.read_text(encoding="utf-8")
                    section_header = f'[mcp_servers."{desc.server_key}"]'
                    if section_header in content:
                        lines = content.splitlines()
                        out_lines = []
                        in_section = False
                        for line in lines:
                            if line.strip() == section_header:
                                in_section = True
                                continue
                            if in_section:
                                if line.strip().startswith("[") and line.strip().endswith("]"):
                                    in_section = False
                                    out_lines.append(line)
                                continue
                            out_lines.append(line)
                        path.write_text("\n".join(out_lines) + "\n", encoding="utf-8")
                except Exception:
                    pass

        return True, f"Removed server entry '{desc.server_key}' for {desc.display_name}."

    def doctor(self) -> dict[str, Any]:
        """Runs health checks on all clients and overall client configuration environment."""
        reports = self.detect_all()
        checks: list[dict[str, Any]] = []
        installed_count = sum(1 for r in reports if r.installed)
        configured_count = sum(1 for r in reports if r.status == ClientStatus.CONFIGURED)

        for r in reports:
            checks.append({
                "client": r.display_name,
                "installed": r.installed,
                "status": r.status.value,
                "config_path": str(r.config_path) if r.config_path else "None",
                "details": r.details,
            })

        return {
            "summary": {
                "total_known_clients": len(self.descriptors),
                "installed_clients": installed_count,
                "configured_clients": configured_count,
            },
            "checks": checks,
        }
