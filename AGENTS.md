# Agent Instructions

**Behavioral rules, compliance requirements, and decision frameworks for AI coding
agents.** For technical workflows and coding standards, see
[CONTRIBUTING.md](CONTRIBUTING.md). For project overview, see
[README.md](README.md).

**External References:**

- @CONTRIBUTING.md - Command reference, testing guidelines, code style patterns
- @AGENT_REQUESTS.md - Escalation and human collaboration
- @AGENT_LEARNINGS.md - Pattern discovery and knowledge sharing

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
