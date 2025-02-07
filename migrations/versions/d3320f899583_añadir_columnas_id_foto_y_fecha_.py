"""Añadir columnas id, foto y fecha_nacimiento

Revision ID: d3320f899583
Revises: 193f61492a06
Create Date: 2025-02-07 14:02:12.112691

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd3320f899583'
down_revision = '193f61492a06'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('animal', schema=None) as batch_op:
        batch_op.add_column(sa.Column('foto', sa.String(length=200), nullable=True))
        batch_op.add_column(sa.Column('fecha_nacimiento', sa.String(length=50), nullable=True))

def downgrade():
    with op.batch_alter_table('animal', schema=None) as batch_op:
        batch_op.drop_column('foto')
        batch_op.drop_column('fecha_nacimiento')


