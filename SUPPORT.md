# Public Support Policy

Hermes Tavern is currently public beta scoped to docs/tests/package-readiness support for
repository contributors and users.

## What this support covers

- Public documentation updates and public README/contributing guidance.
- Repo hygiene, packaging, and offline validation support.
- Non-sensitive issue triage and process questions.

## What this support does not cover

- Runtime behavior changes, provider model routing changes, credential handling,
  gateway service management, network endpoint troubleshooting, or runtime
  incident response.

## GitHub issue routing

For non-security help and reportable defects:

- Use existing public issue templates for non-runtime documentation or test issues.
- Use the bug report path for reproducible behavior defects.
- Use the docs/tests/public-readiness path for release-pipeline or onboarding
  guidance gaps.

## Safe sharing and redaction

Do not post API keys, secrets, tokens, passwords, session IDs, provider
endpoints, or other private account identifiers in issues or PR text.

- Remove or mask values such as `[REDACTED]`, `***`, or `xxxx`.
- Avoid raw logs that include secrets or sensitive metadata.

## Offline validation expectations

When filing docs/tests support requests, please include offline checks that were
run and their outputs.

Examples:

- `python -m pytest tests/test_hermes_tavern_repo_hygiene.py -q -o 'addopts='`
- `python -m pytest tests/test_hermes_tavern_readme_docs.py -q -o 'addopts='`
- `python -m pytest tests/test_hermes_tavern_packaging.py -q -o 'addopts='`
- `python -m py_compile ...` (offline compile checks from CONTRIBUTING.md)

## Security escalation

For suspected security findings, follow [`SECURITY.md`](./SECURITY.md) and
do not share sensitive exploit details in public text.
