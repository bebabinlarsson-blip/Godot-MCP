"""Unit tests for tunnel supervisor and URL extraction."""

from __future__ import annotations

import argparse
import json
import re
import threading
import time
from io import BytesIO
from unittest.mock import MagicMock, patch
from urllib.error import HTTPError

import pytest

from godot_ai import _add_tunnel_argument, _uses_automatic_tunnel
from godot_ai.transport.tunnel import (
    _CF_URL_REGEX,
    _SSH_URL_REGEX,
    _TAILSCALE_URL_REGEX,
    _start_tunnel_for_provider,
    DEFAULT_TUNNEL_PROVIDER,
    _ngrok_endpoint_for_port,
    _verify_local_auth,
    _wait_for_tunnel_match,
    find_tunnel_binary,
    start_cloudflare_named_tunnel,
    start_cloudflare_quick_tunnel,
    start_ssh_tunnel,
    start_tailscale_funnel_tunnel,
)


def test_legacy_tunnel_flag_uses_shared_provider_default():
    parser = argparse.ArgumentParser()
    _add_tunnel_argument(parser)

    assert DEFAULT_TUNNEL_PROVIDER == "localhost.run"
    assert parser.parse_args(["--tunnel"]).tunnel == DEFAULT_TUNNEL_PROVIDER
    assert parser.parse_args(["--tunnel", "cloudflare"]).tunnel == "cloudflare"
    assert parser.parse_args(["--tunnel", "cloudflare-named"]).tunnel == "cloudflare-named"
    assert parser.parse_args(["--tunnel", "tailscale-funnel"]).tunnel == "tailscale-funnel"


def test_tunnel_cli_accepts_named_cloudflare_provider():
    from godot_ai import main

    with (
        patch("godot_ai.runtime_dependencies.verify_runtime_dependencies"),
        patch("godot_ai.transport.tunnel.run_tunnel_forever") as run_tunnel,
    ):
        main(["tunnel", "--provider", "cloudflare-named"])

    run_tunnel.assert_called_once()
    assert run_tunnel.call_args.args[1] == "cloudflare-named"


def test_tunnel_cli_accepts_ngrok_provider():
    from godot_ai import main

    with (
        patch("godot_ai.runtime_dependencies.verify_runtime_dependencies"),
        patch("godot_ai.transport.tunnel.run_tunnel_forever") as run_tunnel,
    ):
        main(["tunnel", "--provider", "ngrok"])

    run_tunnel.assert_called_once()
    assert run_tunnel.call_args.args[1] == "ngrok"


def test_tunnel_cli_accepts_tailscale_funnel_provider():
    from godot_ai import main

    with (
        patch("godot_ai.runtime_dependencies.verify_runtime_dependencies"),
        patch("godot_ai.transport.tunnel.run_tunnel_forever") as run_tunnel,
    ):
        main(["tunnel", "--provider", "tailscale-funnel"])

    run_tunnel.assert_called_once()
    assert run_tunnel.call_args.args[1] == "tailscale-funnel"


def test_manual_tunnel_does_not_request_public_bind():
    assert not _uses_automatic_tunnel(None)
    assert not _uses_automatic_tunnel("manual")
    assert _uses_automatic_tunnel("cloudflare")
    assert _uses_automatic_tunnel("tailscale-funnel")


def test_tailscale_provider_dispatches_to_funnel_starter():
    expected = object()
    with patch(
        "godot_ai.transport.tunnel.start_tailscale_funnel_tunnel",
        return_value=expected,
    ) as start:
        assert _start_tunnel_for_provider(8123, "tailscale-funnel") is expected
    start.assert_called_once_with(8123)


