# Epic: KYC Gate Integration — Provisioning Trigger Relocation, Fan-Out Ownership, and Resumable Polling

> **Product epic** — covers the backend refactor to ensure that partner provisioning only starts after KYC approval, that the onboarding flow is insulated from changes in partner-provisioning logic, and that provisioning polling does not block the user's onboarding transaction.
> **Audience:** Engineers, QA.
> **Non-goal:** This spec contains no technical implementation decisions — no module names, no service boundaries, no port/adapter definitions, no function signatures, no API contracts, no scheduling infrastructure. It describes **what** behavioral invariants change, not **how** code is reorganised.
> **Referenced by:** `kb/specs/onboarding-epic.md` (STRIV-301), `kb/docs/architecture/onboarding/`.
> **Status:** Published as Jira epic **STRIV-446**.

---

## Proposal

The current onboarding implementation has three behavioural problems that cause brittleness and user-facing delays:

1. **Provisioning can start before KYC is approved.** Partner provisioning (Sponsor Bank, Clearing-Platform, Crypto Custodian, Card Processor) is triggered based on profile attachment rather than KYC approval. As a result, a user whose profile is attached but whose KYC has not yet passed can enter a partial provisioning state — even though KYC may later be denied, leaving orphan partner accounts.

2. **Changes to partner provisioning force changes to the onboarding flow.** The onboarding component currently embeds knowledge of how each partner is provisioned. When a partner API contract changes, or a new partner is added, the onboarding flow must be modified — creating coupling that slows down both onboarding and partner-integration work.

3. **Slow partner provisioning blocks the onboarding transaction.** The onboarding flow waits synchronously for each partner to confirm provisioning before it can complete. If a partner is slow or unreachable, the onboarding transaction hangs, database connections stay open, and the user sees no feedback.

This epic refactors the system to:

1. **Gate provisioning on KYC approval** — partner provisioning starts only after KYC has been approved. A user whose KYC is pending or denied is never partially provisioned.
2. **Insulate onboarding from partner-provisioning logic** — changes to how partners are provisioned (API contracts, retry policies, error handling) do not require changes to the onboarding flow.
3. **Make provisioning polling non-blocking** — the onboarding transaction completes without waiting for partner provisioning to finish. Polling is resumed asynchronously from a stored reference.

**Non-goals (out of scope):**

- The onboarding user journey and UI (owned by STRIV-301)
- KYC provider integration or identity verification logic (owned by STRIV-301)
- Partner provisioning business rules (owned by individual integration epics)
- Any change to the KYC approval logic itself

---

## Design

*(No diagrams for this epic — the behaviour is described textually in the rule groups below.)*

---

### Rule Group GR1 — Provisioning Trigger Gated on KYC Approval

**Business rule.** Partner provisioning shall start only after the user's KYC has been approved. A user whose KYC is pending, denied, or under review shall never have partner provisioning initiated. This invariant holds regardless of what other onboarding milestones (profile attachment, data collection, terms acceptance) have been reached.

**Scenario GR1.1 — Provisioning does not start before KYC approval.**

- **Given** a user whose profile has been attached and intake data collected, but KYC is still pending
- **When** the onboarding flow evaluates the next step
- **Then** no partner provisioning is initiated
- **And** the user remains in a pre-provisioning state until KYC resolves

**Scenario GR1.2 — Provisioning starts when KYC is approved.**

- **Given** a user whose KYC has been approved
- **When** the onboarding flow reaches the provisioning step
- **Then** partner provisioning is initiated for all four partners

**Scenario GR1.3 — Provisioning does not start when KYC is denied.**

- **Given** a user whose KYC has been denied
- **When** the onboarding flow evaluates the next step
- **Then** no partner provisioning is initiated
- **And** the user is placed in the KYC-denied state with no orphan partner accounts

### Rule Group GR2 — Onboarding Insulated from Partner-Provisioning Logic

**Business rule.** The onboarding component shall not contain partner-specific provisioning logic (API contracts, retry policies, error handling, timeout handling). A change to how any partner is provisioned, or the addition of a new partner, shall not require a change to the onboarding component.

