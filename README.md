# AgentPay

Intent-aware commerce: verify that a purchase matches the user's requirements before payment. This repository implements a Next.js + TypeScript + Tailwind preview, a FastAPI API with synthetic hotel search, validated Pydantic domain contracts, and deterministic attribute verification. LLM-backed intent parsing is available behind an interface with structured output and a deterministic test fake. Pure deterministic financial eligibility is implemented. Canonical proposal hashing and an internal in-memory approval workflow are implemented. The provider-neutral payment state machine enforces legal event-driven transitions. Database persistence, authenticated approval endpoints, provider execution, and checkout integration remain planned stages.

See [STATUS.md](STATUS.md) for verified progress, [PLAN.md](PLAN.md) for scope, [DECISIONS.md](DECISIONS.md) for decisions, and [domain schemas](docs/domain-schemas.md) for contracts and validation rules. See [catalog documentation](docs/catalog.md) for the eight synthetic offers and search endpoint, and [verification documentation](docs/verification.md) for mandatory/preferred checks and snapshot semantics. [Intent parser documentation](docs/intent-parser.md) covers provider configuration, source validation, and the 15 synthetic prompt cases. [Financial policy documentation](docs/policy.md) describes authority inputs, decisions, reason codes, and the boundary with future transaction controls. [Proposal binding and approvals](docs/approvals.md) documents exact hashes, expiry, invalidation, replay handling, and the in-memory reference store. [Payment state machine](docs/payment-state-machine.md) lists legal events, terminal locks, uncertainty rules, and integration boundaries.

## Docker Compose

Requires Docker Engine with BuildKit and Docker Compose v2.

```sh
cp .env.example .env
docker compose up --build -d --wait
curl --fail http://localhost:8000/health
# Expected: {"status":"ok"}
```

Open http://localhost:3000 for the preview and http://localhost:8000/docs for API documentation. Ports are published on loopback only. `/health` asserts process liveness, not database or provider readiness. Both containers have health checks and run as non-root users. Health and catalog startup need no credentials; intent parsing needs backend OpenAI configuration.

```sh
docker compose logs -f
docker compose down
```

There is no database service yet; persistence belongs to a later stage. The backend loads the labeled `fixtures/hotels.json` at startup and exposes `POST /v1/offers/search`. The frontend is static and does not yet call the API. Compose runs the production frontend build; use the local workflow below for hot reload.

### Builds behind a TLS-inspecting proxy

Keep Docker's configured proxy settings. Both Dockerfiles accept an optional BuildKit secret named `proxy_ca`; this is only a public CA bundle, never an API credential. On a managed cloud environment, create an override **outside the repository** with:

```yaml
services:
  backend:
    build:
      secrets: [proxy_ca]
  frontend:
    build:
      secrets: [proxy_ca]
secrets:
  proxy_ca:
    file: /etc/ssl/certs/ca-certificates.crt
```

Then run `docker compose -f docker-compose.yml -f /path/to/override.yml up --build -d --wait`. Set the file path to the proxy-trusted CA bundle on the host. The CA is mounted only during dependency installation and is not copied into the image. Normal builds require no override.

## Local development

Requires Node.js 22+ (tested with 24), npm, and Python 3.12. Dependencies are recorded in `frontend/package-lock.json` and pinned backend requirements files.

Backend, in one terminal:

```sh
cd backend
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-dev.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Frontend, in another terminal:

```sh
cd frontend
npm ci
npm run dev
```

Visit http://localhost:3000. To test the production frontend locally, use `npm run build` followed by `npm start`. Stop Compose first if using the same ports.

## Checks

```sh
# From backend/
.venv/bin/ruff check .
.venv/bin/pytest -q
.venv/bin/pip check

# From frontend/
npm run lint
npm run typecheck
npm run build

# From repository root, with services running
curl --fail http://localhost:8000/health
curl --fail --output /dev/null http://localhost:3000

docker compose config --quiet
```

Backend tests cover domain validation, fixture integrity, catalog filtering/isolation, deterministic verification/preferences, snapshot identity, deterministic financial policy, canonical hashing, approval lifecycle/expiry/replay/concurrency checks, exhaustive payment transitions and uncertainty paths, intent parsing through the fake and real SDK with mock HTTP, and HTTP health/search/parse contracts without external services. There are no purchase-flow, runtime security, or E2E regression suites yet; linting and type checking are not substitutes for them.

## Configuration and secrets

Use `.env.example` as the canonical template; `env.example` is the original planning template retained for reference. `.env` and local environment variants are ignored by Git and excluded from image build contexts. Never put real credentials into either example.

Compose passes `APP_ENV`, `OPENAI_API_KEY`, and `OPENAI_MODEL` only to the backend at runtime. Set OpenAI values in the ignored root `.env` to enable `POST /v1/agent/parse`; empty values return 503 without breaking health/catalog. Local Uvicorn needs the two OpenAI variables set in its process environment and does not automatically load root `.env`. PayPal and database settings remain reserved and unused. `NEXT_PUBLIC_*` values are public browser configuration and must never contain secrets; the frontend does not consume them yet. No paid/live model validation has been performed; see [intent parser documentation](docs/intent-parser.md).
