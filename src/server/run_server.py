from __future__ import annotations

import os
import sys
from pathlib import Path

if __name__ == "__main__":
    # Lazy import so normal usage doesn't require server deps
    import uvicorn
    # Ensure src is on sys.path
    repo_root = Path(__file__).resolve().parents[2]
    src_path = str(repo_root / "src")
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
    from server.app import app

    host = os.environ.get("HEXI_HOST", "127.0.0.1")
    port = int(os.environ.get("HEXI_PORT", "8000"))
    uvicorn.run(app, host=host, port=port, reload=False)
