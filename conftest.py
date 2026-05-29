"""Pytest bootstrap for ASFDK.

The component source trees use hyphenated directory names (``rrt-advocate/``)
that are not importable Python package identifiers, so their ``src/`` paths must
be on ``sys.path`` for tests to import them directly. Adding this here (instead
of relying on each developer/CI to export ``PYTHONPATH``) lets ``pytest`` be run
from the repo root with no extra setup. See AGENTS.md "Known gotchas".
"""

import os
import sys

_REPO_ROOT = os.path.dirname(os.path.abspath(__file__))

# Component source roots that need to be importable by tests.
_EXTRA_PATHS = [
    os.path.join(_REPO_ROOT, "rrt-advocate", "src"),
]

for _path in _EXTRA_PATHS:
    if os.path.isdir(_path) and _path not in sys.path:
        sys.path.insert(0, _path)
