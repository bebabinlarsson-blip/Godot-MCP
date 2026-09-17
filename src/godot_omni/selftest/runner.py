"""In-process End-to-End Self-Test Runner for Godot Omni."""

from __future__ import annotations

import sys
import time
from dataclasses import dataclass
from typing import Any

from godot_omni.benchmark import BenchmarkSuite
from godot_omni.clients import ClientManager
from godot_omni.exposure import AdaptiveExposureEngine, ExposureMode
from godot_omni.reflection import HandleManager, deserialize_variant, serialize_variant
from godot_omni.registry import get_global_registry


@dataclass
class TestResult:
    name: str
    passed: bool
    message: str
    duration_ms: float


class SelfTestRunner:
    """Executes an in-process, end-to-end verification suite."""

    def __init__(self) -> None:
        self.registry = get_global_registry()
        self.exposure = AdaptiveExposureEngine(self.registry)
        self.client_manager = ClientManager()

    def run_all(self) -> tuple[bool, list[TestResult]]:
        results: list[TestResult] = []

        tests = [
            ("Registry: Minimum Canonical Operations (>= 1500)", self._test_registry_count),
            ("Registry: Fuzzy Search & Typo Ranking", self._test_registry_search),
            ("Registry: Alias Resolution", self._test_registry_alias),
            ("Exposure: Mode Generation (AUTO, FULL, DOMAIN, LAZY, ROUTER)", self._test_exposure_modes),
            ("Reflection: Handle Lifecycle & Freed Protection", self._test_handle_lifecycle),
            ("Reflection: Variant Type Bidirectional Serialization", self._test_variant_serialization),
            ("Clients: Descriptor & Detector Integrity", self._test_clients_integrity),
            ("Benchmark: Router Latency Target (p50 <= 5ms)", self._test_benchmark_router_latency),
        ]

        for name, fn in tests:
            t0 = time.perf_counter()
            try:
                msg = fn()
                t1 = time.perf_counter()
                results.append(TestResult(name, True, msg or "Passed", (t1 - t0) * 1000.0))
            except Exception as exc:
                t1 = time.perf_counter()
                results.append(TestResult(name, False, f"Failed: {exc}", (t1 - t0) * 1000.0))

        all_passed = all(r.passed for r in results)
        return all_passed, results

    def _test_registry_count(self) -> str:
        stats = self.registry.stats()
        total = stats["canonical_operations"]
        if total < 1500:
            raise AssertionError(f"Canonical operations count is {total}, which is less than the required 1,500 operations!")
        return f"Verified {total} canonical operations (threshold: >= 1500)."

    def _test_registry_search(self) -> str:
        res = self.registry.search("node create", limit=5)
        if not res:
            raise AssertionError("Search for 'node create' returned no results.")
        # Test typo suggestion
        suggestions = self.registry.suggest_similar("sesson.lst", limit=3)
        if not suggestions:
            raise AssertionError("Suggest similar for 'sesson.lst' returned no suggestions.")
        return f"Search returned {len(res)} results; typo suggestion resolved to {suggestions[0]}."

    def _test_registry_alias(self) -> str:
        op = self.registry.get("session_list")
        if not op or op.id != "session.list":
            raise AssertionError("Alias 'session_list' failed to resolve to 'session.list'.")
        return "Alias resolved correctly."

    def _test_exposure_modes(self) -> str:
        full_tools = self.exposure.get_exposed_tools(ExposureMode.FULL)
        domain_tools = self.exposure.get_exposed_tools(ExposureMode.DOMAIN)
        router_tools = self.exposure.get_exposed_tools(ExposureMode.ROUTER)
        lazy_tools = self.exposure.get_exposed_tools(ExposureMode.LAZY)

        if len(full_tools) < 1500:
            raise AssertionError(f"FULL mode returned {len(full_tools)} tools (< 1500).")
        if len(domain_tools) > 100:
            raise AssertionError(f"DOMAIN mode returned {len(domain_tools)} tools (> 100 cap).")
        if len(router_tools) != 4:
            raise AssertionError(f"ROUTER mode returned {len(router_tools)} tools (!= 4).")
        if len(lazy_tools) == 0:
            raise AssertionError("LAZY mode returned 0 tools.")

        return f"Verified FULL ({len(full_tools)}), DOMAIN ({len(domain_tools)}), ROUTER ({len(router_tools)}), LAZY ({len(lazy_tools)})."

    def _test_handle_lifecycle(self) -> str:
        hm = HandleManager()
        h1 = hm.register_handle("sess_test", 1001, "Sprite2D")
        resolved = hm.resolve_handle(h1.uri)
        if resolved.object_id != 1001 or resolved.godot_class != "Sprite2D":
            raise AssertionError("Handle resolution failed.")

        # Release and test OBJECT_FREED
        hm.release_handle(h1.uri)
        try:
            hm.resolve_handle(h1.uri)
            raise AssertionError("Resolving freed handle should have raised RuntimeError.")
        except RuntimeError as exc:
            if "OBJECT_FREED" not in str(exc):
                raise AssertionError(f"Expected OBJECT_FREED in exception, got: {exc}")

        return "Handle registered, resolved, and verified OBJECT_FREED on release."

    def _test_variant_serialization(self) -> str:
        sample = {
            "v3": {"_type": "Vector3", "x": 1.5, "y": 2.5, "z": 3.5},
            "color": {"_type": "Color", "r": 1.0, "g": 0.5, "b": 0.2, "a": 1.0},
        }
        encoded = serialize_variant(sample)
        decoded = deserialize_variant(encoded)
        if decoded["v3"]["x"] != 1.5 or decoded["color"]["g"] != 0.5:
            raise AssertionError("Variant deserialization values mismatch.")
        return "Bidirectional Variant encoding verified."

    def _test_clients_integrity(self) -> str:
        reports = self.client_manager.detect_all()
        if len(reports) < 10:
            raise AssertionError(f"Expected at least 10 client descriptors, found {len(reports)}.")
        return f"Evaluated {len(reports)} client descriptors successfully."

    def _test_benchmark_router_latency(self) -> str:
        b = BenchmarkSuite()
        tools_m = b.run_tools_benchmark()
        router_m = next(m for m in tools_m if m.name == "Router Op Lookup")
        if not router_m.passed:
            raise AssertionError(f"Router p50 latency {router_m.p50_ms:.3f}ms exceeded target {router_m.target_ms}ms.")
        return f"Router p50 latency: {router_m.p50_ms:.3f}ms (target: <= {router_m.target_ms}ms)."
