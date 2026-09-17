"""Focused contracts for the one editor-connection table."""

from __future__ import annotations

import json
from dataclasses import FrozenInstanceError

import pytest

from godot_ai.sessions.registry import (
    PendingCommandLimitError,
    Session,
    SessionRegistry,
)
from godot_ai.transport.websocket import GodotWebSocketServer, websocket_client_proof

_CAPABILITY = "01" * 32


class _Peer:
    async def send(self, _payload: str) -> None:
        return None


def _session(session_id: str) -> Session:
    return Session(
        session_id=session_id,
        godot_version="4.7",
        project_path=f"/tmp/{session_id}",
        plugin_version="4.0.0",
        error_watermark={"run_seq": 1},
    )


def _publish(table: SessionRegistry, session_id: str) -> _Peer:
    peer = _Peer()
    assert table.reserve_connection(_session(session_id), peer)
    table.publish_connection(session_id, peer)
    return peer


def test_one_map_owns_session_peer_and_pending_membership() -> None:
    table = SessionRegistry()
    server = GodotWebSocketServer(table)

    assert "_entries" in vars(table)
    assert "_sessions" not in vars(table)
    assert "_connections" not in vars(server)
    assert "_pending" not in vars(server)


def test_session_snapshots_are_frozen_and_do_not_alias_nested_maps() -> None:
    source_watermark = {"run_seq": 1}
    session = Session(
        session_id="immutable",
        godot_version="4.7",
        project_path="/tmp/immutable",
        plugin_version="4.0.0",
        error_watermark=source_watermark,
    )
    table = SessionRegistry()
    table.register(session)
    snapshot = table.get("immutable")
    assert snapshot is not None

    source_watermark["run_seq"] = 99
    assert snapshot.error_watermark["run_seq"] == 1
    assert not hasattr(snapshot, "__dict__")
    with pytest.raises(FrozenInstanceError):
        snapshot.readiness = "playing"  # type: ignore[misc]
    with pytest.raises(TypeError):
        snapshot.error_watermark["run_seq"] = 2  # type: ignore[index]

    table.record_readiness("immutable", "playing")
    assert snapshot.readiness == "ready"
    live = table.get("immutable")
    assert live.readiness == "playing"
    assert live.error_watermark is snapshot.error_watermark

    table.record_scene_changed("immutable", "res://main.tscn")
    assert table.get("immutable").error_watermark is snapshot.error_watermark


async def test_response_claim_is_scoped_to_the_source_peer() -> None:
    table = SessionRegistry()
    owner_peer = _publish(table, "owner")
    forger_peer = _publish(table, "forger")
    _peer, future = table.open_request("owner", "request-1")

    assert table.claim_pending_response("forger", "request-1", peer=forger_peer) is None
    assert not future.done()
    assert table.pending_count == 1

    claimed = table.claim_pending_response("owner", "request-1", peer=owner_peer)
    assert claimed is future
    claimed.set_result("accepted")
    assert await future == "accepted"
    assert table.pending_count == 0


async def test_stale_peer_cannot_claim_after_same_id_reconnect() -> None:
    table = SessionRegistry()
    stale_peer = _publish(table, "reused")
    assert table.remove_connection("reused", peer=stale_peer)
    current_peer = _publish(table, "reused")
    _peer, future = table.open_request("reused", "same-request-id")

    assert table.claim_pending_response("reused", "same-request-id", peer=stale_peer) is None
    assert not future.done()
    assert table.pending_count == 1

    claimed = table.claim_pending_response(
        "reused",
        "same-request-id",
        peer=current_peer,
    )
    assert claimed is future
    claimed.set_result("current")
    assert await future == "current"


async def test_cancelled_request_cannot_authorize_late_response_side_effects() -> None:
    table = SessionRegistry()
    peer = _publish(table, "late")
    _peer, future = table.open_request("late", "timed-out")
    future.cancel()

    assert table.claim_pending_response("late", "timed-out", peer=peer) is None
    assert table.pending_count == 0


async def test_stale_peer_cannot_cancel_after_same_id_reconnect() -> None:
    table = SessionRegistry()
    stale_peer = _publish(table, "cancel-reused")
    assert table.remove_connection("cancel-reused", peer=stale_peer)
    current_peer = _publish(table, "cancel-reused")
    _peer, future = table.open_request("cancel-reused", "same-request-id")

    assert not table.cancel_request(
        "cancel-reused",
        "same-request-id",
        peer=stale_peer,
    )
    assert not future.done()
    assert table.cancel_request(
        "cancel-reused",
        "same-request-id",
        peer=current_peer,
    )
    assert future.cancelled()


