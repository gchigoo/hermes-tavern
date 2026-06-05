# Hermes Tavern Design

> **Product:** Hermes Tavern / hermes-rp
>
> **Goal:** Build a polished Hermes Agent plugin for SillyTavern-compatible roleplay, long-form fiction, and consenting-adult fictional writing through Hermes gateways, especially Telegram.
>
> **Status:** Design v0.1
>
> **Primary implementation target:** `$HERMES_HOME/plugins/hermes-tavern/`

---

## 1. Product Positioning

Hermes Tavern is not a clone of the SillyTavern web UI.

Hermes Tavern is a **SillyTavern-compatible RP / Novel / Adult Fiction runtime for Hermes Gateway**.

It takes the strongest parts of the SillyTavern ecosystem:

- character cards
- presets
- lorebooks / world info
- personas
- macros
- prompt manager concepts
- context templates
- author notes
- chat vectorization
- summarization
- media extensions

and turns them into a Hermes-native experience:

- Telegram-first mobile interaction
- Feishu / Discord / other gateway support later
- Hermes plugin isolation
- Hermes provider/model routing
- Hermes memory and tool ecosystem
- RP session isolation from ordinary assistant sessions
- long-form novel state management
- adult-fiction content modes with explicit boundaries

The product should feel like a **mobile-native power-user writing cockpit**, not a toy bot.

---

## 2. Goals and Non-goals

### 2.1 Goals

1. **Gateway-first RP UX**
   - Use Telegram as the primary interface.
   - Avoid requiring the user to expose a SillyTavern web UI through Cloudflare, Tailscale, LAN ports, or Android/Tauri variants.

2. **SillyTavern asset compatibility**
   - Import and export ST character cards.
   - Import and normalize ST presets.
   - Import and evaluate ST lorebooks/world info.
   - Preserve raw imported data for round-trip export where possible.

3. **Power-user prompt control**
   - Build a modular Prompt Compiler inspired by ST Prompt Manager.
   - Support inspectable prompt order, prompt roles, prompt positions, depth, triggers, macros, and debug output.

4. **Long-form fiction support**
   - Support projects, chapters, scenes, outlines, canon, timeline, summaries, relationship state, character states, and retrieval memory.
   - Avoid relying on infinite context.

5. **Adult fictional writing support**
   - Support clearly fictional consenting-adult content modes.
   - Route to suitable user-configured models instead of trying to force restricted providers.
   - Keep boundaries explicit and inspectable.

6. **Session isolation**
   - RP state, personas, and adult-writing preferences must not pollute the normal Hermes assistant memory or conversation state.

7. **Debuggability**
   - Power users must be able to answer: “Why did the model say this?”
   - Provide context, prompt, lore, memory, and routing debug commands.

### 2.2 Non-goals

1. **Not a jailbreak manager**
   - Do not build features whose purpose is bypassing a third-party provider’s safety policies.
   - Imported presets may contain arbitrary text, but Hermes Tavern should not label, optimize, or auto-generate jailbreaks.

2. **Not a full SillyTavern web UI clone**
   - No need to replicate every ST panel or setting visually.
   - The interface should be command-driven and gateway-native.

3. **Not a general Hermes replacement**
   - Ordinary user requests should still go to normal Hermes unless the user is inside an active RP session or uses `/rp` commands.

4. **Not a single-model system**
   - The design assumes multiple model profiles: RP, adult fiction, summarization, memory extraction, image prompt generation, etc.

---

## 3. Reference Inputs

This design is informed by:

1. **SillyTavern official docs**
   - What is SillyTavern?
   - Quick Start
   - API Connections
   - Prompts
   - Prompt Manager
   - Context Template
   - World Info
   - Character Design
   - Personas
   - Macros
   - Author’s Note
   - Chat Vectorization
   - Summarize
   - Regex
   - Image Generation
   - TTS
   - Extensions

2. **OpenClaw Tavern**
   - `/rp` command namespace
   - ST card/preset/lore compatibility
   - Telegram/Discord channel support
   - RP session persistence
   - long-term memory ideas

3. **Community ST workflows**
   - Typical path: install ST → connect API → import preset → import card → install useful extensions → chat.
   - Presets and cards are the practical quality levers.
   - Mobile access is painful in ST; Hermes Gateway can solve this directly.

4. **User-provided ST preset material**
   - Valuable for module structure, prompt ordering, writing controls, anti-OOC controls, scene pacing, narrator behavior, and long-form conventions.
   - Not used as a source of jailbreak behavior.

---

## 4. Architecture Overview

### 4.1 High-level flow

```text
Telegram / Gateway event
  ↓
pre_gateway_dispatch hook
  ↓
Hermes Tavern Router
  ├─ /rp command? → Command Handler
  ├─ active RP session? → Session Runtime
  └─ otherwise → allow normal Hermes dispatch

Session Runtime
  ↓
Load session + project + card + persona + preset + lorebooks
  ↓
Lorebook Matcher
  ↓
Memory Retriever
  ↓
Context Budget Manager
  ↓
Prompt Compiler
  ├─ Chat renderer
  └─ Text/story-string renderer
  ↓
Model Router
  ↓
Provider call
  ↓
Post-processors
  ↓
Persist message + memory events
  ↓
Gateway reply
```

### 4.2 Plugin-first implementation

Prefer a user plugin:

```text
$HERMES_HOME/plugins/hermes-tavern/
├── plugin.yaml
├── __init__.py
├── db.py
├── models.py
├── commands.py
├── gateway_hook.py
├── runtime.py
├── prompt_compiler.py
├── macro_engine.py
├── lorebook.py
├── memory.py
├── model_router.py
├── importers/
│   ├── cards.py
│   ├── presets.py
│   └── lorebooks.py
├── exporters/
│   ├── cards.py
│   ├── chats.py
│   └── projects.py
└── tests/
```

