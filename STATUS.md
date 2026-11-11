# Ryuk Status

## Groq compatibility repair — 2026-11-12
Reproduced a real provider HTTP 400: Groq rejects the overlapping integer/number branches in the extracted attribute anyOf schema. Compile only the Groq transport schema by removing the redundant integer branch (number already includes integers), retaining the shared strict Pydantic/source/domain validation and mandatory original/parsed intent review. No JSON-mode downgrade, coercion or provider fallback.

Live gpt-oss-120b extraction on the committed synthetic gold request now passes strict backend validation with the expected finite budget. A different synthetic phrasing requested clarification rather than bypassing validation; this is not proof of semantic completeness or live payment acceptance. No payment call was made. Provider HTTP failures now produce code-owned authentication/access/model/rate/request messages without provider bodies or secret reflection. Current regression results are recorded below.


## Current verification — merge repair, 2026-11-12
Repaired latest GitHub commit cde0d08 in an isolated worktree. Original local edits, private configuration and financial records were preserved.

- Removed committed merge markers from seven files; consolidated duplicated review flags, policy enum members and validation handlers.
- Canonical review field: intent_review_required. Preserved original/parsed intent digest binding, source-clause role checks, HTTP authentication/origin/rate limits, and both security test sets.
- Preserved the readable original/parsed review UI and combined browser coverage. Earlier hardening report retained separately in docs/security-hardening.md.
- **1,056 backend tests pass**, Ruff passes; frontend lint/typecheck/production build pass; **44 mocked production-browser assertions pass** using the installed Chromium (CHROMIUM_PATH=/usr/bin/chromium).
- New source/runbook regression rejects committed conflict markers.
- No live model/provider/payment calls, financial reset/deletion or deployment. Docker not rebuilt for this repair. Live buyer-approved Sandbox acceptance remains pending.

## Earlier milestone notes
The following sections retain historical evidence/counts; the verification above is current.


Last verified: 2026-11-11, latest GitHub baseline 674bdf0 plus this security/demo-preparation change. Changes were prepared in an isolated worktree; older workspace edits were preserved.

## Current milestone
Step 12 — Current-source security review completed with four confirmed High findings fixed/contained and documented regression evidence. Remaining Medium/Low risks are open in `docs/security-review.md`. **Step 11 live acceptance remains incomplete**; no live model/Sandbox transaction or timing was attempted. Step 13 has not started.

## Implemented
- Existing casebook UI, synthetic catalog, deterministic evidence/policy/approval, PayPal SDK/backend adapter and atomic persistent SQLite checkout coordinator retained.
- Mandatory application review of original versus parsed intent for every model-derived workspace purchase, bound by proposal digest v2. This prevents automatic bypass, not semantic incompleteness or inattentive consent.
- Authentication on the formerly public parser endpoint; private workspace parser already has actor isolation. Bounded model allowance separate from payment status/reconciliation.
- Static validation/clarification responses without private input/context reflection; HTTPS cannot disable secure session cookies.
- Bounded auth allocations, bounded streaming proxy bodies, frame/MIME/referrer headers and isolated temporary-only test reset fixture.
- Backend-only Groq provider selection/config forwarding, strict schema and shared source/domain validation, preserving earlier local Groq work on the newer remote architecture. No provider fallback.
- Operator-only consistent SQLite backup to new mode-0600 output with overwrite/symlink refusal and integrity checks; no ledger resets.
- Security report with exploit sequences/recommendations: docs/security-review.md. Backup/recovery/mock-runbook: docs/operations.md. Updated demo script and pending live acceptance record: docs/demo-script.md. Decision D-033.

