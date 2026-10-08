# Security and Compliance

This document is an engineering checklist, not legal advice. U.S.-only outreach still requires case-specific legal review when business practices or jurisdictions change.

## CAN-SPAM Controls

The FTC states that CAN-SPAM covers commercial email, including business-to-business email. Each message must use accurate headers and routing, a non-deceptive subject, a clear commercial disclosure, a valid physical postal address, and a clear opt-out method. Opt-outs must remain available for at least 30 days and be honored within 10 business days.

Primary guidance: [FTC CAN-SPAM compliance guide](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business).

The engine applies stricter operational behavior:

- reply-based opt-outs suppress synchronously
- suppression is global across campaigns
- email, domain, and company suppression are checked at enrollment, review, and final send
- no reactivation path exists for permanent unsubscribe entries
- commercial disclosure and postal address are appended by MIME construction
- exact-draft approval prevents post-review content changes

The operator remains responsible for accurate identity, postal address, product claims, and the functioning unsubscribe endpoint.

## OAuth and Secrets

Google’s current Workspace API user-data policy prohibits Gmail-scope applications from distributing unsolicited commercial mail. CRM mail is described as permitted when recipients consent. Therefore the Gmail adapter is not an approved cold-outreach transport for this project without written Google confirmation. CAN-SPAM compliance does not override provider terms.

Official policy: [Google Workspace user data and developer policy](https://developers.google.com/workspace/workspace-api-user-data-developer-policy).

- Keep all credentials only in `.env` or a production secret manager.
- Never commit Gmail client secrets, refresh tokens, Google Places keys, verification keys, or LLM keys.
- OAuth values must be encrypted at rest in hosted deployments and redacted from logs.
- Request only `gmail.send` and `gmail.readonly`.
- Google classifies `gmail.readonly` as a restricted scope. Server-side storage or transmission of restricted-scope data can require OAuth verification and a security assessment. Review this before hosting or adding users.
- One mailbox and one operator do not remove the need for least privilege, access logs, token rotation, and incident response.

Official scope guidance: [Gmail API scopes](https://developers.google.com/workspace/gmail/api/auth/scopes).

## Research Security

Website content is untrusted input. The fetch policy allows only public HTTP/HTTPS targets; blocks credentials, private, loopback, link-local, reserved, and metadata addresses; revalidates redirects; and limits response size, content type, time, and redirect count. It does not bypass authentication, CAPTCHA, robots restrictions, or anti-bot controls.

Google Place responses are transient discovery inputs. Persist Place IDs and query provenance; independently verify durable CRM fields from permitted first-party or licensed sources.

## Deliverability Controls

- Do not use fake warming, tracking pixels, or artificial conversations.
- Start with the approved small cohort and configured limits; do not auto-ramp.
- Verify addresses before send and block INVALID, UNKNOWN, stale, and ACCEPT_ALL by default.
- Pause on complaints, reputation warnings, elevated bounces, history gaps, or ambiguous delivery events.
- Gmail API success means submission accepted, not delivered.
- Keep SPF, DKIM, DMARC, TLS, alignment, and one-click unsubscribe healthy.

Official sender guidance: [Gmail sender guidelines](https://support.google.com/mail/answer/81126).

## Incident Response

1. Set `OUTREACH_ENABLED=false` and `EMERGENCY_STOP=true`.
2. Revoke or rotate affected credentials.
3. Preserve audit events without copying message bodies or tokens into tickets.
4. Reconcile ambiguous Gmail submissions by stable RFC Message-ID; never retry blindly.
5. Apply suppression before any other reply processing.
6. Add a failing regression test before changing sending-critical behavior.