Core Hermes changes should be avoided unless a generic plugin hook is missing.

---

## 5. Gateway UX

### 5.1 Main command namespace

Use `/rp` as the stable namespace.

Examples:

```text
/rp help
/rp status
/rp start <card>
/rp pause
/rp resume
/rp end
/rp retry
/rp regen
/rp swipe
/rp debug prompt
/rp debug context
/rp export
```

### 5.2 Active-session behavior

If a chat/user has an active RP session:

- ordinary messages go to the RP runtime, not normal Hermes;
- `/rp` commands control the session;
- `/rp end` exits and returns the chat to normal Hermes behavior.

The plugin must return:

```python
{"action": "skip", "reason": "hermes-tavern handled message"}
```

after it handles a message, so the normal assistant does not also answer.

### 5.3 Session identity

Session keys must include:

```text
platform
chat_id
thread_id / topic_id if available
user_id
session_id
```

This avoids collisions between Telegram, Feishu, Discord, group chats, and topics.

---

## 6. Core Domain Objects

### 6.1 Asset Library

Hermes Tavern should treat these as first-class assets:

```text
cards
presets
lorebooks
personas
context templates
model profiles
projects
sessions
messages
summaries
memory facts
media assets
```

### 6.2 Character Card

Support ST V1/V2 JSON and PNG metadata.

Canonical fields:

```yaml
card:
  id: uuid
  name: string
  description: text
  personality: text
  scenario: text
  first_mes: text
  alternate_greetings: list[text]
  mes_example: text
  creator_notes: text
  system_prompt_override: text
  post_history_instructions: text
  tags: list[string]
  talkativeness: number
  extensions: json
  raw_json: json
  source_path: string
  created_at: datetime
  updated_at: datetime
```

Commands:

```text
/rp card import <attachment|url|path>
/rp card list
/rp card search <query>
/rp card inspect <card>
/rp card start <card>
/rp card greeting <card>
/rp card export <card>
```

### 6.3 Persona

Personas represent user-side identities and narrator modes.

```yaml
persona:
  id: uuid
  name: string
  description: text
  default: bool
  locked_to_card_id: uuid|null
  locked_to_session_id: uuid|null
  tags: list[string]
```

Commands:

```text
/rp persona list
/rp persona new <name>
/rp persona use <name>
/rp persona inspect <name>
/rp persona lock chat
/rp persona lock card
/rp persona temp <description>
```

### 6.4 Preset

An imported ST preset should be normalized into prompt modules, model defaults, context settings, and generation settings.

```yaml
preset:
  id: uuid
  name: string
  source: sillytavern|native|custom
  prompt_modules: list[PromptModule]
  generation_settings: GenerationSettings
  context_settings: ContextSettings
  raw_json: json
```

### 6.5 Prompt Module

```yaml
prompt_module:
  id: uuid
  preset_id: uuid
  name: string
  role: system|user|assistant|none
  content: text
  enabled: bool
  trigger: always|new_chat|continue|group|manual|conditional
  position: system|before_char|after_char|before_history|after_history|post_history|prefill
  depth: int|null
  order: int
  token_budget: int|null
  exclusive_group: string|null
  tags: list[string]
  source_metadata: json
```

Commands:

```text
/rp preset import <attachment|url|path>
/rp preset list
/rp preset use <name>
/rp prompt list
/rp prompt inspect <module>
/rp prompt enable <module>
/rp prompt disable <module>
/rp prompt move <module> --position before_history --order 20
/rp prompt debug
```

### 6.6 Lorebook / World Info

Lorebooks are dynamic retrieval and injection systems.

Canonical entry fields:

```yaml
lorebook_entry:
  id: uuid
  lorebook_id: uuid
  enabled: bool
  title: string
  comment: text
  content: text
  keys: list[string]
  secondary_keys: list[string]
  filter_logic: any|all|not_any|not_all
  regex_enabled: bool
  case_sensitive: bool
  match_whole_words: bool
  constant: bool
  insertion_position: before_char|after_char|before_history|after_history|post_history|author_note
  insertion_order: int
  priority: int
  probability: float
  group_name: string|null
  group_scoring: max|sum|first|null
  character_filter: json|null
  scan_depth: int
  recursive_enabled: bool
  recursion_level: int
  timed_effect: json|null
  vector_enabled: bool
  budget_weight: float
```

Commands:

```text
/rp lore import <attachment|url|path>
/rp lore list
/rp lore use <name>
/rp lore inspect <entry>
/rp lore enable <entry>
/rp lore disable <entry>
/rp lore test <message>
/rp lore debug
```

Current matcher behavior:

- Lorebook imports preserve raw ST lore keys and flags.
- Runtime matching now applies a local pre-search regex complexity guard when `regex_enabled` entries are evaluated.
- `regex` lore keys longer than 256 characters or with nested quantifier patterns are excluded before `re.search`, and exclusion reasons are surfaced in `/rp lore test`/`/rp lore debug`.
- Regex compile failures remain surfaced as `regex error:` and do not crash matching.
- The guard is matcher/runtime-only and does not mutate imported lorebook data.

### 6.7 Project / Novel

Long-form writing requires a project layer above chat sessions.

```yaml
project:
  id: int
  title: string
  summary: text
  status: draft|in_progress|complete
```

Project Brief v1 makes `type` and `premise` current local metadata for novel
projects: they are persisted in `novel_project_briefs.project_type` and
`novel_project_briefs.premise_text`, visible through `/rp project brief ...`,
`/rp project info`, and project Markdown export. These fields are informational
only and do not feed prompt assembly, provider routing, content mode, or
generation behavior. `style_guide` remains current Phase 124 project-scope
behavior.

