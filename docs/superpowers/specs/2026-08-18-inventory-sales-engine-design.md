# Inventory Sales Engine Design Specification

**Status:** Approved for implementation on 2026-08-18

## 1. Objective

Inventory Sales Engine is a single-operator, U.S.-only outbound sales system for acquiring paying customers for an existing inventory management product.

The business funnel is the governing objective:

```text
qualified companies -> meaningful conversations -> demos -> paid pilots -> customers
```

Engineering completion, email volume, opens, and raw reply counts are not success criteria.

The first validation targets are:

- 100 genuinely qualified companies maximum
- 50 or more successfully delivered targeted messages
- 5 meaningful conversations
- 3 demos
- 1 paid pilot

These are validation targets, not guarantees or established conversion rates.

Gmail does not provide a universal delivery receipt. Reporting must therefore keep `SENT_CONFIRMED`, `BOUNCED`, `DELIVERED_DETECTED`, and `NOT_BOUNCED_AFTER_72H` separate. The 50-message validation target is reported using detected delivery where available and otherwise as sent-confirmed with no detected bounce; the system must not relabel that estimate as confirmed delivery.

## 2. Approved Operating Scope

- One operator
- One Google Workspace mailbox
- U.S.-only outreach
- First niche: small packaging distributors in Chicago and Illinois
- PostgreSQL modular monolith
- REVIEW mode only
- No CONTROLLED_AUTO runtime path
- No FULL_AUTO runtime path
- No live outreach until the complete safety suite passes and the operator explicitly sets `OUTREACH_ENABLED=true`
- Before any real outreach, the operator must review the first 10 qualified companies and their proposed emails

The first cohort has a hard ceiling of 100 qualified companies. Reaching the ceiling pauses discovery and requires a cohort review before another cohort can exist.

## 3. Product Positioning

Approved positioning:

> We help distributors and small manufacturers automatically monitor inventory, flag low-stock products, and reduce manual reorder work without forcing them to replace their existing spreadsheet or workflow.

Messages may reference only capabilities confirmed by the operator or represented in the system's approved product-claims registry. The system must not invent:

- customer results
- savings or ROI
- revenue effects
- testimonials or case studies
- integrations
- user counts
- product capabilities
- company facts
- pain points presented as known facts

A pain point may be stated only as a clearly labeled question or hypothesis derived from evidence.

## 4. Architecture

The application is a Python 3.12 modular monolith with one web process and one or more worker processes.

Primary technologies:

- FastAPI for HTTP and internal control APIs
- PostgreSQL 16 as the system of record
- SQLAlchemy 2 and Alembic for persistence and migrations
- Pydantic Settings for fail-closed configuration
- PostgreSQL-backed durable jobs and leases; no Redis dependency in the MVP
- Provider adapters for Google Places, website fetching, LLMs, contact discovery, email verification, Gmail, and booking links
- Server-rendered operational pages or a minimal JSON API; visual dashboard work is subordinate to the pipeline

The modules share one database but expose explicit service interfaces. External providers never own internal campaign, suppression, approval, or CRM truth.

## 5. Domain Boundaries

### 5.1 Discovery

Runs configurable Google Places Text Search queries for packaging distributors in the approved geography.

Google responses are transient discovery inputs. The system may permanently store Place IDs and query provenance. Other company fields must be independently verified from permitted first-party or licensed sources before becoming durable CRM facts.

Discovery deduplicates by:

1. Google Place ID
2. normalized verified domain
3. normalized company name plus normalized address

### 5.2 Evidence and Research

The website fetcher accesses public first-party business pages only. It must:

- honor site restrictions and provider terms
- reject authentication walls, CAPTCHA challenges, and prohibited sources
- allow only HTTP and HTTPS
- block private, loopback, link-local, multicast, reserved, and cloud-metadata addresses
- revalidate every redirect target
- limit redirects, response size, content type, and request duration
- avoid browser JavaScript execution in the MVP

Fetched content is hostile data. It cannot issue instructions to the model or application.

