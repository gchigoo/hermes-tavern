# Public Security Reporting Policy

## Public-beta status and scope

Hermes Tavern is currently a public beta project. This policy covers public-facing
documentation and contribution workflows for repository content, documentation,
and project packaging in this repository.

It does not authorize runtime, provider, gateway, model, credential, or network
behavior changes.

## What to report

Please report suspected issues in these areas:

- Suspected credential leaks or exposed secrets in docs, tests, or templates.
- Unintended sensitive data and sensitive-data persistence, leakage, or
  unauthorized exposure.
- Unsafe import-path or path-disclosure patterns that can reveal private files.
- Provider/account endpoint exposure or hard-coded service endpoints.
- Multi-user or session-isolation problems, including cross-session bleed-through.

## Safe reporting path

- Do not post sensitive exploit details, raw logs, credentials, tokens,
  provider/account identifiers, or endpoint internals in public issues or PRs.
- Public issues and PRs should be used only for non-sensitive documentation,
  process, or test-coverage issues.
- For sensitive findings, contact the maintainer privately if a private channel is
  available. If not, open one minimal, high-level public issue requesting a
  private disclosure channel and include only redacted, non-actionable hints.

## Offline validation expectation

Validation for suspected issues should be done offline where possible and should
not include runtime lifecycle commands for services.

Avoid Gateway/service lifecycle commands (start, restart, reload, kill, manage,
etc.) and avoid calling provider/network/ComfyUI/TTS/Telegram credential
endpoints during reporting validation.

## Redaction guidance

Before sharing examples:

- Remove tokens, API keys, secrets, passwords, PATs, session tokens, and
  personally-identifying values.
- Replace concrete provider/account values with placeholders such as
  `[REDACTED]`.
- Remove concrete endpoint URLs and sensitive path fragments.

## Private vulnerability reporting

GitHub private security reporting is not guaranteed in this repository yet.
If and when enabled, sensitive reports can move there.
