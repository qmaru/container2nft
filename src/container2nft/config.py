import tomllib
from typing import TypedDict, Literal, cast
from pathlib import Path


class Port(TypedDict):
    host: str
    listen: int
    target: int
    proto: Literal["tcp", "udp"]


class HostService(TypedDict):
    enabled: bool
    type: Literal["host"]
    name: str


class NatService(TypedDict):
    enabled: bool
    type: Literal["nat"]
    name: str
    ip: str
    ports: list[Port]


type Service = HostService | NatService


class ServiceGroup(TypedDict):
    services: list[Service]


type Config = dict[str, ServiceGroup]


def load_config(path: Path | str) -> Config:
    path = Path(path)
    if not path.exists():
        raise RuntimeError(f"Configuration file not found: {path}")

    try:
        with path.open("rb") as f:
            return cast(Config, tomllib.load(f))
    except Exception as e:
        raise RuntimeError(f"Failed to load configuration from {path}: {e}") from e
