"""entity_events: run-scoped primary key (run_id, id)

Generated events are numbered EVT-0000001… per run, so a single-column PK on id
made the second generated run fail with a duplicate-key error.

Revision ID: a3c1e5f0b7d2
Revises: 992d19c34b48
Create Date: 2026-11-02 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'a3c1e5f0b7d2'
down_revision: Union[str, Sequence[str], None] = '992d19c34b48'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_constraint(op.f('pk_entity_events'), 'entity_events', type_='primary')
    op.create_primary_key(op.f('pk_entity_events'), 'entity_events', ['run_id', 'id'])
    # run_id is now the leading PK column, so its separate index is redundant.
    op.drop_index(op.f('ix_entity_events_run_id'), table_name='entity_events')


def downgrade() -> None:
    """Downgrade schema. Fails if two runs share an event id; delete extra runs first."""
    op.create_index(op.f('ix_entity_events_run_id'), 'entity_events', ['run_id'], unique=False)
    op.drop_constraint(op.f('pk_entity_events'), 'entity_events', type_='primary')
    op.create_primary_key(op.f('pk_entity_events'), 'entity_events', ['id'])
