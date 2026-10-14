# Epic: Client Onboarding — New User Journey

> **Product epic** — covers the complete client-facing onboarding journey of the Strive platform: how a prospective client goes from signup to an active, fully provisioned account. Defines the user-facing flow, KYC orchestration, partner provisioning, resumability, and error handling.
> **Audience:** Product managers, engineers, QA, compliance.
> **Non-goal:** This spec contains no technical implementation decisions — no state-machine design, no service boundaries, no ports/adapters, no API contracts.
> **Referenced by:** `kb/docs/architecture/onboarding/onboarding.md`, `kb/docs/design-docs/business-rules/product-vision.md` (section 4.2).
> **Status:** Published as Jira epic **STRIV-301**.

---

## Proposal

Strive needs a single, product-grade onboarding flow that takes a prospective client from signup to an active, fully provisioned account. Currently there is no unified onboarding journey — responsibilities are fragmented, and the user experience for resuming a paused signup or retrying after a KYC denial is undefined.

This epic covers the complete client-facing onboarding journey across five stages:

1. **Signup** — The user creates their identity with email and password, with duplicate detection and outage handling.
2. **Intake form** — The user supplies personal, financial, and regulatory information through a structured multi-page form (6 pages: personal-info, address, employment-income, source-of-funds, tax-id, marketing-consent), with per-page validation and cross-page consistency rules.
3. **KYC verification** — Identity verification via a third-party provider with three outcomes: approved, denied, or manual-review. KYC re-attempt allowed after a configurable cool-down (default 24h).
4. **Terms & consent** — Account agreements, privacy policy, e-sign consent, and W-9 tax certification with acceptance record.
5. **Partner provisioning** — Sub-accounts at all 4 partners (Sponsor Bank, Clearing-Platform, Card Processor, Crypto Custodian). If KYC passes but some partners fail, user enters a partial state requiring ops support.

**Non-goals (out of scope):**

- The KYC gate integration itself (owned by STRIV-446 — provisioning trigger, fan-out ownership, polling)
- Partner-specific provisioning logic (owned by partners module and individual integration epics)
- Post-onboarding features (dashboard, deposits, card, vaults — each owned by its own epic)
- Any technical decision on how the onboarding state machine is implemented

---

## Design

### Rule Group GR1 — Signup

**Business rule.** A new user creates their identity with email and password. The system detects duplicate registrations and handles third-party identity provider outages gracefully.

**Scenario GR1.1 — User signs up with valid credentials.**

- **Given** a prospective user with a valid email and password
- **When** they submit the signup form
- **Then** their identity is created
- **And** they are directed to the intake form

**Scenario GR1.2 — Duplicate signup is detected.**

- **Given** a prospective user whose email is already registered
- **When** they attempt to sign up
- **Then** they are notified that an account already exists
- **And** they are directed to the login flow

**Scenario GR1.3 — Third-party identity provider is unavailable.**

- **Given** the identity provider is experiencing an outage
- **When** a prospective user attempts to sign up
- **Then** they are shown a friendly error message indicating the service is temporarily unavailable
- **And** they are prompted to try again later
- **And** the outage is logged for ops investigation

### Rule Group GR2 — Intake Form

**Business rule.** The intake form spans 6 pages (personal-info, address, employment-income, source-of-funds, tax-id, marketing-consent) with forward/back navigation, per-field validation, and cross-page consistency rules.

**Scenario GR2.1 — User completes intake form in sequence.**

- **Given** a user on the intake form
- **When** they complete each page with valid data and tap "Next"
- **Then** they advance to the next page
- **And** after the 6th page, they are directed to terms & consent

**Scenario GR2.2 — Invalid field blocks advancement.**

- **Given** a user on any intake page
- **When** they enter invalid data (e.g., invalid SSN format)
- **Then** the field shows a validation error
- **And** the "Next" button is disabled until corrected

**Scenario GR2.3 — User returns to a previous page.**

- **Given** a user on page 4 of the intake form
- **When** they tap "Back"
- **Then** they return to page 3
- **And** previously entered data on pages 1–3 is retained

**Scenario GR2.4 — Network failure during form submission.**

- **Given** a user on any intake page submits valid data
- **When** a network failure prevents the data from being saved
- **Then** the user is shown an error message with a retry option
- **And** the entered data is not lost (cached locally until successfully submitted)

### Rule Group GR3 — KYC Verification

**Business rule.** Identity verification is performed via a third-party provider with three outcomes: approved, denied, or manual-review. After denial, the user can re-submit after a configurable cool-down (default 24h). Manual-review outcomes are surfaced to the user as "under review" with expected resolution time.

**Scenario GR3.1 — KYC is approved.**

- **Given** a user who has submitted their intake data
- **When** the KYC provider returns "approved"
- **Then** the user moves to partner provisioning

**Scenario GR3.2 — KYC is denied with re-attempt.**

- **Given** a user whose KYC was denied
- **When** the cool-down period (default 24h) has elapsed
- **Then** the user can re-submit their KYC data
- **And** a new KYC verification is initiated

**Scenario GR3.3 — KYC is denied within cool-down.**

- **Given** a user whose KYC was denied less than 24h ago
- **When** they attempt to re-submit
- **Then** they are notified to wait until the cool-down expires

**Scenario GR3.4 — KYC requires manual review.**

- **Given** a user whose KYC was submitted
- **When** the KYC provider returns "manual-review"
- **Then** the user is shown a status message indicating their application is under manual review
- **And** an expected resolution time is displayed (e.g., "typically 1–2 business days")
- **And** the user is notified that they will receive an update when the review is complete

