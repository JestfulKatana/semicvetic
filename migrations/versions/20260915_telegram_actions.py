"""Track Telegram message copies and lead processing actions."""
from alembic import op
import sqlalchemy as sa

revision = '20260915_actions'
down_revision = '20260915_preferred_date'
branch_labels = None
depends_on = None


def upgrade():
    for table, columns in {
        'lead': [sa.Column('processed_at', sa.DateTime()), sa.Column('processed_by', sa.String(64))],
        'telegram_delivery': [sa.Column('message_id', sa.BigInteger()), sa.Column('rendered_status', sa.String(30))],
    }.items():
        existing = {c['name'] for c in sa.inspect(op.get_bind()).get_columns(table)}
        for column in columns:
            if column.name not in existing:
                op.add_column(table, column)


def downgrade():
    for table, columns in {'lead': ['processed_at', 'processed_by'], 'telegram_delivery': ['message_id', 'rendered_status']}.items():
        with op.batch_alter_table(table) as batch:
            for name in columns:
                batch.drop_column(name)
