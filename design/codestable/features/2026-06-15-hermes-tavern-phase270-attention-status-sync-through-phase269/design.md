---
doc_type: feature-design
status: approved
feature: "2026-06-15-hermes-tavern-phase270-attention-status-sync-through-phase269"
date: "2026-06-15"
created: "2026-06-15"
updated: "2026-06-15"
implementation_ready: true
owner: codestable-cron
summary: >
  Sync the mandatory CodeStable attention current-status line and focused static
  regression through accepted Phase 269, without changing runtime/source behavior,
  plugin architecture, provider safety behavior, adult-fiction/RP compatibility,
  or SillyTavern-compatible assets.
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests]
---

# Phase 270: CodeStable Attention Status Sync Through Phase 269

## Read-Only Architect Precheck

Controller and Codex architect observed:

- Branch/head before materialization: `main` at `a220e5f`, with a clean worktree.
- Latest accepted feature: `design/codestable/features/2026-06-15-hermes-tavern-phase269-attention-status-sync-through-phase268/`.
- Phase 269 design is `status: approved`, checklist top-level is `status: accepted` / `workflow_status: accepted`, S1/S2 are completed, and `acceptance.md` is `status: accepted`.
- `design/codestable/attention.md` currently reports accepted phases through Phase 268.
- `tests/test_hermes_tavern_codestable_status.py` currently guards Phase 168 through Phase 268 labels, stale terminal `1-267` markers, final suffix through Phase 268, and `range(168, 269)`.
- No Phase 270 feature directory existed before this controller materialization.
- Codex architect selected this slice in `/tmp/hermes-tavern-architect-phase270.jsonl`.
- This phase is docs/test/status-only and does not require service lifecycle commands.

## Gap

Phase 269 is accepted, but the mandatory CodeStable startup status and focused static regression still stop at Phase 268.

## Scope

Create exactly one bounded CodeStable status-sync phase:

- Feature directory: `design/codestable/features/2026-06-15-hermes-tavern-phase270-attention-status-sync-through-phase269/`

