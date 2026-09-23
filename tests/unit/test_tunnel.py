"""Unit tests for tunnel supervisor and URL extraction."""

from __future__ import annotations

import re
from unittest.mock import MagicMock, patch

import pytest

from godot_ai.transport.tunnel import (
    _CF_URL_REGEX,
    _SSH_URL_REGEX,
    find_tunnel_binary,
    run_tunnel_forever,
    start_cloudflare_quick_tunnel,
    start_ssh_tunnel,
)


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


def test_cloudflare_url_regex_matches():
    cf_line = "|  https://phys-brochures-hart-indicate.trycloudflare.com  |"
    match = _CF_URL_REGEX.search(cf_line)
    assert match is not None
    assert match.group(0) == "https://phys-brochures-hart-indicate.trycloudflare.com"


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

    with patch("subprocess.Popen", return_value=fake_proc):
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
        patch("subprocess.Popen", return_value=fake_proc),
    ):
        info = start_cloudflare_quick_tunnel(8000)
        assert info.provider == "cloudflare"
        assert info.public_url == "https://quick-test.trycloudflare.com"
        assert info.openapi_url == "https://quick-test.trycloudflare.com/openapi.json"
