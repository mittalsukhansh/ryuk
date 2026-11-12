<!-- Current publication scope: submission tag v0.1.2-sandbox-demo points to af750c2. Production-foundation changes are on the review branch only, not main or the submission tag. Earlier release-preparation wording below is superseded by this scope. No deployment or real-ledger migration. -->

# Production foundations: v0.1.2-sandbox-demo source release

This package strengthens the existing **single-host PayPal Sandbox** application. It does not enable live PayPal, real hotel inventory, bookings, autonomous LLM spending or public deployment. These changes are included on the production-foundation review branch; no installation upgrade or deployment is performed by publishing a tag. The hackathon's existing single-buyer login remains the default; multiple users are not needed to present it.

## Schema upgrades and atomic provisioning

`CheckoutStore` applies the ordered SQL in `backend/app/migrations/` under one `BEGIN IMMEDIATE` transaction. `schema_migrations` records each version and a SHA-256 checksum of newline-normalized SQL. Newer database versions, changed applied files, migration gaps, incompatible legacy core columns and foreign-key violations fail closed. A failed migration rolls back schema/data/version markers together. Existing unversioned ledgers are adopted without resetting accounts, holds, checkout records or consent. Never edit an applied migration; add another version.

Demo account, initial policy and merchant mapping provisioning share a transaction. Existing accounts are never reseeded. Changing an existing merchant mapping requires deliberate operator action; startup cannot silently redirect it. Policy versions are immutable: changed policy terms need a new version. Local identity creation likewise inserts the user, budget and policy together.

Before upgrading an installation, reconcile/inspect active work and use the consistent backup procedure in [operations](operations.md). Keep a protected offline copy and rehearse upgrades against a **copy** first. Verify schema versions and held/settled totals on that copy. Do not run tests against the real ledger. Do not use an old application against an upgraded ledger just because SQLite can open it. Restore only with a reconciliation plan that preserves all provider activity since the backup; a stale backup can lose duplicate protection. This task exercised fresh/legacy fixture upgrades, failure rollback and concurrent startup, not your installation or a power-loss recovery drill.

SQLite remains a local persistent-file, single-host design; WAL and FULL synchronous writes do not provide multi-host failover. Network filesystems are unsupported. The file is mode 0600 and newly created parent directory mode 0700; Windows ACLs, existing parent permissions, encryption, host backups and disk alerts remain operator responsibilities. A symlink at the configured database filename is rejected; this is not a general defense against a compromised host.

## Optional per-user local login

`RYUK_AUTH_MODE=demo` preserves the existing private single-buyer mode. It does not migrate that buyer into a new account. `RYUK_AUTH_MODE=local` explicitly enables **operator-created** identities, separate budgets/policies and owner-scoped records. No registration, external identity service or extra PayPal account is required. Do not switch modes merely to record the hackathon video.

For a separately prepared installation/copy, an operator can create an account with an interactive password prompt:

```sh
docker compose exec backend python -m app.manage_users create buyer-one --limit-minor 150000
docker compose exec backend python -m app.manage_users reset buyer-one
docker compose exec backend python -m app.manage_users disable buyer-one
```

Run only the intended command; reset prompts for a new password, disable revokes access. Passwords are never command-line arguments. These commands require filesystem/container operator authority. Creation fails rather than overwriting an existing identity/account. Reset/disable invalidate that identity's sessions without changing purchases or budget. Resetting a disabled account does not re-enable it.

Passwords use salted scrypt; only hashed opaque session tokens are persisted. Twenty-minute sessions survive backend restarts, expire without sliding renewal and check current credential version/enabled state on every use. Login failures remain generic, including unknown usernames. Local mode limits persist across workers, keyed by the authenticated proxy client address for login and actor for model requests. The existing signed proxy channel, exact backend origin checks, HttpOnly/SameSite cookies and HTTPS/secure-cookie requirement remain. `APP_ENV=production` rejects an enabled shared-demo workspace and requires local auth, HTTPS and the private proxy secret; this gate is not a production certification.

There is no OIDC, MFA, email recovery, password-breach service or public account lifecycle. Local operator access is the administrative trust boundary; operator labels in audit entries are not external identity attestations. An identity-provider integration would be a separate choice, not an unnoticed change to demo login.

## Availability bounds

- Backend bodies: 64 KiB with a ten-second absolute receive deadline; invalid/oversized bodies fail before JSON parsing. The Next proxy also bounds body size/time. Nginx has body/send timeouts.
- Backend in-flight requests: 64 per event loop, with a short admission deadline and 429 on saturation.
- Local login: five attempts per verified client per minute; DB-backed hash concurrency at most four globally/two per client. Session caps: eight per user, 1,024 globally. Rate-event allocation has a global cap.
- Local model use: ten calls per actor per minute; DB-backed concurrency at most two per actor/eight globally. Leases expire after sixty seconds after a crash; normal completion releases them. Existing model HTTP timeout remains twenty seconds with no automatic SDK retries.
- Proposal retention: at most 1,000 canonical proposals per actor; at most 100 saved approval records per proposal. Reject new work at the boundary; never delete financial history to restore quota.
- Compose CPU/memory/PID bounds: backend and frontend each 1 CPU/512 MiB/128 PIDs; ingress 0.5 CPU/128 MiB/64 PIDs. Actual capacity needs load testing; resource limits can cause safe unavailability and cannot replace edge DDoS protection.

