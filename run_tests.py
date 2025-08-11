#!/usr/bin/env python3
"""Compatibility wrapper to run tools/run_tests.py."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def main() -> int:
    tools_script = Path(__file__).resolve().parent / "tools" / "run_tests.py"
    spec = importlib.util.spec_from_file_location("tools.run_tests_proxy", tools_script)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)  # type: ignore[union-attr]
        if hasattr(module, "main"):
            return int(module.main())  # type: ignore[no-any-return]
        return 0
    except SystemExit as e:
        return int(e.code) if isinstance(e.code, int) else 1


if __name__ == "__main__":
    sys.exit(main())
