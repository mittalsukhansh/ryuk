# AgentPay Status

Last verified: 2026-11-11. Evidence: source inspection, local builds, pytest/lint/type checks, live HTTP requests, Chromium smoke checks, and a healthy Docker Compose deployment. Planning checklists alone are not completion evidence.

## Current milestone
Codex Prompt 8 — Exact nine-state payment graph implemented and tested. Next recommended stage: Codex Prompt 9 — PayPal Sandbox adapter, awaiting instruction. Authenticated APIs, durability, payment coordination, and live LLM evaluation remain pending.

## Overall status
In Progress

The foundation runs locally and in Docker Compose. The Next.js preview serves HTTP 200 and FastAPI `/health` returns HTTP 200 with `{"status":"ok"}`. Eight Pydantic domain contracts and the synthetic hotel catalog/search API are implemented. The catalog contains eight labeled offers with evidence and explicit filtering. The full commerce flow is not implemented and the product is not demo ready. Deterministic attribute verification now returns mandatory PASS/FAIL/UNKNOWN, independent preference scores, and evidence-backed in-memory snapshots. LLM-backed parsing and a deterministic fake now implement one interface with structured extraction, source checks, Pydantic validation, exact minor-unit conversion, and the /v1/agent/parse endpoint. Pure financial policy now evaluates explicit backend authority records with deterministic outcomes, reason codes, current-verification checks, and read-only approval/history gates. Canonical proposal digests and a service-owned in-memory approval workflow now enforce exact bindings, expiry, permanent invalidation, replay checks, and checkout policy revalidation. The payment state machine now enforces legal backend events, terminal states, and reconciliation-only capture uncertainty. Persistent/authenticated infrastructure, transactional coordination, and PayPal integration remain unimplemented; live LLM evaluation has not been performed.

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
- [x] 15 labeled synthetic gold prompts tested through both implementations; 83 parser/SDK/API regression cases added. That stage passed 406 tests with no warnings; the current suite total appears below. Ruff and pinned dependency checks passed.
- [x] Parser configuration, limits, trust boundaries, and mock-only evidence documented in `docs/intent-parser.md` and D-024.
- [x] Rebuilt the backend image with pinned SDK dependencies; both containers are healthy. Live Docker checks confirm health/catalog HTTP 200, parse route in OpenAPI, and safe parser HTTP 503 with the currently absent API key/model. No paid model call was made.

- [x] Pure financial policy with explicit policy/budget/history/time inputs, strict requested/active/available caps, currency checks, current deterministic verification, quantity checks, merchant review, and review thresholds.
- [x] Stable reason codes, exact read-only approval binding/expiry/rejection gates, duplicate/unknown-history denial, and separate budget-currency output. No LLM chooses financial eligibility.
- [x] Financial-policy stage added 97 regression cases; that stage passed 503 tests and Ruff. The expanded suite total appears below. Pure function, integration boundaries, and race/persistence limits documented in `docs/policy.md` and D-025.

- [x] Versioned canonical SHA-256 proposal digests bind identity/creation, user, offer, merchant, integer money/currency, policy version, and current verification snapshot; regeneration is enforced by policy and approval consumption.
- [x] Internal in-memory canonical/request ownership, pending creation, one-time approve/reject operations, exact expiry, permanent INVALIDATED grants on term changes, latest-request replay protection, and checkout policy revalidation.
- [x] Process-local locking and expected-digest update checks; returned copies cannot create or extend consent. Restart loses approvals and cannot restore client-held grants.
- [x] Binding/approval stage added 60 regression cases and passed 563 tests/Ruff; the expanded total appears below. Documentation and D-026 explain the in-memory/authentication/persistence boundary.

- [x] Centralized immutable graph for exactly CREATED, POLICY_CHECK, AWAITING_APPROVAL, CHECKOUT_READY, AWAITING_PAYPAL_BUYER, CAPTURE_PENDING, SUCCEEDED, FAILED, PENDING_PROVIDER; unused VERIFYING removed per current user request.
- [x] Event-based transitions reject illegal paths/terminal exits; application approval returns to policy, and ambiguous capture only resolves through conclusive reconciliation events.
- [x] Validated state-only PaymentIntent updates preserve identity, terms, creation/approval data, and idempotency; optional local stale-state check implemented.
- [x] 250 state/event/pair/lifecycle/schema regression cases added; all 813 backend tests pass without warnings and Ruff passes. Graph and trust boundaries documented in `docs/payment-state-machine.md` and D-027; D-021 metadata marks its superseded vocabulary.

