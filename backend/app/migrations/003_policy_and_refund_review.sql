CREATE TABLE policy_versions (
 user_id TEXT NOT NULL, version TEXT NOT NULL, body TEXT NOT NULL, PRIMARY KEY(user_id,version)
);
INSERT INTO policy_versions SELECT user_id,json_extract(body,'$.version'),body FROM policies;
CREATE TABLE refund_requests (
 request_id TEXT PRIMARY KEY, payment_id TEXT NOT NULL UNIQUE REFERENCES checkouts(payment_id),
 user_id TEXT NOT NULL, binding TEXT NOT NULL, state TEXT NOT NULL,
 buyer_reason TEXT NOT NULL, operator TEXT, operator_reason TEXT, created_at TEXT NOT NULL
);
CREATE TABLE financial_adjustments (
 adjustment_id TEXT PRIMARY KEY, payment_id TEXT NOT NULL REFERENCES checkouts(payment_id),
 kind TEXT NOT NULL, amount_minor INTEGER NOT NULL CHECK(amount_minor>0),
 currency TEXT NOT NULL, at TEXT NOT NULL
);
