"""Read the current HTTP capability for repository smoke clients."""

from __future__ import annotations

import os
from urllib.parse import urlsplit

from godot_ai.transport.capability import (
    HTTP_CAPABILITY_ENV,
    read_capabilities,
    validate_capability,
)


def authorization_header(url: str) -> str:
    return f"Bearer {raw_capability(url)}"


def raw_capability(url: str) -> str:
    """Resolve and validate a raw HTTP capability for a target URL."""

    parsed = urlsplit(url)
    loopback = parsed.hostname in {"127.0.0.1", "localhost", "::1"}
    if (
        parsed.scheme not in {"http", "https"}
        or not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
        or (parsed.scheme == "http" and not loopback)
    ):
        raise ValueError("capability target must be loopback HTTP or HTTPS without userinfo")
    if loopback:
        port = parsed.port or (443 if parsed.scheme == "https" else 80)
        record = read_capabilities(port)
        if record is None:
            raise RuntimeError(f"missing Godot AI HTTP capability record for port {port}")
        capability = record.http
    else:
        try:
            capability = validate_capability(os.environ.get(HTTP_CAPABILITY_ENV, ""))
        except ValueError as exc:
            raise ValueError(f"invalid {HTTP_CAPABILITY_ENV}: {exc}") from None
    return capability
