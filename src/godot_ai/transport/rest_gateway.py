"""REST API Gateway exposing MCP tools for ChatGPT Actions and HTTP clients."""

from __future__ import annotations

import base64
import json
import os
from typing import Any

from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse, PlainTextResponse, Response

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


def _parse_query_args(request: Request) -> dict[str, Any]:
    args: dict[str, Any] = {}
    for k, v in request.query_params.items():
        if k in ("tool", "t", "_", "mode", "raw", "format"):
            continue
        if k in ("args", "arguments", "params"):
            if v.startswith("{") and v.endswith("}"):
                try:
                    args.update(json.loads(v))
                    continue
                except Exception:
                    pass
        if v.lower() == "true":
            args[k] = True
        elif v.lower() == "false":
            args[k] = False
        elif v.isdigit():
            args[k] = int(v)
        else:
            try:
                args[k] = float(v)
            except ValueError:
                args[k] = v
    return args


def _json_safe(value: Any) -> Any:
    """Convert MCP/Pydantic values into ordinary JSON values."""
    model_dump = getattr(value, "model_dump", None)
    if callable(model_dump):
        return _json_safe(model_dump(mode="json", by_alias=True, exclude_none=True))
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    if isinstance(value, bytes):
        return base64.b64encode(value).decode("ascii")
    return value


def _serialize_tool_result(result: Any) -> Any:
    """Preserve MCP result blocks, including images, across the JSON gateway."""
    if not hasattr(result, "content"):
        return _json_safe(result)

    content = []
    for block in result.content:
        serialized = _json_safe(block)
        if isinstance(serialized, dict):
            content.append(serialized)
            continue

        block_type = getattr(block, "type", "")
        if block_type == "text" or hasattr(block, "text"):
            content.append({"type": "text", "text": str(getattr(block, "text", ""))})
        elif block_type == "image" or hasattr(block, "data"):
            image_data = getattr(block, "data", b"")
            encoded = (
                image_data
                if isinstance(image_data, str)
                else base64.b64encode(image_data).decode("ascii")
            )
            mime_type = getattr(block, "mimeType", None) or getattr(block, "mime_type", None)
            image_format = getattr(block, "format", None)
            if not mime_type and image_format:
                mime_type = image_format if "/" in image_format else f"image/{image_format}"
            content.append(
                {
                    "type": "image",
                    "data": encoded,
                    **({"mimeType": mime_type} if mime_type else {}),
                }
            )
        else:
            content.append({"type": str(block_type or "text"), "text": str(block)})

    serialized_result: dict[str, Any] = {
        "content": content,
        "isError": bool(
            getattr(result, "isError", getattr(result, "is_error", False))
        ),
    }
    structured_content = getattr(
        result, "structuredContent", getattr(result, "structured_content", None)
    )
    if structured_content is not None:
        serialized_result["structuredContent"] = _json_safe(structured_content)
    return serialized_result


def _tool_result_error(result: Any) -> str:
    if isinstance(result, dict):
        for block in result.get("content", []):
            if isinstance(block, dict) and block.get("type") == "text":
                return str(block.get("text", "Tool call failed"))
    return "Tool call failed"


def _rest_tool_fields(result: Any) -> dict[str, Any]:
    """Add lossless MCP content while keeping the REST ``result`` shape stable."""
    serialized = _serialize_tool_result(result)
    fields: dict[str, Any] = {
        "success": not (
            isinstance(serialized, dict) and serialized.get("isError", False)
        )
    }
    if isinstance(serialized, dict) and "content" in serialized:
        blocks = serialized["content"]
        fields["result"] = [
            block["text"]
            for block in blocks
            if isinstance(block, dict) and block.get("type") == "text"
        ]
        fields["content"] = blocks
        if "structuredContent" in serialized:
            fields["structuredContent"] = serialized["structuredContent"]
        if serialized.get("isError"):
            fields["isError"] = True
    else:
        fields["result"] = serialized
    if not fields["success"]:
        fields["error"] = _tool_result_error(serialized)
    return fields


