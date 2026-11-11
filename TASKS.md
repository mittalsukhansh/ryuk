# AgentPay Task Board

## P0 — Must ship

### Foundation
- [ ] Repo initialized
- [ ] Next.js frontend
- [ ] FastAPI backend
- [ ] .env.example
- [ ] Docker Compose
- [ ] health endpoints
- [ ] lint/test commands

### Intent
- [ ] PurchaseIntent schema
- [ ] structured parsing
- [ ] validation
- [ ] 15 test prompts

### Catalog
- [ ] hotels.json
- [ ] 6+ synthetic offers
- [ ] merchant IDs
- [ ] evidence fields
- [ ] search endpoint

### Verification
- [ ] required attribute checks
- [ ] preferred scoring
- [ ] PASS/FAIL/UNKNOWN
- [ ] verification snapshot
- [ ] evidence shown in UI

### Policy
- [ ] max budget rule
- [ ] approval threshold
- [ ] missing evidence rule
- [ ] merchant review
- [ ] duplicate protection
- [ ] proposal digest

### Approval
- [ ] request creation
- [ ] proposal binding
- [ ] expiry
- [ ] approve/reject endpoint
- [ ] revalidation before checkout

### PayPal
- [ ] Sandbox accounts/app
- [ ] server-side OAuth
- [ ] create order
- [ ] buyer approval
- [ ] capture
- [ ] idempotency
- [ ] final-state verification
- [ ] decline/cancel handling
- [ ] ambiguous timeout handling

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
