import pytest
import re

from plugins.hermes_tavern.commands import (
    RPCommand,
    TAVERN_COMMAND_TABLE,
    TavernCommandEntry,
    _build_help_text,
    dispatch_command,
    parse_rp_command,
)


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

DEFERRED_TOP_LEVEL_AND_PSEUDO_FAMILIES = (
    "novel",
    "volume",
    "arc",
    "outline",
    "project-import",
    "project-archive",
    "canon-check",
    "canon-conflict",
    "canon-pin",
    "relationship-graph",
    "relationship-alias",
    "relationship-merge",
    "relationship-split",
    "geocode",
)


def _command_segment_has_literal(surface_text: str, literal: str) -> bool:
    for line in surface_text.splitlines():
        for segment in re.split(r"\s\|\s", line):
            candidate = segment.strip()
            if candidate == literal or candidate.startswith(literal + " "):
                return True
    return False


@pytest.mark.parametrize(
    "text",
    [
        "hello",
        "ordinary chat",
        "ordinary /rp help",
        "/rpx help",
        " /rpx help ",
        "/rphelp",
        "/rpstart Alice",
    ],
)
def test_parse_rp_command_ignores_non_rp_text(text):
    assert parse_rp_command(text) is None


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("/rp", RPCommand(name="help", args=[], raw="/rp")),
        ("\t/rp\n", RPCommand(name="help", args=[], raw="/rp")),
        ("/rp help", RPCommand(name="help", args=[], raw="/rp help")),
        ("/rp status", RPCommand(name="status", args=[], raw="/rp status")),
        ("/rp StAtUs", RPCommand(name="status", args=[], raw="/rp StAtUs")),
        ("/rp end", RPCommand(name="end", args=[], raw="/rp end")),
        (
            "/rp start Alice",
            RPCommand(name="start", args=["Alice"], raw="/rp start Alice"),
        ),
        (
            "\t/rp\tStart\tAlice\nBob  ",
            RPCommand(
                name="start",
                args=["Alice", "Bob"],
                raw="/rp\tStart\tAlice\nBob",
            ),
        ),
    ],
)
def test_parse_rp_command_returns_structured_command(text, expected):
    assert parse_rp_command(text) == expected


def test_parse_rp_command_tolerates_extra_whitespace():
    assert parse_rp_command("  /rp   start   Alice   Bob  ") == RPCommand(
        name="start",
        args=["Alice", "Bob"],
        raw="/rp   start   Alice   Bob",
    )


def test_parse_rp_command_keeps_unknown_commands_structural():
    assert parse_rp_command(" \n/rp Mystery arg-one arg-two\t") == RPCommand(
        name="mystery",
        args=["arg-one", "arg-two"],
        raw="/rp Mystery arg-one arg-two",
    )


def test_help_output_is_generated_from_command_table_help_lines():
    expected_lines = ["Hermes Tavern commands:"]
    for entry in TAVERN_COMMAND_TABLE.values():
        expected_lines.extend(entry.help_lines)

    assert _build_help_text().splitlines() == expected_lines


def test_help_includes_rp_debug_context_usage():
    help_text = _build_help_text()

    assert "/rp debug context [limit] [page]" in help_text


def test_help_lists_image_configuration_commands():
    help_text = _build_help_text()

    assert "/rp image settings [set <key> <value>|clear <key|all>|export]" in help_text
    assert (
        "/rp image style [list|save <name>|use <name>|inspect <name>|delete <name>]"
        in help_text
    )
    assert "/rp image safety [inspect|mode <safe|mature|explicit>|clear]" in help_text


def test_help_lists_asset_and_prompt_control_commands():
    help_text = _build_help_text()

    assert "/rp card search <query>" in help_text
    assert "/rp prompt list" in help_text
    assert "/rp prompt enable <module>" in help_text
    assert "/rp prompt disable <module>" in help_text
    assert "/rp lore enable <entry>" in help_text
    assert "/rp lore disable <entry>" in help_text
    assert "/rp memory forget <fact-id|all>" in help_text
    assert (
        "/rp memory summary [set <text>|clear|summarize [limit] [live]]"
        in help_text
    )
    assert "/rp persona new <name> <text>" in help_text
    assert "/rp persona temp <text>" in help_text


