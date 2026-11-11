# Ryuk Status

Last verified: 2026-11-11, latest GitHub baseline 674bdf0 plus this security/demo-preparation change. Changes were prepared in an isolated worktree; older workspace edits were preserved.

## Current milestone
Step 12 review and feasible non-live fixes/preparation are complete. Step 13 rehearsal/runbook preparation is complete; **live buyer-approved Step 11 acceptance and demo freeze remain pending**. No production readiness claim.

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

## Remaining requiring buyer/operator or later production work
1. Privately configure the real demo password/origin/model/Sandbox seller and use a distinct Sandbox buyer to explicitly authorize a reviewed payment. Never share passwords or private .env in chat/Git.
2. Verify one backend-confirmed live capture, exact ledger settlement and audit; record actual timing before certifying the three-minute demo. Step 11 live acceptance remains unverified.
3. Review residual Medium constraints: volatile canonical authority/early audit, manual long-lived/orphaned provider uncertainty handling, and private single-buyer auth/availability architecture. Keep one protected backend worker; production multi-user/multi-worker operation needs further architecture.
4. Resolve/accept development tooling advisories and design fully tested script CSP for the dynamic PayPal SDK. No confirmed current XSS/Critical exploit was found.
5. Pull/rebuild the user's deployment from the pushed revision. Isolated container rehearsal is not a deployment of private settings or a buyer-approved payment.

## Source control
Prepared for commit/push as requested. No force-push, remote-history rewrite or financial deployment is authorized/needed. Existing local checkout was not reset or overwritten.
