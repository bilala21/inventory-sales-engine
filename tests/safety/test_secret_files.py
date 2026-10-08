from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_example_environment_contains_no_secret_values() -> None:
    secret_names = {
        "GOOGLE_PLACES_API_KEY",
        "GMAIL_OAUTH_CLIENT_SECRET",
        "GMAIL_OAUTH_REFRESH_TOKEN",
        "EMAIL_VERIFICATION_API_KEY",
        "LLM_API_KEY",
    }
    values = {}
    for line in (PROJECT_ROOT / ".env.example").read_text().splitlines():
        if "=" in line:
            name, value = line.split("=", 1)
            values[name] = value

    assert all(values[name] == "" for name in secret_names)


def test_sensitive_local_files_are_ignored() -> None:
    patterns = set((PROJECT_ROOT / ".gitignore").read_text().splitlines())

    assert {".env", "credentials.json", "token.json", "*.pem"} <= patterns
