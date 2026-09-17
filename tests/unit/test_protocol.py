"""Tests for protocol envelope types."""

import json

import pytest
from pydantic import ValidationError

from godot_ai.protocol.envelope import (
    WS_PROTOCOL_VERSION,
    AuthenticatedHandshake,
    AuthenticationHello,
    CommandRequest,
    CommandResponse,
    ErrorDetail,
)


class TestCommandRequest:
    def test_defaults(self):
        req = CommandRequest(command="get_scene_tree")
        assert req.command == "get_scene_tree"
        assert req.params == {}
        assert len(req.request_id) > 0

    def test_with_params(self):
        req = CommandRequest(command="get_scene_tree", params={"depth": 5})
        assert req.params == {"depth": 5}

    def test_roundtrip_json(self):
        req = CommandRequest(command="test", params={"key": "value"})
        raw = req.model_dump_json()
        parsed = CommandRequest.model_validate_json(raw)
        assert parsed.command == req.command
        assert parsed.request_id == req.request_id
        assert parsed.params == req.params


class TestCommandResponse:
    def test_ok_response(self):
        resp = CommandResponse(
            request_id="abc123",
            status="ok",
            data={"nodes": []},
            readiness="ready",
        )
        assert resp.status == "ok"
        assert resp.error is None

    def test_error_response(self):
        resp = CommandResponse(
            request_id="abc123",
            status="error",
            readiness="ready",
            error=ErrorDetail(
                code="NODE_NOT_FOUND",
                message="Not found",
                data={"path": "/Missing/Node"},
            ),
        )
        assert resp.status == "error"
        assert resp.error.code == "NODE_NOT_FOUND"
        assert resp.error.data == {"path": "/Missing/Node"}

    def test_error_response_defaults_data_to_empty_dict(self):
        resp = CommandResponse(
            request_id="abc123",
            status="error",
            readiness="ready",
            error=ErrorDetail(code="NODE_NOT_FOUND", message="Not found"),
        )
        assert resp.error is not None
        assert resp.error.data == {}

    def test_roundtrip_json(self):
        resp = CommandResponse(
            request_id="abc123",
            status="ok",
            data={"version": "4.4"},
            readiness="ready",
        )
        raw = resp.model_dump_json()
        parsed = CommandResponse.model_validate_json(raw)
        assert parsed.request_id == "abc123"
        assert parsed.data == {"version": "4.4"}

    def test_error_watermark_is_optional(self):
        resp = CommandResponse(
            request_id="abc123",
            status="ok",
            data={},
            readiness="ready",
        )
        assert resp.error_watermark is None

    def test_error_watermark_parses_from_new_plugins(self):
        parsed = CommandResponse.model_validate(
            {
                "request_id": "abc123",
                "status": "ok",
                "data": {},
                "readiness": "ready",
                "error_watermark": {
                    "editor_ring": 1,
                    "debugger_promoted": 2,
                    "game_error_warn": 3,
                },
            }
        )
        assert parsed.error_watermark == {
            "editor_ring": 1,
            "debugger_promoted": 2,
            "game_error_warn": 3,
        }

    def test_error_watermark_accepts_complete_bounded_shape(self):
        watermark = {
            "run_seq": 1,
            "editor_ring": 2,
            "debugger_promoted": 3,
            "game_error_warn": 4,
            "editor_ring_warn": 5,
            "game_warn": (1 << 63) - 1,
        }

        parsed = CommandResponse.model_validate(
            {
                "request_id": "abc123",
                "status": "ok",
                "readiness": "ready",
                "error_watermark": watermark,
            }
        )

        assert parsed.error_watermark == watermark

    def test_error_watermark_rejects_extra_component(self):
        with pytest.raises(ValidationError):
            CommandResponse.model_validate(
                {
                    "request_id": "abc123",
                    "status": "ok",
                    "readiness": "ready",
                    "error_watermark": {
                        "run_seq": 1,
                        "editor_ring": 2,
                        "debugger_promoted": 3,
                        "game_error_warn": 4,
                        "editor_ring_warn": 5,
                        "game_warn": 6,
                        "attacker_component": 7,
                    },
                }
            )

    @pytest.mark.parametrize("value", [True, "1", 1.5, -1, 1 << 63])
    def test_error_watermark_rejects_invalid_counter_shape(self, value):
        with pytest.raises(ValidationError):
            CommandResponse.model_validate(
                {
                    "request_id": "abc123",
                    "status": "ok",
                    "readiness": "ready",
                    "error_watermark": {"run_seq": value},
                }
            )


