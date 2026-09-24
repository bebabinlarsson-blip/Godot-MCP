"""Cloud tunnel supervisor for exposing local Godot AI to ChatGPT on the web."""

from __future__ import annotations

import asyncio
import json
import logging
import os
import queue
import re
import shutil
import subprocess
import threading
import time
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Literal
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit

logger = logging.getLogger(__name__)

TunnelProvider = Literal[
    "serveo",
    "cloudflare",
    "cloudflare-named",
    "tailscale-funnel",
    "ngrok",
    "ssh",
    "pinggy",
    "localhost.run",
    "manual",
]
DEFAULT_TUNNEL_PROVIDER: TunnelProvider = "localhost.run"

_MAX_RECONNECT_DELAY = 30
_INITIAL_RECONNECT_DELAY = 2


@dataclass
class TunnelInfo:
    provider: str
    public_url: str
    openapi_url: str
    process: subprocess.Popen[str] | None = None


_CF_URL_REGEX = re.compile(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com")
_NGROK_URL_REGEX = re.compile(r"https://[a-zA-Z0-9-]+\.ngrok-free\.app")
_SSH_URL_REGEX = re.compile(
    r"https?://(?!admin\.)[a-zA-Z0-9.-]+\.(?:serveousercontent\.com|lhr\.life|localhost\.run|pinggy\.link|a\.pinggy\.link|free\.pinggy\.net|run\.pinggy-free\.link)"
)
_CF_NAMED_READY_REGEX = re.compile(r"Registered tunnel connection", re.IGNORECASE)
_TAILSCALE_URL_REGEX = re.compile(
    r"https://[a-zA-Z0-9.-]+\.ts\.net(?=[\s/|]|$)", re.IGNORECASE
)
TUNNEL_TOKEN_FILE_ENV = "GODOT_AI_CLOUDFLARE_TUNNEL_TOKEN_FILE"
TUNNEL_PUBLIC_URL_ENV = "GODOT_AI_TUNNEL_PUBLIC_URL"
TUNNEL_START_TIMEOUT_SECONDS = 30.0
NGROK_AGENT_API_URL = "http://127.0.0.1:4040/api/endpoints"


def find_tunnel_binary(provider: TunnelProvider = DEFAULT_TUNNEL_PROVIDER) -> str | None:
    """Find binary executable for the requested tunnel provider."""
    if provider in ("cloudflare", "cloudflare-named"):
        return shutil.which("cloudflared")
    if provider == "tailscale-funnel":
        return shutil.which("tailscale")
    if provider == "ngrok":
        return shutil.which("ngrok")
    if provider in ("ssh", "serveo", "pinggy", "localhost.run"):
        return shutil.which("ssh")
    return None


def _wait_for_tunnel_match(
    proc: subprocess.Popen[str], pattern: re.Pattern[str], timeout: float
) -> tuple[str | None, list[str]]:
    """Read tunnel startup output without hanging forever on a silent process."""
    if proc.stdout is None:
        return None, []

    lines: queue.Queue[str | None] = queue.Queue()

    def _read_output() -> None:
        try:
            for line in iter(proc.stdout.readline, ""):
                lines.put(line)
        except Exception:
            logger.debug("Tunnel output reader stopped", exc_info=True)
        finally:
            lines.put(None)

    threading.Thread(target=_read_output, daemon=True, name="TunnelStartupReader").start()
    deadline = time.monotonic() + max(0.0, timeout)
    observed: list[str] = []
    while True:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            return None, observed
        try:
            line = lines.get(timeout=min(0.2, remaining))
        except queue.Empty:
            if proc.poll() is not None:
                return None, observed
            continue
        if line is None:
            return None, observed
        observed.append(line.rstrip())
        match = pattern.search(line)
        if match:
            return match.group(0), observed


def _terminate_tunnel_process(proc: subprocess.Popen[str]) -> None:
    """Stop a tunnel child after startup failure, without leaving a live child."""
    if proc.poll() is not None:
        return
    proc.terminate()
    try:
        proc.wait(timeout=3)
    except (subprocess.TimeoutExpired, OSError):
        try:
            proc.kill()
            proc.wait(timeout=3)
        except (subprocess.TimeoutExpired, OSError):
            logger.warning("Tunnel subprocess did not exit after kill request")


def _ssh_keepalive_opts(null_dev: str) -> list[str]:
    """Common SSH options for aggressive keep-alive and stability."""
    return [
        "-o", "StrictHostKeyChecking=no",
        "-o", f"UserKnownHostsFile={null_dev}",
        "-o", "ServerAliveInterval=10",
        "-o", "ServerAliveCountMax=60",
        "-o", "TCPKeepAlive=yes",
        "-o", "ExitOnForwardFailure=yes",
        "-o", "ConnectTimeout=10",
        "-T",
    ]


def _start_keepalive_worker(
    public_url: str, proc: subprocess.Popen, interval: float = 25.0
) -> None:
    """Send periodic authenticated status checks through the tunnel."""
    def _worker():
        status_url = f"{public_url}/api/v1/status"
        while proc.poll() is None:
            time.sleep(interval)
            if proc.poll() is not None:
                break
            try:
                headers = {"User-Agent": "GodotAI-KeepAlive/1.0"}
                auth_token = os.environ.get("GODOT_AI_AUTH_TOKEN", "").strip()
                if auth_token:
                    headers["Authorization"] = f"Bearer {auth_token}"
                req = urllib.request.Request(
                    status_url,
                    headers=headers,
                )
                with urllib.request.urlopen(req, timeout=8) as _:
                    pass
            except Exception:
                pass

    t = threading.Thread(target=_worker, daemon=True, name="TunnelKeepAlive")
    t.start()


def start_ssh_tunnel(port: int, service: str = "localhost.run") -> TunnelInfo:
    """Start an SSH reverse tunnel using system OpenSSH without extra binaries."""
    _verify_local_auth(port, os.environ.get("GODOT_AI_AUTH_TOKEN", "").strip())
    ssh_bin = find_tunnel_binary("ssh")
    if not ssh_bin:
        raise FileNotFoundError(
            "System ssh client not found. Ensure OpenSSH is installed and in PATH."
        )

    null_dev = "NUL" if subprocess.os.name == "nt" else "/dev/null"
    keepalive = _ssh_keepalive_opts(null_dev)

    if service == "pinggy":
        cmd = [ssh_bin, "-p", "443", "-R", f"0:127.0.0.1:{port}"] + keepalive + ["a.pinggy.io"]
    elif service == "serveo":
        cmd = [ssh_bin, "-R", f"80:127.0.0.1:{port}"] + keepalive + ["serveo.net"]
    else:
        cmd = [ssh_bin, "-R", f"80:127.0.0.1:{port}"] + keepalive + ["nokey@localhost.run"]

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    public_url, _ = _wait_for_tunnel_match(
        proc, _SSH_URL_REGEX, TUNNEL_START_TIMEOUT_SECONDS
    )

    if public_url is None:
        _terminate_tunnel_process(proc)
        if service == "localhost.run":
            logger.warning("localhost.run timed out. Falling back to serveo...")
            return start_ssh_tunnel(port, "serveo")
        if service == "serveo":
            logger.warning("Serveo tunnel timed out. Falling back to pinggy...")
            return start_ssh_tunnel(port, "pinggy")
        raise RuntimeError(f"Failed to obtain public URL from SSH tunnel ({service}).")

    _start_keepalive_worker(public_url, proc)

    return TunnelInfo(
        provider=f"ssh_{service}",
        public_url=public_url,
        openapi_url=f"{public_url}/openapi.json",
        process=proc,
    )


def start_cloudflare_quick_tunnel(port: int) -> TunnelInfo:
    """Start a free, zero-config Cloudflare Quick Tunnel to local port."""
    _verify_local_auth(port, os.environ.get("GODOT_AI_AUTH_TOKEN", "").strip())
    bin_path = find_tunnel_binary("cloudflare")
    if not bin_path:
        logger.info("cloudflared not found, falling back to SSH reverse tunnel...")
        return start_ssh_tunnel(port, "serveo")

    cmd = [
        bin_path,
        "tunnel",
        "--url",
        f"http://127.0.0.1:{port}",
        "--protocol",
        "http2",
        "--no-autoupdate",
    ]
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    public_url, _ = _wait_for_tunnel_match(
        proc, _CF_URL_REGEX, TUNNEL_START_TIMEOUT_SECONDS
    )

    if public_url is None:
        _terminate_tunnel_process(proc)
        logger.warning("Cloudflare tunnel failed. Falling back to SSH tunnel...")
        return start_ssh_tunnel(port, "serveo")

    _start_keepalive_worker(public_url, proc)

    return TunnelInfo(
        provider="cloudflare",
        public_url=public_url,
        openapi_url=f"{public_url}/openapi.json",
        process=proc,
    )


def _cloudflare_named_configuration() -> tuple[Path, str]:
    """Read stable Tunnel configuration without printing its credential."""
    raw_token_file = (
        os.environ.get(TUNNEL_TOKEN_FILE_ENV, "").strip()
        or os.environ.get("TUNNEL_TOKEN_FILE", "").strip()
    )
    if not raw_token_file:
        raise RuntimeError(
            f"Set {TUNNEL_TOKEN_FILE_ENV} to a Cloudflare tunnel token file."
        )

    token_file = Path(raw_token_file).expanduser()
    if not token_file.is_file():
        raise FileNotFoundError(f"Cloudflare tunnel token file does not exist: {token_file}")
    try:
        if not token_file.read_text(encoding="utf-8").strip():
            raise RuntimeError("Cloudflare tunnel token file is empty.")
    except OSError as exc:
        raise RuntimeError("Cloudflare tunnel token file cannot be read.") from exc

    public_url = os.environ.get(TUNNEL_PUBLIC_URL_ENV, "").strip()
    parsed = urlsplit(public_url)
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.username
        or parsed.password
        or parsed.port
        or parsed.path not in ("", "/")
        or parsed.query
        or parsed.fragment
    ):
        raise RuntimeError(
            f"Set {TUNNEL_PUBLIC_URL_ENV} to the stable HTTPS hostname configured in Cloudflare."
        )
    return token_file, public_url.rstrip("/")


