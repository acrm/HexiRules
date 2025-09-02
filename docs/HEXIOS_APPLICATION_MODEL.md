# HexiOS Application Model (Pre-development Spec)

This document specifies the application-layer model for HexiOS so that CLI and ASCII UI operate on the same use-cases and data.

## Goals
- Single source of truth for HexiOS use-cases (independent of presentation).
- Deterministic, testable, and aligned with CLI behaviors.

## Functional Requirements (Worlds)
- List worlds (highlight selected)
- Select world
- Create world
- Rename world
- Delete world
- Load world from local file
- Save world to local file
- Get current world summary

See detailed use-cases and error policies in `HEXIOS_WORLD_USE_CASES.md`.

## API (Proposed)
- WorldsSummary { name, radius, active_count }
- WorldsView { current: Optional[WorldsSummary], names: List[str] }
- HexiOSApp
  - list_worlds() -> List[str]
  - select_world(name)
  - create_world(name, radius, rules_text="")
  - rename_world(old_name, new_name)
  - delete_world(name)
  - load_world(path) -> name
  - save_world(path, rules_text=None)
  - get_current_world_summary() -> Optional[WorldsSummary]
  - get_worlds_view() -> WorldsView

## Non-Goals (initial)
- UI-specific input handling
- Responsive layouts or advanced widgets

## Testing Strategy
- Unit tests for each use-case
- CLI integration tests calling the same app methods
- ASCII snapshot tests mirror the app data

## Acceptance
- CLI and HexiOS show the same worlds and support the same operations.
- Renderer never crashes; errors are user-facing messages.
