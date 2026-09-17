"""Client configuration and status models for Godot Omni."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class ClientStatus(str, Enum):
    """Configuration status for an MCP client."""
    CONFIGURED = "configured"
    CONFIGURED_MISMATCH = "configured_mismatch"
    NOT_CONFIGURED = "not_configured"
    NOT_INSTALLED = "not_installed"


class ConfigFormat(str, Enum):
    """File format used by client configuration."""
    JSON = "json"
    TOML = "toml"
    YAML = "yaml"
    CLI = "cli"


@dataclass
class ClientDescriptor:
    """Descriptor for a known MCP client and how to detect/configure it."""
    id: str
    display_name: str
    config_format: ConfigFormat
    config_paths: list[Path] = field(default_factory=list)
    binary_names: list[str] = field(default_factory=list)
    server_key: str = "godot-omni"
    key_path: list[str] = field(default_factory=lambda: ["mcpServers"])
    command_shape: str = "flat"  # "flat", "nested", "array", or "toml"
    supports_cli_registration: bool = False
    cli_add_template: list[str] = field(default_factory=list)
    cli_remove_template: list[str] = field(default_factory=list)
    extra_fields: dict[str, Any] = field(default_factory=dict)


@dataclass
class ClientReport:
    """Detection and configuration report for a single client."""
    client_id: str
    display_name: str
    installed: bool
    status: ClientStatus
    config_path: Path | None = None
    binary_path: Path | None = None
    server_key: str = "godot-omni"
    details: str = ""
    configured_command: list[str] = field(default_factory=list)
    expected_command: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "client_id": self.client_id,
            "display_name": self.display_name,
            "installed": self.installed,
            "status": self.status.value,
            "config_path": str(self.config_path) if self.config_path else None,
            "binary_path": str(self.binary_path) if self.binary_path else None,
            "server_key": self.server_key,
            "details": self.details,
            "configured_command": self.configured_command,
            "expected_command": self.expected_command,
        }
