"""Cloud tunnel supervisor for exposing local Godot AI to ChatGPT on the web."""

from __future__ import annotations

import asyncio
import logging
import re
import shutil
import subprocess
import time
from dataclasses import dataclass
from typing import Literal

logger = logging.getLogger(__name__)

TunnelProvider = Literal[
    "cloudflare", "serveo", "ngrok", "ssh", "pinggy", "localhost.run", "manual"
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
    r"https?://[a-zA-Z0-9.-]+\.(?:serveousercontent\.com|lhr\.life|localhost\.run|pinggy\.link|a\.pinggy\.link|free\.pinggy\.net|run\.pinggy-free\.link)"
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
        "-o", "ServerAliveInterval=15",
        "-o", "ServerAliveCountMax=4",
        "-o", "TCPKeepAlive=yes",
        "-o", "ExitOnForwardFailure=yes",
        "-o", "ConnectTimeout=10",
        "-T",
    ]


def start_ssh_tunnel(port: int, service: str = "serveo") -> TunnelInfo:
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
    elif service == "localhost.run":
        cmd = [ssh_bin, "-R", f"80:127.0.0.1:{port}"] + keepalive + ["nokey@localhost.run"]
    else:
        cmd = [ssh_bin, "-R", f"80:127.0.0.1:{port}"] + keepalive + ["serveo.net"]

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
        if service == "serveo":
            logger.warning("Serveo tunnel timed out. Falling back to localhost.run...")
            return start_ssh_tunnel(port, "localhost.run")
        if service == "localhost.run":
            logger.warning("localhost.run timed out. Falling back to pinggy...")
            return start_ssh_tunnel(port, "pinggy")
        raise RuntimeError(f"Failed to obtain public URL from SSH tunnel ({service}).")

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

    return TunnelInfo(
        provider="cloudflare",
        public_url=public_url,
        openapi_url=f"{public_url}/openapi.json",
        process=proc,
    )


def _start_tunnel_for_provider(port: int, provider: str = "cloudflare") -> TunnelInfo:
    """Dispatch to the right tunnel starter."""
    if provider == "serveo":
        return start_ssh_tunnel(port, "serveo")
    if provider == "pinggy":
        return start_ssh_tunnel(port, "pinggy")
    if provider == "localhost.run":
        return start_ssh_tunnel(port, "localhost.run")
    if provider == "cloudflare":
        return start_cloudflare_quick_tunnel(port)
    # Default is cloudflare; start_cloudflare_quick_tunnel automatically
    # falls back to SSH (serveo -> localhost.run -> pinggy) if cloudflared is absent.
    return start_cloudflare_quick_tunnel(port)


def run_tunnel_forever(
    port: int,
    provider: str = "cloudflare",
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
    provider: TunnelProvider = "cloudflare",
) -> TunnelInfo:
    """Async supervisor to launch and monitor cloud tunnel."""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(
        None, _start_tunnel_for_provider, port, provider
    )


async def supervise_tunnel_forever(
    port: int,
    provider: TunnelProvider = "cloudflare",
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