def test_help_lists_lore_export_command():
    help_text = _build_help_text()

    assert "/rp lore export <lorebook>" in help_text


def test_help_lists_project_style_commands():
    help_text = _build_help_text()

    assert "/rp project style" in help_text
    assert "/rp project style inspect [project-id]" in help_text
    assert "/rp project style set [project-id] <text>" in help_text
    assert "/rp project style clear [project-id]" in help_text


def test_help_lists_project_inspect_command():
    help_text = _build_help_text()

    assert "/rp project inspect <project-id>" in help_text


def test_help_lists_project_revision_commands():
    help_text = _build_help_text()

    assert "/rp project revision add <project-id> <label> <note...>" in help_text
    assert "/rp project revision list [project-id]" in help_text
    assert "/rp project revision inspect <note-id>" in help_text
    assert "/rp project revision update <note-id> <note...>" in help_text
    assert "/rp project revision delete <note-id>" in help_text


def test_help_lists_timeline_commands():
    help_text = _build_help_text()

    assert "/rp timeline add <project-id> <date> <title> [description...]" in help_text
    assert "/rp timeline list [project-id]" in help_text
    assert "/rp timeline inspect <timeline-id>" in help_text


def test_help_lists_binding_commands():
    help_text = _build_help_text()

    assert "/rp binding set <project|chapter|scene> <scope-id> <card|preset|lorebook|persona> <asset-id>" in help_text
    assert "/rp binding list <project|chapter|scene> <scope-id>" in help_text
    assert "/rp binding inspect <binding-id>" in help_text
    assert "/rp binding clear <binding-id>" in help_text
    assert "/rp binding rows are metadata-only/inert; not auto-applied" in help_text


def test_help_lists_style_sample_commands():
    help_text = _build_help_text()

    assert "/rp style sample add <project-id> <label> <sample...>" in help_text
    assert "/rp style sample list [project-id]" in help_text
    assert "/rp style sample inspect <style-sample-id>" in help_text
    assert "/rp style sample update <style-sample-id> <sample...>" in help_text
    assert "/rp style sample delete <style-sample-id>" in help_text


def test_help_lists_chapter_and_scene_summary_commands():
    help_text = _build_help_text()

    assert "/rp chapter inspect <chapter-id>" in help_text
    assert "/rp chapter summary <chapter-id> [text]" in help_text
    assert "/rp chapter summary clear <chapter-id>" in help_text
    assert "/rp scene inspect <scene-id>" in help_text
    assert "/rp scene summary <scene-id> [text]" in help_text
    assert "/rp scene summary clear <scene-id>" in help_text


def test_help_lists_scene_beat_commands():
    help_text = _build_help_text()

    assert "/rp scene beat add <scene-id> <label> <beat...>" in help_text
    assert "/rp scene beat list <scene-id>" in help_text
    assert "/rp scene beat inspect <beat-id>" in help_text
    assert "/rp scene beat update <beat-id> <beat...>" in help_text
    assert "/rp scene beat delete <beat-id>" in help_text


def test_help_lists_project_brief_commands():
    help_text = _build_help_text()

    assert "/rp project brief [project-id]" in help_text
    assert "/rp project brief inspect [project-id]" in help_text
    assert "/rp project brief type set <project-id> <novel|serial|rp|worldbuilding|other>" in help_text
    assert "/rp project brief type clear <project-id>" in help_text
    assert "/rp project brief premise set <project-id> <text>" in help_text
    assert "/rp project brief premise clear <project-id>" in help_text


def test_help_lists_project_outline_commands():
    help_text = _build_help_text()

    assert "/rp project outline [project-id]" in help_text
    assert "/rp project outline inspect [project-id]" in help_text
    assert "/rp project outline set [project-id] <text>" in help_text
    assert "/rp project outline clear [project-id]" in help_text


