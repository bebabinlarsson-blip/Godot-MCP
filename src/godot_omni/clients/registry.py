"""Client descriptors registry for Godot Omni."""

from __future__ import annotations

import os
from pathlib import Path

from godot_omni.clients.models import ClientDescriptor, ConfigFormat


def _user_home() -> Path:
    return Path(os.path.expanduser("~"))


def _appdata() -> Path:
    appdata = os.environ.get("APPDATA")
    if appdata:
        return Path(appdata)
    return _user_home() / "AppData" / "Roaming"


def _localappdata() -> Path:
    localappdata = os.environ.get("LOCALAPPDATA")
    if localappdata:
        return Path(localappdata)
    return _user_home() / "AppData" / "Local"


def get_known_client_descriptors() -> list[ClientDescriptor]:
    home = _user_home()
    appdata = _appdata()
    localappdata = _localappdata()

    descriptors: list[ClientDescriptor] = [
        # 1. Antigravity
        ClientDescriptor(
            id="antigravity",
            display_name="Antigravity",
            config_format=ConfigFormat.JSON,
            config_paths=[
                home / ".gemini" / "config" / "mcp_config.json",
                home / ".gemini" / "antigravity" / "mcp_config.json",
                home / ".gemini" / "antigravity" / "antigravity.json",
            ],
            binary_names=["agy", "antigravity"],
            server_key="godot-omni",
            key_path=["mcpServers"],
            command_shape="flat",
        ),
        # 2. Claude Code
        ClientDescriptor(
            id="claude_code",
            display_name="Claude Code",
            config_format=ConfigFormat.CLI,
            config_paths=[
                home / ".claude.json",
            ],
            binary_names=["claude", "claude.exe"],
            server_key="godot-omni",
            key_path=["mcpServers"],
            command_shape="flat",
            supports_cli_registration=True,
            cli_add_template=["mcp", "add", "--scope", "user", "{name}", "--", "{command}", "{args...}"],
            cli_remove_template=["mcp", "remove", "--scope", "user", "{name}"],
        ),
        # 3. Claude Desktop
        ClientDescriptor(
            id="claude_desktop",
            display_name="Claude Desktop",
            config_format=ConfigFormat.JSON,
            config_paths=[
                appdata / "Claude" / "claude_desktop_config.json",
                home / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json",
                home / ".config" / "Claude" / "claude_desktop_config.json",
            ],
            binary_names=["claude-desktop"],
            server_key="godot-omni",
            key_path=["mcpServers"],
            command_shape="flat",
        ),
        # 4. Codex CLI
        ClientDescriptor(
            id="codex",
            display_name="OpenAI Codex",
            config_format=ConfigFormat.TOML,
            config_paths=[
                home / ".codex" / "config.toml",
                localappdata / "Programs" / "OpenAI" / "Codex" / "config.toml",
            ],
            binary_names=["codex", "codex.exe"],
            server_key="godot-omni",
            key_path=["mcp_servers", "godot-omni"],
            command_shape="toml",
        ),
        # 5. VS Code
        ClientDescriptor(
            id="vscode",
            display_name="Visual Studio Code",
            config_format=ConfigFormat.JSON,
            config_paths=[
                appdata / "Code" / "User" / "settings.json",
                home / ".config" / "Code" / "User" / "settings.json",
                home / "Library" / "Application Support" / "Code" / "User" / "settings.json",
            ],
            binary_names=["code", "code.cmd"],
            server_key="godot-omni",
            key_path=["mcp", "servers"],
            command_shape="flat",
        ),
        # 6. Cursor
        ClientDescriptor(
            id="cursor",
            display_name="Cursor",
            config_format=ConfigFormat.JSON,
            config_paths=[
                home / ".cursor" / "mcp.json",
                appdata / "Cursor" / "User" / "globalStorage" / "cursor.mcp" / "mcp.json",
            ],
            binary_names=["cursor", "cursor.cmd"],
            server_key="godot-omni",
            key_path=["mcpServers"],
            command_shape="flat",
        ),
        # 7. Windsurf
        ClientDescriptor(
            id="windsurf",
            display_name="Windsurf",
            config_format=ConfigFormat.JSON,
            config_paths=[
                home / ".codeium" / "windsurf" / "mcp_config.json",
            ],
            binary_names=["windsurf"],
            server_key="godot-omni",
            key_path=["mcpServers"],
            command_shape="flat",
        ),
        # 8. Cline
        ClientDescriptor(
            id="cline",
            display_name="Cline",
            config_format=ConfigFormat.JSON,
            config_paths=[
                appdata / "Code" / "User" / "globalStorage" / "saoudrizwan.claude-dev" / "settings" / "cline_mcp_settings.json",
                home / ".config" / "Code" / "User" / "globalStorage" / "saoudrizwan.claude-dev" / "settings" / "cline_mcp_settings.json",
                home / "Library" / "Application Support" / "Code" / "User" / "globalStorage" / "saoudrizwan.claude-dev" / "settings" / "cline_mcp_settings.json",
            ],
            binary_names=[],
            server_key="godot-omni",
            key_path=["mcpServers"],
            command_shape="flat",
        ),
        # 9. Roo Code
        ClientDescriptor(
            id="roo_code",
            display_name="Roo Code",
            config_format=ConfigFormat.JSON,
            config_paths=[
                appdata / "Code" / "User" / "globalStorage" / "rooveterinaryinc.roo-cline" / "settings" / "cline_mcp_settings.json",
                home / ".config" / "Code" / "User" / "globalStorage" / "rooveterinaryinc.roo-cline" / "settings" / "cline_mcp_settings.json",
                home / "Library" / "Application Support" / "Code" / "User" / "globalStorage" / "rooveterinaryinc.roo-cline" / "settings" / "cline_mcp_settings.json",
            ],
            binary_names=[],
            server_key="godot-omni",
            key_path=["mcpServers"],
            command_shape="flat",
        ),
        # 10. OpenCode
        ClientDescriptor(
            id="opencode",
            display_name="OpenCode",
            config_format=ConfigFormat.JSON,
            config_paths=[
                home / ".config" / "opencode" / "opencode.json",
                home / ".opencode.json",
            ],
            binary_names=["opencode"],
            server_key="godot-omni",
            key_path=["mcpServers"],
            command_shape="flat",
        ),
        # 11. Zed
        ClientDescriptor(
            id="zed",
            display_name="Zed",
            config_format=ConfigFormat.JSON,
            config_paths=[
                home / ".config" / "zed" / "settings.json",
                appdata / "Zed" / "settings.json",
            ],
            binary_names=["zed"],
            server_key="godot-omni",
            key_path=["context_servers"],
            command_shape="flat",
        ),
        # 12. Gemini CLI
        ClientDescriptor(
            id="gemini_cli",
            display_name="Gemini CLI",
            config_format=ConfigFormat.JSON,
            config_paths=[
                home / ".gemini" / "config.json",
            ],
            binary_names=["gemini"],
            server_key="godot-omni",
            key_path=["mcpServers"],
            command_shape="flat",
        ),
    ]
    return descriptors
