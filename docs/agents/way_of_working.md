# Way of Working — In-Office Team Mode

This document defines how the AI team collaborates in in-office mode for HexiRules. It aligns with `AGENTS.md` and the `docs/agents` framework while keeping process light and automation-friendly.

## Goals
- Deliver small, well-tested increments mapped to stable requirements (REQ-####).
- Minimize friction: short cycles, explicit handoffs, and actionable artifacts.
- Preserve repo standards: no external deps, Python 3.8+, Black formatting, tests first.

## Roles
- Scrum Master/HR (you): sets priorities, clarifies scope, resolves blockers.
- Lead Agent (rotating per task via routing.md): owns task from planning to PR.
- Reviewer Agent: performs code review and validation.
- Scribe: updates notes under `docs/agents/notes/<Agent>.md`.

## Cadence
- Daily standup (async, 3 bullets): Yesterday, Today, Blockers.
- Sprint: 1 week by default; planning at start, retro at end.
- Checkpoints: after each completed testable requirement or PR merge.

## Message Handling
For in-office conversations: pick the Lead via `routing.md`, gather relevant context (profiles, notes, code/docs), respond concisely, and record handoffs in `notes/` when changing owners.

## Standard Delivery Workflow
1) Intake & Triaging
- Source: `docs/agents/tasks.md` (backlog) or a direct request.
- Each task references at least one `REQ-####` (or a new provisional `DRAFT-####`).

2) Definition of Ready (DoR)
- Clear outcome in one sentence.
- Acceptance criteria (Given/When/Then or bullet list).
- Test plan: unit tests to add/update and any e2e.
- Affected files/directories identified.

3) Plan → Implement → Validate
- Add/Update tests first under `tests/` (cover happy path + 1 edge case).
- Implement minimal code changes; keep engines pure, side effects in GUI.
- Run quality gates:
  - `python tools/run_tests.py --no-gui`
  - `python -m black <changed files>`
  - `HEXIRULES_NO_GUI=1 python tools/check_quality.py`

4) Handoff & Review
- Lead Agent writes a short note in `docs/agents/notes/<Agent>.md` (what changed, why, next).
- Reviewer validates tests/quality gates; merges or requests changes.

5) Definition of Done (DoD)
- All acceptance criteria satisfied.
- Tests green and lints clean; JSON schema/keys unchanged if touched.
- Docs updated: `docs/FUNCTIONAL_REQUIREMENTS.md` and relevant `README.md`.
- Commit messages follow `tools/commit_msg_lint.py` rules (≤72 chars subject, imperative mood).

## Communication Norms
- Tone: short, factual, no emojis; actionable errors.
- Mode: in-office (team personas). Use `routing.md` to select Lead/Reviewer expertise.
- Handoffs: explicit, link to PR or commit.

## Templates
- Use templates in `docs/agents/templates/`:
  - `standup.md` — async daily updates
  - `sprint_planning.md` — goals, scope, risks
  - `task_brief.md` — DoR + acceptance criteria + tests
  - `retro.md` — keep/change/try

## Quick Start
1. Pick a task from `docs/agents/tasks.md`; create a `task_brief.md` using the template.
2. Write/adjust tests, implement changes, and run quality gates.
3. Update notes and open PR; request review.
4. After merge, update `FUNCTIONAL_REQUIREMENTS.md` if needed and close the task.

## Links
- Coding & contribution rules: `/AGENTS.md`
- Backlog: `docs/agents/tasks.md`
- Routing: `docs/agents/routing.md`
- Team: `docs/agents/TEAM.md`