## In Progress
- [ ] No active implementation stage; payment-state transition core is complete. PayPal adapter is recommended next and has not been started. Authenticated HTTP integration, durability, execution coordination, and live model evaluation remain pending.

## Remaining
### P0
- [ ] Configure a valid structured-output-capable OPENAI_MODEL and backend API credentials, then evaluate live parsing/semantic fidelity on the prompt cases. The interface, provider adapter, validation, fake, endpoint, and deterministic tests are implemented.
- [ ] Persist verification snapshots and display evidence/required/preferred checks in the UI. The deterministic engine and in-memory snapshots are implemented.
- [ ] Implement durable/atomic duplicate prevention and ledger reservations. Canonical digest generation and pure policy/approval gates are complete.
- [ ] Add authenticated proposal/approval endpoints and durable storage, and wire the implemented binding/expiry/checkout gate into the future payment coordinator before capture.
- [ ] Implement persistent payment state/audit, atomic budget reservations, and execution coordination. Centralized graph validation exists; it does not perform these side effects.
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
- No unresolved blocker for the requested state-machine core. A live PayPal adapter later needs Sandbox accounts/app credentials and supported buyer/merchant configuration. Public approval deployment requires a real authenticated-user layer and durable repository, neither present in the current application. Live model acceptance remains unverified and requires valid backend OPENAI_API_KEY/OPENAI_MODEL configuration; no paid/live provider call was made.
- Container validation required the managed proxy CA override documented in README.md. Parser rebuilds hit the environment disk limit; unused task build caches/images were cleared and the backend build order reduced temporary VFS layer duplication. A disk-exhaustion failure was resolved by removing task-created build caches and reducing frontend build layers; both containers then passed health checks.
- Sandbox account/app setup and usable credentials are unverified; empty template fields do not establish readiness. They will be required for live Sandbox acceptance, but need not block scaffolding.

## Risks
- The approval reference store is in memory and has no public endpoints/authentication adapter. Only trusted backend callers may register canonical records or supply actor identities; deployment requires durable storage/authenticated handlers. Process-local locking does not prevent cross-process overspend or duplicate capture.
- npm audit reports seven moderate development-tool findings through the TypeScript ESLint/minimatch dependency chain after a compatible update attempt. The production dependency audit reports zero findings. Review tooling updates before broader development.
- Live semantic quality is not established by the 15 canned gold responses. Source/role checks constrain extraction but cannot prove all mandatory requirements were preserved; parsed values remain untrusted proposals.
- Docker VFS builds consume substantial temporary storage; monitor free disk space during rebuilds.
- Schemas cannot establish authenticity of supplied statuses, evidence, IDs, or digests. Digest regeneration and service-owned approval lifecycle checks now exist; authenticated external canonical loading, durable repositories, broader prompt-injection defenses, atomic duplicate protection/budget reservations, and provider reconciliation still need integration and tests.
- PaymentState now follows the explicit nine-state request (D-027); VERIFYING was removed and D-021 vocabulary metadata superseded. Event spelling/graph legality does not authenticate provider outcomes or financial permission; the later coordinator must enforce those facts and durable state/audit writes.
- Synthetic hotel data must be clearly labeled; Sandbox checkout must not imply real hotel booking or arbitrary-merchant support.
- Scope expansion into search integrations, other verticals, or multi-agent orchestration could delay the core demo.

## Next 3 actions
1. On instruction, execute only Codex Prompt 9: implement the PayPal Sandbox adapter with OAuth, create order, status lookup, capture, stable idempotency, and verified provider-state mapping.
2. Use mocked HTTP tests for refusal/error/ambiguous timeout paths, keep secrets backend-only, and never blindly retry capture. No end-to-end live capture is authorized by the state graph alone.
3. Update STATUS.md, TASKS.md, and meaningful decisions, report tests/blockers, recommend checkout integration, and stop for instruction.

