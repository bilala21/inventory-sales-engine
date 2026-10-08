# Inventory Sales Engine

A review-first outbound sales system for one operator, one Google Workspace mailbox, and an initial niche of small packaging distributors in Chicago and Illinois.

The objective is qualified conversations, demos, paid pilots, and customers—not email volume. The first validation cohort is capped at 100 qualified companies, and the first 10 companies plus proposed emails require operator approval before any real outreach.

## Safety Defaults

- `OUTREACH_ENABLED=false`
- `EMERGENCY_STOP=true`
- `APPROVAL_MODE=REVIEW`
- Maximum 20 new and 40 total emails per business day
- `VALID` email verification required
- Global suppression, exact-draft approval, first-10 review, Gmail health, budget, and duplicate checks run at final send time
- CONTROLLED_AUTO and FULL_AUTO are not implemented

## Local Setup

```bash
uv venv .venv --python python3.12
uv pip install -e '.[dev]'
cp .env.example .env
```

Create a local PostgreSQL 16 database and role, then run:

```bash
.venv/bin/alembic upgrade head
.venv/bin/python -m pytest -q
.venv/bin/inventory-sales-engine
```

The local API listens on `127.0.0.1:8000`. It exposes read-only health, safety status, and validation-target endpoints; the MVP intentionally does not provide a broad dashboard or unauthenticated sending controls.

## Provider Policy Blocker

Real cold outreach is not enabled. Google’s current Workspace API policy prohibits Gmail-scope applications from distributing unsolicited commercial mail. The Gmail adapter may be used only for recipients who consented, unless Google gives written approval for the exact use case. A provider or contract that explicitly permits compliant cold B2B outreach must be selected before the production send coordinator is implemented.

## Validation Targets

- 100 qualified companies
- 50 or more delivered targeted emails
- 5 meaningful conversations
- 3 demos
- 1 paid pilot

These are validation targets, not guarantees. Gmail acceptance is not counted as delivery, and a reply is not counted as a customer.

## Documentation

- Approved architecture: `docs/superpowers/specs/2026-08-18-inventory-sales-engine-design.md`
- Implementation plan: `docs/superpowers/plans/2026-08-18-inventory-sales-engine.md`
- Operator procedure: `docs/OPERATOR_RUNBOOK.md`
- Security and compliance: `docs/SECURITY_AND_COMPLIANCE.md`
- Provider setup and costs: `docs/API_AND_PROVIDER_SETUP.md`