Project Outline v1 adds `outline` as a simple local metadata text stored in
`novel_project_outlines.outline_text`, visible through `/rp project outline ...`,
`/rp project info`, and project Markdown export. This outline text is also
informational only and does not feed prompt assembly, provider routing, content
mode, or generation behavior.

Location Metadata v1 adds local project-scoped location rows as plain scene
environment metadata through `/rp location ...`, persisted in
`novel_locations(id, project_id, label, description_text, created_at, updated_at)`.
Location rows are local notes only and do not imply maps, address parsing,
coordinates, or asset bindings.

Organization Metadata v1 adds local project-scoped organization rows as plain
organizational notes through `/rp organization ...`, persisted in
`novel_organizations(id, project_id, label, description_text, created_at, updated_at)`.
Organization rows are local notes only and do not imply hierarchy, membership,
affiliations, or bindings.

Default Binding Metadata v1 includes command-managed default-binding metadata via
`novel_default_bindings` (for `project`/`chapter`/`scene` scope + one of
`card`/`preset`/`lorebook`/`persona` assets) and export visibility only. The
scalar defaults `default_card_id`, `default_preset_id`, and `default_lorebook_ids`
remain deferred; automatic default application is explicitly out of scope.
`canon_policy` and `content_mode` remain deferred.
ST card/preset/lorebook/persona importer/exporter compatibility remains unchanged.

Relationship state is now current local metadata and is managed through
`novel_relationship_states(id, project_id, label, state_text, created_at, updated_at)`.

Character state is also now current local metadata and is managed through
`novel_character_states(id, project_id, label, state_text, created_at, updated_at)`.

Location metadata is also now current local metadata and is managed through
`novel_locations(id, project_id, label, description_text, created_at, updated_at)`.

Organization metadata is also now current local metadata and is managed through
`novel_organizations(id, project_id, label, description_text, created_at, updated_at)`.

Plot threads are now current local metadata and are managed through
`novel_plot_threads(id, project_id, label, description_text, created_at, updated_at)`.

Style samples are now current local metadata and are managed through
`novel_style_samples(id, project_id, label, sample_text, created_at, updated_at)`.

Scene Beat Metadata v1 is current local scene-scoped metadata and is managed
through `/rp scene beat add/list/inspect/update/delete`, persisted in
`novel_scene_beats(id, scene_id, label, beat_text, created_at, updated_at)`.
Scene beats are command/export visible only, scene-local, and intentionally omit
any automatic sequencing or generation behavior.

Default-binding metadata, relationship state, character state, location,
organization, plot-thread, style-sample metadata, and scene beats are
informational-only:
they do not participate in prompt module injection, provider routing, context
budget reporting, vectorization/retrieval, content-mode behavior, credential
persistence, automation/summarization, or generation.

Sub-objects:

```text
chapters
scenes
canon facts
timeline events
character states
relationships
locations
organizations
plot threads
style samples
scene beats
```

Scene objects include:

```text
goal text
beat label + beat text
POV label
tense: past|present
```

Remaining deferred sub-objects from the original vision are relationship
graph/rename/automatic extraction.

Commands:

```text
/rp project create <title>
/rp project list
/rp project info <id>
/rp project set <id>
/rp project export [id]
/rp project style [project-id]
/rp project style inspect [project-id]
/rp project style set [project-id] <text>
/rp project style clear [project-id]
/rp project brief [project-id]
/rp project brief inspect [project-id]
/rp project brief type set <project-id> <novel|serial|rp|worldbuilding|other>
/rp project brief type clear <project-id>
/rp project brief premise set <project-id> <text>
/rp project brief premise clear <project-id>
/rp project outline [project-id]
/rp project outline inspect [project-id]
/rp project outline set [project-id] <text>
/rp project outline clear [project-id]
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
/rp location add <project-id> <label> <description...>
/rp location list [project-id]
/rp location inspect <location-id>
/rp location update <location-id> <description...>
/rp location delete <location-id>
/rp organization add <project-id> <label> <description...>
/rp organization list [project-id]
/rp organization inspect <organization-id>
/rp organization update <organization-id> <description...>
/rp organization delete <organization-id>
/rp plot thread add <project-id> <label> <description...>
/rp plot thread list [project-id]
/rp plot thread inspect <plot-thread-id>
/rp plot thread update <plot-thread-id> <description...>
/rp plot thread delete <plot-thread-id>
/rp style sample add <project-id> <label> <sample...>
/rp style sample list [project-id]
/rp style sample inspect <style-sample-id>
/rp style sample update <style-sample-id> <sample...>
/rp style sample delete <style-sample-id>
/rp chapter create [project-id] <title>
/rp chapter list [project-id]
/rp chapter summary <chapter-id> [text]
/rp chapter summary clear <chapter-id>
/rp scene create <chapter-id> <title>
/rp scene list <chapter-id>
/rp scene start <scene-id>
/rp scene summary <scene-id> [text]
/rp scene summary clear <scene-id>
/rp scene goal <scene-id> [text]
/rp scene goal clear <scene-id>
/rp scene narration <scene-id>
/rp scene narration clear <scene-id>
/rp scene narration pov <scene-id> <label>
/rp scene narration tense <scene-id> <past|present>
/rp scene beat add <scene-id> <label> <beat...>
/rp scene beat list <scene-id>
/rp scene beat inspect <beat-id>
/rp scene beat update <beat-id> <beat...>
/rp scene beat delete <beat-id>
/rp canon add <project-id> <title> <content>
/rp canon list [project-id] [group]
/rp canon group [project-id] <group>
/rp timeline add <project-id> <date> <title> [description]
/rp timeline list [project-id]
```

