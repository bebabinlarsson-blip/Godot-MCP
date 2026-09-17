"""CLI handlers for 'godot-omni benchmark' commands."""

from __future__ import annotations

import argparse
import json
import sys

from godot_omni.benchmark import BenchmarkSuite


def handle_benchmark(args: argparse.Namespace) -> int:
    suite_name = getattr(args, "target", "all") or "all"
    suite = BenchmarkSuite()

    if suite_name == "tools":
        res = suite.run_tools_benchmark()
        all_passed = all(m.passed for m in res)
        out = {"tools": [m.to_dict() for m in res], "all_passed": all_passed}
    elif suite_name == "connection":
        res = suite.run_connection_benchmark()
        all_passed = all(m.passed for m in res)
        out = {"connection": [m.to_dict() for m in res], "all_passed": all_passed}
    elif suite_name == "memory":
        mem = suite.run_memory_benchmark()
        out = {"memory": mem, "all_passed": mem["passed"]}
        all_passed = mem["passed"]
    else:
        out = suite.run_all()
        all_passed = out["all_passed"]

    if getattr(args, "json", False):
        print(json.dumps(out, indent=2))
        return 0 if all_passed else 1

    print("\n==================================================")
    print(f"       GODOT OMNI BENCHMARK ({suite_name.upper()})        ")
    print("==================================================")

    if "tools" in out:
        print("\n--- TOOLS & REGISTRY LATENCIES ---")
        for m in out["tools"]:
            sym = "OK" if m["passed"] else "FAIL"
            print(f"[{sym:^4}] {m['name']:<25} p50: {m['p50_ms']:>6.3f}ms | p95: {m['p95_ms']:>6.3f}ms (target: <= {m['target_ms']}ms)")

    if "connection" in out:
        print("\n--- CONNECTION & SERIALIZATION LATENCIES ---")
        for m in out["connection"]:
            sym = "OK" if m["passed"] else "FAIL"
            print(f"[{sym:^4}] {m['name']:<25} p50: {m['p50_ms']:>6.3f}ms | p95: {m['p95_ms']:>6.3f}ms (target: <= {m['target_ms']}ms)")

    if "memory" in out:
        mem = out["memory"]
        print("\n--- MEMORY & OBJECT SCALING ---")
        print(f"  * Registered Ops       : {mem['canonical_operations_registered']}")
        print(f"  * Approx Registry Size : {mem['registry_approx_size_kb']} KB")
        print(f"  * Handle Stress Test   : {mem['handle_stress_count']} handles created")
        print(f"  * Complexity Scaling   : {mem['handle_memory_scaling']}")

    print("\n" + "=" * 50)
    if all_passed:
        print("[SUCCESS] All performance and latency targets satisfied!\n")
        return 0
    else:
        print("[FAILURE] One or more benchmark targets failed to meet thresholds.\n", file=sys.stderr)
        return 1
