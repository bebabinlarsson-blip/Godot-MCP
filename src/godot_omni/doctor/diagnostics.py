"""Comprehensive Diagnostics and Health Checks for Godot Omni."""

from __future__ import annotations

import os
import platform
import shutil
import socket
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from godot_omni.clients import ClientManager
from godot_omni.registry import get_global_registry


@dataclass
class DiagnosticSection:
    title: str
    passed: bool
    details: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "passed": self.passed,
            "details": self.details,
            "recommendations": self.recommendations,
        }


class OmniDoctor:
    """Runs diagnostics across environment, Godot engine, network ports, and AI clients."""

    def __init__(self) -> None:
        self.client_manager = ClientManager()

    def check_python_environment(self) -> DiagnosticSection:
        details = [
            f"Python Version: {platform.python_version()} ({platform.architecture()[0]})",
            f"Executable: {sys.executable}",
            f"Virtual Environment: {'Active' if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix) else 'Global / System'}",
        ]
        recs = []
        py_version = sys.version_info
        passed = (py_version.major == 3 and py_version.minor >= 11)
        if not passed:
            recs.append("Godot Omni requires Python 3.11+. Please upgrade your Python interpreter.")

        return DiagnosticSection(
            title="Python Runtime Environment",
            passed=passed,
            details=details,
            recommendations=recs,
        )

    def check_godot_installation(self) -> DiagnosticSection:
        details: list[str] = []
        recs: list[str] = []
        found_binaries: list[str] = []

        candidate_names = ["godot", "godot.exe", "godot4", "godot4.exe", "Godot", "Godot.exe"]
        for name in candidate_names:
            resolved = shutil.which(name)
            if resolved and resolved not in found_binaries:
                found_binaries.append(resolved)

        # Check standard Windows paths
        if platform.system() == "Windows":
            user_home = Path(os.path.expanduser("~"))
            standard_paths = [
                Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Godot",
                Path(os.environ.get("PROGRAMFILES", "")) / "Godot",
                user_home / "scoop" / "apps" / "godot",
                user_home / "scoop" / "apps" / "godot4",
            ]
            for sp in standard_paths:
                if sp.is_dir():
                    for exe in sp.glob("**/godot*.exe"):
                        p_str = str(exe)
                        if p_str not in found_binaries:
                            found_binaries.append(p_str)

        if found_binaries:
            details.append(f"Discovered Godot Executables: {', '.join(found_binaries)}")
        else:
            details.append("Godot executable was not found on PATH or standard directories.")
            recs.append("Install Godot Engine 4.x or add Godot executable directory to your PATH.")

        # Check Editor Settings
        if platform.system() == "Windows":
            appdata = os.environ.get("APPDATA", "")
            godot_appdata = Path(appdata) / "Godot"
            if godot_appdata.is_dir():
                settings_files = list(godot_appdata.glob("editor_settings*.tres"))
                details.append(f"Editor Settings Found: {len(settings_files)} configurations ({', '.join(f.name for f in settings_files[:3])})")
            else:
                details.append("No Godot Editor Settings directory found in APPDATA.")

        passed = len(found_binaries) > 0 or details[-1].startswith("Editor Settings Found")
        return DiagnosticSection(
            title="Godot Engine Installation",
            passed=passed,
            details=details,
            recommendations=recs,
        )

    def check_network_ports(self) -> DiagnosticSection:
        details: list[str] = []
        recs: list[str] = []

        def test_port(port: int, label: str) -> bool:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                sock.bind(("127.0.0.1", port))
                sock.close()
                details.append(f"Port {port} ({label}): Available for binding")
                return True
            except OSError:
                details.append(f"Port {port} ({label}): Already in use or reserved by an active server")
                return False

        http_free = test_port(8000, "HTTP / SSE Transport")
        ws_free = test_port(9500, "Godot Plugin WebSocket")

        # Port being in use is fine if Godot AI or Godot Editor is currently running
        passed = True
        if not http_free and not ws_free:
            details.append("Note: Both ports are active. A Godot AI backend is likely running and ready.")
        elif not ws_free:
            details.append("Note: WebSocket port 9500 is in use. Godot editor or server is active.")

        return DiagnosticSection(
            title="Network & Port Availability",
            passed=passed,
            details=details,
            recommendations=recs,
        )

    def check_ai_clients(self) -> DiagnosticSection:
        reports = self.client_manager.detect_all()
        details: list[str] = []
        recs: list[str] = []

        installed = [r for r in reports if r.installed]
        configured = [r for r in reports if r.status.value == "configured"]

        details.append(f"Total AI Clients Detected: {len(installed)} of {len(reports)} known clients")
        details.append(f"Configured Clients: {len(configured)} ({', '.join(r.display_name for r in configured) or 'None'})")

        for r in installed:
            if r.status.value != "configured":
                recs.append(f"Run 'godot-omni clients configure --client {r.client_id}' to enable Godot Omni in {r.display_name}.")

        passed = len(configured) > 0 or len(installed) > 0
        return DiagnosticSection(
            title="AI MCP Clients Integration",
            passed=passed,
            details=details,
            recommendations=recs,
        )

    def check_operations_registry(self) -> DiagnosticSection:
        registry = get_global_registry()
        stats = registry.get_stats()
        total_ops = stats["canonical_operations"]

        details = [
            f"Canonical Operations Count: {total_ops}",
            f"Curated Operations: {stats['curated_operations']}",
            f"Generated ClassDB Operations: {stats['generated_classdb_operations']}",
            f"UI Automation Operations: {stats['ui_automation_operations']}",
            f"Runtime Operations: {stats['runtime_operations']}",
            f"Reflection Operations: {stats['reflection_operations']}",
            f"Distinct Domains: {stats['compact_domains_available']}",
        ]
        recs = []
        passed = total_ops >= 1500
        if not passed:
            recs.append(f"Canonical operations count ({total_ops}) is below required 1,500 operations threshold!")

        return DiagnosticSection(
            title="Canonical Operations Registry",
            passed=passed,
            details=details,
            recommendations=recs,
        )

    def run_all(self) -> dict[str, Any]:
        sections = [
            self.check_python_environment(),
            self.check_godot_installation(),
            self.check_network_ports(),
            self.check_ai_clients(),
            self.check_operations_registry(),
        ]
        all_passed = all(s.passed for s in sections)
        return {
            "all_passed": all_passed,
            "sections": [s.to_dict() for s in sections],
        }
