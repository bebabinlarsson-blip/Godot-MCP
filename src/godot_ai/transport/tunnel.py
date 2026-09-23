"""Cloud tunnel supervisor for exposing local Godot AI to ChatGPT on the web."""

from __future__ import annotations

import asyncio
import logging
import re
import shutil
import subprocess
import threading
import time
import urllib.request
from dataclasses import dataclass
from typing import Literal

logger = logging.getLogger(__name__)

TunnelProvider = Literal[
    "serveo", "cloudflare", "ngrok", "ssh", "pinggy", "localhost.run", "manual"
]

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


def find_tunnel_binary(provider: TunnelProvider = "cloudflare") -> str | None:
    """Find binary executable for the requested tunnel provider."""
    if provider == "cloudflare":
        return shutil.which("cloudflared")
    if provider == "ngrok":
        return shutil.which("ngrok")
    if provider in ("ssh", "serveo", "pinggy", "localhost.run"):
        return shutil.which("ssh")
    return None


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
    """Send periodic lightweight HTTP pings through the tunnel to prevent idle timeouts."""
    def _worker():
        health_url = f"{public_url}/health"
        while proc.poll() is None:
            time.sleep(interval)
            if proc.poll() is not None:
                break
            try:
                req = urllib.request.Request(
                    health_url,
                    headers={"User-Agent": "GodotAI-KeepAlive/1.0"},
                )
                with urllib.request.urlopen(req, timeout=8) as _:
                    pass
            except Exception:
                pass

    t = threading.Thread(target=_worker, daemon=True, name="TunnelKeepAlive")
    t.start()


def start_ssh_tunnel(port: int, service: str = "localhost.run") -> TunnelInfo:
    """Start an SSH reverse tunnel using system OpenSSH without extra binaries."""
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

    public_url = ""
    for _ in range(60):
        line = proc.stdout.readline() if proc.stdout else ""
        if not line:
            if proc.poll() is not None:
                break
            continue
        match = _SSH_URL_REGEX.search(line)
        if match:
            public_url = match.group(0)
            break

    if not public_url:
        proc.terminate()
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

    public_url = ""
    for _ in range(60):
        line = proc.stdout.readline() if proc.stdout else ""
        if not line:
            if proc.poll() is not None:
                break
            continue
        match = _CF_URL_REGEX.search(line)
        if match:
            public_url = match.group(0)
            break

    if not public_url:
        proc.terminate()
        logger.warning("Cloudflare tunnel failed. Falling back to SSH tunnel...")
        return start_ssh_tunnel(port, "serveo")

    _start_keepalive_worker(public_url, proc)

    return TunnelInfo(
        provider="cloudflare",
        public_url=public_url,
        openapi_url=f"{public_url}/openapi.json",
        process=proc,
    )


def _start_tunnel_for_provider(port: int, provider: str = "localhost.run") -> TunnelInfo:
    """Dispatch to the right tunnel starter."""
    if provider == "localhost.run":
        return start_ssh_tunnel(port, "localhost.run")
    if provider == "serveo":
        return start_ssh_tunnel(port, "serveo")
    if provider == "pinggy":
        return start_ssh_tunnel(port, "pinggy")
    if provider == "cloudflare":
        return start_cloudflare_quick_tunnel(port)
    # Default is localhost.run for permanent non-expiring connection without 15m limit
    return start_ssh_tunnel(port, "localhost.run")


def run_tunnel_forever(
    port: int,
    provider: str = "localhost.run",
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
    provider: TunnelProvider = "localhost.run",
) -> TunnelInfo:
    """Async supervisor to launch and monitor cloud tunnel."""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(
        None, _start_tunnel_for_provider, port, provider
    )


async def supervise_tunnel_forever(
    port: int,
    provider: TunnelProvider = "localhost.run",
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
