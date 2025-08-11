#!/usr/bin/env python3
"""Compatibility wrapper to run tools/check_quality.py.

This keeps existing pipelines and debug configs that reference the
old root-level check_quality.py from breaking after repo cleanup.
"""
from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path


def main() -> int:
    # Default to headless to avoid GUI tests in CI unless explicitly opted in
    os.environ.setdefault("HEXIRULES_NO_GUI", "1")

    tools_script = Path(__file__).resolve().parent / "tools" / "check_quality.py"
    if not tools_script.exists():
        print(f"Could not find tools/check_quality.py at {tools_script}")
        return 1

    spec = importlib.util.spec_from_file_location(
        "tools.check_quality_proxy", tools_script
    )
    if spec is None or spec.loader is None:
        print("Failed to load tools/check_quality.py module spec")
        return 1
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)  # type: ignore[union-attr]
    except SystemExit as e:
        # If the underlying script calls sys.exit(), surface its code
        return int(e.code) if isinstance(e.code, int) else 1
    except Exception as e:  # pragma: no cover - defensive
        print(f"Error running tools/check_quality.py: {e}")
        return 1

    # If module exposes main(), call it to get exit code
    if hasattr(module, "main") and callable(module.main):  # type: ignore[attr-defined]
        try:
            return int(module.main())  # type: ignore[no-any-return]
        except SystemExit as e:
            return int(e.code) if isinstance(e.code, int) else 1
        except Exception as e:  # pragma: no cover - defensive
            print(f"Error executing main(): {e}")
            return 1

    # Fallback success if no main is exposed
    return 0


if __name__ == "__main__":
    sys.exit(main())
