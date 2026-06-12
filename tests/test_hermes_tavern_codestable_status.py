import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
ATTENTION_DOC = REPO_ROOT / "design" / "codestable" / "attention.md"


def test_attention_current_status_line_is_current():
    lines = ATTENTION_DOC.read_text(encoding="utf-8").splitlines()

    status_lines = [line for line in lines if re.match(r"^\s*-\s*Current status ", line)]

    assert len(status_lines) == 1
    status = status_lines[0]

    assert "Current status (2026-06-13): All phases 1-194 accepted" in status
    assert "Phase 168 image settings JSON export" in status
    assert "Phase 169 project JSON export surface parity" in status
    assert "Phase 170 export command-surface regression" in status
    assert "Phase 171 root-design export parity" in status
    assert "Phase 172 attention status sync through Phase 171" in status
    assert "Phase 173 root-design section 17 import/export summary parity" in status
    assert "Phase 174 attention status sync through Phase 173" in status
    assert "Phase 175 attention status sync through Phase 174" in status
    assert "Phase 176 attention status sync through Phase 175" in status
    assert "Phase 177 attention status sync through Phase 176" in status
    assert "Phase 178 attention status sync through Phase 177" in status
    assert "Phase 179 attention status sync through Phase 178" in status
    assert "Phase 180 attention status sync through Phase 179" in status
    assert "Phase 181 attention status sync through Phase 180" in status
    assert "Phase 182 attention status sync through Phase 181" in status
    assert "Phase 183 attention status sync through Phase 182" in status
    assert "Phase 184 attention status sync through Phase 183" in status
    assert "Phase 185 attention status sync through Phase 184" in status
    assert "Phase 186 attention status sync through Phase 185" in status
    assert "Phase 187 attention status sync through Phase 186" in status
    assert "Phase 188 attention status sync through Phase 187" in status
    assert "Phase 189 attention status sync through Phase 188" in status
    assert "Phase 190 attention status sync through Phase 189" in status
    assert "Phase 191 attention status sync through Phase 190" in status
    assert "Phase 192 attention status sync through Phase 191" in status
    assert "Phase 193 attention status sync through Phase 192" in status
    assert "Phase 194 attention status sync through Phase 193" in status

    assert "All phases 1-193 accepted" not in status
    assert re.search(r"(?<!\d)1-193(?!\d)", status) is None
    assert re.search(r"(?<!\d)1–193(?!\d)", status) is None
    assert status.endswith(
        "Phase 192 attention status sync through Phase 191, Phase 193 attention status sync through Phase 192, and Phase 194 attention status sync through Phase 193."
    )
    assert all(f"Phase {phase} " in status for phase in range(168, 195))
    assert re.search(r"(?<!\d)Phase 121-167(?!\d)", status) is not None

    test = Path(__file__).read_text(encoding="utf-8")
    assert "Current status (2026-06-13): All phases 1-194 accepted" in test
    assert "Phase 168 image settings JSON export" in test
    assert "Phase 169 project JSON export surface parity" in test
    assert "Phase 170 export command-surface regression" in test
    assert "Phase 171 root-design export parity" in test
    assert "Phase 172 attention status sync through Phase 171" in test
    assert "Phase 173 root-design section 17 import/export summary parity" in test
    assert "Phase 174 attention status sync through Phase 173" in test
    assert "Phase 175 attention status sync through Phase 174" in test
    assert "Phase 176 attention status sync through Phase 175" in test
    assert "Phase 177 attention status sync through Phase 176" in test
    assert "Phase 178 attention status sync through Phase 177" in test
    assert "Phase 179 attention status sync through Phase 178" in test
    assert "Phase 180 attention status sync through Phase 179" in test
    assert "Phase 181 attention status sync through Phase 180" in test
    assert "Phase 182 attention status sync through Phase 181" in test
    assert "Phase 183 attention status sync through Phase 182" in test
    assert "Phase 184 attention status sync through Phase 183" in test
    assert "Phase 185 attention status sync through Phase 184" in test
    assert "Phase 186 attention status sync through Phase 185" in test
    assert "Phase 187 attention status sync through Phase 186" in test
    assert "Phase 188 attention status sync through Phase 187" in test
    assert "Phase 189 attention status sync through Phase 188" in test
    assert "Phase 190 attention status sync through Phase 189" in test
    assert "Phase 191 attention status sync through Phase 190" in test
    assert "Phase 192 attention status sync through Phase 191" in test
    assert "Phase 193 attention status sync through Phase 192" in test
    assert "Phase 194 attention status sync through Phase 193" in test
    assert "All phases 1-193 accepted" in test
    assert "1-193" in test
    assert "1–193" in test
    forbidden_glob = "." + "glob("
    forbidden_rglob = "." + "rglob("
    assert forbidden_glob not in test
    assert forbidden_rglob not in test
    forbidden_iterdir = "iter" + "dir("
    forbidden_os_walk = "os" + "." + "walk"
    assert forbidden_iterdir not in test
    assert forbidden_os_walk not in test
