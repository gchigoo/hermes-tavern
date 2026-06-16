---
doc_type: feature-design
status: approved
feature: "2026-06-15-hermes-tavern-phase273-attention-status-sync-through-phase272"
date: "2026-06-15"
created: "2026-06-15"
updated: "2026-06-15"
implementation_ready: true
owner: codestable-cron
summary: >
  Sync the mandatory CodeStable attention current-status line and focused static
  regression through accepted Phase 272, without changing runtime/source behavior,
  Hermes-native plugin architecture, provider safety behavior, or SillyTavern-compatible assets.
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests]
---

# Phase 273: CodeStable Attention Status Sync Through Phase 272

## Read-Only Architect Precheck

- `design/codestable/attention.md` currently reports `Current status (2026-06-15): All phases 1-271 accepted`.
- `tests/test_hermes_tavern_codestable_status.py` currently guards labels through Phase 271, stale terminal `1-270` markers, final suffix through Phase 271, and `range(168, 272)`.
- Phase 272 is accepted as a docs/test/status-only sync through Phase 271.
- No Phase 273 feature directory existed before this artifact.
- This slice is exactly one bounded docs/test/status-only sync and does not require service lifecycle commands.

## Scope

S1 may change only these no-commit lane files:

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`
- `design/codestable/features/2026-06-15-hermes-tavern-phase273-attention-status-sync-through-phase272/design.md`
- `design/codestable/features/2026-06-15-hermes-tavern-phase273-attention-status-sync-through-phase272/checklist.yaml`

S1 must not create or edit `acceptance.md`, must not perform final S2 closeout, and must not commit or push. Parent/controller verification owns final closeout later.

## Exact S1 Contract

- Current prefix becomes: `Current status (2026-06-15): All phases 1-272 accepted`
- Reject stale prefix/standalone markers: `1-271` and `1–271`
- Preserve valid internal marker: `Phase 121-167`
- Preserve all existing Phase 168-271 short labels.
- Append new terminal label exactly: `Phase 272 attention status sync through Phase 271`
- Final suffix exactly: `Phase 270 attention status sync through Phase 269, Phase 271 attention status sync through Phase 270, and Phase 272 attention status sync through Phase 271.`
- Do not add Phase 273 to the attention status line.

## Test Contract

- `CURRENT_STATUS_PREFIX = "Current status (2026-06-15): All phases 1-272 accepted"`
- `STALE_STATUS_PREFIX = "Current status (2026-06-15): All phases 1-271 accepted"`
- `STALE_PHASE_MARKER = "1-271"`
- `STALE_PHASE_MARKER_EN_DASH = "1–271"`
- `REQUIRED_PHASE_LABELS` includes all existing labels and `Phase 272 attention status sync through Phase 271`.
- `FINAL_STATUS_SUFFIX` is the exact suffix above.
- `phase_range` uses `range(168, 273)`.
- Source assertion requires literal `range(168, 273)` and rejects stale `range(168, 272)` via split-string construction.
- Exactly one `CURRENT_STATUS_PREFIX` assignment.
- No `.glob(`, `.rglob(`, `iterdir(`, or `os.walk` discovery tokens.

## Required Phase Labels

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
Phase 270 attention status sync through Phase 269
Phase 271 attention status sync through Phase 270
Phase 272 attention status sync through Phase 271
```

## Non-Goals

No runtime/source/provider/plugin behavior changes. Do not modify `run_agent.py`, `cli.py`, `gateway/run.py`, provider routing, prompt behavior, import/export behavior, schema behavior, SillyTavern assets, Hermes-native plugin architecture, provider safety behavior, adult-fiction/RP compatibility, or minors/underage handling.

## Verification Commands

- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --dir design/codestable/features/2026-06-15-hermes-tavern-phase273-attention-status-sync-through-phase272 --require doc_type --require status --require feature`
- `PYTHONDONTWRITEBYTECODE=1 python -m py_compile tests/test_hermes_tavern_codestable_status.py`
- `PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o 'addopts=' -p no:cacheprovider -s`
- Static marker guard over `design/codestable/attention.md` and `tests/test_hermes_tavern_codestable_status.py`
- `git diff --check`

## Acceptance Contract

S1 is ready for parent/controller closeout when the single current-status bullet reports all phases `1-272` accepted, preserves `Phase 121-167` and all Phase 168-271 labels, appends exactly the Phase 272 label, ends with the exact suffix through Phase 272, rejects stale `1-271` / `1–271`, and the focused static regression remains explicit and passes. S1 must leave `acceptance.md` and final S2 closeout to the parent/controller.
