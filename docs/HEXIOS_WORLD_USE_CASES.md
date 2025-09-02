# HexiOS Worlds Use-Cases

Each use-case applies equally to CLI and HexiOS ASCII UI.

## UC-1: List worlds
- Preconditions: any
- Trigger: request to list
- Behavior: return all world names in stable order
- Success: list of names
- Errors: none
- CLI: `world list`
- HexiOS: Worlds frame list

## UC-2: Select world
- Preconditions: name exists
- Trigger: select by name
- Behavior: set current world
- Success: current changes; UI updates
- Errors: not found -> error
- CLI: `world select <name>`
- HexiOS: focus W then activate row or command

## UC-3: Create world
- Preconditions: unique name; valid radius
- Trigger: create(name, radius[, rules])
- Behavior: create and optionally set current
- Success: appears in list
- Errors: conflicts, invalid radius -> errors
- CLI: `world create <name> <radius> [rules:"..."]`
- HexiOS: command line

## UC-4: Rename world
- Preconditions: old exists; new unique
- Trigger: rename(old, new)
- Behavior: rename; keep selection semantics
- Success: list shows new name
- Errors: 404/409 -> errors
- CLI: `world rename <old> <new>`
- HexiOS: command line

## UC-5: Delete world
- Preconditions: exists
- Trigger: delete(name)
- Behavior: remove; choose deterministic next current if needed
- Success: removed; possibly reselection
- Errors: 404 -> handled
- CLI: `world delete <name>`
- HexiOS: command line

## UC-6: Load world
- Preconditions: readable path; valid format
- Trigger: load(path)
- Behavior: load and select
- Success: new world selected
- Errors: IO/parse errors -> messages
- CLI: `world load <path>`
- HexiOS: command line

## UC-7: Save world
- Preconditions: current selected; writable path
- Trigger: save(path[, rules])
- Behavior: persist
- Success: file written
- Errors: IO errors -> messages
- CLI: `world save <path> [rules:"..."]`
- HexiOS: command line

## UC-8: Current world summary
- Preconditions: any
- Trigger: query or render
- Behavior: show name, radius, active
- Success: deterministic view
- Errors: none
- CLI: `world current`
- HexiOS: header of Worlds frame
