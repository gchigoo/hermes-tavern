import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
ATTENTION_DOC = REPO_ROOT / "design" / "codestable" / "attention.md"


def test_attention_current_status_line_is_current():
    lines = ATTENTION_DOC.read_text(encoding="utf-8").splitlines()

    status_lines = [line for line in lines if re.match(r"^\s*-\s*Current status ", line)]

    assert len(status_lines) == 1
    status = status_lines[0]

    assert "Current status (2026-06-12): All phases 1-173 accepted" in status
    assert "Phase 168 image settings JSON export" in status
    assert "Phase 169 project JSON export surface parity" in status
    assert "Phase 170 export command-surface regression" in status
    assert "Phase 171 root-design export parity" in status
    assert "Phase 172 attention status sync through Phase 171" in status
    assert "Phase 173 root-design section 17 import/export summary parity" in status

    assert "2026-06-11" not in status

    assert re.search(r"(?<!\d)1-171(?!\d)", status) is None
    assert re.search(r"(?<!\d)1–171(?!\d)", status) is None
    assert re.search(r"(?<!\d)Phase 121-167(?!\d)", status) is not None