Project Markdown export emits `## Project Brief` after `## Summary` and, when
present, emits `## Outline` immediately after Project Brief and before Style
Guide. Project Brief and Outline content are omitted when empty. Project Brief
labels are `Type:` and `Premise:`, and blank field labels are omitted. Location
metadata is exported as optional `## Locations` immediately after Style Guide
when at least one location row exists.
`## Organizations` is exported as an optional section immediately after
`## Locations` when organization rows exist. If no Locations section exists, it
falls back to being emitted after Project Brief, Outline, and Style Guide (when present)
before `## Characters`, `## Relationships`, and `## Chapters`.
`## Locations` and `## Organizations` are omitted when empty.
Character-state metadata is exported as optional `## Characters` after
`## Organizations`/`## Locations` and before `## Relationships` when rows exist.
Relationship-state metadata is exported as optional `## Relationships` after
Characters/Organizations/Locations and before `## Chapters` when rows exist.
Each metadata section is omitted when empty. Chapter and scene summaries are
metadata-only: they are emitted as `Summary:` lines directly under chapter and
scene headings in the same export pass. Blank or
whitespace-only summary values are omitted.

---

## 7. Prompt Compiler

### 7.1 Purpose

The Prompt Compiler is the heart of Hermes Tavern.

It converts domain state into model input:

```text
session + project + card + persona + preset + lore + memory + recent messages
→ final model prompt
```

### 7.2 Two renderers

Hermes Tavern must preserve the ST distinction between chat completions and text completions.

```python
PromptCompiler.render_chat_messages(context) -> list[dict]
PromptCompiler.render_story_string(context) -> str
```

Chat renderer output:

```python
[
  {"role": "system", "content": "..."},
  {"role": "user", "content": "..."},
  {"role": "assistant", "content": "..."},
]
```

Text renderer output:

```text
<system/context preamble>
<character description>
<world info>
<chat history>
{{char}}:
```

### 7.3 Prompt assembly layers

Recommended order:

1. Runtime policy / boundaries
2. Model-format adapter instructions
3. Content mode module
4. Project style guide
5. Character card fields
6. Persona fields
7. Scenario
8. Lorebook entries
9. Author’s note / scene directive
10. Memory summaries
11. Retrieved memories
12. Recent chat history
13. Post-history instructions
14. Prefill / continuation nudge

Exact ordering should be preset-configurable and debuggable.

### 7.4 Prompt debug output

`/rp debug prompt` should show:

```text
model profile selected
renderer selected: chat|text
context window
estimated tokens
included modules
excluded modules and reasons
included lore entries
included memories
recent history range
final prompt preview
```

---

## 8. Macro Engine

### 8.1 Initial compatibility subset

Support common ST-style macros:

```text
{{char}}
{{user}}
{{persona}}
{{description}}
{{personality}}
{{scenario}}
{{system}}
{{mesExamples}}
{{lastMessage}}
{{date}}
{{time}}
{{random::a::b::c}}
{{getvar::name}}
{{setvar::name::value}}
```

### 8.2 Future compatibility

Later versions can support:

- scoped variables
- conditionals
- nested macros
- whitespace control
- arrays/lists
- custom plugin macros

### 8.3 Safety rule

Macros are template expansion, not code execution.

No arbitrary Python, shell, JavaScript, or tool execution from imported assets.

---

## 9. Context Budget Manager

Long-form fiction fails if every asset is blindly injected.

The budget manager should allocate context across layers:

```yaml
context_budget:
  total_tokens: model_context_window
  reserved_for_output: 2048
  runtime_policy: 800
  card: 2000
  persona: 800
  lorebook: 6000
  memory: 6000
  summaries: 4000
  recent_history: dynamic
  author_note: 800
  post_history: 800
```

Responsibilities:

- estimate tokens;
- select recent history range;
- trim or summarize older context;
- enforce lorebook budget;
- detect overflow;
- explain why items were excluded.

Current Phase 126 v1 status:

- `/rp debug context [limit] [page]` is implemented as read-only debug reporting.
- The command renders shallow prompt compilation diagnostics and row-level token
  estimates without changing prompt assembly or generation behavior.
- Budget enforcement, prompt trimming, summarization, vectorization,
  provider-specific tokenizer usage, provider/model routing, and broader context
  enforcement remain future/deferred boundaries.

Command:

```text
/rp debug context
```

---

## 10. Memory Engine

### 10.1 Memory types

Hermes Tavern memory must be separate from ordinary Hermes memory.

Recommended memory types:

```text
raw messages
rolling session summary
scene summary
chapter summary
project summary
canon facts
character state
relationship state
location metadata
timeline events
retrieval snippets
style samples
user preferences for this project
```

Relationship-state, character-state, location, organization, plot-thread, and
style-sample metadata are command-managed local state only. They are
intentionally outside automatic memory extraction, update-cycle output,
vectorization/retrieval indexing, scheduled summarization inputs, automation,
and generation/similar refresh cycles.

### 10.2 Update cycle

After each assistant turn:

1. save raw messages;
2. detect memory-worthy facts;
3. update volatile state if needed;
4. schedule summarization if history crosses threshold;
5. update vector index if enabled;
6. Relationship-state, character-state, location, organization, plot-thread, and
   style-sample metadata are excluded from this cycle; they are updated only via
   `/rp relationship ...`, `/rp character state ...`, `/rp location ...`,
   `/rp organization ...`, `/rp plot thread ...`, and `/rp style sample ...`
   commands.

### 10.3 Summarization profiles

Use cheaper or specialized model profiles:

```yaml
memory_extract:
  task: extract facts / state changes
  model_profile: summarizer_fast

scene_summarize:
  task: summarize current scene
  model_profile: summarizer_quality

canon_reconcile:
  task: detect contradictions
  model_profile: reasoning_model
```

Commands:

