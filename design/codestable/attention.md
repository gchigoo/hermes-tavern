# Attention

This file is the CodeStable skill startup mandatory read for the hermes-agent repo. All CodeStable sub-skills must read it before starting work.

## Project碎片知识

<!-- cs-note managed: new entries appended by cs-note under the relevant section -->

### 编译与构建

- Python 3.11+. No Rust compiler required for core or plugins (Rust only allowed as subprocess/PyO3 shim behind a Python entrypoint — see decision doc).
- Activate env: `source .venv/bin/activate` (fall back to `venv/` if `.venv/` absent).

### 运行与本地起服务

- CLI: `hermes` (after install/activate).
- Gateway: `hermes gateway`.
- Plugin system auto-discovers `plugins/*/plugin.yaml` at startup. Hermes Tavern plugin lives at `plugins/hermes_tavern/`.

### 测试

- Run Tavern plugin tests: `python -m pytest tests/plugins/test_hermes_tavern_*.py -q -o 'addopts='`
- Run full suite: `bash scripts/run_tests.sh`
- Always use `-o 'addopts='` to bypass any injected global pytest flags.
- Test fixtures for card parsing live under `tests/fixtures/` (to be created in Phase 3.5).

### 命令与脚本陷阱

- Never modify `run_agent.py`, `cli.py`, or `gateway/run.py` from within the Tavern plugin. Use the `pre_gateway_dispatch` hook only.
- `pre_gateway_dispatch` must return `{"action": "skip", "reason": "..."}` to suppress normal Hermes dispatch, or `{"action": "allow"}` / `None` to pass through.

### 路径与目录约定

- **Never hard-code `~/.hermes`**. Always use `get_hermes_home()` from `hermes_constants`.
- Plugin data DB lives at: `get_hermes_home() / "plugins" / "hermes-tavern" / "data" / "tavern.sqlite3"`.
- Plugin source lives at: `plugins/hermes_tavern/` (Python underscored package name).

### 环境变量与凭证

- API keys go in `~/.hermes/.env` — never in source or config YAML.
- Do not print API keys or secrets in debug output (enforced by design doc §19).

### 其他