def _verify_local_auth(port: int, token: str) -> None:
    """Require the local MCP server to enforce the configured Bearer token."""
    if not token or "\r" in token or "\n" in token:
        raise RuntimeError(
            "Set GODOT_AI_AUTH_TOKEN before exposing a public tunnel."
        )

    status_url = f"http://127.0.0.1:{port}/api/v1/status"
    try:
        response = urllib.request.urlopen(status_url, timeout=3)
    except HTTPError as exc:
        if exc.code != 401:
            raise RuntimeError(
                f"Local MCP status check returned HTTP {exc.code}; expected 401 without a token."
            ) from None
        exc.close()
    except URLError as exc:
        raise RuntimeError(
            "Could not verify the local MCP server. Start Godot with GODOT_AI_AUTH_TOKEN "
            "set before starting this tunnel."
        ) from exc
    else:
        response.close()
        raise RuntimeError(
            "The local MCP status endpoint did not require authentication; set GODOT_AI_AUTH_TOKEN "
            "before exposing a public tunnel."
        )

    request = urllib.request.Request(
        status_url,
        headers={"Authorization": f"Bearer {token}"},
    )
    try:
        with urllib.request.urlopen(request, timeout=3) as response:
            if response.status != 200:
                raise RuntimeError(
                    "Local MCP status check returned HTTP "
                    f"{response.status} with the configured token."
                )
    except HTTPError:
        raise RuntimeError(
            "The local MCP server rejected GODOT_AI_AUTH_TOKEN; use the same token "
            "for Godot and the tunnel process."
        ) from None
    except URLError as exc:
        raise RuntimeError("Could not verify the configured local MCP token.") from exc


