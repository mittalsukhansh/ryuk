CREATE TABLE IF NOT EXISTS recovery_index (
 sequence INTEGER PRIMARY KEY AUTOINCREMENT, proposal_id TEXT NOT NULL UNIQUE, user_id TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS recovery_owner ON recovery_index(user_id,sequence);
CREATE TABLE IF NOT EXISTS proposal_authority (
 proposal_id TEXT PRIMARY KEY, user_id TEXT NOT NULL, body TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS proposal_owner ON proposal_authority(user_id);
CREATE TABLE IF NOT EXISTS approval_lookup (
 request_id TEXT PRIMARY KEY, proposal_id TEXT NOT NULL REFERENCES proposal_authority(proposal_id)
);
CREATE TABLE IF NOT EXISTS proposal_audit (
 sequence INTEGER PRIMARY KEY, proposal_id TEXT NOT NULL REFERENCES proposal_authority(proposal_id),
 event TEXT NOT NULL, at TEXT NOT NULL, details TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS accounts (
 user_id TEXT PRIMARY KEY, currency TEXT NOT NULL,
 limit_minor INTEGER NOT NULL CHECK(limit_minor >= 0),
 settled_minor INTEGER NOT NULL CHECK(settled_minor >= 0)
);
CREATE TABLE IF NOT EXISTS policies (user_id TEXT PRIMARY KEY, body TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS merchants (merchant_id TEXT PRIMARY KEY, paypal_id TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS checkouts (
 payment_id TEXT PRIMARY KEY, proposal_id TEXT NOT NULL UNIQUE,
 user_id TEXT NOT NULL, body TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS reservations (
 payment_id TEXT PRIMARY KEY REFERENCES checkouts(payment_id),
 user_id TEXT NOT NULL REFERENCES accounts(user_id), currency TEXT NOT NULL,
 amount_minor INTEGER NOT NULL CHECK(amount_minor > 0),
 status TEXT NOT NULL CHECK(status IN ('HELD', 'SETTLED', 'RELEASED'))
);
CREATE TABLE IF NOT EXISTS checkout_audit (
 sequence INTEGER PRIMARY KEY, payment_id TEXT NOT NULL REFERENCES checkouts(payment_id),
 event TEXT NOT NULL, at TEXT NOT NULL, details TEXT NOT NULL
);
INSERT OR IGNORE INTO recovery_index(proposal_id,user_id)
 SELECT proposal_id,user_id FROM checkouts ORDER BY rowid;