Research creates immutable evidence records containing source URL, retrieval time, page title, content hash, relevant excerpt, and extraction metadata.

The LLM returns structured candidate observations. Every accepted observation must reference evidence IDs. Missing, conflicting, stale, or unsupported claims lower confidence and cannot become personalization facts.

### 5.3 Qualification

Qualification is deterministic. The LLM cannot modify weights, thresholds, hard exclusions, or scores directly.

The score contains inspectable dimensions:

- business model and niche fit
- evidence of physical-product inventory
- recurring supplier or replenishment model
- warehouse, SKU, or distribution evidence
- active first-party website
- plausible inventory-workflow pain stated as a hypothesis

Hard exclusions include:

- consumer or hobby business
- no meaningful physical inventory
- huge enterprise without a specific supported pain
- clear sophisticated enterprise inventory platform without a specific supported gap
- non-U.S. company
- prohibited or unverifiable source provenance

The initial configurable qualification threshold is 70 out of 100. Qualification also requires a minimum evidence confidence. A high score with low confidence is blocked.

### 5.4 Contacts and Verification

Contact priority:

1. publicly listed direct business email for an approved role
2. publicly listed department email
3. configured reputable contact provider

Approved roles include owner, operations, purchasing, procurement, supply chain, inventory, warehouse, and general management.

Personal webmail domains are blocked by default. Generated email patterns are never sendable without provider verification.

Verification policy:

- `VALID`: eligible for review
- `ACCEPT_ALL`: manual exception only; blocked by default
- `UNKNOWN`: blocked
- `INVALID`: permanently blocked

Verification records contain provider, status, checked time, provider reference, and expiry.

### 5.5 Personalization

Drafts may use only approved product claims, immutable evidence facts, and verified contact data. Each rendered claim stores its evidence or product-claim identifier.

Emails remain concise:

1. relevant evidence-backed observation
2. operational pain question
3. short outcome-oriented explanation
4. one low-friction CTA
5. required compliance footer and opt-out

Draft changes create new versions. Approval applies to one exact content hash and is invalidated by any later edit.

### 5.6 Review and Send Policy

REVIEW is the only executable mode.

Every external Gmail submission must obtain a transactional `SendEligibilityDecision` immediately before sending. The decision blocks unless all checks pass:

- `OUTREACH_ENABLED` is exactly `true`
- emergency stop is not active
- mailbox and campaign are enabled
- campaign is in `RUNNING` state
- the exact draft version has explicit operator approval
- the first-10 review checkpoint is complete before any real send
- company and contact satisfy qualification and confidence thresholds
- current verification result is `VALID`
- email, domain, and company are not suppressed
- no inbound human reply, negative response, bounce stop, or unresolved inbound event exists
- recipient and company cooldowns have elapsed
- no duplicate message or equivalent sequence step exists
- company has no other active campaign
- sequence will remain at four messages or fewer
- new-email daily cap will remain at or below 20
- total-email daily cap will remain at or below the configured value, initially 40
- 100-qualified-company cohort ceiling has not been exceeded
- provider and monthly budgets remain available
- Gmail synchronization and deliverability health are healthy

The decision and counter reservation occur under database locks. Workers carry identifiers only and must reload current state before acting.

No subsystem may call the Gmail adapter directly except the send service after a successful policy decision.

### 5.7 Gmail and Delivery State

Gmail uses OAuth. Credentials and refresh tokens are never committed or logged and must be encrypted at rest outside local development.

Minimum intended scopes:

- `gmail.send`
- `gmail.readonly`

Outbound state distinguishes:

- `APPROVED`
- `RESERVED`
- `SUBMITTING`
- `SENT_CONFIRMED`
- `UNKNOWN_SEND_STATE`
- `BOUNCED`

A Gmail API success is not recorded as delivered. Delivery remains unknown unless reliable delivery or bounce evidence exists.

The system generates and stores an RFC Message-ID and Gmail identifiers. Follow-ups use the same Gmail thread with matching subject, `References`, and `In-Reply-To` headers.

