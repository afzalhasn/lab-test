"""Create users table with authentication fields

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, primary_key=True),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=100), nullable=False),
        sa.Column('role', sa.Enum('ADMIN', 'LAB_ASSISTANT', name='userrole'), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('refresh_token', sa.Text(), nullable=True),
        sa.Column('refresh_token_expires_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username'),
        schema='public'
    )
    
    # Create index on username for faster lookups
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True, schema='public')
    
    # Create index on role for role-based queries
    op.create_index(op.f('ix_users_role'), 'users', ['role'], schema='public')
    
    # Create index on is_active for filtering active users
    op.create_index(op.f('ix_users_is_active'), 'users', ['is_active'], schema='public')

def downgrade() -> None:
    # Drop indexes
    op.drop_index(op.f('ix_users_is_active'), table_name='users', schema='public')
    op.drop_index(op.f('ix_users_role'), table_name='users', schema='public')
    op.drop_index(op.f('ix_users_username'), table_name='users', schema='public')
    
    # Drop users table
    op.drop_table('users', schema='public')
    
    # Drop enum type
    op.execute('DROP TYPE IF EXISTS userrole') 