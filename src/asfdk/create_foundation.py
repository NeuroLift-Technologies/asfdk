"""The :func:`create_foundation` factory, ported from
``@neurolift-technologies/asfdk`` (``src/create-foundation.ts``).
"""
from __future__ import annotations

from typing import Optional, Union

from .foundation import NeuroLiftFoundation
from .types import FoundationConfig, FoundationMode


async def create_foundation(
    user_id_or_config: Union[str, FoundationConfig],
    mode: Optional[FoundationMode] = None,
) -> NeuroLiftFoundation:
    """Construct and initialize a :class:`NeuroLiftFoundation` instance.

    Two call signatures are supported (mirroring the TypeScript overloads):

    - ``create_foundation(user_id, mode=None)`` — shorthand; ``mode`` defaults to
      :attr:`FoundationMode.UNIFIED`.
    - ``create_foundation(config)`` — full :class:`FoundationConfig` object.
    """
    if isinstance(user_id_or_config, FoundationConfig):
        config = user_id_or_config
    else:
        config = FoundationConfig(
            user_id=user_id_or_config,
            mode=mode if mode is not None else FoundationMode.UNIFIED,
        )

    foundation = NeuroLiftFoundation(config)
    await foundation.initialize()
    return foundation


__all__ = ["create_foundation"]
