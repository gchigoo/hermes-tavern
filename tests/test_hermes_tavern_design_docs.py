from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
DESIGN_DOC = REPO_ROOT / "design" / "HERMES_TAVERN_DESIGN.md"
IMPLEMENTATION_PLAN = REPO_ROOT / "design" / "plans" / "hermes-tavern-implementation-v0.1.md"
ATTENTION_DOC = REPO_ROOT / "design" / "codestable" / "attention.md"
CREDENTIAL_REUSE_DECISION = (
    REPO_ROOT
    / "design"
    / "codestable"
    / "compound"
    / "2026-05-18-decision-hermes-tavern-credential-reuse.md"
)
OBSOLETE_IMPLEMENTATION_PLAN = (
    REPO_ROOT / ".hermes" / "plans" / "hermes-tavern-implementation-v0.1.md"
)
CANONICAL_IMPLEMENTATION_PLAN_PATH = "design/plans/hermes-tavern-implementation-v0.1.md"

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


def _section_17_text() -> str:
    lines = DESIGN_DOC.read_text(encoding="utf-8").splitlines()
    start = None
    end = None
    for idx, line in enumerate(lines):
        if start is None and line.strip() == "## 17. Import / Export":
            start = idx
            continue
        if start is not None and idx > start and line.startswith("## 18."):
            end = idx
            break
    if start is None:
        raise AssertionError("Section 17 heading not found in design document")
    if end is None:
        end = len(lines)
    return "\n".join(lines[start:end])


def _line_has_literal(block: str, literal: str) -> bool:
    for line in block.splitlines():
        text = line.strip()
        if text == literal or text.startswith(f"{literal} "):
            return True
    return False


def test_design_docs_section17_import_export_parity() -> None:
    section = _section_17_text()

    assert "current Phase 121-151" not in section
    assert "current Phase 121–151" not in section

    for literal in (
        "/rp session export <id>",
        "/rp project export json [project-id]",
        "/rp image settings export",
        "/rp character state export <character-state-id>",
        "/rp project revision export <note-id>",
    ):
        assert literal in section

    for stale in (
        "/rp export chat",
        "/rp backup",
        "/rp import <attachment|url|path>",
    ):
        assert stale not in section


@pytest.mark.parametrize("literal", EXPECTED_EXPORT_LITERALS)
def test_design_docs_include_missing_export_command_literals(literal: str) -> None:
    surfaces = _command_surfaces()

    assert any(_line_has_literal(surface, literal) for surface in surfaces), (
        f"Missing command literal in writing command surface: {literal}"
    )


def test_design_docs_use_the_canonical_implementation_plan_path() -> None:
    assert DESIGN_DOC.is_file()
    assert IMPLEMENTATION_PLAN.is_file()
    assert CREDENTIAL_REUSE_DECISION.is_file()
    assert not OBSOLETE_IMPLEMENTATION_PLAN.exists()

    obsolete_path = ".hermes/plans/hermes-tavern-implementation-v0.1.md"
    for authority_document in (
        DESIGN_DOC,
        IMPLEMENTATION_PLAN,
        ATTENTION_DOC,
        CREDENTIAL_REUSE_DECISION,
    ):
        text = authority_document.read_text(encoding="utf-8")
        assert CANONICAL_IMPLEMENTATION_PLAN_PATH in text
        assert obsolete_path not in text

    plan_text = IMPLEMENTATION_PLAN.read_text(encoding="utf-8")
    assert "- `design/HERMES_TAVERN_DESIGN.md`" in plan_text
