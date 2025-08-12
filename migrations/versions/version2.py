"""Add image moderation support

Revision ID: 002_add_image_support
Revises: 001_moderation_events
Create Date: 2025-08-11 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '002_add_image_support'
down_revision = '6ca78f35db24'
branch_labels = None
depends_on = None

def upgrade():
    # Add new columns to moderation_events
    op.add_column('moderation_events', sa.Column('file_path', sa.String(), nullable=True))
    op.add_column('moderation_events', sa.Column('file_size', sa.Integer(), nullable=True))
    op.add_column('moderation_events', sa.Column('file_type', sa.String(), nullable=True))
    op.add_column('moderation_events', sa.Column('image_dimensions', postgresql.JSONB(), nullable=True))
    
    # Create image_analysis table for detailed image data
    op.create_table('image_analysis',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('moderation_event_id', sa.Integer(), nullable=False),
        sa.Column('detected_objects', postgresql.JSONB(), nullable=True),
        sa.Column('nsfw_scores', postgresql.JSONB(), nullable=True),
        sa.Column('text_in_image', sa.Text(), nullable=True),
        sa.Column('image_hash', sa.String(), nullable=True),
        sa.Column('processing_time', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['moderation_event_id'], ['moderation_events.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_image_analysis_moderation_event_id', 'image_analysis', ['moderation_event_id'], unique=False)
    op.create_index('ix_image_analysis_image_hash', 'image_analysis', ['image_hash'], unique=False)

def downgrade():
    op.drop_index('ix_image_analysis_image_hash', table_name='image_analysis')
    op.drop_index('ix_image_analysis_moderation_event_id', table_name='image_analysis')
    op.drop_table('image_analysis')
    op.drop_column('moderation_events', 'image_dimensions')
    op.drop_column('moderation_events', 'file_type')
    op.drop_column('moderation_events', 'file_size')
    op.drop_column('moderation_events', 'file_path')