def test_help_lists_canon_commands():
    help_text = _build_help_text()

    assert "/rp canon add <project-id> <title> <content...> [--group <group>]" in help_text
    assert "/rp canon list [project-id] [group]" in help_text
    assert "/rp canon inspect <canon-id>" in help_text
    assert "/rp canon group [project-id] <group>" in help_text


def test_help_omits_deferred_canon_commands():
    help_text = _build_help_text()

    assert not _command_segment_has_literal(help_text, "/rp canon check")
    assert not _command_segment_has_literal(help_text, "/rp canon conflict")
    assert not _command_segment_has_literal(help_text, "/rp canon pin")


def test_help_omits_deferred_novel_command_literals():
    help_text = _build_help_text()

    for literal in DEFERRED_NOVEL_COMMAND_LITERALS:
        assert not _command_segment_has_literal(help_text, literal)


def test_help_keeps_current_allowed_command_literals():
    help_text = _build_help_text()

    assert _command_segment_has_literal(help_text, "/rp project export")
    assert _command_segment_has_literal(help_text, "/rp project export json [project-id]")
    assert _command_segment_has_literal(help_text, "/rp export [markdown|st-json]")
    assert _command_segment_has_literal(help_text, "/rp archive")


def test_help_keeps_current_export_command_literals():
    help_text = _build_help_text()
    literals = (
        "/rp binding export <binding-id>",
        "/rp style sample export <style-sample-id>",
        "/rp character state export <character-state-id>",
        "/rp relationship export <relationship-id>",
        "/rp location export <location-id>",
        "/rp organization export <organization-id>",
        "/rp plot thread export <plot-thread-id>",
        "/rp project revision export <note-id>",
        "/rp chapter export <chapter-id>",
        "/rp scene beat export <beat-id>",
        "/rp scene export <scene-id>",
        "/rp canon export <canon-id>",
        "/rp timeline export <timeline-id>",
    )

    for literal in literals:
        assert _command_segment_has_literal(help_text, literal)


def test_help_lists_relationship_state_commands():
    help_text = _build_help_text()

    assert "/rp relationship add <project-id> <label> <state...>" in help_text
    assert "/rp relationship list [project-id]" in help_text
    assert "/rp relationship inspect <relationship-id>" in help_text
    assert "/rp relationship rename <relationship-id> <label>" in help_text
    assert "/rp relationship update <relationship-id> <state...>" in help_text
    assert "/rp relationship delete <relationship-id>" in help_text


def test_help_lists_location_commands():
    help_text = _build_help_text()

    assert "/rp location add <project-id> <label> <description...>" in help_text
    assert "/rp location list [project-id]" in help_text
    assert "/rp location inspect <location-id>" in help_text
    assert "/rp location update <location-id> <description...>" in help_text
    assert "/rp location delete <location-id>" in help_text


def test_help_lists_organization_commands():
    help_text = _build_help_text()

    assert "/rp organization add <project-id> <label> <description...>" in help_text
    assert "/rp organization list [project-id]" in help_text
    assert "/rp organization inspect <organization-id>" in help_text
    assert "/rp organization update <organization-id> <description...>" in help_text
    assert "/rp organization delete <organization-id>" in help_text


def test_help_lists_plot_thread_commands():
    help_text = _build_help_text()

    assert "/rp plot thread add <project-id> <label> <description...>" in help_text
    assert "/rp plot thread list [project-id]" in help_text
    assert "/rp plot thread inspect <plot-thread-id>" in help_text
    assert "/rp plot thread update <plot-thread-id> <description...>" in help_text
    assert "/rp plot thread delete <plot-thread-id>" in help_text


