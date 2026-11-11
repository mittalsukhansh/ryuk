# Ryuk — three-minute walkthrough

Release: `v0.1.0-sandbox-demo` (private, single-buyer Sandbox prerelease). Start with [startup instructions](startup.md); see [release evidence and limitations](release-notes.md).

## Before presenting

- Start/rebuild and check both containers before the timer. Open exactly `http://localhost:3000`, unlock the workspace and keep credentials off-screen.
- All hotels and amenity evidence come from the labeled synthetic catalog. Ryuk does not perform a Google search, book a hotel or move real money. PayPal Sandbox buyer approval is a separate action from application review.
- The user has already reported a successful website payment and a local export with `checks_passed=true`. Keep that private receipt and success screenshot available. Do not initiate another payment merely to rehearse this script.
- Check the current available budget. A USD 1,390 settlement from an initial USD 1,500 budget leaves USD 110, so the original USD 1,180/1,390 examples will now be denied. Restarting or changing seed configuration does not replenish this account. Never delete the volume, reset spending or clear uncertain holds for a demo.
- For an existing-payment walkthrough, use the saved success screenshot/receipt or an actual recording and label it as prior evidence. After backend restart, canonical proposals/approvals and their early audit are lost; the durable receipt is not a reconstructed full timeline.
- A fresh buyer-approved live walkthrough requires sufficient legitimately provisioned test budget and a separate buyer account before starting. If unavailable, use the evidence walkthrough below; do not describe it as a newly executed payment. Any separately provisioned rehearsal environment must be isolated from the existing ledger.

## Run of show — target 3:00

| Time | Show | Say |
| --- | --- | --- |
| 0:00–0:25 | Request and current backend budget; enter the built-in hotel example if desired. | “Ryuk turns a request into typed constraints. The model proposes; the backend decides.” |
| 0:25–0:55 | Original instruction and parsed mandatory/preferred constraints. | “A human must review every model-derived purchase. Missing or weakened requirements mean reject.” |
| 0:55–1:20 | Synthetic shortlist, amenity evidence and policy reason codes. If funds are spent, show the current DENY and use the prior recording for earlier review-required offers. | “Missing mandatory evidence and exceeded budgets block checkout, even when a model suggests the offer.” |
| 1:20–1:45 | Exact-term application review from a current eligible proposal or the labeled prior recording. | “Consent binds merchant, amount, currency, intent and snapshot. This is separate from PayPal buyer authorization.” |
| 1:45–2:25 | Prior PayPal approval/result recording and Ryuk success screenshot, clearly labeled. In a prepared fresh live run, use the actual button and wait for backend SUCCEEDED instead. | “PayPal authorizes the buyer. Only provider-verified backend capture confirms payment; a callback or HTTP 200 is insufficient.” |
| 2:25–2:50 | Private receipt: state SUCCEEDED, checks_passed=true and exactly one dispatch/settlement. Redact references for public sharing. | “The durable ledger records one settlement. Retried or concurrent requests cannot create a second payment in the tested scenarios.” |
| 2:50–3:00 | Release limitations. | “This is a private Sandbox demo with synthetic inventory, not a production travel/payment service.” |

For a fresh live run, use the built-in instruction:

> Find a hotel in Switzerland for 5 nights under USD 1,500. Gym, mountain view and free cancellation are required. Private pool preferred. Ask me above USD 1,300.

With an unspent initial budget, the examples are USD 1,180 review-required, USD 1,390 review-required and USD 1,620 denied. All model-derived offers require review, even below the USD 1,300 threshold. The expanded USD 980 no-gym offer demonstrates a mandatory-requirement denial when budget otherwise permits it.

## When something stalls

Do not press Pay again. For pending/uncertain capture, preserve the reservation and use the existing status/reconciliation control; never retry capture blindly. If PayPal resources show ERR_BLOCKED_BY_CLIENT, check site-specific browser Shields/extensions, pop-up and cookie permissions for the local site and PayPal Sandbox. Do not disable protection globally. A failed or pending run is not a completed live acceptance run.

## Acceptance record

Keep privately: exact checkout revision, actual elapsed time, reviewed amount/currency/merchant, user approval, success screenshot, payment/order/capture references and receipt. Compare the capture reference with seller Sandbox Activity for independent provider evidence. The exporter is a local ledger snapshot, not a fresh provider query or a UI timing measurement.

The five required scenarios pass isolated automated checks: [reproducible matrix](required-scenarios.md). Tampering and concurrency are demonstrated by those tests, not by mutating an existing payment. Run automated browser tests only against the isolated test fixture, never against the user's live demo ledger.

**Timing status:** this schedule is prepared; an actual under-three-minute live run has not been measured. A prior-evidence walkthrough must be labeled as such and does not satisfy live execution timing acceptance.
