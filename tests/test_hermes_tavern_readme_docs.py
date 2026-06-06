import re
from pathlib import Path

from hermes_tavern.commands import TAVERN_COMMAND_TABLE


REPO_ROOT = Path(__file__).resolve().parents[1]
README = REPO_ROOT / "README.md"

DEFERRED_NOVEL_COMMAND_LITERALS = (
    "/rp project archive",
    "/rp project import",
    "/rp project zip",
    "/rp novel import",
    "/rp novel archive",
    "/rp project outline generate",
    "/rp project outline rewrite",
    "/rp project outline expand",
    "/rp project outline compress",
    "/rp outline generate",
    "/rp outline rewrite",
    "/rp outline expand",
    "/rp outline compress",
    "/rp canon check",
    "/rp canon conflict",
    "/rp canon pin",
    "/rp relationship graph",
    "/rp relationship alias",
    "/rp relationship merge",
    "/rp relationship split",
    "/rp relationship extract",
    "/rp location map",
    "/rp location geocode",
    "/rp location coordinates",
    "/rp project volume",
    "/rp project arc",
    "/rp volume",
    "/rp arc",
)


def _command_segment_has_literal(surface_text: str, literal: str) -> bool:
    for line in surface_text.splitlines():
        for segment in re.split(r"\s\|\s", line):
            candidate = segment.strip()
            if candidate == literal or candidate.startswith(literal + " "):
                return True
    return False


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


def _readme_section_text(section_name: str) -> str:
    marker = f"## {section_name}"
    text = _readme_text()
    assert marker in text
    section = text.split(marker, maxsplit=1)[1]
    return section.split("\n## ", maxsplit=1)[0]


def test_readme_mentions_rp_doctor():
    assert "/rp doctor" in _readme_text()


def test_readme_has_compatibility_section():
    assert "## Compatibility" in _readme_text()


def test_readme_compatibility_wiring_is_public_safe():
    compatibility = _readme_section_text("Compatibility").lower()

    assert "python 3.11" in compatibility
    assert "hermes agent gateway" in compatibility
    assert "plugin" in compatibility
    assert "sillytavern" in compatibility
    assert "json/png" in compatibility
    assert "character cards" in compatibility
    assert "webp/jpeg" in compatibility
    assert "unsupported" in compatibility
    assert "friendly" in compatibility
    assert "unsupported-format" in compatibility


def test_readme_compatibility_has_no_operational_provider_network_or_credential_guidance():
    compatibility = _readme_section_text("Compatibility").lower()

    forbidden_guidance = [
        "gateway start",
        "gateway restart",
        "gateway reload",
        "gateway kill",
        "systemctl",
        "docker compose",
        "service start",
        "service restart",
        "curl ",
        "provider",
        "network",
        "api key",
        "secret",
        "credential",
        "paste",
        "provide",
    ]

    for phrase in forbidden_guidance:
        assert phrase not in compatibility


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


def test_readme_development_links_to_support_guide():
    text = _readme_text()
    marker = "## Development"
    assert marker in text
    development = text.split(marker, maxsplit=1)[1].split("\n## ", maxsplit=1)[0]
    assert "SUPPORT.md" in development


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


def test_readme_core_commands_includes_debug_context_literal():
    core_commands = _readme_core_commands_text()

    assert "/rp debug context [limit] [page]" in core_commands


def test_readme_core_commands_includes_scene_goal_literals():
    core_commands = _readme_core_commands_text()

    assert "/rp scene goal <scene-id> [text]" in core_commands
    assert "/rp scene goal clear <scene-id>" in core_commands


def test_readme_core_commands_include_scene_beat_literals():
    core_commands = _readme_core_commands_text()

    assert "/rp scene beat add <scene-id> <label> <beat...>" in core_commands
    assert "/rp scene beat list <scene-id>" in core_commands
    assert "/rp scene beat inspect <beat-id>" in core_commands
    assert "/rp scene beat update <beat-id> <beat...>" in core_commands
    assert "/rp scene beat delete <beat-id>" in core_commands


def test_readme_core_commands_includes_scene_narration_literals():
    core_commands = _readme_core_commands_text()

    assert "/rp scene narration <scene-id>" in core_commands
    assert "/rp scene narration clear <scene-id>" in core_commands
    assert "/rp scene narration pov <scene-id> <label>" in core_commands
    assert "/rp scene narration tense <scene-id> <past|present>" in core_commands