def test_ssh_url_regex_matches():
    # Serveo URL format
    serveo_line = "Forwarding HTTP traffic from https://40cf1dfc750df797-109-104-14-146.serveousercontent.com"
    match = _SSH_URL_REGEX.search(serveo_line)
    assert match is not None
    assert match.group(0) == "https://40cf1dfc750df797-109-104-14-146.serveousercontent.com"

    # localhost.run URL format
    lhr_line = "e91fbf1a264952.lhr.life tunneled with tls termination, https://e91fbf1a264952.lhr.life"
    match_lhr = _SSH_URL_REGEX.search(lhr_line)
    assert match_lhr is not None
    assert match_lhr.group(0) == "https://e91fbf1a264952.lhr.life"

    # Pinggy link formats
    pinggy_line = "https://njqgh-109-104-14-146.run.pinggy-free.link"
    match_pinggy = _SSH_URL_REGEX.search(pinggy_line)
    assert match_pinggy is not None
    assert match_pinggy.group(0) == "https://njqgh-109-104-14-146.run.pinggy-free.link"

    pinggy_net = "https://tfyux-109-104-14-146.free.pinggy.net"
    match_pnet = _SSH_URL_REGEX.search(pinggy_net)
    assert match_pnet is not None
    assert match_pnet.group(0) == "https://tfyux-109-104-14-146.free.pinggy.net"

    # Should NOT match admin.localhost.run
    assert _SSH_URL_REGEX.search("https://admin.localhost.run/") is None


def test_cloudflare_url_regex_matches():
    cf_line = "|  https://phys-brochures-hart-indicate.trycloudflare.com  |"
    match = _CF_URL_REGEX.search(cf_line)
    assert match is not None
    assert match.group(0) == "https://phys-brochures-hart-indicate.trycloudflare.com"


def test_tailscale_url_regex_matches_only_ts_net_hosts():
    match = _TAILSCALE_URL_REGEX.search(
        "Available on the internet: https://godot-host.personal-tailnet.ts.net\n"
    )
    assert match is not None
    assert match.group(0) == "https://godot-host.personal-tailnet.ts.net"
    assert _TAILSCALE_URL_REGEX.search("https://godot-host.ts.net.attacker.example") is None


def test_find_tunnel_binary():
    assert find_tunnel_binary("ssh") is not None
    assert find_tunnel_binary("serveo") is not None
    assert find_tunnel_binary("pinggy") is not None
    assert find_tunnel_binary("localhost.run") is not None


def test_start_ssh_tunnel_success():
    fake_proc = MagicMock()
    fake_proc.stdout.readline.side_effect = [
        "Warning: Permanently added 'serveo.net' (ED25519) to the list of known hosts.\n",
        "Forwarding HTTP traffic from https://my-tunnel.serveousercontent.com\n",
    ]

    with (
        patch("godot_ai.transport.tunnel._verify_local_auth"),
        patch("subprocess.Popen", return_value=fake_proc),
    ):
        info = start_ssh_tunnel(8000, service="serveo")
        assert info.provider == "ssh_serveo"
        assert info.public_url == "https://my-tunnel.serveousercontent.com"
        assert info.openapi_url == "https://my-tunnel.serveousercontent.com/openapi.json"


def test_start_cloudflare_tunnel_success():
    fake_proc = MagicMock()
    fake_proc.stdout.readline.side_effect = [
        "Requesting new quick Tunnel on trycloudflare.com...\n",
        "|  https://quick-test.trycloudflare.com  |\n",
    ]

    with (
        patch("godot_ai.transport.tunnel.find_tunnel_binary", return_value="cloudflared"),
        patch("godot_ai.transport.tunnel._verify_local_auth"),
        patch("subprocess.Popen", return_value=fake_proc),
    ):
        info = start_cloudflare_quick_tunnel(8000)
        assert info.provider == "cloudflare"
        assert info.public_url == "https://quick-test.trycloudflare.com"
        assert info.openapi_url == "https://quick-test.trycloudflare.com/openapi.json"


def test_tunnel_startup_reader_times_out_if_output_read_blocks():
    read_started = threading.Event()
    release_read = threading.Event()

    class BlockingStdout:
        def readline(self):
            read_started.set()
            release_read.wait(timeout=1)
            return ""

    fake_proc = MagicMock()
    fake_proc.stdout = BlockingStdout()
    fake_proc.poll.return_value = None
    started = time.monotonic()
    try:
        match, lines = _wait_for_tunnel_match(fake_proc, re.compile(r"https://example\.com"), 0.05)
    finally:
        release_read.set()

    assert read_started.wait(timeout=0.5)
    assert time.monotonic() - started < 0.75
    assert match is None
    assert lines == []


