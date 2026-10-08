from __future__ import annotations

import pytest

from inventory_sales_engine.contacts.service import ContactPolicyError, create_contact


def test_public_business_contact_is_normalized_and_accepted() -> None:
    contact = create_contact(
        company_id="company-1",
        name="Sara Jones",
        role="Operations Manager",
        email=" Sara@ExamplePackaging.COM ",
        source_type="PUBLIC_WEBSITE",
        source_reference="https://examplepackaging.com/contact",
        generated_pattern=False,
    )

    assert contact.email == "sara@examplepackaging.com"
    assert contact.role == "Operations Manager"


@pytest.mark.parametrize("email", ["owner@gmail.com", "buyer@yahoo.com", "ops@outlook.com"])
def test_personal_webmail_domains_are_blocked(email: str) -> None:
    with pytest.raises(ContactPolicyError, match="personal webmail"):
        create_contact(
            company_id="company-1",
            name="Owner",
            role="Owner",
            email=email,
            source_type="PUBLIC_WEBSITE",
            source_reference="https://example.com/contact",
            generated_pattern=False,
        )


def test_generated_pattern_is_marked_non_sendable_until_verified() -> None:
    contact = create_contact(
        company_id="company-1",
        name="Sara Jones",
        role="Purchasing Manager",
        email="sara@examplepackaging.com",
        source_type="GENERATED_PATTERN",
        source_reference="provider-pattern",
        generated_pattern=True,
    )

    assert contact.requires_verification is True


def test_unapproved_role_is_rejected() -> None:
    with pytest.raises(ContactPolicyError, match="role"):
        create_contact(
            company_id="company-1",
            name="Sara",
            role="Intern",
            email="sara@example.com",
            source_type="PUBLIC_WEBSITE",
            source_reference="https://example.com",
            generated_pattern=False,
        )

