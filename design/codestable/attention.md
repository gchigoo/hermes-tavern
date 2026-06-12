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
- Current status (2026-06-12): All phases 1-186 accepted - skeleton, SQLite, card import, session CRUD, gateway hook, Phase 3.5 hardening, Phase 4 Prompt Compiler, Phase 5-6 provider bridge/integration, Phase 7-38 core runtime + hardening, Phase 121-167 novel project layer + metadata + JSON export for all entity types, Phase 168 image settings JSON export, Phase 169 project JSON export surface parity, Phase 170 export command-surface regression, Phase 171 root-design export parity, Phase 172 attention status sync through Phase 171, Phase 173 root-design section 17 import/export summary parity, Phase 174 attention status sync through Phase 173, Phase 175 attention status sync through Phase 174, Phase 176 attention status sync through Phase 175, Phase 177 attention status sync through Phase 176, Phase 178 attention status sync through Phase 177, Phase 179 attention status sync through Phase 178, Phase 180 attention status sync through Phase 179, Phase 181 attention status sync through Phase 180, Phase 182 attention status sync through Phase 181, Phase 183 attention status sync through Phase 182, Phase 184 attention status sync through Phase 183, Phase 185 attention status sync through Phase 184, and Phase 186 attention status sync through Phase 185.
- Adult-fiction non-negotiable boundaries defined in design doc §12.3 — do not build features that bypass provider safety systems.

### Hermes Tavern 凭证约束

- **Tavern DB 禁止持久化 api_key / access_token**。所有 LLM 凭证必须在运行时通过 `resolve_runtime_provider(requested=profile.provider, target_model=profile.model_id)` 获取，用完即丢。DB 只存逻辑 model profile（provider / model_id / api_mode / base_url override）。详见 `.codestable/compound/2026-05-18-decision-hermes-tavern-credential-reuse.md`。
- **Tavern 默认模型路由优先级**：(1) Claude 订阅/Claude Code 订阅适配器（Opus 4.6，若 Hermes 安全暴露）→ (2) `resolve_runtime_provider('anthropic', 'claude-opus-4-6')` → (3) OpenRouter/自定义 profile → (4) Hermes 全局配置兜底。model id 通过 model profile 配置解析，禁止在代码多处硬编码。详见 `.codestable/compound/2026-05-18-decision-hermes-tavern-default-model-routing.md`。
