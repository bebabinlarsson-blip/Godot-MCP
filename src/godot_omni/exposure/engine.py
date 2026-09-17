"""Adaptive Tool Exposure Engine for Godot Omni.

Dynamically tailors tool surface area to client capabilities, token budgets,
and latency requirements without sacrificing engine control.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Callable

from godot_omni.exposure.models import (
    CLIENT_BUDGETS,
    ClientBudget,
    ExposureMode,
)
from godot_omni.registry import CanonicalOperation, CanonicalOperationRegistry, get_global_registry

logger = logging.getLogger(__name__)


@dataclass
class ExposedTool:
    """Representation of an exposed MCP tool."""
    name: str
    description: str
    parameters_schema: dict[str, Any]
    handler_target: str
    operations_covered: list[str] = field(default_factory=list)


class AdaptiveExposureEngine:
    """Adapts tool registration to client capabilities and token budgets."""

    def __init__(self, registry: CanonicalOperationRegistry | None = None) -> None:
        self.registry = registry or get_global_registry()

    def resolve_mode(self, client_hint: str | None, requested_mode: str | ExposureMode | None) -> ExposureMode:
        if requested_mode:
            if isinstance(requested_mode, ExposureMode):
                return requested_mode
            try:
                return ExposureMode(requested_mode.lower())
            except ValueError:
                pass

        # Auto-detect from client hint
        if client_hint:
            norm = client_hint.lower()
            for key, budget in CLIENT_BUDGETS.items():
                if key in norm:
                    return budget.recommended_mode

        return ExposureMode.AUTO

    def get_exposed_tools(
        self,
        mode: ExposureMode = ExposureMode.AUTO,
        client_hint: str | None = None,
        included_domains: list[str] | None = None,
        excluded_domains: list[str] | None = None,
    ) -> list[ExposedTool]:
        """Generates the list of exposed tools for the given mode and client constraints."""
        actual_mode = mode
        if actual_mode == ExposureMode.AUTO:
            actual_mode = self.resolve_mode(client_hint, None)
            if actual_mode == ExposureMode.AUTO:
                # If still auto, default to domain rollup (safe under 100 tool cap)
                actual_mode = ExposureMode.DOMAIN

        if actual_mode == ExposureMode.FULL:
            return self._build_full_tools(included_domains, excluded_domains)
        elif actual_mode == ExposureMode.DOMAIN:
            return self._build_domain_tools(included_domains, excluded_domains)
        elif actual_mode == ExposureMode.LAZY:
            return self._build_lazy_tools()
        elif actual_mode == ExposureMode.ROUTER:
            return self._build_router_tools()

        return self._build_domain_tools(included_domains, excluded_domains)

    def _build_full_tools(
        self,
        included_domains: list[str] | None,
        excluded_domains: list[str] | None,
    ) -> list[ExposedTool]:
        """Exposes all registered operations as individual tools (1,700+ tools)."""
        tools: list[ExposedTool] = []
        all_ops = self.registry.list_all()

        for op in all_ops:
            if included_domains and op.domain not in included_domains:
                continue
            if excluded_domains and op.domain in excluded_domains:
                continue

            properties: dict[str, Any] = {}
            required: list[str] = []
            for p in op.parameters:
                properties[p.name] = {
                    "type": p.type_name,
                    "description": p.description,
                }
                if p.required:
                    required.append(p.name)

            schema = {
                "type": "object",
                "properties": properties,
                "required": required,
            }

            tools.append(
                ExposedTool(
                    name=op.id.replace(":", "_").replace(".", "_"),
                    description=f"[{op.domain}] {op.description}",
                    parameters_schema=schema,
                    handler_target=op.handler_info.get("handler", op.id),
                    operations_covered=[op.id],
                )
            )
        return tools

    def _build_domain_tools(
        self,
        included_domains: list[str] | None,
        excluded_domains: list[str] | None,
    ) -> list[ExposedTool]:
        """Exposes domain rollup tools + discovery tools (under 50 tools total)."""
        tools: list[ExposedTool] = []

        # 1. Add Discovery & Router tools
        tools.extend(self._build_discovery_tools())

        # 2. Add Domain Rollup tools
        domains = self.registry.list_domains()
        for domain in sorted(domains):
            if included_domains and domain not in included_domains:
                continue
            if excluded_domains and domain in excluded_domains:
                continue

            ops_in_domain = self.registry.list_by_domain(domain)
            actions = [op.id.split(":")[-1] for op in ops_in_domain]

            tool_name = f"{domain}_manage"
            desc = (
                f"Manage {domain} operations in Godot. Supports actions: "
                f"{', '.join(actions[:15])}{'...' if len(actions) > 15 else ''}. "
                f"Total operations in domain: {len(ops_in_domain)}."
            )

            schema = {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "description": f"The action or operation to perform within {domain}.",
                    },
                    "parameters": {
                        "type": "object",
                        "description": "Parameters for the action. Use tools_describe to check required arguments.",
                    },
                },
                "required": ["action"],
            }

            tools.append(
                ExposedTool(
                    name=tool_name,
                    description=desc,
                    parameters_schema=schema,
                    handler_target=f"domain_multiplexer:{domain}",
                    operations_covered=[op.id for op in ops_in_domain],
                )
            )

        return tools

    def _build_lazy_tools(self) -> list[ExposedTool]:
        """Lazy mode: discovery tools + dynamic executor + core operations."""
        tools = self._build_discovery_tools()

        # Add curated core essentials
        core_ops = [
            op for op in self.registry.list_all()
            if op.domain in ("node", "scene", "script", "project", "session", "editor")
            and "get" in op.id or "open" in op.id or "state" in op.id or "create" in op.id
        ]
        for op in core_ops[:30]:
            tools.append(
                ExposedTool(
                    name=op.id.replace(":", "_"),
                    description=f"[{op.domain}] {op.description}",
                    parameters_schema={"type": "object", "properties": {}},
                    handler_target=op.handler_info.get("handler", op.id),
                    operations_covered=[op.id],
                )
            )

        return tools

    def _build_router_tools(self) -> list[ExposedTool]:
        """Router mode: minimal 4 tools footprint."""
        return [
            ExposedTool(
                name="godot_execute",
                description="Executes any canonical Godot operation (1,700+ available). Pass operation_id and parameters.",
                parameters_schema={
                    "type": "object",
                    "properties": {
                        "operation_id": {
                            "type": "string",
                            "description": "Canonical operation ID (e.g. 'node:create', 'rendering:shader_create', 'reflection:call_method').",
                        },
                        "parameters": {
                            "type": "object",
                            "description": "Arguments dictionary for the specified operation.",
                        },
                    },
                    "required": ["operation_id"],
                },
                handler_target="router:execute",
                operations_covered=[op.id for op in self.registry.list_all()],
            ),
            ExposedTool(
                name="godot_search",
                description="Searches the canonical Godot operations registry by keyword, domain, or class name.",
                parameters_schema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query keywords (e.g. 'shader compile', 'audio play', 'navigation agent').",
                        },
                        "domain": {
                            "type": "string",
                            "description": "Optional domain filter (e.g. 'physics', 'rendering', 'node').",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results to return (default 20).",
                        },
                    },
                    "required": ["query"],
                },
                handler_target="router:search",
                operations_covered=[],
            ),
            ExposedTool(
                name="godot_describe",
                description="Returns detailed documentation, parameters, types, and examples for a canonical Godot operation.",
                parameters_schema={
                    "type": "object",
                    "properties": {
                        "operation_id": {
                            "type": "string",
                            "description": "The exact operation ID to describe (e.g. 'scene:instantiate').",
                        },
                    },
                    "required": ["operation_id"],
                },
                handler_target="router:describe",
                operations_covered=[],
            ),
            ExposedTool(
                name="godot_status",
                description="Returns live Godot editor status, active session, connected clients, and engine metrics.",
                parameters_schema={
                    "type": "object",
                    "properties": {},
                },
                handler_target="router:status",
                operations_covered=[],
            ),
        ]

    def _build_discovery_tools(self) -> list[ExposedTool]:
        """Discovery tools allowing agents to inspect available operations dynamically."""
        return [
            ExposedTool(
                name="godot_execute",
                description="Universal executor for any canonical Godot operation in the registry.",
                parameters_schema={
                    "type": "object",
                    "properties": {
                        "operation_id": {"type": "string", "description": "Canonical operation ID"},
                        "parameters": {"type": "object", "description": "Operation arguments"},
                    },
                    "required": ["operation_id"],
                },
                handler_target="router:execute",
                operations_covered=[op.id for op in self.registry.list_all()],
            ),
            ExposedTool(
                name="tools_search",
                description="Search the canonical Godot operations registry with fuzzy matching and scoring.",
                parameters_schema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search keyword or phrase"},
                        "domain": {"type": "string", "description": "Optional domain filter"},
                        "limit": {"type": "integer", "description": "Result limit (default 20)"},
                    },
                    "required": ["query"],
                },
                handler_target="router:search",
                operations_covered=[],
            ),
            ExposedTool(
                name="tools_describe",
                description="Describe parameters, schemas, latency tiers, and examples for an operation.",
                parameters_schema={
                    "type": "object",
                    "properties": {
                        "operation_id": {"type": "string", "description": "Canonical operation ID"},
                    },
                    "required": ["operation_id"],
                },
                handler_target="router:describe",
                operations_covered=[],
            ),
        ]
