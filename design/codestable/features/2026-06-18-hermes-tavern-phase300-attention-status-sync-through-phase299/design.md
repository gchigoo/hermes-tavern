---
doc_type: feature-design
status: approved
implementation_ready: true
feature: "2026-06-18-hermes-tavern-phase300-attention-status-sync-through-phase299"
date: "2026-06-18"
created: "2026-06-18"
updated: "2026-06-18"
owner: company-boost
summary: >
  Sync the mandatory CodeStable attention current-status line and focused static
  regression through accepted Phase 299 only, without changing runtime behavior,
  plugin/provider/gateway internals, root design, architecture, roadmap,
  requirements, compound docs, credentials, service lifecycle, or build assets.
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests]
---

# Phase 300: CodeStable Attention Status Sync Through Phase 299

## Selected Phase and Gate

Selected phase slug: `2026-06-18-hermes-tavern-phase300-attention-status-sync-through-phase299`.

Phase 299 is accepted: `design/codestable/features/2026-06-18-hermes-tavern-phase299-attention-status-sync-through-phase298/acceptance.md` has `status: accepted`. Therefore Phase 300 is the next bounded attention/status-sync slice.

## Current State and Evidence

- `design/codestable/attention.md` currently reports `Current status (2026-06-18): All phases 1-298 accepted`.
- `tests/test_hermes_tavern_codestable_status.py` currently enforces Phase 298 as current, Phase 297 as stale, `range(168, 299)`, and explicit labels through Phase 298.
- `design/codestable/features/2026-06-18-hermes-tavern-phase299-attention-status-sync-through-phase298/` contains accepted `design.md`, `checklist.yaml`, and `acceptance.md`.
- This Phase 300 feature artifact is for controller materialization only; the read-only architect must not edit files.

## Goal

Advance the recurring status-sync family by exactly one accepted phase: sync `design/codestable/attention.md` and the focused static regression through accepted Phase 299 only.

## Scope

