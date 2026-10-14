# Epic: Security Architecture

> **Product epic** — covers the security hardening of the Strive platform for production readiness: comprehensive observability (CloudWatch dashboards, alarms, X-Ray tracing), security auditing (OWASP Top 10 assessment), encryption of sensitive data at rest (KMS, Secrets Manager, S3 Object Lock), end-to-end test coverage for 5 critical user paths, and audit logging for all state-changing operations.
> **Audience:** Product managers, engineers, QA, compliance.
> **Non-goal:** This spec contains no technical implementation decisions — no service architecture, no code-level security patterns, no vendor-specific integration details beyond scope definition.
> **Referenced by:** `kb/docs/architecture/aws-foundation/`, `kb/specs/account-infra-stack.md` (STRIV-26).
> **Depends on:** STRIV-26 (Landing Zones & Infrastructure Foundation — VPC, subnets, CloudFront, WAF, Network Firewall).
> **Open decisions resolved:** OP-A (5-min standard, 1-min for critical path), OP-B (internal team for V1), OP-C (7 years per SEC Rule 17a-4).
> **Status:** Published as Jira epic **STRIV-45**.

---

## Proposal

The Strive platform handles sensitive financial data (user PII, SatC positions, card authorizations, ACH/Wire transfers) and real-time fiduciary operations (JIT debit authorization, market buy/sell orders, dividend routing to Bitcoin). Without observability, the team cannot detect incidents or performance degradation in a sub-100ms authorization path. Without security hardening, the platform exposes user PII and financial transaction data to potential breaches (OWASP Top 10 risks). Without E2E tests, the 5 critical user flows can regress without detection.

This epic covers five responsibility areas:

1. **Observability** — Provision CloudWatch dashboards and alarms for every application service and enable X-Ray distributed tracing across the BFF and backend with trace header propagation.
2. **Security Auditing** — Perform a comprehensive OWASP Top 10 security assessment covering all 10 vulnerability categories and remediate or document accepted risks.
3. **Data Encryption** — Encrypt all sensitive data at rest (RDS, DynamoDB, S3 with SSE-KMS) and manage secrets via AWS Secrets Manager.
4. **End-to-End Test Coverage** — Establish E2E test suites for 5 critical user paths (onboarding to ACTIVE, deposit to rebalance, card authorization, withdrawal, vault creation to funding) running in CI.
5. **Audit Logging** — Log all state-changing operations immutably with timestamp, user ID, operation type, before/after state, and correlation ID.

**Non-goals (out of scope):**

- Application business logic (owned by individual feature epics)
- Infrastructure provisioning (owned by STRIV-26 — VPC, subnets, CloudFront, WAF, Network Firewall)
- Third-party vendor compliance audits (each vendor owns its own compliance posture)
- Penetration testing by external firms (post-launch scope)

---

## Design

### Rule Group GR1 — Observability

**Business rule.** Every application service shall have a CloudWatch dashboard displaying latency (p50, p90, p99), error rate, throughput, and Lambda invocation metrics. Alarms shall fire: error rate >5% over 5 minutes (1 minute for critical path), p99 latency >2 seconds over 5 minutes (1 minute for critical path), Lambda errors >10 in 5 minutes. X-Ray distributed tracing shall span the BFF through gRPC to backend services.

**Scenario GR1.1 — CloudWatch dashboard shows service metrics.**

- **Given** a deployed application service (BFF, backend, or Lambda function)
- **When** the CloudWatch dashboard is opened
- **Then** it displays request latency (p50, p90, p99), error rate, throughput, and Lambda invocation metrics
- **And** the dashboard is accessible to the on-call team via the AWS Console

**Scenario GR1.2 — Alarm triggers on high error rate.**

- **Given** an application service with error rate exceeding 5% over a 5-minute window
- **When** the error threshold is breached
- **Then** a CloudWatch alarm fires and notifies the on-call channel within 5 minutes

**Scenario GR1.3 — Critical-path alarm triggers in 1 minute.**

- **Given** the card authorization path has an error rate exceeding 5% over a 1-minute window
- **When** the error threshold is breached
- **Then** a CloudWatch alarm fires and notifies the on-call channel within 1 minute

**Scenario GR1.4 — X-Ray trace spans BFF to backend.**

- **Given** a request enters the BFF
- **When** the BFF makes a gRPC call to the backend
- **Then** an X-Ray trace header is propagated through the gRPC call
- **And** each service hop records segment-level timing

### Rule Group GR2 — Security Auditing (OWASP Top 10)