```text
/rp memory summary
/rp memory search <query>
/rp memory add <fact>
/rp memory pin <fact>
/rp memory forget <id>
/rp debug memory
```

---

## 11. Model Router

### 11.1 Model profiles

Do not hard-code one model.

```yaml
model_profile:
  id: rp_default
  provider: openrouter
  model: example/model
  mode: chat|completion
  context_window: 128000
  temperature: 0.9
  top_p: 0.95
  max_tokens: 2048
  stop_strings: []
  supports_images: false
  supports_tools: false
  content_modes: [safe, mature]
```

### 11.2 Routing tasks

Separate model profiles for:

```text
rp_reply
adult_fiction_reply
novel_continuation
summarization
memory_extraction
canon_check
lorebook_vectorization
image_prompt_generation
tts_script_cleanup
```

### 11.3 Adult-fiction routing principle

For adult fictional writing, prefer routing to a model/profile selected by the user for that content mode.

Do not rely on jailbreak attempts against restricted models.

Commands:

```text
/rp model profile list
/rp model profile use <name>
/rp model route show
/rp model test <profile>
```

---

## 12. Adult Fiction Mode

### 12.1 Purpose

Hermes Tavern should support fiction for adults, including mature themes and explicit consenting-adult content, without hiding the behavior inside jailbreak prompts.

### 12.2 Content modes

```text
safe      general audience / low-risk roleplay
mature    adult themes, non-explicit
explicit  consenting-adult erotic fiction where allowed by selected model/provider
dark      fictional dark themes with stricter boundary checks
custom    user-defined mode with explicit config
```

### 12.3 Non-negotiable boundaries

Hermes Tavern must not assist with:

- sexual content involving minors or ambiguous age;
- real-person sexual fabrication or non-consensual deepfake-style content;
- instructions for real-world abuse, exploitation, coercion, or trafficking;
- evading a third-party provider’s safety system;
- turning imported jailbreak text into optimized bypass prompts.

### 12.4 Product behavior

The plugin should support:

- project-level content mode;
- session-level content mode;
- model profile compatibility check;
- clear error when selected model refuses or is unsuitable;
- suggestion to choose an appropriate user-configured model profile rather than trying to bypass the provider.

Commands:

```text
/rp mode safe
/rp mode mature
/rp mode explicit
/rp mode dark
/rp mode show
```

---

## 13. Novel Engine

### 13.1 Why this exists

A long novel is not just a long chat. It requires stable state.

Hermes Tavern should model:

```text
project
chapter
scene
timeline
canon
character states
relationship states
location notes
organization notes
plot threads
style samples
scene beats
```

Future novel-engine dimensions remain deferred: volume/arc, location map/
geocode derivatives, revision notes, relationship graph/rename/automatic
extraction.

### 13.2 Writing commands

```text
/rp project create/list/info/set/export
/rp project style [project-id]
/rp project style inspect [project-id]
/rp project style set [project-id] <text>
/rp project style clear [project-id]
/rp project brief [project-id]
/rp project brief inspect [project-id]
/rp project brief type set <project-id> <novel|serial|rp|worldbuilding|other>
/rp project brief type clear <project-id>
/rp project brief premise set <project-id> <text>
/rp project brief premise clear <project-id>
/rp project outline [project-id]
/rp project outline inspect [project-id]
/rp project outline set [project-id] <text>
/rp project outline clear [project-id]
/rp character state add <project-id> <label> <state...>
/rp character state list [project-id]
/rp character state inspect <character-state-id>
/rp character state update <character-state-id> <state...>
/rp character state delete <character-state-id>
/rp location add <project-id> <label> <description...>
/rp location list [project-id]
/rp location inspect <location-id>
/rp location update <location-id> <description...>
/rp location delete <location-id>
/rp organization add <project-id> <label> <description...>
/rp organization list [project-id]
/rp organization inspect <organization-id>
/rp organization update <organization-id> <description...>
/rp organization delete <organization-id>
/rp plot thread add <project-id> <label> <description...>
/rp plot thread list [project-id]
/rp plot thread inspect <plot-thread-id>
/rp plot thread update <plot-thread-id> <description...>
/rp plot thread delete <plot-thread-id>
/rp style sample add <project-id> <label> <sample...>
/rp style sample list [project-id]
/rp style sample inspect <style-sample-id>
/rp style sample update <style-sample-id> <sample...>
/rp style sample delete <style-sample-id>
/rp relationship add <project-id> <label> <state...>
/rp relationship list [project-id]
/rp relationship inspect <relationship-id>
/rp relationship update <relationship-id> <state...>
/rp relationship delete <relationship-id>
/rp chapter create/list
/rp chapter summary <chapter-id> [text]
/rp chapter summary clear <chapter-id>
/rp scene create/list/start
/rp scene summary <scene-id> [text]
/rp scene summary clear <scene-id>
/rp scene goal <scene-id> [text]
/rp scene goal clear <scene-id>
/rp scene narration <scene-id>
/rp scene narration clear <scene-id>
/rp scene narration pov <scene-id> <label>
/rp scene narration tense <scene-id> <past|present>
/rp scene beat add <scene-id> <label> <beat...>
/rp scene beat list <scene-id>
/rp scene beat inspect <beat-id>
/rp scene beat update <beat-id> <beat...>
/rp scene beat delete <beat-id>
/rp canon add/list/group
/rp timeline add/list
```

