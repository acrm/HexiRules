from __future__ import annotations

"""Launch the optional FastAPI server for HexiRules.

Install server deps first:
    pip install -r requirements-server.txt

Run:
    python tools/run_server.py
"""

import os
import sys
from pathlib import Path


def main() -> None:
    # Ensure 'src' is importable (so 'server' package resolves)
    repo_root = Path(__file__).resolve().parent.parent
    src_path = str(repo_root / "src")
    if src_path not in sys.path:
        sys.path.insert(0, src_path)

    import uvicorn  # type: ignore
    from server.app import app  # type: ignore

    host = os.environ.get("HEXI_HOST", "127.0.0.1")
    port = int(os.environ.get("HEXI_PORT", "8000"))
    uvicorn.run(app, host=host, port=port, reload=False)


if __name__ == "__main__":
    main()
