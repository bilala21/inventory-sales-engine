from __future__ import annotations

import pytest

from inventory_sales_engine.research.fetcher import (
    FetchPolicy,
    UnsafeFetchTarget,
    validate_fetch_response,
    validate_public_url,
)


@pytest.mark.parametrize(
    "url",
    [
        "file:///etc/passwd",
        "http://127.0.0.1/admin",
        "http://localhost/admin",
        "http://169.254.169.254/latest/meta-data",
        "http://10.0.0.5/private",
        "https://user:password@example.com",
    ],
)
def test_private_or_non_http_targets_are_blocked(url: str) -> None:
    with pytest.raises(UnsafeFetchTarget):
        validate_public_url(url)


def test_redirect_target_is_revalidated() -> None:
    validate_public_url("https://93.184.216.34")
    with pytest.raises(UnsafeFetchTarget):
        validate_public_url("http://127.0.0.1/redirected")


def test_response_policy_blocks_oversize_and_wrong_content_type() -> None:
    policy = FetchPolicy(max_bytes=100, allowed_content_types=frozenset({"text/html"}))

    with pytest.raises(UnsafeFetchTarget, match="size"):
        validate_fetch_response(content_type="text/html", content_length=101, policy=policy)
    with pytest.raises(UnsafeFetchTarget, match="content type"):
        validate_fetch_response(content_type="application/pdf", content_length=50, policy=policy)


def test_fetch_policy_has_conservative_time_and_redirect_limits() -> None:
    policy = FetchPolicy()

    assert policy.timeout_seconds <= 10
    assert policy.max_redirects <= 3