**Scenario GR3.5 — KYC provider is unavailable.**

- **Given** the KYC provider is unavailable during verification
- **When** the KYC verification attempt times out
- **Then** the user is shown an error message
- **And** they are prompted to retry
- **And** the outage is logged for ops investigation

### Rule Group GR4 — Terms & Consent

**Business rule.** The user must accept account agreements, privacy policy, e-sign consent, and W-9 tax certification before provisioning begins. All opt-ins are unchecked by default.

**Scenario GR4.1 — User accepts all terms.**

- **Given** a user on the terms & consent screen
- **When** they check all required consent boxes and tap "Accept"
- **Then** an acceptance record is created
- **And** the user moves to partner provisioning

**Scenario GR4.2 — User does not accept required terms.**

- **Given** a user on the terms & consent screen
- **When** they attempt to proceed without accepting all required terms
- **Then** the "Accept" button is disabled
- **And** the user is prompted to accept the required terms

### Rule Group GR5 — Partner Provisioning

**Business rule.** Sub-accounts are provisioned at all 4 partners in parallel. If all succeed, the user enters ACTIVE state. If any fail, the user enters a PARTIAL state requiring ops support. Partner timeouts are treated as failures for the initial provisioning attempt.

**Scenario GR5.1 — All partners provision successfully.**

- **Given** KYC has been approved and terms accepted
- **When** all 4 partners provision successfully
- **Then** the user status transitions to ACTIVE
- **And** the user can access all platform features

**Scenario GR5.2 — Some partners fail to provision.**

- **Given** KYC has been approved and terms accepted
- **When** some partners provision successfully but others fail
- **Then** the user status transitions to PARTIAL
- **And** an ops support ticket is created for the failed partners
- **And** the user is notified that setup is incomplete

**Scenario GR5.3 — Partner times out during provisioning.**

- **Given** KYC has been approved and terms accepted
- **When** a partner does not respond within the timeout period
- **Then** the timed-out partner is treated as a failure
- **And** the user status transitions to PARTIAL
- **And** an ops ticket is created for the timed-out partner

### Rule Group GR6 — Session Resumability

**Business rule.** A user who leaves mid-flow can return where they stopped within a 24-hour session window. After expiry, the session is reset.

**Scenario GR6.1 — User resumes within the session window.**

- **Given** a user who completed 3 of 6 intake pages and then left
- **When** they return within 24 hours and log in
- **Then** they resume on page 4
- **And** previously entered data on pages 1–3 is retained

**Scenario GR6.2 — Session expires.**

- **Given** a user who started the intake form more than 24 hours ago
- **When** they return and log in
- **Then** their session has expired
- **And** they are prompted to restart the intake form

---

## Edge Cases

| ID | Scenario | Expected Behavior |
|---|---|---|
| EC1 | User abandons signup mid-flow (closes browser) | Partial data discarded on session expiry (24h); no orphan records created |
| EC2 | KYC provider returns "review" and takes >5 business days | Ops escalates; user notified of delay; manual intervention triggered |
| EC3 | All 4 partners fail to provision | User enters PARTIAL state; urgent ops ticket created; user notified that setup encountered an error and will be contacted |
| EC4 | User enters an invalid email format during signup | Field shows validation error; "Create Account" disabled until email format is valid |
| EC5 | User provides SSN that fails format validation | Field shows error with format guidance; "Next" disabled |
| EC6 | Intake form detects inconsistent data across pages (e.g., age in personal-info conflicts with employment history) | Cross-page validation flags the inconsistency on the final page; user must correct before proceeding |

---

## Compliance Items (To Investigate)

The following compliance items are flagged for investigation before production release:

- BSA/AML threshold reporting (CTR/SAR)
- Reg E disclosure timing for electronic fund transfers
- State-level money transmitter licensing requirements
- FinCEN BOI reporting obligations
- SSN/ITIN validation requirements
- CIP minimum requirements under USA PATRIOT Act
- ESIGN Act record-keeping for electronic signatures
- Partner-specific KYC/KYB requirements
- OFAC screening timing during onboarding
- Data privacy and retention policy compliance

---

## Tasks

### T1 — Signup with duplicate detection and outage handling
**Done when:** Valid signup creates identity per GR1.1; duplicate email detected per GR1.2; third-party outage handled gracefully per GR1.3.

### T2 — Multi-page intake form with validation
**Done when:** 6-page form with forward/back navigation per GR2.1; per-field validation blocks advancement on invalid data per GR2.2; back navigation retains data per GR2.3; network failure preserves data per GR2.4; cross-page consistency validation per EC6.

### T3 — KYC orchestration with approved/denied/review outcomes
**Done when:** Approved moves to provisioning per GR3.1; denied re-attempt after cool-down per GR3.2; cool-down enforced per GR3.3; manual-review status surfaced per GR3.4; provider outage handled per GR3.5; delayed review escalation per EC2.

### T4 — Terms, consent, and tax certification
**Done when:** Acceptance recorded per GR4.1; required terms enforced per GR4.2.

### T5 — Four-partner provisioning with ACTIVE and PARTIAL states
**Done when:** All partners succeed → ACTIVE per GR5.1; partial failure → PARTIAL with ops ticket per GR5.2; partner timeout → PARTIAL per GR5.3; all fail → urgent ops ticket per EC3.

### T6 — Session persistence (24h window) and graceful expiry
**Done when:** Resume within window retains progress per GR6.1; expired session resets per GR6.2; mid-flow abandonment handled per EC1.

### T7 — Compliance investigation
**Done when:** All 10 compliance items are investigated; findings documented; regulatory risks assessed.