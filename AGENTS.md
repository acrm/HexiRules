# Instructions for AI Contributors

## Testing
- Run `python tools/run_tests.py --no-gui`.
- Format changed files with `python -m black`.
- Run `HEXIRULES_NO_GUI=1 python tools/check_quality.py`.

## Functional requirements
- Describe new features in `docs/FUNCTIONAL_REQUIREMENTS.md`.
- Implement unit and end-to-end tests verifying each requirement.

## Code style
- Python 3.8+ only; no external dependencies.
- Minimal diffs; do not reformat or rename unrelated code.
- Type hints on public functions and classes; use explicit imports.
- Black-compatible formatting; run `python -m black` before committing.
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

### Commit Message Enforcement
Local automation is provided to help enforce these rules:

1. Use the commit template:
	git config commit.template .gitmessage
2. Enable the hook-based linter:
	git config core.hooksPath .githooks
3. The hook rejects commits if:
	- Subject line > 72 characters
	- Subject not in (roughly) imperative mood (heuristic: flags verbs ending with 's' or 'ed')
	- Subject starts with a lowercase letter
	- Body lines exceed 72 characters
	- Emoji detected in subject

You can run the linter manually:
	python tools/commit_msg_lint.py .git/COMMIT_EDITMSG

Heuristics are intentionally lightweight (no external deps). Adjust allowlists in tools/commit_msg_lint.py if needed.

## Repository layout
- GUI code lives in `src/gui.py`.
- ASCII control panel in `src/ascii_ui.py`.
- HexiDirect engine in `src/domain/hexidirect/`.
- Tests under `tests/` named `test_*.py`.
- Documentation under `docs/` (`*.md`); strict rule lists in `*.txt`.
- Scripts and helper tools in `tools/`.
- File names use `lowercase_with_underscores.py`.
