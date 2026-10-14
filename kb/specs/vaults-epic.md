# Epic: Vaults — Goal-Based Savings Sub-Ledgers

> **Product epic** — covers the Vaults feature of the Strive platform: goal-based savings sub-ledgers. Defines how users create Vaults, fund them (move money in), withdraw from them (move money out), delete them, and how Vault balances are presented and isolated from the rest of the platform.
> **Audience:** Product managers, engineers, QA.
> **Non-goal:** This spec contains no technical implementation decisions — no ledger schema, no service boundaries, no state-machine design, no ports/adapters, no API contracts.
> **Referenced by:** `kb/docs/design-docs/business-rules/product-vision.md` (sections 4.3, 5.5), `kb/specs/local-ledger-epic.md` (STRIV-377).
> **Status:** Published as Jira epic **STRIV-374**.

---

## Proposal

Vaults are goal-based savings sub-ledgers that allow users to allocate a portion of their SatC balance toward named savings goals. Vaults are a **local logical balance separation in the Ledger** — not separate accounts. The user's total balance never changes when they fund or withdraw from a Vault; only the visible Non-Vault/Vault breakdown does. All Vault funds are held in **SatC** (a direct issuance by Strive through a Broker at a fixed price, held at Clearing-Platform) — the same investment security as the main balance.

This epic defines:

1. **Creation & naming** — Up to 10 active Vaults with unique names (1–40 characters, restricted character set). Deleted Vaults free their slot.
2. **Funding (move in)** — Pure ledger reallocation from Non-Vault SatC to the Vault. No Buy or Sell order. Applied immediately.
3. **Withdrawal (move out)** — Pure ledger reallocation back to Non-Vault SatC. No Sell or Buy order. Applied immediately. No source override.
4. **Deletion** — Empty-only. Frees the slot and releases the name.
5. **Display** — Total balance includes Non-Vault SatC + Vault SatC. Each Vault shows its name and current value.
6. **Platform isolation** — Vault SatC is excluded from the debit card limit and never sold for card settlement. Vault SatC is protected from external withdrawals.

**Non-goals (out of scope):**

- Recurring contributions (manual transfers only for V1)
- Vault-specific allocation rules or target-date investing
- Separate investment strategies per Vault (all Vaults hold SatC)
- Any technical decision on how the ledger stores Vault sub-ledgers

---

## Design

### Rule Group GR1 — Vault Creation & Naming

**Business rule.** A user may create up to 10 active Vaults with unique names (1–40 characters, letters/digits/spaces/hyphens/apostrophes only). Names must be unique among the user's active Vaults. Renaming is allowed at any time.

**Scenario GR1.1 — User creates a Vault with a valid name.**

- **Given** a user with fewer than 10 active Vaults
- **When** they create a Vault named "Emergency Fund"
- **Then** the Vault is created with name "Emergency Fund"
- **And** the user now has one additional active Vault

**Scenario GR1.2 — User creates a Vault with a duplicate name.**

- **Given** a user with an active Vault named "Emergency Fund"
- **When** they attempt to create another Vault named "Emergency Fund"
- **Then** the creation is rejected with an error indicating the name is already in use

**Scenario GR1.3 — User creates a 11th Vault.**

- **Given** a user with 10 active Vaults
- **When** they attempt to create another Vault
- **Then** the creation is blocked with a message indicating the maximum of 10 Vaults has been reached

**Scenario GR1.4 — User renames a Vault.**

- **Given** a Vault named "Trip 2026"
- **When** the user renames it to "Europe Trip"
- **Then** the Vault name is updated to "Europe Trip"
- **And** the old name is released for reuse

### Rule Group GR2 — Vault Funding

**Business rule.** Funding a Vault moves SatC from the user's Non-Vault balance to the Vault as a pure ledger reallocation — no Buy or Sell order is sent to Clearing-Platform. The credit is applied immediately. The user's total balance is unchanged.

**Scenario GR2.1 — User funds a Vault.**

