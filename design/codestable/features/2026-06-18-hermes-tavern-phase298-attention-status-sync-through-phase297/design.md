---
doc_type: feature-design
status: approved
implementation_ready: true
feature: "2026-06-18-hermes-tavern-phase298-attention-status-sync-through-phase297"
date: "2026-06-18"
created: "2026-06-18"
updated: "2026-06-18"
owner: codestable-cron
summary: >
  Sync the mandatory CodeStable attention current-status line and focused static
  regression through accepted Phase 297 only, without changing runtime behavior,
  plugin/provider/gateway internals, root design, architecture, roadmap,
  requirements, compound docs, credentials, or build assets.
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests]
---

# Phase 298: CodeStable Attention Status Sync Through Phase 297

## Current State and Evidence

Read-only architect verification for `/tmp/hermes-tavern-architect-design-companyboost-1781748054.jsonl` confirmed the next bounded slice is Phase 298:

- `design/codestable/attention.md` currently reports `Current status (2026-06-18): All phases 1-296 accepted`.
- `tests/test_hermes_tavern_codestable_status.py` currently enforces the same Phase 296 prefix and `range(168, 297)` aggregate range.
- `design/codestable/features/2026-06-18-hermes-tavern-phase297-attention-status-sync-through-phase296/` has `design.md`, `checklist.yaml`, and `acceptance.md` with accepted status for the sync-through-296 slice.
- No Phase 298 feature artifact directory exists before this controller materialization.

## Goal

Advance the recurring status-sync family by exactly one accepted phase: sync `design/codestable/attention.md` and the focused static regression through accepted Phase 297 only, and keep the new Phase 298 artifacts non-final until parent-controller verification.

## Non-Goals

- Do not change runtime, source, plugin, provider, gateway, CLI, root design, README, architecture, roadmap, requirements, compound docs, build outputs, fixtures, assets, schemas, credentials, model/provider routing, or service lifecycle behavior.
- Do not modify `run_agent.py`, `cli.py`, or `gateway/run.py`.
- Do not create minors/CSAM functionality, bypass provider safety systems, or change adult-fiction/RP boundaries.
- Do not commit, push, stage files, or update `.hermes/project-progress/state.json`.

## Exact S1 Contract

- `design/codestable/attention.md` current status must advance from `Current status (2026-06-18): All phases 1-296 accepted` to `Current status (2026-06-18): All phases 1-297 accepted`.
- Add exactly one new short label to the same status line: `Phase 297 attention status sync through Phase 296`.
- Preserve `Phase 121-167`.
- Preserve all explicit `Phase 168` through `Phase 296` labels exactly.
- Do not add any `Phase 298` label to `attention.md`.
- Phase 298 syncs only through accepted Phase 297.
- Do not change runtime/product/source/plugin/provider/gateway behavior.

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

The final status suffix must be exactly:

```text
Phase 295 attention status sync through Phase 294, Phase 296 attention status sync through Phase 295, and Phase 297 attention status sync through Phase 296.
```

## Focused Status Regression Contract

Update `tests/test_hermes_tavern_codestable_status.py` so it enforces:

- `CURRENT_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-297 accepted"`.
- `STALE_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-296 accepted"`.
- `STALE_PHASE_MARKER = "1-296"` and `STALE_PHASE_MARKER_EN_DASH = "1–296"`.
- `REQUIRED_PHASE_LABELS` preserves every prior explicit short label through Phase 296 and includes `Phase 297 attention status sync through Phase 296`.
- `FINAL_STATUS_SUFFIX` is exactly `Phase 295 attention status sync through Phase 294, Phase 296 attention status sync through Phase 295, and Phase 297 attention status sync through Phase 296.`
- The runtime phase range assertion is `range(168, 298)`.
- The source self-check contains `aggregate_range = "range(168, 298)"`.
- Stale aggregate negative guards include split-string construction for stale `range(168, 297)` and retain older stale ranges.
- The single `CURRENT_STATUS_PREFIX` assignment check uses anchored regex: `re.findall(r"^CURRENT_STATUS_PREFIX\\s*=", test, re.M) == ["CURRENT_STATUS_PREFIX ="]`.
- Discovery-token guards keep `.glob(`, `.rglob(`, `iterdir(`, and `os.walk` split inside strings.

## Scope

Allowed files only:

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`
- `design/codestable/features/2026-06-18-hermes-tavern-phase298-attention-status-sync-through-phase297/design.md`
- `design/codestable/features/2026-06-18-hermes-tavern-phase298-attention-status-sync-through-phase297/checklist.yaml`
- `design/codestable/features/2026-06-18-hermes-tavern-phase298-attention-status-sync-through-phase297/acceptance.md`

## Prohibited Files/Actions

No changes to runtime, source, provider, plugin, gateway, root design, README, architecture, roadmap, requirements, compound docs, build outputs, assets, schemas, credential files, service lifecycle, provider configuration, prior phase artifacts, or `.hermes/project-progress/state.json`. Do not commit, push, stage, or run destructive git commands.

## Validators, Tests, and Guards

Worker-controller verification must run after implementation:

- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --dir design/codestable/features/2026-06-18-hermes-tavern-phase298-attention-status-sync-through-phase297 --require doc_type --require status --require feature`
- `PYTHONDONTWRITEBYTECODE=1 python -m py_compile tests/test_hermes_tavern_codestable_status.py`
- `PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o 'addopts=' -p no:cacheprovider`
- Static status guard using anchored regex for `CURRENT_STATUS_PREFIX` assignment count and exact prefix/suffix/range/label/stale marker/discovery-token checks.
- Protected-path diff guard over the five allowed files, including untracked Phase 298 files.
- `git diff --check`.
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o 'addopts='` if feasible; do not disable plugin autoload for the full suite.
- Rerun YAML validation after any checklist/acceptance evidence patch.

## Executor Prompt

Implement only Phase 298 status sync. Edit only `design/codestable/attention.md`, `tests/test_hermes_tavern_codestable_status.py`, and the Phase 298 design/checklist/acceptance artifacts. Advance current status to `All phases 1-297 accepted`, preserve all existing labels through Phase 296, append only `Phase 297 attention status sync through Phase 296`, and do not add a Phase 298 label to `attention.md`. Update the focused test constants/ranges/stale guards exactly as specified above. Keep checklist and acceptance non-final until parent-controller verification; `parent_verification_required` and `no_commit_or_push_performed` must remain true. Do not commit, push, stage, update state, touch runtime/protected paths, or run service lifecycle commands.

## Architect Review Checklist

- Diff touches only the five allowed files.
- `attention.md` has exactly one current-status bullet.
- Prefix is exactly `Current status (2026-06-18): All phases 1-297 accepted`.
- Stale `All phases 1-296 accepted`, `1-296`, and `1–296` terminal markers are rejected.
- `Phase 121-167` remains present.
- Explicit `Phase 168` through `Phase 296` labels are preserved exactly.
- Only new attention label is `Phase 297 attention status sync through Phase 296`.
- No `Phase 298 attention status sync` label appears in `attention.md`.
- Final suffix is exactly the Phase 295/296/297 suffix.
- Focused regression uses `range(168, 298)`.
- Stale aggregate guards are split and include stale `range(168, 297)`.
- Phase 298 artifacts remain non-final until parent-controller verification.
- No runtime, plugin, provider, gateway, root-design, README, architecture, roadmap, requirements, compound, build, credential, service lifecycle, commit, push, or state update occurred.