Allowed files exactly:

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`
- `design/codestable/features/2026-06-18-hermes-tavern-phase300-attention-status-sync-through-phase299/design.md`
- `design/codestable/features/2026-06-18-hermes-tavern-phase300-attention-status-sync-through-phase299/checklist.yaml`

## Non-Goals

- Do not change runtime, source, plugin, provider, gateway, CLI, root design, README, architecture, roadmap, requirements, compound docs, build outputs, fixtures, assets, credentials, provider configuration, model routing, or service lifecycle behavior.
- Do not modify `run_agent.py`, `cli.py`, or `gateway/run.py`.
- Do not change Hermes-native plugin architecture.
- Do not change SillyTavern asset compatibility.
- Do not create minors/CSAM functionality, bypass provider safety systems, or change adult-fiction/RP boundaries.
- Do not stage, commit, push, or update `~/.hermes/project-progress/state.json`.
- Do not create or update a Phase 300 acceptance artifact in this executor slice unless a parent controller separately authorizes it.

## Structure Health and Micro-Refactor

No micro-refactor is part of this slice. The change is a narrow status literal and focused regression update. `attention.md` is intentionally the central startup status record, and the focused test is intentionally the static guard for that record. No source directories, runtime modules, plugin files, provider files, gateway files, or assets should be reorganized.

## Exact Status Line Contract

- Prefix advances from `Current status (2026-06-18): All phases 1-298 accepted` to `Current status (2026-06-18): All phases 1-299 accepted`.
- Add exactly one new short label to the same status line: `Phase 299 attention status sync through Phase 298`.
- Preserve `Phase 121-167`.
- Preserve every existing explicit label `Phase 168` through `Phase 298` exactly.
- Do not add any `Phase 300` attention/status label to `attention.md`; this phase syncs only through accepted Phase 299.
- Final suffix must be exactly: `Phase 297 attention status sync through Phase 296, Phase 298 attention status sync through Phase 297, and Phase 299 attention status sync through Phase 298.`

## Full Required Short-Label List

After implementation, the status line and focused regression must contain this exact Phase 168+ label set, with `Phase 121-167` also preserved:

- `Phase 168 image settings JSON export`
- `Phase 169 project JSON export surface parity`
- `Phase 170 export command-surface regression`
- `Phase 171 root-design export parity`
- `Phase 172 attention status sync through Phase 171`
- `Phase 173 root-design section 17 import/export summary parity`
- `Phase 174 attention status sync through Phase 173`
- `Phase 175 attention status sync through Phase 174`
- `Phase 176 attention status sync through Phase 175`
- `Phase 177 attention status sync through Phase 176`
- `Phase 178 attention status sync through Phase 177`
- `Phase 179 attention status sync through Phase 178`
- `Phase 180 attention status sync through Phase 179`
- `Phase 181 attention status sync through Phase 180`
- `Phase 182 attention status sync through Phase 181`
- `Phase 183 attention status sync through Phase 182`
- `Phase 184 attention status sync through Phase 183`
- `Phase 185 attention status sync through Phase 184`
- `Phase 186 attention status sync through Phase 185`
- `Phase 187 attention status sync through Phase 186`
- `Phase 188 attention status sync through Phase 187`
- `Phase 189 attention status sync through Phase 188`
- `Phase 190 attention status sync through Phase 189`
- `Phase 191 attention status sync through Phase 190`
- `Phase 192 attention status sync through Phase 191`
- `Phase 193 attention status sync through Phase 192`
- `Phase 194 attention status sync through Phase 193`
- `Phase 195 attention status sync through Phase 194`
- `Phase 196 attention status sync through Phase 195`
- `Phase 197 attention status sync through Phase 196`
- `Phase 198 attention status sync through Phase 197`
- `Phase 199 attention status sync through Phase 198`
- `Phase 200 attention status sync through Phase 199`
- `Phase 201 attention status sync through Phase 200`
- `Phase 202 attention status sync through Phase 201`
- `Phase 203 attention status sync through Phase 202`
- `Phase 204 attention status sync through Phase 203`
- `Phase 205 attention status sync through Phase 204`
- `Phase 206 attention status sync through Phase 205`
- `Phase 207 attention status sync through Phase 206`
- `Phase 208 attention status sync through Phase 207`
- `Phase 209 attention status sync through Phase 208`
- `Phase 210 attention status sync through Phase 209`
- `Phase 211 attention status sync through Phase 210`
- `Phase 212 attention status sync through Phase 211`
- `Phase 213 attention status sync through Phase 212`
- `Phase 214 attention status sync through Phase 213`
- `Phase 215 attention status sync through Phase 214`
- `Phase 216 attention status sync through Phase 215`
- `Phase 217 attention status sync through Phase 216`
- `Phase 218 attention status sync through Phase 217`
- `Phase 219 attention status sync through Phase 218`
- `Phase 220 attention status sync through Phase 219`
- `Phase 221 attention status sync through Phase 220`
- `Phase 222 attention status sync through Phase 221`
- `Phase 223 attention status sync through Phase 222`
- `Phase 224 attention status sync through Phase 223`
- `Phase 225 attention status sync through Phase 224`
- `Phase 226 attention status sync through Phase 225`
- `Phase 227 attention status sync through Phase 226`
- `Phase 228 attention status sync through Phase 227`
- `Phase 229 attention status sync through Phase 228`
- `Phase 230 attention status sync through Phase 229`
- `Phase 231 attention status sync through Phase 230`
- `Phase 232 attention status sync through Phase 231`
- `Phase 233 attention status sync through Phase 232`
- `Phase 234 attention status sync through Phase 233`
- `Phase 235 attention status sync through Phase 234`
- `Phase 236 attention status sync through Phase 235`
- `Phase 237 attention status sync through Phase 236`
- `Phase 238 attention status sync through Phase 237`
- `Phase 239 attention status sync through Phase 238`
- `Phase 240 attention status sync through Phase 239`
- `Phase 241 attention status sync through Phase 240`
- `Phase 242 attention status sync through Phase 241`
- `Phase 243 attention status sync through Phase 242`
- `Phase 244 attention status sync through Phase 243`
- `Phase 245 attention status sync through Phase 244`
- `Phase 246 attention status sync through Phase 245`
- `Phase 247 attention status sync through Phase 246`
- `Phase 248 attention status sync through Phase 247`
- `Phase 249 attention status sync through Phase 248`
- `Phase 250 attention status sync through Phase 249`
- `Phase 251 attention status sync through Phase 250`
- `Phase 252 attention status sync through Phase 251`
- `Phase 253 attention status sync through Phase 252`
- `Phase 254 attention status sync through Phase 253`
- `Phase 255 attention status sync through Phase 254`
- `Phase 256 attention status sync through Phase 255`
- `Phase 257 attention status sync through Phase 256`
- `Phase 258 attention status sync through Phase 257`
- `Phase 259 attention status sync through Phase 258`
- `Phase 260 attention status sync through Phase 259`
- `Phase 261 attention status sync through Phase 260`
- `Phase 262 attention status sync through Phase 261`
- `Phase 263 attention status sync through Phase 262`
- `Phase 264 attention status sync through Phase 263`
- `Phase 265 attention status sync through Phase 264`
- `Phase 266 attention status sync through Phase 265`
- `Phase 267 attention status sync through Phase 266`
- `Phase 268 attention status sync through Phase 267`
- `Phase 269 attention status sync through Phase 268`
- `Phase 270 attention status sync through Phase 269`
- `Phase 271 attention status sync through Phase 270`
- `Phase 272 attention status sync through Phase 271`
- `Phase 273 attention status sync through Phase 272`
- `Phase 274 attention status sync through Phase 273`
- `Phase 275 attention status sync through Phase 274`
- `Phase 276 attention status sync through Phase 275`
- `Phase 277 attention status sync through Phase 276`
- `Phase 278 attention status sync through Phase 277`
- `Phase 279 attention status sync through Phase 278`
- `Phase 280 attention status sync through Phase 279`
- `Phase 281 attention status sync through Phase 280`
- `Phase 282 attention status sync through Phase 281`
- `Phase 283 attention status sync through Phase 282`
- `Phase 284 attention status sync through Phase 283`
- `Phase 285 attention status sync through Phase 284`
- `Phase 286 attention status sync through Phase 285`
- `Phase 287 attention status sync through Phase 286`
- `Phase 288 attention status sync through Phase 287`
- `Phase 289 attention status sync through Phase 288`
- `Phase 290 attention status sync through Phase 289`
- `Phase 291 attention status sync through Phase 290`
- `Phase 292 attention status sync through Phase 291`
- `Phase 293 attention status sync through Phase 292`
- `Phase 294 attention status sync through Phase 293`
- `Phase 295 attention status sync through Phase 294`
- `Phase 296 attention status sync through Phase 295`
- `Phase 297 attention status sync through Phase 296`
- `Phase 298 attention status sync through Phase 297`
- `Phase 299 attention status sync through Phase 298`

## Focused Status Regression Contract

Update `tests/test_hermes_tavern_codestable_status.py` so it enforces:

- `CURRENT_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-299 accepted"`.
- `STALE_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-298 accepted"`.
- `STALE_PHASE_MARKER = "1-298"` and `STALE_PHASE_MARKER_EN_DASH = "1–298"`.
- `REQUIRED_PHASE_LABELS` preserves every prior explicit short label through Phase 298 and includes `Phase 299 attention status sync through Phase 298`.
- `FINAL_STATUS_SUFFIX` is exactly `Phase 297 attention status sync through Phase 296, Phase 298 attention status sync through Phase 297, and Phase 299 attention status sync through Phase 298.`
- The runtime phase range assertion is `range(168, 300)`.
- The source self-check contains `aggregate_range = "range(168, 300)"`.
- Stale aggregate negative guards must reject split-string constructed `range(168, 299)` and retain older stale ranges.
- Avoid direct stale aggregate literals in the test source where self-source guards would count assertion literals incorrectly.
- The single `CURRENT_STATUS_PREFIX` assignment check uses anchored regex: `re.findall(r"^CURRENT_STATUS_PREFIX\s*=", test, re.M) == ["CURRENT_STATUS_PREFIX ="]`.
- Discovery-token guards keep `.glob(`, `.rglob(`, `iterdir(`, and `os.walk` split inside strings.

