"""CLI package - delegates to root main.py for unified entry point."""
from __future__ import annotations

# Re-export for backwards compatibility
# Primary entry: python main.py --repo <url> --mode review
# This module exists so `python -m src.cli.main` also works

import sys
from pathlib import Path

# Ensure root is on path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from main import main  # noqa: E402

if __name__ == "__main__":
    main()
