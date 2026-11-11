# AgentPay Status

Last verified: 2026-11-11. Evidence: source inspection, local builds, pytest/lint/type checks, live HTTP requests, Chromium smoke checks, and a healthy Docker Compose deployment. Planning checklists alone are not completion evidence.

## Current milestone
Codex Prompt 4 — Deterministic required/preferred verification complete and verified. Scaffold, schemas, and catalog remain complete. Next recommended stage: Codex Prompt 5 — Intent parser, awaiting instruction.

## Overall status
In Progress

The foundation runs locally and in Docker Compose. The Next.js preview serves HTTP 200 and FastAPI `/health` returns HTTP 200 with `{"status":"ok"}`. Eight Pydantic domain contracts and the synthetic hotel catalog/search API are implemented. The catalog contains eight labeled offers with evidence and explicit filtering. The full commerce flow is not implemented and the product is not demo ready. Deterministic attribute verification now returns mandatory PASS/FAIL/UNKNOWN, independent preference scores, and evidence-backed in-memory snapshots. AI parsing, financial policy, approval authorization, payment transitions, and provider integration remain unimplemented.

## Completed
- [x] Git repository initialized and checked out on `main`.
- [x] Planning artifacts exist: PLAN.md, AGENTS.md, ARCHITECTURE.md, TASKS.md, CODEX_PROMPTS.md, and README_START_HERE.md.
- [x] Canonical `.env.example` added with empty credential fields; original `env.example` retained for reference. Local environment files and dependency/build outputs are ignored. Credential-pattern checks passed; no real credentials were introduced.
- [x] Initial decision log and live status tracker created; documentation/stage instructions appended to AGENTS.md.
- [x] Next.js + TypeScript + Tailwind preview, lockfile, ESLint/typecheck commands, and standalone production build.
- [x] FastAPI backend with a Pydantic health response, pinned runtime/dev dependencies, Ruff, and a passing pytest health-contract test.
- [x] Dockerfiles and Compose with non-root runtime users, loopback ports, and health checks; both services built and reached healthy status.
- [x] Frontend startup verified locally and in containers; Chromium smoke checks passed at 1440px and 390px with styling, no horizontal overflow, and no browser runtime errors.
- [x] README.md documents local and Compose startup, checks, configuration boundaries, and optional proxy CA build support.
- [x] Eight domain schemas exported from `app.schemas` with strict integer minor units, explicit enums, evidence/status consistency, proposal references, and approval timing validation.
- [x] Domain-schema stage introduced 190 schema test cases plus the health test; the expanded suite total appears below. Ruff and dependency checks pass. Contract usage and trust boundaries are documented in `docs/domain-schemas.md`; D-021 records schema choices.

- [x] Eight synthetic hotel offers with merchant IDs, price/location/stay/amenity evidence, and deliberate absent/false mandatory attributes for future verification cases.
- [x] Read-only catalog service, canonical ID lookup returning deep copies, and POST /v1/offers/search with explicit filters, pagination, and synthetic response labels.
- [x] Catalog stage added 76 catalog/service/API test cases; the expanded test total appears below. Backend container rebuilt with root-context fixture packaging, reached healthy status, and passed live health/search/validation requests.
- [x] Catalog behavior and limitations documented in `docs/catalog.md` and decision D-022.

- [x] Deterministic required/preferred attribute checks, strict scalar comparisons, evidence-gap handling, mandatory FAIL/UNKNOWN/PASS, and independent equal-weight preference scoring.
- [x] Preferred check details and deterministic content-derived verification snapshots, with source evidence and input/version identity. Snapshots are generated in memory; no database persistence is claimed.
- [x] 56 verifier regression cases added; all 323 backend tests pass, and Ruff passes. Rules, trust boundaries, and snapshot semantics documented in `docs/verification.md` and D-023.

## In Progress
- [ ] No active implementation stage; deterministic verification is complete. Intent parsing is recommended next but has not been started.

## Remaining
### P0
- [ ] Implement structured intent parsing and parser validation with 15 test prompts. Domain contracts are complete; parser behavior remains unimplemented.
- [ ] Persist verification snapshots and display evidence/required/preferred checks in the UI. The deterministic engine and in-memory snapshots are implemented.
- [ ] Implement deterministic budget/currency/merchant/evidence policy, reason codes, duplicate protection, and proposal digests.
- [ ] Implement bound, expiring approvals and revalidation before checkout/capture.
- [ ] Implement persistence, atomic budget reservations, and centralized payment transitions.
- [ ] Configure Sandbox accounts/app; implement server-side OAuth, orders, buyer approval, capture, stable idempotency, provider verification, decline/cancel handling, and ambiguous-timeout reconciliation.
- [ ] Persist audit events and build command, shortlist, verification, approval, checkout, result, and timeline UI.
- [ ] Add relevant unit, integration, and security tests; validate eligible, escalation, denial, amount-tampering, and duplicate scenarios.
- [ ] Add seed/reset command and demo script; verify reproducible startup and a full Sandbox demo.

### P1
- [ ] Semantic evidence matching and human review for insufficient evidence.
- [ ] Prompt-injection, concurrency, and merchant-substitution tests.
- [ ] Requirement matrix UI and “Why this purchase?” summary.

### P2
- [ ] Electronics and subscription verifiers; real external search API.
- [ ] LangGraph checkpointing and specialized subagents after P0/P1.
- [ ] Multi-rail adapter, conceptual UPI Circle/P3P adapter, and team approvals.

