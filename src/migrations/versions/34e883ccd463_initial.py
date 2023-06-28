"""create schema

Revision ID: 34e883ccd463
Revises: 
Create Date: 2023-06-28 21:08:47.740456

"""
from alembic import op

from models.entity import User
from models.roles import Role, UserRole

# revision identifiers, used by Alembic.
revision = '34e883ccd463'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'users',
        User.id.expression,
        User.email.expression,
        User.password.expression,
        User.first_name.expression,
        User.last_name.expression,
        User.disabled.expression,
        User.created_at.expression
    )

    op.create_table(
        'roles',
        Role.id.expression,
        Role.title.expression,
        Role.permissions.expression,
        Role.created_at.expression,
    )

    op.create_table(
        'users_roles',
        UserRole.id.expression,
        UserRole.user_id.expression,
        UserRole.role_id.expression,
        UserRole.user_role_idx
    )


def downgrade() -> None:
    op.drop_table('users')
    op.drop_table('roles')
    op.drop_table('users_roles')
