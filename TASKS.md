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
- [ ] evidence shown in UI

### Policy
- [x] max budget rule
- [x] approval threshold
- [x] missing evidence rule
- [x] merchant review
- [x] duplicate/unknown-attempt policy checks against explicit backend history snapshots
- [x] read-only approval binding/expiry/rejection policy checks
- [ ] duplicate protection (persistent/atomic enforcement)
- [x] proposal digest

### Approval
- [x] request creation (internal in-memory service)
- [x] proposal binding (internal in-memory service)
- [x] expiry (internal in-memory service)
- [x] approve/reject service operations with one-time decisions
- [ ] authenticated approve/reject endpoint
- [x] revalidation before checkout (backend gate; payment wiring deferred)
- [ ] durable approval storage and authenticated user integration

### Payment state machine
- [x] Exact nine-state vocabulary and centralized immutable event/transition graph
- [x] Illegal transitions, same-state moves, and terminal exits rejected
- [x] Approval returns to policy; pending-provider recovery requires reconciliation events
- [x] State-only updates preserve binding, identity, and idempotency; exhaustive tests
- [ ] Durable conditional state updates, coordinator integration, and audit persistence

### PayPal
- [ ] Sandbox accounts/app
- [x] server-side OAuth (Sandbox-only adapter; mocked HTTP)
- [x] create order (internal adapter; mocked HTTP)
- [ ] buyer approval
- [x] capture (internal adapter with provider approval preflight; mocked HTTP)
- [x] stable operation-specific PayPal-Request-Id (adapter; mocked HTTP)
- [ ] durable operation-key/terms storage and atomic execution lock
- [x] get status and exact order/capture binding/state mapping (mocked HTTP)
- [ ] live Sandbox final-state acceptance
- [ ] decline/cancel handling
- [x] ambiguous timeout classification, no automatic capture retry, status reconciliation (adapter tests)
- [ ] durable pending-provider recovery and unknown-create recovery procedure

### Audit
- [ ] audit table
- [ ] verification events
- [ ] policy events
- [ ] approval events
- [ ] provider events
- [ ] timeline UI

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
- [ ] concurrency test
- [ ] merchant substitution test
- [ ] "Why this purchase?" summary
- [ ] requirement matrix UI
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
