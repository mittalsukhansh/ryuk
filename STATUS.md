# AgentPay Status

Last verified: 2026-11-11. Evidence: source inspection, local builds, pytest/lint/type checks, live HTTP requests, Chromium smoke checks, and a healthy Docker Compose deployment. Planning checklists alone are not completion evidence.

## Current milestone
Codex Prompt 5 — Intent parser implemented and mock-integrated; deterministic tests pass. Scaffold, schemas, catalog, and verifier remain complete. Live model calls/semantic accuracy remain unverified. Next recommended stage: Codex Prompt 6 — Financial policy engine, awaiting instruction.

## Overall status
In Progress

The foundation runs locally and in Docker Compose. The Next.js preview serves HTTP 200 and FastAPI `/health` returns HTTP 200 with `{"status":"ok"}`. Eight Pydantic domain contracts and the synthetic hotel catalog/search API are implemented. The catalog contains eight labeled offers with evidence and explicit filtering. The full commerce flow is not implemented and the product is not demo ready. Deterministic attribute verification now returns mandatory PASS/FAIL/UNKNOWN, independent preference scores, and evidence-backed in-memory snapshots. LLM-backed parsing and a deterministic fake now implement one interface with structured extraction, source checks, Pydantic validation, exact minor-unit conversion, and the /v1/agent/parse endpoint. Financial policy, approval authorization, payment transitions, and PayPal integration remain unimplemented; live LLM evaluation has not been performed.

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
- [x] Verifier stage added 56 regression cases; the expanded suite total appears below, and Ruff passes. Rules, trust boundaries, and snapshot semantics documented in `docs/verification.md` and D-023.

- [x] Async parser interface, OpenAI strict structured-output adapter, closed extraction schema, required/preferred quote checks, exact quoted-money conversion, and deterministic fake using the same validation path.
- [x] POST /v1/agent/parse with lazy backend-only provider configuration, safe error responses, and no fake production fallback. The existing TestClient warning is resolved by the SDK httpx2 dependency.
- [x] 15 labeled synthetic gold prompts tested through both implementations; 83 parser/SDK/API regression cases added. All 406 backend tests pass with no warnings, Ruff passes, and pinned dependencies pass `pip check`.
- [x] Parser configuration, limits, trust boundaries, and mock-only evidence documented in `docs/intent-parser.md` and D-024.
- [x] Rebuilt the backend image with pinned SDK dependencies; both containers are healthy. Live Docker checks confirm health/catalog HTTP 200, parse route in OpenAPI, and safe parser HTTP 503 with the currently absent API key/model. No paid model call was made.

## In Progress
- [ ] No active implementation stage; parser implementation is complete. Live model evaluation is pending provider setup and is not represented by mock/gold-response tests. Financial policy is recommended next and has not been started.

## Remaining
### P0
- [ ] Configure a valid structured-output-capable OPENAI_MODEL and backend API credentials, then evaluate live parsing/semantic fidelity on the prompt cases. The interface, provider adapter, validation, fake, endpoint, and deterministic tests are implemented.
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
- No unresolved blocker for the completed parser implementation or next policy stage. Live model acceptance remains unverified and requires valid backend OPENAI_API_KEY/OPENAI_MODEL configuration; no paid/live provider call was made.
- Container validation required the managed proxy CA override documented in README.md. Parser rebuilds hit the environment disk limit; unused task build caches/images were cleared and the backend build order reduced temporary VFS layer duplication. A disk-exhaustion failure was resolved by removing task-created build caches and reducing frontend build layers; both containers then passed health checks.
- Sandbox account/app setup and usable credentials are unverified; empty template fields do not establish readiness. They will be required for live Sandbox acceptance, but need not block scaffolding.

## Risks
- Schema-boundary safeguards have test evidence; runtime commerce authorization and payment invariants remain unimplemented.
- npm audit reports seven moderate development-tool findings through the TypeScript ESLint/minimatch dependency chain after a compatible update attempt. The production dependency audit reports zero findings. Review tooling updates before broader development.
- Live semantic quality is not established by the 15 canned gold responses. Source/role checks constrain extraction but cannot prove all mandatory requirements were preserved; parsed values remain untrusted proposals.
- Docker VFS builds consume substantial temporary storage; monitor free disk space during rebuilds.
- Schemas cannot establish authenticity of supplied statuses, evidence, IDs, or digests. Canonical lookups, current policy/expiry checks, digest generation, prompt-injection defenses, duplicate protection, budget reservations, and provider reconciliation still require services and tests.
- PaymentState includes VERIFYING from ARCHITECTURE.md (D-021), resolving the earlier vocabulary discrepancy. Legal transitions and state-dependent authorization remain deferred to the payment-state-machine stage.
- Synthetic hotel data must be clearly labeled; Sandbox checkout must not imply real hotel booking or arbitrary-merchant support.
- Scope expansion into search integrations, other verticals, or multi-agent orchestration could delay the core demo.

