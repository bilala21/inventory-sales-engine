# Inventory Sales Engine Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a REVIEW-only outbound sales MVP that produces evidence-grounded lead review packets and cannot send unless every safety and compliance gate passes.

**Architecture:** A Python 3.12 modular monolith uses PostgreSQL as the system of record and a small set of provider adapters. Deterministic domain services own qualification, campaign state, suppression, limits, review approval, and CRM transitions; LLMs only extract structured evidence, draft from approved facts, and classify replies behind fail-closed validation.

**Tech Stack:** Python 3.12, FastAPI, Pydantic Settings, SQLAlchemy 2, Alembic, PostgreSQL 16, httpx, Google Gmail API client, pytest, pytest-asyncio, Hypothesis.

**Spec:** `docs/superpowers/specs/2026-08-18-inventory-sales-engine-design.md`

## Global Constraints

- The business objective is qualified conversations, demos, pilots, and paying customers, not send volume.
- The first niche is small packaging distributors in Chicago and Illinois.
- The first validation cohort contains at most 100 qualified companies.
- The first 10 qualified companies and proposed emails require operator review before any real outreach.
- `OUTREACH_ENABLED=false` is the default and malformed or missing safety configuration fails closed.
- `MAX_NEW_EMAILS_PER_DAY=20` and `MAX_TOTAL_EMAILS_PER_DAY=40` are initial hard ceilings.
- REVIEW is the only executable approval mode; CONTROLLED_AUTO and FULL_AUTO are rejected.
- Suppression is absolute, global, durable, and checked in the final send transaction.
- Unknown, stale, partial, conflicting, or unverifiable state blocks sending.
- Product and company claims require approved evidence identifiers.
- Gmail ambiguous outcomes never retry automatically.
- No real credentials or external sends are used in automated tests.
- No commits are created unless the user explicitly requests them.

---

### Task 1: Project Foundation and Fail-Closed Configuration

**Files:**
- Create: `AGENTS.md`
- Create: `.env.example`
- Create: `pyproject.toml`
- Create: `src/inventory_sales_engine/__init__.py`
- Create: `src/inventory_sales_engine/config.py`
- Create: `tests/config/test_settings.py`
- Create: `tests/safety/test_secret_files.py`

**Interfaces:**
- Produces: `Settings`, `ApprovalMode`, `get_settings()`
- Invariants: outreach disabled by default; only REVIEW parses; caps cannot exceed approved defaults in the MVP.

- [ ] Write tests proving defaults are fail-closed, malformed booleans fail, missing postal address blocks readiness, and non-REVIEW modes are rejected.
- [ ] Run `python3.12 -m pytest tests/config/test_settings.py -q` and confirm failure because the package does not exist.
- [ ] Implement typed settings and project configuration with no credential values.
- [ ] Run the focused tests and secret-file tests until green.

### Task 2: Domain Types, State Machines, and Audit Events

**Files:**
- Create: `src/inventory_sales_engine/domain/enums.py`
- Create: `src/inventory_sales_engine/domain/models.py`
- Create: `src/inventory_sales_engine/domain/transitions.py`
- Create: `tests/domain/test_transitions.py`

**Interfaces:**
- Produces: lead, campaign, message, verification, reply, and stop enums; immutable decision dataclasses; `transition_lead_stage(current, target)`.
- Invariants: terminal stop states do not reopen automatically; stage skips fail; inbound human activity stops sequences.

- [ ] Write table-driven failing tests for valid and invalid lifecycle transitions.
- [ ] Run `python3.12 -m pytest tests/domain/test_transitions.py -q` and confirm the missing-module failure.
- [ ] Implement the minimum enums and transition graph.
- [ ] Run focused tests until green and refactor only after green.

### Task 3: PostgreSQL Schema and Repository Contracts

**Files:**
- Create: `alembic.ini`
- Create: `alembic/env.py`
- Create: `alembic/versions/0001_initial.py`
- Create: `src/inventory_sales_engine/db/base.py`
- Create: `src/inventory_sales_engine/db/models.py`
- Create: `src/inventory_sales_engine/db/repositories.py`
- Create: `tests/db/test_schema.py`
- Create: `tests/db/test_repository_contracts.py`

**Interfaces:**
- Produces: SQLAlchemy models for the tables in the spec; normalized-key helpers; repository protocols and SQL implementations.
- Constraints: unique Place ID, domain, email, active company campaign, message idempotency key, provider event ID, and suppression key.

- [ ] Write failing schema tests that inspect unique constraints and normalized keys.
- [ ] Run focused schema tests and confirm they fail for missing models.
- [ ] Implement the smallest schema and repositories required by later services.
- [ ] Run schema and repository tests until green.

### Task 4: Suppression, Limits, and Send Eligibility

**Files:**
- Create: `src/inventory_sales_engine/safety/suppression.py`
- Create: `src/inventory_sales_engine/safety/counters.py`
- Create: `src/inventory_sales_engine/safety/eligibility.py`
- Create: `tests/safety/test_suppression.py`
- Create: `tests/safety/test_limits.py`
- Create: `tests/safety/test_send_eligibility.py`
- Create: `tests/safety/test_send_races.py`