async def test_local_and_aggregate_pending_budgets_are_independent() -> None:
    table = SessionRegistry(max_pending_per_peer=1, max_pending_total=2)
    _publish(table, "a")
    _publish(table, "b")
    _publish(table, "c")
    table.open_request("a", "a-1")

    with pytest.raises(PendingCommandLimitError, match="per-peer limit 1"):
        table.open_request("a", "a-2")

    table.open_request("b", "b-1")
    with pytest.raises(PendingCommandLimitError, match="aggregate limit 2"):
        table.open_request("c", "c-1")

    assert table.pending_count == 2
    table.remove_connection("a")
    table.remove_connection("b")


async def test_removal_is_atomic_and_fails_only_that_peers_requests() -> None:
    table = SessionRegistry()
    owner_peer = _publish(table, "owner")
    _publish(table, "survivor")
    _peer, removed_future = table.open_request("owner", "owner-1")
    _peer, survivor_future = table.open_request("survivor", "survivor-1")

    assert table.remove_connection("owner", peer=owner_peer)
    assert table.get("owner") is None
    with pytest.raises(ConnectionError, match="No connection"):
        table.open_request("owner", "after-removal")
    assert table.pending_count == 1
    with pytest.raises(ConnectionError, match="disconnected"):
        await removed_future
    assert not survivor_future.done()
    table.remove_connection("survivor")


class _Protocol:
    max_message_size = 8 * 1024


class _AuthenticatedPeer:
    def __init__(self, session_id: str, *, fail_ack: bool = False) -> None:
        self.session_id = session_id
        self.fail_ack = fail_ack
        self.protocol = _Protocol()
        self.client_nonce = "02" * 32
        self.challenge: dict | None = None
        self.closed = False
        self._recv_count = 0

    async def recv(self) -> str:
        self._recv_count += 1
        if self._recv_count == 1:
            return json.dumps(
                {
                    "type": "auth_hello",
                    "protocol_version": 2,
                    "client_nonce": self.client_nonce,
                }
            )
        assert self.challenge is not None
        response = {
            "type": "auth_response",
            "protocol_version": 2,
            "client_nonce": self.client_nonce,
            "server_nonce": self.challenge["server_nonce"],
            "session_id": self.session_id,
            "godot_version": "4.7",
            "project_path": f"/tmp/{self.session_id}",
            "plugin_version": "4.0.0",
            "readiness": "ready",
            "editor_pid": 1,
            "server_launch_mode": "test",
        }
        response["client_proof"] = websocket_client_proof(
            _CAPABILITY,
            client_nonce=response["client_nonce"],
            server_nonce=response["server_nonce"],
            session_id=response["session_id"],
            godot_version=response["godot_version"],
            project_path=response["project_path"],
            plugin_version=response["plugin_version"],
            readiness=response["readiness"],
            editor_pid=response["editor_pid"],
            server_launch_mode=response["server_launch_mode"],
            server_version=self.challenge["server_version"],
        )
        return json.dumps(response)

    async def send(self, payload: str) -> None:
        message = json.loads(payload)
        if message["type"] == "auth_challenge":
            self.challenge = message
        elif self.fail_ack:
            raise ConnectionError("ACK write failed")

    async def close(self, **_kwargs: object) -> None:
        self.closed = True


async def test_ack_send_failure_never_publishes_a_routable_session() -> None:
    table = SessionRegistry()
    server = GodotWebSocketServer(table, auth_token=_CAPABILITY)
    peer = _AuthenticatedPeer("ack-failure", fail_ack=True)

    await server._handle_connection(peer)  # type: ignore[arg-type]

    assert table.get("ack-failure") is None
    assert vars(table)["_entries"] == {}
    assert len(table) == 0


class _ToolCatalogSpy:
    def __init__(self) -> None:
        self.removed: list[str] = []

    def remove_session(self, session_id: str) -> bool:
        self.removed.append(session_id)
        return False


async def test_rejected_duplicate_cannot_cleanup_live_peers_tools() -> None:
    table = SessionRegistry()
    original_peer = _publish(table, "duplicate")
    server = GodotWebSocketServer(table, auth_token=_CAPABILITY)
    catalog = _ToolCatalogSpy()
    server._custom_tool_service = catalog  # type: ignore[assignment]

    await server._handle_connection(_AuthenticatedPeer("duplicate"))  # type: ignore[arg-type]

    assert catalog.removed == []
    assert vars(table)["_entries"]["duplicate"].peer is original_peer