def diagnose_named_tunnel(port: int = 8000, check_public: bool = True) -> dict:
    """Check named-tunnel prerequisites and both authenticated endpoints.

    Return only booleans and actionable messages; never return credentials.
    """
    checks: dict[str, dict[str, object]] = {}
    binary_found = bool(find_tunnel_binary("cloudflare-named"))
    checks["cloudflared"] = {
        "ok": binary_found,
        "message": "Ready" if binary_found else "Install cloudflared and add it to PATH",
    }
    public_url = ""
    try:
        _, public_url = _cloudflare_named_configuration()
        checks["hostname_and_token_file"] = {"ok": True, "message": "Configured"}
    except (RuntimeError, FileNotFoundError) as exc:
        checks["hostname_and_token_file"] = {"ok": False, "message": str(exc)}
    token = os.environ.get("GODOT_AI_AUTH_TOKEN", "").strip()
    try:
        _verify_local_auth(port, token)
        checks["local_auth"] = {
            "ok": True,
            "message": "Anonymous access denied; configured token accepted",
        }
    except RuntimeError as exc:
        checks["local_auth"] = {"ok": False, "message": str(exc)}
    if check_public and public_url and checks["local_auth"]["ok"]:
        url = f"{public_url}/api/v1/status"
        try:
            with urllib.request.urlopen(url, timeout=5):
                checks["public_auth"] = {
                    "ok": False, "message": "Public endpoint allows anonymous access",
                }
        except HTTPError as exc:
            checks["public_auth"] = {
                "ok": exc.code == 401,
                "message": f"Anonymous response: HTTP {exc.code}",
            }
            exc.close()
        except (URLError, TimeoutError):
            checks["public_auth"] = {
                "ok": False,
                "message": "Public hostname is unreachable; check DNS, tunnel process and route",
            }
        if checks["public_auth"]["ok"]:
            try:
                request = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
                with urllib.request.urlopen(request, timeout=5) as response:
                    checks["public_tools"] = {
                        "ok": response.status == 200,
                        "message": f"Status HTTP {response.status}",
                    }
                tools_request = urllib.request.Request(
                    f"{public_url}/api/v1/tools", headers={"Authorization": f"Bearer {token}"}
                )
                with urllib.request.urlopen(tools_request, timeout=5) as response:
                    tools_payload = json.load(response)
                    catalog_ready = (
                        response.status == 200
                        and isinstance(tools_payload, dict)
                        and tools_payload.get("count", 0) > 0
                    )
                    checks["public_tools"] = {
                        "ok": catalog_ready,
                        "message": "Authenticated tool catalog available" if catalog_ready
                        else "Remote tool catalog is empty",
                    }
            except (HTTPError, URLError, TimeoutError, ValueError):
                checks["public_tools"] = {
                    "ok": False,
                    "message": "Authenticated remote status or tool catalog unavailable",
                }
    return {
        "ready": all(c["ok"] for c in checks.values()),
        "public_url": public_url,
        "checks": checks,
    }


