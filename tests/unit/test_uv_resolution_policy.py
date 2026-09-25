"""Production Python launchers share one explicit package-index trust boundary."""

from __future__ import annotations

from pathlib import Path

from tests.unit._gdscript_text import get_func_block

ROOT = Path(__file__).resolve().parents[2]
PLUGIN = ROOT / "plugin" / "addons" / "godot_ai"


def _source(relative: str) -> str:
    return (PLUGIN / relative).read_text(encoding="utf-8")


def test_one_policy_owns_public_index_and_explicit_qualification_escape() -> None:
    policy = _source("utils/uv_resolution_policy.gd")
    args = get_func_block(policy, "static func args() -> Array[String]:")

    assert policy.count('const PUBLIC_INDEX := "https://pypi.org/simple"') == 1
    assert 'const QUALIFICATION_INDEX_ENV := "GODOT_AI_QUALIFICATION_PYTHON_INDEX"' in policy
    for option in (
        "--isolated",
        "--no-config",
        "--no-env-file",
        "--no-sources",
        "--no-build",
        "--index-strategy",
        "--keyring-provider",
    ):
        assert option in policy
    for option in ("--index", "--default-index", "--find-links"):
        assert option in args
    assert "if not qualification_authorized():" in args


def test_every_uv_server_attach_and_prewarm_builder_uses_one_policy() -> None:
    configurator = _source("client_configurator.gd")
    attach = get_func_block(configurator, "static func _resolve_attach_launch_uncached(")
    server = get_func_block(configurator, "static func get_server_command() -> Array[String]:")
    prewarm = get_func_block(
        configurator, "static func prewarm_server_package_argv(version: String) -> Array[String]:"
    )

    assert "UvResolution.args()" in attach
    assert "UvResolution.args()" in server
    assert "UvResolution.args()" in prewarm
    assert 'var direct_uv := OS.get_name() == "Windows" and not uv.is_empty()' in server
    assert 'var runner := uv if direct_uv else uvx' in server
    assert 'var cmd: Array[String] = [runner]' in server
    assert 'cmd.append_array(["tool", "run"])' in server
    assert "static func find_uv() -> String:" in configurator
    assert 'releases/download/v%s/' in configurator
    assert 'godot_ai-%s-py3-none-any.whl' in configurator
    assert "server_package_source(plugin_version)" in attach


def test_server_prewarms_the_same_release_wheel_used_for_launch() -> None:
    configurator = _source("client_configurator.gd")
    server = get_func_block(configurator, "static func get_server_command() -> Array[String]:")
    prewarm_argv = get_func_block(
        configurator, "static func prewarm_server_package_argv(version: String) -> Array[String]:"
    )

    assert "server_package_source(get_plugin_version())" in server
    assert "server_package_source(pinned)" in prewarm_argv
    assert '"--no-build"' in _source("utils/uv_resolution_policy.gd")


def test_production_uv_detection_covers_uvx_and_direct_uv_tool_run() -> None:
    policy = _source("utils/uv_resolution_policy.gd")
    production = get_func_block(
        policy, "static func is_production_command(command: Array) -> bool:"
    )

    assert 'var is_uvx := executable.begins_with("uvx")' in production
    assert 'executable == "uv.exe"' in production
    assert 'str(command[1]) == "tool"' in production
    assert 'str(command[2]) == "run"' in production
    for option in ('"--index"', '"--default-index"', '"--find-links"'):
        assert option in production


def test_godot_owned_server_and_prewarm_spawns_strip_uv_environment() -> None:
    policy = _source("utils/uv_resolution_policy.gd")
    lifecycle = _source("utils/server_lifecycle.gd")
    cli_exec = _source("clients/_cli_exec.gd")
    configurator = _source("client_configurator.gd")

    spawn = get_func_block(
        lifecycle,
        "static func _create_process_with_environment(",
    )
    piped = get_func_block(cli_exec, "static func _run_piped(")
    prewarm = get_func_block(
        configurator, "static func prewarm_server_package_blocking("
    )

    for name in (
        "UV_INDEX",
        "UV_DEFAULT_INDEX",
        "UV_FIND_LINKS",
        "UV_CONFIG_FILE",
        "UV_OVERRIDE",
        "UV_PYTHON",
        "UV_CACHE_DIR",
    ):
        assert f'"{name}"' in policy
    assert spawn.index("PortResolver.lock_process_spawn()") < spawn.index(
        "UvResolution.isolate_environment()"
    )
    assert spawn.index("UvResolution.restore_environment(") < spawn.index(
        "PortResolver.unlock_process_spawn()"
    )
    assert "UvResolution.isolate_environment() if isolate_uv_resolution else {}" in piped
    assert "UvResolution.is_production_command(command)" in prewarm


def test_qualification_authority_is_process_local_not_release_metadata() -> None:
    policy = _source("utils/uv_resolution_policy.gd")
    manager = _source("utils/update_manager.gd")
    assert "PathTemplate.env_lookup(QUALIFICATION_INDEX_ENV)" in policy
    assert "GODOT_AI_QUALIFICATION_PYTHON_INDEX" not in manager
