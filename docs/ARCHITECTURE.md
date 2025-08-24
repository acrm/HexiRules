# HexiRules Architecture

This project separates core application logic from multiple user interfaces:

- HexiOS (control plane) and HexiScope (visual hex grid) are independent.
- Python UI:
  - HexiOS is ASCII-based and receives keyboard input only.
  - HexiScope is drawn with Tk Canvas and receives mouse events.
- React UI:
  - HexiOS is built with React forms; HexiScope uses Canvas.
  - React UI talks to the same application logic via REST (FastAPI).
- Single unified launcher (`hexirules`) starts any mode: Tk GUI, React desktop, ASCII CLI, or pure CLI.

## Source Layout

- `src/application`: Services (e.g., `WorldService`) — shared across all UIs
- `src/domain`: Domain models and rule engine — shared
- `src/infrastructure`: Persistence, adapters (future)
- `src/ui/ascii`: ASCII HexiOS view model, renderer, layout
- `src/ui/tk`: Tk-specific helpers (future placement of Tk-only code)
- `src/ui/react`: React-specific adapters (server client types, if any)
- `src/server`: FastAPI app powering the React UI and API
- `src/main.py`: Unified launcher
- `src/cli.py`: Pure CLI shell
- `src/gui.py`: Python GUI wiring (Tk + ASCII)

## Run Modes

- `hexirules --mode py-gui` — Tk GUI (HexiScope + ASCII HexiOS)
- `hexirules --mode react-desktop` — FastAPI + embedded browser window (pywebview if available)
- `hexirules --mode ascii-cli` — ASCII HexiOS interactive control panel
- `hexirules --mode cli` — Pure CLI shell

All modes share `application` and `domain` packages.

## Dependencies

- Base project intentionally has no mandatory external deps.
- React desktop mode requires optional `fastapi`, `uvicorn`, and `pywebview`.

## Testing

Use the built-in runner:

```
python tools/run_tests.py --no-gui
```

GUI tests can be enabled locally if desired.