def test_ngrok_endpoint_lookup_uses_current_api_and_requested_upstream_port():
    payload = {
        "endpoints": [
            {
                "url": "https://other.ngrok.app",
                "upstream": {"url": "http://localhost:9000"},
            },
            {
                "url": "https://godot.example.ngrok.app",
                "upstream": {"url": "http://127.0.0.1:8123"},
            },
        ]
    }
    with patch(
        "godot_ai.transport.tunnel.urllib.request.urlopen",
        return_value=BytesIO(json.dumps(payload).encode()),
    ) as urlopen:
        assert _ngrok_endpoint_for_port(8123) == "https://godot.example.ngrok.app"

    assert urlopen.call_args.args[0] == "http://127.0.0.1:4040/api/endpoints"


def test_ngrok_endpoint_lookup_rejects_non_https_and_wrong_upstream_port():
    payload = {
        "endpoints": [
            {"url": "http://godot.example.ngrok.app", "upstream": {"url": "127.0.0.1:8123"}},
            {"url": "https://godot.example.ngrok.app", "upstream": {"url": "127.0.0.1:9000"}},
        ]
    }
    with patch(
        "godot_ai.transport.tunnel.urllib.request.urlopen",
        return_value=BytesIO(json.dumps(payload).encode()),
    ):
        assert _ngrok_endpoint_for_port(8123) is None


def test_ngrok_provider_starts_and_returns_its_matching_public_url(monkeypatch):
    monkeypatch.setenv("GODOT_AI_AUTH_TOKEN", "mcp-auth-secret")
    fake_proc = MagicMock()
    fake_proc.poll.return_value = None
    with (
        patch("godot_ai.transport.tunnel._verify_local_auth"),
        patch("godot_ai.transport.tunnel.find_tunnel_binary", return_value="ngrok"),
        patch(
            "godot_ai.transport.tunnel._ngrok_endpoint_for_port",
            return_value="https://godot.ngrok.app",
        ),
        patch("godot_ai.transport.tunnel._start_keepalive_worker"),
        patch("subprocess.Popen", return_value=fake_proc) as popen,
    ):
        from godot_ai.transport.tunnel import _start_tunnel_for_provider

        info = _start_tunnel_for_provider(8123, "ngrok")

    assert popen.call_args.args[0] == ["ngrok", "http", "127.0.0.1:8123"]
    assert info.provider == "ngrok"
    assert info.public_url == "https://godot.ngrok.app"
    assert info.openapi_url == "https://godot.ngrok.app/openapi.json"


def test_named_cloudflare_tunnel_uses_token_file_and_stable_https_url(monkeypatch, tmp_path):
    token_file = tmp_path / "tunnel-token"
    token_file.write_text("secret-token", encoding="utf-8")
    monkeypatch.setenv("GODOT_AI_CLOUDFLARE_TUNNEL_TOKEN_FILE", str(token_file))
    monkeypatch.setenv("GODOT_AI_TUNNEL_PUBLIC_URL", "https://mcp.example.com/")
    monkeypatch.setenv("GODOT_AI_AUTH_TOKEN", "mcp-auth-secret")

    fake_proc = MagicMock()
    fake_proc.stdout.readline.side_effect = [
        "Registered tunnel connection connIndex=0\n",
    ]
    with (
        patch("godot_ai.transport.tunnel.find_tunnel_binary", return_value="cloudflared"),
        patch("godot_ai.transport.tunnel._verify_local_auth"),
        patch("subprocess.Popen", return_value=fake_proc) as popen,
    ):
        info = start_cloudflare_named_tunnel(8000)

    command = popen.call_args.args[0]
    assert command[:4] == ["cloudflared", "tunnel", "run", "--token-file"]
    assert command[4] == str(token_file)
    assert "secret-token" not in command
    assert info.provider == "cloudflare-named"
    assert info.public_url == "https://mcp.example.com"
    assert info.openapi_url == "https://mcp.example.com/openapi.json"