## Verification
- Backend: **1,034 tests passed**, no warnings; Ruff and pinned dependency consistency pass.
- Frontend: ESLint, TypeScript and optimized production build pass.
- Browser: **23 assertions passed** through actual production UI/proxy/API/SQLite with isolated model/SDK/provider mocks. Covers original/parsed review, rejection, denial, delayed capture confirmation, reconciliation, no premature success, origin/path/body/auth controls, private cookies, security headers, desktop/mobile layout and runtime errors.
- npm production audit: **zero** findings. Full audit: **eight moderate development-tool** advisories, no High/Critical.
- Docker: CLI/daemon available here; both images built with CA trust preserved. Separately named credential-disabled Compose project uses isolated ports/volume; backend/frontend healthy, backend health OK and frontend HTTP 200. Compose config and diff whitespace checks pass.
- No live model/provider/payment calls, private secret-value inspection, or existing financial record reset/deletion in this stage. Mock reset actions are confined to newly created temporary fixture ledgers.
- The externally supplied 1,004-test/36-assertion review summary was not present in origin/main; it was not independently verifiable and is superseded by the evidence above.


## Completed
- [x] Next.js/TypeScript/Tailwind and FastAPI/Compose foundation, strict integer-money domain contracts, eight labeled synthetic hotel offers and trusted search.
- [x] Deterministic evidence-backed required/preferred verification and snapshots, structured OpenAI parser interface/fake/15 test prompts and pure financial policy.
- [x] Canonical digest v2 and process-local approval ownership/expiry/permanent invalidation/replay checks; exact nine-state payment graph. Backend-owned intent-review flag and intent-bearing snapshot bind all model-derived workspace proposals to explicit application consent.
- [x] Backend Sandbox OAuth/create/status/capture adapter, immutable provider binding, stable request IDs and safe ambiguous outcomes.
- [x] Durable SQLite checkout/payment/key/terms/state/ledger/hold/checkout-audit records; atomic final policy/approval/digest/merchant/reservation claim, exactly-once settlement/release and GET-only uncertainty recovery.
- [x] Visible Ryuk branding, original monochrome casebook with restrained red, serif/monospace typography, subtle grain, three-record primary shortlist and optional expansion. No franchise artwork or generic AI gradients/glassmorphism.
- [x] Working command entry and backend-parsed intent display, backend candidate/verdict/evidence/preference matrix, exact-term approve/reject dialog, snapshot and backend timeline.
- [x] Real SDK integration code: server-owned order ID -> PayPal buyer authorization -> backend capture. Result waits for backend SUCCEEDED; callback alone never displays paid. Pending state offers reconciliation, not a capture retry.
- [x] Thin workspace/proposal/approval/audit APIs reuse existing services; query/identifier/decision bodies reject browser authority fields.
- [x] Explicitly enabled single-buyer demo password verification, opaque hashed session tokens, HttpOnly/SameSite cookie, origin checks, rate limit/logout; default missing configuration stays blocked. Direct parser HTTP now authenticates before provider initialization; HTTPS cannot disable Secure cookies.
- [x] Same-origin Next proxy with allowlisted paths, credential isolation, no cache/redirect forwarding and safe errors. Only PayPal's public client ID reaches the SDK.
- [x] Trusted runtime account/policy/payee provisioning and protected persistent Compose ledger volume. Startup preserves existing funds/holds and never resets spending.
- [x] Independently reran pre-fix baseline: **983 passed**. Six new failing pre-fix assertions reproduced four High findings. Final backend suite **1,004 passed** (21 additional regression cases), no pytest warnings; Ruff and `pip check` pass.
- [x] Frontend ESLint, TypeScript and optimized production build pass. Chromium against the intended standalone production server passes **36 assertions** over actual Next proxy/FastAPI/services/SQLite with mocked SDK/provider, desktop/mobile and mobile intent-review dialog, no page errors or horizontal overflow. No live timing claim.
- [x] Browser bundles checked for backend credential names/synthetic-secret markers; image inputs reviewed for test/environment exclusion. Secret values were not inspected; no full historical credential-audit claim. Docker/Compose validation could not be rerun because the Docker CLI is unavailable here.
- [x] Step 12 fixes: authenticated billable parser; enclosing-clause role checks plus mandatory exact intent review for every model-derived workspace proposal; input-free validation errors; enforced secure HTTPS cookies. Detailed exploit sequences/preconditions/fixes/tests and remaining risks: `docs/security-review.md`, D-033.
- [x] Browser test harness now allocates new isolated mock ledgers per case, never deletes reservations or resets existing financial records. Production fixture-control routes and proxy forwarding are rejected; redirect regression proves no upstream redirect is followed.

