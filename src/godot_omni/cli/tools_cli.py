"""CLI handlers for 'godot-omni tools' commands."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from godot_omni.exposure import AdaptiveExposureEngine, ExposureMode
from godot_omni.registry import get_global_registry


def handle_tools_stats(args: argparse.Namespace) -> int:
    registry = get_global_registry()
    stats = registry.stats()
    total_ops = stats["canonical_operations"]

    if getattr(args, "json", False):
        print(json.dumps(stats, indent=2))
    else:
        print("\n==================================================")
        print("         GODOT OMNI CANONICAL OPERATIONS          ")
        print("==================================================")
        print(f"Total Canonical Operations : {total_ops}")
        print(f"  * Curated Operations     : {stats['curated_operations']}")
        print(f"  * Generated ClassDB Ops  : {stats['generated_classdb_operations']}")
        print(f"  * UI Automation Ops      : {stats['ui_automation_operations']}")
        print(f"  * Runtime Operations     : {stats['runtime_operations']}")
        print(f"  * Reflection Operations  : {stats['reflection_operations']}")
        print(f"Distinct Domains           : {stats['compact_domains_available']}")
        print(f"Dynamic Reflection (obj://): Supported")
        print("==================================================")

    # Hard enforcement: MUST fail if canonical_operations < 1500
    if total_ops < 1500:
        print(
            f"\n[ERROR] Required minimum 1,500 canonical operations not met: {total_ops} < 1500!",
            file=sys.stderr,
        )
        return 1

    if not getattr(args, "json", False):
        print("[SUCCESS] Minimum canonical operations threshold satisfied (>= 1500).\n")
    return 0


def handle_tools_search(args: argparse.Namespace) -> int:
    registry = get_global_registry()
    query = getattr(args, "query", "")
    domain = getattr(args, "domain", None)
    limit = getattr(args, "limit", 20)

    results = registry.search(query, domain=domain, limit=limit)

    if getattr(args, "json", False):
        print(json.dumps(results, indent=2))
        return 0

    print(f"\nSearch results for '{query}'" + (f" in domain '{domain}'" if domain else "") + f" ({len(results)} found):")
    print("-" * 80)
    if not results:
        suggestions = registry.suggest_similar(query)
        print("No exact matches found.")
        if suggestions:
            print(f"Did you mean: {', '.join(suggestions)}?")
        return 0

    for r in results:
        op = r["operation"]
        score = r["score"]
        print(f"[{score:>5.1f}]  {op['id']:<40} [{op['domain']}] {op['description'][:60]}")
    print("-" * 80 + "\n")
    return 0


def handle_tools_describe(args: argparse.Namespace) -> int:
    registry = get_global_registry()
    op_id = getattr(args, "operation_id", "")
    op = registry.get(op_id)

    if not op:
        suggestions = registry.suggest_similar(op_id)
        if getattr(args, "json", False):
            print(json.dumps({"error": f"Unknown operation '{op_id}'", "suggestions": suggestions}, indent=2))
        else:
            print(f"[ERROR] Operation '{op_id}' not found in canonical registry.", file=sys.stderr)
            if suggestions:
                print(f"Similar operations: {', '.join(suggestions)}", file=sys.stderr)
        return 1

    data = op.to_dict()
    if getattr(args, "json", False):
        print(json.dumps(data, indent=2))
        return 0

    print("\n" + "=" * 80)
    print(f"Operation: {op.id} ({op.title})")
    print("=" * 80)
    print(f"Domain           : {op.domain}")
    print(f"Category         : {op.category.value}")
    print(f"Access           : {op.read_write.value}")
    print(f"Execution Context: {op.execution_context.value}")
    print(f"Latency Tier     : {op.latency_tier.value}")
    print(f"Description      : {op.description}")
    if op.aliases:
        print(f"Aliases          : {', '.join(op.aliases)}")
    print("\nParameters:")
    if not op.parameters:
        print("  (None)")
    else:
        for p in op.parameters:
            req_str = "required" if p.required else "optional"
            def_str = f", default: {p.default}" if p.default is not None else ""
            enum_str = f", options: {list(p.enum_values)}" if p.enum_values else ""
            print(f"  * {p.name} ({p.type_name}, {req_str}{def_str}{enum_str})")
            print(f"    {p.description}")

    if op.examples:
        print("\nExamples:")
        for ex in op.examples:
            print(f"  * {ex.title}")
            print(f"    params: {json.dumps(ex.params)}")
            print(f"    result: {json.dumps(ex.result)}")
    print("=" * 80 + "\n")
    return 0


def handle_tools_list(args: argparse.Namespace) -> int:
    registry = get_global_registry()
    domain = getattr(args, "domain", None)
    category = getattr(args, "category", None)
    exposure_mode_str = getattr(args, "exposure", None)

    if exposure_mode_str:
        exposure = AdaptiveExposureEngine(registry)
        mode = ExposureMode(exposure_mode_str.lower())
        tools = exposure.get_exposed_tools(mode)
        if getattr(args, "json", False):
            print(json.dumps([{"name": t.name, "description": t.description, "target": t.handler_target} for t in tools], indent=2))
        else:
            print(f"\nExposed MCP Tools under mode '{mode.value}' ({len(tools)} tools):")
            print("-" * 80)
            for t in tools:
                print(f"* {t.name:<35} -> {t.handler_target:<30} {t.description[:50]}")
            print("-" * 80 + "\n")
        return 0

    all_ops = registry.list_all()
    filtered = []
    for op in all_ops:
        if domain and op.domain.lower() != domain.lower():
            continue
        if category and op.category.value.lower() != category.lower():
            continue
        filtered.append(op)

    if getattr(args, "json", False):
        print(json.dumps([op.to_dict() for op in filtered], indent=2))
        return 0

    print(f"\nCanonical Operations" + (f" in domain '{domain}'" if domain else "") + f" ({len(filtered)} total):")
    print("-" * 80)
    for op in filtered[:50]:
        print(f"* {op.id:<45} [{op.domain}] {op.title}")
    if len(filtered) > 50:
        print(f"... and {len(filtered) - 50} more. Use --json or filter by --domain.")
    print("-" * 80 + "\n")
    return 0


def handle_tools_export(args: argparse.Namespace) -> int:
    registry = get_global_registry()
    export_format = getattr(args, "format", "json").lower()
    output_path = getattr(args, "output", None)

    ops_data = registry.export_json()

    if export_format == "json":
        rendered = json.dumps(ops_data, indent=2)
    elif export_format == "markdown":
        lines = [
            "# Godot Omni Canonical Operations Registry",
            f"\nTotal canonical operations: {len(ops_data)}\n",
            "| ID | Domain | Category | Description |",
            "| :--- | :--- | :--- | :--- |",
        ]
        for op in ops_data:
            desc = op["description"].replace("|", "\\|")
            lines.append(f"| `{op['id']}` | {op['domain']} | {op['category']} | {desc} |")
        rendered = "\n".join(lines)
    elif export_format == "yaml":
        try:
            import yaml
            rendered = yaml.dump(ops_data, sort_keys=False)
        except ImportError:
            # Simple YAML fallback
            lines = ["operations:"]
            for op in ops_data:
                lines.append(f"  - id: \"{op['id']}\"")
                lines.append(f"    domain: \"{op['domain']}\"")
                lines.append(f"    title: \"{op['title']}\"")
            rendered = "\n".join(lines)
    else:
        print(f"[ERROR] Unsupported format '{export_format}'. Use json, markdown, or yaml.", file=sys.stderr)
        return 1

    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(rendered)
        print(f"[SUCCESS] Exported {len(ops_data)} operations to {output_path}")
    else:
        print(rendered)
    return 0