## Implementation Steps

S1: Sync attention status and focused static regression through Phase 299.

- Update only the status bullet in `design/codestable/attention.md`.
- Update only the focused static status test in `tests/test_hermes_tavern_codestable_status.py`.
- Materialize this Phase 300 `design.md` and `checklist.yaml`.
- Keep checklist root status non-final for parent verification.

S2: Worker and parent-controller verification.

- Run the verification commands below.
- Confirm the dirty path set is exactly the four allowed files.
- Leave final checklist/root workflow status pending or in progress for parent verification.
- Do not stage, commit, push, or update `~/.hermes/project-progress/state.json`.

## Verification

Required verification commands:

- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --dir design/codestable/features/2026-06-18-hermes-tavern-phase300-attention-status-sync-through-phase299 --require doc_type --require status --require feature`
- `PYTHONDONTWRITEBYTECODE=1 python -m py_compile tests/test_hermes_tavern_codestable_status.py`
- `PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o 'addopts=' -p no:cacheprovider`
- Static status/protected-path guard.
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o 'addopts='` if feasible, without `PYTEST_DISABLE_PLUGIN_AUTOLOAD`.
- `git diff --check`

Static status/protected-path guard must verify:

- Exactly one current-status bullet exists in `attention.md`.
- The status prefix, stale prefix, stale markers, full required label set, final suffix, runtime range, and source self-check aggregate range match this design.
- The test source uses anchored `CURRENT_STATUS_PREFIX` assignment counting.
- Stale aggregate guards are split in the test source and include `range(168, 299)` plus older stale ranges.
- Discovery-token guards stay split for `.glob(`, `.rglob(`, `iterdir(`, and `os.walk`.
- No file outside the four allowed files is modified or untracked for this slice.
- No staged files exist.