**Scenario GR2.1 — Onboarding delegates provisioning without partner details.**

- **Given** KYC approval has been received for a user
- **When** the onboarding component triggers partner provisioning
- **Then** it does so without embedding any partner-specific API contract, retry policy, or error-handling logic
- **And** the onboarding result does not depend on how each partner is individually provisioned

**Scenario GR2.2 — A partner API contract changes without affecting onboarding.**

- **Given** an existing partner changes its provisioning API contract (e.g., new required field, different endpoint)
- **When** the change is implemented
- **Then** no change is required to the onboarding component
- **And** the updated partner-provisioning logic is handled entirely outside the onboarding flow

**Scenario GR2.3 — A new partner is added without affecting onboarding.**

- **Given** a fifth partner is introduced
- **When** provisioning logic for the new partner is added
- **Then** no change is required to the onboarding component
- **And** the onboarding flow automatically provisions the new partner alongside the existing four

### Rule Group GR3 — Non-Blocking Provisioning Polling

**Business rule.** The onboarding transaction shall complete without waiting for partner provisioning to finish. Provisioning status shall be tracked asynchronously via a stored reference that a separate polling engine picks up and processes. No blocking wait or sleep shall occur inside the onboarding transaction.

**Scenario GR3.1 — Onboarding transaction completes before provisioning finishes.**

- **Given** a provisioning request is submitted to a partner
- **When** the partner acknowledges the request (but has not yet completed provisioning)
- **Then** the onboarding transaction completes and returns control immediately
- **And** the provisioning request is tracked via a stored reference for later polling
- **And** the user sees a provisioning-in-progress status, not a hang or timeout

**Scenario GR3.2 — Polling resumes provisioning from a stored reference.**

- **Given** a stored polling reference exists for a partner provisioning request
- **When** the polling engine processes the reference
- **Then** it queries the partner provisioning status using the stored reference
- **And** if provisioning is complete, the user's provisioning status is updated accordingly
- **And** if provisioning is still in progress, the reference is re-stored for the next polling cycle

**Scenario GR3.3 — Provisioning failure is handled without blocking onboarding.**

- **Given** a partner provisioning request fails (after retries are exhausted)
- **When** the polling engine detects the failure
- **Then** the user's provisioning status transitions to PARTIAL
- **And** an escalation is triggered for ops investigation
- **And** the onboarding transaction is unaffected (it completed before the failure was known)

---

## Edge Cases

| ID | Scenario | Expected Behavior |
|---|---|---|
| EC1 | Partner provisioning completes before the first polling cycle runs | The first polling cycle finds provisioning complete; the user transitions to ACTIVE without delay |
| EC2 | User's KYC is re-submitted while in-flight provisioning is still being polled | In-flight provisioning completes against the original KYC result; new provisioning is triggered only after the re-submitted KYC is approved |
| EC3 | Polling reference is lost (data corruption, restart) | The provisioning is flagged as orphaned; ops escalates; the user transitions to PARTIAL for manual resolution |
| EC4 | All partners provision synchronously faster than the polling interval | First polling cycle finds all complete; no artificial delay introduced |

---

## Tasks

### T1 — Gate provisioning trigger on KYC approval
**Done when:** Provisioning is not initiated before KYC approval per GR1.1; provisioning starts when KYC is approved per GR1.2; provisioning is not initiated when KYC is denied per GR1.3.

### T2 — Insulate onboarding from partner-provisioning logic
**Done when:** Onboarding delegates provisioning without partner-specific details per GR2.1; a partner API contract change does not require onboarding changes per GR2.2; adding a new partner does not require onboarding changes per GR2.3.

### T3 — Make provisioning polling non-blocking
**Done when:** Onboarding transaction completes before provisioning finishes per GR3.1; polling resumes from stored reference per GR3.2; provisioning failure does not block onboarding per GR3.3; completed-before-polling and lost-reference edge cases are handled per EC1/EC3.