"""MCP tool for Godot cryptography, hashing, and certificates."""

from __future__ import annotations

from fastmcp import FastMCP

from godot_ai.handlers import crypto as crypto_handlers
from godot_ai.tools._meta_tool import register_manage_tool

_DESCRIPTION = """\
Cryptographic Operations, File/String Checksums, Random Tokens, RSA, and X509 Certificates.

Ops:
  * hash_file(file_path, algorithm="sha256")
        Compute checksum digest of a project file (sha256, sha1, md5).

  * hash_string(content, algorithm="sha256")
        Compute checksum digest of a string (sha256, sha1, md5).

  * generate_random_bytes(size=32, format="hex")
        Generate cryptographically secure random bytes (hex or base64).

  * generate_rsa_key(key_size=2048, save_path="")
        Generate and optionally save an RSA private key.

  * generate_self_signed_cert(key_path="", cert_save_path="",
                              common_name="localhost", issuer_name="GodotMCP")
        Generate a self-signed X509 certificate.

  * hmac_digest(key, message, algorithm="sha256")
        Compute HMAC authentication digest.
"""


def register_crypto_tools(mcp: FastMCP) -> None:
    register_manage_tool(
        mcp,
        tool_name="crypto_manage",
        description=_DESCRIPTION,
        ops={
            "hash_file": crypto_handlers.crypto_hash_file,
            "hash_string": crypto_handlers.crypto_hash_string,
            "generate_random_bytes": crypto_handlers.crypto_generate_random_bytes,
            "generate_rsa_key": crypto_handlers.crypto_generate_rsa_key,
            "generate_self_signed_cert": crypto_handlers.crypto_generate_self_signed_cert,
            "hmac_digest": crypto_handlers.crypto_hmac_digest,
        },
        read_resource_forms={
            "hash_file": None,
            "hash_string": None,
            "generate_random_bytes": None,
            "hmac_digest": None,
        },
    )
