"""Add durable per-recipient Telegram delivery queue to existing site schema."""
from alembic import op
import sqlalchemy as sa

revision = '20260915_delivery'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # A fresh development database may already contain the model via create_all.
    if sa.inspect(op.get_bind()).has_table('telegram_delivery'):
        return
    op.create_table('telegram_delivery',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('lead_id', sa.Integer(), sa.ForeignKey('lead.id'), nullable=False),
        sa.Column('chat_id', sa.String(64), nullable=False),
        sa.Column('attempts', sa.Integer(), nullable=False),
        sa.Column('next_attempt_at', sa.DateTime(), nullable=False),
        sa.Column('sent_at', sa.DateTime(), nullable=True),
        sa.Column('last_error', sa.String(80), nullable=True),
        sa.UniqueConstraint('lead_id', 'chat_id', name='uq_lead_recipient'))
    op.create_index('ix_telegram_delivery_lead_id', 'telegram_delivery', ['lead_id'])


def downgrade():
    op.drop_table('telegram_delivery')
