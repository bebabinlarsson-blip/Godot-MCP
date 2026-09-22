"""OpenAPI 3.1 schema generator for ChatGPT Custom GPT Actions and REST clients."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from fastmcp import FastMCP

COMPACT_PRIMARY_TOOLS: tuple[str, ...] = (
    "scene_manage",
    "node_manage",
    "script_manage",
    "project_manage",
    "editor_manage",
    "game_manage",
    "ui_manage",
    "physics_manage",
    "animation_manage",
    "resource_manage",
    "body_manage",
    "world_manage",
    "headless_manage",
    "cloud_manage",
    "input_event_manage",
    "physics_query_manage",
    "gi_manage",
    "curve_manage",
)


async def generate_openapi_spec(
    mcp: FastMCP,
    *,
    server_url: str = "http://localhost:8000",
    title: str = "Godot AI Engine Control",
    version: str = "5.0.26",
    mode: str = "compact",
    tools: Sequence[Any] | None = None,
) -> dict[str, Any]:
    """Generate an OpenAPI 3.1.0 specification dictionary from registered tools.

    In 'compact' mode (default), generates <= 25 operations to strictly respect
    OpenAI's 30-operation limit for Custom GPT Actions.
    In 'full' mode, generates endpoints for all registered tools.
    """
    paths: dict[str, Any] = {}
    tool_list = await mcp.list_tools() if tools is None else tools

    for tool in tool_list:
        tool_name = getattr(tool, "name", "")
        if not tool_name:
            continue
        if mode == "compact" and tool_name not in COMPACT_PRIMARY_TOOLS:
            continue
        description = getattr(tool, "description", "") or f"Execute {tool_name} tool."
        parameters = getattr(tool, "parameters", None)

        request_body_schema: dict[str, Any] = {
            "type": "object",
            "properties": {},
        }
        if isinstance(parameters, dict):
            request_body_schema = {
                "type": "object",
                "properties": parameters.get("properties", {}),
                "required": parameters.get("required", []),
            }

        paths[f"/api/v1/tools/{tool_name}"] = {
            "post": {
                "summary": tool_name.replace("_", " ").title(),
                "description": description[:300],
                "operationId": f"call_{tool_name}",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": request_body_schema,
                        }
                    },
                },
                "responses": {
                    "200": {
                        "description": "Tool execution succeeded.",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "success": {"type": "boolean"},
                                        "data": {"type": "object"},
                                    },
                                }
                            }
                        },
                    },
                    "400": {"description": "Invalid tool arguments or error."},
                    "503": {"description": "Godot editor session disconnected."},
                },
            }
        }

    # Universal /api/v1/call endpoint
    paths["/api/v1/call"] = {
        "post": {
            "summary": "Universal Tool Dispatcher",
            "description": "Execute any Godot AI tool dynamically by name with arguments.",
            "operationId": "call_universal",
            "requestBody": {
                "required": True,
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "tool": {"type": "string", "description": "Target tool name."},
                                "arguments": {
                                    "type": "object",
                                    "description": "Arguments dictionary.",
                                },
                            },
                            "required": ["tool"],
                        }
                    }
                },
            },
            "responses": {
                "200": {"description": "Execution result."},
                "400": {"description": "Error or invalid request."},
            },
        }
    }

    return {
        "openapi": "3.1.0",
        "info": {
            "title": title,
            "version": version,
            "description": (
                "REST and Action interface for Godot AI MCP Server. "
                "Enables ChatGPT web actions and remote cloud clients to interact with Godot."
            ),
        },
        "servers": [{"url": server_url}],
        "paths": paths,
        "components": {
            "securitySchemes": {
                "BearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "description": "Optional Bearer token when --auth-token is enabled.",
                }
            }
        },
    }