def test_readme_core_commands_includes_scene_and_chapter_summary_literals():
    core_commands = _readme_core_commands_text()

    assert "/rp chapter inspect <chapter-id>" in core_commands
    assert "/rp chapter summary <chapter-id> [text]" in core_commands
    assert "/rp chapter summary clear <chapter-id>" in core_commands
    assert "/rp scene inspect <scene-id>" in core_commands
    assert "/rp scene summary <scene-id> [text]" in core_commands
    assert "/rp scene summary clear <scene-id>" in core_commands


def test_readme_core_commands_include_timeline_literals():
    core_commands = _readme_core_commands_text()

    assert "/rp timeline add/list" in core_commands
    assert "/rp timeline inspect <timeline-id>" in core_commands


def test_readme_core_commands_include_project_style_literals():
    core_commands = _readme_core_commands_text()

    assert "/rp project style [project-id]" in core_commands
    assert "/rp project style inspect [project-id]" in core_commands
    assert "/rp project style set [project-id] <text>" in core_commands
    assert "/rp project style clear [project-id]" in core_commands


def test_readme_core_commands_include_style_sample_literals():
    core_commands = _readme_core_commands_text()

    assert "/rp style sample add <project-id> <label> <sample...>" in core_commands
    assert "/rp style sample list [project-id]" in core_commands
    assert "/rp style sample inspect <style-sample-id>" in core_commands
    assert "/rp style sample update <style-sample-id> <sample...>" in core_commands
    assert "/rp style sample delete <style-sample-id>" in core_commands


def test_readme_core_commands_include_project_revision_literals():
    core_commands = _readme_core_commands_text()

    assert "/rp project revision add <project-id> <label> <note...>" in core_commands
    assert "/rp project revision list [project-id]" in core_commands
    assert "/rp project revision inspect <note-id>" in core_commands
    assert "/rp project revision update <note-id> <note...>" in core_commands
    assert "/rp project revision delete <note-id>" in core_commands


def test_readme_core_commands_include_binding_literals():
    core_commands = _readme_core_commands_text()

    assert "/rp binding set <project|chapter|scene> <scope-id> <card|preset|lorebook|persona> <asset-id>" in core_commands
    assert "/rp binding list <project|chapter|scene> <scope-id>" in core_commands
    assert "/rp binding inspect <binding-id>" in core_commands
    assert "/rp binding clear <binding-id>" in core_commands
    assert "metadata-only/inert" in core_commands
    assert "not auto-applied to prompts, sessions, providers, or generation" in core_commands


def test_readme_core_commands_include_project_brief_literals():
    core_commands = _readme_core_commands_text()

    assert "/rp project brief [project-id]" in core_commands
    assert "/rp project brief inspect [project-id]" in core_commands
    assert "/rp project brief type set <project-id> <novel|serial|rp|worldbuilding|other>" in core_commands
    assert "/rp project brief type clear <project-id>" in core_commands
    assert "/rp project brief premise set <project-id> <text>" in core_commands
    assert "/rp project brief premise clear <project-id>" in core_commands


def test_readme_core_commands_include_project_inspect_literal():
    core_commands = _readme_core_commands_text()

    assert "/rp project inspect <project-id>" in core_commands


def test_readme_core_commands_include_project_outline_literals():
    core_commands = _readme_core_commands_text()

    assert "/rp project outline [project-id]" in core_commands
    assert "/rp project outline inspect [project-id]" in core_commands
    assert "/rp project outline set [project-id] <text>" in core_commands
    assert "/rp project outline clear [project-id]" in core_commands


def test_readme_core_commands_include_canon_inspect_literal():
    core_commands = _readme_core_commands_text()

    assert "/rp canon inspect <canon-id>" in core_commands


def test_readme_core_commands_omit_deferred_novel_command_literals():
    core_commands = _readme_core_commands_text()

    for literal in DEFERRED_NOVEL_COMMAND_LITERALS:
        assert not _command_segment_has_literal(core_commands, literal)


def test_readme_core_commands_omit_deferred_canon_commands():
    core_commands = _readme_core_commands_text()

    assert not _command_segment_has_literal(core_commands, "/rp canon check")
    assert not _command_segment_has_literal(core_commands, "/rp canon conflict")
    assert not _command_segment_has_literal(core_commands, "/rp canon pin")


