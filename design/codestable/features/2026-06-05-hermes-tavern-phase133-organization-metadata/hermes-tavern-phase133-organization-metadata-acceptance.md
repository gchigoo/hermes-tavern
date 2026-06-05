---
doc_type: feature-acceptance
feature: "2026-06-05-hermes-tavern-phase133-organization-metadata"
status: accepted
date: "2026-06-05"
summary: >
  Phase 133 Organization Metadata v1 is accepted. S1 implemented local
  project-scoped organization persistence, `/rp organization ...` commands,
  help/README visibility, optional `## Organizations` Markdown export, and
  no-leak tests. S2 verified the implementation, finalized status docs, and
  merged the current metadata/export-only boundary into architecture and root
  design docs.
---

# 2026-06-05-hermes-tavern-phase133-organization-metadata Acceptance

## 1. Accepted interface contract

Phase 133 Organization Metadata v1 is accepted as a local/offline metadata
surface for project-scoped organization notes.

Accepted storage and runtime contract:

- `novel_organizations(id, project_id, label, description_text, created_at, updated_at)`
  is created with `project_id REFERENCES novel_projects(id) ON DELETE CASCADE`.
- `idx_novel_organizations_project` indexes rows by project.
- Store helpers create/list/get/update/delete organization rows and preserve bounded
  missing-project / missing-organization behavior.
- `/rp organization add <project-id> <label> <description...>` stores a freeform
  description for a compact command label.
- `/rp organization list [project-id]` supports explicit project IDs and active-project
  fallback for list only.
- `/rp organization inspect/update/delete <organization-id>` operate by organization ID.
- `/rp help` and README Core commands expose the organization command family.
- Project Markdown export emits optional `## Organizations` after `## Locations`
  when present, or after Project Brief / Outline / Style Guide when no Locations
  section exists, before Characters / Relationships / Chapters; the section is
  omitted when empty.

## 2. Boundary accepted

Organization metadata remains informational/export-visible only. It is not an
organization graph, hierarchy model, membership roster, affiliation engine,
automatic extractor, summarizer, retrieval source, vector store input, prompt
module, model/provider routing signal, content-mode control, credential store,
cloud/collaboration surface, generation workflow, or provider-safety bypass.

No minors/underage/school-grade semantics or examples were added.

## 3. Controller verification evidence

Controller reran the required checks after Codex executor drafted S2 artifacts:

- Focused suite: `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_novel_db.py tests/test_hermes_tavern_novel_runtime.py tests/test_hermes_tavern_commands.py tests/test_hermes_tavern_readme_docs.py -q -o 'addopts=' -p no:cacheprovider` → `243 passed in 7.78s`.
- Tavern plugin suite: `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_*.py -q -o 'addopts=' -p no:cacheprovider` → `934 passed in 39.86s`.
- Full suite: `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o 'addopts=' -p no:cacheprovider` → `934 passed in 39.88s`.
- Design frontmatter validator passed.
- Acceptance frontmatter validator passed.
- Checklist YAML validator passed after final controller status update.
- S2 source/protected diff guards were empty for README, source, tests, core, build,
  prompt, provider, model, generation, content, runtime debug, adapters, and importer paths.
- Stale wording scan found no remaining `current through Phase 132`, `Phase 121–132`,
  or organization-still-deferred current-doc wording.
- `git diff --check` passed.

## 4. Architecture and root-design writeback

S2 updated `design/codestable/architecture/ARCHITECTURE.md` to mark Phase 133 as
current through:

- capability summary for Organization Metadata v1;
- `/rp organization add/list/inspect/update/delete` command surface;
- `novel_organizations` schema/index documentation;
- prompt/debug/context-budget/provider/model/content/retrieval/vectorization/automation/
  generation exclusion notes;
- Phase 133 known constraint boundary.

S2 updated `design/HERMES_TAVERN_DESIGN.md` to move organizations from deferred
future sub-objects into current local metadata, document command literals and
Markdown export order, and preserve deferred boundaries for plot threads,
relationship graph/rename/automatic extraction, style samples, default bindings,
canon/content-mode metadata, provider routing, generation, retrieval,
vectorization, automation, project archive import/export, cloud/collaboration,
and safety-bypass behavior.

## 5. Requirement and roadmap writeback

No requirement or roadmap writeback was needed: the feature is a bounded local
metadata continuation with no `requirement` or `roadmap_item` frontmatter target.

## 6. Residual deferred work

Still deferred after Phase 133:

- plot threads;
- relationship graph/rename/automatic extraction;
- style samples;
- default card/preset/lorebook binding metadata;
- canon policy and content-mode metadata behavior changes;
- provider routing / generation coupling;
- retrieval, vectorization, and automation integration;
- project archive ZIP/import/export and Markdown import;
- cloud collaboration / multi-user runtime;
- provider-safety-bypass pathways.

## 7. Final status

Accepted. No implementation behavior beyond the completed S1 organization metadata
slice is included in S2.