Project Brief and Project Outline commands are metadata-only. They expose local
project metadata for inspection/info/export, not prompt injection, content-mode
changes, provider selection, or generation control.
Chapter and scene summaries are metadata-only and local-only: command-driven
metadata for prose visibility and export, no model/provider/routing side effect.
Character-state metadata is command-driven local-only: it is surfaced for
inspection/list/update/delete and optional Markdown export, and is excluded from
prompt/debug, context-budget reporting, retrieval/vectorization, provider/model
routing, content-mode decisions, credentials, and generation.
Location metadata is command-driven local-only: it is surfaced for
add/inspect/list/update/delete, optional Markdown export, and is excluded from
prompt/debug, context-budget reporting, retrieval/vectorization, provider/model
routing, content-mode decisions, credentials, and generation.
Organization metadata is command-driven local-only: it is surfaced for
add/inspect/list/update/delete, optional Markdown export, and is excluded from
prompt/debug, context-budget reporting, retrieval/vectorization, provider/model
routing, content-mode decisions, credentials, and generation.
Plot-thread metadata is command-driven local-only: it is surfaced for
add/list/inspect/update/delete, optional Markdown export, and is excluded from
prompt/debug, context-budget reporting, retrieval/vectorization, provider/model
routing, content-mode decisions, credentials, and generation.
Style-sample metadata is command-driven local-only: it is surfaced for
add/list/inspect/update/delete, optional Markdown export, and is excluded from
prompt/debug, context-budget reporting, retrieval/vectorization, provider/model
routing, content-mode decisions, credentials, and generation.
Scene-beat metadata is command-driven local-only: it is surfaced for
add/list/inspect/update/delete, optional owning-scene Markdown export, and is
excluded from prompt/debug, context-budget reporting, retrieval/vectorization,
provider/model routing, content-mode decisions, credentials, generation, media,
archive, graph, automatic extraction, and safety behavior.
Relationship state is metadata-only and local-only: command-driven relationship
notes for inspection/list/update/delete and optional Markdown export, no prompt,
context-budget, retrieval/vectorization, provider/model/routing, content-mode,
credential, or generation side effect.

Future writing commands from the original vision remain deferred: outline
generation/rewrite/expand/compress workflows, project archive
ZIP/export/import, and relationship graph/rename/automatic extraction.

### 13.3 Canon management

Commands:

```text
/rp canon add <project-id> <title> <content>
/rp canon list [project-id] [group]
/rp canon group [project-id] <group>
```

Canon check/correlation tools are deferred; only add/list/group are included in Phase 9.
Future canon commands from the original vision remain deferred: `/rp canon check`,
`/rp canon conflict`, and `/rp canon pin <fact>`.

Cross-cutting deferred novel constraints remain explicit in this slice:
relationship graph/rename/automatic extraction, project archive ZIP/import
workflows, automatic default-binding application and scalar default fields,
canon-policy/content-mode metadata, provider routing, generation side effects,
retrieval/vectorization/automation coupling, archive ZIP/import/export workflows,
cloud collaboration, no provider credential persistence, no minors/underage
handling, and no provider safety bypass pathways.

---

## 14. Post-processing and Regex Hooks

Inspired by ST Regex extension.

Use cases:

- clean unwanted prefixes;
- normalize markdown;
- strip accidental assistant meta-commentary;
- enforce message format;
- convert custom blocks to Telegram-friendly formatting;
- split long replies into multiple gateway messages.

Canonical hook:

```python
postprocess(response, session_context) -> PostprocessResult
```

Commands:

```text
/rp regex list
/rp regex add
/rp regex enable
/rp regex disable
/rp debug postprocess
```

Phase 125 is intentionally separate from ST Regex-style output post-processing and does not implement `/rp regex` output rewrite hooks, postprocessing output mutation, or extension hook response rewrites.

---

## 15. Media Extensions

### 15.1 TTS

Integrate with Hermes TTS providers.

Commands:

```text
/rp tts on
/rp tts off
/rp voice <text>
```

### 15.2 Image generation

Image generation should be optional and routed through Hermes image tools or configured providers.

Commands:

```text
/rp image prompt
/rp image scene
/rp image character
```

### 15.3 Future media features

- expression images / sprites;
- character portraits;
- scene moodboards;
- video snippets;
- audio ambiance;
- captioning uploaded images.

---

## 16. SQLite Data Model

Use SQLite under plugin data directory:

```text
$HERMES_HOME/plugins/hermes-tavern/data/tavern.sqlite3
```

Use `get_hermes_home()`; never hard-code `~/.hermes`.

### 16.1 Tables

Recommended initial tables:

```text
assets
cards
presets
prompt_modules
lorebooks
lorebook_entries
personas
model_profiles
novel_projects
novel_project_outlines
novel_project_briefs
novel_chapters
novel_scenes
novel_scene_goals
sessions
messages
swipes
summaries
memory_facts
novel_canon
novel_timeline
novel_character_states
novel_relationship_states
novel_locations
novel_organizations
novel_plot_threads
novel_style_samples
media_assets
settings
```

Current Project Brief table:
`novel_project_briefs(id, project_id, project_type, premise_text, created_at, updated_at)`,
with `project_id UNIQUE REFERENCES novel_projects(id) ON DELETE CASCADE` and
`idx_novel_project_briefs_project ON novel_project_briefs(project_id)`.

Current Project Outline table:
`novel_project_outlines(id, project_id, outline_text, created_at, updated_at)`,
with `project_id UNIQUE REFERENCES novel_projects(id) ON DELETE CASCADE` and
`idx_novel_project_outlines_project ON novel_project_outlines(project_id)`.

Current chapter/scene summary metadata:
`novel_chapters.summary` and `novel_scenes.summary` are reused by Phase 129 for
local chapter/scene summary commands and Markdown export visibility.

Current character-state metadata table:
`novel_character_states(id, project_id, label, state_text, created_at, updated_at)`,
with `project_id REFERENCES novel_projects(id) ON DELETE CASCADE` and
`idx_novel_character_states_project ON novel_character_states(project_id)`.