**Business rule.** An internal security team shall assess the platform against all 10 OWASP Top 10 vulnerability categories for V1. Identified risks shall be remediated or documented as accepted with a mitigation plan.

**Scenario GR2.1 — Injection vulnerabilities are prevented.**

- **Given** the platform accepts user input
- **When** the input is processed
- **Then** all inputs are validated, sanitized, and parameterized
- **And** WAF rules (from STRIV-26) have SQL injection and XSS rule groups enabled

**Scenario GR2.2 — Broken access control is enforced.**

- **Given** a user requests access to a resource
- **When** the request is processed
- **Then** the platform verifies the user owns or is authorized to access that resource
- **And** RBAC is enforced at the API gateway and service layer

**Scenario GR2.3 — Sensitive data is not exposed in logs.**

- **Given** sensitive data (PII, financial records, card numbers) is processed
- **When** the request is logged or traced
- **Then** no sensitive data appears in CloudWatch logs or X-Ray traces
- **And** redaction filters are applied before logging

**Scenario GR2.4 — Dependency scanning detects known vulnerabilities.**

- **Given** dependencies are installed or updated
- **When** the CI pipeline runs
- **Then** a dependency scanning tool (npm audit or Dependabot) runs and fails the build on critical CVEs

### Rule Group GR3 — Data Encryption

**Business rule.** All sensitive data shall be encrypted at rest using AWS-managed KMS keys. Secrets shall be stored in AWS Secrets Manager and retrieved at runtime via IAM roles — never in source code or environment variables. S3 Object Lock shall be enabled for audit log immutability.

**Scenario GR3.1 — Database is encrypted at rest.**

- **Given** an RDS or DynamoDB instance is provisioned
- **When** data is written
- **Then** it is encrypted at rest using AWS-managed KMS keys
- **And** encryption is enabled at provisioning time

**Scenario GR3.2 — Secrets are never in source code.**

- **Given** a secret is needed by an application service
- **When** the service starts
- **Then** the secret is retrieved from AWS Secrets Manager via IAM role credentials
- **And** no secret appears in source code, plaintext environment variables, or container image layers

**Scenario GR3.3 — S3 Object Lock prevents audit log tampering.**

- **Given** an audit log entry is written to S3
- **When** the Object Lock is enabled in governance mode
- **Then** the entry is immutable for the 7-year retention period
- **And** no user or service can delete or modify the entry

### Rule Group GR4 — End-to-End Test Coverage

**Business rule.** Five critical user paths shall have E2E test suites running in CI on every PR to develop and main, using mocked vendor adapters.

**Scenario GR4.1 — Onboarding to ACTIVE E2E test passes.**

- **Given** a new user registration
- **When** the E2E test runs
- **Then** it simulates registration → KYC → identity verification → account provisioning → ACTIVE status
- **And** asserts the user can log in and view the dashboard

**Scenario GR4.2 — Deposit to rebalance E2E test passes.**

- **Given** a user initiates an ACH deposit
- **When** the E2E test runs
- **Then** it simulates deposit → SatC buy order → balance update → rebalancer trigger
- **And** asserts the balance reflects the deposited amount

**Scenario GR4.3 — Card authorization E2E test passes.**

- **Given** a card swipe is simulated
- **When** the E2E test runs
- **Then** it simulates Galileo authorization webhook → balance check → authorize/deny → hold lock → balance update
- **And** asserts a swipe within available balance is authorized and the hold is applied

**Scenario GR4.4 — Withdrawal E2E test passes.**

- **Given** a user requests a withdrawal
- **When** the E2E test runs
- **Then** it simulates withdrawal request → balance check → SatC sell order → USD settlement → external transfer → balance update
- **And** asserts the withdrawn amount is deducted

**Scenario GR4.5 — Vault creation to funding E2E test passes.**

- **Given** a user creates a new vault
- **When** the E2E test runs
- **Then** it simulates vault creation → funding from SatC → balance update
- **And** asserts the vault is created and funded with the specified amount

**Scenario GR4.6 — CI runs all E2E tests on every PR.**

- **Given** a PR is opened to develop or main
- **When** CI triggers
- **Then** all 5 E2E test suites run using mocked vendor adapters
- **And** a failing test blocks the PR from merging
- **And** test results are published as a CI artifact

### Rule Group GR5 — Audit Logging

**Business rule.** Every state-changing operation shall produce an immutable audit log entry with timestamp (UTC), user ID, operation type, before/after state (JSON), and correlation ID. Logs shall be stored in S3 with Object Lock enabled for a 7-year retention period.

