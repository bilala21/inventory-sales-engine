# API and Provider Setup

Do not paste credentials into chat. Create `.env` from `.env.example` and enter values locally.

## Google Places API

Enable Places API (New) in a restricted Google Cloud project. Restrict the API key by API and deployment source. Use Text Search (New) with `X-Goog-FieldMask`; wildcard field masks are prohibited.

The MVP mask requests Place ID, display name, formatted address, website, national phone, and primary type. Current Google documentation places website and phone in the Text Search Enterprise SKU. As checked on 2026-08-18, the global list shows a 1,000-event free usage cap and then $35 per 1,000 events in the first paid tier. Pricing and free caps can change; verify before enabling discovery.

- [Text Search (New)](https://developers.google.com/maps/documentation/places/web-service/text-search)
- [Google Maps Platform pricing](https://developers.google.com/maps/billing-and-pricing/pricing)

For this 100-company cohort, expected Places cost is approximately $0 if total monthly Enterprise Text Search events remain inside the current free cap. This is an estimate, not a guarantee. The cost ledger preauthorizes every provider call and pauses before the configured monthly budget is exceeded.

## Gmail API

**Cold-outreach blocker:** Google’s current Workspace API user-data policy prohibits Gmail-scope applications from distributing unsolicited commercial mail. It gives consented CRM mail as the permitted example. Do not use the Gmail adapter for this project’s cold cohort unless Google gives written confirmation for the exact use case. The adapter remains useful for consented conversations or a consent-first workflow.

Create an OAuth desktop or web client for the single operator mailbox. Request only:

```text
https://www.googleapis.com/auth/gmail.send
https://www.googleapis.com/auth/gmail.readonly
```

The API has no separate per-message charge, but Google Workspace subscription costs and account limits still apply. Internal limits remain 20 new and 40 total messages per business day, regardless of higher provider limits.

Google recommends renewing Gmail `watch` daily and requires renewal at least every seven days. Keep periodic `history.list` reconciliation and all-mail safety sweeps because push notifications can be delayed or missed.

- [Gmail API scopes](https://developers.google.com/workspace/gmail/api/auth/scopes)
- [Google Workspace user data and developer policy](https://developers.google.com/workspace/workspace-api-user-data-developer-policy)
- [Gmail push notifications](https://developers.google.com/workspace/gmail/api/guides/push)
- [Gmail sender guidelines](https://support.google.com/mail/answer/81126)

## Email Verification

The provider is configurable and optional until contact verification begins. It must return `VALID`, `INVALID`, `ACCEPT_ALL`, or `UNKNOWN`, plus provider reference and expiry.

Typical low-volume verification pricing is an estimate of roughly $0.005–$0.02 per address, or approximately $0.50–$2.00 for 100 addresses. Confirm the selected provider's current price, data-processing terms, and retention policy before purchase.

## LLM Provider

No LLM provider is required for deterministic qualification, safety, CRM, or message rendering. If configured for research extraction or reply suggestions, it must return structured output with evidence IDs and must not control hard exclusions, thresholds, suppression, send eligibility, or autonomous deal negotiation.

At 100 companies, a small-model workflow is expected to cost approximately $1–$15 depending on page size, retries, prompts, and provider pricing. This is an estimate. Cache content hashes and research results, and preauthorize every call.

## PostgreSQL and Hosting

Local PostgreSQL has no service fee. A small managed PostgreSQL deployment commonly starts around $10–$30 monthly, but vendor, backup, network, and retention choices vary. Hosted deployment must encrypt OAuth tokens, restrict database access, enable backups, and complete any Gmail restricted-scope requirements.

## Booking

A public Calendly or equivalent booking link is sufficient for the MVP. A booking API is optional; the system can track demo status manually until real conversations justify automation.
