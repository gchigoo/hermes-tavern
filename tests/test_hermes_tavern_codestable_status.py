import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
ATTENTION_DOC = REPO_ROOT / "design" / "codestable" / "attention.md"
CURRENT_STATUS_PREFIX = "Current status (2026-06-17): All phases 1-286 accepted"
STALE_STATUS_PREFIX = "Current status (2026-06-17): All phases 1-285 accepted"
STALE_PHASE_MARKER = "1-285"
STALE_PHASE_MARKER_EN_DASH = "1–285"
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
    "Phase 212 attention status sync through Phase 211",
    "Phase 213 attention status sync through Phase 212",
    "Phase 214 attention status sync through Phase 213",
    "Phase 215 attention status sync through Phase 214",
    "Phase 216 attention status sync through Phase 215",
    "Phase 217 attention status sync through Phase 216",
    "Phase 218 attention status sync through Phase 217",
    "Phase 219 attention status sync through Phase 218",
    "Phase 220 attention status sync through Phase 219",
    "Phase 221 attention status sync through Phase 220",
    "Phase 222 attention status sync through Phase 221",
    "Phase 223 attention status sync through Phase 222",
    "Phase 224 attention status sync through Phase 223",
    "Phase 225 attention status sync through Phase 224",
    "Phase 226 attention status sync through Phase 225",
    "Phase 227 attention status sync through Phase 226",
    "Phase 228 attention status sync through Phase 227",
    "Phase 229 attention status sync through Phase 228",
    "Phase 230 attention status sync through Phase 229",
    "Phase 231 attention status sync through Phase 230",
    "Phase 232 attention status sync through Phase 231",
    "Phase 233 attention status sync through Phase 232",
    "Phase 234 attention status sync through Phase 233",
    "Phase 235 attention status sync through Phase 234",
    "Phase 236 attention status sync through Phase 235",
    "Phase 237 attention status sync through Phase 236",
    "Phase 238 attention status sync through Phase 237",
    "Phase 239 attention status sync through Phase 238",
    "Phase 240 attention status sync through Phase 239",
    "Phase 241 attention status sync through Phase 240",
    "Phase 242 attention status sync through Phase 241",
    "Phase 243 attention status sync through Phase 242",
    "Phase 244 attention status sync through Phase 243",
    "Phase 245 attention status sync through Phase 244",
    "Phase 246 attention status sync through Phase 245",
    "Phase 247 attention status sync through Phase 246",
    "Phase 248 attention status sync through Phase 247",
    "Phase 249 attention status sync through Phase 248",
    "Phase 250 attention status sync through Phase 249",
    "Phase 251 attention status sync through Phase 250",
    "Phase 252 attention status sync through Phase 251",
    "Phase 253 attention status sync through Phase 252",
    "Phase 254 attention status sync through Phase 253",
    "Phase 255 attention status sync through Phase 254",
    "Phase 256 attention status sync through Phase 255",
    "Phase 257 attention status sync through Phase 256",
    "Phase 258 attention status sync through Phase 257",
    "Phase 259 attention status sync through Phase 258",
    "Phase 260 attention status sync through Phase 259",
    "Phase 261 attention status sync through Phase 260",
    "Phase 262 attention status sync through Phase 261",
    "Phase 263 attention status sync through Phase 262",
    "Phase 264 attention status sync through Phase 263",
    "Phase 265 attention status sync through Phase 264",
    "Phase 266 attention status sync through Phase 265",
    "Phase 267 attention status sync through Phase 266",
    "Phase 268 attention status sync through Phase 267",
    "Phase 269 attention status sync through Phase 268",
    "Phase 270 attention status sync through Phase 269",
    "Phase 271 attention status sync through Phase 270",
    "Phase 272 attention status sync through Phase 271",
    "Phase 273 attention status sync through Phase 272",
    "Phase 274 attention status sync through Phase 273",
    "Phase 275 attention status sync through Phase 274",
    "Phase 276 attention status sync through Phase 275",
    "Phase 277 attention status sync through Phase 276",
    "Phase 278 attention status sync through Phase 277",
    "Phase 279 attention status sync through Phase 278",
    "Phase 280 attention status sync through Phase 279",
    "Phase 281 attention status sync through Phase 280",
    "Phase 282 attention status sync through Phase 281",
    "Phase 283 attention status sync through Phase 282",
    "Phase 284 attention status sync through Phase 283",
    "Phase 285 attention status sync through Phase 284",
    "Phase 286 attention status sync through Phase 285",
]
FINAL_STATUS_SUFFIX = "Phase 284 attention status sync through Phase 283, Phase 285 attention status sync through Phase 284, and Phase 286 attention status sync through Phase 285."


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
    phase_range = range(168, 287)
    assert all(f"Phase {phase} " in status for phase in phase_range)
    assert re.search(r"(?<!\d)Phase 121-167(?!\d)", status) is not None
    test = Path(__file__).read_text(encoding="utf-8")
    assert re.findall(r"^CURRENT_STATUS_PREFIX\s*=", test, re.M) == ["CURRENT_STATUS_PREFIX ="]
    assert CURRENT_STATUS_PREFIX in test
    assert all(label in test for label in REQUIRED_PHASE_LABELS)
    stale_aggregate_range_286 = "".join(["range(168, ", "28", "6", ")"])
    stale_aggregate_range_285 = "".join(["range(168, ", "28", "5", ")"])
    assert stale_aggregate_range_285 not in test
    assert stale_aggregate_range_286 not in test
    stale_aggregate_range_284 = "".join(["range(168, ", "28", "4", ")"])
    assert stale_aggregate_range_284 not in test
    stale_aggregate_range_283 = "".join(["range(168, ", "28", "3", ")"])
    assert stale_aggregate_range_283 not in test
    stale_aggregate_range_282 = "".join(["range(168, ", "28", "2", ")"])
    assert stale_aggregate_range_282 not in test
    stale_aggregate_range_281 = "".join(["range(168, ", "28", "1", ")"])
    assert stale_aggregate_range_281 not in test
    aggregate_range = "range(168, 287)"
    assert aggregate_range in test
    forbidden_glob = "." + "gl" + "ob("
    forbidden_rglob = "." + "rg" + "lob("
    assert forbidden_glob not in test
    assert forbidden_rglob not in test
    forbidden_iterdir = "iter" + "dir("
    forbidden_os_walk = "os" + "." + "walk"
    assert forbidden_iterdir not in test
    assert forbidden_os_walk not in test
