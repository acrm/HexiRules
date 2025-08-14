# HexiRules Proposed Clean Architecture

This document outlines a draft restructuring of the project to follow
Clean Architecture and Domain-Driven Design principles. No code has been
moved yet; this is a plan for discussion.

## Objectives
- Separate core domain logic for **HexiDirect** rule processing and
  **Worlds** management from user interfaces.
- Introduce clear boundaries between **Domain**, **Application**, and
  **Infrastructure** layers.
- Enable easier testing and future extension.

## Planned Directory Layout
```
src/
    domain/
        hexidirect/
            models.py          # HexCell, Condition, HexRule entities
            rule_parser.py     # Parse rule notation
            rule_engine.py     # Applies rules and exposes available states
        worlds/
            world.py           # World aggregate root, grid, rules, history
            repository.py      # Abstract repository interface
    application/
        use_cases/
            create_world.py
            rename_world.py
            list_worlds.py
            load_world.py
            save_world.py
            randomize_world.py
            update_rules.py
            list_available_states.py
            set_cell_state.py
            step_world.py
        services/
            simulation_service.py  # Orchestrates rule engine per world
    infrastructure/
        persistence/
            json_world_repository.py  # File-based repository implementation
        gui/
            tk/                 # Tkinter UI
        cli/
            commands/           # CLI entry points
```

### Layer Responsibilities
- **Domain** contains business rules and entities with no external
  dependencies.
- **Application** defines use cases and orchestrates domain objects via
  repository interfaces.
- **Infrastructure** hosts implementations for persistence, UI, and
  external adapters.

### Interaction Flow
1. UI or CLI triggers Application use case.
2. Application uses Domain entities and repositories to modify state.
3. Infrastructure provides repository implementations and platform
   details.

## World Management Capabilities
- Create a world with a given name and grid size.
- Rename existing worlds.
- Save and load worlds from persistent storage.
- Define and update rule sets for each world.
- Expose available cell states derived from current rules.
- Set individual cell states for the current step.
- Advance to the next step while logging actions.
- Preserve history of world states for every step.

## Next Steps
- Discuss and refine this structure.
- Gradually move existing logic into the outlined modules.
