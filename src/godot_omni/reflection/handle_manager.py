"""Object Handle Manager for Godot Omni.

Tracks dynamic Godot object references using deterministic handles:
`obj://<session_id>/<object_id>`
Guards against stale handles, memory leaks, and freed object access.
"""

from __future__ import annotations

import re
import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ObjectHandle:
    """Represents an active or tracked Godot Object handle."""
    session_id: str
    object_id: int
    godot_class: str
    generation: int = 1
    created_at: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)
    is_freed: bool = False

    @property
    def uri(self) -> str:
        return f"obj://{self.session_id}/{self.object_id}"

    def mark_freed(self) -> None:
        self.is_freed = True


HANDLE_REGEX = re.compile(r"^obj://([a-zA-Z0-9_\-\.]+)/(\d+)$")


class HandleManager:
    """Manages creation, resolution, validation, and lifecycle of object handles."""

    def __init__(self) -> None:
        # Key: (session_id, object_id) -> ObjectHandle
        self._handles: dict[tuple[str, int], ObjectHandle] = {}

    def register_handle(
        self,
        session_id: str,
        object_id: int,
        godot_class: str,
        metadata: dict[str, Any] | None = None,
    ) -> ObjectHandle:
        key = (session_id, object_id)
        if key in self._handles:
            existing = self._handles[key]
            if not existing.is_freed:
                return existing
            # If freed previously and reallocated, increment generation
            gen = existing.generation + 1
        else:
            gen = 1

        handle = ObjectHandle(
            session_id=session_id,
            object_id=object_id,
            godot_class=godot_class,
            generation=gen,
            metadata=metadata or {},
        )
        self._handles[key] = handle
        return handle

    def parse_uri(self, uri: str) -> tuple[str, int] | None:
        match = HANDLE_REGEX.match(uri.strip())
        if not match:
            return None
        session_id, obj_id_str = match.groups()
        return session_id, int(obj_id_str)

    def resolve_handle(self, uri: str) -> ObjectHandle:
        parsed = self.parse_uri(uri)
        if not parsed:
            raise ValueError(f"Malformed object handle URI: '{uri}'. Expected format: obj://<session>/<id>")

        key = parsed
        handle = self._handles.get(key)
        if not handle:
            # Create lazy untracked reference
            handle = ObjectHandle(
                session_id=parsed[0],
                object_id=parsed[1],
                godot_class="Object",
            )
            self._handles[key] = handle

        if handle.is_freed:
            raise RuntimeError(f"OBJECT_FREED: Object {uri} has been freed or destroyed in Godot.")

        return handle

    def release_handle(self, uri: str) -> bool:
        parsed = self.parse_uri(uri)
        if not parsed:
            return False
        handle = self._handles.get(parsed)
        if handle:
            handle.mark_freed()
            return True
        return False

    def clear_session(self, session_id: str) -> int:
        removed = 0
        keys_to_del = [k for k in self._handles if k[0] == session_id]
        for k in keys_to_del:
            del self._handles[k]
            removed += 1
        return removed

    def get_stats(self) -> dict[str, Any]:
        total = len(self._handles)
        active = sum(1 for h in self._handles.values() if not h.is_freed)
        freed = total - active
        return {
            "total_handles": total,
            "active_handles": active,
            "freed_handles": freed,
        }
