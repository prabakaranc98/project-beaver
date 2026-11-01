#!/usr/bin/env python3
"""Validate a Beaver workspace: a thin entry point over beaver.validate.

    python tools/validate.py core/examples

`beaver validate` runs the same check once the package is installed.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from beaver.validate import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
