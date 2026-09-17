"""Exposure mode definitions and client tool budget models."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class ExposureMode(str, Enum):
    """Tool exposure strategy for MCP server."""
    AUTO = "auto"        # Automatically adapt to client capabilities and caps
    FULL = "full"        # Expose all 1,500+ operations as individual MCP tools
    LAZY = "lazy"        # Expose discovery + on-demand tools + core operations
    DOMAIN = "domain"    # Expose high-level domain rollups (<= 50 tools)
    ROUTER = "router"    # Ultra-lean footprint (4 tools: execute, search, describe, status)


@dataclass
class ClientBudget:
    """Estimated tool capacity and limits for specific AI clients."""
    client_name: str
    max_tool_count: int
    recommended_mode: ExposureMode
    supports_lazy: bool = False
    notes: str = ""


CLIENT_BUDGETS: dict[str, ClientBudget] = {
    "antigravity": ClientBudget(
        client_name="Antigravity",
        max_tool_count=100,
        recommended_mode=ExposureMode.DOMAIN,
        supports_lazy=True,
        notes="Antigravity enforces a strict 100-tool cap per server. Use DOMAIN or ROUTER mode.",
    ),
    "claude_code": ClientBudget(
        client_name="Claude Code",
        max_tool_count=200,
        recommended_mode=ExposureMode.DOMAIN,
        supports_lazy=False,
        notes="Claude Code handles up to ~200 tools comfortably.",
    ),
    "codex": ClientBudget(
        client_name="OpenAI Codex",
        max_tool_count=300,
        recommended_mode=ExposureMode.DOMAIN,
        supports_lazy=False,
        notes="Codex performs best with domain rollups or curated sets.",
    ),
    "cursor": ClientBudget(
        client_name="Cursor",
        max_tool_count=150,
        recommended_mode=ExposureMode.DOMAIN,
        supports_lazy=False,
        notes="Cursor works best with domain rollups.",
    ),
    "windsurf": ClientBudget(
        client_name="Windsurf",
        max_tool_count=150,
        recommended_mode=ExposureMode.DOMAIN,
        supports_lazy=False,
        notes="Windsurf cascades best with domain rollups.",
    ),
    "generic": ClientBudget(
        client_name="Generic",
        max_tool_count=50,
        recommended_mode=ExposureMode.ROUTER,
        supports_lazy=False,
        notes="Default conservative router mode for unknown clients.",
    ),
}