## Executor Prompt

Implement only Phase 300 status sync. Edit only `design/codestable/attention.md`, `tests/test_hermes_tavern_codestable_status.py`, `design/codestable/features/2026-06-18-hermes-tavern-phase300-attention-status-sync-through-phase299/design.md`, and `design/codestable/features/2026-06-18-hermes-tavern-phase300-attention-status-sync-through-phase299/checklist.yaml`. Advance current status to `All phases 1-299 accepted`, preserve `Phase 121-167` and all existing explicit labels through Phase 298, append only `Phase 299 attention status sync through Phase 298`, and do not add any Phase 300 attention/status label to `attention.md`. Update the focused test constants, required labels, suffix, stale markers, runtime range, source self-check aggregate range, stale aggregate split guards, anchored assignment-count regex, and discovery-token guards exactly as specified. Keep final checklist/root status pending or in progress for parent verification. Do not stage, commit, push, update `~/.hermes/project-progress/state.json`, touch runtime/source/plugin/provider/gateway/CLI/root-design/README/architecture/roadmap/requirements/compound/build/credential/service-lifecycle files, or change provider safety behavior.

## Architect Review Criteria

- Diff touches only the four allowed files.
- `attention.md` has exactly one current-status bullet.
- Prefix is exactly `Current status (2026-06-18): All phases 1-299 accepted`.
- Stale `All phases 1-298 accepted`, `1-298`, and `1–298` terminal markers are rejected.
- `Phase 121-167` remains present.
- Explicit `Phase 168` through `Phase 298` labels are preserved exactly.
- Only new attention label is `Phase 299 attention status sync through Phase 298`.
- No `Phase 300` attention/status label appears in `attention.md`.
- Final suffix is exactly the Phase 297/298/299 suffix.
- Focused regression uses runtime `range(168, 300)`.
- Source self-check aggregate range is exactly `range(168, 300)`.
- Stale aggregate guards are split and include stale `range(168, 299)` plus older stale ranges.
- Protected-path scope excludes runtime, source, plugin, provider, gateway, CLI, root design, README, architecture, roadmap, requirements, compound docs, build outputs, fixtures/assets, credentials, service lifecycle files, and `~/.hermes/project-progress/state.json`.
- Hermes-native plugin architecture and SillyTavern asset compatibility remain untouched.
- Adult-fiction/RP compatibility remains unchanged, with no minors/CSAM work and no provider-safety bypass.
- Checklist/root workflow status remains non-final for parent verification.
- No staging, commit, push, or progress-state update occurred.
- YAML validation, py_compile, focused status pytest, static status/protected-path guard, full pytest if feasible, and `git diff --check` are accounted for.