If the provider outcome is ambiguous, the message enters `UNKNOWN_SEND_STATE`, the recipient sequence pauses, and the system does not retry automatically.

### 5.8 Reply and Bounce Processing

Inbound monitoring uses Gmail watch notifications, `history.list` reconciliation, periodic all-mail safety sweeps, and daily watch renewal.

Any inbound human message pauses the sequence before classification.

Deterministic unsubscribe and negative-language rules run before the LLM. Reply classes are:

- `INTERESTED`
- `QUESTION`
- `NOT_INTERESTED`
- `UNSUBSCRIBE`
- `REFERRAL`
- `OUT_OF_OFFICE`
- `UNCLEAR`

Actions:

- `UNSUBSCRIBE`: immediate permanent suppression
- `NOT_INTERESTED`: terminal stop
- `INTERESTED`: terminal sequence stop and immediate operator notification
- `QUESTION`: sequence stop and suggested response for operator review
- `REFERRAL`: sequence stop and manual review
- `OUT_OF_OFFICE`: careful reschedule only when a return date is confidently extracted; otherwise manual review
- `UNCLEAR`: sequence stop and manual review

Bounce detection parses delivery-status notifications and provider warnings. Because Gmail does not expose a perfect bounce object, unresolved bounce-like messages stop the sequence pending review.

### 5.9 CRM, Timeline, and Experiments

The CRM stores a current state plus an append-only event timeline. Terminal stop states cannot reopen automatically.

Required stages:

- `DISCOVERED`
- `RESEARCHED`
- `QUALIFIED`
- `CONTACT_FOUND`
- `VERIFIED`
- `READY_TO_SEND`
- `CONTACTED`
- `FOLLOW_UP`
- `REPLIED`
- `INTERESTED`
- `DEMO_BOOKED`
- `PILOT`
- `CUSTOMER`
- `LOST`
- `UNSUBSCRIBED`

Experiments lock niche, geography, audience, offer, CTA, template version, and qualification policy version for a cohort. Safety settings are never experiment variables.

At this volume, experiments are sequential cohorts rather than simultaneous multivariate tests.

### 5.10 Cost and Failure Controls

Every provider call records estimated and actual cost where available.

Discovery pauses before a call that would exceed the monthly budget. Cost reporting includes:

- monthly cost estimate
- cost per qualified lead
- cost per meaningful conversation
- cost per demo
- cost per pilot
- cost per customer

Commercial failure rules:

- discovery pauses at 100 qualified companies
- zero meaningful conversations after the first validated cohort triggers a diagnostic report and blocks cohort expansion
- a segment with 15 to 20 contacted, delivered accounts and zero qualified replies is flagged for early review
- approximately five completed demos with no pilot progression pauses the offer for review

The diagnostic reviews ICP, evidence quality, contact quality, message, offer, deliverability, and pilot design. It never recommends volume expansion as the default remedy.

## 6. Data Model

Primary tables:

- `system_settings`
- `mailboxes`
- `companies`
- `company_sources`
- `evidence_snapshots`
- `research_runs`
- `qualification_decisions`
- `contacts`
- `contact_sources`
- `verification_checks`
- `product_claims`
- `campaigns`
- `campaign_memberships`
- `sequence_steps`
- `message_drafts`
- `approvals`
- `send_attempts`
- `mail_threads`
- `inbound_messages`
- `reply_classifications`
- `suppression_entries`
- `appointments`
- `customers`
- `experiments`
- `provider_costs`
- `daily_send_counters`
- `jobs`
- `audit_events`

Database constraints enforce unique Place IDs where present, normalized domains, normalized contact emails, active campaign membership per company, message idempotency keys, provider event IDs, and suppression keys.

## 7. Compliance and Deliverability

Every commercial message includes:

- accurate sender and routing identity
- non-deceptive subject
- clear commercial disclosure
- configured valid physical postal address
- plain-language opt-out instructions
- signed one-click unsubscribe mechanism

Missing sender identity, postal address, or unsubscribe configuration blocks sending.