S1 is the bounded implementation slice and may change exactly two existing files:

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`

S2 is parent-controller closeout after verification and may change only these new Phase 270 feature artifacts:

- `design/codestable/features/2026-06-15-hermes-tavern-phase270-attention-status-sync-through-phase269/design.md`
- `design/codestable/features/2026-06-15-hermes-tavern-phase270-attention-status-sync-through-phase269/checklist.yaml`
- `design/codestable/features/2026-06-15-hermes-tavern-phase270-attention-status-sync-through-phase269/acceptance.md`

## Exact Marker Contract

S1 must update only the terminal current-status range from `All phases 1-268 accepted` to `All phases 1-269 accepted`, preserve the status date `2026-06-15`, preserve all existing labels from Phase 168 through Phase 268 and the valid internal `Phase 121-167` range, and append exactly:

`Phase 269 attention status sync through Phase 268`

The attention status bullet must remain exactly one bullet. Do not add Phase 270 to the attention status.

The focused static regression must advance together:

- `CURRENT_STATUS_PREFIX`: `Current status (2026-06-15): All phases 1-269 accepted`
- `STALE_STATUS_PREFIX`: `Current status (2026-06-15): All phases 1-268 accepted`
- stale standalone terminal markers: `1-268` and `1–268`
- valid internal range remains: `Phase 121-167`
- append label exactly: `Phase 269 attention status sync through Phase 268`
- final suffix exactly: `Phase 267 attention status sync through Phase 266, Phase 268 attention status sync through Phase 267, and Phase 269 attention status sync through Phase 268.`
- `REQUIRED_PHASE_LABELS` must explicitly include Phase 168 through Phase 269, preserving the non-uniform Phase 168-173 labels from the current test and appending the new Phase 269 label.
- required aggregate phase coverage: `range(168, 270)`
- stale aggregate range to reject in test source: `range(168, 269)`, avoiding direct literal false positives where necessary
- exactly one `CURRENT_STATUS_PREFIX` assignment
- focused test remains static and explicit: no `glob`, `rglob`, `iterdir`, `os.walk`, or generated filesystem discovery

## Required Phase 168-269 Short Labels

```text
Phase 168 image settings JSON export
Phase 169 project JSON export surface parity
Phase 170 export command-surface regression
Phase 171 root-design export parity
Phase 172 attention status sync through Phase 171
Phase 173 root-design section 17 import/export summary parity
Phase 174 attention status sync through Phase 173
Phase 175 attention status sync through Phase 174
Phase 176 attention status sync through Phase 175
Phase 177 attention status sync through Phase 176
Phase 178 attention status sync through Phase 177
Phase 179 attention status sync through Phase 178
Phase 180 attention status sync through Phase 179
Phase 181 attention status sync through Phase 180
Phase 182 attention status sync through Phase 181
Phase 183 attention status sync through Phase 182
Phase 184 attention status sync through Phase 183
Phase 185 attention status sync through Phase 184
Phase 186 attention status sync through Phase 185
Phase 187 attention status sync through Phase 186
Phase 188 attention status sync through Phase 187
Phase 189 attention status sync through Phase 188
Phase 190 attention status sync through Phase 189
Phase 191 attention status sync through Phase 190
Phase 192 attention status sync through Phase 191
Phase 193 attention status sync through Phase 192
Phase 194 attention status sync through Phase 193
Phase 195 attention status sync through Phase 194
Phase 196 attention status sync through Phase 195
Phase 197 attention status sync through Phase 196
Phase 198 attention status sync through Phase 197
Phase 199 attention status sync through Phase 198
Phase 200 attention status sync through Phase 199
Phase 201 attention status sync through Phase 200
Phase 202 attention status sync through Phase 201
Phase 203 attention status sync through Phase 202
Phase 204 attention status sync through Phase 203
Phase 205 attention status sync through Phase 204
Phase 206 attention status sync through Phase 205
Phase 207 attention status sync through Phase 206
Phase 208 attention status sync through Phase 207
Phase 209 attention status sync through Phase 208
Phase 210 attention status sync through Phase 209
Phase 211 attention status sync through Phase 210
Phase 212 attention status sync through Phase 211
Phase 213 attention status sync through Phase 212
Phase 214 attention status sync through Phase 213
Phase 215 attention status sync through Phase 214
Phase 216 attention status sync through Phase 215
Phase 217 attention status sync through Phase 216
Phase 218 attention status sync through Phase 217
Phase 219 attention status sync through Phase 218
Phase 220 attention status sync through Phase 219
Phase 221 attention status sync through Phase 220
Phase 222 attention status sync through Phase 221
Phase 223 attention status sync through Phase 222
Phase 224 attention status sync through Phase 223
Phase 225 attention status sync through Phase 224
Phase 226 attention status sync through Phase 225
Phase 227 attention status sync through Phase 226
Phase 228 attention status sync through Phase 227
Phase 229 attention status sync through Phase 228
Phase 230 attention status sync through Phase 229
Phase 231 attention status sync through Phase 230
Phase 232 attention status sync through Phase 231
Phase 233 attention status sync through Phase 232
Phase 234 attention status sync through Phase 233
Phase 235 attention status sync through Phase 234
Phase 236 attention status sync through Phase 235
Phase 237 attention status sync through Phase 236
Phase 238 attention status sync through Phase 237
Phase 239 attention status sync through Phase 238
Phase 240 attention status sync through Phase 239
Phase 241 attention status sync through Phase 240
Phase 242 attention status sync through Phase 241
Phase 243 attention status sync through Phase 242
Phase 244 attention status sync through Phase 243
Phase 245 attention status sync through Phase 244
Phase 246 attention status sync through Phase 245
Phase 247 attention status sync through Phase 246
Phase 248 attention status sync through Phase 247
Phase 249 attention status sync through Phase 248
Phase 250 attention status sync through Phase 249
Phase 251 attention status sync through Phase 250
Phase 252 attention status sync through Phase 251
Phase 253 attention status sync through Phase 252
Phase 254 attention status sync through Phase 253
Phase 255 attention status sync through Phase 254
Phase 256 attention status sync through Phase 255
Phase 257 attention status sync through Phase 256
Phase 258 attention status sync through Phase 257
Phase 259 attention status sync through Phase 258
Phase 260 attention status sync through Phase 259
Phase 261 attention status sync through Phase 260
Phase 262 attention status sync through Phase 261
Phase 263 attention status sync through Phase 262
Phase 264 attention status sync through Phase 263
Phase 265 attention status sync through Phase 264
Phase 266 attention status sync through Phase 265
Phase 267 attention status sync through Phase 266
Phase 268 attention status sync through Phase 267
Phase 269 attention status sync through Phase 268
```

## Main Flow

Phase 269 accepted -> S1 advances the attention status to 1-269 -> S1 advances the focused static regression -> child lane verifies and leaves Phase 270 artifacts non-final -> parent controller reruns gates and performs final S2 acceptance closeout.

## Non-Goals And Boundaries

This phase does not change runtime behavior, source behavior, plugin behavior, provider/model routing, prompt/generation behavior, import/export behavior, schema behavior, README text, root design, architecture docs, roadmap docs, requirement docs, compound docs, build outputs, content mode, minors/underage handling, provider safety behavior, plugin assets, SillyTavern asset compatibility, Hermes-native plugin architecture, adult-fiction/RP compatibility, or safety-bypass behavior.

Do not run service lifecycle commands. Do not repair unrelated checklist residue in this slice. Do not commit or push.

## Verification Commands

- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --dir design/codestable/features/2026-06-15-hermes-tavern-phase270-attention-status-sync-through-phase269 --require doc_type --require status --require feature`
- `PYTHONDONTWRITEBYTECODE=1 python -m py_compile tests/test_hermes_tavern_codestable_status.py`
- `PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o 'addopts=' -p no:cacheprovider -s`
- Static marker guard for one current-status line, terminal 1-269, Phase 168-269 labels, stale 1-268 rejection, valid Phase 121-167 preservation, final suffix through Phase 269, exactly one `CURRENT_STATUS_PREFIX` assignment, `range(168, 270)`, stale range rejection, and no generated discovery tokens.
- Changed-path guard for exactly the two S1 files plus the new Phase 270 design/checklist/draft acceptance artifacts.
- Protected-path guard for changes outside the allowed files and protected runtime/source/plugin/provider/prompt/import/export/schema/root-design/architecture/README/roadmap/requirements/compound/build surfaces.
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o 'addopts='` if feasible.
- `git diff --check`.

## Acceptance Contract

Phase 270 S1 is ready for parent closeout when the single current-status bullet reports all phases 1-269 accepted with date 2026-06-15, preserves prior labels through Phase 268, appends exactly `Phase 269 attention status sync through Phase 268`, ends with the required final suffix through Phase 269, rejects stale terminal `1-268` and `1–268` markers while preserving valid `Phase 121-167`, the focused static regression passes and remains explicit/static, changed paths are limited to the five allowed files, protected runtime/source/plugin surfaces stay unchanged, and final acceptance/checklist closeout remains non-final until parent verification.

## Risks

- The stale-negative checks and aggregate range must advance together.
- The stale status prefix intentionally uses the same 2026-06-15 date as the expected prefix; only the terminal accepted range differs.
- The long status bullet can drift in punctuation; the final suffix must move the `and` from Phase 268 to Phase 269.
- The focused test self-inspects its own source; split stale aggregate literals so the rejected range does not appear contiguously.
