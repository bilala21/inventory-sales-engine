from __future__ import annotations

import ipaddress
import socket
from dataclasses import dataclass
from typing import Callable, Iterable
from urllib.parse import urlsplit


class UnsafeFetchTarget(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class FetchPolicy:
    max_bytes: int = 1_000_000
    allowed_content_types: frozenset[str] = frozenset({"text/html", "text/plain"})
    timeout_seconds: float = 8.0
    max_redirects: int = 3


AddressResolver = Callable[[str], Iterable[str]]


def _resolve_addresses(hostname: str) -> tuple[str, ...]:
    return tuple(
        address[4][0]
        for address in socket.getaddrinfo(hostname, None, type=socket.SOCK_STREAM)
    )


def _is_public_ip(value: str) -> bool:
    address = ipaddress.ip_address(value)
    return address.is_global


def validate_public_url(url: str, *, resolver: AddressResolver = _resolve_addresses) -> str:
    parsed = urlsplit(url)
    if parsed.scheme not in {"http", "https"}:
        raise UnsafeFetchTarget("Only HTTP and HTTPS are allowed")
    if parsed.username is not None or parsed.password is not None:
        raise UnsafeFetchTarget("Embedded credentials are not allowed")
    hostname = parsed.hostname
    if not hostname or hostname.casefold() == "localhost" or hostname.casefold().endswith(".local"):
        raise UnsafeFetchTarget("A public hostname is required")
    try:
        ipaddress.ip_address(hostname)
        addresses = (hostname,)
    except ValueError:
        try:
            addresses = tuple(resolver(hostname))
        except OSError as error:
            raise UnsafeFetchTarget("Hostname could not be safely resolved") from error
    if not addresses or any(not _is_public_ip(address) for address in addresses):
        raise UnsafeFetchTarget("Private or reserved network targets are blocked")
    return url


def validate_fetch_response(
    *, content_type: str, content_length: int, policy: FetchPolicy
) -> None:
    media_type = content_type.partition(";")[0].strip().casefold()
    if media_type not in policy.allowed_content_types:
        raise UnsafeFetchTarget("Response content type is not allowed")
    if content_length < 0 or content_length > policy.max_bytes:
        raise UnsafeFetchTarget("Response size exceeds the configured limit")

