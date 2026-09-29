"""Resolve the execution target before any browser navigation."""

import re
from dataclasses import dataclass
from typing import Self
from urllib.parse import urlsplit

MOCK_PORT = 8090


def worker_port(worker: str | None, base: int = MOCK_PORT) -> int:
    """Each pytest-xdist worker (gw0, gw1, ...) serves the mock on its own port."""
    if not worker:
        return base
    match = re.fullmatch(r"gw(\d+)", worker)
    if match is None:
        raise ValueError(f"Unexpected pytest-xdist worker id: {worker!r}")
    return base + 1 + int(match[1])


def check_parallel(target: str, workers: object) -> None:
    """Live runs stay serial so the store sees one browser at a time."""
    if target == "live" and workers not in (None, 0, "0"):
        raise ValueError("Live runs are serial: remove -n/--numprocesses")


@dataclass(frozen=True)
class Settings:
    target: str
    base_url: str
    external_server: bool = False
    seed: int = 1729
    navigation_timeout: int = 30_000
    action_timeout: int = 10_000
    assertion_timeout: int = 5_000

    @classmethod
    def resolve(
        cls,
        target: str = "mock",
        base_url: str | None = None,
        seed: int = 1729,
        mock_port: int = MOCK_PORT,
    ) -> Self:
        if target not in {"mock", "live"}:
            raise ValueError("TARGET must be 'mock' or 'live'")
        default = (
            f"http://127.0.0.1:{mock_port}"
            if target == "mock"
            else "https://www.pgoriginal.com"
        )
        url = base_url if base_url is not None else default
        parts = urlsplit(url)
        if (
            not parts.hostname
            or parts.username is not None
            or parts.password is not None
            or parts.query
            or parts.fragment
            or parts.path not in {"", "/"}
        ):
            raise ValueError("Base URL must be an origin without credentials or a path")
        port = parts.port
        if target == "mock":
            valid = parts.scheme == "http" and parts.hostname in {
                "127.0.0.1",
                "localhost",
                "::1",
            }
        else:
            valid = (
                parts.scheme == "https"
                and parts.hostname == "www.pgoriginal.com"
                and port in {None, 443}
            )
        if not valid or port == 0:
            raise ValueError(f"Base URL is not permitted for target {target!r}")
        return cls(target, url.rstrip("/"), base_url is not None, seed)


def eligible(markers: set[str], target: str) -> bool:
    if {"mock_only", "live_safe"} <= markers:
        raise ValueError("A test cannot be both mock_only and live_safe")
    return target == "mock" or bool(markers & {"framework", "live_safe"})
