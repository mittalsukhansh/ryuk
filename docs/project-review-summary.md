> **Publication scope:** Submission tag `v0.1.2-sandbox-demo` points to `af750c2`. Production foundations are on `production-foundation` for review only, excluded from main and the submission. No deployment or real-ledger migration.

# Ryuk — project-wide review handoff

As of 2026-11-12. This describes repository implementation, not a production certificate or a scoring claim. The presentation/provenance/docs batch was previously pushed at `af750c2`. The production-foundation changes described here are included on **production-foundation (review only)**, together with the earlier presentation/provenance work. This source freeze does not deploy or upgrade an installation.

## What Ryuk does

Ryuk turns a buyer's natural-language purchase request into a validated hotel intent, retrieves a labeled synthetic catalog, verifies mandatory/preferred requirements with evidence, evaluates deterministic financial policy, obtains exact human consent and separate PayPal Sandbox buyer approval, and records the backend-confirmed checkout. It does not search Google, reserve hotel inventory, make real bookings or use real money. **The LLM proposes; only the deterministic backend authorizes spending.**

## Implemented across the project

| Area | Existing implementation and new local foundations |
| --- | --- |
| Stack and startup | FastAPI/Pydantic backend; Next.js/TypeScript casebook; non-root application images; loopback Compose ingress, health checks and persistent protected SQLite storage. |
| Intent parsing | Backend-only OpenAI/Groq selection with `LLM_PROVIDER`, explicit model settings, structured output, strict schemas, original-quote validation and integer minor-unit money. No provider credential is public. |
| Intent provenance | Persist validated mandatory/preferred source quotes and Unicode spans; show original text beside parsed requirements with keyboard-accessible highlights. Preserve legacy serialization/digests. Quotes do not prove semantic completeness. |
| Catalog and verifier | Eight synthetic hotel offers, structured evidence, PASS/FAIL/UNKNOWN mandatory checks, preferred scoring and a bound verification snapshot. Missing evidence is not a PASS. |
| Deterministic policy | Explicit currency, total budget, threshold, merchant, mandatory requirement, approval and duplicate/uncertainty checks. Browser/model output cannot alter authoritative amounts or policy. Reason codes remain visible with plain-English explanations. |
| Consent | Digest-bound original-versus-parsed review for all model-derived purchases, exact merchant/amount/currency consent, expiry/rejection/invalidation/replay handling and pre-capture revalidation. PayPal buyer authorization remains separate. |
| Durable execution | Canonical proposals, approvals, early audit, checkouts, holds and settlement persisted in SQLite. Atomic reservation/dispatch claims, stable operation keys and duplicate protection across connections/restarts; one ledger settlement per capture. |
| Recovery | Owner-scoped saved activity/audit, existing-payment status controls, GET-only uncertain capture reconciliation, narrowly verified instrument-decline recovery and explicit operator inspection. Unknown creates/captures remain blocked rather than retried blindly. |
| PayPal | Sandbox-only Orders v2 adapter validates exact order/merchant/capture/amount/currency and final capture evidence. Backend confirmation is required for success. Credentials remain backend-only. |
| Security | Authenticated model requests, sanitized validation/provider errors, HTTPS secure-cookie checks, origin checks, authenticated proxy client identity, private caching rules and per-document nonce CSP with PayPal nonce propagation. No model spending authority. |
| Presentation | Persistent Sandbox/synthetic/no-real-money notice, evidence matrix, original intent review, reason explanations, settled/held/available budget display, bounded waiting/error guidance, responsive keyboard controls, README/startup guide, Mermaid architecture and demo script. |
| Evidence | Consistent protected backups, receipt exporter, documented acceptance scenarios and isolated browser fixture that cannot reuse an existing ledger. |
| New: schema/provisioning | Four ordered checksummed forward migrations, legacy adoption, transactional failure rollback, concurrent startup checks, atomic bootstrap and immutable policy versions. No automatic financial reset. |
| New: optional local identities | Operator-created local users with isolated budgets/policies, salted scrypt, hashed persistent expiring sessions, reset/disable revocation and cross-instance DB quotas. Demo login remains default; local mode is optional. |
| New: resource limits | Body size/deadlines, bounded in-flight requests, DB-backed login/model leases and rate allocation, session/proposal/approval caps, Compose CPU/memory/PID limits. |
| New: provider operations | GET-only paged monitoring including terminal payments, separate later provider observations, verified/deduplicated Sandbox events, once-only external-capture/full-refund/reversal adjustments. |
| New: refunds | Buyer-owned durable full-refund requests; explicit operator approve/reject; separate opt-in one-shot dispatch with stable key; no repeated POST after ambiguity; GET/webhook reconciliation. Saved activity shows review/provider status after reload. Gross purchase budget is not silently replenished. |

## Validation of the source-freeze implementation

