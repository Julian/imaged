==========
``imaged``
==========

|PyPI| |Pythons| |CI| |ReadTheDocs|

.. |PyPI| image:: https://img.shields.io/pypi/v/imaged.svg
  :alt: PyPI version
  :target: https://pypi.org/project/imaged/

.. |Pythons| image:: https://img.shields.io/pypi/pyversions/imaged.svg
  :alt: Supported Python versions
  :target: https://pypi.org/project/imaged/

.. |CI| image:: https://github.com/Julian/imaged/workflows/CI/badge.svg
  :alt: Build status
  :target: https://github.com/Julian/imaged/actions?query=workflow%3ACI


.. |ReadTheDocs| image:: https://readthedocs.org/projects/imaged/badge/?version=stable&style=flat
  :alt: ReadTheDocs status
  :target: https://imaged.readthedocs.io/en/stable/

``imaged`` gives you one interface to `docker <https://www.docker.com/>`_,
`podman <https://podman.io/>`_ and `Apple's container
<https://github.com/apple/container>`_.
Start a container, speak to its standard streams, and be told what went wrong
in terms you can branch on.

.. code-block:: python

    from imaged import Engine

    engine = Engine.detect()

    id = await engine.create_pulling_if_needed("alpine", "cat")
    async with engine.start(id) as session:
        await session.send("hello")
        assert await session.receive() == "hello"

Why
---

Every engine reports the same failure differently, and none of them do so
machine readably -- not even over their HTTP APIs.
Working out that an image simply doesn't exist otherwise means matching on
substrings of prose, separately for each engine.
``imaged`` does that once, and raises ``NoSuchImage``.

Each engine is driven via its command line interface, which is the only
mechanism all three have in common, as Apple's container has no HTTP API at
all.
Doing so also leaves the engine to demultiplex container stdio onto real
pipes, rather than leaving you to unpick its framing.

Containers get no networking unless you ask for it, on the theory that
something you are running should have to say so before it can phone home.

`anyio <https://anyio.readthedocs.io/>`_ is the only async dependency, so
this runs unmodified on both asyncio and trio.
Its own test suite runs on both, against all three engines.
