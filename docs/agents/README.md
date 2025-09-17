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
- In-Office mode: all your messages are addressed to the team. I will respond as the most relevant agent persona (see routing.md), keep notes, and perform handoffs.
- Out-Office mode: your messages are treated as regular prompts; I’ll answer directly without agent roleplay.

How to set mode:
- Edit `docs/agents/mode.txt` and set either `in-office` or `out-office`.
- Or set environment variable `HEXI_AGENT_MODE` to override the file at runtime.