def start_cloudflare_named_tunnel(port: int) -> TunnelInfo:
    """Start a named Cloudflare Tunnel with its stable, user-owned hostname.

    Cloudflare routes this hostname to the local service in the dashboard. The
    token stays in a file and is passed using cloudflared's ``--token-file``
    option, so it is never added to the process command line or logs.
    """
    token_file, public_url = _cloudflare_named_configuration()
    bin_path = find_tunnel_binary("cloudflare-named")
    if not bin_path:
        raise FileNotFoundError(
            "cloudflared is required for a named Cloudflare Tunnel; install it and retry."
        )
    _verify_local_auth(port, os.environ.get("GODOT_AI_AUTH_TOKEN", "").strip())

    proc = subprocess.Popen(
        [bin_path, "tunnel", "run", "--token-file", str(token_file)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    ready, _ = _wait_for_tunnel_match(
        proc, _CF_NAMED_READY_REGEX, TUNNEL_START_TIMEOUT_SECONDS
    )
    if ready is None:
        _terminate_tunnel_process(proc)
        raise RuntimeError(
            "cloudflared did not establish a named tunnel connection within "
            f"{TUNNEL_START_TIMEOUT_SECONDS:g} seconds. Check the token, hostname route, "
            "and network access."
        )

    _start_keepalive_worker(public_url, proc)
    return TunnelInfo(
        provider="cloudflare-named",
        public_url=public_url,
        openapi_url=f"{public_url}/openapi.json",
        process=proc,
    )


def start_tailscale_funnel_tunnel(port: int) -> TunnelInfo:
    """Expose the local, authenticated MCP server through a stable Tailscale URL.

    Tailscale Funnel uses the device's ``*.ts.net`` HTTPS name and does not
    require a separately purchased domain. The Tailscale client and Funnel
    policy must already be configured on the host. The foreground process is
    intentionally retained so the tunnel supervisor can detect drops and
    reconnect without losing the stable device hostname.
    """
    _verify_local_auth(port, os.environ.get("GODOT_AI_AUTH_TOKEN", "").strip())
    bin_path = find_tunnel_binary("tailscale-funnel")
    if not bin_path:
        raise FileNotFoundError(
            "Tailscale CLI is required for Tailscale Funnel; install Tailscale, sign in, "
            "and enable Funnel for this device."
        )

    proc = subprocess.Popen(
        [
            bin_path,
            "funnel",
            "--yes",
            "--https=443",
            f"http://127.0.0.1:{port}",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    public_url, _ = _wait_for_tunnel_match(
        proc, _TAILSCALE_URL_REGEX, TUNNEL_START_TIMEOUT_SECONDS
    )
    if public_url is None:
        _terminate_tunnel_process(proc)
        raise RuntimeError(
            "Tailscale Funnel did not publish a *.ts.net HTTPS URL within "
            f"{TUNNEL_START_TIMEOUT_SECONDS:g} seconds. Sign in to Tailscale, enable Funnel "
            "for the tailnet, and check that port 443 is not already used by Serve."
        )

    _start_keepalive_worker(public_url, proc)
    return TunnelInfo(
        provider="tailscale-funnel",
        public_url=public_url.rstrip("/"),
        openapi_url=f"{public_url.rstrip('/')}/openapi.json",
        process=proc,
    )


def _ngrok_endpoint_for_port(port: int) -> str | None:
    """Return a public HTTPS endpoint forwarding to the requested local port."""
    try:
        with urllib.request.urlopen(NGROK_AGENT_API_URL, timeout=1) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (OSError, URLError, TimeoutError, ValueError, json.JSONDecodeError):
        return None

    endpoints = payload.get("endpoints", []) if isinstance(payload, dict) else []
    for endpoint in endpoints:
        if not isinstance(endpoint, dict):
            continue
        upstream = endpoint.get("upstream")
        upstream_url = upstream.get("url") if isinstance(upstream, dict) else None
        if not isinstance(upstream_url, str):
            continue
        parsed_upstream = urlsplit(
            upstream_url if "://" in upstream_url else f"http://{upstream_url}"
        )
        try:
            upstream_port = parsed_upstream.port
        except ValueError:
            continue
        if parsed_upstream.hostname not in {"localhost", "127.0.0.1", "::1"}:
            continue
        if upstream_port != port:
            continue

        public_url = endpoint.get("url")
        if not isinstance(public_url, str):
            continue
        parsed_public = urlsplit(public_url)
        try:
            public_port = parsed_public.port
        except ValueError:
            continue
        if (
            parsed_public.scheme == "https"
            and parsed_public.hostname
            and parsed_public.username is None
            and parsed_public.password is None
            and public_port in (None, 443)
            and parsed_public.path in ("", "/")
            and not parsed_public.query
            and not parsed_public.fragment
        ):
            return public_url.rstrip("/")
    return None


def start_ngrok_tunnel(port: int) -> TunnelInfo:
    """Start ngrok and read the matching public endpoint from its local Agent API."""
    _verify_local_auth(port, os.environ.get("GODOT_AI_AUTH_TOKEN", "").strip())
    bin_path = find_tunnel_binary("ngrok")
    if not bin_path:
        raise FileNotFoundError(
            "ngrok is required for the ngrok tunnel provider; install it and retry."
        )

    proc = subprocess.Popen(
        [bin_path, "http", f"127.0.0.1:{port}"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
    )
    deadline = time.monotonic() + TUNNEL_START_TIMEOUT_SECONDS
    public_url = None
    while time.monotonic() < deadline:
        if proc.poll() is not None:
            break
        public_url = _ngrok_endpoint_for_port(port)
        if public_url:
            break
        time.sleep(0.25)

    if public_url is None:
        _terminate_tunnel_process(proc)
        raise RuntimeError(
            "ngrok did not publish an HTTPS endpoint for the requested port within "
            f"{TUNNEL_START_TIMEOUT_SECONDS:g} seconds. Check ngrok authentication and "
            "the local Agent API at 127.0.0.1:4040."
        )

    _start_keepalive_worker(public_url, proc)
    return TunnelInfo(
        provider="ngrok",
        public_url=public_url,
        openapi_url=f"{public_url}/openapi.json",
        process=proc,
    )


def _start_tunnel_for_provider(
    port: int, provider: str = DEFAULT_TUNNEL_PROVIDER
) -> TunnelInfo:
    """Dispatch to the right tunnel starter."""
    if provider == "localhost.run":
        return start_ssh_tunnel(port, "localhost.run")
    if provider == "serveo":
        return start_ssh_tunnel(port, "serveo")
    if provider == "pinggy":
        return start_ssh_tunnel(port, "pinggy")
    if provider == "cloudflare-named":
        return start_cloudflare_named_tunnel(port)
    if provider == "tailscale-funnel":
        return start_tailscale_funnel_tunnel(port)
    if provider == "cloudflare":
        return start_cloudflare_quick_tunnel(port)
    if provider == "ngrok":
        return start_ngrok_tunnel(port)
    if provider == "ssh":
        return start_ssh_tunnel(port, "localhost.run")
    raise ValueError(f"Unsupported tunnel provider: {provider}")


def run_tunnel_forever(
    port: int,
    provider: str = DEFAULT_TUNNEL_PROVIDER,
    on_connect: "callable | None" = None,
) -> None:
    """Start a tunnel and auto-reconnect on drops with exponential backoff.

    Blocks forever (until KeyboardInterrupt). Calls *on_connect(info)* each
    time a new tunnel comes up so the caller can print the URL.
    """
    delay = _INITIAL_RECONNECT_DELAY
    while True:
        try:
            info = _start_tunnel_for_provider(port, provider)
        except Exception as exc:
            print(f"Tunnel start failed: {exc}. Retrying in {delay}s...", flush=True)
            time.sleep(delay)
            delay = min(delay * 2, _MAX_RECONNECT_DELAY)
            continue

        delay = _INITIAL_RECONNECT_DELAY

        if on_connect:
            on_connect(info)

        if info.process:
            try:
                info.process.wait()
            except KeyboardInterrupt:
                info.process.terminate()
                return

        exit_code = info.process.returncode if info.process else -1
        print(
            f"Tunnel dropped (exit code {exit_code}). Reconnecting in {delay}s...",
            flush=True,
        )
        time.sleep(delay)
        delay = min(delay * 2, _MAX_RECONNECT_DELAY)


async def supervise_tunnel(
    port: int,
    provider: TunnelProvider = DEFAULT_TUNNEL_PROVIDER,
) -> TunnelInfo:
    """Async supervisor to launch and monitor cloud tunnel."""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(
        None, _start_tunnel_for_provider, port, provider
    )


async def supervise_tunnel_forever(
    port: int,
    provider: TunnelProvider = DEFAULT_TUNNEL_PROVIDER,
    on_connect: "callable | None" = None,
) -> None:
    """Async auto-reconnecting tunnel supervisor for co-launch mode.

    Runs until cancelled. Each time a tunnel connects, *on_connect(info)*
    is called (if provided) so the caller can log the URL.
    """
    loop = asyncio.get_running_loop()
    delay = _INITIAL_RECONNECT_DELAY
    while True:
        try:
            info = await loop.run_in_executor(
                None, _start_tunnel_for_provider, port, provider
            )
        except Exception as exc:
            logger.warning("Tunnel start failed: %s. Retrying in %ds...", exc, delay)
            await asyncio.sleep(delay)
            delay = min(delay * 2, _MAX_RECONNECT_DELAY)
            continue

        delay = _INITIAL_RECONNECT_DELAY
        if on_connect:
            on_connect(info)

        if info.process:
            await loop.run_in_executor(None, info.process.wait)

        exit_code = info.process.returncode if info.process else -1
        logger.info("Tunnel dropped (exit %d). Reconnecting in %ds...", exit_code, delay)
        await asyncio.sleep(delay)
        delay = min(delay * 2, _MAX_RECONNECT_DELAY)
