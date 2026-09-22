"""Remote Godot Client for cloud sandboxes and ChatGPT work mode environments."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any


class RemoteGodotError(Exception):
    """Exception raised for errors during remote Godot MCP calls."""

    def __init__(self, message: str, status_code: int | None = None, data: Any = None) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.data = data


class RemoteGodotClient:
    """Client for controlling Godot AI from cloud sandboxes or remote Python environments.

    Communicates with Godot AI's REST gateway over HTTP/HTTPS, enabling tool
    execution without local engine installation or open inbound ports.
    """

    def __init__(
        self,
        base_url: str,
        *,
        auth_token: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.auth_token = auth_token
        self.timeout = timeout

    def _make_headers(self) -> dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "GodotAI-RemoteClient/5.0.25",
        }
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
            headers["X-Godot-AI-Key"] = self.auth_token
        return headers

    def status(self) -> dict[str, Any]:
        """Check the status and health of the remote Godot AI server."""
        url = f"{self.base_url}/api/v1/status"
        req = urllib.request.Request(url, headers=self._make_headers(), method="GET")
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                payload = response.read().decode("utf-8")
                return json.loads(payload)
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise RemoteGodotError(f"HTTP {exc.code}: {body}", status_code=exc.code) from exc
        except Exception as exc:
            raise RemoteGodotError(f"Connection failed: {exc}") from exc

    def list_tools(self) -> list[dict[str, Any]]:
        """List all available MCP tools registered on the remote server."""
        url = f"{self.base_url}/api/v1/tools"
        req = urllib.request.Request(url, headers=self._make_headers(), method="GET")
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                payload = response.read().decode("utf-8")
                data = json.loads(payload)
                return data.get("tools", [])
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise RemoteGodotError(f"HTTP {exc.code}: {body}", status_code=exc.code) from exc
        except Exception as exc:
            raise RemoteGodotError(f"Connection failed: {exc}") from exc

    def call(self, tool_name: str, arguments: dict[str, Any] | None = None) -> Any:
        """Execute a tool by name with arguments on the remote Godot instance."""
        url = f"{self.base_url}/api/v1/tools/{tool_name}"
        data_bytes = json.dumps(arguments or {}).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data_bytes,
            headers=self._make_headers(),
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                payload = response.read().decode("utf-8")
                result_json = json.loads(payload)
                if not result_json.get("success", False):
                    raise RemoteGodotError(
                        result_json.get("error", "Unknown tool error"),
                        data=result_json,
                    )
                return result_json.get("result")
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            try:
                err_data = json.loads(body)
                msg = err_data.get("error", body)
            except Exception:
                msg = body
            raise RemoteGodotError(f"HTTP {exc.code}: {msg}", status_code=exc.code) from exc
        except RemoteGodotError:
            raise
        except Exception as exc:
            raise RemoteGodotError(f"Tool call failed: {exc}") from exc