def test_help_lists_character_state_commands():
    help_text = _build_help_text()

    assert "/rp character state add <project-id> <label> <state...>" in help_text
    assert "/rp character state list [project-id]" in help_text
    assert "/rp character state inspect <character-state-id>" in help_text
    assert "/rp character state update <character-state-id> <state...>" in help_text
    assert "/rp character state delete <character-state-id>" in help_text


def test_help_lists_card_greeting_command():
    help_text = _build_help_text()

    assert "/rp card search <query>" in help_text
    assert "/rp card greeting <card>" in help_text
    assert "/rp card export <card>" in help_text


def test_help_lists_preset_export_command():
    help_text = _build_help_text()

    assert _command_segment_has_literal(help_text, "/rp preset export <preset>")



class RecordingRuntime:
    def __init__(self):
        self.calls = []

    def command_and_event(self, command, event):
        self.calls.append(("command_and_event", command, event))
        return "command+event"

    def event_only(self, event):
        self.calls.append(("event_only", event))
        return "event"

    def command_only(self, command):
        self.calls.append(("command_only", command))
        return "command"

    def no_args(self):
        self.calls.append(("no_args",))
        return "none"


def test_dispatch_command_passes_command_and_event_by_default():
    runtime = RecordingRuntime()
    event = object()
    command = RPCommand("test", ["arg"], "/rp test arg")
    table = {"test": TavernCommandEntry(handler="command_and_event")}

    response = dispatch_command(table, runtime, command, event)

    assert response == "command+event"
    assert runtime.calls == [("command_and_event", command, event)]


def test_dispatch_command_respects_argument_flags():
    runtime = RecordingRuntime()
    event = object()
    command = RPCommand("event", [], "/rp event")
    table = {
        "event": TavernCommandEntry(handler="event_only", needs_command=False),
        "command": TavernCommandEntry(handler="command_only", needs_event=False),
        "none": TavernCommandEntry(
            handler="no_args",
            needs_command=False,
            needs_event=False,
        ),
    }

    assert dispatch_command(table, runtime, command, event) == "event"
    assert (
        dispatch_command(table, runtime, RPCommand("command", [], "/rp command"), event)
        == "command"
    )
    assert (
        dispatch_command(table, runtime, RPCommand("none", [], "/rp none"), event)
        == "none"
    )
    assert runtime.calls == [
        ("event_only", event),
        ("command_only", RPCommand("command", [], "/rp command")),
        ("no_args",),
    ]


def test_dispatch_command_is_case_insensitive_for_table_lookup():
    runtime = RecordingRuntime()
    event = object()
    command = RPCommand("STATUS", [], "/rp STATUS")
    table = {
        "status": TavernCommandEntry(
            handler="no_args",
            needs_command=False,
            needs_event=False,
        )
    }

    assert dispatch_command(table, runtime, command, event) == "none"
    assert runtime.calls == [("no_args",)]


def test_dispatch_command_help_entry_returns_table_help_text():
    runtime = RecordingRuntime()
    command = RPCommand("help", [], "/rp help")
    table = {
        "help": TavernCommandEntry(
            handler="",
            help_lines=["/rp help"],
            needs_command=False,
            needs_event=False,
        )
    }

    response = dispatch_command(table, runtime, command, object())

    assert response.startswith("Hermes Tavern commands:")
    assert "/rp help" in response
    assert runtime.calls == []


def test_dispatch_command_unknown_uses_mobile_safe_preview():
    runtime = RecordingRuntime()
    long_name = "x" * 120
    response = dispatch_command(
        {},
        runtime,
        RPCommand(long_name, [], f"/rp {long_name}"),
        object(),
    )

    assert response.startswith("Unknown /rp command: ")
    assert len(response) < 120
    assert "…" in response
    assert runtime.calls == []


def test_dispatch_command_unknown_after_structural_parse_only():
    runtime = RecordingRuntime()
    command = parse_rp_command("/rp mystery arg")

    assert command == RPCommand(name="mystery", args=["arg"], raw="/rp mystery arg")
    assert (
        dispatch_command({}, runtime, command, object())
        == "Unknown /rp command: mystery"
    )
    assert runtime.calls == []