Suppression is global and durable. It is checked before enrollment, scheduling, approval, and send. Only minimal compliance data is retained when full contact deletion is required.

Before outreach, the operator must verify SPF, DKIM, DMARC, TLS, and domain alignment. The system does not implement fake warming, tracking pixels, or artificial reputation manipulation.

Default deliverability pauses:

- any direct complaint or provider reputation warning
- three hard bounces in one business day
- hard-bounce rate of at least 2 percent over 100 sends
- Postmaster spam rate above 0.1 percent requires review
- Postmaster spam rate at or above 0.3 percent is a hard stop
- unhealthy Gmail synchronization is a hard stop

## 8. Security

- Secrets exist only in environment variables or an approved secret manager.
- `.env`, OAuth token files, raw logs, reports, and downloaded provider data are ignored by Git.
- OAuth tokens are encrypted at rest in deployed environments.
- Logs redact credentials, authorization headers, email bodies, and unnecessary personal data.
- Website fetches are isolated from internal networks and cloud metadata.
- Fetched pages are untrusted input, never instructions.
- Administrative changes to outreach enablement, caps, suppression exceptions, and policy versions are audited.
- Unsuppression is not available in the MVP.

## 9. Testing Strategy

Sending-critical behavior uses strict red-green-refactor TDD.

Required deterministic tests include:

- duplicate company prevention
- duplicate contact and duplicate email prevention
- absolute suppression enforcement across every send path
- unsubscribe and negative-response detection
- kill switch and emergency stop
- new and total daily limits
- qualification threshold and hard exclusions
- low-confidence research blocking
- invalid, unknown, and accept-all verification blocking
- campaign state and active-company exclusivity
- follow-up business-day scheduling and four-message maximum
- any reply stopping the sequence
- bounce and ambiguous provider outcome handling
- monotonic CRM transitions
- experiment immutability and safety separation
- API budget preauthorization
- Gmail OAuth scope and secret-safety checks
- first-10 review checkpoint
- 100-qualified-company cohort ceiling

Database integration tests cover locks, counter reservations, duplicate races, job leasing, and provider-event replay.

Provider contract tests use recorded sanitized fixtures and test 401, 403, 404 history cursor, 429, 5xx, malformed payload, timeout, and ambiguous submission behavior.

LLM evaluations separately measure evidence grounding, fabrication rate, personalization support, reply-classification safety, and schema validity. Deterministic checks run before model judgments.

End-to-end tests use fake providers and prove that REVIEW mode cannot send without explicit approval.

## 10. MVP Phases

1. Project instructions, configuration, database foundation, and safety policy
2. Company discovery, evidence research, deterministic qualification, and cohort limits
3. Contact discovery, verification, personalization, and operator review packets
4. Gmail submission, reconciliation, sequences, reply handling, suppression, and deliverability controls
5. Minimal CRM/control APIs, funnel metrics, experiment and cost reporting
6. Full verification, adversarial review, and credential-readiness handoff

The first real-world checkpoint is not a send. It is an exported or displayed review packet containing the first 10 qualified companies, evidence, scores, contact provenance, verification status, and proposed emails.

## 11. Explicitly Deferred

- CONTROLLED_AUTO
- FULL_AUTO
- multiple mailboxes or tenants
- external CRM synchronization
- rich dashboard and visualization work
- autonomous deal negotiation
- automatic response sending beyond unsubscribe processing
- deep booking-platform integration
- tracking pixels and open tracking
- LinkedIn scraping or prohibited directory extraction
- workflow-engine or microservice decomposition

## 12. Required Operator Inputs Before Real Outreach

Implementation and automated tests do not require real credentials. Real outreach remains blocked until the operator provides or configures:

- Google Places API credentials
- one Google Workspace mailbox and OAuth client
- sending domain or subdomain decision
- verified SPF, DKIM, DMARC, and TLS posture
- valid physical postal address
- approved sender identity and signature
- approved booking link
- approved product-claims registry
- explicit `OUTREACH_ENABLED=true`

No credentials should be pasted into chat.
