"""
One interface to docker, podman and Apple's container.

Start a container, speak to its standard streams, and get told what went
wrong in terms you can actually branch on -- with the same code and the
same answers whichever engine is installed.

Each engine is driven via its command line interface, which is the only
mechanism all three have in common, and which conveniently leaves the
engine to demultiplex container stdio onto real pipes for us.

`anyio` is the only async dependency, so this runs unmodified on both
asyncio and trio.
"""

from imaged._dialects import (
    CONTAINER,
    DOCKER,
    KNOWN,
    PODMAN,
    Dialect,
)
from imaged._errors import (
    EngineError,
    EngineFailed,
    EngineNotRunning,
    NoSuchContainer,
    NoSuchEngine,
    NoSuchImage,
    SessionClosed,
    Unsupported,
)
from imaged._subprocess import Engine, Session

__all__ = [
    "CONTAINER",
    "DOCKER",
    "KNOWN",
    "PODMAN",
    "Dialect",
    "Engine",
    "EngineError",
    "EngineFailed",
    "EngineNotRunning",
    "NoSuchContainer",
    "NoSuchEngine",
    "NoSuchImage",
    "Session",
    "SessionClosed",
    "Unsupported",
]
