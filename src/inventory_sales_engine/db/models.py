from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    JSON,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from inventory_sales_engine.db.base import Base, IdMixin, TimestampMixin, utc_now


class SystemSetting(Base, TimestampMixin):
    __tablename__ = "system_settings"
    key: Mapped[str] = mapped_column(String(120), primary_key=True)
    value: Mapped[dict] = mapped_column(JSON, nullable=False)


class Mailbox(Base, IdMixin, TimestampMixin):
    __tablename__ = "mailboxes"
    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    sync_healthy: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    gmail_history_id: Mapped[str | None] = mapped_column(String(100))


class Company(Base, IdMixin, TimestampMixin):
    __tablename__ = "companies"
    name: Mapped[str] = mapped_column(String(300), nullable=False)
    normalized_name: Mapped[str] = mapped_column(String(300), nullable=False, index=True)
    normalized_domain: Mapped[str | None] = mapped_column(String(253), unique=True)
    google_place_id: Mapped[str | None] = mapped_column(String(255), unique=True)
    website_url: Mapped[str | None] = mapped_column(Text)
    phone: Mapped[str | None] = mapped_column(String(80))
    address: Mapped[str | None] = mapped_column(Text)
    category: Mapped[str | None] = mapped_column(String(200))
    country_code: Mapped[str] = mapped_column(String(2), default="US", nullable=False)
    lead_stage: Mapped[str] = mapped_column(String(40), default="DISCOVERED", nullable=False)


class CompanySource(Base, IdMixin, TimestampMixin):
    __tablename__ = "company_sources"
    company_id: Mapped[str] = mapped_column(ForeignKey("companies.id"), nullable=False, index=True)
    source_type: Mapped[str] = mapped_column(String(60), nullable=False)
    source_reference: Mapped[str] = mapped_column(Text, nullable=False)
    independently_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class EvidenceSnapshot(Base, IdMixin):
    __tablename__ = "evidence_snapshots"
    company_id: Mapped[str] = mapped_column(ForeignKey("companies.id"), nullable=False, index=True)
    source_url: Mapped[str] = mapped_column(Text, nullable=False)
    retrieved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    page_title: Mapped[str | None] = mapped_column(Text)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    excerpt: Mapped[str] = mapped_column(Text, nullable=False)
    extraction_metadata: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)


class ResearchRun(Base, IdMixin, TimestampMixin):
    __tablename__ = "research_runs"
    company_id: Mapped[str] = mapped_column(ForeignKey("companies.id"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(40), nullable=False)
    confidence_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    fit_reason: Mapped[str | None] = mapped_column(Text)
    pain_point_hypothesis: Mapped[str | None] = mapped_column(Text)
    personalization_fact: Mapped[str | None] = mapped_column(Text)


class QualificationDecision(Base, IdMixin):
    __tablename__ = "qualification_decisions"
    company_id: Mapped[str] = mapped_column(ForeignKey("companies.id"), nullable=False, index=True)
    research_run_id: Mapped[str] = mapped_column(ForeignKey("research_runs.id"), nullable=False)
    policy_version: Mapped[str] = mapped_column(String(50), nullable=False)
    fit_score: Mapped[int] = mapped_column(Integer, nullable=False)
    qualified: Mapped[bool] = mapped_column(Boolean, nullable=False)
    hard_exclusions: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    reasons: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    decided_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)


class Contact(Base, IdMixin, TimestampMixin):
    __tablename__ = "contacts"
    company_id: Mapped[str] = mapped_column(ForeignKey("companies.id"), nullable=False, index=True)
    name: Mapped[str | None] = mapped_column(String(250))
    role: Mapped[str | None] = mapped_column(String(150))
    email: Mapped[str] = mapped_column(String(320), nullable=False)
    normalized_email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False)
    email_confidence: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


