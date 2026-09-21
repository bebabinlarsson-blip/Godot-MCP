"""MCP tool for Godot TranslationServer localization and CSV workflows."""

from __future__ import annotations

from fastmcp import FastMCP

from godot_ai.handlers import localization as loc_handlers
from godot_ai.tools._meta_tool import register_manage_tool

_DESCRIPTION = """\
Godot TranslationServer Localization and CSV Translation Workflows.

Ops:
  * scaffold_csv(path="res://localization.csv", languages=["en", "es", "fr", "de", "ja", "zh"])
        Generate a starter localization CSV file and register it in ProjectSettings.

  * add_entry(path="res://localization.csv", key="ui_start",
              translations={"en": "Start", "es": "Iniciar"})
        Add or update a translation string row in the project's localization CSV.

  * get_locales()
        Query loaded locales, active locale, and translation settings from TranslationServer.

  * set_locale(locale="es")
        Switch the active test locale in TranslationServer.

  * translate(message="ui_start", context="")
        Test and evaluate translation string resolution via TranslationServer.

  * extract_strings(root_dir="res://")
        Scan project GDScript and scene files for tr() message lookup occurrences.
"""


def register_localization_tools(mcp: FastMCP) -> None:
    register_manage_tool(
        mcp,
        tool_name="localization_manage",
        description=_DESCRIPTION,
        ops={
            "scaffold_csv": loc_handlers.localization_scaffold_csv,
            "add_entry": loc_handlers.localization_add_entry,
            "get_locales": loc_handlers.localization_get_locales,
            "set_locale": loc_handlers.localization_set_locale,
            "translate": loc_handlers.localization_translate,
            "extract_strings": loc_handlers.localization_extract_strings,
        },
        read_resource_forms={
            "get_locales": None,
            "set_locale": None,
            "translate": None,
            "extract_strings": None,
        },
    )
