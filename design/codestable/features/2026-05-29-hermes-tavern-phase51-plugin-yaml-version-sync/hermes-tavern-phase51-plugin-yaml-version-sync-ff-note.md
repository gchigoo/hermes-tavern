---
name: hermes-tavern-phase51-plugin-yaml-version-sync
description: Enforce plugin.yaml version == pyproject.toml version via a test; explicitly declare empty dependencies in pyproject.toml
metadata:
  type: feature-ff-note
---

## 做了什么
为 hermes-tavern 添加版本一致性保护：当 pyproject.toml 版本号被 bump 后，若 plugin.yaml 未同步更新，新增测试会在 CI 中立即失败，阻止不一致的元数据发布。同时在 pyproject.toml 中显式声明 `dependencies = []`，明确表达「无运行时依赖」合约。

## 改了哪些
- `pyproject.toml` — 在 [project] 表中加入 `dependencies = []`
- `tests/test_hermes_tavern_packaging.py` — 新增 `test_plugin_yaml_version_matches_package_version`，读取 plugin.yaml 并断言其 version 字段与 `hermes_tavern.__version__` 一致

## 怎么验证的
py_compile 全文件通过；`pytest tests/test_hermes_tavern_*.py -q` 449 passed（较 Phase 50 的 448 +1）；checklist YAML 验证通过。
