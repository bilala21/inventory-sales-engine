# Operator Runbook

## Purpose

Operate the Inventory Sales Engine toward qualified conversations, demos, paid pilots, and customers. Never treat message volume as the success metric.

## Mandatory Pre-Send Gates

Every item must be complete before `OUTREACH_ENABLED` can be changed locally:

1. Select a provider whose written terms explicitly permit the intended compliant B2B outreach. Gmail API may be used only for recipients who consented unless Google confirms otherwise in writing.
2. Use a dedicated mailbox on a domain you control.
3. Verify SPF, DKIM, DMARC, TLS, and From-domain alignment.
4. Configure accurate sender name, sender email, and a valid physical postal address.
5. Configure a working HTTPS unsubscribe endpoint that handles one-click POST and reply-based opt-outs.
6. Complete the selected provider authorization with the minimum required permissions.
7. Configure and validate an email-verification provider; only current `VALID` results may send.
8. Approve the product-claim registry against functionality that exists today.
9. Review the first 10 qualified companies, their evidence, contacts, and exact email drafts.
10. Approve the exact first-10 packet hash and each exact draft hash.
11. Run the full safety suite with no failures.
12. Keep REVIEW mode, then deliberately set `EMERGENCY_STOP=false` and `OUTREACH_ENABLED=true` locally.

Do not put credentials in chat, source control, logs, screenshots, or review packets.

## First Cohort

- Niche: small packaging distributors
- Geography: Chicago and Illinois
- Country: United States only
- Maximum qualified companies: 100
- Exclude consumers, hobby shops, companies without meaningful physical inventory, huge enterprises, and companies with sophisticated inventory systems unless a supported gap exists.

Discovery stops when the qualified cohort reaches 100. If roughly 100 genuinely qualified prospects produce no meaningful conversation, keep outreach paused and diagnose ICP, offer, evidence quality, contact quality, message, and deliverability. Do not expand volume by default.

## Review Procedure

For each candidate, verify:

- the company is a packaging distributor or closely matching small manufacturer
- every company fact links to a public first-party evidence snapshot
- fit score and confidence meet the configured threshold
- the pain point is phrased as a hypothesis or question, not a claimed fact
- the contact role and business email have source provenance
- verification is current and `VALID`
- the draft uses only approved product claims and evidence IDs
- subject, sender identity, commercial disclosure, postal address, and opt-out are accurate

Editing a draft invalidates its approval. Regenerate the packet and review the new hash.

## Daily Operation

1. Confirm `/health` and `/safety/status` are healthy and expected.
2. Review discovery costs before approving new provider calls.
3. Review queued companies and drafts.
4. Confirm Gmail inbound synchronization is healthy before any send.
5. Approve exact drafts only after checking evidence and claims.
6. Monitor replies, bounces, opt-outs, and provider warnings before reviewing more sends.
7. Notify interested leads immediately; questions receive suggestions only, not automatic replies.
8. Record demos, pilots, and paid customers in the CRM timeline.

Any human inbound message pauses the sequence before classification. Any unsubscribe is suppressed immediately and permanently. Any ambiguous Gmail result, bounce-like event, sync gap, complaint indicator, or provider warning pauses affected outreach for review.

## Emergency Stop

Set these locally:

```text
OUTREACH_ENABLED=false
EMERGENCY_STOP=true
```

Restart workers and confirm `/safety/status`. Do not resume until the cause is understood and the safety suite passes.

## Commercial Checkpoints

- 15–20 delivered accounts with no qualified replies: early message/contact/ICP review
- Approximately five completed demos with no pilot: pause and review offer and pilot design
- 100 qualified companies with zero meaningful conversations: stop cohort expansion and produce a diagnostic

Software completion is not business validation. Report qualified companies, delivery evidence, meaningful conversations, demos, pilots, and paying customers separately.