def register_rest_gateway(
    mcp: FastMCP,
    *,
    auth_token: str | None = None,
    public_url: str | None = None,
) -> None:
    """Register REST endpoints and OpenAPI schema on FastMCP server."""
    token = auth_token or os.environ.get(AUTH_TOKEN_ENV, "").strip() or None

    @mcp.custom_route("/", methods=["GET"], include_in_schema=False)
    @mcp.custom_route("/index.html", methods=["GET"], include_in_schema=False)
    @mcp.custom_route("/chatgpt", methods=["GET"], include_in_schema=False)
    @mcp.custom_route("/docs", methods=["GET"], include_in_schema=False)
    @mcp.custom_route("/llms.txt", methods=["GET"], include_in_schema=False)
    @mcp.custom_route("/ai.txt", methods=["GET"], include_in_schema=False)
    @mcp.custom_route("/instructions", methods=["GET"], include_in_schema=False)
    async def landing_endpoint(request: Request) -> Response:
        base_url = public_url or str(request.base_url).rstrip("/")
        accept = request.headers.get("accept", "").lower()
        path = request.url.path

        work_mode_snippet = (
            "import base64, json, urllib.request\n\n"
            f'BASE = "{base_url}"\n'
            'AUTH_TOKEN = ""  # Paste your --auth-token value here if enabled\n\n'
            "def _display_images(response):\n"
            '    blocks = response.get("content", [])\n'
            '    images = [block for block in blocks if block.get("type") == "image"]\n'
            "    if not images:\n"
            "        return\n"
            "    try:\n"
            "        from IPython.display import Image, display\n"
            "    except ImportError:\n"
            "        return  # Image data remains available as base64 in the response\n"
            "    for block in images:\n"
            '        display(Image(data=base64.b64decode(block["data"])))\n'
            '        block["data"] = "[image displayed in this cell]"\n\n'
            "def godot(tool: str, **kwargs):\n"
            '    payload = json.dumps({"tool": tool, "arguments": kwargs}).encode()\n'
            '    headers = {"Content-Type": "application/json"}\n'
            "    if AUTH_TOKEN:\n"
            '        headers["Authorization"] = f"Bearer {AUTH_TOKEN}"\n'
            '    req = urllib.request.Request(\n'
            '        f"{BASE}/api/v1/call", data=payload, headers=headers\n'
            "    )\n"
            "    with urllib.request.urlopen(req) as resp:\n"
            "        result = json.loads(resp.read().decode())\n"
            '    if not result.get("success", False):\n'
            '        raise RuntimeError(result.get("error", "Godot tool call failed"))\n'
            "    _display_images(result)\n"
            "    return result\n\n"
            'print(godot("editor_state"))\n'
            'print(godot("filesystem_manage", op="read_text", path="res://project.godot"))\n'
            '# Captures and displays the editor image in Work Mode\n'
            '# godot("editor_screenshot")\n'
        )

        if (
            "application/json" in accept
            and "text/html" not in accept
        ) or request.query_params.get("format") == "json":
            return JSONResponse(
                {
                    "name": "Godot AI Remote Engine Bridge",
                    "version": _SERVER_VERSION,
                    "status": "online",
                    "connected": True,
                    "description": (
                        "Full-access remote bridge to local Godot 4 editor and game project."
                    ),
                    "endpoints": {
                        "call": f"{base_url}/api/v1/call",
                        "files": f"{base_url}/api/v1/files?path=res://...",
                        "tree": f"{base_url}/api/v1/tree",
                        "status": f"{base_url}/api/v1/status",
                        "tools": f"{base_url}/api/v1/tools",
                        "openapi": f"{base_url}/openapi.json",
                    },
                }
            )

        markdown_doc = (
            f"# Godot AI Remote Engine Bridge (v{_SERVER_VERSION})\n\n"
            "Full-access remote bridge to local Godot 4 editor and game project. "
            "Works out-of-the-box in ChatGPT Web, ChatGPT Work Mode, "
            "and Python Code Interpreter.\n\n"
            f"Base URL: {base_url}\n\n"
            "## 1. Direct Project File Endpoints\n"
            f"- Project Tree: GET {base_url}/api/v1/tree?path=res://\n"
            f"- Read File:    GET {base_url}/api/v1/files?path=res://path/to/script.gd "
            "(add &raw=true for plain text)\n"
            f"- Write File:   POST {base_url}/api/v1/files?path=res://path/to/script.gd "
            "(send text or {\"content\": \"...\"})\n\n"
            "## 2. Universal Tool Dispatcher (100 Godot Tools)\n"
            f"- HTTP POST: POST {base_url}/api/v1/call with "
            '{"tool": "<tool_name>", "arguments": {...}}\n'
            f"- HTTP GET:  GET {base_url}/api/v1/call?tool=<tool_name>&arg1=val1\n"
            f"- Tool List: GET {base_url}/api/v1/tools\n\n"
            "## 3. Essential Tool Examples\n"
            f"- Editor State:     {base_url}/api/v1/call?tool=editor_state\n"
            f"- Scene Hierarchy:  {base_url}/api/v1/call?tool=scene_get_hierarchy\n"
            f"- List Project:     {base_url}/api/v1/call?tool=filesystem_manage&op=list\n"
            f"- Create Node:      {base_url}/api/v1/call?tool=node_create&name=Player\n"
            f"- Create Script:    {base_url}/api/v1/call?tool=script_create&path=res://player.gd\n"
            f"- Open Scene:       {base_url}/api/v1/call?tool=scene_open&path=res://main.tscn\n"
            f"- Run Project:      {base_url}/api/v1/call?tool=project_run&op=run\n\n"
            "## 4. ChatGPT Python Snippet\n"
            "```python\n"
            f"{work_mode_snippet}"
            "```\n"
        )

        if (
            path in ("/llms.txt", "/ai.txt", "/instructions")
            or "text/markdown" in accept
            or ("text/plain" in accept and "text/html" not in accept)
        ):
            return PlainTextResponse(markdown_doc, media_type="text/markdown; charset=utf-8")

        html_content = (
            "<!DOCTYPE html>\n"
            '<html lang="en">\n'
            "<head>\n"
            '<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            "<title>Godot AI Remote Engine Bridge</title>\n"
            "<style>\n"
            "  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', "
            "Roboto, sans-serif; line-height: 1.6; max-width: 920px; margin: 40px auto; "
            "padding: 0 20px; color: #1e293b; background: #f8fafc; }\n"
            "  .card { background: #ffffff; border-radius: 10px; padding: 24px; "
            "box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); margin-bottom: 24px; "
            "border: 1px solid #e2e8f0; }\n"
            "  pre, code { font-family: monospace; background: #f1f5f9; border-radius: 6px; }\n"
            "  pre { padding: 16px; overflow-x: auto; border: 1px solid #cbd5e1; "
            "font-size: 0.9em; }\n"
            "  code { padding: 2px 6px; font-size: 0.9em; }\n"
            "  h1 { color: #0f172a; margin-top: 0; }\n"
            "  h2 { color: #1e293b; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px; "
            "margin-top: 24px; }\n"
            "  h3 { color: #334155; margin-top: 18px; }\n"
            "  .badge { display: inline-block; padding: 4px 10px; border-radius: 9999px; "
            "font-size: 0.8em; font-weight: 600; background: #e0e7ff; color: #3730a3; }\n"
            "  .status-badge { display: inline-block; padding: 4px 10px; border-radius: 9999px; "
            "font-size: 0.8em; font-weight: 600; background: #dcfce7; color: #166534; }\n"
            "  .endpoint { margin: 12px 0; padding: 12px 16px; background: #f8fafc; "
            "border-left: 4px solid #3b82f6; border-radius: 0 6px 6px 0; }\n"
            "  .method { display: inline-block; padding: 2px 6px; border-radius: 4px; "
            "font-weight: bold; font-size: 0.8em; margin-right: 6px; }\n"
            "  .get { background: #dbeafe; color: #1e40af; }\n"
            "  .post { background: #dcfce7; color: #166534; }\n"
            "  ul { padding-left: 20px; }\n"
            "  li { margin-bottom: 6px; }\n"
            "</style>\n"
            "</head>\n"
            "<body>\n"
            '<div class="card">\n'
            f"  <h1>Godot AI Remote Engine Bridge <span class=\"badge\">v{_SERVER_VERSION}</span> "
            '<span class="status-badge">Online</span></h1>\n'
            "  <p>Connected to local Godot 4 Editor. Full access enabled for ChatGPT.</p>\n"
            "</div>\n"
            '<div class="card">\n'
            "  <h2>Instructions for ChatGPT &amp; AI Assistants</h2>\n"
            "  <p>You have direct, full access to the user's running Godot 4 project. "
            "You can inspect project files, read/write scripts, view scene trees, "
            "create or modify nodes, inspect properties, and control editor actions.</p>\n"
            "  <h3>1. Direct File Access</h3>\n"
            '  <div class="endpoint">\n'
            f'    <span class="method get">GET</span> <code>{base_url}/api/v1/tree?path=res://</code><br>\n'
            "    Returns the file and directory hierarchy of the Godot project.\n"
            "  </div>\n"
            '  <div class="endpoint">\n'
            f'    <span class="method get">GET</span> <code>{base_url}/api/v1/files'
            '?path=res://path/to/script.gd</code><br>\n'
            "    Reads the content of any project file. Add <code>&amp;raw=true</code> "
            "for plain text.\n"
            "  </div>\n"
            '  <div class="endpoint">\n'
            f'    <span class="method post">POST</span> <code>{base_url}/api/v1/files'
            '?path=res://path/to/script.gd</code><br>\n'
            '    Writes or updates any project file. Send text or JSON '
            '<code>{{"content": "..."}}</code> in body.\n'
            "  </div>\n"
            "  <h3>2. Universal Engine Tool Dispatcher (100 Tools)</h3>\n"
            "  <p>You can execute ANY of the 100 tools via standard HTTP requests:</p>\n"
            '  <div class="endpoint">\n'
            f'    <span class="method post">POST</span> <code>{base_url}/api/v1/call</code> '
            'with body <code>{{"tool": "&lt;tool_name&gt;", "arguments": {{...}}}}</code><br>\n'
            "    <em>Or via simple Web Browsing / GET URL:</em><br>\n"
            f'    <span class="method get">GET</span> <code>{base_url}/api/v1/call'
            '?tool=&lt;tool_name&gt;&amp;arg1=val1</code>\n'
            "  </div>\n"
            "  <h3>Essential Tool Examples</h3>\n"
            "  <ul>\n"
            '    <li><strong>Check Editor &amp; Active Scene:</strong> '
            f'<code><a href="{base_url}/api/v1/call?tool=editor_state">'
            f'{base_url}/api/v1/call?tool=editor_state</a></code></li>\n'
            '    <li><strong>Get Scene Node Hierarchy:</strong> '
            f'<code><a href="{base_url}/api/v1/call?tool=scene_get_hierarchy">'
            f'{base_url}/api/v1/call?tool=scene_get_hierarchy</a></code></li>\n'
            '    <li><strong>List All 100 Tools:</strong> '
            f'<code><a href="{base_url}/api/v1/tools">{base_url}/api/v1/tools</a></code></li>\n'
            '    <li><strong>Create a Node:</strong> '
            f'<code>{base_url}/api/v1/call?tool=node_create&amp;name=Player</code></li>\n'
            '    <li><strong>Create or Edit Script:</strong> '
            f'<code>{base_url}/api/v1/call?tool=script_create&amp;path=res://player.gd</code></li>\n'
            '    <li><strong>Open Scene:</strong> '
            f'<code>{base_url}/api/v1/call?tool=scene_open&amp;path=res://main.tscn</code></li>\n'
            "  </ul>\n"
            "</div>\n"
            '<div class="card">\n'
            "  <h2>ChatGPT Python / Code Interpreter Snippet</h2>\n"
            "  <p>If running in ChatGPT Python mode (Work Mode), run:</p>\n"
            f'<pre><code class="language-python">{work_mode_snippet}</code></pre>\n'
            "</div>\n"
            "</body>\n"
            "</html>"
        )
        return HTMLResponse(html_content)

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

    @mcp.custom_route("/", methods=["POST"], include_in_schema=False)
    async def root_post_endpoint(request: Request) -> Response:
        if not _check_auth(request, token):
            return JSONResponse(
                {"jsonrpc": "2.0", "error": {"code": -32600, "message": "Unauthorized"}},
                status_code=401,
            )
        try:
            body = await request.json() if await request.body() else {}
        except Exception:
            return JSONResponse(
                {"jsonrpc": "2.0", "error": {"code": -32700, "message": "Parse error"}},
                status_code=400,
            )

        if isinstance(body, dict) and "jsonrpc" in body:
            method = body.get("method", "")
            req_id = body.get("id")
            params = body.get("params") or {}

            if method == "initialize":
                return JSONResponse(
                    {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "result": {
                            "protocolVersion": "2024-11-05",
                            "capabilities": {
                                "tools": {"listChanged": False},
                                "resources": {"subscribe": False, "listChanged": False},
                                "prompts": {"listChanged": False},
                            },
                            "serverInfo": {
                                "name": "Godot AI",
                                "version": _SERVER_VERSION,
                            },
                        },
                    }
                )

            if method in ("notifications/initialized", "initialized"):
                return Response(status_code=204)

            if method == "ping":
                return JSONResponse({"jsonrpc": "2.0", "id": req_id, "result": {}})

            if method == "tools/list":
                tools = await mcp.list_tools()
                tool_list = [
                    {
                        "name": t.name,
                        "description": t.description or "",
                        "inputSchema": getattr(
                            t, "parameters", {"type": "object", "properties": {}}
                        ),
                    }
                    for t in tools
                ]
                return JSONResponse(
                    {"jsonrpc": "2.0", "id": req_id, "result": {"tools": tool_list}}
                )

            if method == "tools/call":
                tool_name = params.get("name", "")
                arguments = params.get("arguments") or {}
                try:
                    result = await mcp.call_tool(tool_name, arguments=arguments)
                    return JSONResponse(
                        {
                            "jsonrpc": "2.0",
                            "id": req_id,
                            "result": _serialize_tool_result(result),
                        }
                    )
                except Exception as exc:
                    return JSONResponse(
                        {
                            "jsonrpc": "2.0",
                            "id": req_id,
                            "result": {
                                "content": [{"type": "text", "text": f"Error: {exc}"}],
                                "isError": True,
                            },
                        }
                    )

            if method in ("resources/list", "prompts/list"):
                entity = method.split("/")[0]
                return JSONResponse({"jsonrpc": "2.0", "id": req_id, "result": {entity: []}})

            return JSONResponse(
                {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32601, "message": f"Method '{method}' not found"},
                },
                status_code=404,
            )

        if isinstance(body, dict) and "tool" in body:
            tool_name = str(body["tool"]).strip()
            arguments = body.get("arguments") or {}
            try:
                result = await mcp.call_tool(tool_name, arguments=arguments)
                return JSONResponse({"tool": tool_name, **_rest_tool_fields(result)})
            except Exception as exc:
                return JSONResponse(
                    {"success": False, "tool": tool_name, "error": str(exc)},
                    status_code=400,
                )

        return JSONResponse({"error": "Unsupported request shape"}, status_code=400)

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

    @mcp.custom_route(
        "/api/v1/tools/{tool_name}",
        methods=["POST", "GET"],
        include_in_schema=False,
    )
    async def invoke_tool_endpoint(request: Request) -> JSONResponse:
        if not _check_auth(request, token):
            return JSONResponse({"error": "Unauthorized"}, status_code=401)
        tool_name = request.path_params.get("tool_name", "")

        if request.method == "POST":
            try:
                body = await request.json() if await request.body() else {}
            except Exception:
                return JSONResponse({"error": "Malformed JSON body"}, status_code=400)
            if not isinstance(body, dict):
                return JSONResponse({"error": "Expected JSON object body"}, status_code=400)
            arguments = body
        else:
            arguments = _parse_query_args(request)

        try:
            result = await mcp.call_tool(tool_name, arguments=arguments)
            return JSONResponse({"tool": tool_name, **_rest_tool_fields(result)})
        except Exception as exc:
            return JSONResponse(
                {"success": False, "tool": tool_name, "error": str(exc)},
                status_code=400,
            )

    @mcp.custom_route("/api/v1/call", methods=["POST", "GET"], include_in_schema=False)
    async def universal_call_endpoint(request: Request) -> JSONResponse:
        if not _check_auth(request, token):
            return JSONResponse({"error": "Unauthorized"}, status_code=401)

        tool_name = ""
        arguments: dict[str, Any] = {}

        if request.method == "POST":
            try:
                body = await request.json() if await request.body() else {}
            except Exception:
                return JSONResponse({"error": "Malformed JSON body"}, status_code=400)
            tool_name = body.get("tool", "")
            arguments = body.get("arguments", body.get("params", body.get("args", {})))
            if not tool_name:
                tool_name = request.query_params.get("tool", "")
        else:
            tool_name = request.query_params.get("tool", request.query_params.get("t", ""))
            arguments = _parse_query_args(request)

        if not tool_name:
            return JSONResponse(
                {
                    "error": (
                        "Missing 'tool' parameter. Provide ?tool=<tool_name> in query "
                        "or {'tool': '<tool_name>'} in JSON body"
                    )
                },
                status_code=400,
            )

        try:
            result = await mcp.call_tool(tool_name, arguments=arguments)
            return JSONResponse(
                {
                    "tool": tool_name,
                    "arguments": arguments,
                    **_rest_tool_fields(result),
                }
            )
        except Exception as exc:
            return JSONResponse(
                {"success": False, "tool": tool_name, "error": str(exc)},
                status_code=400,
            )

    @mcp.custom_route("/api/v1/files", methods=["GET", "POST", "PUT"], include_in_schema=False)
    async def files_endpoint(request: Request) -> Response:
        if not _check_auth(request, token):
            return JSONResponse({"error": "Unauthorized"}, status_code=401)

        path = request.query_params.get("path", "")
        if not path:
            return JSONResponse(
                {"error": "Missing 'path' query parameter, e.g. ?path=res://main.gd"},
                status_code=400,
            )

        if request.method == "GET":
            try:
                res = await mcp.call_tool(
                    "filesystem_manage",
                    arguments={"op": "read_text", "path": path},
                )
                content = ""
                if hasattr(res, "content"):
                    content = "".join(getattr(c, "text", str(c)) for c in res.content)
                else:
                    content = str(res)
                if (
                    request.query_params.get("raw") == "true"
                    or "text/plain" in request.headers.get("accept", "")
                ):
                    return PlainTextResponse(content)
                return JSONResponse({"success": True, "path": path, "content": content})
            except Exception as exc:
                return JSONResponse(
                    {"success": False, "path": path, "error": str(exc)},
                    status_code=400,
                )
        else:
            content = ""
            try:
                body_bytes = await request.body()
                try:
                    data = json.loads(body_bytes.decode("utf-8"))
                    if isinstance(data, dict):
                        content = data.get("content", "")
                    else:
                        content = body_bytes.decode("utf-8")
                except Exception:
                    content = body_bytes.decode("utf-8")
            except Exception:
                content = ""

            try:
                res = await mcp.call_tool(
                    "filesystem_manage",
                    arguments={"op": "write_text", "path": path, "content": content},
                )
                return JSONResponse(
                    {"success": True, "path": path, "result": str(res)}
                )
            except Exception as exc:
                return JSONResponse(
                    {"success": False, "path": path, "error": str(exc)},
                    status_code=400,
                )

    @mcp.custom_route("/api/v1/tree", methods=["GET"], include_in_schema=False)
    async def tree_endpoint(request: Request) -> JSONResponse:
        if not _check_auth(request, token):
            return JSONResponse({"error": "Unauthorized"}, status_code=401)
        path = request.query_params.get("path", "res://")
        try:
            res = await mcp.call_tool(
                "filesystem_manage",
                arguments={"op": "list", "path": path, "recursive": True},
            )
            tool_fields = _rest_tool_fields(res)
            return JSONResponse(
                {
                    "path": path,
                    "tree": tool_fields.pop("result"),
                    **tool_fields,
                }
            )
        except Exception as exc:
            return JSONResponse(
                {"success": False, "path": path, "error": str(exc)},
                status_code=400,
            )