def test_novel_command_table_does_not_have_top_level_revision_family():
    assert "revision" not in TAVERN_COMMAND_TABLE
    assert "relationship-rename" not in TAVERN_COMMAND_TABLE


def test_tavern_command_table_omits_deferred_top_level_and_pseudo_families():
    for family in DEFERRED_TOP_LEVEL_AND_PSEUDO_FAMILIES:
        assert family not in TAVERN_COMMAND_TABLE


def test_tavern_command_table_keeps_current_allowed_top_level_families():
    assert "project" in TAVERN_COMMAND_TABLE
    assert "export" in TAVERN_COMMAND_TABLE
    assert "archive" in TAVERN_COMMAND_TABLE


def test_tavern_command_table_session_family_includes_export_route():
    assert "/rp session export <id>" in TAVERN_COMMAND_TABLE["session"].help_lines


def test_dispatch_command_resolves_aliases_to_canonical_commands():
    runtime = RecordingRuntime()
    event = object()
    table = {
        "retry": TavernCommandEntry(handler="no_args", needs_command=False, needs_event=False),
        "undo": TavernCommandEntry(handler="no_args", needs_command=False, needs_event=False),
        "end": TavernCommandEntry(handler="no_args", needs_command=False, needs_event=False),
        "start": TavernCommandEntry(handler="no_args", needs_command=False, needs_event=False),
        "pause": TavernCommandEntry(handler="no_args", needs_command=False, needs_event=False),
        "resume": TavernCommandEntry(handler="no_args", needs_command=False, needs_event=False),
    }

    assert dispatch_command(table, runtime, RPCommand("regen", [], "/rp regen"), event) == "none"
    assert dispatch_command(table, runtime, RPCommand("REGENERATE", [], "/rp REGENERATE"), event) == "none"
    assert dispatch_command(table, runtime, RPCommand("reroll", [], "/rp reroll"), event) == "none"
    assert dispatch_command(table, runtime, RPCommand("revert", [], "/rp revert"), event) == "none"
    assert dispatch_command(table, runtime, RPCommand("rollback", [], "/rp rollback"), event) == "none"
    assert dispatch_command(table, runtime, RPCommand("stop", [], "/rp stop"), event) == "none"
    assert dispatch_command(table, runtime, RPCommand("quit", [], "/rp quit"), event) == "none"
    assert dispatch_command(table, runtime, RPCommand("exit", [], "/rp exit"), event) == "none"
    assert dispatch_command(table, runtime, RPCommand("terminate", [], "/rp terminate"), event) == "none"
    assert dispatch_command(table, runtime, RPCommand("halt", [], "/rp halt"), event) == "none"
    assert dispatch_command(table, runtime, RPCommand("abort", [], "/rp abort"), event) == "none"
    assert dispatch_command(table, runtime, RPCommand("close", [], "/rp close"), event) == "none"
    assert dispatch_command(table, runtime, RPCommand("finish", [], "/rp finish"), event) == "none"
    assert dispatch_command(table, runtime, RPCommand("new", [], "/rp new"), event) == "none"
    assert dispatch_command(table, runtime, RPCommand("begin", [], "/rp begin"), event) == "none"
    assert dispatch_command(table, runtime, RPCommand("launch", [], "/rp launch"), event) == "none"
    assert dispatch_command(table, runtime, RPCommand("init", [], "/rp init"), event) == "none"
    assert dispatch_command(table, runtime, RPCommand("open", [], "/rp open"), event) == "none"
    assert dispatch_command(table, runtime, RPCommand("suspend", [], "/rp suspend"), event) == "none"
    assert dispatch_command(table, runtime, RPCommand("hold", [], "/rp hold"), event) == "none"
    assert dispatch_command(table, runtime, RPCommand("freeze", [], "/rp freeze"), event) == "none"
    assert dispatch_command(table, runtime, RPCommand("standby", [], "/rp standby"), event) == "none"
    assert dispatch_command(table, runtime, RPCommand("sleep", [], "/rp sleep"), event) == "none"
    assert dispatch_command(table, runtime, RPCommand("unpause", [], "/rp unpause"), event) == "none"
    assert dispatch_command(table, runtime, RPCommand("continue", [], "/rp continue"), event) == "none"
    assert dispatch_command(table, runtime, RPCommand("proceed", [], "/rp proceed"), event) == "none"
    assert dispatch_command(table, runtime, RPCommand("unhold", [], "/rp unhold"), event) == "none"
    assert dispatch_command(table, runtime, RPCommand("unfreeze", [], "/rp unfreeze"), event) == "none"
    assert dispatch_command(table, runtime, RPCommand("unsuspend", [], "/rp unsuspend"), event) == "none"
    assert dispatch_command(table, runtime, RPCommand("unstandby", [], "/rp unstandby"), event) == "none"
    assert dispatch_command(table, runtime, RPCommand("unsleep", [], "/rp unsleep"), event) == "none"
    assert dispatch_command(table, runtime, RPCommand("wake", [], "/rp wake"), event) == "none"
    assert dispatch_command(table, runtime, RPCommand("wakeup", [], "/rp wakeup"), event) == "none"
    assert dispatch_command(table, runtime, RPCommand("awake", [], "/rp awake"), event) == "none"
    assert dispatch_command(table, runtime, RPCommand("awaken", [], "/rp awaken"), event) == "none"
    assert dispatch_command(table, runtime, RPCommand("revive", [], "/rp revive"), event) == "none"
    assert dispatch_command(table, runtime, RPCommand("reactivate", [], "/rp reactivate"), event) == "none"
    assert dispatch_command(table, runtime, RPCommand("restore", [], "/rp restore"), event) == "none"
    assert dispatch_command(table, runtime, RPCommand("recover", [], "/rp recover"), event) == "none"
    assert dispatch_command(table, runtime, RPCommand("recommence", [], "/rp recommence"), event) == "none"
    assert dispatch_command(table, runtime, RPCommand("reengage", [], "/rp reengage"), event) == "none"
    assert dispatch_command(table, runtime, RPCommand("reinstate", [], "/rp reinstate"), event) == "none"
    assert dispatch_command(table, runtime, RPCommand("reanimate", [], "/rp reanimate"), event) == "none"
    assert dispatch_command(table, runtime, RPCommand("resurrect", [], "/rp resurrect"), event) == "none"
    assert len(runtime.calls) == 44


