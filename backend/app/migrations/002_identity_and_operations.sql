CREATE TABLE users (
 user_id TEXT PRIMARY KEY, username TEXT NOT NULL UNIQUE,
 password_hash TEXT NOT NULL, salt TEXT NOT NULL,
 enabled INTEGER NOT NULL DEFAULT 1 CHECK(enabled IN (0,1)), credential_version INTEGER NOT NULL DEFAULT 1
);
CREATE TABLE sessions (
 token_hash TEXT PRIMARY KEY, user_id TEXT NOT NULL REFERENCES users(user_id),
 credential_version INTEGER NOT NULL, expires_at REAL NOT NULL
);
CREATE INDEX session_owner ON sessions(user_id,expires_at);
CREATE TABLE rate_events (
 bucket TEXT NOT NULL, at REAL NOT NULL
);
CREATE INDEX rate_bucket ON rate_events(bucket,at);
CREATE TABLE resource_leases (
 lease_id TEXT PRIMARY KEY, user_id TEXT NOT NULL, kind TEXT NOT NULL, expires_at REAL NOT NULL
);
CREATE TABLE provider_observations (
 sequence INTEGER PRIMARY KEY, payment_id TEXT NOT NULL REFERENCES checkouts(payment_id),
 at TEXT NOT NULL, capture_status TEXT, event_id TEXT, details TEXT NOT NULL
);
CREATE TABLE provider_events (
 event_id TEXT PRIMARY KEY, event_type TEXT NOT NULL, resource_id TEXT NOT NULL, received_at TEXT NOT NULL
);
CREATE TABLE refund_attempts (
 refund_id TEXT PRIMARY KEY, payment_id TEXT NOT NULL UNIQUE REFERENCES checkouts(payment_id),
 request_key TEXT NOT NULL UNIQUE, state TEXT NOT NULL,
 provider_refund_id TEXT, amount_minor INTEGER NOT NULL, currency TEXT NOT NULL,
 operator TEXT NOT NULL, reason TEXT NOT NULL, created_at TEXT NOT NULL
);
CREATE TABLE identity_events (
 sequence INTEGER PRIMARY KEY, user_id TEXT NOT NULL REFERENCES users(user_id),
 event TEXT NOT NULL, at TEXT NOT NULL
);
