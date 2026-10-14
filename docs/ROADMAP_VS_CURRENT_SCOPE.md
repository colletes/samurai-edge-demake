# Strive — Product Roadmap vs Current Scope Traceability

> **Source:** `/Users/thiagocarvalho/Downloads/Product Roadmap.docx` (MVP vs Phased classification)
> **Targets:** STRIV Jira Project + Bitbucket Workspace (`altran-ais/strive-workspace`)

## Legend

| Icon | Meaning |
|---|---|
| ✅ | Epic exists + spec exists in Bitbucket |
| ⚠️ | Epic exists but cancelled or has gaps |
| ❌ | No epic / no spec / not found |
| 🟢 | Epic exists, not started (To Do) |
| 🔵 | In Progress |
| 🟢 | Done |

---

## MVP Features (Must Have at Launch)

| # | Feature | Jira Epic | Bitbucket Spec | Status | Gap |
|---|---|---|---|---|---|
| 1 | **High-Yield Checking Account** (SATA-backed, 10.40% APY) | STRIV-377 (Local Ledger) 🟢, STRIV-187 (Rebalancer — Cancelled) ⚠️ | `kb/specs/local-ledger-epic.md` ✅, `kb/specs/dividend-router-epic.md` ✅ | Partial — rebalancer cancelled, cash-in/out To Do | Rebalancer needs re-scoping |
| 2 | **Virtual Debit Card** (Visa/MC) | STRIV-360 🟢 | `kb/specs/debit-card-authorization-limit-epic.md` ✅ | To Do | No started |
| 3 | **Account Opening Flow** (Web + Mobile, <10 min) | STRIV-301 🟢 | `kb/specs/cognito-onboarding-integration.md` ✅ | To Do | Needs full exec plan |
| 4 | **Account KYC / Identity Verification** | STRIV-260 (Cancelled) ⚠️, STRIV-301 (partial) 🟢 | `kb/specs/cognito-onboarding-integration.md` ✅ | Cancelled/Partial | No active KYC-dedicated epic |
| 5 | **ACH Deposits & Withdrawals** | STRIV-265 🟢 | `kb/specs/cashin-cashout-epic.md` ✅ | To Do | Not started |
| 6 | **Client Direct Deposit** (routing/account #, early pay) | ❌ | ❌ | **Missing** | Needs epic and spec |
| 7 | **Daily SATA Dividend Accrual & Crediting** | STRIV-187 (Cancelled) ⚠️ | `kb/specs/dividend-router-epic.md` ✅ | Cancelled | **Core differentiator — critical** |
| 8 | **T+0 Liquidity Float / Credit Facility** | ❌ | ❌ | **Missing** | Needs infrastructure epic |
| 9 | **Customer Dashboard** (balance, earnings, vaults) | STRIV-266 🟢, STRIV-28 🟢 | `kb/specs/mobile-screens-epic.md` ✅ | To Do | Wireframes spec exists but dev not started |
| 10 | **Risk Disclosures & Educational Content** | ❌ | ❌ | **Missing** | Needs epic |
| 11 | **Alerts & Notification System** (email, SMS, push) | ❌ | ❌ | **Missing** | Needs epic |
| 12 | **Customer Support** (chat bot + live agent) & **Monthly Statements** | ❌ | ❌ | **Missing** | Needs epic |
| 13 | **Physical Debit Card** | STRIV-360 🟢 | `kb/specs/debit-card-authorization-limit-epic.md` ✅ | To Do | Extends virtual card scope |
| 14 | **iOS Mobile, Android Mobile, Web App** | STRIV-266 🟢, STRIV-28 🟢, STRIV-29 🟢 | `kb/specs/mobile-screens-epic.md` ✅ | Partially started | Design system To Do, mobile screens To Do |
| 15 | **Cash vs SATA Balance Allocation** | STRIV-187 (Cancelled) ⚠️ | ❌ | Cancelled | Needs re-scoping |
| 16 | **Bitcoin Dividend Routing** (BitGo custody) | STRIV-375 🟢 | `kb/specs/bitcoin-epic.md` ✅ | To Do | BitGo commercial agreement dependency |
| 17 | **Apple / Google / Samsung Wallet Integration** | ❌ | ❌ | **Missing** | Needs epic |
| 18 | **Vaults** (goal-based sub-accounts, up to 10) | STRIV-374 🟢 | ❌ (domain concepts in CONTEXT.md) | To Do | Spec stub needed in Bitbucket |

---

## Phase 2 Features

| # | Feature | Jira Epic | Bitbucket Spec | Status | Gap |
|---|---|---|---|---|---|
| 19 | **Tax Document Download** (1099s) | ❌ | ❌ | **Missing** | Needs epic |
| 20 | **Plaid Integration** | ❌ | ❌ | **Missing** | Needs epic |
| 21 | **Referral Program** | ❌ | ❌ | **Missing** | Needs epic |
| 22 | **"Plus" Account** (no market risk) | ❌ | ❌ | **Missing** | Needs epic + PRD |
| 23 | **Strive BTC Rewards Credit Card** | ❌ | ❌ | **Missing** | Needs epic |

---

## Phase 3 Features

| # | Feature | Jira Epic | Bitbucket Spec | Status | Gap |
|---|---|---|---|---|---|
| 24 | **Joint Accounts** | ❌ | ❌ | Future scope | — |
| 25 | **Beneficiary / TOD / POD** | ❌ | ❌ | Future scope | — |
| 26 | **Zelle / Real-Time Payments** | ❌ | ❌ | Future scope | — |
| 27 | **Wire Transfers** | ❌ | ❌ | Future scope | — |
| 28 | **Security Architecture** | STRIV-45 🟢 | ❌ | To Do | Needs spec stub |

---

## Phase 4 Features

| # | Feature | Jira Epic | Bitbucket Spec | Status | Gap |
|---|---|---|---|---|---|
| 29 | **Business / SMB Accounts** | ❌ | ❌ | Future scope | — |
| 30 | **International Banking / FX** | ❌ | ❌ | Long-term aspiration | — |

---

## Completed Work

| Issue | What Was Done |
|---|---|
| STRIV-51 | Static Core AWS Infrastructure (VPC, Subnets, ALB, WAF) — DONE |
| STRIV-54 | Shared Resource Export via SSM Parameter Store — DONE |
| STRIV-56 | Apex Hexagonal Adapter & Ports Layer — DONE |
| STRIV-60 | Define Core Business Goals & MVP Scope Baseline — DONE |
| STRIV-61 | Map User Journeys & MVP Feature Set — DONE |
| Infrastructure | `kb/specs/account-infra-stack.md` deployed (network-foundation, infra-stack, cognito-pool, identity-documents) |

---

## Summary of Critical Gaps

### Active Epics Needing Immediate Attention

| Priority | Epic | Issue |
|---|---|---|
| 🔴 Critical | STRIV-187 (Rebalancer) | Cancelled — core product differentiator (SATA dividend + allocation) with no replacement |
| 🔴 Critical | STRIV-260 (Onboarding/KYC) | Cancelled — new user onboarding is MVP, but re-created as STRIV-301. Ensure no scope loss |
| 🟡 High | 7x missing MVP epics | Direct Deposit, T+0 Liquidity, Risk Disclosures, Alerts, Support, Wallet Integration, Physical Card UX — all labelled MVP in roadmap but absent from Jira |
| 🟡 High | 5x missing Phase 2 epics | Tax Docs, Plaid, Referral, Plus Account, BTC Credit Card |
| 🔵 Medium | STRIV-45 (Security) | Has an epic but no spec in Bitbucket |

### Counts

- **MVP features with active epics:** 11/18
- **MVP features with no epic at all:** 7
- **Phase 2 features with no epic:** 5/5
- **Cancelled epics needing replacement:** 2 (Rebalancer, KYC Onboarding)
- **Epics missing Saga labels:** 9
- **Epics missing Phase labels:** 5
- **Bitbucket specs without active Jira epic:** 1 (`dividend-router-epic.md` → Rebalancer was cancelled)
- **Jira epics without Bitbucket spec:** 2 (SatC Order Routing, Security Architecture)