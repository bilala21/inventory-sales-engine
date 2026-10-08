# Inventory Sales Engine Instructions

## Business Objective

- Optimize for qualified conversations, demos, paid pilots, and customers, not email volume.
- Keep the first validation cohort capped at 100 genuinely qualified companies.
- Require operator review of the first 10 qualified companies and proposed emails before any real outreach.
- Treat the validation targets as targets, never guarantees.

## Truthfulness

- Never fabricate company research, pain points, product claims, results, savings, ROI, testimonials, integrations, or urgency.
- Every company fact and personalization claim must retain source provenance.
- Missing, stale, ambiguous, conflicting, or unverifiable evidence must block sending.

## Outreach Safety

- `OUTREACH_ENABLED=false` is the default.
- REVIEW is the only executable mode.
- Do not add CONTROLLED_AUTO or FULL_AUTO without a separate architecture and safety review.
- Suppression is absolute and permanent for outreach purposes.
- Opt-outs, negative replies, and human replies stop sequences immediately.
- No automatic massive sending, fake warming, deceptive marketing, fake urgency, or fake testimonials.
- No sending-critical change without tests first and independent review.

## Security and Compliance

- Protect OAuth and provider credentials; never commit or log them.
- Use public business information only and preserve source lineage.
- Do not bypass authentication, CAPTCHAs, robots restrictions, or anti-bot protections.
- U.S.-only outreach in the MVP.
- A valid postal address and unsubscribe mechanism are mandatory before sending.

