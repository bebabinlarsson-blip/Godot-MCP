"""Handler functions routing Localization commands to the connected Godot runtime."""

from __future__ import annotations

from godot_ai.handlers._readiness import require_writable_async
from godot_ai.runtime.direct import DirectRuntime


async def localization_scaffold_csv(
    runtime: DirectRuntime,
    path: str = "res://localization.csv",
    languages: list[str] | None = None,
) -> dict:
    """Scaffold a localization CSV and register it in ProjectSettings."""
    await require_writable_async(runtime)
    return await runtime.send_command(
        "localization_scaffold_csv",
        {
            "path": path,
            "languages": languages or ["en", "es", "fr", "de", "ja", "zh"],
        },
        timeout=15.0,
    )


async def localization_add_entry(
    runtime: DirectRuntime,
    path: str = "res://localization.csv",
    key: str = "",
    translations: dict | None = None,
) -> dict:
    """Insert or update a translation row in the project localization CSV."""
    await require_writable_async(runtime)
    return await runtime.send_command(
        "localization_add_entry",
        {
            "path": path,
            "key": key,
            "translations": translations or {},
        },
        timeout=15.0,
    )


async def localization_get_locales(
    runtime: DirectRuntime,
) -> dict:
    """Query loaded locales and translation status from TranslationServer."""
    return await runtime.send_command(
        "localization_get_locales",
        {},
        timeout=10.0,
    )


async def localization_set_locale(
    runtime: DirectRuntime,
    locale: str = "en",
) -> dict:
    """Set the active test locale in TranslationServer."""
    return await runtime.send_command(
        "localization_set_locale",
        {"locale": locale},
        timeout=10.0,
    )


async def localization_translate(
    runtime: DirectRuntime,
    message: str = "",
    context: str = "",
) -> dict:
    """Translate a message string using TranslationServer."""
    return await runtime.send_command(
        "localization_translate",
        {"message": message, "context": context},
        timeout=10.0,
    )


async def localization_extract_strings(
    runtime: DirectRuntime,
    root_dir: str = "res://",
) -> dict:
    """Scan GDScript and scene files for tr() translation calls."""
    return await runtime.send_command(
        "localization_extract_strings",
        {"root_dir": root_dir},
        timeout=30.0,
    )