**Interfaces:**
- Produces: `SuppressionService.suppress()`, `SuppressionService.is_suppressed()`, `SendEligibilityService.evaluate_and_reserve(command)` returning an allow decision or explicit block reasons.
- Invariants: every check runs at final send time; counters reserve atomically; no direct provider call exists outside the send service.

- [ ] Write failing suppression tests for exact email, normalized email, domain, company, and permanent opt-out behavior.
- [ ] Verify RED with focused pytest commands.
- [ ] Implement suppression minimally and verify GREEN.
- [ ] Write failing decision-table tests covering kill switch, mode, approval hash, confidence, verification, duplicate, cooldown, campaign state, caps, budgets, sync health, first-10 gate, and cohort ceiling.
- [ ] Verify RED, implement the policy engine, and verify GREEN.
- [ ] Add database-backed race tests for concurrent counter reservations and duplicate idempotency keys.

### Task 5: Campaigns, Cohorts, Sequences, and Experiments

**Files:**
- Create: `src/inventory_sales_engine/campaigns/service.py`
- Create: `src/inventory_sales_engine/campaigns/scheduling.py`
- Create: `src/inventory_sales_engine/experiments/service.py`
- Create: `tests/campaigns/test_campaign_state.py`
- Create: `tests/campaigns/test_scheduling.py`
- Create: `tests/campaigns/test_cohort_limits.py`
- Create: `tests/experiments/test_experiments.py`

**Interfaces:**
- Produces: campaign state service, `next_business_day_send_at()`, sequence enrollment, immutable experiment assignment.
- Invariants: four-touch maximum; 3/5/7-business-day follow-up offsets; one active campaign per company; 100 qualified maximum; safety settings cannot be experiment variables.

- [ ] Write and run failing campaign-state and scheduling tests.
- [ ] Implement deterministic state and business-day scheduling.
- [ ] Write and run failing cohort and experiment immutability tests.
- [ ] Implement cohort ceiling and versioned experiment assignments.
- [ ] Run all campaign and experiment tests until green.

### Task 6: Discovery, Safe Website Research, and Qualification

**Files:**
- Create: `src/inventory_sales_engine/providers/places.py`
- Create: `src/inventory_sales_engine/research/fetcher.py`
- Create: `src/inventory_sales_engine/research/evidence.py`
- Create: `src/inventory_sales_engine/research/service.py`
- Create: `src/inventory_sales_engine/qualification/service.py`
- Create: `tests/providers/test_places_contract.py`
- Create: `tests/research/test_fetch_safety.py`
- Create: `tests/research/test_evidence_grounding.py`
- Create: `tests/qualification/test_qualification.py`

**Interfaces:**
- Produces: Places query request builder with exact field mask, public-address validator, immutable evidence records, structured research validation, deterministic `QualificationDecision`.
- Invariants: Google content is transient except Place IDs; private-network and redirected SSRF targets fail; unsupported claims are discarded; hard exclusions override score.

- [ ] Write failing contract tests for Places request fields, query bounds, cost reservation, and transient-field handling.
- [ ] Implement request construction without making network calls in tests.
- [ ] Write failing SSRF, redirect, content-size, content-type, and timeout tests.
- [ ] Implement the safe fetch policy and evidence store interface.
- [ ] Write failing qualification tables for positive, excluded, threshold, and low-confidence cases.
- [ ] Implement deterministic scoring and run the complete task suite.

### Task 7: Contacts, Verification, Product Claims, and Drafting

**Files:**
- Create: `src/inventory_sales_engine/contacts/service.py`
- Create: `src/inventory_sales_engine/verification/service.py`
- Create: `src/inventory_sales_engine/personalization/claims.py`
- Create: `src/inventory_sales_engine/personalization/service.py`
- Create: `tests/contacts/test_contacts.py`
- Create: `tests/verification/test_verification.py`
- Create: `tests/personalization/test_grounded_drafts.py`

**Interfaces:**
- Produces: normalized public contact records, verification policy, approved product-claim registry, evidence-bound `MessageDraft` with content hash.
- Invariants: personal webmail blocked; generated patterns require verification; only VALID is eligible; every factual sentence has evidence or claim provenance; edits invalidate approval.

- [ ] Write failing tests for contact provenance and personal-domain blocking.
- [ ] Implement contact normalization and public-source policy.
- [ ] Write failing verification policy tests for every status and stale checks.
- [ ] Implement the verification adapter contract and policy.
- [ ] Write failing draft-grounding and approval-invalidation tests.
- [ ] Implement deterministic template rendering around validated structured suggestions.
- [ ] Run all task tests until green.

### Task 8: Gmail Submission and Reconciliation

**Files:**
- Create: `src/inventory_sales_engine/providers/gmail.py`
- Create: `src/inventory_sales_engine/mail/service.py`
- Create: `src/inventory_sales_engine/mail/reconciliation.py`
- Create: `tests/mail/test_mime_and_threads.py`
- Create: `tests/mail/test_submission.py`
- Create: `tests/mail/test_reconciliation.py`
- Create: `tests/safety/test_gmail_oauth.py`

