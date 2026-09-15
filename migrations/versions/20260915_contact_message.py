"""Remember contacts already delivered to a recipient."""
from alembic import op
import sqlalchemy as sa
revision = '20260915_contact'
down_revision = '20260915_actions'
branch_labels = None
depends_on = None


def upgrade():
    columns = {c['name'] for c in sa.inspect(op.get_bind()).get_columns('telegram_delivery')}
    if 'contact_message_id' not in columns:
        op.add_column('telegram_delivery', sa.Column('contact_message_id', sa.BigInteger()))


def downgrade():
    with op.batch_alter_table('telegram_delivery') as batch:
        batch.drop_column('contact_message_id')
