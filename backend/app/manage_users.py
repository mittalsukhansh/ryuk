"""Local operator identity provisioning. Passwords are prompted, never command arguments."""

import argparse
import getpass
import os
from uuid import uuid4

from app.schemas.catalog import CatalogSearchRequest
from app.schemas.policy import FinancialPolicy
from app.services.catalog import CatalogService
from app.services.checkout_store import CheckoutStore
from app.services.local_auth import provision_user, reset_credentials


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["create", "reset", "disable"])
    parser.add_argument("username")
    parser.add_argument("--database", default=os.environ.get("RYUK_CHECKOUT_DB_PATH"))
    parser.add_argument("--limit-minor", type=int, default=150000)
    args = parser.parse_args()
    if not args.database:
        parser.error("Configured database required")
    try:
        store = CheckoutStore(args.database)
        password = None
        if args.action != "disable":
            password = getpass.getpass("New password (16+ characters): ")
            if password != getpass.getpass("Confirm password: "):
                raise ValueError("Password confirmation differs")
        if args.action == "create":
            actor = str(uuid4())
            policy = FinancialPolicy(
                user_id=actor,
                version="account-policy-v1",
                currency="USD",
                max_amount_minor=150000,
                approval_threshold_minor=130000,
                allowed_merchant_ids=frozenset(
                    o.merchant_id for o in CatalogService().search(CatalogSearchRequest()).offers
                ),
            )
            provision_user(
                store, args.username, password, limit_minor=args.limit_minor, policy=policy
            )
        else:
            reset_credentials(store, args.username, password)
    except Exception:
        parser.exit(1, "Account operation failed; no credential values displayed.\n")
    print("Account operation completed. Existing financial records preserved.")


if __name__ == "__main__":
    main()
