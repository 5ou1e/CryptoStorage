import time

import anyio
from fastapi import Depends, FastAPI

app = FastAPI()


def sync_dependency_one() -> str:
    time.sleep(0.00000001)
    return "sync_dependency_one"


def sync_dependency_two(
    injected_sync_one: str = Depends(sync_dependency_one),
) -> list[str]:
    time.sleep(0.00000001)
    return [injected_sync_one, "sync_dependency_two"]


def sync_dependency_three(
    injected_sync_two: list[str] = Depends(sync_dependency_two),
) -> list[str]:
    time.sleep(0.00000001)
    return [*injected_sync_two, "sync_dependency_three"]


async def async_dependency_one() -> str:
    await anyio.sleep(0.00000001)
    return "async_dependency_one"


async def async_dependency_two(
    injected_async_one: str = Depends(async_dependency_one),
) -> list[str]:
    await anyio.sleep(0.00000001)
    return [injected_async_one, "async_dependency_two"]


async def async_dependency_three(
    injected_async_two: list[str] = Depends(async_dependency_two),
) -> list[str]:
    await anyio.sleep(0.00000001)
    return [*injected_async_two, "async_dependency_three"]


async def dependencies_mixed(
    injected_sync_three: list[str] = Depends(sync_dependency_three),
    injected_async_three: list[str] = Depends(async_dependency_three),
) -> tuple[list[str], list[str]]:
    return injected_sync_three, injected_async_three


@app.get("/async-dependencies-sync")
async def async_dependencies_sync(
    injected_sync_one: str = Depends(sync_dependency_one),
    injected_sync_two: list[str] = Depends(sync_dependency_two),
    injected_sync_three: list[str] = Depends(sync_dependency_three),
) -> list[str]:
    return injected_sync_three


@app.get("/async-dependencies-async")
async def async_dependencies_async(
    injected_async_one: str = Depends(async_dependency_one),
    injected_async_two: list[str] = Depends(async_dependency_two),
    injected_async_three: list[str] = Depends(async_dependency_three),
) -> list[str]:
    return injected_async_three


@app.get("/async-dependencies-mixed")
async def async_dependencies_mixed(
    injected_sync_one: str = Depends(sync_dependency_one),
    injected_sync_two: list[str] = Depends(sync_dependency_two),
    injected_sync_three: list[str] = Depends(sync_dependency_three),
    injected_async_one: str = Depends(async_dependency_one),
    injected_async_two: list[str] = Depends(async_dependency_two),
    injected_async_three: list[str] = Depends(async_dependency_three),
    injected_mixed: tuple[list[str], list[str]] = Depends(dependencies_mixed),
) -> tuple[list[str], list[str]]:
    return injected_mixed