- [x] Local startup troubleshooting fix: setting-specific sanitized diagnostics, validated HTTPS/loopback origins, preflight budget/merchant checks and SQLite error classification; 21 regression cases pass. The user’s exact local invalid setting remains unconfirmed until they run the updated image.

## In Progress
- [ ] Step 11 live acceptance remains unverified. This review deliberately made no real model/payment calls and did not inspect private provider configuration. UI/integration mock evidence is not live acceptance.

## Remaining
### P0
- [ ] Make actual provider configuration available to the runtime and run the real structured parser/Sandbox checkout through the UI. No production fake fallback exists.
- [ ] Verify live SDK popup, separate buyer authorization, backend provider-confirmed capture/reference, ledger settlement and audit under three minutes.
- [ ] Complete Step 11 live acceptance before calling the demo ready. Step 12 was explicitly requested and reviewed without performing that live acceptance.
- [ ] Durable canonical proposal/approval/evidence and early audit storage; these remain process-local. Production multi-user identity and multi-worker authority deployment remain unimplemented.
- [ ] Operator recovery for unknown/orphaned creates and permanently inconclusive captures; preserve uncertain holds.
- [ ] Validate the proposed demo script on a live Sandbox run. Checkout/audit browser flow is mock-tested, not live accepted.

### P1
- [ ] Residual semantic omissions/changed meaning need buyer scrutiny and separate evaluation; automatic review bypass is contained, not semantic completeness proven.
- [ ] Bound request buffering, parser quotas/concurrency, session/canonical retention and proxy-aware login limiting (M-01).
- [ ] Enforce schema migrations, OS-specific ledger/backup ACLs, atomic provisioning and immutable policy versions (M-04).
- [ ] Address terminal-provider monitoring, dev-tool advisory chain and proxy/header defense-in-depth gaps (M-05/M-06/L-01/L-02).
- [ ] Production PostgreSQL-backed authority/ledger deployment and migration; SQLite remains a single-host reference.
- [ ] Extend visual/accessibility/browser/device coverage after live acceptance; desktop and phone are verified, not all device/provider combinations.

### P2
- [ ] Other purchase verticals, real external search, multi-rail/team approvals and conceptual UPI/P3P.
- [ ] LangGraph/specialized agents only after the core demo works.

## Blockers
- Live acceptance was outside this review's permitted actions. A root `.env` exists in this local checkout but its values were never opened; existence does not establish provider readiness. Keep it private, not in chat/Git upload.
- Actual model/Sandbox account, seller verification and buyer popup/capture behavior remain unverified by mocks. No provider credential readiness assertion is made.
- Docker CLI is unavailable; Compose/container validation and image rebuild were not performed. No deployment changes were applied.
- A private demo also needs opt-in password/origin/cookie configuration. Production multi-user authentication and durable canonical authority are still separate limitations.

## Risks
- Demo auth and canonical approvals/early audit are process-local/single-buyer. Restart invalidates sessions/consent and blocks new capture; durable attempted captures still reconcile using original terms.
- SQLite must use a protected persistent local directory/volume, not ephemeral storage or NFS. Pending holds cannot be released just because time passed or the browser closed.
- Candidate verdicts are backend snapshots; selection and capture recheck current rules/budget. One USD 1,500 ledger cannot fund both USD 1,180 and USD 1,390 successful demo purchases.
- Local cancellation does not void a PayPal order; refunds/external merchant actions and long-lived provider uncertainty need operator support.
- Hotel data is synthetic and checkout targets a configured demo payee, not a real hotel booking. Preference percentages cannot override mandatory checks or financial rules.
- Live model fidelity, SDK/account behavior and buyer timing are not established by mocks.
- Current npm audit reports seven moderate **development dependency nodes** in one minimatch/TypeScript-ESLint advisory chain; `npm audit --omit=dev` reports zero. Dev-tool upgrade remains separate work; no broad audit fix or lockfile rewrite was performed.
- Source-role checks and required human review cannot prove complete model fidelity. Resource limits, reload discovery/operator recovery, SQLite/ACL/migration/provisioning and external-terminal-provider monitoring remain open; see M-01 through M-06 and L-01/L-02.

