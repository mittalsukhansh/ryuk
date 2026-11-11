# AgentPay Status

Last verified: 2026-11-11. Completion evidence is implementation and passing checks, not planning checklists.

## Current milestone
Codex Prompt 10 — Checkout integration implemented and tested with mocked provider HTTP. Next recommended stage: Prompt 11 — Frontend. It has not been started.

## Overall status
In Progress

Backend checkout connects canonical proposals/current approvals and policy to PayPal order creation, provider-verified buyer approval and capture. A SQLite ledger persists exact terms, stable operation keys, unique dispatch claims, budget holds/settlement and checkout audit. The public routes fail closed until real authentication and trusted service provisioning. The frontend remains a scaffold preview; the complete product is not demo ready. No live model or PayPal acceptance is claimed.

## Completed
- [x] Next.js/TypeScript/Tailwind scaffold, FastAPI health/catalog/parse APIs, Dockerfiles/Compose and empty backend credential templates. Earlier scaffold builds, boots and desktop/mobile smoke checks passed; frontend is unchanged in this stage.
- [x] Eight validated domain contracts with strict integer minor units, explicit enums and security boundary checks.
- [x] Eight labeled synthetic hotel fixtures, evidence, trusted catalog lookup and explicit search/filter API.
- [x] Deterministic mandatory/preferred verification, PASS/FAIL/UNKNOWN, independent preference score and content-derived evidence snapshots.
- [x] Parser interface, structured OpenAI extraction with Pydantic/source checks, deterministic fake, and 15 gold prompt fixtures tested through mocked SDK HTTP.
- [x] Pure deterministic financial policy, reason codes, current-verification checks, caps/currency/quantity/merchant rules and approval/history gates. The LLM has no financial authority.
- [x] Canonical SHA-256 proposal binding and in-memory approval creation/approve/reject/expiry/permanent invalidation/current-request ownership. Canonical authority is not durable.
- [x] Exact nine-state immutable event graph with illegal/terminal transition rejection and reconciliation-only capture uncertainty.
- [x] Backend-only Sandbox OAuth/create/status/capture adapter, stable operation-specific provider request IDs, strict USD/EUR conversion, exact binding/provider-state checks and safe errors.
- [x] CheckoutService reloads canonical authority and current policy/budget, regenerates digest and checks approval before creating a server-owned order. One durable checkout/key per proposal prevents repeat order creation.
- [x] Final capture gate runs after provider buyer-approval/binding preflight and OAuth. It reloads proposal/current approval/policy, verifies original digest and mapped payee, and atomically reserves funds, claims capture and writes state/audit before POST.
- [x] SQLite local-file ledger with WAL/FULL synchronous transactions, persistent account/policy/mapping/payment/key/terms records, unique claims and exactly-once hold settlement/release. No lock spans provider I/O.
- [x] Ambiguous capture/cancellation retains holds; restart and repeated capture actions use GET-only reconciliation. Open orders and GET errors do not release holds or trigger capture retries. Unknown create stops without automatic retry.
- [x] Identifier-only create/read/capture/reconcile/cancel HTTP contracts reject browser amount/merchant/user/approval/status/order fields. Default authentication/service dependencies return 503; ownership checks and safe HTTP errors are implemented.
- [x] Checkout audit records revalidation, proposal/snapshot/policy/approval references, operation IDs, reservation/dispatch, provider observations and settlement/release. Full cross-domain audit/timeline is incomplete.
- [x] 49 new checkout service/HTTP/recovery/concurrency cases; full backend suite: 946 passed, no pytest warnings. Ruff and dependency checks pass. Documentation: docs/checkout.md and D-029.

## In Progress
- [ ] No active implementation stage after Prompt 10. Prompt 11 frontend, real authentication/provisioning, durable canonical authority and live Sandbox acceptance remain pending.

## Remaining
### P0
- [ ] Implement the command/shortlist/verification/policy/approval/PayPal buyer/result/timeline frontend; current UI is a static scaffold.
- [ ] Install a real server-side session/token verifier and trusted runtime checkout service/merchant/account/policy provisioning before exposing payment actions. Unsigned identity headers are rejected.
- [ ] Replace in-memory canonical proposal/approval authority with durable authenticated storage; persist verification snapshots. SQLite checkout execution is durable, canonical authority is not.
- [ ] Configure supported Sandbox buyer/merchant/app credentials and verify a live buyer-authorized transaction. Backend mocked HTTP does not establish account readiness or live acceptance.
- [ ] Define operator recovery for unknown/orphaned order creation and permanently inconclusive captures. No automatic retry or timed release of uncertain holds exists.
- [ ] Add broader domain verification/policy/approval/provider audit persistence and UI timeline; checkout-specific audit exists.
- [ ] Configure/evaluate live structured parsing against the 15 prompts. No paid/live model call has been made.
- [ ] Add full purchase browser E2E and comprehensive security review; validate visible ALLOW/REQUIRE_APPROVAL/DENY/tampering/duplicate demo scenarios.
- [ ] Add seed/reset and demo script; verify reproducible full Sandbox demo with persistent storage and actual auth. Rebuild deployed images when runtime provisioning is ready.

