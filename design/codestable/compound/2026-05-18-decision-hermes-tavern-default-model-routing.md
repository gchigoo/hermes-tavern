---
doc_type: decision
category: preference
date: 2026-05-18
slug: hermes-tavern-default-model-routing
status: active
area: hermes-tavern / model-routing
tags: [hermes-tavern, model-routing, claude-subscription, opus-4-6, provider-priority]
---

## 背景

Hermes Tavern 需要在发起 LLM 请求时选择 provider 和具体模型。用户有多种可用凭证来源（Claude 订阅/Claude Code 订阅适配器、Anthropic API key、OpenRouter、Hermes 全局配置），需要确定默认路由优先级，以便实现代码和 model profile 缺省值有统一依据。

## 决定

**Tavern 运行时默认模型路由优先级（从高到低）：**

1. **Claude 订阅 / Claude Code 订阅适配器**（最高优先）  
   若 Hermes 安全暴露了 Claude Code 订阅访问渠道（无需持久化 API key），优先通过该适配器使用 Opus 4.6。该渠道不存储任何秘密，由 Hermes 统一代理。目标模型：`claude-opus-4-6`（或 Hermes provider registry 中对应的 Opus 4.6 model id）。

2. **Anthropic provider 凭证**（次优）  
   通过 `resolve_runtime_provider(requested='anthropic', target_model='claude-opus-4-6')` 获取运行时凭证。`target_model` 的具体 model id 应通过 model profile 配置解析，而非在多处硬编码字符串。

3. **OpenRouter / 自定义 profile**（第三优先）  
   若前两者均不可用，查找用户配置的 OpenRouter profile 或其他兼容 Opus 4.6 的自定义 provider profile。model id 由 profile 配置指定，不硬编码。

4. **Hermes 全局 provider 配置**（兜底）  
   `session.model_profile_id IS NULL` 或所有上述渠道均不可用时，回落到 Hermes 当前全局 model/provider 配置（等价于裸调 `resolve_runtime_provider()` 不带 override）。

## 理由

- 用户明确偏好优先消费已有的 Claude 订阅额度，而非消耗独立 API key 余额。
- Opus 4.6 是当前首选质量档位；路由链保证在该模型不可用时有有序降级路径，而非静默失败。
- 凭证持久化约束（见 `2026-05-18-decision-hermes-tavern-credential-reuse.md`）不变：无论哪一优先级命中，均通过 `resolve_runtime_provider()` 短暂获取凭证，不写入 DB。

## 重要不确定性（实现时需解析）

- Claude Code 订阅适配器的 Hermes 侧接口尚未定稿——实现者须查阅 Hermes provider registry，确认对应 provider 名称和 capability 标识，而非猜测字符串。
- Opus 4.6 的 model id 在不同 provider 下可能不同（如 `claude-opus-4-6` vs `anthropic/claude-opus-4-6`）。正确做法：在 model profile 或 Hermes 配置中查 model id，Phase 4 实现时通过配置/profile 解析，不在代码多处散落硬编码。

## 约束

- **禁止**：在 Phase 4 Prompt Compiler 或任何 Tavern 运行时代码中把 `"claude-opus-4-6"` 这类字符串硬编码在多处；应统一从 model profile 或 Hermes provider registry 读取。
- **允许**：在 model profile 的缺省值（migration seed 或 CLI `/model set` 默认参数）中写入 `claude-opus-4-6` 作为默认 model_id，以便用户可以显式覆盖。

## 相关文档

- `.codestable/compound/2026-05-18-decision-hermes-tavern-credential-reuse.md`（凭证禁止持久化）
- `.codestable/attention.md` §Hermes Tavern 凭证约束
- `HERMES_TAVERN_DESIGN.md`（整体设计）
- `hermes_cli.runtime_provider.resolve_runtime_provider`（凭证解析入口）
