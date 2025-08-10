"""Version information for HexiRules."""

import sys
from pathlib import Path


def get_version() -> str:
    """Get version from pyproject.toml."""
    try:
        pyproject_path = Path(__file__).parent / "pyproject.toml"

        # For Python 3.11+, use tomllib
        if sys.version_info >= (3, 11):
            import tomllib

            with open(pyproject_path, "rb") as f:
                data = tomllib.load(f)
            return str(data["project"]["version"])
        else:
            # For older Python versions, parse manually
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