### P1
- [ ] Semantic evidence matching/human review, prompt-injection/runtime authorization review, requirement matrix and purchase explanation.
- [ ] Extend targeted checkout concurrency/merchant substitution tests into a comprehensive security suite.
- [ ] Production PostgreSQL-backed authority/ledger deployment; SQLite currently provides a single-host execution reference.

### P2
- [ ] Electronics/subscriptions, live external search, multi-rail/team approvals and conceptual UPI/P3P support.
- [ ] LangGraph/specialized agents only after the core demo works.

## Blockers
- No unresolved blocker for the requested mocked backend checkout integration.
- Public checkout intentionally returns 503 until trusted authentication and runtime service provisioning. There is no production session/token verifier or durable canonical approval source.
- Live Sandbox acceptance needs configured supported app/merchant/buyer accounts. Credential/account readiness remains unverified; no live provider call was made.
- Live semantic parsing needs valid backend model credentials/configuration and evaluation.

## Risks
- Canonical approvals/proposals are in memory. Restart blocks new capture rather than reconstructing consent from client data; persisted attempted captures can still reconcile. This is not a durable multi-worker authority deployment.
- SQLite must use a protected persistent local file/directory, not an ephemeral container layer or network filesystem. Cross-connection execution claims are serialized, but production PostgreSQL and migration/deployment work remain pending.
- Authorization commits before remote dispatch; later revocation cannot undo an already committed request. Uncertain holds may require operator review and remain reserved indefinitely.
- Local cancellation does not void an order at PayPal. Refunds and external merchant actions after a local terminal result need additional monitoring/operator support.
- Synthetic hotel merchants are not actual hotel integrations. Supported demo-payee mappings must be backend controlled and clearly presented with synthetic data and buyer consent.
- Mock provider/model responses do not establish live account readiness or semantic fidelity.
- Earlier frontend audit reported seven moderate development-tool findings and zero production findings; no dependency/frontend changes were made in this stage. Docker VFS rebuilds previously required cache cleanup due storage limits.

## Next 3 actions
1. On instruction, execute only Prompt 11 frontend: connect the request/offer/verification/approval/result surfaces and server-issued PayPal order IDs. Do not bypass missing authentication with browser identities or production fake consent.
2. Provision real authentication, durable canonical authority and a protected persistent checkout ledger/runtime merchant mapping before a public checkout demo.
3. Configure Sandbox accounts, validate the full buyer flow, then perform the requested security/demo stages. Keep unknown-provider recovery explicit and update this tracker after each stage.

## Demo readiness
- Intent parsing: Interface/OpenAI structured adapter/fake/API/15 prompts implemented and mock tested; live semantic evaluation unverified.
- Offer search: Eight labeled synthetic offers and filtering API implemented; interactive shortlist UI pending.
- Verification: Deterministic evidence-based required/preferred checks and stable snapshots implemented; durable snapshot storage/UI pending.
- Policy: Deterministic financial service integrated at checkout creation and final pre-capture claim using current persisted policy/ledger availability.
- Approval: In-memory canonical consent/binding/expiry/invalidation rechecked at capture; real authenticated endpoints/UI and durable canonical storage pending.
- PayPal: Adapter and backend checkout/API flow implemented with mocked HTTP. Persistent holds, duplicate prevention and GET-only recovery tested. Routes fail closed until auth/service provisioning; buyer UI and live Sandbox acceptance pending.
- Audit: Durable checkout-specific state/reservation/provider/accounting events implemented; broader domain audit and timeline UI pending.
- Security tests: Targeted tampering/ownership/digest/expiry/concurrency/restart/uncertainty/API-field cases pass. Full security review and purchase browser E2E pending. Demo is not ready.

## Test status
- Unit: Full backend `pytest -q`: 946 passed, no pytest warnings (897 previous cases plus 49 checkout cases). Ruff passes; `pip check` reports no broken requirements.
- Integration: Actual PayPal HTTP adapter with MockTransport connects existing catalog/verifier/policy/approval to SQLite and HTTP routes. Tests cover eligible/review consent, create/capture, concurrent duplicates and competing funds, source changes during provider GET, exact expiry/supersession, safe cancellation, terminal accounting, rollback, and restart/reconciliation. A failed settlement write after provider success rolls back local settlement and recovers by GET without recapture. No live calls.
- E2E: In-process backend HTTP checkout flow passes with test-only authenticated dependency overrides. Earlier frontend scaffold browser smoke checks passed; complete buyer purchase browser E2E is not implemented.
- Security: Browser financial/identity/approval/status/order fields rejected, unsigned identity headers never authenticate, owner isolation enforced, original digest/terms/payee rechecked, stale/expired consent blocks, uncertainty retains holds and never authorizes a new capture. No comprehensive production runtime security acceptance yet.

Current stage changes no dependencies or frontend code. FastAPI startup/health and guarded routes are checked through TestClient. Container images were not rebuilt for this stage and previous running containers do not contain these new checkout routes until rebuilt. Local payment databases/sidecars are ignored; no real credentials or provider calls were introduced.
