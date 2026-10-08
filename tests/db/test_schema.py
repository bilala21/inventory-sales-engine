from __future__ import annotations

from sqlalchemy import Index, UniqueConstraint

from inventory_sales_engine.db.base import Base
from inventory_sales_engine.db import models  # noqa: F401


EXPECTED_TABLES = {
    "system_settings",
    "mailboxes",
    "companies",
    "company_sources",
    "evidence_snapshots",
    "research_runs",
    "qualification_decisions",
    "contacts",
    "contact_sources",
    "verification_checks",
    "product_claims",
    "campaigns",
    "campaign_memberships",
    "sequence_steps",
    "message_drafts",
    "approvals",
    "send_attempts",
    "mail_threads",
    "inbound_messages",
    "reply_classifications",
    "suppression_entries",
    "appointments",
    "customers",
    "experiments",
    "provider_costs",
    "daily_send_counters",
    "jobs",
    "audit_events",
}


def _unique_columns(table_name: str) -> set[tuple[str, ...]]:
    table = Base.metadata.tables[table_name]
    unique_sets = {
        tuple(column.name for column in constraint.columns)
        for constraint in table.constraints
        if isinstance(constraint, UniqueConstraint)
    }
    unique_sets.update(
        tuple(column.name for column in index.columns)
        for index in table.indexes
        if isinstance(index, Index) and index.unique
    )
    return unique_sets


def test_schema_contains_required_system_of_record_tables() -> None:
    assert EXPECTED_TABLES <= set(Base.metadata.tables)


def test_duplicate_barriers_are_database_enforced() -> None:
    assert ("google_place_id",) in _unique_columns("companies")
    assert ("normalized_domain",) in _unique_columns("companies")
    assert ("normalized_email",) in _unique_columns("contacts")
    assert ("idempotency_key",) in _unique_columns("send_attempts")
    assert ("provider_event_id",) in _unique_columns("inbound_messages")
    assert ("suppression_key",) in _unique_columns("suppression_entries")


def test_campaign_membership_has_company_lookup_index() -> None:
    table = Base.metadata.tables["campaign_memberships"]
    indexed = {tuple(column.name for column in index.columns) for index in table.indexes}

    assert ("company_id",) in indexed