**Interfaces:**
- Produces: Gmail adapter protocol and official-client implementation, MIME builder, serialized send service, reconciliation service.
- Invariants: only the send service invokes the adapter; compliant footer is mandatory; Message-ID is stable; ambiguous outcomes pause and never retry automatically; send success is not delivery.

- [ ] Write failing MIME tests for accurate headers, compliance footer, unsubscribe headers, Message-ID, and follow-up threading.
- [ ] Implement MIME construction and verify GREEN.
- [ ] Write failing submission tests for successful reconciliation, provider rejection, timeout, and lost-response ambiguity.
- [ ] Implement the serialized send state machine using fake Gmail adapters in tests.
- [ ] Write OAuth safety tests proving narrow scope declaration and secret redaction behavior.
- [ ] Run all mail and safety tests until green.

### Task 9: Inbound Sync, Reply Classification, and Bounce Stops

**Files:**
- Create: `src/inventory_sales_engine/replies/detection.py`
- Create: `src/inventory_sales_engine/replies/classification.py`
- Create: `src/inventory_sales_engine/replies/service.py`
- Create: `src/inventory_sales_engine/mail/inbound_sync.py`
- Create: `tests/replies/test_unsubscribe_detection.py`
- Create: `tests/replies/test_reply_actions.py`
- Create: `tests/mail/test_inbound_sync.py`
- Create: `tests/mail/test_bounces.py`

**Interfaces:**
- Produces: deterministic unsubscribe/negative detector, structured classifier validation, inbound idempotency, history cursor reconciliation, DSN parser.
- Invariants: any human inbound pauses first; unsubscribe suppresses synchronously; unclear stops for review; history gaps and bounce-like ambiguity fail closed.

- [ ] Write failing table tests for unsubscribe and negative-language variations.
- [ ] Implement deterministic detection.
- [ ] Write failing action tests for all seven reply classes and confidence thresholds.
- [ ] Implement reply actions and suggestion-only QUESTION handling.
- [ ] Write failing sync tests for duplicate notifications, expired watch, history 404, delayed events, and all-mail sweep recovery.
- [ ] Implement idempotent inbound reconciliation and DSN parsing.
- [ ] Run the complete task suite until green.

### Task 10: CRM Metrics, Review Packets, Costs, and Minimal Control API

**Files:**
- Create: `src/inventory_sales_engine/crm/service.py`
- Create: `src/inventory_sales_engine/metrics/service.py`
- Create: `src/inventory_sales_engine/costs/service.py`
- Create: `src/inventory_sales_engine/review_packets/service.py`
- Create: `src/inventory_sales_engine/api.py`
- Create: `src/inventory_sales_engine/__main__.py`
- Create: `tests/crm/test_timeline.py`
- Create: `tests/metrics/test_funnel.py`
- Create: `tests/costs/test_budget.py`
- Create: `tests/review_packets/test_first_ten.py`
- Create: `tests/integration/test_review_mode_pipeline.py`

**Interfaces:**
- Produces: append-only CRM timeline, funnel and validation-target metrics, cost ledger, first-10 review packet, minimal health/campaign/review endpoints.
- Invariants: vanity metrics do not replace funnel outcomes; costs preauthorize before provider calls; review pipeline performs zero external sends without approval and enablement.

- [ ] Write failing CRM timeline and metric tests with hand-derived funnel values.
- [ ] Implement event-derived current state and funnel metrics.
- [ ] Write failing budget preauthorization and provider-cost tests.
- [ ] Implement cost ledger and monthly stop behavior.
- [ ] Write failing first-10 packet tests for evidence, score, contact provenance, verification, and draft provenance.
- [ ] Implement packet export and minimal control endpoints.
- [ ] Write and pass an end-to-end fake-provider pipeline test from discovery through reviewed draft with zero real send.

### Task 11: Operational Documentation and Full Verification

**Files:**
- Create: `README.md`
- Create: `docs/OPERATOR_RUNBOOK.md`
- Create: `docs/SECURITY_AND_COMPLIANCE.md`
- Create: `docs/API_AND_PROVIDER_SETUP.md`
- Create: `experiments.csv`
- Modify: `.env.example`

**Interfaces:**
- Produces: credential-free local setup, explicit pre-send checklist, exact operator actions, provider limitations, experiment ledger headers.

- [ ] Document local PostgreSQL setup, migrations, tests, fake-provider review pipeline, and no-secret handling.
- [ ] Document the mandatory sender-domain, OAuth, postal-address, product-claim, first-10, and enablement gates.
- [ ] Run `python3.12 -m pytest -q` and retain fresh output.
- [ ] Run packaging/import checks and migration validation.
- [ ] Dispatch independent architecture, compliance/deliverability, security, and QA reviewers against the spec and implementation.
- [ ] Fix every Critical or Important finding with a failing regression test first.
- [ ] Re-run the full test suite and report actual counts, limitations, and the one next operator action.
