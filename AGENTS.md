# Instructions for AI Contributors

## Testing
- Run `python tools/run_tests.py --no-gui`.
- Run `HEXIRULES_NO_GUI=1 python tools/check_quality.py`.

## Code style
- Python 3.8+ only; no external dependencies.
- Minimal diffs; do not reformat or rename unrelated code.
- Type hints on public functions and classes; use explicit imports.
- Black-compatible formatting; MyPy-friendly typing.
- Naming: snake_case for functions and variables, PascalCase for classes, UPPER_SNAKE for constants.
- Keep functions small (≈40 lines); extract helpers when needed.
- Avoid global state; keep engines pure and side effects in the GUI.
- No prints in libraries; use existing logging or GUI log methods.
- Cross-platform paths; prefer pathlib; ensure Windows-friendly code.
- Preserve GUI layout contracts and event bindings.
- Keep JSON save format stable (keys unchanged).

## Messages
- Commit and PR titles use imperative mood, ≤72 characters; wrap body text at 72.
- Logs and status messages: short, factual, no emojis.
- Errors: actionable; include offending value or context.
- UI labels: Title Case; other user text: sentence case.
- Chat responses: short, impersonal, no emojis, no fluff.

## Repository layout
- GUI code lives in `src/gui.py`.
- Conway engine in `src/automaton.py`; HexiDirect engine in `src/hex_rules.py`.
- Tests under `tests/` named `test_*.py`.
- Documentation under `docs/` (`*.md`); strict rule lists in `*.txt`.
- Scripts and helper tools in `tools/`.
- File names use `lowercase_with_underscores.py`.
