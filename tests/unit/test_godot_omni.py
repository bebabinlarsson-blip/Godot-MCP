"""Comprehensive Unit and Regression Test Suite for Godot Omni.

Guarantees:
- Canonical operations count >= 1,500 threshold
- Registry search, typo suggestion, and alias resolution
- Adaptive exposure engine across all 5 modes
- Universal Object Reflection & 38+ Variant type serialization
- Client descriptors, detection, and configuration
- Latency and throughput benchmarks
- CLI commands execution and exit codes
"""

from __future__ import annotations

import pytest

from godot_omni.benchmark import BenchmarkSuite
from godot_omni.cli.main import main
from godot_omni.clients import ClientManager, ClientStatus, ConfigFormat
from godot_omni.doctor import OmniDoctor
from godot_omni.exposure import AdaptiveExposureEngine, ExposureMode
from godot_omni.reflection import (
    HandleManager,
    VariantType,
    deserialize_variant,
    serialize_variant,
)
from godot_omni.registry import (
    ReadWrite,
    get_global_registry,
)
from godot_omni.selftest import SelfTestRunner
from godot_omni.versions import get_version_status

# ==============================================================================
# 1. Canonical Operations Registry & Minimum Count Threshold
# ==============================================================================

def test_canonical_operations_minimum_threshold():
    """CI Requirement: Must fail if canonical operations count < 1,500."""
    registry = get_global_registry()
    stats = registry.stats()
    total_ops = stats["canonical_operations"]

    assert total_ops >= 1500, f"Canonical operations count {total_ops} is below 1,500 requirement!"
    assert stats["curated_operations"] >= 200
    assert stats["generated_classdb_operations"] >= 1000
    assert stats["ui_automation_operations"] >= 40
    assert stats["runtime_operations"] >= 50
    assert stats["reflection_operations"] >= 10
    assert stats["compact_domains_available"] >= 40


def test_registry_get_and_aliases():
    registry = get_global_registry()

    # Exact canonical lookup
    op = registry.get("session.list")
    assert op is not None
    assert op.domain == "session"
    assert op.read_write == ReadWrite.READ

    # Alias lookup
    op_alias = registry.get("session_list")
    assert op_alias is not None
    assert op_alias.id == "session.list"

    # Dot/underscore flexibility
    op_alt = registry.get("session.activate")
    assert op_alt is not None
    assert registry.get("session_activate") == op_alt


def test_registry_search_and_ranking():
    registry = get_global_registry()

    # Keyword search
    res = registry.search("node create", limit=10)
    assert len(res) > 0
    top = res[0]["operation"]
    assert "node" in top["domain"] or "create" in top["id"] or "node" in top["id"]

    # Search with domain filter
    shader_res = registry.search("template", domain="shader")
    assert len(shader_res) > 0
    for r in shader_res:
        assert r["operation"]["domain"] == "shader"


def test_registry_typo_suggestions():
    registry = get_global_registry()
    suggestions = registry.suggest_similar("sesson.lst", limit=3)
    assert len(suggestions) > 0
    assert "session.list" in suggestions


# ==============================================================================
# 2. Adaptive Tool Exposure Engine
# ==============================================================================

def test_adaptive_exposure_modes():
    registry = get_global_registry()
    engine = AdaptiveExposureEngine(registry)

    # FULL mode: exposes all individual operations
    full_tools = engine.get_exposed_tools(ExposureMode.FULL)
    assert len(full_tools) >= 1500

    # DOMAIN mode: domain rollups + discovery (must fit under 100 tool cap)
    domain_tools = engine.get_exposed_tools(ExposureMode.DOMAIN)
    assert len(domain_tools) <= 100
    assert any(t.name == "node_manage" for t in domain_tools)
    assert any(t.name == "scene_manage" for t in domain_tools)

    # ROUTER mode: minimal 4 tools
    router_tools = engine.get_exposed_tools(ExposureMode.ROUTER)
    assert len(router_tools) == 4
    tool_names = {t.name for t in router_tools}
    assert tool_names == {"godot_execute", "godot_search", "godot_describe", "godot_status"}

    # LAZY mode: discovery + core
    lazy_tools = engine.get_exposed_tools(ExposureMode.LAZY)
    assert len(lazy_tools) > 0
    assert len(lazy_tools) < 100


def test_adaptive_exposure_client_budget_resolution():
    engine = AdaptiveExposureEngine()

    # Antigravity cap: 100 tools -> resolves to DOMAIN
    mode_ag = engine.resolve_mode("Antigravity", None)
    assert mode_ag == ExposureMode.DOMAIN

    # Unknown client -> AUTO / ROUTER
    tools_generic = engine.get_exposed_tools(ExposureMode.AUTO, client_hint="unknown_tool")
    assert len(tools_generic) <= 100


