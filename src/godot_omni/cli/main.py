"""Master CLI entry point for Godot Omni.

Unified command: `godot-omni`
Subcommands:
- attach
- tools (stats, search, describe, list, export)
- clients (detect, status, configure, remove, doctor)
- benchmark (all, connection, tools, memory)
- doctor
- versions (status)
- self-test
"""

from __future__ import annotations

import argparse
import sys
from typing import Sequence

import godot_omni
from godot_omni.cli.benchmark_cli import handle_benchmark
from godot_omni.cli.clients_cli import (
    handle_clients_configure,
    handle_clients_detect,
    handle_clients_doctor,
    handle_clients_remove,
    handle_clients_status,
)
from godot_omni.cli.doctor_cli import handle_doctor
from godot_omni.cli.selftest_cli import handle_self_test
from godot_omni.cli.tools_cli import (
    handle_tools_describe,
    handle_tools_export,
    handle_tools_list,
    handle_tools_search,
    handle_tools_stats,
)
from godot_omni.cli.versions_cli import handle_versions_status


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="godot-omni",
        description="Godot Omni — Universal Godot AI MCP Architecture & Engine Control",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"godot-omni {godot_omni.__version__}",
    )

    subparsers = parser.add_subparsers(dest="subcommand", help="Subcommand to execute")

    # 1. attach
    attach_parser = subparsers.add_parser(
        "attach",
        help="Client-owned bridge connecting MCP stdio transport to active Godot backend",
        add_help=False,  # Let attach pass through its own flags
    )
    attach_parser.add_argument("attach_args", nargs=argparse.REMAINDER)

    # 2. tools
    tools_parser = subparsers.add_parser("tools", help="Inspect and search canonical Godot operations")
    tools_subparsers = tools_parser.add_subparsers(dest="tools_subcommand", help="Tools action")

    # tools stats
    stats_p = tools_subparsers.add_parser("stats", help="Show canonical operations stats (fails CI if < 1500)")
    stats_p.add_argument("--json", action="store_true", help="Output machine-readable JSON")

    # tools search
    search_p = tools_subparsers.add_parser("search", help="Search operations registry with fuzzy ranking")
    search_p.add_argument("query", help="Keyword query (e.g. 'shader compile', 'node create')")
    search_p.add_argument("--domain", default=None, help="Filter by domain")
    search_p.add_argument("--limit", type=int, default=20, help="Maximum results to return")
    search_p.add_argument("--json", action="store_true", help="Output machine-readable JSON")

    # tools describe
    desc_p = tools_subparsers.add_parser("describe", help="Show full parameter and schema details for an operation")
    desc_p.add_argument("operation_id", help="Canonical operation ID or alias (e.g. 'session.list')")
    desc_p.add_argument("--json", action="store_true", help="Output machine-readable JSON")

    # tools list
    list_p = tools_subparsers.add_parser("list", help="List operations or exposed tools")
    list_p.add_argument("--domain", default=None, help="Filter by domain")
    list_p.add_argument("--category", default=None, help="Filter by category")
    list_p.add_argument("--exposure", choices=["auto", "full", "domain", "lazy", "router"], default=None, help="Expose tools under a specific mode")
    list_p.add_argument("--json", action="store_true", help="Output machine-readable JSON")

    # tools export
    export_p = tools_subparsers.add_parser("export", help="Export full canonical catalog")
    export_p.add_argument("--format", choices=["json", "markdown", "yaml"], default="json", help="Output format")
    export_p.add_argument("--output", default=None, help="Output file path (default stdout)")

    # 3. clients
    clients_parser = subparsers.add_parser("clients", help="Detect, configure, and manage AI MCP clients")
    clients_subparsers = clients_parser.add_subparsers(dest="clients_subcommand", help="Clients action")

    # clients detect
    cdetect_p = clients_subparsers.add_parser("detect", help="Detect installed AI clients")
    cdetect_p.add_argument("--json", action="store_true", help="Output JSON")

    # clients status
    cstatus_p = clients_subparsers.add_parser("status", help="Inspect configuration status of installed clients")
    cstatus_p.add_argument("--json", action="store_true", help="Output JSON")

    # clients configure
    cconf_p = clients_subparsers.add_parser("configure", help="Configure Godot Omni in AI client(s)")
    cconf_p.add_argument("--client", default=None, help="Client ID to configure")
    cconf_p.add_argument("--all", action="store_true", help="Configure all detected clients")

    # clients remove
    crem_p = clients_subparsers.add_parser("remove", help="Remove Godot Omni entry from AI client(s)")
    crem_p.add_argument("--client", default=None, help="Client ID to remove")
    crem_p.add_argument("--all", action="store_true", help="Remove from all configured clients")

    # clients doctor
    cdoct_p = clients_subparsers.add_parser("doctor", help="Run health checks on client configurations")
    cdoct_p.add_argument("--json", action="store_true", help="Output JSON")

    # 4. benchmark
    bench_parser = subparsers.add_parser("benchmark", help="Run performance, latency, and memory benchmarks")
    bench_parser.add_argument(
        "target",
        nargs="?",
        choices=["all", "connection", "tools", "memory"],
        default="all",
        help="Benchmark target suite (default: all)",
    )
    bench_parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")

    # 5. doctor
    doctor_parser = subparsers.add_parser("doctor", help="Run system, Godot engine, network, and registry diagnostics")
    doctor_parser.add_argument("--json", action="store_true", help="Output JSON")

    # 6. versions
    versions_parser = subparsers.add_parser("versions", help="Inspect Godot version compatibility matrix")
    versions_subparsers = versions_parser.add_subparsers(dest="versions_subcommand", help="Versions action")
    vstatus_p = versions_subparsers.add_parser("status", help="Show compatibility across Godot 4.1 to 4.7+")
    vstatus_p.add_argument("--json", action="store_true", help="Output JSON")

    # 7. self-test
    selftest_parser = subparsers.add_parser("self-test", help="Run in-process end-to-end self-test suite")
    selftest_parser.add_argument("--json", action="store_true", help="Output JSON")

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    effective_argv = list(sys.argv[1:] if argv is None else argv)
    if not effective_argv:
        parser = build_parser()
        parser.print_help()
        return 0

    # Special handling for attach: pass through arguments directly
    if effective_argv[0] == "attach":
        from godot_ai.attach.main import main as attach_main
        attach_main(effective_argv[1:])
        return 0

    parser = build_parser()
    args = parser.parse_args(effective_argv)

    if args.subcommand == "tools":
        if args.tools_subcommand == "stats":
            return handle_tools_stats(args)
        elif args.tools_subcommand == "search":
            return handle_tools_search(args)
        elif args.tools_subcommand == "describe":
            return handle_tools_describe(args)
        elif args.tools_subcommand == "list":
            return handle_tools_list(args)
        elif args.tools_subcommand == "export":
            return handle_tools_export(args)
        else:
            parser.parse_args(["tools", "--help"])
            return 0

    elif args.subcommand == "clients":
        if args.clients_subcommand == "detect":
            return handle_clients_detect(args)
        elif args.clients_subcommand == "status":
            return handle_clients_status(args)
        elif args.clients_subcommand == "configure":
            return handle_clients_configure(args)
        elif args.clients_subcommand == "remove":
            return handle_clients_remove(args)
        elif args.clients_subcommand == "doctor":
            return handle_clients_doctor(args)
        else:
            parser.parse_args(["clients", "--help"])
            return 0

    elif args.subcommand == "benchmark":
        return handle_benchmark(args)

    elif args.subcommand == "doctor":
        return handle_doctor(args)

    elif args.subcommand == "versions":
        if args.versions_subcommand == "status":
            return handle_versions_status(args)
        else:
            return handle_versions_status(args)

    elif args.subcommand == "self-test":
        return handle_self_test(args)

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
