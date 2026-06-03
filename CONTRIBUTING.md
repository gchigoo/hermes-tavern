# Hermes Tavern Contributor Guide

This repository is open for external contributions, with strict guardrails to keep
contributor workflow lightweight, safe, and review-friendly.

## Scope

Ordinary contributions should focus on docs, tests, and explicit, audited design
artifacts. Keep changes scoped to public-facing work unless a dedicated reviewer
request explicitly authorizes runtime behavior changes.

## Required setup

Set up a clean local environment with the project test-dependency bootstrap and
editable install:

```bash
python -m pip install -r requirements-test.txt
python -m pip install -e . --no-deps
```

## Required offline verification commands

Run all of these commands locally before opening a PR:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_repo_hygiene.py tests/test_hermes_tavern_readme_docs.py -q -o 'addopts='
PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_packaging.py -q -o 'addopts='
PYTHONPYCACHEPREFIX=/private/tmp/hermes-tavern-phase103-pycache python -m py_compile conftest.py plugins/__init__.py plugins/hermes_tavern/__init__.py src/hermes_tavern/*.py src/hermes_tavern/importers/*.py tests/test_hermes_tavern_*.py
PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_*.py -q -o 'addopts='
python design/codestable/tools/validate-yaml.py --yaml-only --file design/codestable/features/2026-06-03-hermes-tavern-phase120-codestable-public-verification-contract/checklist.yaml
git diff --check -- CONTRIBUTING.md README.md tests/test_hermes_tavern_repo_hygiene.py design/codestable/features/2026-06-03-hermes-tavern-phase120-codestable-public-verification-contract/checklist.yaml
```

## Safe validation rules for contributors

Ordinary contributions should not start/restart/reload/kill/manage the Gateway or
any services in this repo for validation.

Ordinary contributions should not call provider/model/network/ComfyUI/TTS/Telegram
credential endpoints in validation routines or examples.

## Secret handling

Do not commit secrets, API keys, tokens, service credentials, or any other
sensitive runtime material. If one is discovered, remove it immediately and reopen
history if needed.

## Security issues

For suspected security findings, follow [`SECURITY.md`](./SECURITY.md) for the
supported reporting scope and the private reporting path.

## Support

For non-security help and public process questions, use the support guidance in
[`SUPPORT.md`](./SUPPORT.md).

## What to include in PRs

When possible, include tests and docs updates with each change, and explicitly note
whether the change is safe from external side effects.

## Code of Conduct

Before opening issues or PRs, please read and follow
[`CODE_OF_CONDUCT.md`](./CODE_OF_CONDUCT.md).
All contribution workflows should remain respectful and constructive.