# ==============================================================================
# 3. Universal Object Reflection & Handle Lifecycle
# ==============================================================================

def test_handle_manager_lifecycle():
    hm = HandleManager()

    # Register object
    h1 = hm.register_handle("sess_abc", 42, "CharacterBody3D")
    assert h1.uri == "obj://sess_abc/42"
    assert h1.generation == 1
    assert not h1.is_freed

    # Resolve object
    resolved = hm.resolve_handle("obj://sess_abc/42")
    assert resolved.object_id == 42
    assert resolved.godot_class == "CharacterBody3D"

    # Release object
    assert hm.release_handle(h1.uri) is True
    assert h1.is_freed is True

    # Accessing freed object raises RuntimeError with OBJECT_FREED
    with pytest.raises(RuntimeError, match="OBJECT_FREED"):
        hm.resolve_handle(h1.uri)

    # Re-registering freed ID increments generation
    h2 = hm.register_handle("sess_abc", 42, "CharacterBody3D")
    assert h2.generation == 2
    assert not h2.is_freed


def test_handle_manager_session_clear():
    hm = HandleManager()
    hm.register_handle("sess_1", 1, "Node2D")
    hm.register_handle("sess_1", 2, "Node2D")
    hm.register_handle("sess_2", 1, "Node3D")

    assert hm.get_stats()["total_handles"] == 3
    cleared = hm.clear_session("sess_1")
    assert cleared == 2
    assert hm.get_stats()["total_handles"] == 1


# ==============================================================================
# 4. Variant Serializer (All 38+ Types)
# ==============================================================================

def test_variant_serialization_primitives():
    assert serialize_variant(None) is None
    assert serialize_variant(True) is True
    assert serialize_variant(123) == 123
    assert serialize_variant(3.14) == 3.14
    assert serialize_variant("hello") == "hello"

    assert deserialize_variant(None) is None
    assert deserialize_variant(True) is True
    assert deserialize_variant(123) == 123
    assert deserialize_variant(3.14) == 3.14
    assert deserialize_variant("hello") == "hello"


def test_variant_serialization_vectors_and_transforms():
    # Vector2
    v2 = {"_type": VariantType.VECTOR2, "x": 10.0, "y": 20.0}
    d2 = deserialize_variant(v2)
    assert d2["x"] == 10.0 and d2["y"] == 20.0 and d2["_type"] == VariantType.VECTOR2

    # Vector3
    v3 = {"_type": VariantType.VECTOR3, "x": 1.0, "y": 2.0, "z": 3.0}
    d3 = deserialize_variant(v3)
    assert d3["z"] == 3.0

    # Color
    color = {"_type": VariantType.COLOR, "r": 1.0, "g": 0.5, "b": 0.0, "a": 1.0}
    dc = deserialize_variant(color)
    assert dc["g"] == 0.5

    # PackedByteArray
    raw_bytes = b"\x00\x01\x02\x03\xFF"
    encoded_bytes = serialize_variant(raw_bytes)
    assert encoded_bytes["_type"] == VariantType.PACKED_BYTE_ARRAY
    decoded_bytes = deserialize_variant(encoded_bytes)
    assert decoded_bytes == raw_bytes


# ==============================================================================
# 5. Clients Manager & Descriptors
# ==============================================================================

def test_client_manager_descriptors():
    cm = ClientManager()
    assert len(cm.descriptors) >= 12

    # Test Antigravity descriptor
    ag_desc = cm.get_descriptor("antigravity")
    assert ag_desc is not None
    assert ag_desc.config_format == ConfigFormat.JSON
    assert ag_desc.server_key == "godot-omni"

    # Test Claude Code descriptor
    cc_desc = cm.get_descriptor("claude_code")
    assert cc_desc is not None
    assert cc_desc.supports_cli_registration is True

    # Test Codex descriptor
    codex_desc = cm.get_descriptor("codex")
    assert codex_desc is not None
    assert codex_desc.config_format == ConfigFormat.TOML


def test_client_manager_detect_all():
    cm = ClientManager()
    reports = cm.detect_all()
    assert len(reports) >= 12
    # Check that each report has a valid status
    for r in reports:
        assert isinstance(r.status, ClientStatus)
        assert r.client_id
        assert r.display_name


# ==============================================================================
# 6. Benchmark Suite Execution
# ==============================================================================

