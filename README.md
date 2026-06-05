# Hermes Tavern

Project status: **Beta / Experimental**.

A Hermes Agent plugin for character-based roleplay (RP) with SillyTavern compatibility.

Hermes Tavern is a standalone, publication-ready **SillyTavern-compatible RP/novel runtime** that runs as a plugin against Hermes Agent gateways.

Extracted from the hermes-agent monorepo to an independent project.

## Public posture

This repository is for fictional roleplay and creative writing workflows only.
It does not bypass, weaken, or replace provider/platform safety mechanisms.
No real API keys or credentials should be committed.

## Compatibility

Hermes Tavern targets Python 3.11+ and runs as a Hermes Agent Gateway plugin.
It is compatible with the SillyTavern card JSON/PNG import surface for character cards.
WebP/JPEG character-card imports are not supported yet and return a friendly
unsupported-format error message.

## Structure

```
hermes-tavern/
├── src/hermes_tavern/    # Plugin source code
├── tests/                # Test suite (pytest)
├── design/               # Design docs, CodeStable plans, architecture decisions
│   ├── codestable/       # Phase-by-phase feature designs & checklists
│   └── plans/            # Implementation plans
├── patches/              # Core hermes-agent diffs this plugin depends on
└── README.md
```

## Origin

This plugin was developed as part of the [hermes-agent](https://github.com/nousresearch/hermes-agent) monorepo (`tavern-dev` branch), spanning 40+ feature phases from May 2026.

## Installation

Install as an editable package into the same environment as Hermes Agent:

```bash
python -m pip install -e /path/to/hermes-tavern --no-deps
```

Hermes Gateway discovers the plugin via `plugin.yaml` at the package root. The
`entry_point` key names the Python callable that Hermes calls to register hooks:

```yaml
entry_point: "hermes_tavern:register"
```

`register(ctx)` attaches a single `pre_gateway_dispatch` hook. No network calls
are made during registration; all external I/O happens inside the hook at request
time. Standalone import/registration also works outside the repo root; when the
full Hermes Agent package is not present, Hermes Tavern falls back to
`$HERMES_HOME` or `~/.hermes` only for path resolution.

## Telegram / Gateway quick smoke

After installing into the active Hermes environment and enabling the plugin,
the operator can start or reload Hermes Gateway when they choose. Then verify
the mobile loop from Telegram:

```text
/rp help
/rp doctor
/rp card import        # attach JSON/PNG; WebP/JPEG -> friendly unsupported-format error
/rp start <card-name>
hello from mobile
/rp session info
/rp pause
hello regular Hermes   # should fall through to the normal Hermes agent
/rp resume
/rp export
```

Expected behavior:

- `/rp ...` commands are handled by Hermes Tavern and skipped from the normal
  Hermes agent dispatch.
- `/rp doctor` prints offline current-scope diagnostics without making provider,
  model, network, ComfyUI, or filesystem-write calls.
- Ordinary messages are intercepted only while the current gateway scope has an
  active Tavern session.
- The session scope includes platform, chat, thread/topic, and user ID; tests
  cover multi-user, multi-chat, multi-thread, and multi-platform isolation.
- Gateway imports are attachment-first: explicit paths are accepted only when
  they normalize to a same-message local attachment, so mobile users cannot read
  arbitrary host-local paths.
- Export/image responses use `MEDIA:` markers so the gateway can deliver native
  files/media while keeping marker text out of chat replies.

## Core commands

```text
/rp help | /rp status | /rp doctor
/rp start <card> | /rp say <message> | /rp greeting list/use <n>
/rp pause | /rp resume | /rp end | /rp archive
/rp retry | /rp swipe list | /rp undo | /rp edit last <text>
/rp speak | /rp voice [on|off] | /rp history [limit] [page]
/rp session info | /rp sessions [all] [limit] [page] | /rp switch <session-id-prefix>
/rp rename <name> | /rp clone [name]
/rp export [markdown|st-json]
/rp assets | /rp cards
/rp card import <file>     # JSON/PNG; WebP/JPEG not supported yet (friendly unsupported-format error)
/rp card search/inspect/use <card>
/rp preset import/list/inspect/use/clear <preset>
/rp prompt list/inspect/enable/disable/debug
/rp lore import/list/inspect/use/clear/enable/disable/test/debug
/rp memory add/forget/list/summary/debug
/rp persona import/new/list/inspect/use/temp/clear/debug
/rp note set/clear/inspect/position/frequency
/rp content mode [safe|adult-fiction]
/rp model status/profiles/seed/use/mode/live/test
/rp image scene/character/face/background/last | /rp image prompt/retry/inspect/history
/rp image provider/settings/style/safety ...
/rp project create/list/info/set/export
/rp project style [project-id] | /rp project style inspect [project-id]
/rp project style set [project-id] <text> | /rp project style clear [project-id]
/rp project brief [project-id] | /rp project brief inspect [project-id]
/rp project brief type set <project-id> <novel|serial|rp|worldbuilding|other> | /rp project brief type clear <project-id>
/rp project brief premise set <project-id> <text> | /rp project brief premise clear <project-id>
/rp project outline [project-id] | /rp project outline inspect [project-id]
/rp project outline set [project-id] <text> | /rp project outline clear [project-id]
/rp chapter create/list
/rp chapter summary <chapter-id> [text]
/rp chapter summary clear <chapter-id>
/rp scene create/list/start
/rp scene goal <scene-id> [text] | /rp scene goal clear <scene-id>
/rp scene summary <scene-id> [text]
/rp scene summary clear <scene-id>
/rp scene narration <scene-id>
/rp scene narration clear <scene-id>
/rp scene narration pov <scene-id> <label>
/rp scene narration tense <scene-id> <past|present>
/rp canon add/list/group | /rp timeline add/list
/rp character state add <project-id> <label> <state...>
/rp character state list [project-id]
/rp character state inspect <character-state-id>
/rp character state update <character-state-id> <state...>
/rp character state delete <character-state-id>
/rp relationship add <project-id> <label> <state...>
/rp relationship list [project-id]
/rp relationship inspect <relationship-id>
/rp relationship update <relationship-id> <state...>
/rp relationship delete <relationship-id>
/rp debug prompt [limit] [page] | /rp debug context [limit] [page] | /rp debug swipes
```

## Development

For contributor onboarding and issue routing, use the dedicated public policy
documents:

- [CONTRIBUTING.md](CONTRIBUTING.md)
- [SUPPORT.md](SUPPORT.md)
- [SECURITY.md](SECURITY.md)
- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- [CHANGELOG.md](CHANGELOG.md)

```bash
python -m pip install -r requirements-test.txt
python -m pip install -e . --no-deps
python -m py_compile conftest.py plugins/__init__.py plugins/hermes_tavern/__init__.py src/hermes_tavern/*.py src/hermes_tavern/importers/*.py tests/test_hermes_tavern_*.py
python -m pytest tests/test_hermes_tavern_*.py -q -o 'addopts='
```

## License

This project is licensed under the [MIT License](LICENSE).

## Release preflight

For public-release context, see [CHANGELOG](CHANGELOG.md) before running checks.

Run these offline checks before release, so we can catch regressions without
restarting the Gateway or touching runtime services:

- `python -m pip install -r requirements-test.txt`
- `python -m py_compile conftest.py plugins/__init__.py plugins/hermes_tavern/__init__.py src/hermes_tavern/*.py src/hermes_tavern/importers/*.py tests/test_hermes_tavern_*.py`
- `python -m pytest tests/test_hermes_tavern_readme_docs.py -q -o 'addopts='`
- `python -m pytest tests/test_hermes_tavern_packaging.py -q -o 'addopts='`
- `python -m pytest tests/test_hermes_tavern_*.py -q -o 'addopts='`
- `python design/codestable/tools/validate-yaml.py --yaml-only --file design/codestable/features/2026-06-03-hermes-tavern-phase120-codestable-public-verification-contract/checklist.yaml`
- `git diff --check -- CONTRIBUTING.md README.md tests/test_hermes_tavern_repo_hygiene.py design/codestable/features/2026-06-03-hermes-tavern-phase120-codestable-public-verification-contract/checklist.yaml`
- `python -m build --sdist --wheel --outdir /tmp && python -m pip install --no-deps --target /tmp/hermes-tavern-release-smoke --no-index --find-links /tmp --force-reinstall hermes-tavern` to verify isolated wheel install and entry point metadata.
- Inspect wheel/sdist artifact inspection (payload + dist-info + metadata) and validate no repo-root-only files land in the wheel.
- Verify wheel payload boundary coverage includes `entry_points.txt` and excludes forbidden repository artifacts.

Packaging smoke from outside the repo root:

```bash
cd /tmp
python - <<'PY'
import importlib.resources as resources
import hermes_tavern
class Ctx:
    def __init__(self): self.hooks = []
    def register_hook(self, name, fn): self.hooks.append((name, fn.__module__, fn.__name__))
text = resources.files('hermes_tavern').joinpath('plugin.yaml').read_text(encoding='utf-8')
ctx = Ctx(); hermes_tavern.register(ctx)
assert 'entry_point: "hermes_tavern:register"' in text
assert ctx.hooks == [('pre_gateway_dispatch', 'hermes_tavern.gateway_hook', 'pre_gateway_dispatch')]
print('hermes-tavern packaging smoke: PASS')
PY
```

The package also exposes a pip entry point for Hermes plugin discovery:

```toml
[project.entry-points."hermes_agent.plugins"]
hermes-tavern = "hermes_tavern"
```

Enable it in the active Hermes profile after install:

```bash
hermes plugins enable hermes-tavern
```

After enablement, start or reload the Gateway at an operator-chosen maintenance
point so plugin discovery can pick up the package.

## Dependencies

- Hermes Agent at runtime for the plugin loader and gateway hooks.
- Optional provider/runtime integrations such as ComfyUI, TTS, and model
  providers are configured in Hermes/Tavern commands; registration itself does
  not call the network.
- The patches in `patches/` may need to be applied to a compatible hermes-agent version.