- **Given** a user with Non-Vault SatC balance of $5,000 and a Vault named "Emergency" with $0 balance
- **When** they fund the Vault with $1,000
- **Then** the Non-Vault SatC balance decreases by $1,000 to $4,000
- **And** the Vault "Emergency" balance increases to $1,000
- **And** the user's total balance remains $5,000

**Scenario GR2.2 — User funds a Vault with insufficient Non-Vault SatC.**

- **Given** a user with Non-Vault SatC balance of $500
- **When** they attempt to fund a Vault with $1,000
- **Then** the funding is rejected with an insufficient-balance error

### Rule Group GR3 — Vault Withdrawal

**Business rule.** Withdrawing from a Vault moves SatC back to the Non-Vault balance as a pure ledger reallocation — no Sell or Buy order. The debit and credit are applied immediately. There is no source override — funds always return to Non-Vault SatC.

**Scenario GR3.1 — User withdraws from a Vault.**

- **Given** a Vault with $2,000 balance
- **When** the user withdraws $500 from the Vault
- **Then** the Vault balance decreases by $500 to $1,500
- **And** the Non-Vault SatC balance increases by $500
- **And** the user's total balance is unchanged

**Scenario GR3.2 — User withdraws more than the Vault balance.**

- **Given** a Vault with $500 balance
- **When** the user attempts to withdraw $600
- **Then** the withdrawal is rejected with an insufficient-balance error

### Rule Group GR4 — Vault Deletion

**Business rule.** A Vault must have a zero balance before it can be deleted. Deleting frees the slot toward the 10-Vault limit and releases the name for reuse.

**Scenario GR4.1 — User deletes an empty Vault.**

- **Given** a Vault with $0 balance
- **When** the user deletes the Vault
- **Then** the Vault is removed
- **And** the slot is freed (user can create up to 10 Vaults again)
- **And** the name is available for reuse

**Scenario GR4.2 — User attempts to delete a Vault with funds.**

- **Given** a Vault with $500 balance
- **When** the user attempts to delete the Vault
- **Then** deletion is blocked with a message to withdraw or empty the Vault first

### Rule Group GR5 — Platform Isolation

**Business rule.** Vault SatC is excluded from the debit card available limit and is never sold for card settlement. Vault SatC is protected from external withdrawals — withdrawals consume Non-Vault SatC only.

**Scenario GR5.1 — Vault SatC does not increase card limit.**

- **Given** a user with Non-Vault SatC of $5,000 and Vault SatC of $3,000
- **When** the card's available limit is determined
- **Then** the limit is based on Non-Vault SatC only ($5,000)
- **And** Vault SatC ($3,000) contributes nothing to the limit

**Scenario GR5.2 — Card authorization cannot consume Vault SatC.**

- **Given** a user with $0 Non-Vault SatC and $1,000 Vault SatC
- **When** a card authorization request arrives
- **Then** the authorization is declined (insufficient Non-Vault SatC)
- **And** Vault SatC is never sold to satisfy the authorization

---

## Tasks

### T1 — Vault creation, naming, and rename
**Done when:** Users can create up to 10 active Vaults with valid names per GR1.1; duplicate names rejected per GR1.2; 11th Vault blocked per GR1.3; rename works per GR1.4.

### T2 — Vault funding from Non-Vault SatC
**Done when:** Funding moves SatC from Non-Vault to Vault immediately per GR2.1; insufficient balance rejected per GR2.2.

### T3 — Vault withdrawal to main balance
**Done when:** Withdrawal moves SatC from Vault back to Non-Vault immediately per GR3.1; excess withdrawal rejected per GR3.2.

### T4 — Vault deletion (empty-only)
**Done when:** Empty Vault can be deleted, freeing slot and name per GR4.1; funded Vault deletion blocked per GR4.2.

### T5 — Vault display and balance presentation
**Done when:** Total balance includes Non-Vault + Vault SatC; each Vault shows name and current value in USD.

### T6 — Vault platform isolation
**Done when:** Vault SatC excluded from card limit per GR5.1; card cannot consume Vault SatC per GR5.2.