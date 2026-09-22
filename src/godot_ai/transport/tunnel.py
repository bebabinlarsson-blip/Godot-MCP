"""Cloud tunnel supervisor for exposing local Godot AI to ChatGPT on the web."""

from __future__ import annotations

import asyncio
import logging
import re
import shutil
import subprocess
from dataclasses import dataclass
from typing import Literal

logger = logging.getLogger(__name__)

TunnelProvider = Literal["cloudflare", "ngrok", "manual"]


@dataclass
class TunnelInfo:
    provider: str
    public_url: str
    openapi_url: str
    process: subprocess.Popen[str] | None = None


_CF_URL_REGEX = re.compile(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com")
_NGROK_URL_REGEX = re.compile(r"https://[a-zA-Z0-9-]+\.ngrok-free\.app")


def find_tunnel_binary(provider: TunnelProvider = "cloudflare") -> str | None:
    """Find binary executable for the requested tunnel provider."""
    if provider == "cloudflare":
        return shutil.which("cloudflared")
    if provider == "ngrok":
        return shutil.which("ngrok")
    return None


def start_cloudflare_quick_tunnel(port: int) -> TunnelInfo:
    """Start a free, zero-config Cloudflare Quick Tunnel to local port."""
    bin_path = find_tunnel_binary("cloudflare")
    if not bin_path:
        raise FileNotFoundError(
            "cloudflared binary not found in PATH. Install cloudflared to use "
            "automated Cloudflare Quick Tunnels, or use --tunnel manual."
        )

    cmd = [
        bin_path,
        "tunnel",
        "--url",
        f"http://127.0.0.1:{port}",
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
    # Read output until quick tunnel URL is found (within 30s)
    for _ in range(60):
        line = proc.stdout.readline() if proc.stdout else ""
        if not line:
            continue
        match = _CF_URL_REGEX.search(line)
        if match:
            public_url = match.group(0)
            break

    if not public_url:
        proc.terminate()
        raise RuntimeError("Failed to obtain Cloudflare Quick Tunnel URL.")

    return TunnelInfo(
        provider="cloudflare",
        public_url=public_url,
        openapi_url=f"{public_url}/openapi.json",
        process=proc,
    )


async def supervise_tunnel(
    port: int,
    provider: TunnelProvider = "cloudflare",
) -> TunnelInfo:
    """Async supervisor to launch and monitor cloud tunnel."""
    loop = asyncio.get_running_loop()
    if provider == "cloudflare":
        return await loop.run_in_executor(None, start_cloudflare_quick_tunnel, port)
    raise NotImplementedError(f"Tunnel provider {provider} is not currently implemented.")