class TestV4HandshakeModels:
    NONCE = "01" * 32
    PROOF = "02" * 32

    @classmethod
    def response(cls, **changes):
        value = {
            "type": "auth_response",
            "protocol_version": WS_PROTOCOL_VERSION,
            "client_nonce": cls.NONCE,
            "server_nonce": "03" * 32,
            "client_proof": cls.PROOF,
            "session_id": "my-game@a3f2",
            "godot_version": "4.7.0",
            "project_path": "/tmp/project",
            "plugin_version": "4.0.0",
            "readiness": "ready",
            "editor_pid": 123,
            "server_launch_mode": "dev_venv",
        }
        value.update(changes)
        return value

    def test_auth_hello_is_metadata_free_and_exact(self):
        hello = AuthenticationHello.model_validate(
            {
                "type": "auth_hello",
                "protocol_version": WS_PROTOCOL_VERSION,
                "client_nonce": self.NONCE,
            }
        )
        assert json.loads(hello.model_dump_json()) == {
            "type": "auth_hello",
            "protocol_version": WS_PROTOCOL_VERSION,
            "client_nonce": self.NONCE,
        }

    @pytest.mark.parametrize("field", ["session_id", "project_path", "auth_token"])
    def test_auth_hello_rejects_metadata_and_raw_token(self, field):
        with pytest.raises(ValidationError):
            AuthenticationHello.model_validate(
                {
                    "type": "auth_hello",
                    "protocol_version": WS_PROTOCOL_VERSION,
                    "client_nonce": self.NONCE,
                    field: "attacker-controlled",
                }
            )

    @pytest.mark.parametrize("nonce", ["", "0" * 63, "0" * 65, "g" * 64])
    def test_auth_hello_requires_fresh_nonce_shape(self, nonce):
        with pytest.raises(ValidationError):
            AuthenticationHello(
                type="auth_hello",
                protocol_version=WS_PROTOCOL_VERSION,
                client_nonce=nonce,
            )

    def test_authenticated_metadata_has_no_legacy_defaults(self):
        parsed = AuthenticatedHandshake.model_validate(self.response())
        assert parsed.session_id == "my-game@a3f2"
        for required in ("readiness", "editor_pid", "server_launch_mode", "client_proof"):
            value = self.response()
            value.pop(required)
            with pytest.raises(ValidationError):
                AuthenticatedHandshake.model_validate(value)

    @pytest.mark.parametrize("protocol_version", [1, 3, "2"])
    def test_mixed_protocol_version_rejected(self, protocol_version):
        with pytest.raises(ValidationError):
            AuthenticationHello.model_validate(
                {
                    "type": "auth_hello",
                    "protocol_version": protocol_version,
                    "client_nonce": self.NONCE,
                }
            )

    @pytest.mark.parametrize(
        "bad_id",
        [
            "",  # empty
            "has space",  # whitespace
            "a/b/../etc",  # path separators / traversal shape
            "x" * 129,  # over the 128 bound
            "emoji😀",  # non-ASCII control/payload
        ],
    )
    def test_malformed_session_id_rejected(self, bad_id):
        ## An untrusted WS peer can't register an arbitrary/oversized id that
        ## then flows into the registry key, logs, and telemetry hash (#527).
        with pytest.raises(ValidationError):
            AuthenticatedHandshake.model_validate(self.response(session_id=bad_id))
