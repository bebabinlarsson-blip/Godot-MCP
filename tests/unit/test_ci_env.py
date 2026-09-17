"""Contracts for capability-authenticated shell smoke clients."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from godot_ai.transport.capability import (
    CAPABILITY_DIR_ENV,
    HTTP_CAPABILITY_ENV,
    WS_CAPABILITY_ENV,
    write_capabilities,
)

ROOT = Path(__file__).resolve().parents[2]
CI_ENV = ROOT / "script" / "_ci_env.sh"
LOCAL_HTTP_CAPABILITY = "local-ci-http-capability-0123456789abcdef"
REMOTE_HTTP_CAPABILITY = "remote-ci-http-capability-0123456789abcdef"
WS_CAPABILITY = "0123456789abcdef" * 4
INSTANCE_NONCE = "1234567890abcdef1234567890abcdef"


def _environment(**overrides: str) -> dict[str, str]:
    environment = os.environ.copy()
    for name in (CAPABILITY_DIR_ENV, HTTP_CAPABILITY_ENV, WS_CAPABILITY_ENV):
        environment.pop(name, None)
    environment.update(overrides)
    environment["PYTHON_CMD"] = sys.executable
    python_path = [str(ROOT / "src")]
    if inherited := environment.get("PYTHONPATH"):
        python_path.append(inherited)
    environment["PYTHONPATH"] = os.pathsep.join(python_path)
    return environment


def _load_http_auth(environment: dict[str, str]) -> subprocess.CompletedProcess[str]:
    bash = shutil.which("bash")
    if bash is None:
        pytest.skip("bash is required for shell harness contracts")
    return subprocess.run(
        [
            bash,
            "-c",
            'set -euo pipefail; source "$1"; ci_load_http_auth; '
            'printf "%s\\n" "${HTTP_AUTH_HEADERS[@]}"',
            "ci-env-test",
            str(CI_ENV),
        ],
        cwd=ROOT,
        env=environment,
        text=True,
        capture_output=True,
        check=False,
    )


def _capability_fixture(tmp_path: Path) -> tuple[Path, dict[str, str]]:
    if os.name == "nt":
        return tmp_path / "godot-ai" / "capabilities", {"LOCALAPPDATA": str(tmp_path)}
    directory = tmp_path / "capabilities"
    return directory, {CAPABILITY_DIR_ENV: str(directory)}


def test_ci_env_uses_current_capability_api() -> None:
    source = CI_ENV.read_text(encoding="utf-8")

    assert "capability_from_env" not in source
    assert "from _transport_auth import raw_capability" in source
    assert "read_capabilities" not in source
    assert "validate_capability" not in source


@pytest.mark.parametrize(
    "url",
    (
        "http://127.0.0.1:18123/mcp",
        "http://localhost:18123/mcp",
        "http://[::1]:18123/mcp",
    ),
)
def test_ci_env_reads_loopback_capability_record_and_ignores_environment(
    tmp_path: Path,
    url: str,
) -> None:
    capability_dir, capability_environment = _capability_fixture(tmp_path)
    write_capabilities(
        18123,
        LOCAL_HTTP_CAPABILITY,
        WS_CAPABILITY,
        instance_nonce=INSTANCE_NONCE,
        directory=capability_dir,
    )
    result = _load_http_auth(
        _environment(
            **{
                "MCP_SERVER_URL": url,
                **capability_environment,
                HTTP_CAPABILITY_ENV: REMOTE_HTTP_CAPABILITY,
            }
        )
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.splitlines() == [
        "-H",
        f"Authorization: Bearer {LOCAL_HTTP_CAPABILITY}",
    ]


def test_ci_env_validates_remote_http_capability_without_requiring_websocket_token() -> None:
    result = _load_http_auth(
        _environment(
            **{
                "MCP_SERVER_URL": "https://remote.example.invalid/mcp",
                HTTP_CAPABILITY_ENV: REMOTE_HTTP_CAPABILITY,
            }
        )
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.splitlines() == [
        "-H",
        f"Authorization: Bearer {REMOTE_HTTP_CAPABILITY}",
    ]


@pytest.mark.parametrize("capability", (None, "too-short", "a" * 32 + "\nInjected: yes"))
def test_ci_env_rejects_missing_or_invalid_remote_http_capability(
    capability: str | None,
) -> None:
    environment = _environment(MCP_SERVER_URL="https://remote.example.invalid/mcp")
    if capability is not None:
        environment[HTTP_CAPABILITY_ENV] = capability

    result = _load_http_auth(environment)

    assert result.returncode != 0
    assert result.stdout == ""
    assert f"invalid {HTTP_CAPABILITY_ENV}" in result.stderr


def test_ci_env_does_not_fall_back_to_environment_for_missing_loopback_record(
    tmp_path: Path,
) -> None:
    _capability_dir, capability_environment = _capability_fixture(tmp_path)
    result = _load_http_auth(
        _environment(
            **{
                "MCP_SERVER_URL": "http://127.0.0.1:18124/mcp",
                **capability_environment,
                HTTP_CAPABILITY_ENV: REMOTE_HTTP_CAPABILITY,
            }
        )
    )

    assert result.returncode != 0
    assert result.stdout == ""
    assert "missing Godot AI HTTP capability record" in result.stderr


@pytest.mark.parametrize(
    "url",
    (
        "http://remote.example.invalid/mcp",
        "http://127.0.0.1.evil.invalid/mcp",
        "http://localhost@remote.example.invalid/mcp",
        "https://user:password@remote.example.invalid/mcp",
        "ftp://remote.example.invalid/mcp",
        "https:///mcp",
    ),
)
def test_ci_env_rejects_unsafe_target_before_exposing_capability(url: str) -> None:
    result = _load_http_auth(
        _environment(
            **{
                "MCP_SERVER_URL": url,
                HTTP_CAPABILITY_ENV: REMOTE_HTTP_CAPABILITY,
            }
        )
    )
    assert result.returncode != 0
    assert result.stdout == ""
    assert "capability target must be" in result.stderr
    assert REMOTE_HTTP_CAPABILITY not in result.stderr
