"""Publication resume paths that the first v4.0.0 release exercised for real."""

from __future__ import annotations

import urllib.error

import pytest

from script import release_promotion as promotion
from script import release_support as support

BASE = f"repos/{support.REPOSITORY}"


def test_release_for_tag_finds_the_draft_the_tag_endpoint_hides(monkeypatch):
    draft = {"tag_name": "v4.0.0", "draft": True, "id": 1}

    def fake_gh(*args, allow_missing=False):
        if args[0].startswith(f"{BASE}/releases/tags/"):
            assert allow_missing
            return None
        if args[0] == f"{BASE}/releases?per_page=100":
            return [{"tag_name": "v3.2.5", "draft": False}, draft]
        raise AssertionError(args)

    monkeypatch.setattr(promotion, "gh", fake_gh)
    assert promotion._release_for_tag(BASE, "v4.0.0") == draft
    assert promotion._release_for_tag(BASE, "v4.0.1") is None

    published = {"tag_name": "v4.0.0", "draft": False}
    monkeypatch.setattr(promotion, "gh", lambda *a, allow_missing=False: published)
    assert promotion._release_for_tag(BASE, "v4.0.0") is published


def _not_found(url):
    raise urllib.error.HTTPError(url, 404, "Not Found", {}, None)


def test_verify_pypi_waits_for_the_index_to_list_a_fresh_upload(monkeypatch):
    record = {"version": "4.0.0", "files": {}}
    calls = []

    def lagging_index(url):
        calls.append(url)
        if len(calls) < 3:
            _not_found(url)
        return {"urls": []}

    monkeypatch.setattr(promotion, "public_json", lagging_index)
    monkeypatch.setattr(promotion.time, "sleep", lambda seconds: None)
    with pytest.raises(support.ReleaseError, match="incomplete or unexpected"):
        promotion.verify_pypi(record)  # listed on the third try, then the inventory check runs
    assert len(calls) == 3

    monkeypatch.setattr(promotion, "public_json", _not_found)
    monkeypatch.setattr(promotion, "PYPI_INDEX_WAIT_SECONDS", 0.0)
    with pytest.raises(support.ReleaseError, match="still does not list 4.0.0"):
        promotion.verify_pypi(record)

    def forbidden(url):
        raise urllib.error.HTTPError(url, 403, "Forbidden", {}, None)

    monkeypatch.setattr(promotion, "public_json", forbidden)
    with pytest.raises(urllib.error.HTTPError):
        promotion.verify_pypi(record)  # only a 404 is the index lagging


def test_verify_pypi_never_waits_past_its_deadline(monkeypatch):
    # A controlled clock: each lookup costs 100 s, so the third 404 lands at
    # 300 s and the wait must clamp to the budget rather than add a poll.
    record = {"version": "4.0.0", "files": {}}
    clock = {"now": 0.0}
    sleeps = []
    monkeypatch.setattr(promotion.time, "monotonic", lambda: clock["now"])
    monkeypatch.setattr(promotion.time, "sleep", lambda seconds: sleeps.append(seconds))
    monkeypatch.setattr(promotion, "PYPI_INDEX_WAIT_SECONDS", 300.0)
    monkeypatch.setattr(promotion, "PYPI_INDEX_POLL_SECONDS", 15.0)

    def lookup(url):
        clock["now"] += 100.0
        _not_found(url)

    monkeypatch.setattr(promotion, "public_json", lookup)
    with pytest.raises(support.ReleaseError, match="still does not list 4.0.0"):
        promotion.verify_pypi(record)
    assert sleeps == [15.0, 15.0], "the third lookup hit the deadline; no sleep past it"

    clock["now"] = 0.0
    sleeps.clear()
    monkeypatch.setattr(promotion, "PYPI_INDEX_WAIT_SECONDS", 105.0)
    with pytest.raises(support.ReleaseError, match="still does not list 4.0.0"):
        promotion.verify_pypi(record)
    assert sleeps == [5.0], "a sleep is clamped to the remaining budget"


