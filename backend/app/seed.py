"""Seed one login user per role (dev only). Idempotent: existing emails are skipped, never overwritten.

python -m app.seed
python -m app.seed --password "MyStr0ngPass"   # same password for every seeded user
"""
import argparse

from sqlalchemy import select

from app.core.permissions import Role
from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models import User

DEFAULT_PASSWORD = "Password@123"
SEED_USERS = [
    ("admin@vrptw.com", "Admin", Role.ADMIN, None),
    ("planner@vrptw.com", "Planner", Role.PLANNER, None),
    ("warehouse@vrptw.com", "Warehouse Operator", Role.WAREHOUSE, None),
    ("analyst@vrptw.com", "Logistics Analyst", Role.ANALYST, None),
    ("ops@vrptw.com", "Operations Manager", Role.OPS_MANAGER, None),
    ("supplier@vrptw.com", "Supplier", Role.SUPPLIER, "SUP-001"),
]


def main() -> None:
    ap = argparse.ArgumentParser(prog="seed")
    ap.add_argument("--password", default=DEFAULT_PASSWORD, help="min 8 chars (login API enforces this)")
    args = ap.parse_args()
    if len(args.password) < 8:
        ap.error("password must be at least 8 characters")

    with SessionLocal() as db:
        for email, name, role, supplier_id in SEED_USERS:
            if db.scalar(select(User).where(User.email == email)):
                print(f"skip    {email:22} (exists)")
                continue
            db.add(User(email=email, name=name, role=role, supplier_id=supplier_id,
                        password_hash=hash_password(args.password)))
            print(f"created {email:22} {role}")
        db.commit()
    print(f"\nPassword for newly created users: {args.password}")


if __name__ == "__main__":
    main()
