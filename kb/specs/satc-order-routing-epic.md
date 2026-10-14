# Epic: SatC Order Routing & Lifecycle

> **Product epic** — covers the SatC order routing layer of the Strive platform: the shared lifecycle by which any platform component submits a SatC Buy or Sell order to Clearing-Platform, tracks it through its statuses, handles optional market-hours awareness, and reports the outcome back to the originating trigger.
> **Audience:** Product managers, engineers, QA.
> **Non-goal:** This spec contains no technical implementation decisions — no order types, no ledger schema, no service boundaries, no state-machine design, no ports/adapters, no API contracts.
> **Referenced by:** `kb/docs/design-docs/business-rules/product-vision.md` (sections 4.1, 4.2, 4.4).
> **Triggered by:** Cash In (STRIV-265), Cash Out (STRIV-265), Debit Card (STRIV-360), Dividend Router (STRIV-401).
> **Open decisions resolved:** D1 (Yes — Regular Session gating per CONTEXT.md), D2 (FIFO), D3 (7 days).
> **Status:** Published as Jira epic **STRIV-376**.

---

## Proposal

The Strive platform generates SatC Buy and Sell orders based on automatic actions, not manual user trades. SatC is a direct issuance by Strive through a Broker at a fixed price — there is no market order book, no limit prices, and no trading strategy. The user does not fill any order form — the platform generates and sends orders based on deposit settlement (Cash-in auto-investment), card capture (debit settlement), withdrawal execution (cash-out), and dividend reinvestment.

This epic defines the **order-routing layer itself** — the shared lifecycle by which any trigger source submits an order, tracks it from submission to execution, and reports the outcome. Four trigger sources consume this layer, each owned by its own epic:

| Trigger Source | Direction | Owned By |
|---|---|---|
| Cash-in (deposit settlement) | Buy | STRIV-265 (Cash In & Cash Out) |
| Cash-out (withdrawal) | Sell | STRIV-265 (Cash In & Cash Out) |
| Debit Card (capture) | Sell | STRIV-360 (Debit Card Authorization) |
| Dividend reinvestment | Buy | STRIV-401 (Smart Dividend Router) |

**Non-goals (out of scope):**

- Trigger logic itself (each trigger source epic owns its "when to submit" decision)
- Vault funding and withdrawal (pure ledger reallocations per STRIV-374 — no orders)
- Retry mechanics, backoff, dead-letter queues — technical decisions
- Order book, limit prices, trading strategies — all orders are fixed-price at the direct issuance price
- Conflict detection — the layer queues all orders; Clearing-Platform sorts availability

---

## Design

### Rule Group GR1 — Order Types & Structure

**Business rule.** Every SatC order carries a direction (Buy or Sell), a trigger source identifier, a SatC amount (in SatC shares, fractional allowed up to 6 decimal places), and a caller-supplied idempotency key. Buy orders are funded from fiat held at the Sponsor Bank; Sell orders originate from Non-Vault SatC only — Vault SatC is protected and never sold.

**Scenario GR1.1 — Order carries required fields.**

- **Given** a trigger source submits a SatC order
- **When** the order is accepted by the routing layer
- **Then** the order contains: direction (Buy or Sell), trigger source identifier, SatC amount, idempotency key, and timestamp
- **And** a Buy order records that fiat funding is available at the Sponsor Bank
- **And** a Sell order records that the SatC is sourced from Non-Vault SatC only

**Scenario GR1.2 — Sell order with Vault SatC source is rejected.**

- **Given** a trigger source submits a Sell order that would consume Vault SatC
- **When** the order is validated
- **Then** the order is rejected with an error indicating Vault SatC is protected
- **And** the trigger source is notified that the order could not be submitted

### Rule Group GR2 — Order Lifecycle

**Business rule.** Every order follows the lifecycle: `Pending → PendingSubmit → Executed / Failed`. Per CONTEXT.md, the Regular Session (9:30 AM–4:00 PM ET on NYSE trading days) governs whether SatC orders execute. Orders submitted during market hours move to `PendingSubmit` immediately; orders outside market hours remain in `Pending` until the next eligible session.

**Scenario GR2.1 — Order lifecycle during market hours.**

- **Given** a SatC Buy order is submitted during the Regular Session (9:30 AM–4:00 PM ET on a trading day)
- **When** the order is accepted
- **Then** the order transitions to `Pending` briefly
- **And** immediately transitions to `PendingSubmit`
- **And** the order is queued for submission to Clearing-Platform

**Scenario GR2.2 — Order lifecycle outside market hours.**

- **Given** a SatC Sell order is submitted outside the Regular Session (after 4:00 PM ET, before 9:30 AM ET, or on a non-trading day)
- **When** the order is accepted
- **Then** the order transitions to `Pending`
- **And** remains in `Pending` until the next Regular Session
- **And** at the start of the next session, it transitions to `PendingSubmit` in FIFO order

