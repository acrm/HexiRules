"""Version information for HexiRules."""

import sys
from pathlib import Path


def get_version() -> str:
    """Get version from pyproject.toml."""
    try:
        # Try root pyproject (two levels up from this file: src/version.py -> project root)
        pyproject_path = Path(__file__).resolve().parent.parent / "pyproject.toml"
        if not pyproject_path.exists():
            # Fallback: sometimes tests import from repo root; try cwd
            pyproject_path = Path.cwd() / "pyproject.toml"

        # For Python 3.11+, use tomllib
        if sys.version_info >= (3, 11) and pyproject_path.exists():
            import tomllib

            with open(pyproject_path, "rb") as f:
                data = tomllib.load(f)
            return str(data["project"]["version"])
        else:
            # For older Python versions, parse manually
            if pyproject_path.exists():
                with open(pyproject_path, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.strip().startswith('version = "'):
                            return line.split('"')[1]
        return "0.0.1"  # fallback version
    except Exception:
        # Fallback version if pyproject.toml can't be read
        return "0.0.1"

    return "0.0.1"


__version__ = get_version()
