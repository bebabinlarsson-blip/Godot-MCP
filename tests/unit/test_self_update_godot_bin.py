"""Unit tests for GODOT_BIN resolution in the self-update fixture.

Issue #917: when CI sets GODOT_BIN to a name that does not resolve,
pytest.skip() made the whole step exit 0 with zero tests executed.
Unset still skips so a local run without an engine stays optional.

On Windows, setup-godot's ``godot`` alias is extensionless, so
``shutil.which("godot")`` misses an engine that later bash steps can
invoke. Resolution must find ``godot.exe`` / the setup-godot path.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tests.integration._self_update_fixture import (
    _windows_godot_fallbacks,
    godot_bin_or_skip,
)


def test_godot_bin_unset_skips(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GODOT_BIN", raising=False)

    with pytest.raises(pytest.skip.Exception, match="GODOT_BIN is not set"):
        godot_bin_or_skip()


def test_godot_bin_directory_fails(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("GODOT_BIN", str(tmp_path))
    monkeypatch.delenv("GODOT", raising=False)
    monkeypatch.delenv("GODOT4", raising=False)
    monkeypatch.setattr(
        "tests.integration._self_update_fixture.shutil.which",
        lambda _name: None,
    )

    with pytest.raises(pytest.fail.Exception, match="does not resolve"):
        godot_bin_or_skip()


def test_godot_bin_set_but_unresolvable_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GODOT_BIN", "godot-ai-missing-binary-917")
    monkeypatch.delenv("GODOT", raising=False)
    monkeypatch.delenv("GODOT4", raising=False)
    monkeypatch.setattr(
        "tests.integration._self_update_fixture.shutil.which",
        lambda _name: None,
    )

    with pytest.raises(pytest.fail.Exception, match="does not resolve"):
        godot_bin_or_skip()


def test_windows_fallback_resolves_godot_exe(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    exe = tmp_path / "godot.exe"
    exe.write_bytes(b"fake")
    monkeypatch.setattr(
        "tests.integration._self_update_fixture.shutil.which",
        lambda name: str(exe) if name == "godot.exe" else None,
    )
    monkeypatch.delenv("GODOT", raising=False)
    monkeypatch.delenv("GODOT4", raising=False)

    assert _windows_godot_fallbacks("godot") == exe


def test_windows_fallback_walks_path_for_extensionless_alias(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    alias = tmp_path / "godot"
    alias.write_bytes(b"fake")
    monkeypatch.setattr(
        "tests.integration._self_update_fixture.shutil.which",
        lambda _name: None,
    )
    monkeypatch.delenv("GODOT", raising=False)
    monkeypatch.delenv("GODOT4", raising=False)
    monkeypatch.setenv("PATH", str(tmp_path))

    assert _windows_godot_fallbacks("godot") == alias


def test_windows_fallback_uses_setup_godot_env(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    alias = tmp_path / "bin" / "godot"
    alias.parent.mkdir()
    alias.write_bytes(b"fake")
    monkeypatch.setattr(
        "tests.integration._self_update_fixture.shutil.which",
        lambda _name: None,
    )
    monkeypatch.setenv("GODOT", str(alias))
    monkeypatch.delenv("GODOT4", raising=False)
    monkeypatch.setenv("PATH", "")

    assert _windows_godot_fallbacks("godot") == alias


def test_windows_fallback_finds_setup_godot_install_exe(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    exe = tmp_path / "godot" / "Godot_v4.7.0-stable_win64.exe"
    exe.parent.mkdir()
    exe.write_bytes(b"fake")
    monkeypatch.setattr(
        "tests.integration._self_update_fixture.shutil.which",
        lambda _name: None,
    )
    monkeypatch.delenv("GODOT", raising=False)
    monkeypatch.delenv("GODOT4", raising=False)
    monkeypatch.setenv("PATH", "")
    monkeypatch.setattr(
        "tests.integration._self_update_fixture.Path.home",
        lambda: tmp_path,
    )

    assert _windows_godot_fallbacks("godot") == exe


def test_godot_bin_uses_windows_fallbacks_when_which_misses(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    exe = tmp_path / "godot.exe"
    exe.write_bytes(b"fake")
    monkeypatch.setenv("GODOT_BIN", "godot")
    # Patch the local helper, not os.name — that aliases the real os module
    # and makes pathlib instantiate WindowsPath on Linux CI.
    monkeypatch.setattr(
        "tests.integration._self_update_fixture._is_windows",
        lambda: True,
    )
    monkeypatch.setattr(
        "tests.integration._self_update_fixture.shutil.which",
        lambda name: str(exe) if name == "godot.exe" else None,
    )
    monkeypatch.delenv("GODOT", raising=False)
    monkeypatch.delenv("GODOT4", raising=False)

    assert godot_bin_or_skip() == str(exe)
