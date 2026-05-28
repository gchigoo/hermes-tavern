---
doc_type: decision
category: constraint
date: 2026-05-18
slug: hermes-tavern-credential-reuse
status: active
area: hermes-tavern / credential-management
tags: [hermes-tavern, credentials, api-key, model-profile, resolve-runtime-provider]
---

## 背景

Hermes Tavern 需要向 LLM provider 发送请求（角色扮演、对话补全等），因此涉及 API 凭证管理。Hermes Agent 已经有一套完整的凭证解析链：`hermes_cli.runtime_provider.resolve_runtime_provider()`、`config.yaml` 中的 model 设置、`~/.hermes/.env` / secrets 文件、以及 credential pool。在 Tavern 插件设计阶段需要决定：Tavern 是否应自行存储 API key，还是复用 Hermes 已有机制。

## 决定

**Hermes Tavern 不在插件 DB 中持久化任何 API key 或 access token。**

Tavern DB（SQLite）只存储逻辑性的"模型档案"（model profile）引用，包含：

- `provider`（提供商名称，如 `anthropic`、`openai`）
- `name`（档案显示名称）
- `model_id`（具体模型标识符）
- `api_mode`（调用模式，如 `chat`、`completion`）
- `base_url`（可选，仅当需要覆盖默认 endpoint 时）
- `content_mode` / routing metadata（内容分级、路由标记等）

运行时通过 `resolve_runtime_provider(requested=profile.provider, target_model=profile.model_id)` 获取凭证，返回的 `api_key` / `base_url` / `api_mode` 仅在请求生命周期内短暂使用，不写入任何持久化存储。

若当前会话未绑定 model profile，默认回落到 Hermes 当前的 model/provider 全局配置。

## 理由

1. **单一凭证来源**：Hermes 的凭证解析链已经处理了多 provider、多 key 轮转、pool 选择等复杂度；Tavern 自己维护一份会造成两套凭证来源，难以一致性管理。
2. **安全边界**：将 API key 写入 SQLite 会扩大密钥暴露面。插件 DB 文件权限比 `~/.hermes/.env` 更难管控，且可能随 DB 导出/备份流出。
3. **最小权限原则**：插件只需要"用完即丢"的凭证，没有理由持久化。
4. **向后兼容**：用户在 `config.yaml` / `.env` 更换 key 后，Tavern 会话自动使用新凭证，无需重新配置 Tavern 侧。

## 考虑过的替代方案

| 方案 | 淘汰理由 |
|---|---|
| 在 Tavern DB 存储加密后的 API key，per-profile 独立配置 | 实现加密存储复杂，且造成凭证双轨，与 Hermes 全局 key 管理冲突 |
| 允许用户在 Tavern 侧覆盖 provider key（仅存于内存 session） | 超出 v0.1 范围，且绕过 Hermes 统一 credential pool（含轮转/限流逻辑） |
| 继承环境变量（直接读 `os.environ`） | 跳过 `resolve_runtime_provider` 的 pool / fallback 逻辑，行为不一致 |

## 后果

- **必须**：所有发起 LLM 请求的 Tavern 运行时代码（Phase 4 Prompt Compiler 及后续阶段）都需调用 `resolve_runtime_provider()` 而非直接读取环境变量或 DB 字段。
- **禁止**：任何 Tavern DB migration、ORM model、或 Pydantic schema 中出现 `api_key`、`access_token`、`secret` 字段。
- **允许**：`base_url` 字段可存储，因其不是敏感凭证，仅用于 endpoint 路由覆盖。
- **默认行为**：`session.model_profile_id IS NULL` 时，运行时等价于直接调用 `resolve_runtime_provider()` 不带 override，即使用 Hermes 全局配置。

## 相关文档

- `HERMES_TAVERN_DESIGN.md` §19（禁止打印/泄露 API key）
- `.codestable/attention.md` §环境变量与凭证
- `hermes_cli.runtime_provider.resolve_runtime_provider`（凭证解析入口）
- `.hermes/plans/hermes-tavern-implementation-v0.1.md`