The shared-demo mode retains its existing process-local session/rate behavior. These limits are not a distributed public edge or automatic financial-record retention policy. Monitor disk growth and archive under a reviewed operational process; no audit/ledger pruning was introduced.

## Provider observations and reversals

Local terminal payment states remain immutable. A provider observation is separate: a historically successful checkout may later show REFUNDED or REVERSED. An authenticated exact-order GET can also discover a capture after a local failure; that capture is recorded once as a financial adjustment and added to gross settled spend. It is never hidden behind a terminal local status.

Operators can query one payment or page through all payments, including terminal ones:

```sh
docker compose exec -T backend python -m app.provider_admin monitor --reference PAYMENT_ID --operator local-operator --reason "Scheduled exact-order observation"
docker compose exec -T backend python -m app.provider_admin monitor-batch --after 0 --limit 50 --operator local-operator --reason "Scheduled provider observation"
```

Batch monitoring performs GETs only; inspect each returned error and follow `next_after` until null. A future sweep starts at zero. The operator must schedule these commands/alerts; no background scheduler was installed. An order-creation orphan with no order ID stays blocked for investigation using the original references.

An optional Sandbox webhook subscription can target `/v1/provider/paypal/webhook` through a deliberately configured HTTPS ingress. `PAYPAL_WEBHOOK_ID` enables the route; otherwise it fails closed. Subscribe to capture COMPLETED, PENDING, DENIED, REFUNDED and REVERSED events. A real public HTTPS webhook endpoint/subscription was not created in this task; localhost cannot receive PayPal callbacks.

Events require PayPal's signature-verification API, bounded headers/body, a five-minute transmission window and bounded verification allowance. Provider resource links never select arbitrary fetch destinations. The backend verifies its stored exact order/capture, amount/currency and merchant; refund details are separately fetched and bound to the original capture. Only authenticated provider evidence can write an observation/adjustment. Event IDs and financial adjustment IDs deduplicate repeated delivery. If observation fails, the event is not acknowledged as processed, allowing provider redelivery. Expired transmissions require polling/reconciliation rather than weakening replay checks.

Full refund/reversal adjustments are recorded separately; gross settled purchase budget is **not automatically replenished**, avoiding accidental new spending authority. Partial refunds, fees, FX, disputes/chargeback lifecycle and net merchant accounting are outside this implementation. Partial/unknown statuses remain visible for operator investigation. If a refund/reversal is first discovered while the original local capture is still uncertain, recording that adjustment does not by itself settle or release its hold; preserve the reservation for operator reconciliation. A signed reversal does not rewrite the historical capture receipt.

## Buyer request → operator review → explicit full Sandbox refund

`RYUK_REFUNDS_ENABLED=true` explicitly enables requests and dispatch; the default is false. A buyer can request a full Sandbox refund from a confirmed checkout or saved activity. The backend binds the request to its owned payment, digest, capture and exact terms. There is one request/attempt per checkout. The buyer cannot choose amount/merchant, approve their request or invoke a refund mutation. Saved activity shows the durable review/provider state after reload.

```sh
docker compose exec -T backend python -m app.provider_admin list-requests
docker compose exec -T backend python -m app.provider_admin approve --reference REQUEST_ID --operator local-operator --reason "Reviewed buyer request"
# Or use reject instead of approve. Approval itself performs no refund.
docker compose exec -T backend python -m app.provider_admin dispatch-refund --reference REQUEST_ID --operator local-operator --reason "Explicit execution after review"
docker compose exec -T backend python -m app.provider_admin reconcile-refund --reference REFUND_ATTEMPT_ID --operator local-operator --reason "Check original refund outcome"
```

These examples are instructions for a later controlled Sandbox acceptance test, **not commands executed in this task**. `list-requests` returns the latest 100; use the buyer's known request reference if it is older. Review is durable and audited; dispatch first verifies the original completed capture, rechecks the bound approval, then atomically claims a unique stable idempotency key before one POST. A duplicate dispatch returns the existing attempt. A timeout/malformed response stays UNKNOWN; process termination may leave DISPATCHED. Neither permits another POST. Known refund IDs can be reconciled with GET even after disabling new refund execution. A verified webhook can attach/resolve an observed full refund. If no refund ID is known, use PayPal merchant records/support with the original key and references; never make another payment/refund to discover what happened.

Live refund/webhook behavior, provider delivery ordering, public load, operator alerting and disaster recovery remain deployment acceptance gates. Automated coverage uses synthetic accounts, fresh temporary SQLite files and mocked provider HTTP only.