**Scenario GR5.1 — State change produces audit log.**

- **Given** a state-changing operation (account creation, balance change, vault operation, card transaction, withdrawal, deposit, rebalancer run)
- **When** the operation completes
- **Then** an audit log entry is written with timestamp (UTC), user ID, operation type, before-state (JSON), after-state (JSON), and correlation ID
- **And** the log is stored in S3 with Object Lock enabled

**Scenario GR5.2 — Audit log write failure rolls back the operation.**

- **Given** the S3 Object Lock bucket is unavailable
- **When** the audit log write attempt fails
- **Then** the state-changing operation is rolled back (no state change without audit log)
- **And** a CloudWatch alarm fires for audit log write failure

**Scenario GR5.3 — Correlation ID propagates end-to-end.**

- **Given** a request flows through the BFF, backend, and external integrations
- **When** the request is processed
- **Then** a correlation ID is generated at the entry point and propagated through all downstream calls
- **And** the correlation ID appears in X-Ray traces and audit log entries

---

## Edge Cases

| ID | Scenario | Expected Behavior |
|---|---|---|
| EC1 | X-Ray trace header is dropped by an intermediary (ALB, Network Firewall) | Trace continues from re-injection point; warning logged but request not blocked |
| EC2 | CloudWatch alarm fires during a deployment window | Alarm auto-acknowledged for 30 min; re-armed after; escalates if deployment exceeds 30 min |
| EC3 | Secrets Manager is unavailable during service startup | Service fails fast — does not start with fallback/plaintext secrets; CloudWatch alarm fires |
| EC4 | OWASP assessment identifies a critical vulnerability that cannot be remediated before launch | Risk documented as accepted with mitigation plan; interim WAF rule deployed; remediation ticket created with deadline |
| EC5 | Audit log write fails (S3 Object Lock unavailable) | State-changing operation rolled back; CloudWatch alarm fires; retry with exponential backoff |
| EC6 | E2E test is flaky (passes locally, fails in CI) | Test quarantined; bug ticket created; PR not blocked by quarantined test; must fix within 1 sprint |
| EC7 | Correlation ID is missing from an inbound vendor webhook | Strive generates new correlation ID at ingestion; vendor-provided ID logged as secondary reference |
| EC8 | S3 bucket encryption is disabled by a misconfigured update | Bucket policy denies the update; Config rule alerts on encryption-status change |
| EC9 | Mocked vendor adapter diverges from real API contract | Mock updated to match real contract; contract test added to detect drift on weekly cadence |
| EC10 | User attempts to access another user's balance | API returns 403; access attempt logged as security event; repeated attempts trigger brute-force alert |

---

## Tasks

### T1 — Provision CloudWatch dashboards and alarms
**Done when:** Dashboards display latency, error rate, throughput per GR1.1; alarms fire on thresholds per GR1.2; critical-path alarms fire in 1 minute per GR1.3; alarm notifications route to on-call channel; deployment-window suppression per EC2.

### T2 — Enable X-Ray distributed tracing
**Done when:** Traces show end-to-end request flow from BFF through gRPC to backend per GR1.4; trace headers propagated through all gRPC calls; dropped header fallback per EC1.

### T3 — Perform OWASP Top 10 security assessment
**Done when:** All 10 OWASP categories assessed by internal team per GR2; injection, access control, sensitive data exposure, and dependency scanning covered per GR2.1–GR2.4; risks remediated or accepted with mitigation plan per EC4; dependency scanning runs in CI.

### T4 — Encrypt all sensitive data at rest
**Done when:** RDS and DynamoDB use KMS encryption per GR3.1; S3 uses SSE-KMS with Object Lock per GR3.3; all secrets in AWS Secrets Manager per GR3.2; encryption disablement guarded per EC8.

### T5 — Establish E2E test suites for 5 critical user paths
**Done when:** All 5 E2E tests (onboarding per GR4.1, deposit per GR4.2, card auth per GR4.3, withdrawal per GR4.4, vault per GR4.5) pass in CI per GR4.6; flaky test quarantine per EC6; mock drift detection per EC9.

### T6 — Implement audit logging
**Done when:** Every state-changing operation logs per GR5.1; logs stored in S3 Object Lock bucket immutably; failed write rolls back operation per GR5.2/EC5; correlation ID propagated per GR5.3/EC7.

### T7 — Access control enforcement and security logging
**Done when:** Unauthorized access returns 403 per EC10; access attempts logged as security events; repeated failures trigger brute-force alert.