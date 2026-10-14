# Epic: Reconciliation — Keep Strive's Ledger Consistent with Partners

> **Product epic** — covers reconciliation of the Local Ledger against Strive's four money-handling partners: Clearing-Platform (SatC), Sponsor Bank (Cash), Crypto Custodian (Bitcoin), and Card Processor (debit card activity). Reconciliation compares the Local Ledger against each Partner Ledger, detects when they diverge, and locates where. It is a detection and escalation process only — it never silently corrects a balance toward either side.
> **Audience:** Product managers, engineers, compliance, QA.
> **Non-goal:** This spec contains no technical implementation decisions — no reconciliation engine architecture, no scheduling infrastructure, no data pipelines, no API contracts.
> **Referenced by:** `kb/specs/local-ledger-epic.md` (STRIV-377), `kb/docs/design-docs/business-rules/product-vision.md` (section 6).
> **Depends on:** STRIV-377 (Local Ledger — the ledger must exist before it can be reconciled).
> **Open decisions resolved:** OD-1 (Static $50 materiality threshold), OD-2 (Grace window: 30-day flag for dangling authorizations; partner evaluation still needed), OD-3 (Yes — fixed price simplifies SatC reconciliation to pure quantity checking).
> **Status:** Published as Jira epic **STRIV-422**.

---

## Proposal

Strive's customers hold balances across four external partners: SatC at Clearing-Platform, Cash at the Sponsor Bank, Bitcoin at the Crypto Custodian, and debit card activity at the Card Processor. The Local Ledger (STRIV-377) records what the platform believes each user's balance to be, but the settlement truth lives at each partner. Over time, differences may arise due to timing, fees, rounding, failed orders, or system errors.

Reconciliation detects these differences systematically. It never auto-corrects — because either the local ledger or the partner ledger could be the erroneous one. Instead, it classifies differences by materiality, escalates discrepancies through tiered internal channels, and produces a daily audit trail.

This epic covers:

1. **Partner scope & reconciliation units** — Balance-bearing partners compared at balance level first, then transaction level. Card Processor at transaction level only.
2. **No-blind-authority policy** — Neither ledger is authoritative over the other. No auto-correction in V1.
3. **Materiality threshold & escalation** — Static $50 threshold. Differences at or below $50 are tolerated. Above $50 escalates tiered by severity.
4. **Daily cadence** — Scheduled daily batch, as-of end-of-market-day close, producing a formal daily report.
5. **Per-Vault sub-ledger reconciliation** — Clearing-Platform reconciled at main SatC level, then per-Vault to locate phantom Vaults.
6. **Bitcoin as separate flow** — BTC reconciled against Crypto Custodian with own $50 materiality threshold.
7. **In-Flight classification** — Items accepted by a partner but not yet settled excluded from balance comparison. Items stale after 30 days are flagged.
8. **Suspense/clearing book** — Unattributable partner activity booked to an internal ops-visible book so the ledger total still reconciles to custodied assets.

**Non-goals (out of scope):**

- The Local Ledger itself (STRIV-377 owns ledger structure, posting rules, balance computation)
- Auto-correction or self-healing of discrepancies (V1 — all manually investigated)
- Customer-facing dispute resolution workflows
- Any technical decision on reconciliation engine architecture or scheduling

---

## Design

### Rule Group GR1 — Partner Scope & Reconciliation Units

**Business rule.** Balance-bearing partners (Clearing-Platform, Sponsor Bank, Crypto Custodian) are compared at the balance level first, then at the transaction level to locate discrepancies. The Card Processor holds no stored balance — its reconciliation is inherently transaction-level (authorization vs clearing completeness).

**Scenario GR1.1 — Balance-bearing partner reconciled at balance level.**

- **Given** a user with a SatC balance recorded in the Local Ledger
- **When** the daily reconciliation batch runs
- **Then** the Local Ledger SatC balance is compared against the Clearing-Platform balance
- **And** if the balances match within the $50 materiality threshold, no further action is taken

**Scenario GR1.2 — Balance discrepancy descends to transaction level.**