## Next 3 actions
1. Review the remaining Medium/Low findings and separately authorize prioritized hardening; protect the existing ledger and private settings.
2. When explicitly permitted, complete Step 11 real model/Sandbox acceptance and timing without substituting mocked evidence.
3. Stop after Step 12. Step 13 requires a separate instruction.

## Demo readiness
- Intent parsing: UI and protected backend parser orchestration implemented; fake/SDK tests pass. Live model response/fidelity unverified.
- Offer search: Backend candidates appear in the shortlist; six USD records from eight labeled fixtures, top three initially visible. No live hotel availability or booking.
- Verification: Real backend evidence/status/preference counts and snapshot displayed in matrix; no invented evidence/PASS.
- Policy: Backend deterministic verdict/reasons displayed. UI does not calculate eligibility. Current rules rerun before capture with an atomic hold.
- Approval: Every model-derived proposal requires original/parsed intent review; exact terms/expiry/reasons use authenticated backend consent. Process-local authority remains a deployment limitation.
- PayPal: Actual SDK integration and server-order/capture/status code complete; mock browser flow passes. **Real Sandbox buyer/capture acceptance remains unverified and Step 11 remains incomplete.**
- Audit: UI uses backend canonical/approval events and durable checkout events/timestamps. Early events remain in memory; broader durable audit deployment is pending.
- Security review: Step 12 actual-source review and isolated adversarial regressions complete; four High findings fixed/contained, Medium/Low residuals documented. Live demo and production deployment are not certified.

## Test status
- Unit: Backend `pytest -q`: **1,004 passed**, no pytest warnings; independently verified pre-fix **983 passed**; Ruff passes; `pip check` reports no broken requirements.
- Integration: Real-adapter/SQLite checkout tests plus authenticated session/proxy/workspace paths, exact backend evidence/verdicts, consent, forbidden fields, origin/owner checks, cancellation races, duplicate/overspend, rollback and restart/lost-response GET-only recovery pass. Bundle marker check passes. Compose validation blocked by missing CLI.
- E2E: Standalone production Next -> same-origin proxy -> actual FastAPI/services/SQLite -> mocked SDK/HTTP provider: **36 Chromium assertions** pass at 1440px/390px. Required intent-review/rejection, secret-safe errors, origin/allowlist/method/redirect checks, spoofed callback, cancellation, no false success, timeout reconciliation and mobile dialog pass. Test external browser traffic is blocked. Not real Sandbox acceptance.
- Security: Confirmed High reproductions, bound review, authenticated direct parser, input-safe errors, cookie hardening and existing financial tampering/race/recovery tests pass. No production deployment, power-loss durability or live provider acceptance claimed.

Step 12 changes application review policy for model-derived proposals and advances the canonical digest format; active financial caps, payment graph, atomic claims/accounting and GET-only uncertainty recovery are unchanged. Provider credentials remain backend-only. Only isolated mock backend and local standalone production frontend were booted for validation. No secret values read, live calls/captures, existing financial resets/deletes, image rebuild, deployment or Step 13 work.

Groq repair validation: 1,063 backend tests pass (including schema-equivalence and sanitized provider-status regressions), Ruff and diff checks pass. Workspace tests explicitly isolate provider selection from inherited live Groq configuration. Live gold extraction passed through strict validation on gpt-oss-120b; no payment operation performed. Frontend unchanged by this backend-only repair.

