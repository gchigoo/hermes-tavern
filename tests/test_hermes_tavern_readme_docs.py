import re
from pathlib import Path

from hermes_tavern.commands import TAVERN_COMMAND_TABLE


REPO_ROOT = Path(__file__).resolve().parents[1]
README = REPO_ROOT / "README.md"


def _readme_text() -> str:
    return README.read_text(encoding="utf-8")


def _readme_core_commands_text() -> str:
    text = _readme_text()
    marker = "## Core commands"
    assert marker in text
    core = text.split(marker, maxsplit=1)[1]
    return core.split("\n## ", maxsplit=1)[0]


def _readme_release_preflight_text() -> str:
    text = _readme_text()
    marker = "## Release preflight"
    assert marker in text
    section = text.split(marker, maxsplit=1)[1]
    return section.split("\n## ", maxsplit=1)[0]


def test_readme_mentions_rp_doctor():
    assert "/rp doctor" in _readme_text()


def test_readme_has_public_status_and_positioning():
    readme = _readme_text().lower()

    assert "beta / experimental" in readme
    assert "sillytavern-compatible rp/novel runtime" in readme


def test_readme_has_public_safety_publication_note():
    readme = _readme_text().lower()

    assert "fictional roleplay" in readme
    assert "does not bypass" in readme
    assert "no real api keys or credentials" in readme


def test_readme_has_release_preflight_section():
    assert "## Release preflight" in _readme_text()


def test_readme_release_preflight_has_offline_gates():
    preflight = _readme_release_preflight_text().lower()

    offline_gates = [
        "python -m py_compile",
        "python -m pip install -r requirements-test.txt",
        "python -m pytest tests/test_hermes_tavern_readme_docs.py -q -o 'addopts='",
        "python -m pytest tests/test_hermes_tavern_packaging.py -q -o 'addopts='",
        "python -m pytest tests/test_hermes_tavern_*.py -q -o 'addopts='",
    ]

    for gate in offline_gates:
        assert gate in preflight

    assert "wheel/sdist artifact inspection" in preflight
    assert "isolated wheel install" in preflight
    assert "entry point metadata" in preflight
    assert "wheel payload boundary" in preflight
    assert "hermes gateway restart" not in preflight
    assert "curl " not in preflight
    assert "docker compose" not in preflight
    assert "systemctl" not in preflight


def test_readme_release_preflight_mentions_requirements_test():
    preflight = _readme_release_preflight_text().lower()
    assert "requirements-test.txt" in preflight
    assert "python -m pip install -r requirements-test.txt" in preflight


def test_readme_release_preflight_is_offline_only():
    preflight = _readme_release_preflight_text().lower()

    forbidden = [
        "hermes gateway restart",
        "systemctl",
        "docker compose",
        "curl ",
    ]

    for command in forbidden:
        assert command not in preflight


def test_readme_does_not_include_executable_gateway_restart():
    assert "hermes gateway restart" not in _readme_text()


def test_readme_keeps_install_or_enablement_guidance():
    readme = _readme_text()

    has_package_install = "python -m pip install -e /path/to/hermes-tavern" in readme
    has_plugin_enablement = "hermes plugins enable hermes-tavern" in readme

    assert has_package_install or has_plugin_enablement


def test_readme_development_links_to_contributing_guide():
    text = _readme_text()
    marker = "## Development"
    assert marker in text
    development = text.split(marker, maxsplit=1)[1].split("\n## ", maxsplit=1)[0]
    assert "CONTRIBUTING.md" in development


def test_readme_core_commands_cover_command_table():
    core_commands = _readme_core_commands_text()
    missing = [
        f"/rp {command}"
        for command in TAVERN_COMMAND_TABLE
        if re.search(rf"/rp\s+{re.escape(command)}\b", core_commands) is None
    ]

    assert missing == []


def test_readme_core_commands_keep_operator_anchors():
    core_commands = _readme_core_commands_text()
    anchors = [
        "/rp model status",
        "/rp prompt list",
        "/rp content mode",
        "/rp assets",
        "/rp cards",
        "/rp debug prompt",
    ]
    missing = [anchor for anchor in anchors if anchor not in core_commands]

    assert missing == []


def test_readme_card_import_format_docs_are_accurate():
    card_import_lines = [
        line.strip()
        for line in _readme_text().splitlines()
        if line.strip().startswith("/rp card import")
    ]
    card_import_docs = "\n".join(card_import_lines).lower()

    assert len(card_import_lines) >= 2
    assert "json/png" in card_import_docs
    assert "webp/jpeg" in card_import_docs
    assert "not supported yet" in card_import_docs
    assert "friendly" in card_import_docs
    assert "unsupported-format" in card_import_docs
    assert "json/png/webp" not in card_import_docs
    assert "json/png/jpeg" not in card_import_docs
    assert "json/png/jpg" not in card_import_docs
    assert "json, png, webp" not in card_import_docs
    assert "json, png, jpeg" not in card_import_docs
    assert "json, png, jpg" not in card_import_docs
