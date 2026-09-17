"""Register live MCP client sessions with CustomToolService.

FastMCP 3.4.2 offers no out-of-request-context way to reach connected
clients, but ``notifications/tools/list_changed`` must be sent when the
Godot plugin pushes a ``custom_tools_changed`` WS event — i.e. OUTSIDE
any MCP request. This middleware bridges the gap: every MCP message
carries its ``ServerSession`` in the FastMCP context; we stash it in
CustomToolService's WeakSet so ``notify_tools_change`` can later call
``session.send_tool_list_changed()`` on each.

Purely observational — never mutates the request or response, never
raises into the chain. Its position relative to the other godot_ai
middleware is NOT load-bearing, but it IS listed in
tests/unit/test_server_middleware_order.py's EXPECTED_ORDER (innermost)
because that suite's coverage test requires every registered godot_ai
middleware to be declared in the lock.
"""

from __future__ import annotations

import logging
from typing import Any

from fastmcp.server.middleware import CallNext, Middleware, MiddlewareContext

logger = logging.getLogger(__name__)


class TrackMcpSessions(Middleware):
    async def on_message(
        self, context: MiddlewareContext[Any], call_next: CallNext[Any, Any]
    ) -> Any:
        try:
            ctx = context.fastmcp_context
            if ctx is not None:
                from godot_ai.services.custom_tool_service import CustomToolService

                CustomToolService.get_instance().track_mcp_session(ctx.session)
        except Exception:
            ## Session not established yet (Context.session raises
            ## RuntimeError during early init) or service not constructed
            ## (unit tests building a bare server). Tracking is best-effort;
            ## never fail the actual request over it.
            logger.debug("MCP session tracking skipped", exc_info=True)
        return await call_next(context)
