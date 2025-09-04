"""Fix auto-increment for all id columns

Revision ID: 0c970d99f6b2
Revises: a3a0a441c50f
Create Date: 2025-09-04 12:43:22.501819

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0c970d99f6b2'
down_revision: Union[str, None] = 'a3a0a441c50f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # List of all tables that need auto-increment on their id column
    tables = [
        'attendance_records',
        'chatbot_menus',
        'customer_data',
        'employees',
        'expense_records',
        'hr_support_tickets',
        'inventory_items',
        'leave_applications',
        'marketing_campaigns',
        'payslips',
        'promotions',
        'sales_records',
        'staff_messages',
        'work_schedules'
    ]

    # Create sequences and set them as default for id columns
    for table in tables:
        sequence_name = f'{table}_id_seq'

        # Create sequence
        op.execute(f'CREATE SEQUENCE IF NOT EXISTS {sequence_name}')

        # Set sequence as default for id column
        op.execute(
            f'ALTER TABLE {table} ALTER COLUMN id SET DEFAULT nextval(\'{sequence_name}\')')

        # Set the sequence ownership to the column (important for proper cleanup)
        op.execute(f'ALTER SEQUENCE {sequence_name} OWNED BY {table}.id')

        # Reset sequence to start from current max value + 1
        op.execute(f'''
            SELECT setval('{sequence_name}', 
                COALESCE((SELECT MAX(id) FROM {table}), 0) + 1, 
                false)
        ''')


def downgrade() -> None:
    """Downgrade schema."""
    # List of all tables that had auto-increment added
    tables = [
        'attendance_records',
        'chatbot_menus',
        'customer_data',
        'employees',
        'expense_records',
        'hr_support_tickets',
        'inventory_items',
        'leave_applications',
        'marketing_campaigns',
        'payslips',
        'promotions',
        'sales_records',
        'staff_messages',
        'work_schedules'
    ]

    # Remove auto-increment from id columns
    for table in tables:
        sequence_name = f'{table}_id_seq'

        # Remove default from column
        op.execute(f'ALTER TABLE {table} ALTER COLUMN id DROP DEFAULT')

        # Drop sequence
        op.execute(f'DROP SEQUENCE IF EXISTS {sequence_name}')
