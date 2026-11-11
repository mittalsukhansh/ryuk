# Ryuk — three-minute demo outline

This is a proposed live script, not evidence that Sandbox acceptance passed.
Configure the private workspace and live Sandbox app/buyer first; see frontend.md.
All hotel records are synthetic. The payment must be a real Sandbox transaction.

1. **0:00–0:25 — Intent.** Unlock the private workspace. Show the server's USD 1,500
   available budget, USD 1,500 purchase ceiling and USD 1,300 review threshold.
   Submit the supplied Switzerland/gym/mountain-view/cancellation instruction.
2. **0:25–0:50 — Control.** Show the three records: review-required USD 1,180, review USD
   1,390, blocked USD 1,620. Open the blocked record; backend DENY and no checkout
   button make the hard ceiling visible.
3. **0:50–1:25 — Evidence.** Open the USD 1,390 record. Point to mandatory evidence,
   preferred pool and snapshot. Show REQUIRE_APPROVAL and the threshold reason.
4. **1:25–1:45 — Application consent.** Compare the original request with the full parsed intent. Reject omissions or weakened requirements. Then show bound merchant,
   amount/currency and expiry. Explicitly approve. Explain that this consent does
   not replace PayPal's buyer authorization.
5. **1:45–2:35 — Sandbox.** Use the actual PayPal button and Sandbox buyer account.
   Wait for backend-confirmed success, capture reference, snapshot and USD 110
   remaining. Do not describe a callback, pending status or test stub as payment.
6. **2:35–3:00 — Trace.** Show the backend audit: verification, policy, application
   approval, order, buyer approval, reservation, capture and settlement.

Only one transaction is needed. Two successful USD 1,180/1,390 purchases cannot
both fit in the same USD 1,500 ledger. A canceled/pending payment is not a successful
demo; preserve pending reservations and query status rather than retrying capture.
Do not reset a ledger with an uncertain provider outcome. Time the actual live
sequence before claiming the three-minute acceptance criterion is met.

## Automated acceptance already reproducible

Backend tests cover eligible trusted proposals, mandatory model-intent review, budget/required-attribute denial, proposal amount/merchant/currency tampering, duplicate capture, expired/replayed consent, concurrency and ambiguous provider recovery. The browser suite exercises the real UI/proxy/API/ledger with mocked SDK/provider, including below-threshold intent review, rejection, hard denial, held capture responses, reconciliation and mobile layout. Run the commands in operations.md. These are mock acceptance evidence, not a live three-minute measurement.

## Live acceptance record — pending user action

Record the application revision, actual duration, authenticated buyer action, exact reviewed merchant/amount/currency, internal proposal/payment and provider order/capture references, final backend state, ledger movement and audit evidence. Keep references private and do not publish buyer identity, passwords, OAuth/session tokens or real credentials. Require backend SUCCEEDED and exactly one settlement. If the outcome is uncertain, stop and reconcile; do not reset or force another capture. The unused connection probe from a different workspace is not acceptance of this revision.

Step 13 preparation is implemented; live acceptance/demo freeze remains pending. This document deliberately does not certify a live payment or semantic completeness.