## Next 3 actions
1. On instruction, execute only Codex Prompt 6: implement the pure deterministic financial policy service with DENY / REQUIRE_APPROVAL / ALLOW_ELIGIBLE_FOR_CHECKOUT and explicit reason codes.
2. Test hard budget/currency constraints, mandatory FAIL/UNKNOWN, approval thresholds, merchant review, and supported duplicate/approval state inputs; no LLM may decide financial eligibility.
3. Update STATUS.md, TASKS.md, and meaningful decisions, report tests/blockers, recommend proposal binding/approvals, and stop for instruction.

## Demo readiness
- Intent parsing: Interface, OpenAI structured adapter, Pydantic/source/role validation, exact minor-unit conversion, fake parser, /v1/agent/parse, and 15 prompt fixtures implemented. Mock integration passes; live provider configuration and semantic quality remain unverified.
- Offer search: Implemented/tested with eight synthetic hotel fixtures, explicit filters, stable pagination, canonical ID lookup, and API labels. No live search or frontend catalog UI.
- Verification: Deterministic engine implemented/tested with required/preferred checks, evidence, independent preference percentage, and stable in-memory snapshots. Semantic matching, database persistence, and UI are absent. PASS does not imply financial-policy eligibility.
- Policy: PolicyDecision contract and enums exist; deterministic policy service and budget controls absent.
- Approval: Bound ApprovalRequest contract and timestamp validation exist; authorization service and PayPal buyer flow absent.
- PayPal: PaymentIntent contract exists; no provider adapter, transition service, or integration. Sandbox account/credential readiness remains unknown.
- Audit: Not implemented; no persistence or timeline.
- Security tests: Boundary validation cases pass (strict money, unexpected fields, evidence, references, timestamps); runtime authorization/provider tests absent. Demo is not ready.

## Test status
- Unit: Backend `pytest -q`: 406 tests passed (190 domain-contract, 76 catalog/service/API, 56 verifier, 83 parser/SDK/API, and the existing health test), with no warnings.
- Integration: Both parsers run the 15 gold cases; real SDK mocked HTTP confirms strict closed JSON schema and real production dependency wiring. Unconfigured parsing returns 503 while health/catalog remain operational. Verifier runs against committed synthetic fixtures with expected PASS/FAIL/UNKNOWN. Existing in-process search/health/OpenAPI and HTTP 422 cases also pass. Rebuilt backend in Docker Compose and confirmed healthy status, /health HTTP 200, eight labeled offers, the three planned demo-price candidates, combined filters, and currency-required price filtering. Frontend container remains healthy; frontend code unchanged.
- E2E: Temporary Playwright/Chromium scaffold smoke checks passed on local development and Compose production frontend at desktop/mobile sizes, with no runtime errors or horizontal overflow. No committed full purchase-flow E2E suite yet.
- Security: Schema tests reject coerced/negative money, missing budgets, forged extra fields, unsupported enums, mismatched snapshot references, malformed digests, semantic PASS without evidence, and invalid approval windows. Catalog tests additionally reject malformed fixtures, duplicate IDs, non-synthetic labels, coerced filters, and caller paths; returned objects cannot mutate canonical offers. Verifier cases cover missing evidence, mandatory false even with no evidence, coercion/type confusion, injection-like prose, unknown/unsupported predicates, perfect preferences unable to override failure, input mutation, and snapshot changes on altered terms/evidence. Parser cases reject missing/unlimited/fabricated budgets, source mismatches, unit/currency ambiguity, role swaps, duplicate attributes, quantity confusion, extra authority fields, partial/refused output, and raw provider errors. No comprehensive runtime security suite yet. Prior scaffold checks verified empty credentials and ignored local env files. npm production audit: zero findings; development audit: seven moderate tooling findings.

Current stage: Ruff, pytest (406 passed, no warnings), and `pip check` pass. OpenAI SDK and its runtime dependencies are pinned; parser route and backend-only Compose configuration are added. Backend Docker rebuild/healthy startup and live health/catalog/OpenAPI checks pass. The unconfigured deployed parse route correctly returns HTTP 503; actual backend API key/model are absent. No frontend, financial policy, database persistence, approval, or payment changes; no paid/live model calls.

Prior scaffold checks passed: frontend ESLint, TypeScript check, production build; backend Ruff and `pip check`; Compose configuration validation and image builds; diff whitespace validation. Managed proxy CA override used for container dependency downloads. Services left running through Compose on localhost ports 3000 and 8000.
