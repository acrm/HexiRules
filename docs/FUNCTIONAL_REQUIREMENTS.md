## Grid
- The system shall represent a hexagonal grid of radius R using axial coordinates (q, r) with |q + r| <= R.
## Conway Engine
- The system shall support Conway-style totalistic rules in B../S.. format.
- The system shall parse Conway rule strings and apply them during simulation steps.
- The system shall allow toggling, setting, and clearing cell states in Conway mode.
- The system shall advance the Conway automaton by one step and update all cells according to the rule.
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
- The system shall process rules in two substeps: `select_applicable_rules` collects all matching rules per cell, and `apply_random_rules` randomly chooses one rule to apply to each cell.
- The system shall apply at most one resulting transformation per cell per step.
## Graphical User Interface
- The system shall provide a graphical user interface.
- The system shall present stacked control sections: Worlds, Cells, Rules, Run, and Log.
- The system shall render the hex grid on a canvas that scales to fill the available space.
## Worlds
- The system shall support creating, selecting, and deleting worlds.
- The system shall allow per-world configuration of radius, mode (Conway or HexiDirect), and rules.
## Persistence
- The system shall save a world to JSON including radius, mode, rules, and non-empty cells.
- The system shall load a world from JSON and restore radius, mode, rules, and cells.
## Editing and Interaction
- The system shall allow interactive cell editing according to the active mode.
- The system shall allow left-click to cycle state in HexiDirect mode.
- The system shall allow right-click to cycle direction in HexiDirect mode.
- The system shall allow middle-click to clear a cell in HexiDirect mode.
- The system shall allow left-click to toggle cells in Conway mode.
- The system shall allow editing rules in a multi-line text area.
- The system shall allow switching between Conway and HexiDirect modes.
- The system shall clear all cells on request.
- The system shall randomize a subset of cells on request.

## Execution and Status
- The system shall execute a single simulation step on demand.
- The system shall display status including world name, active cell count, and a compact rules summary.
- The system shall log rule parsing, expansion, applications, and step summaries in a scrollable log.
- The system shall allow clearing the log.
