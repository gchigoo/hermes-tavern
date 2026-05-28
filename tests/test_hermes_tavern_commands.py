import pytest

from plugins.hermes_tavern.commands import RPCommand, _build_help_text, parse_rp_command


@pytest.mark.parametrize("text", ["hello", "/rpx help", " /rpx help "])
def test_parse_rp_command_ignores_non_rp_text(text):
    assert parse_rp_command(text) is None


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("/rp", RPCommand(name="help", args=[], raw="/rp")),
        ("/rp help", RPCommand(name="help", args=[], raw="/rp help")),
        ("/rp status", RPCommand(name="status", args=[], raw="/rp status")),
        ("/rp end", RPCommand(name="end", args=[], raw="/rp end")),
        (
            "/rp start Alice",
            RPCommand(name="start", args=["Alice"], raw="/rp start Alice"),
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


def test_help_lists_image_configuration_commands():
    help_text = _build_help_text()

    assert "/rp image settings [set <key> <value>|clear <key|all>]" in help_text
    assert "/rp image style [list|save <name>|use <name>|inspect <name>|delete <name>]" in help_text
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
    assert "/rp memory summary [set <text>|clear|summarize [limit] [live]]" in help_text
    assert "/rp persona new <name> <text>" in help_text
    assert "/rp persona temp <text>" in help_text