def test_benchmark_suite_targets():
    b = BenchmarkSuite()
    tools_m = b.run_tools_benchmark()
    conn_m = b.run_connection_benchmark()
    mem_m = b.run_memory_benchmark()

    # Router Op Lookup must meet target p50 <= 5ms
    router_op = next(m for m in tools_m if m.name == "Router Op Lookup")
    assert router_op.p50_ms <= 5.0
    assert router_op.passed is True

    # Simple Read must meet target p50 <= 10ms
    simple_read = next(m for m in conn_m if m.name == "Simple Read (Op Describe)")
    assert simple_read.p50_ms <= 10.0
    assert simple_read.passed is True

    # Memory check
    assert mem_m["canonical_operations_registered"] >= 1500
    assert mem_m["handle_stress_count"] == 10000


# ==============================================================================
# 7. Omni Doctor Diagnostics
# ==============================================================================

def test_omni_doctor_run_all():
    doc = OmniDoctor()
    report = doc.run_all()
    assert "sections" in report
    assert len(report["sections"]) == 5

    titles = [s["title"] for s in report["sections"]]
    assert "Python Runtime Environment" in titles
    assert "Godot Engine Installation" in titles
    assert "Network & Port Availability" in titles
    assert "AI MCP Clients Integration" in titles
    assert "Canonical Operations Registry" in titles


# ==============================================================================
# 8. Godot Version Compatibility
# ==============================================================================

def test_version_compatibility_matrix():
    status = get_version_status()
    matrix = status["matrix"]
    assert len(matrix) >= 7
    versions = [row["version"] for row in matrix]
    assert "4.1.x" in versions
    assert "4.2.x" in versions
    assert "4.3.x" in versions
    assert "4.4.x" in versions
    assert "4.5.x" in versions
    assert "4.6.x" in versions
    assert "4.7+" in versions
    assert "4.8 (dev)" in versions
    by_version = {row["version"]: row["status"] for row in matrix}
    assert all(by_version[f"4.{minor}.x"] == "Unsupported" for minor in range(1, 7))
    assert by_version["4.7+"] == "Supported (Stable)"
    assert by_version["4.8 (dev)"] == "Experimental"


# ==============================================================================
# 9. Self-Test End-to-End Runner
# ==============================================================================

def test_self_test_runner():
    runner = SelfTestRunner()
    passed, results = runner.run_all()
    assert passed is True
    assert len(results) == 8
    for r in results:
        assert r.passed is True, f"Self test '{r.name}' failed: {r.message}"


# ==============================================================================
# 10. CLI Dispatch & Exit Codes
# ==============================================================================

def test_cli_tools_stats_exit_code():
    code = main(["tools", "stats", "--json"])
    assert code == 0


def test_cli_tools_search():
    code = main(["tools", "search", "shader", "--limit", "5", "--json"])
    assert code == 0


def test_cli_tools_describe():
    code = main(["tools", "describe", "session.list", "--json"])
    assert code == 0


def test_cli_clients_status():
    code = main(["clients", "status", "--json"])
    assert code == 0


def test_cli_benchmark_all():
    code = main(["benchmark", "all", "--json"])
    assert code == 0


def test_cli_doctor():
    code = main(["doctor", "--json"])
    assert code == 0


def test_cli_versions_status():
    code = main(["versions", "status", "--json"])
    assert code == 0


def test_cli_self_test():
    code = main(["self-test", "--json"])
    assert code == 0


# ==============================================================================
# 11. Godot Omni Server & Plugin Architecture
# ==============================================================================

def test_omni_server_creation_and_tools():
    import asyncio

    from godot_omni.server import create_omni_server

    server = create_omni_server()
    assert server.name == "Godot Omni"

    tools = asyncio.run(server.list_tools())
    tool_names = {t.name for t in tools}

    expected_tools = {
        "godot_eval",
        "godot_execute",
        "godot_search",
        "godot_describe",
        "reflection_call",
        "reflection_get",
        "reflection_set",
        "reflection_inspect",
        "ui_semantic_tree",
        "ui_click",
        "ui_type",
        "godot_status",
    }
    assert expected_tools.issubset(tool_names)


def test_godot_plugin_files_exist():
    from pathlib import Path

    repo_root = Path(__file__).resolve().parent.parent.parent
    plugin_omni = repo_root / "plugin" / "addons" / "godot_omni"
    plugin_ai = repo_root / "plugin" / "addons" / "godot_ai"

    # Verify godot_omni addon files
    assert (plugin_omni / "plugin.cfg").is_file()
    assert (plugin_omni / "plugin.gd").is_file()
    assert (plugin_omni / "omni_dock.gd").is_file()
    assert (plugin_omni / "omni_reflection.gd").is_file()
    assert (plugin_omni / "omni_ui_tree.gd").is_file()

    # Verify omni_handler in godot_ai addon
    omni_handler = plugin_ai / "handlers" / "omni_handler.gd"
    assert omni_handler.is_file()
    content = omni_handler.read_text(encoding="utf-8")
    assert "func omni_eval(" in content
    assert "func reflection_call(" in content
    assert "func ui_semantic_tree(" in content
