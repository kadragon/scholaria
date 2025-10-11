---
id: AG-WORKFLOW-RSP-I-001
version: 1.0.0
scope: global
status: active
supersedes: []
depends: [AG-POLICY-DEV-GUARDRAILS-001]
last-updated: 2025-10-11
owner: team-admin
---
# RSP-I Development Workflow

## Phases
Structured development cycle for non-trivial features and fixes.

### 1. Research (R)
- Investigate existing flows, dependencies, and constraints.
- Document findings in `.tasks/<task>/RESEARCH.md`.
- Output: Hypotheses, evidence, and decision rationale.

### 2. Spec (S)
- Define acceptance criteria and contracts.
- Create `.tasks/<task>/SPEC-DELTA.md` or update `.spec/<domain>/<name>.spec.md`.
- Include examples that become automated tests.

### 3. Plan (P)
- Break work into discrete steps.
- Identify test scenarios, rollback strategies, and dependencies.
- Document in `.tasks/<task>/PLAN.md`.

### 4. Implement (I)
- Follow TDD: write failing test → minimal pass → refactor on Green.
- Update `.tasks/<task>/PROGRESS.md` as milestones complete.
- Commit logical units separately with structured messages.

## Automation
- Default: auto-progress R → S → P → I in single turn for small tasks.
- Hard gate (ask once) for:
  - Schema/data changes
  - Security/compliance touches
  - External API writes
  - Public contract changes
  - Major refactors (>200 LOC or >3 modules)

## Completion
- Merge insights into nearest `.agents/` policy or workflow.
- Summarize to `.tasks/<task>/TASK_SUMMARY.md`.
- Archive under `.tasks/_archive/YYYY/Q/<task>/`.