def test_card_command_empty_args_returns_usage():
    from hermes_tavern.runtime_assets import card_command

    runtime = RecordingRuntime()
    event = object()
    result = card_command(runtime, RPCommand("card", [], "/rp card"), event)
    assert result.startswith("Usage: /rp card")
    assert "/rp card import <file>" in result
    assert "/rp card search <query>" in result
    assert "/rp card inspect <card>" in result
    assert "/rp card export <card>" in result
    assert "/rp card use <card>" in result
    assert "/rp card greeting <card>" in result
    assert len(runtime.calls) == 0


def test_session_command_delegates_to_session_info():
    from hermes_tavern.runtime_sessions import session_command

    class SessionInfoRuntime:
        def __init__(self):
            self.calls = []

        def _session_info(self, event):
            self.calls.append(("session_info", event))
            return "session-info-result"

    runtime = SessionInfoRuntime()
    event = object()
    # Empty args defaults to "info"
    res1 = session_command(runtime, RPCommand("session", [], "/rp session"), event)
    assert res1 == "session-info-result"

    # Explicit "info"
    res2 = session_command(runtime, RPCommand("session", ["info"], "/rp session info"), event)
    assert res2 == "session-info-result"

    # Unknown subcommand returns usage
    res3 = session_command(runtime, RPCommand("session", ["unknown_sub"], "/rp session unknown_sub"), event)
    assert res3 == "Usage: /rp session info"

    assert len(runtime.calls) == 2