## Blockers
- No unresolved blocker for the completed verifier stage. Live intent parsing will need configured LLM credentials/model; deterministic fake-parser tests need no provider credentials.
- Container validation required the managed proxy CA override documented in README.md. A disk-exhaustion failure was resolved by removing task-created build caches and reducing frontend build layers; both containers then passed health checks.
- Sandbox account/app setup and usable credentials are unverified; empty template fields do not establish readiness. They will be required for live Sandbox acceptance, but need not block scaffolding.

## Risks
- Schema-boundary safeguards have test evidence; runtime commerce authorization and payment invariants remain unimplemented.
- npm audit reports seven moderate development-tool findings through the TypeScript ESLint/minimatch dependency chain after a compatible update attempt. The production dependency audit reports zero findings. Review tooling updates before broader development.
- pytest passes with one upstream Starlette TestClient/httpx deprecation warning.
- Docker VFS builds consume substantial temporary storage; monitor free disk space during rebuilds.
- Schemas cannot establish authenticity of supplied statuses, evidence, IDs, or digests. Canonical lookups, current policy/expiry checks, digest generation, prompt-injection defenses, duplicate protection, budget reservations, and provider reconciliation still require services and tests.
- PaymentState includes VERIFYING from ARCHITECTURE.md (D-021), resolving the earlier vocabulary discrepancy. Legal transitions and state-dependent authorization remain deferred to the payment-state-machine stage.
- Synthetic hotel data must be clearly labeled; Sandbox checkout must not imply real hotel booking or arbitrary-merchant support.
- Scope expansion into search integrations, other verticals, or multi-agent orchestration could delay the core demo.

## Next 3 actions
1. On instruction, execute only Codex Prompt 5: implement an LLM-backed intent parser behind an interface with structured output and Pydantic validation.
2. Preserve required/preferred distinctions, reject missing/unlimited budgets, add a deterministic fake parser and the 15 prompt cases, and run relevant tests.
3. Update STATUS.md, TASKS.md, and meaningful decisions, report tests/blockers, recommend the policy engine stage, and stop for instruction.

## Demo readiness
- Intent parsing: PurchaseIntent schema implemented/tested; parser and prompt fixtures absent.
- Offer search: Implemented/tested with eight synthetic hotel fixtures, explicit filters, stable pagination, canonical ID lookup, and API labels. No live search or frontend catalog UI.
- Verification: Deterministic engine implemented/tested with required/preferred checks, evidence, independent preference percentage, and stable in-memory snapshots. Semantic matching, database persistence, and UI are absent. PASS does not imply financial-policy eligibility.
- Policy: PolicyDecision contract and enums exist; deterministic policy service and budget controls absent.
- Approval: Bound ApprovalRequest contract and timestamp validation exist; authorization service and PayPal buyer flow absent.
- PayPal: PaymentIntent contract exists; no provider adapter, transition service, or integration. Sandbox account/credential readiness remains unknown.
- Audit: Not implemented; no persistence or timeline.
- Security tests: Boundary validation cases pass (strict money, unexpected fields, evidence, references, timestamps); runtime authorization/provider tests absent. Demo is not ready.

## Test status
- Unit: Backend `pytest -q`: 323 tests passed (190 domain-contract, 76 catalog/service/API, 56 verifier, and the existing health test), with the existing upstream Starlette/httpx deprecation warning.
- Integration: Verifier runs against committed synthetic fixtures with expected PASS/FAIL/UNKNOWN. Existing in-process search/health/OpenAPI and HTTP 422 cases also pass. Rebuilt backend in Docker Compose and confirmed healthy status, /health HTTP 200, eight labeled offers, the three planned demo-price candidates, combined filters, and currency-required price filtering. Frontend container remains healthy; frontend code unchanged.
- E2E: Temporary Playwright/Chromium scaffold smoke checks passed on local development and Compose production frontend at desktop/mobile sizes, with no runtime errors or horizontal overflow. No committed full purchase-flow E2E suite yet.
- Security: Schema tests reject coerced/negative money, missing budgets, forged extra fields, unsupported enums, mismatched snapshot references, malformed digests, semantic PASS without evidence, and invalid approval windows. Catalog tests additionally reject malformed fixtures, duplicate IDs, non-synthetic labels, coerced filters, and caller paths; returned objects cannot mutate canonical offers. Verifier cases cover missing evidence, mandatory false even with no evidence, coercion/type confusion, injection-like prose, unknown/unsupported predicates, perfect preferences unable to override failure, input mutation, and snapshot changes on altered terms/evidence. No comprehensive runtime security suite yet. Prior scaffold checks verified empty credentials and ignored local env files. npm production audit: zero findings; development audit: seven moderate tooling findings.

Current stage: Ruff and pytest (323 passed) pass. No dependency, frontend, or route changes; verification is a backend service function. Catalog-stage Docker rebuild, health/search requests, Compose configuration, and dependency checks previously passed. This stage does not claim a new deployment, database persistence, or payment behavior.

Prior scaffold checks passed: frontend ESLint, TypeScript check, production build; backend Ruff and `pip check`; Compose configuration validation and image builds; diff whitespace validation. Managed proxy CA override used for container dependency downloads. Services left running through Compose on localhost ports 3000 and 8000.
