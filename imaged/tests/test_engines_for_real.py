"""
The same behavior, asserted against an actual container engine.

`imaged` exists so that three engines answer identically, which is a
claim only an actual engine can settle.
So these run one set of assertions against whichever engine
`IMAGED_ENGINE` names, and CI runs them once per engine.

They are the only tests here needing a container runtime, and skip
themselves when there isn't one.
"""

from __future__ import annotations

from os import environ

import pytest

from imaged import (
    Engine,
    NoSuchEngine,
    NoSuchImage,
    SessionClosed,
    Unsupported,
)

pytestmark = [pytest.mark.anyio, pytest.mark.real]

#: Something tiny, ubiquitous, and able to hold a conversation.
IMAGE = "docker.io/library/alpine:3.22"


@pytest.fixture(params=["asyncio", "trio"])
def anyio_backend(request):
    return request.param


@pytest.fixture(scope="module")
def engine():
    named = environ.get("IMAGED_ENGINE")
    try:
        return Engine.named(named) if named else Engine.detect()
    except NoSuchEngine as error:  # pragma: no cover
        pytest.skip(str(error))


@pytest.fixture
async def container(engine):
    """
    Containers running the given command, cleaned up afterwards.
    """
    created: list[str] = []

    async def _container(*command: str) -> str:
        id = await engine.create_pulling_if_needed(IMAGE, *command)
        created.append(id)
        return id

    yield _container

    for id in created:
        await engine.remove(id)


async def test_round_trip(engine, container):
    id = await container("cat")
    async with engine.start(id) as session:
        await session.send("hello")
        assert await session.receive() == "hello"
        await session.send("goodbye")
        assert await session.receive() == "goodbye"


async def test_a_container_which_exits(engine, container):
    id = await container("true")
    async with engine.start(id) as session:
        with pytest.raises(SessionClosed):
            await session.receive()


async def test_stderr_is_kept_separate(engine, container):
    id = await container("sh", "-c", "echo trouble >&2; exec cat")
    async with engine.start(id) as session:
        await session.send("hello")
        assert await session.receive() == "hello"
        assert b"trouble" in session.stderr()


async def test_stderr_survives_the_container(engine, container):
    id = await container("sh", "-c", "echo very wrong >&2; exit 1")
    async with engine.start(id) as session:
        with pytest.raises(SessionClosed):
            await session.receive()
        assert b"very wrong" in session.stderr()


async def test_networking_is_off_by_default(engine, container):
    """
    The whole point of the default, so worth checking it really holds.
    """
    id = await container("sh", "-c", "ls /sys/class/net")
    async with engine.start(id) as session:
        assert await session.receive() == "lo"


async def test_networking_can_be_asked_for(engine):
    id = await engine.create_pulling_if_needed(
        IMAGE,
        "sh",
        "-c",
        "ls /sys/class/net",
        network=True,
    )
    try:
        async with engine.start(id) as session:
            assert await session.receive() != "lo"
    finally:
        await engine.remove(id)


async def test_nonexistent_image(engine):
    with pytest.raises(NoSuchImage):
        await engine.create_pulling_if_needed(
            "ghcr.io/Julian/imaged-definitely-not-a-real-image:nope",
        )


async def test_exists(engine, container):
    id = await container("cat")
    assert await engine.exists(id)


async def test_doesnt_exist(engine):
    assert not await engine.exists("imaged-definitely-not-a-container")


async def test_attaching_to_a_running_container(engine, container):
    id = await container("cat")
    if not engine.attaches:
        with pytest.raises(Unsupported):
            async with engine.attach(id):
                pass
        return

    await engine.start_detached(id)
    async with engine.attach(id) as session:
        await session.send("hello")
        assert await session.receive() == "hello"


async def test_building(engine, tmp_path):
    context = tmp_path / "context"
    context.mkdir()
    context.joinpath("Dockerfile").write_text(
        f"FROM {IMAGE}\nRUN echo built > /built\n",
    )
    tag = "imaged-test-build:latest"
    await engine.build(tag=tag, context=context)
    try:
        id = await engine.create(tag, "cat", "/built")
        try:
            async with engine.start(id) as session:
                assert await session.receive() == "built"
        finally:
            await engine.remove(id)
    finally:
        await engine.remove_image(tag)
