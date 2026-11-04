#!/usr/bin/env python3
"""Show what is waiting in a Beaver workspace: a thin entry point over beaver.status.

    python tools/status.py core/examples

`beaver` on its own runs the same check on your home once the package is installed.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from beaver.status import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