- **Given** a balance discrepancy between the Local Ledger and Clearing-Platform that exceeds the $50 materiality threshold
- **When** the reconciliation batch descends to transaction level
- **Then** individual transactions are compared to locate the specific entries causing the discrepancy

**Scenario GR1.3 — Card Processor is reconciled at transaction level only.**

- **Given** a user with card transaction history
- **When** the daily reconciliation batch runs for the Card Processor
- **Then** authorizations are compared against clearing completions
- **And** no balance-level comparison is performed

### Rule Group GR2 — Materiality Threshold & Escalation

**Business rule.** A static $50 materiality threshold separates normal rounding/fee noise from a Discrepancy. Discrepancies are escalated tiered by severity/materiality. No automatic customer-facing action.

**Scenario GR2.1 — Difference within threshold is tolerated.**

- **Given** a difference of $2 between the Local Ledger and a partner balance
- **When** the materiality threshold is $50
- **Then** the difference is classified as within tolerance
- **And** it is logged but does not trigger escalation

**Scenario GR2.2 — Difference exceeding threshold is escalated.**

- **Given** a difference of $150 between the Local Ledger and a partner balance
- **When** the materiality threshold is $50
- **Then** the difference is classified as a Discrepancy
- **And** an escalation is triggered to internal operations

### Rule Group GR3 — Daily Cadence & Reporting

**Business rule.** Reconciliation runs as a scheduled daily batch, as-of end-of-market-day close, producing a formal daily report (all-clear or discrepancy list) for an audit trail.

**Scenario GR3.1 — Daily reconciliation produces an all-clear report.**

- **Given** no discrepancies are found across any partner
- **When** the daily reconciliation batch completes
- **Then** a formal daily report is produced with status "All Clear"
- **And** the report is archived for audit trail

**Scenario GR3.2 — Daily reconciliation produces a discrepancy report.**

- **Given** one or more discrepancies are found
- **When** the daily reconciliation batch completes
- **Then** a formal daily report is produced listing each discrepancy with partner, amount, and materiality
- **And** the report is archived for audit trail

### Rule Group GR4 — In-Flight Classification

**Business rule.** Items accepted by a partner but not yet settled (ACH float, pending SatC orders, pending BTC transfers) are classified as In-Flight and excluded from the balance comparison. Items stale after 30 days are flagged.

**Scenario GR4.1 — In-Flight item excluded from comparison.**

- **Given** a SatC order is in PendingSubmit status (submitted to Clearing-Platform, not yet executed)
- **When** the daily reconciliation batch runs
- **Then** the pending order amount is classified as In-Flight
- **And** it is excluded from the balance comparison

**Scenario GR4.2 — Stale In-Flight item triggers investigation.**

- **Given** a SatC order has been In-Flight for longer than 30 days
- **When** the daily reconciliation batch runs
- **Then** the order is flagged as stale
- **And** it is included in the discrepancy report for investigation

### Rule Group GR5 — Bitcoin Reconciliation

**Business rule.** Bitcoin is reconciled against the Crypto Custodian as a separate flow with its own resource (sub-ledger, cadence, and $50 threshold). Straight segregation means BTC is never compared against Cash or SatC balances.

**Scenario GR5.1 — Bitcoin balance is compared at BTC quantity level.**

- **Given** a user with a Bitcoin balance in the Local Ledger
- **When** the daily reconciliation batch runs for the Crypto Custodian
- **Then** the Local Ledger BTC quantity is compared against the Crypto Custodian BTC quantity
- **And** if the quantities match within the $50 equivalent threshold, no further action is taken

**Scenario GR5.2 — Bitcoin discrepancy is investigated separately.**

- **Given** a Bitcoin quantity discrepancy that exceeds the $50 equivalent threshold
- **When** the reconciliation batch flags the discrepancy
- **Then** it is recorded in the discrepancy report as a Bitcoin-specific item
- **And** it is investigated separately from Cash and SatC discrepancies

### Rule Group GR6 — Per-Vault Sub-Ledger Reconciliation

