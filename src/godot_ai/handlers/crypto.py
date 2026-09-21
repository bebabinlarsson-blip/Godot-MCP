"""Handler functions routing Cryptography and Hashing commands to the connected Godot runtime."""

from __future__ import annotations

from typing import Any

from godot_ai.handlers._readiness import require_writable_async
from godot_ai.runtime.direct import DirectRuntime


async def crypto_hash_file(
    runtime: DirectRuntime,
    file_path: str,
    algorithm: str = "sha256",
) -> dict[str, Any]:
    """Compute checksum digest of a project file."""
    params: dict[str, Any] = {
        "file_path": file_path,
        "algorithm": algorithm,
    }
    return await runtime.send_command("crypto_hash_file", params, timeout=10.0)


async def crypto_hash_string(
    runtime: DirectRuntime,
    content: str,
    algorithm: str = "sha256",
) -> dict[str, Any]:
    """Compute checksum digest of a string."""
    params: dict[str, Any] = {
        "content": content,
        "algorithm": algorithm,
    }
    return await runtime.send_command("crypto_hash_string", params, timeout=10.0)


async def crypto_generate_random_bytes(
    runtime: DirectRuntime,
    size: int = 32,
    format: str = "hex",
) -> dict[str, Any]:
    """Generate cryptographically secure random bytes."""
    params: dict[str, Any] = {
        "size": size,
        "format": format,
    }
    return await runtime.send_command("crypto_generate_random_bytes", params, timeout=10.0)


async def crypto_generate_rsa_key(
    runtime: DirectRuntime,
    key_size: int = 2048,
    save_path: str = "",
) -> dict[str, Any]:
    """Generate and optionally save an RSA private key."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "key_size": key_size,
        "save_path": save_path,
    }
    return await runtime.send_command("crypto_generate_rsa_key", params, timeout=10.0)


async def crypto_generate_self_signed_cert(
    runtime: DirectRuntime,
    key_path: str = "",
    cert_save_path: str = "",
    common_name: str = "localhost",
    issuer_name: str = "GodotMCP",
) -> dict[str, Any]:
    """Generate a self-signed X509 certificate."""
    await require_writable_async(runtime)
    params: dict[str, Any] = {
        "key_path": key_path,
        "cert_save_path": cert_save_path,
        "common_name": common_name,
        "issuer_name": issuer_name,
    }
    return await runtime.send_command(
        "crypto_generate_self_signed_cert", params, timeout=10.0
    )


async def crypto_hmac_digest(
    runtime: DirectRuntime,
    key: str,
    message: str,
    algorithm: str = "sha256",
) -> dict[str, Any]:
    """Compute HMAC authentication digest."""
    params: dict[str, Any] = {
        "key": key,
        "message": message,
        "algorithm": algorithm,
    }
    return await runtime.send_command("crypto_hmac_digest", params, timeout=10.0)
