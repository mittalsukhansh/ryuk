# AgentPay Status

Last verified: 2026-11-11. Evidence: source inspection, local builds, pytest/lint/type checks, live HTTP requests, Chromium smoke checks, and a healthy Docker Compose deployment. Planning checklists alone are not completion evidence.

## Current milestone
Codex Prompt 2 — Domain schemas complete and verified. Phase 0 scaffold remains complete. Next recommended stage: Codex Prompt 3 — Hotel fixture catalog, awaiting instruction.

## Overall status
In Progress

The foundation runs locally and in Docker Compose. The Next.js preview serves HTTP 200 and FastAPI `/health` returns HTTP 200 with `{"status":"ok"}`. All eight Pydantic domain contracts and schema-validation tests now exist. The commerce flow is not implemented and the product is not demo ready. No catalog, AI, financial policy evaluation, approval authorization, payment transitions, or provider integration was added in this stage.

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
- [x] 190 schema test cases plus the existing health test pass (191 total); Ruff and dependency checks pass. Contract usage and trust boundaries are documented in `docs/domain-schemas.md`; D-021 records schema choices.

## In Progress
- [ ] No active implementation stage; domain schema work is complete. Hotel fixture catalog is recommended next but has not been started.

## Remaining
### P0
- [ ] Implement structured intent parsing and parser validation with 15 test prompts. Domain contracts are complete; parser behavior remains unimplemented.
- [ ] Add at least six labeled synthetic hotel offers with merchant IDs, attributes, evidence, and a catalog/search endpoint.
- [ ] Implement required/preferred verification, PASS/FAIL/UNKNOWN, snapshots, and evidence display.
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
- No unresolved blocker for the completed schema stage or for beginning the fixture catalog.
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
1. On instruction, execute only Codex Prompt 3: add at least six clearly labeled synthetic hotel offers with merchant IDs, structured attributes, evidence, and sources, validated against Offer.
2. Implement the catalog/search service and tests for fixture validity and filtering; do not begin verification or intent parsing automatically.
3. Update STATUS.md, TASKS.md, and meaningful decisions, report tests/blockers, recommend the deterministic verification stage, and stop for instruction.

## Demo readiness
- Intent parsing: PurchaseIntent schema implemented/tested; parser and prompt fixtures absent.
- Offer search: Not implemented; no catalog or synthetic hotel fixtures.
- Verification: CheckResult/VerificationResult contracts and consistency tests exist; verification engine, snapshot persistence, and UI absent.
- Policy: PolicyDecision contract and enums exist; deterministic policy service and budget controls absent.
- Approval: Bound ApprovalRequest contract and timestamp validation exist; authorization service and PayPal buyer flow absent.
- PayPal: PaymentIntent contract exists; no provider adapter, transition service, or integration. Sandbox account/credential readiness remains unknown.
- Audit: Not implemented; no persistence or timeline.
- Security tests: Boundary validation cases pass (strict money, unexpected fields, evidence, references, timestamps); runtime authorization/provider tests absent. Demo is not ready.

## Test status
- Unit: Backend `pytest -q`: 191 tests passed (190 domain-contract cases and 1 existing health-contract test), with the existing upstream Starlette/httpx deprecation warning.
- Integration: In-process HTTP health test passes in this stage. Live local/Compose HTTP checks and healthy containers were verified during the scaffold stage; no integration routes or dependencies changed here.
- E2E: Temporary Playwright/Chromium scaffold smoke checks passed on local development and Compose production frontend at desktop/mobile sizes, with no runtime errors or horizontal overflow. No committed full purchase-flow E2E suite yet.
- Security: Schema tests reject coerced/negative money, missing budgets, forged extra fields, unsupported enums, mismatched snapshot references, malformed digests, semantic PASS without evidence, and invalid approval windows. No comprehensive runtime security suite yet. Prior scaffold checks verified empty credentials and ignored local env files. npm production audit: zero findings; development audit: seven moderate tooling findings.

Current stage: Ruff, pytest (191 passed), and `pip check` pass. No dependencies or frontend/runtime routes changed.

Prior scaffold checks passed: frontend ESLint, TypeScript check, production build; backend Ruff and `pip check`; Compose configuration validation and image builds; diff whitespace validation. Managed proxy CA override used for container dependency downloads. Services left running through Compose on localhost ports 3000 and 8000.