def test_tailscale_funnel_forwards_authenticated_local_server(monkeypatch):
    monkeypatch.setenv("GODOT_AI_AUTH_TOKEN", "mcp-auth-secret")
    fake_proc = MagicMock()
    fake_proc.stdout.readline.side_effect = [
        "Available on the internet: https://godot-host.personal-tailnet.ts.net\n",
    ]
    with (
        patch("godot_ai.transport.tunnel.find_tunnel_binary", return_value="tailscale"),
        patch("godot_ai.transport.tunnel._verify_local_auth") as verify_auth,
        patch("godot_ai.transport.tunnel._start_keepalive_worker") as keepalive,
        patch("subprocess.Popen", return_value=fake_proc) as popen,
    ):
        info = start_tailscale_funnel_tunnel(8123)

    assert popen.call_args.args[0] == [
        "tailscale",
        "funnel",
        "--yes",
        "--https=443",
        "http://127.0.0.1:8123",
    ]
    verify_auth.assert_called_once_with(8123, "mcp-auth-secret")
    keepalive.assert_called_once_with("https://godot-host.personal-tailnet.ts.net", fake_proc)
    assert info.provider == "tailscale-funnel"
    assert info.public_url == "https://godot-host.personal-tailnet.ts.net"
    assert info.openapi_url == "https://godot-host.personal-tailnet.ts.net/openapi.json"


def test_named_tunnel_requires_local_server_authentication(monkeypatch):
    monkeypatch.delenv("GODOT_AI_AUTH_TOKEN", raising=False)

    with pytest.raises(RuntimeError, match="GODOT_AI_AUTH_TOKEN"):
        _verify_local_auth(8000, "")


def test_named_tunnel_checks_that_local_server_requires_and_accepts_token(monkeypatch):
    class Response:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

    monkeypatch.setenv("GODOT_AI_AUTH_TOKEN", "expected-token")
    requests = []

    def fake_urlopen(request, timeout):
        requests.append((request, timeout))
        if isinstance(request, str):
            raise HTTPError(request, 401, "unauthorized", {}, BytesIO())
        return Response()

    with patch("godot_ai.transport.tunnel.urllib.request.urlopen", side_effect=fake_urlopen):
        _verify_local_auth(8123, "expected-token")

    assert requests[0][0] == "http://127.0.0.1:8123/api/v1/status"
    assert requests[1][0].full_url == "http://127.0.0.1:8123/api/v1/status"
    assert requests[1][0].get_header("Authorization") == "Bearer expected-token"


def test_keepalive_uses_authenticated_status_endpoint(monkeypatch):
    from godot_ai.transport.tunnel import _start_keepalive_worker

    monkeypatch.setenv("GODOT_AI_AUTH_TOKEN", "expected-token")
    completed = threading.Event()
    calls = []
    poll_count = 0

    class Process:
        def poll(self):
            nonlocal poll_count
            poll_count += 1
            return None if poll_count <= 2 else 0

    def fake_urlopen(request, timeout):
        calls.append((request, timeout))
        completed.set()
        return MagicMock()

    with (
        patch("godot_ai.transport.tunnel.time.sleep"),
        patch("godot_ai.transport.tunnel.urllib.request.urlopen", side_effect=fake_urlopen),
    ):
        _start_keepalive_worker("https://mcp.example.com", Process(), interval=0)
        assert completed.wait(1), "keepalive should request the status endpoint"

    request, timeout = calls[0]
    assert request.full_url == "https://mcp.example.com/api/v1/status"
    assert request.get_header("Authorization") == "Bearer expected-token"
    assert timeout == 8


@pytest.mark.parametrize(
    ("public_url", "message"),
    [
        ("http://mcp.example.com", "stable HTTPS hostname"),
        ("https://mcp.example.com/path", "stable HTTPS hostname"),
        ("https://user@mcp.example.com", "stable HTTPS hostname"),
    ],
)
def test_named_cloudflare_tunnel_rejects_non_host_urls(
    monkeypatch, tmp_path, public_url, message
):
    token_file = tmp_path / "tunnel-token"
    token_file.write_text("secret-token", encoding="utf-8")
    monkeypatch.setenv("GODOT_AI_CLOUDFLARE_TUNNEL_TOKEN_FILE", str(token_file))
    monkeypatch.setenv("GODOT_AI_TUNNEL_PUBLIC_URL", public_url)

    with pytest.raises(RuntimeError, match=message):
        start_cloudflare_named_tunnel(8000)
