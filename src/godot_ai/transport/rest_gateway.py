"""REST API Gateway exposing MCP tools for ChatGPT Actions and HTTP clients."""

from __future__ import annotations

import os
from typing import Any

from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse

from godot_ai import __version__ as _SERVER_VERSION
from godot_ai.transport.openapi import generate_openapi_spec

AUTH_TOKEN_ENV = "GODOT_AI_AUTH_TOKEN"


def _check_auth(request: Request, auth_token: str | None) -> bool:
    if not auth_token:
        return True
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:].strip()
        if token == auth_token:
            return True
    key_header = request.headers.get("X-Godot-AI-Key", "").strip()
    return key_header == auth_token


def register_rest_gateway(
    mcp: FastMCP,
    *,
    auth_token: str | None = None,
    public_url: str | None = None,
) -> None:
    """Register REST endpoints and OpenAPI schema on FastMCP server."""
    token = auth_token or os.environ.get(AUTH_TOKEN_ENV, "").strip() or None

    @mcp.custom_route("/openapi.json", methods=["GET"], include_in_schema=False)
    async def openapi_endpoint(request: Request) -> JSONResponse:
        base_url = public_url or str(request.base_url).rstrip("/")
        mode = request.query_params.get("mode", "compact")
        spec = await generate_openapi_spec(
            mcp,
            server_url=base_url,
            version=_SERVER_VERSION,
            mode=mode,
        )
        return JSONResponse(spec)

    @mcp.custom_route("/openapi-full.json", methods=["GET"], include_in_schema=False)
    async def openapi_full_endpoint(request: Request) -> JSONResponse:
        base_url = public_url or str(request.base_url).rstrip("/")
        spec = await generate_openapi_spec(
            mcp,
            server_url=base_url,
            version=_SERVER_VERSION,
            mode="full",
        )
        return JSONResponse(spec)

    @mcp.custom_route("/api/v1/status", methods=["GET"], include_in_schema=False)
    async def status_endpoint(request: Request) -> JSONResponse:
        if not _check_auth(request, token):
            return JSONResponse({"error": "Unauthorized"}, status_code=401)
        return JSONResponse(
            {
                "status": "online",
                "version": _SERVER_VERSION,
                "auth_required": token is not None,
            }
        )

    @mcp.custom_route("/api/v1/tools", methods=["GET"], include_in_schema=False)
    async def list_tools_endpoint(request: Request) -> JSONResponse:
        if not _check_auth(request, token):
            return JSONResponse({"error": "Unauthorized"}, status_code=401)
        tools = await mcp.list_tools()
        result = [
            {
                "name": t.name,
                "description": (t.description or "")[:120],
            }
            for t in tools
        ]
        return JSONResponse({"count": len(result), "tools": result})

    @mcp.custom_route("/api/v1/tools/{tool_name}", methods=["POST"], include_in_schema=False)
    async def invoke_tool_endpoint(request: Request) -> JSONResponse:
        if not _check_auth(request, token):
            return JSONResponse({"error": "Unauthorized"}, status_code=401)
        tool_name = request.path_params.get("tool_name", "")
        try:
            body = await request.json() if await request.body() else {}
        except Exception:
            return JSONResponse({"error": "Malformed JSON body"}, status_code=400)

        if not isinstance(body, dict):
            return JSONResponse({"error": "Expected JSON object body"}, status_code=400)

        try:
            result = await mcp.call_tool(tool_name, arguments=body)
            # Serialize result content
            data: Any = result
            if hasattr(result, "content"):
                data = [getattr(c, "text", str(c)) for c in result.content]
            return JSONResponse({"success": True, "result": data})
        except Exception as exc:
            return JSONResponse({"success": False, "error": str(exc)}, status_code=400)

    @mcp.custom_route("/api/v1/call", methods=["POST"], include_in_schema=False)
    async def universal_call_endpoint(request: Request) -> JSONResponse:
        if not _check_auth(request, token):
            return JSONResponse({"error": "Unauthorized"}, status_code=401)
        try:
            body = await request.json()
        except Exception:
            return JSONResponse({"error": "Malformed JSON body"}, status_code=400)

        tool_name = body.get("tool", "")
        if not tool_name:
            return JSONResponse({"error": "Missing 'tool' parameter"}, status_code=400)
        arguments = body.get("arguments", body.get("params", {}))

        try:
            result = await mcp.call_tool(tool_name, arguments=arguments)
            data: Any = result
            if hasattr(result, "content"):
                data = [getattr(c, "text", str(c)) for c in result.content]
            return JSONResponse({"success": True, "result": data})
        except Exception as exc:
            return JSONResponse({"success": False, "error": str(exc)}, status_code=400)