Current location metadata table:
`novel_locations(id, project_id, label, description_text, created_at, updated_at)`,
with `project_id REFERENCES novel_projects(id) ON DELETE CASCADE` and
`idx_novel_locations_project ON novel_locations(project_id)`.

Current organization metadata table:
`novel_organizations(id, project_id, label, description_text, created_at, updated_at)`,
with `project_id REFERENCES novel_projects(id) ON DELETE CASCADE` and
`idx_novel_organizations_project ON novel_organizations(project_id)`.

Current style-sample metadata table:
`novel_style_samples(id, project_id, label, sample_text, created_at, updated_at)`,
with `project_id REFERENCES novel_projects(id) ON DELETE CASCADE` and
`idx_novel_style_samples_project ON novel_style_samples(project_id)`.

### 16.2 Message table

```sql
messages (
  id TEXT PRIMARY KEY,
  session_id TEXT NOT NULL,
  role TEXT NOT NULL,
  content TEXT NOT NULL,
  created_at TEXT NOT NULL,
  token_estimate INTEGER,
  parent_message_id TEXT,
  swipe_group_id TEXT,
  metadata_json TEXT
)
```

### 16.3 Swipe support

SillyTavern-style alternate assistant responses should be modeled explicitly.

```text
swipe_group_id
selected_swipe_index
```

Commands:

```text
/rp swipe list
/rp swipe next
/rp swipe prev
/rp swipe select <n>
/rp regen
```

---

## 17. Import / Export

### 17.1 Importers

Required importers:

```text
ST character JSON
ST character PNG metadata
ST preset JSON
ST lorebook/world info JSON
```

Hermes Tavern native project archives are deferred; the current Phase 121–138
implementation provides Markdown export only, not project/novel import.
Relationship-state, character-state, location, organization, plot-thread, and
style-sample rows, plus scene-beat rows, remain local metadata and are not bound
to ST card objects in this phase.

Later:

```text
ST chat logs
RisuAI cards if compatible
Chub-style cards if compatible
Markdown novel projects
```

### 17.2 Exporters

Required exporters:

```text
card export JSON
preset export JSON/native
lorebook export JSON
chat export JSONL
novel export Markdown
```

Project archive ZIP remains a future exporter/importer; current Phase 121–138 writes
local Markdown via `/rp project export [id]`.
Project Brief and Project Outline are exported as optional top-level `## Project Brief`
and `## Outline` sections after `## Summary` when non-empty. Project style guides
are exported as a top-level `## Style Guide` section after optional Project Brief
and Outline when non-empty. `## Style Samples` appears after `## Style Guide` when
present, or after Project Brief/Outline when no Style Guide is present, before
`## Locations`, `## Organizations`, `## Plot Threads`, `## Characters`,
`## Relationships`, and `## Chapters`. `## Style Samples` is omitted when no
style-sample rows exist.
`## Default Bindings` appears after `## Relationships` and before `## Chapters`,
and is omitted when no default-binding rows exist.
`## Locations` appears after Style Samples when present; otherwise it follows
the post-Style Guide / Project Brief / Project Outline placement. When at least
one location row exists, this section is emitted before Organizations,
Characters, Relationships, and Chapters; it is omitted when empty.
`## Organizations` appears after Locations when present, or after Project Brief,
Outline, and Style Guide/Style Samples fallback placement when no Locations section
exists, before Characters, Relationships, and Chapters. `## Organizations` is
omitted when empty.
`## Plot Threads` appears after Organizations when present, or after Project
Brief, Outline, Style Guide, and Style Samples fallback placement otherwise, before
Characters, Relationships, and Chapters. It is omitted when empty.
`## Characters` appears after Locations/Organizations when at least one
character-state row exists, before `## Relationships`; both sections are omitted
when empty. `## Relationships` is exported after Locations/Organizations/Characters
and before Chapters when at least one relationship-state row exists; it is omitted
when empty.
Chapter summaries are exported as `Summary: <text>` immediately under chapter headings
when non-empty.
Scene summaries are exported as `Summary: <text>` immediately under scene headings,
before scene goal, narration controls, and session content, and whitespace-only
summaries are omitted.
Scene goals are exported in Markdown directly under the relevant scene heading
as `Goal: <text>`, when set.
Scene beats are exported for the owning scene as bullet lines:
`- <label>: <beat_text>`. They are omitted when no beats exist and appear
after `Goal:` (if present) and before narration controls/session content.
Scene narration controls are also exported under scene headings with only
non-empty fields:
- `Scene narration controls:`
- `POV: <text>`
- `Tense: <past|present>`

Commands:

```text
/rp import <attachment|url|path>
/rp export chat
/rp export project
/rp export markdown
/rp backup
```

Project/novel import is deferred for this phase; only export is implemented.

---

## 18. Extension Hooks

Hermes Tavern should define its own plugin-internal hooks so later features do not become tangled.

```python
before_command(command, context)
after_command(command, result, context)
before_prompt_compile(context)
after_prompt_compile(compiled_prompt, context)
before_model_call(request, context)
after_model_call(response, context)
before_memory_update(turn, context)
after_memory_update(updates, context)
before_gateway_reply(reply, context)
after_gateway_reply(reply, context)
```

Potential future extensions:

- custom lore matchers;
- custom memory extractors;
- extra macro providers;
- custom post-processors;
- image/TTS integrations;
- UI dashboard;
- project analytics.

---

## 19. Debug and Observability

Power-user features require strong debug tools.

Commands:

```text
/rp debug prompt
/rp debug context
/rp debug lore
/rp debug memory
/rp debug model
/rp debug session
/rp debug last
```

Debug output should include:

- selected session;
- selected project;
- selected card;
- selected persona;
- selected preset;
- selected model profile;
- active content mode;
- included prompt modules;
- lore matches;
- memory matches;
- token estimates;
- final rendered prompt preview;
- provider request summary, excluding secrets.