def test_readme_core_commands_keeps_current_allowed_command_literals():
    core_commands = _readme_core_commands_text()

    assert _command_segment_has_literal(core_commands, "/rp export [markdown|st-json]")
    assert _command_segment_has_literal(core_commands, "/rp archive")


def test_readme_core_commands_include_character_state_literals():
    core_commands = _readme_core_commands_text()

    assert "/rp character state add <project-id> <label> <state...>" in core_commands
    assert "/rp character state list [project-id]" in core_commands
    assert "/rp character state inspect <character-state-id>" in core_commands
    assert "/rp character state update <character-state-id> <state...>" in core_commands
    assert "/rp character state delete <character-state-id>" in core_commands


def test_readme_core_commands_include_relationship_state_literals():
    core_commands = _readme_core_commands_text()

    assert "/rp relationship add <project-id> <label> <state...>" in core_commands
    assert "/rp relationship list [project-id]" in core_commands
    assert "/rp relationship inspect <relationship-id>" in core_commands
    assert "/rp relationship rename <relationship-id> <label>" in core_commands
    assert "/rp relationship update <relationship-id> <state...>" in core_commands
    assert "/rp relationship delete <relationship-id>" in core_commands


def test_readme_core_commands_include_location_state_literals():
    core_commands = _readme_core_commands_text()

    assert "/rp location add <project-id> <label> <description...>" in core_commands
    assert "/rp location list [project-id]" in core_commands
    assert "/rp location inspect <location-id>" in core_commands
    assert "/rp location update <location-id> <description...>" in core_commands
    assert "/rp location delete <location-id>" in core_commands


def test_readme_core_commands_include_organization_state_literals():
    core_commands = _readme_core_commands_text()

    assert "/rp organization add <project-id> <label> <description...>" in core_commands
    assert "/rp organization list [project-id]" in core_commands
    assert "/rp organization inspect <organization-id>" in core_commands
    assert "/rp organization update <organization-id> <description...>" in core_commands
    assert "/rp organization delete <organization-id>" in core_commands


def test_readme_core_commands_include_plot_thread_literals():
    core_commands = _readme_core_commands_text()

    assert "/rp plot thread add <project-id> <label> <description...>" in core_commands
    assert "/rp plot thread list [project-id]" in core_commands
    assert "/rp plot thread inspect <plot-thread-id>" in core_commands
    assert "/rp plot thread update <plot-thread-id> <description...>" in core_commands
    assert "/rp plot thread delete <plot-thread-id>" in core_commands


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


def _readme_public_policy_text() -> str:
    return _readme_section_text("Development")


def test_readme_public_policy_navigation_block_has_required_links():
    public_policy = _readme_public_policy_text()
    required_links = [
        "[CONTRIBUTING.md](CONTRIBUTING.md)",
        "[SUPPORT.md](SUPPORT.md)",
        "[SECURITY.md](SECURITY.md)",
        "[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)",
        "[CHANGELOG.md](CHANGELOG.md)",
    ]

    for link in required_links:
        assert link in public_policy


def test_readme_public_policy_navigation_block_has_no_forbidden_operational_runtime_or_credential_guidance():
    public_policy = _readme_public_policy_text().lower()

    forbidden_guidance = [
        "gateway start",
        "gateway restart",
        "gateway reload",
        "gateway kill",
        "systemctl",
        "docker compose",
        "service start",
        "service restart",
        "curl ",
        "api key",
        "secret",
        "credential",
        "paste",
        "provide",
    ]

    for phrase in forbidden_guidance:
        assert phrase not in public_policy


def test_readme_license_section_has_mit_link_and_mit_wording():
    license_section = _readme_section_text("License").lower()

    assert "[mit license](license)" in license_section
    assert "mit" in license_section
    assert "license" in license_section


def test_readme_license_section_has_no_forbidden_operational_provider_network_or_credential_guidance():
    license_section = _readme_section_text("License").lower()

    forbidden_guidance = [
        "gateway start",
        "gateway restart",
        "gateway reload",
        "gateway kill",
        "provider",
        "network",
        "service start",
        "service restart",
        "systemctl",
        "docker compose",
        "curl ",
        "api key",
        "secret",
        "credential",
        "paste",
        "provide",
    ]

    for phrase in forbidden_guidance:
        assert phrase not in license_section
