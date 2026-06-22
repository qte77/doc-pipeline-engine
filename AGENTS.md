# Agent Instructions

**Behavioral rules, compliance requirements, and decision frameworks for AI coding
agents.** For technical workflows and coding standards, see
[CONTRIBUTING.md](CONTRIBUTING.md). For project overview, see
[README.md](README.md).

**External References** (human contributors): [CONTRIBUTING.md](CONTRIBUTING.md) | [AGENT_REQUESTS.md](AGENT_REQUESTS.md) | [AGENT_LEARNINGS.md](AGENT_LEARNINGS.md)

## Key Commands

| Command | Purpose |
| --- | --- |
| `make install` | `uv sync` — install dev dependencies |
| `make test` | Full pytest suite |
| `make test_rerun` | Rerun only failed tests (fast TDD iteration) |
| `make lint` | Ruff check on Python sources |
| `make validate` | Pre-commit gate: lint + test + lint_md + lint_links |
| `make run_local SAMPLE=path` | Run the offline local leg on one sample (no API key) |

## Code Conventions

- **Imports**: absolute (`from doc_pipeline_engine.module import X`)
- **Comments**: default to none; add `# Reason:` only when the *why* is non-obvious
- **Tests**: mirror `src/` layout under `tests/`; new functionality requires tests
- **Commits**: Conventional Commits (`feat:`, `fix:`, `docs:`, `chore:`, `refactor:`, `test:`)

### Pydantic + TCH (type-checking imports)

The `TCH` ruff rules (`TC001`/`TC002`/`TC003`) suggest moving annotations-only
imports into `if TYPE_CHECKING:` blocks. This is safe for function-signature
annotations (deferred by `from __future__ import annotations`), but **breaks
Pydantic** when applied to Pydantic model field types:

```python
# WRONG — Pydantic resolves field types at validation time; moving to
# TYPE_CHECKING makes the class unavailable at runtime.
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .composite_scores import CompositeScores  # breaks model_validate()

class MyModel(StrictModel):
    scores: CompositeScores | None = None  # Pydantic cannot resolve this
```

Keep Pydantic field-type imports at module level and suppress with `# noqa: TCH001`:

```python
from .composite_scores import CompositeScores  # noqa: TCH001  # pydantic runtime requirement
```

The models in `src/doc_pipeline_engine/models/` all use `_common.StrictModel`
(a `pydantic.BaseModel` subclass). Any import used as a Pydantic field type
must remain at runtime scope. See `docs/architecture.md` boundary-failure table
for where `model_validate()` is the boundary policy.

## Escalation

Write to `AGENT_REQUESTS.md` when: user instructions conflict with safety practices, rules contradict each other, required information is missing, or actions would significantly change project architecture.

## Claude Code Infrastructure

**Rules** (`.claude/rules/`): Session-loaded constraints (always active)

## Decision Framework

**Priority Order:** User instructions > AGENTS.md compliance > Documentation
hierarchy > Project patterns > General best practices

**When to Escalate to AGENT_REQUESTS.md:**

- User instructions conflict with safety/security practices
- AGENTS.md rules contradict each other
- Required information completely missing
- Actions would significantly change project architecture

## Compliance Requirements

1. **Command Execution**: Use project make recipes or standard tooling
2. **Quality Validation**: Run validation before task completion; fix ALL issues
3. **Coding Style**: Follow existing project patterns and conventions
4. **Documentation Updates**: Update docs when introducing new patterns
5. **Testing**: Create tests for new functionality
6. **Code Standards**: Use absolute imports, add `# Reason:` comments for complex logic

## Quality Thresholds

**Before starting any task, ensure:**

- **Context**: 8/10 - Understand requirements, codebase patterns, dependencies
- **Clarity**: 7/10 - Clear implementation path and expected outcomes
- **Alignment**: 8/10 - Follows project patterns and architectural decisions
- **Success**: 7/10 - Confident in completing task correctly

### Below Threshold Action

Gather more context or escalate to AGENT_REQUESTS.md.
