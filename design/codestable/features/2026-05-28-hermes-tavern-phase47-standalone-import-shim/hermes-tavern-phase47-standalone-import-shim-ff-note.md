---
doc_type: feature-ff-note
feature: hermes-tavern-phase47-standalone-import-shim
date: 2026-05-28
requirement:
tags: [standalone, import-shim, compatibility, testing]
---

## 做了什么
让独立仓库的测试能正常 import `plugins.hermes_tavern.*`，无需把源码搬回 monorepo。
新增 `conftest.py`（MetaPathFinder shim）和 `plugins/__init__.py`（命名空间占位符），
以及 `plugins/hermes_tavern/__init__.py`（独立脚本可用的 legacy package shim），
同时修正 `test_hermes_tavern_cards.py` 里一个遗留自 monorepo 的 fixture 路径偏差。

## 改了哪些
- `conftest.py` (新建) — 向 `sys.path` 注入 `src/`，并通过 `_HermesTavernShimFinder` 将
  `plugins.hermes_tavern.*` 全部重定向到 `hermes_tavern.*`；`_AliasLoader.exec_module`
  直接替换 `sys.modules` 条目以保证对象同一性（isinstance / is 均安全）
- `plugins/__init__.py` (新建) — 两行注释，让 `plugins` 作为磁盘包可被标准 importer 找到
- `plugins/hermes_tavern/__init__.py` (新建) — 将 legacy 包路径委托到
  `src/hermes_tavern`，让 pytest 之外的独立开发脚本也能 `import plugins.hermes_tavern.*`
- `tests/test_hermes_tavern_cards.py:33` — `parent.parent` → `parent`；monorepo 路径深度
  比独立仓库多一级，导致 `st_v2.json` / `direct.json` 找不到

## 怎么验证的
- legacy import smoke outside pytest — PASS
- `python -m py_compile conftest.py plugins/__init__.py plugins/hermes_tavern/__init__.py src/hermes_tavern/*.py src/hermes_tavern/importers/*.py tests/test_hermes_tavern_*.py` — PASS
- `python -m pytest tests/test_hermes_tavern_plugin.py tests/test_hermes_tavern_adapters.py tests/test_hermes_tavern_cards.py -q -o 'addopts='` — 39 passed
- `python -m pytest tests/test_hermes_tavern_*.py -q -o 'addopts='` — 442 passed
- `python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-05-28-hermes-tavern-phase47-standalone-import-shim/checklist.yaml` — PASS

## 顺手发现（可选，不阻塞）
- Claude Code 两次命中 `error_max_turns`，但文件修改已落盘；controller 已独立完成全量验证。
