# Optional Render Sandbox review branch

This branch adds a separate hosted Sandbox configuration and an operator-triggered read-only Render Workflow. It does not replace submission tag v0.1.3-sandbox-demo at 9c4ee9d. Do not merge or retag automatically. Hosting alone is not a claim of sponsor eligibility or successful Workflows execution.

## Before creating resources

Claim and verify sponsor credits in Render Billing. The sponsor page links to a signup/credit portal but publishes no reusable promo code. If credits are missing, use the sponsor's Render/PayPal Discord support. This Blueprint creates three paid Starter services, a 1 GB disk and a metered Workflow. Review the Dashboard's current prices and billing before deployment; credits do not impose a permanent spending cap. No resources were activated by local preparation.

Use a separate Render project with trusted workspace members only. Do not import an existing ledger, .env, receipt or Docker volume. Never paste credentials into chat. Enter backend credentials directly in Render's private environment settings. Never give PayPal/Groq secrets or a disk to the Workflow.

## Deploy with a Blueprint

1. In Render choose New > Blueprint, connect this repository and select branch `render-sandbox`.
2. Review `render.yaml`: private backend, private frontend, public nginx ingress and a Python Workflow. All automatic deployments are off. Use a separate project; do not point this Blueprint at pre-existing services with the same names.
3. Set `RYUK_APP_ORIGIN` on the backend to the exact final HTTPS URL of `ryuk-render-demo`, with no trailing slash/path. If Render changes the hostname, update this value before login. A mismatch blocks login; never disable origin checks to bypass it.
4. Configure GROQ_API_KEY, GROQ_MODEL and the Sandbox-only PayPal app client ID/secret and merchant ID privately on the backend. Empty settings leave parsing/checkout unavailable. No live-money environment is supported. The backend demo password and shared proxy secret are generated privately; the frontend references only the proxy secret, not model/payment credentials.
5. The frontend's backend host/port is wired from the private backend service, with `http://` added by its start command. The public nginx service references the private frontend host/port. Do not expose the internal services as public web services.
6. Review costs/credits and create resources only when authorized. After builds finish, check the public page, private backend liveness, HTTPS cookies, exact origin and nonce CSP. Log in manually with the generated demo password. Never publish that password. Test actual provider behavior separately; health checks do not establish it.

The backend runs unchanged in explicit shared-demo mode, not production identity mode. Nginx uses its socket peer for login rate identity and strips caller-supplied address/token headers. Render edge peers may share that identity, so an attacker may exhaust a shared allowance. This conservative configuration avoids inventing trust for arbitrary forwarded headers; it is a private demo with a documented availability limit, not public-scale auth. Do not disable rate limits or trust the leftmost forwarded IP to work around it. Render runtime, disk permissions and provider compatibility need live acceptance before claiming a working hosted checkout.

## Workflow setup (manual alternative)

Create New > Workflow. Choose **Python 3**, not Docker; select repository branch `render-sandbox` and leave Root Directory blank.

Build command:
```
pip install -r backend/requirements.txt -r render_workflows/requirements.txt
```
Start command:
```
PYTHONPATH=backend:. python -m render_workflows.main
```
Python version: 3.12.12. Wait for Render to register the `verify_catalog` definition. Do not reuse backend/Dockerfile: it does not package the workflow or SDK.

The task calls the existing deterministic verifier against the canonical synthetic catalog. It validates an intent and returns advisory evidence/snapshots for up to eight same-currency offers (the example has six USD offers). It has no imports of checkout, PayPal, approval or ledger services, no financial credentials and no mounted disk. Task retries are set to zero with a 30-second timeout.

This is a **separate operator-triggered verification job**. The website's normal investigation still verifies locally and makes its own deterministic policy/approval decisions. Remote results cannot authorize spending, replace canonical offers or mark a payment successful. There is no automatic website dispatch or new browser API endpoint.

Use public fixture input only: Render retains workflow arguments/results temporarily. Do not enter real buyer requests, identities or secrets. To run from the Dashboard, provide a JSON array containing the single object in `render_workflows/demo-input.json`, then run `verify_catalog`. Inspect its actual completed output before claiming Render Workflows acceptance. Registration or a local mock is not a successful cloud run.

Optional local operator trigger after registration:
```
# Install only in a separate local venv; enter RENDER_API_KEY privately, never as an argument.
PYTHONPATH=backend:. python -m render_workflows.run_demo YOUR_WORKFLOW_SLUG/verify_catalog
```
It dispatches only the public bundled example and prints the run ID. It never invokes a model or payment. Investigate the existing run if dispatch is uncertain rather than repeatedly creating runs. Dashboard execution avoids creating an operator API key.

## Local validation

```
python -m venv .venv-render
.venv-render/bin/pip install -r render_workflows/requirements-dev.txt
PYTHONPATH=backend:. .venv-render/bin/pytest -c backend/pyproject.toml -q backend/tests render_workflows/tests
.venv-render/bin/ruff check backend
.venv-render/bin/ruff check --config backend/pyproject.toml render_workflows
```

Validation: **1,123 backend/workflow tests passed** (1,114 existing backend + nine new workflow tests), zero skips/failures/errors. Both Ruff checks and Git whitespace checks pass. The nginx image builds and its official entry point renders a valid configuration (`nginx -t`) in a network-disabled temporary container. Frontend runtime is unchanged; no new frontend/browser/live acceptance is claimed.

Only temporary test databases and mocked providers are used. Workflow tests exercise the real pinned Render SDK's registration without starting cloud execution. The nginx image is tested with network disabled and placeholder loopback upstream; no existing containers or volumes are modified.

Blueprint structure is checked locally against the documented fields and service boundaries. Provider-side Blueprint acceptance is still unverified. Direct download of Render's JSON schema was blocked by the environment's HTTP proxy; this was not bypassed. Actual registration, credits, deployment, task completion and browser/provider behavior on Render remain external gates. Existing frontend/payment/policy/approval/auth runtime code is unchanged.

Official references: [Workflows](https://render.com/docs/workflows), [Python SDK](https://render.com/docs/workflows-sdk-python), [Blueprint spec](https://render.com/docs/blueprint-spec), [Sponsor page](https://paypalaihackathon.devpost.com/details/render).