Do not print API keys or secrets.

---

## 20. Testing Strategy

### 20.1 Unit tests

Test pure modules first:

```text
macro expansion
card parsing
preset parsing
lore matching
prompt ordering
context budgeting
model routing
post-processing
```

### 20.2 Integration tests

Use fake gateway events and fake model providers.

Test cases:

```text
/rp command is intercepted
normal message is allowed when no active session exists
active session message is handled and skipped from normal Hermes
card import starts a session
lorebook entry triggers correctly
prompt debug shows expected modules
/rp end returns chat to normal Hermes
```

### 20.3 Golden tests

Maintain fixtures:

```text
tests/fixtures/cards/*.json
tests/fixtures/cards/*.png
tests/fixtures/presets/*.json
tests/fixtures/lorebooks/*.json
tests/golden/prompts/*.txt
```

Golden tests are important because prompt ordering regressions can be subtle.

---

## 21. Implementation Phases

### Phase 0: Repo-ready design package

Deliverables:

- this design document;
- plugin skeleton plan;
- initial schema plan;
- test fixture plan.

### Phase 1: Plugin skeleton and command router

Build:

- `plugin.yaml`
- `__init__.py`
- `gateway_hook.py`
- `/rp help`
- `/rp status`
- `/rp end`
- active session lookup stub

Acceptance:

- `/rp help` is handled by plugin;
- non-RP messages still go to normal Hermes;
- active RP messages can be intercepted.

### Phase 2: SQLite persistence

Build:

- database path handling with `get_hermes_home()`;
- schema migrations;
- sessions table;
- messages table;
- cards table;
- basic settings.

Acceptance:

- plugin creates DB on first use;
- session state survives gateway restart.

### Phase 3: Character card import and start session

Build:

- ST JSON card importer;
- PNG metadata card importer;
- `/rp card import`;
- `/rp card list`;
- `/rp start <card>`.

Acceptance:

- imported card can start a session;
- first greeting is sent;
- messages persist.

### Phase 4: Prompt Compiler v1

Build:

- native prompt modules;
- card/persona/scenario assembly;
- chat renderer;
- `/rp debug prompt`.

Acceptance:

- deterministic compiled prompt;
- debug output explains module order.

### Phase 5: Model Router v1

Build:

- model profile storage;
- default profile resolution;
- route RP replies through selected provider/profile.

Acceptance:

- `/rp model profile use` changes route;
- failed provider calls produce clear user-facing errors.

### Phase 6: Preset import v1

Build:

- ST preset parser;
- prompt module normalization;
- generation settings extraction;
- preset selection.

Acceptance:

- imported preset changes prompt module list;
- unsupported fields are preserved in raw JSON.

### Phase 7: Lorebook v1

Build:

- lorebook import;
- keyword matching;
- regex matching;
- insertion order;
- context budget;
- `/rp lore test`.

Acceptance:

- triggered entries appear in debug context;
- non-triggered entries show exclusion reason.

Phase 7 matcher hardening note:
- `/rp lore test` and `/rp lore debug` now include bounded rejection reasons for regex complexity guard (`pattern too long`, `nested quantifier`) added under Phase 125.
- Acceptance report: `design/codestable/features/2026-06-04-hermes-tavern-phase125-lore-regex-guard/hermes-tavern-phase125-lore-regex-guard-acceptance.md`

### Phase 8: Memory and summaries v1

Build:

- rolling session summary;
- manual memory facts;
- summary trigger by token/message threshold;
- memory debug command.

Acceptance:

- long chats stay within context budget;
- summaries are visible and editable.

### Phase 9: Novel project layer

Build:

- projects;
- chapters;
- scenes;
- canon facts;
- timeline;
- Markdown export.

Acceptance:

- a project can produce chapter/scene structured output;
- canon facts can be injected and debugged.
- Implemented (2026-06-03). Acceptance report: design/codestable/features/2026-06-03-hermes-tavern-phase121-novel-project-layer/hermes-tavern-phase121-novel-project-layer-acceptance.md

### Phase 10: Adult Fiction Mode

Build:

- content mode setting;
- boundaries module;
- model profile compatibility checks;
- clear route errors.

Acceptance:

- content mode is explicit in debug output;
- selected model profile declares supported modes;
- boundary violations are refused without polluting ordinary Hermes memory.

### Phase 11: Media and extension hooks

Build:

- TTS toggle;
- image prompt command;
- regex postprocessor;
- internal extension hook registry.

Acceptance:

- generated audio/image outputs can be sent through gateway when configured;
- postprocessor can be debugged.

---

## 22. Open Questions

1. Should the first implementation live only in `$HERMES_HOME/plugins/hermes-tavern/`, or should we also keep docs in the main repo?
2. Which provider/model profiles should be used as the user’s defaults for:
   - normal RP;
   - long novel writing;
   - explicit adult fiction;
   - summarization;
   - memory extraction?
3. Should Telegram commands use only slash commands, or also button-like quick replies where the platform supports them?
4. Should project export be plain Markdown first, or a ZIP containing Markdown + JSON assets?
5. Should vector memory use an existing Hermes memory backend, a plugin-local embedding store, or both?

---

## 23. Immediate Next Step

Create an implementation plan:

```text
.hermes/plans/hermes-tavern-implementation-v0.1.md
```

The plan should break Phase 1–3 into bite-sized TDD tasks:

1. plugin skeleton;
2. hook interception;
3. command parser;
4. SQLite database;
5. session persistence;
6. ST JSON card import;
7. start/end RP session;
8. fake-model integration test.

After that, implementation should use the subagent-driven development workflow: one focused coding agent per task, with review after each task.
