"""Deprecated server runner. Use uvicorn or the unified launcher.

Examples:
    python -m uvicorn server.app:app --reload
    python src/main.py --mode react-desktop
"""

if __name__ == "__main__":
    raise SystemExit(
        "Deprecated. Use 'uvicorn infrastructure.server.app:app --reload' or 'python src/main.py --mode react-desktop'"
    )
