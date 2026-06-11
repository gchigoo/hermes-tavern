from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
DESIGN_DOC = REPO_ROOT / "design" / "HERMES_TAVERN_DESIGN.md"

EXPECTED_EXPORT_LITERALS = (
    "/rp relationship export <relationship-id>",
    "/rp location export <location-id>",
    "/rp organization export <organization-id>",
    "/rp binding export <binding-id>",
    "/rp scene export <scene-id>",
    "/rp scene beat export <beat-id>",
    "/rp project revision export <note-id>",
    "/rp canon export <canon-id>",
    "/rp timeline export <timeline-id>",
)


def _command_surfaces() -> list[str]:
    text = DESIGN_DOC.read_text(encoding="utf-8")

    in_text_block = False
    blocks: list[str] = []
    current: list[str] = []

    for line in text.splitlines():
        stripped = line.strip()
        if stripped == "```text":
            in_text_block = True
            current = []
            continue
        if stripped.startswith("```") and in_text_block:
            blocks.append("\n".join(current))
            in_text_block = False
            continue
        if in_text_block:
            current.append(line)

    return [
        block
        for block in blocks
        if any(line.lstrip().startswith("/rp ") for line in block.splitlines())
    ]


def _line_has_literal(block: str, literal: str) -> bool:
    for line in block.splitlines():
        text = line.strip()
        if text == literal or text.startswith(f"{literal} "):
            return True
    return False


@pytest.mark.parametrize("literal", EXPECTED_EXPORT_LITERALS)
def test_design_docs_include_missing_export_command_literals(literal: str) -> None:
    surfaces = _command_surfaces()

    assert any(_line_has_literal(surface, literal) for surface in surfaces), (
        f"Missing command literal in writing command surface: {literal}"
    )