## Demo readiness
- Intent parsing: Interface, OpenAI structured adapter, Pydantic/source/role validation, exact minor-unit conversion, fake parser, /v1/agent/parse, and 15 prompt fixtures implemented. Mock integration passes; live provider configuration and semantic quality remain unverified.
- Offer search: Implemented/tested with eight synthetic hotel fixtures, explicit filters, stable pagination, canonical ID lookup, and API labels. No live search or frontend catalog UI.
- Verification: Deterministic engine implemented/tested with required/preferred checks, evidence, independent preference percentage, and stable in-memory snapshots. Semantic matching, database persistence, and UI are absent. PASS does not imply financial-policy eligibility.
- Policy: Pure deterministic eligibility implemented/tested, with strict caps/currency, available-funds arithmetic, current verification, quantity/merchant checks, reason codes, and read-only approval/history gates. No public policy endpoint, persistent active policy store, atomic reservations, or durable duplicate lock.
- Approval: Canonical digest generation, service-owned in-memory pending/approve/reject lifecycle, owner/binding/expiry/invalidation/replay checks, and checkout revalidation implemented. Authenticated HTTP adapters, durable storage/audit, UI, and PayPal buyer flow remain absent.
- PayPal: PaymentIntent and event-driven state machine implemented/tested; no provider adapter or checkout execution. Reconciliation events are structural inputs, not real provider queries. Sandbox account/credential readiness remains unknown.
- Audit: Not implemented; no persistence or timeline.
- Security tests: Boundary validation cases pass (strict money, unexpected fields, evidence, references, timestamps); runtime authorization/provider tests absent. Demo is not ready.

## Test status
- Unit: Backend `pytest -q`: 813 tests passed (190 domain-contract, 76 catalog/service/API, 56 verifier, 83 parser/SDK/API, 97 policy, 60 binding/approval/schema, 250 state-machine, and the existing health test), with no warnings.
- Integration: State-machine success/approval/recheck/uncertainty paths and all state-event/state-pair combinations pass; input bindings/idempotency remain unchanged. No provider events are authenticated or executed in these tests. In-memory workflow plus current policy/verifier pass create/decide/checkout, expiry, changed/restored terms, version change, supersession, replay, wrong-user, restart-loss, and concurrent approval/update checks. Policy consumes real synthetic offers and current verifier results, yielding eligible/review/denied demo cases; approval, state, currency, and stale-record combinations pass. Both parsers run the 15 gold cases; real SDK mocked HTTP confirms strict closed JSON schema and real production dependency wiring. Unconfigured parsing returns 503 while health/catalog remain operational. Verifier runs against committed synthetic fixtures with expected PASS/FAIL/UNKNOWN. Existing in-process search/health/OpenAPI and HTTP 422 cases also pass. Rebuilt backend in Docker Compose and confirmed healthy status, /health HTTP 200, eight labeled offers, the three planned demo-price candidates, combined filters, and currency-required price filtering. Frontend container remains healthy; frontend code unchanged.
- E2E: Temporary Playwright/Chromium scaffold smoke checks passed on local development and Compose production frontend at desktop/mobile sizes, with no runtime errors or horizontal overflow. No committed full purchase-flow E2E suite yet.
- Security: Schema tests reject coerced/negative money, missing budgets, forged extra fields, unsupported enums, mismatched snapshot references, malformed digests, semantic PASS without evidence, and invalid approval windows. Catalog tests additionally reject malformed fixtures, duplicate IDs, non-synthetic labels, coerced filters, and caller paths; returned objects cannot mutate canonical offers. Verifier cases cover missing evidence, mandatory false even with no evidence, coercion/type confusion, injection-like prose, unknown/unsupported predicates, perfect preferences unable to override failure, input mutation, and snapshot changes on altered terms/evidence. Parser cases reject missing/unlimited/fabricated budgets, source mismatches, unit/currency ambiguity, role swaps, duplicate attributes, quantity confusion, extra authority fields, partial/refused output, and raw provider errors. Policy cases prove active/requested limits cannot be raised by model text, approvals/preferences cannot override hard denial, uncertain history blocks execution, all approval bindings and expiry are checked, and mutated/coercible authority inputs fail closed. New binding/approval tests cover all identity/term changes, forged hash pairs, source verification freshness, exact deadline, stale updates, returned-object tampering, one-time decisions, owner isolation, no revival on term restoration, and current-policy revalidation. State-machine tests cover all illegal event/source combinations, direct success/approval bypasses, terminal restarts, retry/cancel during capture uncertainty, removed/unknown states, malformed events, stale expected state, and mutated model rejection. No comprehensive runtime transaction/security suite yet. Prior scaffold checks verified empty credentials and ignored local env files. npm production audit: zero findings; development audit: seven moderate tooling findings.

Current stage: Ruff and pytest (813 passed, no warnings) pass. No dependency, frontend, public route, persistence, or provider changes. The state graph is structural backend validation only; no new deployment, authenticated provider observation, fund reservation, capture, or live payment is claimed.

Prior scaffold checks passed: frontend ESLint, TypeScript check, production build; backend Ruff and `pip check`; Compose configuration validation and image builds; diff whitespace validation. Managed proxy CA override used for container dependency downloads. Services left running through Compose on localhost ports 3000 and 8000.
