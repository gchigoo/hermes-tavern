---
doc_type: feature-ff-note
feature: hermes-tavern-phase49-packaging-polish
date: 2026-05-29
requirement: ""
tags: [packaging, metadata, smoke-test, plugin-discovery]
---

## 做了什么
关闭 Phase 48 的隔离验证缺口：新增 subprocess 隔离 smoke test，证明 editable install 在没有 conftest.py sys.path 注入的情况下同样可工作。同时补齐 plugin.yaml entry_point 字段、pyproject.toml PEP 621 元数据（readme/license/authors）、README 安装文档。

## 改了哪些
- `src/hermes_tavern/plugin.yaml` — 新增 `entry_point: "hermes_tavern:register"` 字段
- `pyproject.toml` — 新增 `readme`、`license`、`authors` 三个 PEP 621 字段
- `tests/test_hermes_tavern_packaging.py` — 新增 `test_editable_install_isolation_smoke`（subprocess PYTHONPATH="" 隔离）和 `test_plugin_yaml_declares_entry_point`
- `README.md` — 新增 Installation + Development 章节

## 怎么验证的
py_compile 全量通过；pytest tests/test_hermes_tavern_*.py 447 passed（+2 新测试）；隔离 smoke 以 subprocess PYTHONPATH="" 启动子进程确认 editable install 独立可用；YAML validator 1 file passed。

## 顺手发现（可选，不阻塞）
- `design/codestable/features/2026-05-28-hermes-tavern-phase48-standalone-packaging/checklist.yaml:32` — S2 result 声称"editable-install smoke from /tmp"但实际测试在进程内（conftest 已注入 src/），Phase 49 S3 才真正闭环。Phase 48 checklist 状态可保持不变，因为功能本身无误，只是验证粒度不足。
