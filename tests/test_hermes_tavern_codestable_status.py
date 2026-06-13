import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
ATTENTION_DOC = REPO_ROOT / "design" / "codestable" / "attention.md"
CURRENT_STATUS_PREFIX = "Current status (2026-06-13): All phases 1-211 accepted"
STALE_STATUS_PREFIX = "Current status (2026-06-13): All phases 1-210 accepted"
STALE_PHASE_MARKER = "1-210"
STALE_PHASE_MARKER_EN_DASH = "1–210"
REQUIRED_PHASE_LABELS = [
    "Phase 168 image settings JSON export",
    "Phase 169 project JSON export surface parity",
    "Phase 170 export command-surface regression",
    "Phase 171 root-design export parity",
    "Phase 172 attention status sync through Phase 171",
    "Phase 173 root-design section 17 import/export summary parity",
    "Phase 174 attention status sync through Phase 173",
    "Phase 175 attention status sync through Phase 174",
    "Phase 176 attention status sync through Phase 175",
    "Phase 177 attention status sync through Phase 176",
    "Phase 178 attention status sync through Phase 177",
    "Phase 179 attention status sync through Phase 178",
    "Phase 180 attention status sync through Phase 179",
    "Phase 181 attention status sync through Phase 180",
    "Phase 182 attention status sync through Phase 181",
    "Phase 183 attention status sync through Phase 182",
    "Phase 184 attention status sync through Phase 183",
    "Phase 185 attention status sync through Phase 184",
    "Phase 186 attention status sync through Phase 185",
    "Phase 187 attention status sync through Phase 186",
    "Phase 188 attention status sync through Phase 187",
    "Phase 189 attention status sync through Phase 188",
    "Phase 190 attention status sync through Phase 189",
    "Phase 191 attention status sync through Phase 190",
    "Phase 192 attention status sync through Phase 191",
    "Phase 193 attention status sync through Phase 192",
    "Phase 194 attention status sync through Phase 193",
    "Phase 195 attention status sync through Phase 194",
    "Phase 196 attention status sync through Phase 195",
    "Phase 197 attention status sync through Phase 196",
    "Phase 198 attention status sync through Phase 197",
    "Phase 199 attention status sync through Phase 198",
    "Phase 200 attention status sync through Phase 199",
    "Phase 201 attention status sync through Phase 200",
    "Phase 202 attention status sync through Phase 201",
    "Phase 203 attention status sync through Phase 202",
    "Phase 204 attention status sync through Phase 203",
    "Phase 205 attention status sync through Phase 204",
    "Phase 206 attention status sync through Phase 205",
    "Phase 207 attention status sync through Phase 206",
    "Phase 208 attention status sync through Phase 207",
    "Phase 209 attention status sync through Phase 208",
    "Phase 210 attention status sync through Phase 209",
    "Phase 211 attention status sync through Phase 210",
]
FINAL_STATUS_SUFFIX = "Phase 209 attention status sync through Phase 208, Phase 210 attention status sync through Phase 209, and Phase 211 attention status sync through Phase 210."


def test_attention_current_status_line_is_current():
    lines = ATTENTION_DOC.read_text(encoding="utf-8").splitlines()

    status_lines = [line for line in lines if re.match(r"^\s*-\s*Current status ", line)]

    assert len(status_lines) == 1
    status = status_lines[0]

    assert status.startswith(f"- {CURRENT_STATUS_PREFIX}")
    for label in REQUIRED_PHASE_LABELS:
        assert label in status

    assert STALE_STATUS_PREFIX not in status
    assert re.search(rf"(?<!\d){re.escape(STALE_PHASE_MARKER)}(?!\d)", status) is None
    assert re.search(rf"(?<!\d){re.escape(STALE_PHASE_MARKER_EN_DASH)}(?!\d)", status) is None
    assert status.endswith(FINAL_STATUS_SUFFIX)
    assert all(f"Phase {phase} " in status for phase in range(168, 212))
    assert re.search(r"(?<!\d)Phase 121-167(?!\d)", status) is not None

    test = Path(__file__).read_text(encoding="utf-8")
    assert CURRENT_STATUS_PREFIX in test
    assert STALE_STATUS_PREFIX in test
    assert STALE_PHASE_MARKER in test
    assert STALE_PHASE_MARKER_EN_DASH in test
    assert all(label in test for label in REQUIRED_PHASE_LABELS)
    assert "range(168, 212)" in test
    forbidden_glob = "." + "glob("
    forbidden_rglob = "." + "rglob("
    assert forbidden_glob not in test
    assert forbidden_rglob not in test
    forbidden_iterdir = "iter" + "dir("
    forbidden_os_walk = "os" + "." + "walk"
    assert forbidden_iterdir not in test
    assert forbidden_os_walk not in test
