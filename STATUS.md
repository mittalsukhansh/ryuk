# Ryuk Status

Last verified: 2026-11-11. Completion follows implementation and actual checks, not planning checkboxes.

## Current milestone
Step 11 — Frontend integration implemented and mock-tested; **live acceptance remains blocked**. The user's required real parser/Sandbox buyer transaction and live three-minute timing are unverified. Step 11 is not marked complete. Step 12 has not started.

## Overall status
In Progress

Ryuk now has a responsive dark casebook connected to backend intent, catalog, verification, policy, approval, checkout and audit. Private session/runtime integration is opt-in; financial authority stays in the existing deterministic backend services. Actual PayPal JS v5 create/approve/server-capture wiring is implemented. The whole stack passes mocked browser/provider integration, but it is not a verified live Sandbox demo.

## Completed
- [x] Next.js/TypeScript/Tailwind and FastAPI/Compose foundation, strict integer-money domain contracts, eight labeled synthetic hotel offers and trusted search.
- [x] Deterministic evidence-backed required/preferred verification and snapshots, structured OpenAI parser interface/fake/15 test prompts and pure financial policy.
- [x] Canonical digest and process-local approval ownership/expiry/permanent invalidation/replay checks; exact nine-state payment graph.
- [x] Backend Sandbox OAuth/create/status/capture adapter, immutable provider binding, stable request IDs and safe ambiguous outcomes.
- [x] Durable SQLite checkout/payment/key/terms/state/ledger/hold/checkout-audit records; atomic final policy/approval/digest/merchant/reservation claim, exactly-once settlement/release and GET-only uncertainty recovery.
- [x] Visible Ryuk branding, original monochrome casebook with restrained red, serif/monospace typography, subtle grain, three-record primary shortlist and optional expansion. No franchise artwork or generic AI gradients/glassmorphism.
- [x] Working command entry and backend-parsed intent display, backend candidate/verdict/evidence/preference matrix, exact-term approve/reject dialog, snapshot and backend timeline.
- [x] Real SDK integration code: server-owned order ID -> PayPal buyer authorization -> backend capture. Result waits for backend SUCCEEDED; callback alone never displays paid. Pending state offers reconciliation, not a capture retry.
- [x] Thin workspace/proposal/approval/audit APIs reuse existing services; query/identifier/decision bodies reject browser authority fields.
- [x] Explicitly enabled single-buyer demo password verification, opaque hashed session tokens, HttpOnly/SameSite cookie, origin checks, rate limit/logout; default missing configuration stays blocked.
- [x] Same-origin Next proxy with allowlisted paths, credential isolation, no cache/redirect forwarding and safe errors. Only PayPal's public client ID reaches the SDK.
- [x] Trusted runtime account/policy/payee provisioning and protected persistent Compose ledger volume. Startup preserves existing funds/holds and never resets spending.
- [x] 16 new backend session/workspace integration cases; complete suite **962 passed**, no pytest warnings. Ruff/dependency checks pass.
- [x] Frontend ESLint, TypeScript and optimized production build pass. Chromium production-browser suite passes **13 assertions** over the actual proxy/backend/services/SQLite with mocked SDK/provider at desktop/mobile sizes, no page errors or horizontal overflow. All mocked scenarios took **14.6 seconds**, not a live payment measurement.
- [x] Browser bundles checked for backend credential names/synthetic-secret markers; Compose config validates and sends private settings only to backend. No real credentials committed or live calls made.

## In Progress
- [ ] Step 11 acceptance: configure actual private model/Sandbox credentials, authenticate a real Sandbox buyer, verify capture/ledger/audit and time the live happy path. UI/integration code is complete for review; acceptance is not.

## Remaining
### P0
- [ ] Make actual provider configuration available to the runtime and run the real structured parser/Sandbox checkout through the UI. No production fake fallback exists.
- [ ] Verify live SDK popup, separate buyer authorization, backend provider-confirmed capture/reference, ledger settlement and audit under three minutes.
- [ ] Complete Step 11 acceptance before calling the demo ready or advancing stages.
- [ ] On instruction, perform Step 12 comprehensive security review; current targeted tests are not that review.
- [ ] Durable canonical proposal/approval/evidence and early audit storage; these remain process-local. Production multi-user identity and multi-worker authority deployment remain unimplemented.
- [ ] Operator recovery for unknown/orphaned creates and permanently inconclusive captures; preserve uncertain holds.
- [ ] Validate the proposed demo script on a live Sandbox run. Checkout/audit browser flow is mock-tested, not live accepted.

### P1
- [ ] Semantic evidence matching and human review, broader prompt-injection/concurrency/runtime security assessment.
- [ ] Production PostgreSQL-backed authority/ledger deployment and migration; SQLite remains a single-host reference.
- [ ] Extend visual/accessibility/browser/device coverage after live acceptance; desktop and phone are verified, not all device/provider combinations.

