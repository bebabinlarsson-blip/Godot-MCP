"""Direct, in-process runtime adapter."""

from __future__ import annotations

from typing import Any, Protocol

from fastmcp import Context

from godot_ai.godot_client.client import GodotClient, HintPolicy
from godot_ai.sessions.registry import Session, SessionRegistry


class SupportsDirectRuntime(Protocol):
    registry: SessionRegistry
    client: GodotClient


class DirectRuntime:
    """In-process runtime used by the current single-process server."""

    def __init__(
        self,
        registry: SessionRegistry,
        client: GodotClient,
        session_id: str | None = None,
    ):
        self._registry = registry
        self._client = client
        self._bound_session_id = session_id

    @classmethod
    def from_context(cls, ctx: Context, session_id: str | None = None) -> DirectRuntime:
        ## Public accessor for the value our lifespan yielded (an AppContext).
        ## When the lifespan hasn't run it returns None or an empty dict
        ## instead of the app object, so guard on shape rather than on None.
        ## getattr, not attribute access: a Context-like object without the
        ## accessor should surface as the same stable RuntimeError, not an
        ## AttributeError.
        app = getattr(ctx, "lifespan_context", None)
        if not (hasattr(app, "registry") and hasattr(app, "client")):
            raise RuntimeError("FastMCP lifespan context is not available")
        return cls.from_app_context(app, session_id=session_id)

    @classmethod
    def from_app_context(
        cls, app: SupportsDirectRuntime, session_id: str | None = None
    ) -> DirectRuntime:
        return cls(registry=app.registry, client=app.client, session_id=session_id)

    def _pin_active_session_id(self) -> str | None:
        """Resolve the active session once and keep it for this runtime.

        Unpinned calls used to re-read the process-global active session
        in both ``require_writable_async`` and ``send_command``. On the
        readiness slow path that pair can disagree if ``session_activate``
        interleaves (#911). Per-call ``session_id`` already pinned; the
        default path must too.
        """
        if self._bound_session_id is not None:
            return self._bound_session_id
        session = self._registry.get_active()
        if session is not None:
            self._bound_session_id = session.session_id
        return self._bound_session_id

    async def send_command(
        self,
        command: str,
        params: dict[str, Any] | None = None,
        session_id: str | None = None,
        timeout: float = 5.0,
        hint_policy: HintPolicy | None = None,
    ) -> dict[str, Any]:
        resolved_session_id = (
            session_id if session_id is not None else self._pin_active_session_id()
        )
        return await self._client.send(
            command=command,
            params=params,
            session_id=resolved_session_id,
            timeout=timeout,
            hint_policy=hint_policy,
        )

    def list_sessions(self) -> list[Session]:
        return self._registry.list_all()

    def get_active_session(self) -> Session | None:
        pinned = self._pin_active_session_id()
        if pinned is not None:
            return self._registry.get(pinned)
        return None

    def get_session(self, session_id: str) -> Session | None:
        """Return an immutable snapshot for one editor connection."""

        return self._registry.get(session_id)

    def record_session_readiness(self, session_id: str, value: object) -> bool:
        """Apply an authoritative readiness observation by intent."""

        return self._registry.record_readiness(session_id, value)

    @property
    def active_session_id(self) -> str | None:
        return self._pin_active_session_id()

    def set_active_session(self, session_id: str) -> None:
        self._registry.set_active(session_id)
        self._bound_session_id = session_id

    async def wait_for_session(
        self,
        exclude_id: str | None = None,
        timeout: float = 15.0,
        *,
        known_ids: set[str] | frozenset[str] | None = None,
        project_path: str | None = None,
    ) -> Session:
        return await self._registry.wait_for_session(
            exclude_id=exclude_id,
            timeout=timeout,
            known_ids=known_ids,
            project_path=project_path,
        )