class ContactSource(Base, IdMixin, TimestampMixin):
    __tablename__ = "contact_sources"
    contact_id: Mapped[str] = mapped_column(ForeignKey("contacts.id"), nullable=False, index=True)
    source_type: Mapped[str] = mapped_column(String(60), nullable=False)
    source_reference: Mapped[str] = mapped_column(Text, nullable=False)


class VerificationCheck(Base, IdMixin):
    __tablename__ = "verification_checks"
    contact_id: Mapped[str] = mapped_column(ForeignKey("contacts.id"), nullable=False, index=True)
    provider: Mapped[str] = mapped_column(String(80), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    checked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    provider_reference: Mapped[str | None] = mapped_column(String(255))


class ProductClaim(Base, IdMixin, TimestampMixin):
    __tablename__ = "product_claims"
    claim_text: Mapped[str] = mapped_column(Text, nullable=False)
    approved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    capability_reference: Mapped[str] = mapped_column(String(255), nullable=False)


class Experiment(Base, IdMixin, TimestampMixin):
    __tablename__ = "experiments"
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    configuration: Mapped[dict] = mapped_column(JSON, nullable=False)
    locked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    __table_args__ = (UniqueConstraint("name", "version"),)


class Campaign(Base, IdMixin, TimestampMixin):
    __tablename__ = "campaigns"
    experiment_id: Mapped[str] = mapped_column(ForeignKey("experiments.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    state: Mapped[str] = mapped_column(String(30), default="DRAFT", nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    niche: Mapped[str] = mapped_column(String(150), nullable=False)
    geography: Mapped[str] = mapped_column(String(150), nullable=False)


class CampaignMembership(Base, IdMixin, TimestampMixin):
    __tablename__ = "campaign_memberships"
    campaign_id: Mapped[str] = mapped_column(ForeignKey("campaigns.id"), nullable=False)
    company_id: Mapped[str] = mapped_column(ForeignKey("companies.id"), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    stopped_reason: Mapped[str | None] = mapped_column(String(60))
    __table_args__ = (
        Index("ix_campaign_memberships_company_id", "company_id"),
        Index(
            "uq_active_campaign_per_company",
            "company_id",
            unique=True,
            postgresql_where=text("active = true"),
            sqlite_where=text("active = 1"),
        ),
    )


class SequenceStep(Base, IdMixin, TimestampMixin):
    __tablename__ = "sequence_steps"
    campaign_id: Mapped[str] = mapped_column(ForeignKey("campaigns.id"), nullable=False)
    step_number: Mapped[int] = mapped_column(Integer, nullable=False)
    business_day_offset: Mapped[int] = mapped_column(Integer, nullable=False)
    template_version: Mapped[str] = mapped_column(String(80), nullable=False)
    __table_args__ = (UniqueConstraint("campaign_id", "step_number"),)


class MessageDraft(Base, IdMixin, TimestampMixin):
    __tablename__ = "message_drafts"
    membership_id: Mapped[str] = mapped_column(ForeignKey("campaign_memberships.id"), nullable=False)
    contact_id: Mapped[str] = mapped_column(ForeignKey("contacts.id"), nullable=False)
    sequence_step_id: Mapped[str] = mapped_column(ForeignKey("sequence_steps.id"), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    subject: Mapped[str] = mapped_column(String(250), nullable=False)
    body_text: Mapped[str] = mapped_column(Text, nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    claim_references: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    state: Mapped[str] = mapped_column(String(40), default="DRAFT", nullable=False)
    __table_args__ = (UniqueConstraint("membership_id", "sequence_step_id", "version"),)


class Approval(Base, IdMixin):
    __tablename__ = "approvals"
    message_draft_id: Mapped[str] = mapped_column(ForeignKey("message_drafts.id"), nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    approved_by: Mapped[str] = mapped_column(String(200), nullable=False)
    approved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    __table_args__ = (UniqueConstraint("message_draft_id", "content_hash"),)


class SendAttempt(Base, IdMixin, TimestampMixin):
    __tablename__ = "send_attempts"
    message_draft_id: Mapped[str] = mapped_column(ForeignKey("message_drafts.id"), nullable=False)
    idempotency_key: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    state: Mapped[str] = mapped_column(String(40), nullable=False)
    gmail_message_id: Mapped[str | None] = mapped_column(String(255), unique=True)
    rfc_message_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    error_code: Mapped[str | None] = mapped_column(String(120))


class MailThread(Base, IdMixin, TimestampMixin):
    __tablename__ = "mail_threads"
    membership_id: Mapped[str] = mapped_column(ForeignKey("campaign_memberships.id"), unique=True, nullable=False)
    gmail_thread_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    root_rfc_message_id: Mapped[str] = mapped_column(String(255), nullable=False)


class InboundMessage(Base, IdMixin):
    __tablename__ = "inbound_messages"
    mailbox_id: Mapped[str] = mapped_column(ForeignKey("mailboxes.id"), nullable=False)
    membership_id: Mapped[str | None] = mapped_column(ForeignKey("campaign_memberships.id"))
    provider_event_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    gmail_message_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    from_email: Mapped[str] = mapped_column(String(320), nullable=False)
    subject: Mapped[str] = mapped_column(Text, default="", nullable=False)
    body_text: Mapped[str] = mapped_column(Text, default="", nullable=False)
    unresolved: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class ReplyClassification(Base, IdMixin):
    __tablename__ = "reply_classifications"
    inbound_message_id: Mapped[str] = mapped_column(ForeignKey("inbound_messages.id"), unique=True, nullable=False)
    reply_class: Mapped[str] = mapped_column(String(40), nullable=False)
    confidence_score: Mapped[int] = mapped_column(Integer, nullable=False)
    deterministic: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    suggested_response: Mapped[str | None] = mapped_column(Text)
    classified_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)


class SuppressionEntry(Base, IdMixin):
    __tablename__ = "suppression_entries"
    suppression_key: Mapped[str] = mapped_column(String(500), unique=True, nullable=False)
    scope: Mapped[str] = mapped_column(String(30), nullable=False)
    reason: Mapped[str] = mapped_column(String(80), nullable=False)
    source: Mapped[str] = mapped_column(String(80), nullable=False)
    suppressed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class Appointment(Base, IdMixin, TimestampMixin):
    __tablename__ = "appointments"
    company_id: Mapped[str] = mapped_column(ForeignKey("companies.id"), nullable=False)
    contact_id: Mapped[str] = mapped_column(ForeignKey("contacts.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False)
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    booking_reference: Mapped[str | None] = mapped_column(String(255))


class Customer(Base, IdMixin, TimestampMixin):
    __tablename__ = "customers"
    company_id: Mapped[str] = mapped_column(ForeignKey("companies.id"), unique=True, nullable=False)
    pilot_started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    setup_price: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    monthly_price: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))


class ProviderCost(Base, IdMixin):
    __tablename__ = "provider_costs"
    provider: Mapped[str] = mapped_column(String(80), nullable=False)
    operation: Mapped[str] = mapped_column(String(120), nullable=False)
    company_id: Mapped[str | None] = mapped_column(ForeignKey("companies.id"))
    estimated_cost_usd: Mapped[Decimal] = mapped_column(Numeric(12, 6), default=0, nullable=False)
    actual_cost_usd: Mapped[Decimal | None] = mapped_column(Numeric(12, 6))
    incurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)


class DailySendCounter(Base):
    __tablename__ = "daily_send_counters"
    mailbox_id: Mapped[str] = mapped_column(ForeignKey("mailboxes.id"), primary_key=True)
    send_date: Mapped[date] = mapped_column(Date, primary_key=True)
    new_email_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_email_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


class Job(Base, IdMixin, TimestampMixin):
    __tablename__ = "jobs"
    job_type: Mapped[str] = mapped_column(String(80), nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False)
    payload: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    run_after: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


class AuditEvent(Base, IdMixin):
    __tablename__ = "audit_events"
    event_type: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(String(80), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    data: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