### P2
- [ ] Other purchase verticals, real external search, multi-rail/team approvals and conceptual UPI/P3P.
- [ ] LangGraph/specialized agents only after the core demo works.

## Blockers
- Real model/Sandbox acceptance: the shared checkout has no root/backend `.env` and no configured provider process settings. The user's local `.env` is not automatically available here. Keep it private; use local Compose with it or private cloud environment settings, not chat/Git upload.
- Required settings include actual OpenAI key/model, Sandbox client ID/secret and supported seller merchant ID; buyer interaction must use a separate Sandbox buyer. This task made no live provider calls.
- A private demo also needs opt-in password/origin/cookie configuration. Production multi-user authentication and durable canonical authority are still separate limitations.

## Risks
- Demo auth and canonical approvals/early audit are process-local/single-buyer. Restart invalidates sessions/consent and blocks new capture; durable attempted captures still reconcile using original terms.
- SQLite must use a protected persistent local directory/volume, not ephemeral storage or NFS. Pending holds cannot be released just because time passed or the browser closed.
- Candidate verdicts are backend snapshots; selection and capture recheck current rules/budget. One USD 1,500 ledger cannot fund both USD 1,180 and USD 1,390 successful demo purchases.
- Local cancellation does not void a PayPal order; refunds/external merchant actions and long-lived provider uncertainty need operator support.
- Hotel data is synthetic and checkout targets a configured demo payee, not a real hotel booking. Preference percentages cannot override mandatory checks or financial rules.
- Live model fidelity, SDK/account behavior and buyer timing are not established by mocks.
- Earlier dependency audit found seven moderate frontend development-tool findings, zero production findings. Docker VFS builds previously hit storage limits. Current images were not rebuilt in this stage.

## Next 3 actions
1. Keep the user's `.env` private and configure the new opt-in demo settings using docs/frontend.md. Run locally with that file, or provision the shared runtime through private settings.
2. Perform the actual model/Sandbox buyer/capture/ledger/audit run and time the live demo; resolve any integration issues and close Step 11 only when acceptance passes.
3. Then, on instruction, perform Step 12 security review. Do not automatically start it.

## Demo readiness
- Intent parsing: UI and protected backend parser orchestration implemented; fake/SDK tests pass. Live model response/fidelity unverified.
- Offer search: Backend candidates appear in the shortlist; six USD records from eight labeled fixtures, top three initially visible. No live hotel availability or booking.
- Verification: Real backend evidence/status/preference counts and snapshot displayed in matrix; no invented evidence/PASS.
- Policy: Backend deterministic verdict/reasons displayed. UI does not calculate eligibility. Current rules rerun before capture with an atomic hold.
- Approval: Exact bound terms/expiry/reasons and approve/reject UI use authenticated backend service. Process-local authority remains a deployment limitation.
- PayPal: Actual SDK integration and server-order/capture/status code complete; mock browser flow passes. **Real Sandbox buyer/capture acceptance remains unverified and Step 11 remains incomplete.**
- Audit: UI uses backend canonical/approval events and durable checkout events/timestamps. Early events remain in memory; broader durable audit deployment is pending.
- Security tests: Existing 946 cases plus 16 session/workspace cases and 13 browser assertions pass. Comprehensive Step 12 review has not been performed. Live demo is not ready to certify.

## Test status
- Unit: Backend `pytest -q`: **962 passed**, no pytest warnings; Ruff passes; `pip check` reports no broken requirements.
- Integration: Existing real-adapter/SQLite checkout tests plus authenticated session/proxy/workspace paths, exact backend evidence/verdicts, consent, forbidden fields, origin/owner checks, cancellation, duplicate/overspend and pending recovery. Compose config/private-variable separation and browser-bundle secret-marker checks pass.
- E2E: Production Next -> same-origin proxy -> actual FastAPI/services/SQLite -> mocked SDK/HTTP provider: 13 Chromium assertions pass at 1440px/390px, no page errors or horizontal overflow, 14.6-second suite. Blocked/rejected purchases have no checkout; no paid label before backend response; timeout reconciles. This is not a real Sandbox E2E acceptance.
- Security: Session forgery/guess limit/logout/expiry/origin tests, browser authority rejection and existing financial tampering/race/recovery tests pass. No comprehensive production security acceptance claimed.

No core policy/approval/payment-state/financial execution rules changed. Provider credentials remain backend-only. Container configuration/volume wiring is updated, but images were not rebuilt; prior running Compose containers still show their previous build. Backend and local production frontend were booted for this stage's browser tests. Test-only model/provider hooks are outside production startup and image inputs.