**Scenario GR2.3 — Order execution and failure.**

- **Given** a SatC order in `PendingSubmit` status
- **When** Clearing-Platform confirms the fill
- **Then** the order transitions to `Executed`
- **And** the balance is updated (Buy → SatC credited; Sell → fiat proceeds credited)

- **Given** a SatC order in `PendingSubmit` status
- **When** Clearing-Platform reports the order as unfillable
- **Then** the order transitions to `Failed`
- **And** the balance reservation is reversed

### Rule Group GR3 — Market-Hours Awareness & Pending Queue

**Business rule.** Orders submitted outside the Regular Session enter a Pending FIFO queue. They are submitted at the next Regular Session in submission order. Orders that remain in Pending for longer than 7 days auto-fail. When the market re-opens, the queue is drained in FIFO order during the session.

**Scenario GR3.1 — Pending queue processes in FIFO order.**

- **Given** three SatC orders (O1, O2, O3) submitted in that order outside market hours
- **When** the next Regular Session begins
- **Then** O1 transitions to `PendingSubmit` first, followed by O2, then O3

**Scenario GR3.2 — Order auto-fails after 7 days in Pending.**

- **Given** a SatC order that has been in `Pending` status for 8 days (exceeds the 7-day threshold)
- **When** the pendency check runs
- **Then** the order transitions to `Failed`
- **And** the trigger source is notified that the order expired
- **And** the balance reservation is reversed

### Rule Group GR4 — Idempotency & Duplicate Detection

**Business rule.** Duplicate submissions are rejected via the trigger-provided idempotency key. Idempotency is scoped per trigger source. Each trigger source maintains its own idempotency namespace so identical keys from different sources do not conflict.

**Scenario GR4.1 — Duplicate order is rejected.**

- **Given** a trigger source submits a SatC order with idempotency key `ABC123`
- **When** the same trigger source submits another order with the same idempotency key `ABC123`
- **Then** the second submission is recognized as a duplicate
- **And** the routing layer returns the status of the original order without creating a new order

**Scenario GR4.2 — Same idempotency key from different sources is accepted.**

- **Given** trigger source A submits an order with idempotency key `XYZ`
- **When** trigger source B submits a different order with the same idempotency key `XYZ`
- **Then** both orders are accepted as distinct (idempotency is scoped per trigger source)

---

## Edge Cases

| ID | Scenario | Expected Behavior |
|---|---|---|
| EC1 | Clearing-Platform is unreachable at submission time | Order stays in `PendingSubmit`; retry with backoff; escalates after N retries |
| EC2 | Regular Session ends while Pending queue is being drained | Remaining orders stay in `Pending`; drain resumes at the next Regular Session |
| EC3 | Trigger source submits order with zero or negative amount | Order is rejected at validation; trigger source notified |
| EC4 | Balance reservation fails (insufficient fiat/SatC at order time) | Order is rejected; trigger source notified; no balance change |
| EC5 | Clearing-Platform reports partial fill | Order is marked `Executed` with partial amount; unreconciled remainder is reported back to trigger source for handling |
| EC6 | Trigger source is not recognized | Order is rejected; the unknown source is logged as a security event |

---

## Tasks

### T1 — Order types, parameters, and trigger source validation
**Done when:** Buy and Sell order types are defined with required fields (direction, trigger source, SatC amount, idempotency key) per GR1.1; Sell orders from Vault SatC are rejected per GR1.2; zero/negative amounts rejected per EC3; unknown trigger sources rejected per EC6.

### T2 — Order lifecycle with market-hours awareness
**Done when:** Lifecycle statuses (Pending, PendingSubmit, Executed, Failed) are implemented per GR2; Pending→PendingSubmit transition gated by Regular Session per GR2.1/GR2.2; FIFO queue ordering per GR3.1; 7-day auto-fail per GR3.2; session-end pause per EC2.

### T3 — Execution outcomes and balance reconciliation
**Done when:** Executed orders credit/debit balances appropriately per GR2.3; Failed orders reverse reservations per GR2.3; partial fills report executed amount + unreconciled remainder per EC5; Clearing-Platform unreachable handled per EC1.

### T4 — Order history and audit trail
**Done when:** Every order produces an immutable record with order ID, trigger source, direction, amount, status history with timestamps, final outcome, and Clearing-Platform reference.

### T5 — Duplicate detection via idempotency keys
**Done when:** Duplicate submissions with same idempotency key and trigger source are rejected per GR4.1; same key from different sources accepted per GR4.2; idempotency scoped per trigger source.

### T6 — Insufficient balance at order time
**Done when:** Order with insufficient fiat (Buy) or SatC (Sell) is rejected per EC4; trigger source notified with specific error.