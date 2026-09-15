"""Preserve the date requested in trial appointment forms."""
from alembic import op
import sqlalchemy as sa

revision = '20260915_preferred_date'
down_revision = '20260915_delivery'
branch_labels = None
depends_on = None


def upgrade():
    if 'preferred_date' not in {c['name'] for c in sa.inspect(op.get_bind()).get_columns('lead')}:
        op.add_column('lead', sa.Column('preferred_date', sa.Date(), nullable=True))


def downgrade():
    with op.batch_alter_table('lead') as batch:
        batch.drop_column('preferred_date')