**Business rule.** Clearing-Platform is reconciled at the main SatC balance level first, then at the per-Vault sub-ledger level to locate discrepancies such as phantom Vaults or missing allocations.

**Scenario GR6.1 — Main SatC balance matches, then Vaults are checked.**

- **Given** the main SatC balance matches between the Local Ledger and Clearing-Platform
- **When** the reconciliation batch descends to Vault sub-ledgers
- **Then** each Vault's balance is compared against its corresponding sub-ledger in Clearing-Platform
- **And** if a Vault exists in the Local Ledger but not in Clearing-Platform, it is flagged as a "phantom Vault" discrepancy

**Scenario GR6.2 — Phantom Vault is detected.**

- **Given** a Vault exists in the Local Ledger with $2,000 balance
- **When** the per-Vault reconciliation runs against Clearing-Platform
- **Then** if the Vault has no corresponding sub-ledger at Clearing-Platform, it is flagged as a phantom Vault
- **And** the discrepancy is escalated for investigation

### Rule Group GR7 — Suspense/Clearing Book

**Business rule.** Partner-reported activity unattributable to a known user is booked to an internal suspense/clearing book (ops-visible only, not user-visible), so the ledger total still reconciles to custodied assets pending manual resolution.

**Scenario GR7.1 — Unattributable partner activity is booked to suspense.**

- **Given** a partner reports a transaction that cannot be attributed to any known user
- **When** the reconciliation batch processes the unattributable item
- **Then** the amount is posted to the suspense/clearing book (ops-visible only)
- **And** the ledger total continues to reconcile to custodied assets
- **And** a manual resolution ticket is created for ops investigation

---

## Edge Cases

| ID | Scenario | Expected Behavior |
|---|---|---|
| EC1 | Daily batch finds no partners available (all APIs down) | Batch fails with error; retry with backoff; escalate after N retries |
| EC2 | A partner balance exceeds the Local Ledger by $50+ due to a fee the ledger has not recorded | Discrepancy escalated; ops investigates whether to record the fee in the ledger or dispute it with the partner |
| EC3 | User closes account; residual balance remains at a partner | Residual is flagged; ops initiates manual sweep or escheatment process |
| EC4 | SatC quantity is correct but per-Vault breakdown sums differ from Vault total | Discrepancy flagged as sub-ledger arithmetic error; ops investigates which Vault is mis-attributed |
| EC5 | In-Flight item resolves (settles) mid-batch | The batch processes the resolved item as booked; no In-Flight exclusion applied |

---

## Tasks

### T1 — Partner scope & reconciliation units defined
**Done when:** Balance-bearing partners are identified and reconciliation units (balance-level then transaction-level) defined per GR1.1/GR1.2; Card Processor transaction-only per GR1.3.

### T2 — No-blind-authority, investigate-only correction policy
**Done when:** Policy documented and implemented: no auto-correction toward either ledger for V1 per GR2.

### T3 — Detection with $50 materiality threshold and tiered escalation
**Done when:** Differences ≤$50 tolerated per GR2.1; differences >$50 escalate per GR2.2.

### T4 — Daily cadence, end-of-market-day boundary, and formal daily report
**Done when:** Daily batch runs as-of end-of-market-day close per GR3.1; all-clear and discrepancy reports produced per GR3.2.

### T5 — Per-Vault sub-ledger reconciliation
**Done when:** Main SatC balanced checked first per GR6.1; phantom Vaults detected per GR6.2.

### T6 — Bitcoin reconciled as a separate flow
**Done when:** BTC quantity compared against Crypto Custodian per GR5.1; BTC discrepancies tracked separately per GR5.2.

### T7 — In-Flight classification
**Done when:** Pending items excluded from comparison per GR4.1; stale items flagged after 30 days per GR4.2; mid-batch settlement handled per EC5.

### T8 — Suspense/clearing book for unattributable activity
**Done when:** Unattributable partner activity posted to suspense book per GR7.1; ops ticket created; ledger total reconciles.