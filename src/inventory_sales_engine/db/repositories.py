from __future__ import annotations

import re
from urllib.parse import urlsplit


def normalize_email(email: str) -> str:
    return email.strip().casefold()


def normalize_domain(value: str) -> str:
    candidate = value.strip()
    if "://" not in candidate:
        candidate = f"https://{candidate}"
    hostname = (urlsplit(candidate).hostname or "").casefold().rstrip(".")
    if hostname.startswith("www."):
        hostname = hostname[4:]
    return hostname


def normalize_company_name(name: str) -> str:
    words_only = re.sub(r"[^\w\s]", " ", name.casefold())
    return " ".join(words_only.split())
