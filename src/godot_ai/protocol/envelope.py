"""Protocol envelope types for server <-> plugin communication."""

from __future__ import annotations

import math
from typing import Annotated, Any, Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, StrictInt, StrictStr

WS_PROTOCOL_VERSION = 2

NonceHex = Annotated[StrictStr, Field(pattern=r"^[0-9a-f]{64}$")]
ProofHex = Annotated[StrictStr, Field(pattern=r"^[0-9a-f]{64}$")]
SessionId = Annotated[StrictStr, Field(pattern=r"^[A-Za-z0-9._@-]{1,128}$")]
VersionToken = Annotated[StrictStr, Field(min_length=1, max_length=64)]

## The plugin emits exactly these six counters. Keeping the wire shape finite
## prevents an untrusted local WebSocket peer from parking a near-4 MiB mapping
## in Session and making every later one-field state transition copy it.
ErrorWatermarkKey = Literal[
    "run_seq",
    "editor_ring",
    "debugger_promoted",
    "game_error_warn",
    "editor_ring_warn",
    "game_warn",
]
ErrorWatermarkValue = Annotated[StrictInt, Field(ge=0, le=(1 << 63) - 1)]
ErrorWatermark = Annotated[
    dict[ErrorWatermarkKey, ErrorWatermarkValue],
    Field(max_length=6),
]

Readiness = Literal["ready", "importing", "playing", "no_scene"]
KNOWN_READINESS: frozenset[str] = frozenset(Readiness.__args__)


def find_non_finite_float(value: Any, path: str = "params") -> str | None:
    """Return the key path of the first non-finite float in a params tree.

    NaN/Infinity are not representable in JSON: ``model_dump_json`` serializes
    them as ``null``, so a write-tool param that went NaN upstream (physics
    blowup, divide-by-zero position) would silently corrupt scene data while
    the tool reports success (#688). Callers reject the command instead.
    Returns ``None`` when every float in the tree is finite.
    """
    if isinstance(value, float) and not math.isfinite(value):
        return path
    if isinstance(value, dict):
        for key, item in value.items():
            found = find_non_finite_float(item, f"{path}.{key}")
            if found is not None:
                return found
    elif isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            found = find_non_finite_float(item, f"{path}[{index}]")
            if found is not None:
                return found
    return None


class CommandRequest(BaseModel):
    """A command sent from the Python server to the Godot plugin."""

    request_id: str = Field(default_factory=lambda: uuid4().hex)
    command: str
    params: dict[str, Any] = Field(default_factory=dict)


class CommandResponse(BaseModel):
    """A response sent from the Godot plugin back to the Python server."""

    request_id: str
    status: Literal["ok", "error"]
    data: dict[str, Any] = Field(default_factory=dict)
    error: ErrorDetail | None = None
    readiness: Readiness
    ## Optional monotonic-ish counters stamped by newer plugins after each
    ## command. Components may reset independently (game run rotation), so the
    ## server compares per key and treats decreases as a reset baseline.
    error_watermark: ErrorWatermark | None = None


class ErrorDetail(BaseModel):
    """Structured error information from the plugin."""

    code: str
    message: str
    data: dict[str, Any] = Field(default_factory=dict)


class AuthenticationHello(BaseModel):
    """Metadata-free first message for the single v4 editor protocol."""

    model_config = ConfigDict(extra="forbid")

    type: Literal["auth_hello"]
    protocol_version: Literal[2]
    client_nonce: NonceHex


class AuthenticatedHandshake(BaseModel):
    """Editor identity disclosed only after it verifies the server proof."""

    model_config = ConfigDict(extra="forbid")

    type: Literal["auth_response"]
    protocol_version: Literal[2]
    client_nonce: NonceHex
    server_nonce: NonceHex
    client_proof: ProofHex
    session_id: SessionId
    godot_version: VersionToken
    project_path: Annotated[StrictStr, Field(min_length=1, max_length=4096)]
    plugin_version: VersionToken
    readiness: Readiness
    editor_pid: Annotated[StrictInt, Field(ge=0, le=(1 << 63) - 1)]
    server_launch_mode: Annotated[
        StrictStr,
        Field(pattern=r"^[A-Za-z0-9._+-]{1,32}$"),
    ]


## State events emitted by the plugin's _check_state_changes() poller. Each
## carries one typed string field. Validating them on receive prevents a
## malformed event (or a hijacked WS) from setting non-string values on the
## Session, which then ship to MCP clients verbatim via Session.to_dict().
## See audit-v2 finding #7 (issue #351).


class SceneChangedEvent(BaseModel):
    current_scene: Annotated[StrictStr, Field(max_length=4096)]


class PlayStateChangedEvent(BaseModel):
    play_state: Literal["stopped", "playing"]


class ReadinessChangedEvent(BaseModel):
    readiness: Readiness


## Plugin-emitted telemetry event. The plugin relays its own events
## (self-update outcome, plugin reload, dock startup) through this
## envelope so opt-out / endpoint / customer_uuid stay in one place
## (Python). The dispatcher in transport/websocket.py validates and
## forwards to ``telemetry.record_telemetry``.
class PluginTelemetryEvent(BaseModel):
    name: str = ""
    data: dict[str, Any] = Field(default_factory=dict)


## Runtime telemetry opt-out (#913). Field-free on purpose: the wire carries
## no way to turn telemetry back *on*, so one editor's opt-out survives
## another's preference on a shared backend. Validated anyway to reject a
## non-dict ``data`` like the other events here.
class TelemetryOptOutEvent(BaseModel):
    pass


class CustomToolsChangedEvent(BaseModel):
    ## Required (no default): a snapshot event without a tools list is
    ## malformed, not "empty". Bounded per the server-side catalog budgets
    ## in services/custom_tool_service.py — the 4 MB WS message cap alone
    ## must not size the per-session catalog.
    tools: list[dict[str, Any]] = Field(max_length=128)
