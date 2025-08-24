# HexiRules

HexiRules is a hexagonal cellular automaton with two UI parts:
- HexiOS (controls)
- HexiScope (hex grid)

There are multiple UI implementations sharing the same application logic:
- Python: Tk HexiScope + ASCII HexiOS
- React: React HexiOS + Canvas HexiScope via FastAPI

## Run modes (unified launcher)

```bash
# Python GUI (Tk + ASCII)
python src/main.py --mode py-gui

# React desktop (starts FastAPI and opens a window or browser)
python src/main.py --mode react-desktop

# ASCII control panel in terminal
python src/main.py --mode ascii-cli

# Pure CLI shell
python src/main.py --mode cli
```

Environment variables:
- HEXIRULES_MODE: default run mode (fallback for --mode)
- HEXI_HOST / HEXI_PORT: FastAPI bind (server/dev)
- HEXI_URL: override URL for desktop window
- HEXI_DATA_DIR: data directory used by tests and services

See [docs](docs/) for architecture, server details, and React migration.
