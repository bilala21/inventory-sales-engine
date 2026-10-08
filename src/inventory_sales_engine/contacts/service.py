from __future__ import annotations

from dataclasses import dataclass

from email_validator import EmailNotValidError, validate_email

from inventory_sales_engine.db.repositories import normalize_email


class ContactPolicyError(ValueError):
    pass


PERSONAL_EMAIL_DOMAINS = frozenset(
    {"gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "icloud.com", "aol.com"}
)
APPROVED_ROLE_TERMS = frozenset(
    {
        "owner",
        "operations",
        "supply chain",
        "inventory",
        "purchasing",
        "procurement",
        "warehouse",
        "general manager",
    }
)


@dataclass(frozen=True, slots=True)
class ContactRecord:
    company_id: str
    name: str | None
    role: str
    email: str
    source_type: str
    source_reference: str
    requires_verification: bool


def create_contact(
    *,
    company_id: str,
    name: str | None,
    role: str,
    email: str,
    source_type: str,
    source_reference: str,
    generated_pattern: bool,
) -> ContactRecord:
    if not any(term in role.casefold() for term in APPROVED_ROLE_TERMS):
        raise ContactPolicyError("Contact role is outside the approved operational roles")
    if not source_reference.strip():
        raise ContactPolicyError("A public or licensed source reference is required")
    normalized = normalize_email(email)
    try:
        validated = validate_email(normalized, check_deliverability=False)
    except EmailNotValidError as error:
        raise ContactPolicyError("Contact email is malformed") from error
    domain = validated.domain.casefold()
    if domain in PERSONAL_EMAIL_DOMAINS:
        raise ContactPolicyError("personal webmail domains are blocked")
    return ContactRecord(
        company_id=company_id,
        name=name.strip() if name else None,
        role=role.strip(),
        email=validated.normalized,
        source_type=source_type,
        source_reference=source_reference,
        requires_verification=generated_pattern,
    )
