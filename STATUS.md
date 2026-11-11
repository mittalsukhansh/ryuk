# AgentPay Status

Last verified: 2026-11-11. Evidence: source inspection, local builds, pytest/lint/type checks, live HTTP requests, Chromium smoke checks, and a healthy Docker Compose deployment. Planning checklists alone are not completion evidence.

## Current milestone
Phase 0 — Scaffold complete and verified. Next recommended stage: Codex Prompt 2 — Domain schemas, awaiting explicit instruction.

## Overall status
In Progress

The foundation runs locally and in Docker Compose. The Next.js preview serves HTTP 200 and FastAPI `/health` returns HTTP 200 with `{"status":"ok"}`. The commerce flow is not implemented and the product is not demo ready. AI and payments were intentionally excluded from this stage.

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

## In Progress
- [ ] No active implementation stage; scaffold work is complete. Domain schemas are recommended next, but have not been started.

## Remaining
### P0
- [ ] Define typed domain schemas and validated structured intent parsing with 15 test prompts.
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
- No unresolved blocker for the completed scaffold or for beginning domain schemas.
- Container validation required the managed proxy CA override documented in README.md. A disk-exhaustion failure was resolved by removing task-created build caches and reducing frontend build layers; both containers then passed health checks.
- Sandbox account/app setup and usable credentials are unverified; empty template fields do not establish readiness. They will be required for live Sandbox acceptance, but need not block scaffolding.

## Risks
- No commerce security or payment invariant has implementation/test evidence yet.
- npm audit reports seven moderate development-tool findings through the TypeScript ESLint/minimatch dependency chain after a compatible update attempt. The production dependency audit reports zero findings. Review tooling updates before broader development.
- pytest passes with one upstream Starlette TestClient/httpx deprecation warning.
- Docker VFS builds consume substantial temporary storage; monitor free disk space during rebuilds.
- Browser tampering, prompt injection, approval replay, duplicate capture, concurrent overspend, and ambiguous provider outcomes remain unmitigated in code.
- ARCHITECTURE.md includes VERIFYING in the payment states; CODEX_PROMPTS.md task 8 omits it. Resolve the state list during the payment-state-machine stage.
- Synthetic hotel data must be clearly labeled; Sandbox checkout must not imply real hotel booking or arbitrary-merchant support.
- Scope expansion into search integrations, other verticals, or multi-agent orchestration could delay the core demo.

## Next 3 actions
1. On instruction, execute only Codex Prompt 2: define typed PurchaseIntent, Offer, CheckResult, VerificationResult, PolicyDecision, PurchaseProposal, ApprovalRequest, and PaymentIntent contracts using integer minor units.
2. Add and run schema-validation tests, including invalid input and monetary boundary cases; rerun affected foundation checks.
3. Update STATUS.md, TASKS.md, and meaningful decisions; report results/blockers, recommend the hotel fixture catalog stage, and stop for instruction.

## Demo readiness
- Intent parsing: Not implemented; no schema, parser, or prompt fixtures.
- Offer search: Not implemented; no catalog or synthetic hotel fixtures.
- Verification: Not implemented; no checks, evidence snapshots, or UI.
- Policy: Not implemented; no deterministic policy service or budget controls.
- Approval: Not implemented; no application approval service or PayPal buyer flow.
- PayPal: Not integrated; Sandbox configuration template only, credentials/account readiness unknown.
- Audit: Not implemented; no persistence or timeline.
- Security tests: Absent; no safety claims validated. Demo is not ready.

## Test status
- Unit: No domain unit suite yet. Backend `pytest -q`: 1 health-contract test passed, with one upstream deprecation warning.
- Integration: In-process HTTP health test passed; live local and Compose `/health` returned HTTP 200 and `{"status":"ok"}`. Both Compose services are healthy; frontend HTTP 200 confirmed.
- E2E: Temporary Playwright/Chromium scaffold smoke checks passed on local development and Compose production frontend at desktop/mobile sizes, with no runtime errors or horizontal overflow. No committed full purchase-flow E2E suite yet.
- Security: Empty credential-template fields, ignored local env files, and repository private-key/common-token-pattern checks passed; no comprehensive security suite yet. npm production audit: zero findings; development audit: seven moderate tooling findings.

Additional checks passed: frontend ESLint, TypeScript check, production build; backend Ruff and `pip check`; Compose configuration validation and image builds; diff whitespace validation. Managed proxy CA override used for container dependency downloads. Services left running through Compose on localhost ports 3000 and 8000.
