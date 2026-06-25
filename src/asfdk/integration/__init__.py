"""Integration adapters wrapping the four Solidarity Framework pillar packages.

Mirrors ``@neurolift-technologies/asfdk``'s ``src/integration/`` directory:

- :mod:`asfdk.integration.toi_otoi`    → ``nlt_toi`` + ``nlt_otoi``
- :mod:`asfdk.integration.sleepwalker` → ``sleepwalker_protocol``
- :mod:`asfdk.integration.rrt`         → ``rrt_advocate``
"""
from __future__ import annotations

from . import rrt, sleepwalker, toi_otoi

__all__ = ["toi_otoi", "sleepwalker", "rrt"]
