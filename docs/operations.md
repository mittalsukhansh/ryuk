# Private demo operations

## Boundaries
Run one private backend worker on a protected local SQLite volume. This is not a public multi-user deployment. Sessions, proposals/approvals and early audit remain process-local. Never infer lost authority from browser data after restart. Durable pending captures must use provider-state reconciliation, not renewed consent or an automatic capture retry. Configure HTTPS with secure cookies outside loopback.

## Back up without changing the ledger

From backend/ with the backend virtual environment active:

```sh
python -m app.backup_checkout /absolute/path/ledger.sqlite3 /private/new-backup.sqlite3
```

The command reads the source using SQLite's online backup API (including committed WAL state), writes a new private file and verifies integrity. It refuses all existing destinations, including symlinks; it never clears holds/spending. Protect backups like the live ledger. An interrupted/failed destination is not a verified backup: retain it for diagnosis and choose a new destination for a retry.

For a restore rehearsal, use an isolated host/process and a NEW destination, never the configured live path. Verify integrity and original account/hold/payment/audit counts before any traffic. Keep provider calls disabled. Before switching a real deployment to a restored ledger, stop financial writes and reconcile provider activity since that backup; a stale backup can otherwise forget captures and permit duplicates. No automatic rollback/reset/restore-in-place command is provided.

## Uncertainty and incident handling

- Save internal proposal/payment IDs and original provider request/order/capture references in private incident records; do not publish tokens or passwords.
- Query the provider using the original stored terms. Unknown provider outcomes retain their holds.
- Do not delete attempts, reset spending, release holds by age, or create a replacement purchase to resolve uncertainty.
- For an orphaned create with no stored provider ID, use the controlled merchant's Sandbox records/support and exact original reference/request ID. Do not invent a provider lookup API or silently retry a mutation.
- Rotate the private demo password and restart to invalidate process-local sessions if compromise is suspected; preserve the ledger. Capture reconciliation remains tied to durable original terms.
- Use trusted edge request limits for public-facing infrastructure; do not accept arbitrary forwarded IP headers as identity.

## Container rehearsal performed

A separately named Docker Compose project built both images using the managed public CA build secret. Credentials and demo enablement were explicitly disabled, separate ports/volume were used, both health checks passed, frontend returned HTTP 200 and backend /health returned ok. No private ledger, buyer interaction or provider capture was used. This verifies packaging/default fail-closed startup, not a full payment deployment.

## Mock rehearsal

Start the backend fixture from backend/:

```sh
RYUK_E2E_TEST_ONLY=1 PYTHONPATH=. python tests/frontend_server.py
```

It always creates a fresh temporary ledger; its reset endpoints are not in production app/image startup. Start the production frontend from frontend/ with `RYUK_BACKEND_URL=http://127.0.0.1:8100 npm start -- --port 3100`, then run `npm run test:e2e`. Model/provider behavior is mocked. Stop these fixture processes after testing; do not use them for user purchases.