## UI example monetary evidence repair — 2026-11-12
Reproduced the exact screenshot prompt live: the model placed currency text in amount_text, then another response omitted the monetary role cue from its quote. The prompt now explicitly separates numeric tokens from currency. Groq transport constrains numeric amount grammar and, where exact role-bearing/currency-bearing source spans are available, narrows budget/threshold quote/amount enums to those spans. No coercion, default budget, financial policy change or automatic fallback. Strict backend source/money validation and human intent review remain in force. The screenshot's unchanged text now passed live gpt-oss-120b validation. No payment call performed.

UI example repair validation: 1,066 backend tests, Ruff and diff checks pass. Exact screenshot prompt live-validates with 150000/130000 minor-unit money and mandatory amenities preserved. This is a tested extraction case, not a general semantic guarantee; no financial execution occurred.

## PayPal SDK callback lifecycle repair — 2026-11-12
Confirmed that a terminal/pending capture response caused the parent to unmount PayPalCheckout and invoke Buttons.close while the SDK onApprove promise was still running. A realistic mock lifecycle regression failed before the fix (one premature close). Keep SDK nodes mounted for the selected purchase, hide further button action on non-awaiting states, and let the SDK finish its own callback/window cleanup. Local cancellation now holds the UI busy until its callback completes too.

Frontend lint/typecheck/production build and 47 production-browser assertions pass, including success/pending/cancellation lifecycle guards. Backend financial rules, keys, claims/reservations and no-retry semantics are unchanged; no backend tests were rerun for this frontend-only repair. No live provider/payment call or user payment-status claim in this stage. HTTP 200 alone does not prove SUCCEEDED; inspect the existing payment's state before any new purchase. Update/recreate frontend only to avoid resetting in-memory backend authority.

## Read-only acceptance evidence export — 2026-11-12
Added app.export_acceptance CLI for the operator to export recorded capture/order/payment references, backend state, minimal audit and exact-once settlement checks from the local SQLite ledger. Read-only/query-only snapshot; no provider calls or resets. Credentials, actor identity, request text, idempotency keys and arbitrary audit details are omitted. Default receipt filenames are Git-ignored.

The separately authorized USD100 Sandbox test in this workspace has exported evidence: recorded SUCCEEDED, capture reference, exactly one dispatch/settlement, matching settled reservation and 15 audit events. This does not certify the user's separate website payment or UI timing; that receipt must be exported from their local Docker ledger. No new payment was attempted in this task.

Evidence exporter validation: 1,069 backend tests passed; Ruff and diff checks passed. Frontend unchanged; no live provider operation performed. Actual receipts remain private outside Git.

## Required scenarios verified — 2026-11-12
Approval-required, budget-denied, mandatory-requirement-denied, tampering-blocked and duplicate-prevented checks pass in a focused 32-test run. New API regression proves an under-budget USD980 no-gym offer cannot create an approval/order, with zero provider calls or funds settled/reserved. Existing approval/buyer gates, canonical/browser tampering and duplicate/concurrency tests were rerun. Evidence and commands: docs/required-scenarios.md. No financial implementation change, live payment, private configuration change or existing ledger reset.

Required-scenario final validation: 1,070 full backend tests passed; focused acceptance run 32 passed; Ruff and diff checks pass. Frontend/financial implementation unchanged in this verification task.

## Final revision revalidation — 2026-11-11 UTC

Validated clean source revision `31367ae338faf494d6bbbcc5a0d6265c3585c6ad`, matching origin/main when checked. This is source/build validation in the managed workspace, not evidence that the user's deployed installation runs this revision.

- Backend: 1,070 tests passed; Ruff and pip dependency consistency passed.
- Frontend: lint, TypeScript and fresh production build passed.
- Browser: 47 assertions passed against the newly built standalone server and isolated FastAPI/SQLite fixtures, with mocked SDK/model/provider, desktop/mobile.
- Git whitespace checks passed. No application implementation changed; no live provider/payment calls or existing financial ledger mutations occurred.
- Deployment identity, running artifact/configuration and deployed smoke checks remain unverified. No Docker image rebuild or deployment was performed in this rerun. User-local receipt export and timed live acceptance remain separate pending evidence.
