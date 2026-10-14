# Handoff: SDD Agent — Epic Refactoring (Strive Project)

## Objective

Refactor the STRIV Jira project epics to align with the Product Roadmap, Bitbucket repo specs, and consistent labeling conventions. This handoff is scoped to avoid affecting SDD's existing ways of working (no changes to workflows, statuses, custom fields, or SDD agents).

## Sources

| Source | URL / Path |
|---|---|
| Bitbucket Workspace (develop) | `https://bitbucket.org/altran-ais/strive-workspace/src/develop/` (PAT at `~/.config/marvincode/PAT_bitbucket.txt`) |
| Jira STRIV Project | `https://aistech.atlassian.net/jira/software/c/projects/STRIV/boards/3113` (cloudId: `f05e3f8f-fa45-468e-867b-91db92bbb54e`) |
| Product Roadmap | `/Users/thiagocarvalho/Downloads/Product Roadmap.docx` |

## Instructions

### 1. Label Remapping — Phase Alignment

Rename Phase labels on all epics to match the Product Roadmap:

| Current Label | New Label | Applies To |
|---|---|---|
| `Phase_1` | `MVP` | STRIV-26, STRIV-28, STRIV-29 |
| `Phase_2` | `Phase_2` | Keep as-is (STRIV-265, STRIV-266, STRIV-374, STRIV-375) |
| `Phase_3` | `Phase_3` | Keep as-is (STRIV-45) |
| *(missing)* | `MVP` | Add to: STRIV-301 (Onboarding), STRIV-360 (Debit Card), STRIV-374 (Vaults), STRIV-375 (Bitcoin), STRIV-376 (SatC), STRIV-377 (Local Ledger) |

### 2. Add Missing Saga Labels

| Epic | Saga Label to Add |
|---|---|
| STRIV-265 (Cash In/Out — Fiat) | `Saga_Core` |
| STRIV-266 (Mobile Screens V1) | `Saga_Experience` |
| STRIV-301 (Onboarding) | `Saga_Foundation` |
| STRIV-360 (Debit Card) | `Saga_Integration` |
| STRIV-374 (Vaults) | `Saga_Core` |
| STRIV-375 (Bitcoin) | `Saga_Core` |
| STRIV-376 (SatC Order Routing) | `Saga_Integration` |
| STRIV-377 (Local Ledger) | `Saga_Core` |

### 3. Mark Duplicate Stories as Cancelled

Transition the following stories to **Cancelled** status:

- **STRIV-53**: `[DUPLICATE - see STRIV-228, STRIV-229, STRIV-230] Application-Level CDK Constructs`
- **STRIV-64**: `[DUPLICATE - see STRIV-213, STRIV-215, STRIV-216] NestJS API Gateway with JWT Validation`
- **STRIV-65**: `[DUPLICATE - see STRIV-220, STRIV-221, STRIV-222, STRIV-224] React + TypeScript Web UI Framework`

### 4. Create Stub Epics for Missing Specs

For these epics, ensure bitbucket spec files exist in `kb/specs/` (or create minimal stubs). Cross-reference the spec path in the Jira epic description.

| Jira Epic | Spec Path in Bitbucket | Action |
|---|---|---|
| STRIV-376 (SatC Order Routing) | `kb/specs/satc-order-routing-epic.md` | Create stub spec with placeholder content |
| STRIV-45 (Security Architecture) | `kb/specs/security-architecture-epic.md` | Create stub spec with placeholder content |

### 5. Cross-Reference Specs in Epic Descriptions

For each active epic that has a corresponding Bitbucket spec, add a reference line at the top of the epic description:

```
**Spec reference:** `kb/specs/<filename>.md` in Bitbucket workspace
```

Mapping:

| Epic Key | Bitbucket Spec File |
|---|---|
| STRIV-26 | `kb/specs/account-infra-stack.md` |
| STRIV-265 | `kb/specs/cashin-cashout-epic.md` |
| STRIV-266 | `kb/specs/mobile-screens-epic.md` |
| STRIV-301 | `kb/specs/cognito-onboarding-integration.md` |
| STRIV-360 | `kb/specs/debit-card-authorization-limit-epic.md` |
| STRIV-374 | `kb/specs/vaults-epic.md` (to be created; reference `goal-based-savings` domain concepts in CONTEXT.md) |
| STRIV-375 | `kb/specs/bitcoin-epic.md` |
| STRIV-377 | `kb/specs/local-ledger-epic.md` |

### 6. What NOT to Change

| Item | Keep As-Is |
|---|---|
| Workflows / statuses | SDD agents own these |
| Custom fields | SDD convention unchanged |
| Sprint assignments | Not part of this refactor |
| Issue hierarchy (Epic → Story → Task) | Preserve existing structure |
| Project permissions / schemes | Out of scope |
| Confluence sync or docs | Out of scope |

## Verification Checklist

- [ ] All 16 epics have consistent `Phase_*`/`MVP` labels matching the roadmap
- [ ] All active epics have a `Saga_*` label assigned
- [ ] Duplicate stories (STRIV-53, STRIV-64, STRIV-65) are Cancelled
- [ ] Stub specs created in Bitbucket for missing epics
- [ ] Every active epic has a spec reference in its Jira description
- [ ] No changes to SDD workflows, statuses, custom fields, or permissions