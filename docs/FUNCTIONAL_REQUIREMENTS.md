## Grid
- The system shall represent a hexagonal grid of radius R using axial coordinates (q, r) with |q + r| <= R.
## HexiDirect Engine
- The system shall support a HexiDirect symbolic rules engine.
- The system shall represent cells as symbolic states including "_" for empty and letter states.
- The system shall allow an optional direction 1..6 to be associated with a cell.
- The system shall parse HexiDirect rules with a source state optionally constrained to a specific direction.
- The system shall support the source any-direction macro using % in HexiDirect rules.
- The system shall support target direction specification in HexiDirect rules.
- The system shall support target direction persistence using % in HexiDirect rules.
- The system shall support target rotation using %N in HexiDirect rules.
- The system shall support conditions in brackets [ ... ] that constrain neighbor state and direction.
- The system shall support negated conditions using - inside the condition block.
- The system shall support the pointing shorthand [state.] meaning a neighbor state pointing toward the center cell.
- The system shall support explicit neighbor pointing direction in conditions (e.g., [1t4]).
- The system shall expand macro rules into concrete directional variants prior to evaluation.
- The system shall apply grouped random selection when multiple rules arising from the same macro expansion match a cell.
- The system shall evaluate rule conditions against the six neighbors in clockwise order.
- The system shall process rules in two substeps: `select_applicable_rules` gathers all matching rules for each cell, and `apply_random_rules` randomly selects one rule to apply to each cell.
- The system shall apply at most one resulting transformation per cell per step.
- The system shall expand rule presets including `b3s23` into equivalent HexiDirect rules.
- The system shall support bracket repetition `[state]N` and in-bracket alternatives such as `[a|_]`.
## Graphical User Interface
- The system shall provide a graphical user interface.
- The system shall render the hex grid on a canvas that scales to fill the available space.
- The system shall expose controls through an ASCII panel.
## Worlds
- The system shall support creating, selecting, and deleting worlds.
- The system shall allow per-world configuration of radius and rules.
## Persistence
- The system shall save a world to JSON including radius, rules, and non-empty cells.
- The system shall load a world from JSON and restore radius, rules, and cells.
## Editing and Interaction
- The system shall allow interactive cell editing.
- The system shall allow left-click to cycle state in HexiDirect mode.
- The system shall allow right-click to cycle direction in HexiDirect mode.
- The system shall allow middle-click to clear a cell in HexiDirect mode.
- The system shall allow editing rules in a multi-line text area.
- The system shall clear all cells on request.
- The system shall randomize a subset of cells on request.

## ASCII Control Panel
- The system shall display a text-based control panel of fixed width.
- The panel shall allow entering rules.
- The panel shall allow advancing the automaton by one step.
- The panel shall allow clearing all cells.
- The panel shall render placeholder content when no world is selected.
- The ASCII renderer shall expose tagged per-character output for automated
  visualization tests.

## Execution and Status
- The system shall execute a single simulation step on demand.
- The system shall display status including world name, active cell count, and a compact rules summary.

## Command-Line Interface
- The system shall provide a command-line interface for running the automaton.
- The CLI shall allow setting rules, editing cell states, and advancing steps.
- The CLI shall allow querying individual cell states.
- The CLI shall display active rules and list all live cells on request.
- The CLI shall render the current grid as ASCII art.
