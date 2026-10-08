"""Create the Inventory Sales Engine system of record.

Revision ID: 0001_initial
Revises:
Create Date: 2026-08-18
"""

from alembic import op

from inventory_sales_engine.db.base import Base
from inventory_sales_engine.db import models  # noqa: F401


revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    Base.metadata.create_all(bind=op.get_bind())


def downgrade() -> None:
    Base.metadata.drop_all(bind=op.get_bind())