def test_release_notes_pin_the_guides_at_the_source_and_append_generated_notes(monkeypatch):
    record = {"tag": "v4.0.3", "source": "abc123"}
    calls = []

    def fake_gh(*args, allow_missing=False):
        calls.append(args)
        return {
            "body": "## What's Changed\n* fix: x by @y in https://github.com/hi-godot/godot-ai/pull/1\n\n"
        }

    monkeypatch.setattr(promotion, "gh", fake_gh)
    body = promotion.release_notes(record, "4.0.2")

    assert calls == [
        (
            "--method",
            "POST",
            f"{BASE}/releases/generate-notes",
            "-f",
            "tag_name=v4.0.3",
            "-f",
            "target_commitish=abc123",
            "-f",
            "previous_tag_name=v4.0.2",
        )
    ]
    blob = f"https://github.com/{support.REPOSITORY}/blob/abc123"
    assert body.splitlines() == [
        f"See the version-pinned migration guide: {blob}/docs/v4-migration.md",
        f"Changelog: {blob}/CHANGELOG.md",
        "",
        "## What's Changed",
        "* fix: x by @y in https://github.com/hi-godot/godot-ai/pull/1",
    ]
    assert body.endswith("\n")


def test_release_notes_fall_back_to_the_links_when_generation_fails(monkeypatch, capsys):
    def failing_gh(*args, allow_missing=False):
        raise support.ReleaseError("GitHub API request failed: HTTP 422")

    monkeypatch.setattr(promotion, "gh", failing_gh)
    body = promotion.release_notes({"tag": "v4.0.3", "source": "abc123"}, "4.0.2")

    blob = f"https://github.com/{support.REPOSITORY}/blob/abc123"
    assert body == (
        f"See the version-pinned migration guide: {blob}/docs/v4-migration.md\n"
        f"Changelog: {blob}/CHANGELOG.md\n"
    )
    assert "did not generate notes" in capsys.readouterr().err

    monkeypatch.setattr(promotion, "gh", lambda *a, allow_missing=False: {"body": "   \n"})
    assert promotion.release_notes({"tag": "v4.0.3", "source": "abc123"}, "4.0.2") == body


def test_publish_github_creates_the_draft_with_the_composed_notes(monkeypatch, tmp_path):
    files = {f"release/{name}": {"size": 1, "sha256": "0" * 64} for name in support.RELEASE_NAMES}
    record = {"version": "4.0.3", "tag": "v4.0.3", "source": "abc123", "files": files}
    create_values = []
    state = {"release": None}

    def fake_gh(*args, allow_missing=False):
        if args[0] == f"{BASE}/git/ref/tags/v4.0.3":
            return None
        if args[:3] == ("--method", "POST", f"{BASE}/git/refs"):
            return {}
        if args[:3] == ("--method", "POST", f"{BASE}/releases/generate-notes"):
            return {"body": "## What's Changed\n* one\n"}
        if args[:3] == ("--method", "POST", f"{BASE}/releases"):
            create_values.extend(args[4::2])  # the values after each -f / -F flag
            state["release"] = {"id": 7, "draft": True, "prerelease": False, "assets": []}
            return state["release"]
        if args[:3] == ("--method", "PATCH", f"{BASE}/releases/7"):
            state["release"] = {**state["release"], "draft": False}
            return state["release"]
        raise AssertionError(args)

    def fake_preflight(_record):
        release = state["release"]
        if release is not None and not release["assets"]:
            release["assets"] = [
                {"name": name, "browser_download_url": f"https://github.com/x/{name}"}
                for name in sorted(support.RELEASE_NAMES)
            ]
        return release

    monkeypatch.setattr(promotion, "gh", fake_gh)
    monkeypatch.setattr(promotion, "verify_pypi", lambda _record: {})
    monkeypatch.setattr(promotion, "github_preflight", fake_preflight)
    monkeypatch.setattr(promotion, "verify_public_file", lambda url, expected, hosts: None)
    uploads = []
    monkeypatch.setattr(
        promotion.subprocess, "run", lambda argv, check: uploads.append(argv) or None
    )

    result = promotion.publish_github(tmp_path, record, "4.0.2")

    blob = f"https://github.com/{support.REPOSITORY}/blob/abc123"
    assert "draft=true" in create_values and "name=Godot AI 4.0.3" in create_values
    assert create_values[-1] == (
        f"body=See the version-pinned migration guide: {blob}/docs/v4-migration.md\n"
        f"Changelog: {blob}/CHANGELOG.md\n"
        "\n"
        "## What's Changed\n* one\n"
    )
    assert len(uploads) == 1 and uploads[0][:3] == ["gh", "release", "upload"]
    assert set(result) == set(support.RELEASE_NAMES)
