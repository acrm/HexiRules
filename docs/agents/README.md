# Agent Framework

This folder defines a lightweight AI-agent workflow for HexiRules. Each agent has:
- A profile (personality, competencies, goals, responsibilities)
- A notes file for running thoughts, decisions, and handoffs
- Clear routing rules for when to take lead or hand off to another agent

Key principles:
- Keep the core small, dependency-light, and well-tested.
- Use Requirements with stable IDs (REQ-XXXX) to drive tests and code.
- Make handoffs explicit; each agent writes a short note before/after.

See also: `/AGENTS.md` for coding style and contribution rules.

Contents:
- TEAM.md — agents and their scope
- routing.md — how an agent is selected for a topic
- templates/ — profile, notes, and task templates
- profiles/ — individual agent profiles
- notes/ — ongoing notes per agent (meeting log, decisions)
- tasks.md — current backlog triaged by agents

Mode of operation:
- In-Office mode (team mode): messages are addressed to the team; responses are written in the voice of the most relevant persona per `routing.md`. Handoffs are explicit and logged in `notes/`.
- Out-Office mode: no team role-play; a single default agent responds plainly with default preferences.

Notes:
- Team documents do not describe or track any “team engine” automation or self-improvement activities. Such activities, if performed, are handled outside the team (out-office) and are not recorded here; only their outcomes may be used implicitly by the team.
- You can set the mode by editing `docs/agents/mode.txt`.
