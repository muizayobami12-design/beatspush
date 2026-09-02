"""Add Collaboration System tables

Revision ID: 006
Revises: 005
Create Date: 2026-09-01 10:00:00.000000

This migration creates all tables for the Collaboration System:
- collaboration_projects: Joint artist/producer projects
- project_collaborators: Project team members and roles
- stem_files: Audio stems uploaded by collaborators
- project_versions: Project milestones with approval workflow

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision: str = '006'
down_revision: Union[str, Sequence[str], None] = '005'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create collaboration system tables."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = inspector.get_table_names()
    
    # 1. Create collaboration_projects table
    if 'collaboration_projects' not in existing_tables:
        op.create_table(
            'collaboration_projects',
            sa.Column('id', sa.String(length=36), nullable=False),
            sa.Column('project_name', sa.String(length=255), nullable=False),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('creator_id', sa.String(length=36), nullable=False),
            sa.Column('genre', sa.String(length=100), nullable=True),
            sa.Column('status', sa.String(length=50), nullable=True, default='draft'),
            sa.Column('revenue_split_type', sa.String(length=50), nullable=True, default='equal'),
            sa.Column('custom_split', sa.JSON(), nullable=True),
            sa.Column('final_beat_id', sa.String(length=36), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(['creator_id'], ['users.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['final_beat_id'], ['beats.id'], ondelete='SET NULL'),
            sa.PrimaryKeyConstraint('id'),
        )
        op.create_index('ix_collaboration_projects_creator_id', 'collaboration_projects', ['creator_id'])
        op.create_index('ix_collaboration_projects_status', 'collaboration_projects', ['status'])
        op.create_index('ix_collaboration_projects_created_at', 'collaboration_projects', ['created_at'])
    
    # 2. Create project_collaborators table
    if 'project_collaborators' not in existing_tables:
        op.create_table(
            'project_collaborators',
            sa.Column('id', sa.String(length=36), nullable=False),
            sa.Column('project_id', sa.String(length=36), nullable=False),
            sa.Column('user_id', sa.String(length=36), nullable=False),
            sa.Column('role', sa.String(length=50), nullable=True),
            sa.Column('permissions', sa.JSON(), nullable=True),
            sa.Column('revenue_percentage', sa.Float(), default=0.0, nullable=True),
            sa.Column('invited_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
            sa.Column('accepted_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('is_active', sa.Integer(), default=0, nullable=True),
            sa.ForeignKeyConstraint(['project_id'], ['collaboration_projects.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id'),
        )
        op.create_index('ix_project_collaborators_project_id', 'project_collaborators', ['project_id'])
        op.create_index('ix_project_collaborators_user_id', 'project_collaborators', ['user_id'])
    
    # 3. Create stem_files table
    if 'stem_files' not in existing_tables:
        op.create_table(
            'stem_files',
            sa.Column('id', sa.String(length=36), nullable=False),
            sa.Column('project_id', sa.String(length=36), nullable=False),
            sa.Column('uploaded_by', sa.String(length=36), nullable=False),
            sa.Column('name', sa.String(length=255), nullable=False),
            sa.Column('file_url', sa.String(length=500), nullable=True),
            sa.Column('file_size', sa.Integer(), nullable=True),
            sa.Column('file_type', sa.String(length=50), nullable=True),
            sa.Column('duration', sa.Float(), nullable=True),
            sa.Column('bpm', sa.Integer(), nullable=True),
            sa.Column('key', sa.String(length=10), nullable=True),
            sa.Column('version', sa.Integer(), default=1, nullable=True),
            sa.Column('previous_version_id', sa.String(length=36), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(['project_id'], ['collaboration_projects.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['uploaded_by'], ['users.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['previous_version_id'], ['stem_files.id'], ondelete='SET NULL'),
            sa.PrimaryKeyConstraint('id'),
        )
        op.create_index('ix_stem_files_project_id', 'stem_files', ['project_id'])
        op.create_index('ix_stem_files_created_at', 'stem_files', ['created_at'])
    
    # 4. Create project_versions table
    if 'project_versions' not in existing_tables:
        op.create_table(
            'project_versions',
            sa.Column('id', sa.String(length=36), nullable=False),
            sa.Column('project_id', sa.String(length=36), nullable=False),
            sa.Column('version_number', sa.Integer(), nullable=True),
            sa.Column('name', sa.String(length=255), nullable=True),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('master_file_url', sa.String(length=500), nullable=True),
            sa.Column('stem_manifest', sa.JSON(), nullable=True),
            sa.Column('created_by', sa.String(length=36), nullable=True),
            sa.Column('approved_by', sa.String(length=36), nullable=True),
            sa.Column('approval_status', sa.String(length=50), nullable=True),
            sa.Column('feedback', sa.JSON(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
            sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(['project_id'], ['collaboration_projects.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
            sa.ForeignKeyConstraint(['approved_by'], ['users.id'], ondelete='SET NULL'),
            sa.PrimaryKeyConstraint('id'),
        )
        op.create_index('ix_project_versions_project_id', 'project_versions', ['project_id'])
        op.create_index('ix_project_versions_created_at', 'project_versions', ['created_at'])


def downgrade() -> None:
    """Drop collaboration system tables."""
    op.drop_index('ix_project_versions_created_at', table_name='project_versions')
    op.drop_index('ix_project_versions_project_id', table_name='project_versions')
    op.drop_table('project_versions')
    
    op.drop_index('ix_stem_files_created_at', table_name='stem_files')
    op.drop_index('ix_stem_files_project_id', table_name='stem_files')
    op.drop_table('stem_files')
    
    op.drop_index('ix_project_collaborators_user_id', table_name='project_collaborators')
    op.drop_index('ix_project_collaborators_project_id', table_name='project_collaborators')
    op.drop_table('project_collaborators')
    
    op.drop_index('ix_collaboration_projects_created_at', table_name='collaboration_projects')
    op.drop_index('ix_collaboration_projects_status', table_name='collaboration_projects')
    op.drop_index('ix_collaboration_projects_creator_id', table_name='collaboration_projects')
    op.drop_table('collaboration_projects')