- **1,153 backend tests pass**, with zero failures/errors/skips; baseline was 1,114. Thirty-nine added regressions cover migration preservation/rollback/concurrency, atomic bootstrap, immutable policy versions, local identity isolation/revocation/quota persistence, body/concurrency boundaries, reviewed refund ownership/duplicate/timeout/concurrent dispatch and authenticated provider adjustments.
- **25 frontend helper tests pass**, no skips; lint, TypeScript checks and production build pass.
- **102 isolated Chromium assertions pass**, including the real UI → Next proxy → FastAPI/services → fresh SQLite flow, source highlights, CSP injection blocking, desktop/mobile and durable refund-request review state. SDK/model/provider responses are mocked; no external payment call is made.
- Ruff, Python dependency consistency and Compose configuration validation pass. The current backend image builds and passes a non-root fresh-tmpfs migration smoke test. The frontend image build stalled in npm ci for over ten minutes and was stopped; no frontend-image success is claimed. The host production build and isolated browser checks passed.
- npm production dependency audit reports **zero known advisories**; the full developer-tooling tree has **eight moderate advisories**. No forced dependency rewrite or independent audit is claimed.

One fresh-process browser attempt failed with ECONNRESET on the isolated reset endpoint; a complete rerun passed all 102 assertions. The transient connection failure is retained as a validation limitation, not silently treated as a clean first attempt.

The required eligible, approval-required, budget-denied, mandatory-attribute-denied, duplicate-prevented and amount-tampering-blocked scenarios remain covered by the existing suites. Passing tests are evidence of tested boundaries, not proof of semantic correctness, race freedom under every failure or public production readiness.

## What remains outside verified scope

1. User previously reported a completed website Sandbox capture and passing receipt export. That is historical user-reported evidence; it was not independently re-inspected in this batch. There was no new live model, buyer payment, refund or webhook call. Current real SDK/CSP behavior, refund delivery and webhook ordering still need controlled Sandbox acceptance.
2. The user owns the video and timed walkthrough. No measured live three-minute run is claimed.
3. Optional local authentication is not OIDC/MFA, public registration, email recovery or a public identity lifecycle. The user asked why multiple users were introduced; it is not required to demo Ryuk and remains off by default.
4. SQLite is still single-host. PostgreSQL, multi-host HA, power-loss drills, host/Windows ACL assurance, production TLS/edge/load/alerting and a scheduled provider monitor are not installed or certified.
5. Orphaned provider creates and refund dispatches without a known provider reference require operator/provider investigation; no unsafe release or retry is provided.
6. Partial refunds, fees/FX, disputes/chargebacks and net merchant accounting remain unsupported; full adjustments do not automatically replenish the gross-spend budget.
7. LLM semantic completeness cannot be proved by strict JSON or source quotes. Human review remains mandatory. Development dependency advisories and ongoing operational/disk-growth review remain.

## Suggested independent review request

Review this repository and its actual diff, not this summary alone. Score hackathon implementation and production readiness separately. Inspect the money/identity trust boundaries, migration compatibility, reservation/dispatch concurrency, consent binding, webhook verification, refund idempotency and uncertain-outcome recovery. Give concrete exploit sequences and file references for findings. Distinguish mocked coverage, historical user-reported acceptance and independently verified live evidence. Do not assume synthetic inventory is real or that passing tests prove production safety.

## Files in the production-foundation batch


Configuration and status:

- `.env.example`
- `DECISIONS.md`
- `README.md`
- `STATUS.md`
- `TASKS.md`
- `deploy/nginx.conf`
- `docker-compose.yml`

Backend runtime:

- `backend/app/api/agent.py`
- `backend/app/api/checkout.py`
- `backend/app/api/provider_events.py`
- `backend/app/api/workspace.py`
- `backend/app/main.py`
- `backend/app/manage_users.py`
- `backend/app/migrations/001_core.sql`
- `backend/app/migrations/002_identity_and_operations.sql`
- `backend/app/migrations/003_policy_and_refund_review.sql`
- `backend/app/migrations/004_provider_lookup.sql`
- `backend/app/provider_admin.py`
- `backend/app/request_limits.py`
- `backend/app/schemas/checkout.py`
- `backend/app/schemas/provider.py`
- `backend/app/services/checkout_store.py`
- `backend/app/services/durable_approvals.py`
- `backend/app/services/local_auth.py`
- `backend/app/services/migrations.py`
- `backend/app/services/paypal.py`
- `backend/app/services/provider_operations.py`
- `backend/app/services/provisioning.py`
- `backend/app/services/resources.py`
- `backend/app/services/session.py`
- `backend/app/services/workspace.py`

Regression tests:

- `backend/tests/frontend_server.py`
- `backend/tests/test_checkout.py`
- `backend/tests/test_local_auth_http.py`
- `backend/tests/test_production_foundation.py`
- `backend/tests/test_provider_operations.py`
- `frontend/tests/e2e.mjs`

Frontend runtime:

- `frontend/app/api/ryuk/[...path]/route.ts`
- `frontend/app/page.tsx`
- `frontend/components/recovery-history.tsx`
- `frontend/lib/contracts.ts`

Documentation:

- `docs/operations.md`
- `docs/production-foundation.md`
- `docs/project-review-summary.md`
- `docs/security-hardening.md`
- `docs/security-review.md`
- `docs/startup.md`
