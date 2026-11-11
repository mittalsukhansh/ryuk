# AgentPay Task Board

## P0 — Must ship

### Foundation
- [x] Repo initialized
- [x] Next.js frontend
- [x] FastAPI backend
- [x] .env.example
- [x] Docker Compose
- [x] health endpoints
- [x] lint/test commands

### Domain schemas
- [x] PurchaseIntent, Offer, CheckResult, VerificationResult, PolicyDecision, PurchaseProposal, ApprovalRequest, PaymentIntent
- [x] Strict integer minor units, explicit enums, and contract-validation tests

### Intent
- [x] PurchaseIntent schema
- [x] structured parsing
- [x] validation
- [x] 15 test prompts

### Catalog
- [x] hotels.json
- [x] 6+ synthetic offers
- [x] merchant IDs
- [x] evidence fields
- [x] search endpoint

### Verification
- [x] required attribute checks
- [x] preferred scoring
- [x] PASS/FAIL/UNKNOWN
- [x] verification snapshot (generated in memory with evidence and stable ID; persistence deferred)
- [x] evidence shown in UI (backend matrix, sources and snapshot)

### Policy
- [x] max budget rule
- [x] approval threshold
- [x] missing evidence rule
- [x] merchant review
- [x] duplicate/unknown-attempt policy checks against explicit backend history snapshots
- [x] read-only approval binding/expiry/rejection policy checks
- [x] duplicate protection (SQLite checkout uniqueness and atomic capture claim)
- [x] proposal digest

### Approval
- [x] request creation (internal in-memory service)
- [x] proposal binding (internal in-memory service)
- [x] expiry (internal in-memory service)
- [x] approve/reject service operations with one-time decisions
- [x] authenticated approve/reject endpoint (opt-in single-buyer demo session)
- [x] revalidation before checkout (backend gate; payment wiring deferred)
- [ ] durable approval storage and authenticated user integration

### Payment state machine
- [x] Exact nine-state vocabulary and centralized immutable event/transition graph
- [x] Illegal transitions, same-state moves, and terminal exits rejected
- [x] Approval returns to policy; pending-provider recovery requires reconciliation events
- [x] State-only updates preserve binding, identity, and idempotency; exhaustive tests
- [x] Durable conditional checkout state updates, coordinator integration, and checkout audit (SQLite reference)

### PayPal
- [ ] Sandbox accounts/app
- [x] server-side OAuth (Sandbox-only adapter; mocked HTTP)
- [x] create order (internal adapter; mocked HTTP)
- [ ] buyer approval
- [x] capture (internal adapter with provider approval preflight; mocked HTTP)
- [x] stable operation-specific PayPal-Request-Id (adapter; mocked HTTP)
- [x] durable operation-key/terms storage and atomic execution claim (SQLite)
- [x] get status and exact order/capture binding/state mapping (mocked HTTP)
- [ ] live Sandbox final-state acceptance
- [x] verified capture decline and local pre-dispatch cancel handling (mocked HTTP)
- [x] buyer UI cancel/decline/pending presentation (browser/provider mocks)
- [x] ambiguous timeout classification, no automatic capture retry, status reconciliation (adapter tests)
- [x] durable pending-provider GET-only recovery and held-budget accounting
- [ ] unknown-create/operator recovery procedure

### Checkout integration
- [x] Canonical proposal -> server-owned PayPal order -> provider-verified buyer approval -> capture (mocked HTTP)
- [x] Final reload/digest/current policy/approval/merchant mapping checks after provider preflight
- [x] Atomic reserve/dispatch claim, success settlement, verified-failure release, uncertain-hold retention
- [x] Identifier-only create/read/capture/reconcile/cancel HTTP contracts with forbidden authority fields
- [x] Default routes fail closed until trusted authentication/service provisioning
- [x] Duplicate/concurrent budget, expiry/tampering, transaction rollback and restart tests
- [x] Opt-in private demo password session and trusted runtime service provisioning
- [ ] Production multi-user identity and durable canonical authority
- [x] Buyer UI / actual PayPal JS v5 integration implemented and browser-mock tested
- [ ] Live Sandbox checkout acceptance

### Frontend — Stage 11
- [x] Sanitized setting-specific demo startup diagnostics and 21 configuration regression cases
- [x] Visible Ryuk branding and restrained dark editorial casebook design
- [x] Command input, backend intent, candidate records and evidence/preference detail
- [x] Backend policy verdict and exact-term approval/reject modal
- [x] Actual PayPal JS SDK/server order/capture integration; success only from backend
- [x] Backend result/reference/snapshot/available budget and audit timeline
- [x] Same-origin proxy, authenticated private session and explicit unavailable states
- [x] Production build, desktop/mobile browser integration and no secret-marker bundles
- [ ] Real configured model + real Sandbox buyer/capture acceptance (credentials absent here)
- [ ] Live happy path timed under three minutes
- [ ] Stage 11 acceptance complete; do not infer completion from mocked tests
- [ ] Stage 12 security review (not started)

### Audit
- [x] checkout execution/reservation/provider-observation events persisted in SQLite
- [x] checkout_audit table (checkout-only; broader domain audit remains pending)
- [ ] verification events
- [ ] policy events
- [ ] approval events
- [ ] provider events
- [x] timeline UI (backend canonical and checkout events; early records process-local)

### Demo
- [ ] ALLOW scenario
- [ ] REQUIRE_APPROVAL scenario
- [ ] DENY scenario
- [ ] amount tampering blocked
- [ ] duplicate payment blocked
- [ ] seed/reset command
- [ ] demo script

## P1 — Strong differentiators
- [ ] semantic evidence matcher
- [ ] prompt-injection test
- [x] checkout duplicate/overspend concurrency tests (broader security review remains pending)
- [x] checkout merchant/provider mapping substitution tests (mocked HTTP)
- [ ] "Why this purchase?" summary
- [x] requirement matrix UI
- [ ] human review when evidence is insufficient

## P2 — Only if P0/P1 complete
- [ ] electronics verifier
- [ ] subscription verifier
- [ ] real external search API
- [ ] LangGraph checkpointing
- [ ] specialized subagents
- [ ] multi-rail adapter
- [ ] UPI Circle/P3P conceptual adapter
- [ ] team approvals

## Verified security / non-live readiness — 2026-11-11
- [x] Review latest origin/main implementation and preserve older local work separately
- [x] Authenticate model endpoint and enforce bounded model requests
- [x] Digest-bound mandatory review of original versus parsed intent for model purchases
- [x] Prevent validation/clarification credential reflection and unsafe HTTPS cookies
- [x] Streaming proxy body limits, bounded auth allocations and frame/security headers
- [x] Isolate test reset fixture to explicit fresh temporary ledgers
- [x] Retain backend-only Groq parsing with shared strict validation and mocked tests
- [x] Consistent private backup command and fresh-fixture recovery rehearsal
- [x] Update security report, operations runbook, demo script and D-033
- [x] 1,034 backend tests, frontend lint/type/build, 23 mocked browser assertions
- [x] Build both Docker images and verify isolated credential-disabled Compose health
- [ ] Real buyer-approved Sandbox acceptance and timed live demo freeze
- [ ] Production durable canonical authority/multi-user auth and operator orphan recovery
- [ ] Development dependency advisory resolution and full SDK-compatible script CSP

This current evidence supersedes earlier unchecked Step 12 instructions/counts. Step 13 preparation is done; live acceptance remains unverified. See STATUS.md for the authoritative current state.