- Plugin entrypoint contract: `plugin.yaml` (metadata) + `__init__.py` exposing `register(ctx) -> None` which calls `ctx.register_hook("pre_gateway_dispatch", handler)`.
- Design doc: `HERMES_TAVERN_DESIGN.md` (root). Implementation plan: `.hermes/plans/hermes-tavern-implementation-v0.1.md`.
- Current status (2026-06-18): All phases 1-310 accepted - skeleton, SQLite, card import, session CRUD, gateway hook, Phase 3.5 hardening, Phase 4 Prompt Compiler, Phase 5-6 provider bridge/integration, Phase 7-38 core runtime + hardening, Phase 121-167 novel project layer + metadata + JSON export for all entity types, Phase 168 image settings JSON export, Phase 169 project JSON export surface parity, Phase 170 export command-surface regression, Phase 171 root-design export parity, Phase 172 attention status sync through Phase 171, Phase 173 root-design section 17 import/export summary parity, Phase 174 attention status sync through Phase 173, Phase 175 attention status sync through Phase 174, Phase 176 attention status sync through Phase 175, Phase 177 attention status sync through Phase 176, Phase 178 attention status sync through Phase 177, Phase 179 attention status sync through Phase 178, Phase 180 attention status sync through Phase 179, Phase 181 attention status sync through Phase 180, Phase 182 attention status sync through Phase 181, Phase 183 attention status sync through Phase 182, Phase 184 attention status sync through Phase 183, Phase 185 attention status sync through Phase 184, Phase 186 attention status sync through Phase 185, Phase 187 attention status sync through Phase 186, Phase 188 attention status sync through Phase 187, Phase 189 attention status sync through Phase 188, Phase 190 attention status sync through Phase 189, Phase 191 attention status sync through Phase 190, Phase 192 attention status sync through Phase 191, Phase 193 attention status sync through Phase 192, Phase 194 attention status sync through Phase 193, Phase 195 attention status sync through Phase 194, Phase 196 attention status sync through Phase 195, Phase 197 attention status sync through Phase 196, Phase 198 attention status sync through Phase 197, Phase 199 attention status sync through Phase 198, Phase 200 attention status sync through Phase 199, Phase 201 attention status sync through Phase 200, Phase 202 attention status sync through Phase 201, Phase 203 attention status sync through Phase 202, Phase 204 attention status sync through Phase 203, Phase 205 attention status sync through Phase 204, Phase 206 attention status sync through Phase 205, Phase 207 attention status sync through Phase 206, Phase 208 attention status sync through Phase 207, Phase 209 attention status sync through Phase 208, Phase 210 attention status sync through Phase 209, Phase 211 attention status sync through Phase 210, Phase 212 attention status sync through Phase 211, Phase 213 attention status sync through Phase 212, Phase 214 attention status sync through Phase 213, Phase 215 attention status sync through Phase 214, Phase 216 attention status sync through Phase 215, Phase 217 attention status sync through Phase 216, Phase 218 attention status sync through Phase 217, Phase 219 attention status sync through Phase 218, Phase 220 attention status sync through Phase 219, Phase 221 attention status sync through Phase 220, Phase 222 attention status sync through Phase 221, Phase 223 attention status sync through Phase 222, Phase 224 attention status sync through Phase 223, Phase 225 attention status sync through Phase 224, Phase 226 attention status sync through Phase 225, Phase 227 attention status sync through Phase 226, Phase 228 attention status sync through Phase 227, Phase 229 attention status sync through Phase 228, Phase 230 attention status sync through Phase 229, Phase 231 attention status sync through Phase 230, Phase 232 attention status sync through Phase 231, Phase 233 attention status sync through Phase 232, Phase 234 attention status sync through Phase 233, Phase 235 attention status sync through Phase 234, Phase 236 attention status sync through Phase 235, Phase 237 attention status sync through Phase 236, Phase 238 attention status sync through Phase 237, Phase 239 attention status sync through Phase 238, Phase 240 attention status sync through Phase 239, Phase 241 attention status sync through Phase 240, Phase 242 attention status sync through Phase 241, Phase 243 attention status sync through Phase 242, Phase 244 attention status sync through Phase 243, Phase 245 attention status sync through Phase 244, Phase 246 attention status sync through Phase 245, Phase 247 attention status sync through Phase 246, Phase 248 attention status sync through Phase 247, Phase 249 attention status sync through Phase 248, Phase 250 attention status sync through Phase 249, Phase 251 attention status sync through Phase 250, Phase 252 attention status sync through Phase 251, Phase 253 attention status sync through Phase 252, Phase 254 attention status sync through Phase 253, Phase 255 attention status sync through Phase 254, Phase 256 attention status sync through Phase 255, Phase 257 attention status sync through Phase 256, Phase 258 attention status sync through Phase 257, Phase 259 attention status sync through Phase 258, Phase 260 attention status sync through Phase 259, Phase 261 attention status sync through Phase 260, Phase 262 attention status sync through Phase 261, Phase 263 attention status sync through Phase 262, Phase 264 attention status sync through Phase 263, Phase 265 attention status sync through Phase 264, Phase 266 attention status sync through Phase 265, Phase 267 attention status sync through Phase 266, Phase 268 attention status sync through Phase 267, Phase 269 attention status sync through Phase 268, Phase 270 attention status sync through Phase 269, Phase 271 attention status sync through Phase 270, Phase 272 attention status sync through Phase 271, Phase 273 attention status sync through Phase 272, Phase 274 attention status sync through Phase 273, Phase 275 attention status sync through Phase 274, Phase 276 attention status sync through Phase 275, Phase 277 attention status sync through Phase 276, Phase 278 attention status sync through Phase 277, Phase 279 attention status sync through Phase 278, Phase 280 attention status sync through Phase 279, Phase 281 attention status sync through Phase 280, Phase 282 attention status sync through Phase 281, Phase 283 attention status sync through Phase 282, Phase 284 attention status sync through Phase 283, Phase 285 attention status sync through Phase 284, Phase 286 attention status sync through Phase 285, Phase 287 attention status sync through Phase 286, Phase 288 attention status sync through Phase 287, Phase 289 attention status sync through Phase 288, Phase 290 attention status sync through Phase 289, Phase 291 attention status sync through Phase 290, Phase 292 attention status sync through Phase 291, Phase 293 attention status sync through Phase 292, Phase 294 attention status sync through Phase 293, Phase 295 attention status sync through Phase 294, Phase 296 attention status sync through Phase 295, Phase 297 attention status sync through Phase 296, Phase 298 attention status sync through Phase 297, Phase 299 attention status sync through Phase 298, Phase 300 attention status sync through Phase 299, Phase 301 attention status sync through Phase 300, Phase 302 attention status sync through Phase 301, Phase 303 attention status sync through Phase 302, Phase 304 attention status sync through Phase 303, Phase 305 attention status sync through Phase 304, Phase 306 attention status sync through Phase 305, Phase 307 attention status sync through Phase 306, Phase 308 attention status sync through Phase 307, Phase 309 attention status sync through Phase 308, and Phase 310 attention status sync through Phase 309.
- Adult-fiction non-negotiable boundaries defined in design doc §12.3 — do not build features that bypass provider safety systems.

### Hermes Tavern 凭证约束

- **Tavern DB 禁止持久化 api_key / access_token**。所有 LLM 凭证必须在运行时通过 `resolve_runtime_provider(requested=profile.provider, target_model=profile.model_id)` 获取，用完即丢。DB 只存逻辑 model profile（provider / model_id / api_mode / base_url override）。详见 `.codestable/compound/2026-05-18-decision-hermes-tavern-credential-reuse.md`。
- **Tavern 默认模型路由优先级**：(1) Claude 订阅/Claude Code 订阅适配器（Opus 4.6，若 Hermes 安全暴露）→ (2) `resolve_runtime_provider('anthropic', 'claude-opus-4-6')` → (3) OpenRouter/自定义 profile → (4) Hermes 全局配置兜底。model id 通过 model profile 配置解析，禁止在代码多处硬编码。详见 `.codestable/compound/2026-05-18-decision-hermes-tavern-default-model-routing.md`。
