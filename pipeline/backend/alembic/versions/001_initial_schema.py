"""Initial schema

Revision ID: 001
Revises: 
Create Date: 2026-01-13

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create pipelines table
    op.create_table(
        'pipelines',
        sa.Column('id', sa.String(64), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('version', sa.String(32), default='1.0.0'),
        sa.Column('definition', sa.JSON, nullable=False),
        sa.Column('config', sa.JSON, default={}),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('schedule', sa.String(128), nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('ix_pipelines_id', 'pipelines', ['id'])
    op.create_index('ix_pipelines_name', 'pipelines', ['name'])
    
    # Create pipeline_stages table
    op.create_table(
        'pipeline_stages',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('stage_id', sa.String(64), nullable=False),
        sa.Column('pipeline_id', sa.String(64), sa.ForeignKey('pipelines.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('stage_type', sa.String(32), nullable=False),
        sa.Column('config', sa.JSON, default={}),
        sa.Column('dependencies', sa.JSON, default=[]),
        sa.Column('timeout', sa.Integer, default=120),
        sa.Column('max_retries', sa.Integer, default=3),
        sa.Column('retry_delay', sa.Float, default=1.0),
        sa.Column('is_critical', sa.Boolean, default=True),
        sa.Column('order', sa.Integer, default=0),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index('ix_pipeline_stages_stage_id', 'pipeline_stages', ['stage_id'])
    op.create_index('ix_pipeline_stages_pipeline_order', 'pipeline_stages', ['pipeline_id', 'order'])
    
    # Create executions table
    op.create_table(
        'executions',
        sa.Column('id', sa.String(64), primary_key=True),
        sa.Column('pipeline_id', sa.String(64), sa.ForeignKey('pipelines.id', ondelete='SET NULL'), nullable=True),
        sa.Column('pipeline_name', sa.String(255), nullable=False),
        sa.Column('pipeline_version', sa.String(32), nullable=True),
        sa.Column('status', sa.String(32), nullable=False, default='pending'),
        sa.Column('total_stages', sa.Integer, default=0),
        sa.Column('completed_stages', sa.Integer, default=0),
        sa.Column('current_stage', sa.String(64), nullable=True),
        sa.Column('started_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('completed_at', sa.DateTime, nullable=True),
        sa.Column('duration', sa.Float, nullable=True),
        sa.Column('context', sa.JSON, default={}),
        sa.Column('variables', sa.JSON, default={}),
        sa.Column('error', sa.Text, nullable=True),
        sa.Column('risk_score', sa.Float, nullable=True),
        sa.Column('ai_blocked', sa.Boolean, default=False),
        sa.Column('triggered_by', sa.String(128), default='manual'),
        sa.Column('trigger_metadata', sa.JSON, default={}),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index('ix_executions_id', 'executions', ['id'])
    op.create_index('ix_executions_status', 'executions', ['status'])
    op.create_index('ix_executions_pipeline_status', 'executions', ['pipeline_id', 'status'])
    op.create_index('ix_executions_started_at', 'executions', ['started_at'])
    
    # Create stage_executions table
    op.create_table(
        'stage_executions',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('execution_id', sa.String(64), sa.ForeignKey('executions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('stage_id', sa.String(64), nullable=False),
        sa.Column('stage_name', sa.String(255), nullable=False),
        sa.Column('status', sa.String(32), nullable=False, default='pending'),
        sa.Column('started_at', sa.DateTime, nullable=True),
        sa.Column('completed_at', sa.DateTime, nullable=True),
        sa.Column('duration', sa.Float, nullable=True),
        sa.Column('retry_count', sa.Integer, default=0),
        sa.Column('output', sa.JSON, nullable=True),
        sa.Column('error', sa.Text, nullable=True),
        sa.Column('is_anomaly', sa.Boolean, default=False),
        sa.Column('anomaly_reason', sa.Text, nullable=True),
    )
    op.create_index('ix_stage_executions_stage_id', 'stage_executions', ['stage_id'])
    op.create_index('ix_stage_executions_execution_stage', 'stage_executions', ['execution_id', 'stage_id'])
    
    # Create logs table
    op.create_table(
        'logs',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('execution_id', sa.String(64), sa.ForeignKey('executions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('stage_id', sa.String(64), nullable=True),
        sa.Column('level', sa.String(16), default='info'),
        sa.Column('message', sa.Text, nullable=False),
        sa.Column('metadata', sa.JSON, default={}),
        sa.Column('timestamp', sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index('ix_logs_timestamp', 'logs', ['timestamp'])
    op.create_index('ix_logs_execution_timestamp', 'logs', ['execution_id', 'timestamp'])
    
    # Create ai_insights table
    op.create_table(
        'ai_insights',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('pipeline_id', sa.String(64), sa.ForeignKey('pipelines.id', ondelete='CASCADE'), nullable=True),
        sa.Column('execution_id', sa.String(64), sa.ForeignKey('executions.id', ondelete='CASCADE'), nullable=True),
        sa.Column('stage_id', sa.String(64), nullable=True),
        sa.Column('insight_type', sa.String(32), nullable=False),
        sa.Column('severity', sa.String(16), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('message', sa.Text, nullable=False),
        sa.Column('recommendation', sa.Text, nullable=True),
        sa.Column('confidence', sa.Float, default=0.0),
        sa.Column('risk_score', sa.Float, nullable=True),
        sa.Column('factors', sa.JSON, default=[]),
        sa.Column('explanation', sa.Text, nullable=True),
        sa.Column('action_taken', sa.String(64), nullable=True),
        sa.Column('action_result', sa.Text, nullable=True),
        sa.Column('is_resolved', sa.Boolean, default=False),
        sa.Column('resolved_at', sa.DateTime, nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index('ix_ai_insights_pipeline', 'ai_insights', ['pipeline_id'])
    op.create_index('ix_ai_insights_type_severity', 'ai_insights', ['insight_type', 'severity'])
    op.create_index('ix_ai_insights_created_at', 'ai_insights', ['created_at'])
    
    # Create execution_locks table
    op.create_table(
        'execution_locks',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('pipeline_id', sa.String(64), nullable=False, unique=True),
        sa.Column('execution_id', sa.String(64), nullable=True),
        sa.Column('locked_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('expires_at', sa.DateTime, nullable=False),
        sa.Column('holder', sa.String(255), nullable=True),
    )
    op.create_index('ix_execution_locks_pipeline', 'execution_locks', ['pipeline_id'])
    op.create_index('ix_execution_locks_expires', 'execution_locks', ['expires_at'])
    
    # Create metrics table
    op.create_table(
        'metrics',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('metric_type', sa.String(64), nullable=False),
        sa.Column('metric_name', sa.String(128), nullable=False),
        sa.Column('value', sa.Float, nullable=False),
        sa.Column('unit', sa.String(32), default=''),
        sa.Column('pipeline_id', sa.String(64), nullable=True),
        sa.Column('execution_id', sa.String(64), nullable=True),
        sa.Column('tags', sa.JSON, default={}),
        sa.Column('timestamp', sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index('ix_metrics_type', 'metrics', ['metric_type'])
    op.create_index('ix_metrics_timestamp', 'metrics', ['timestamp'])
    op.create_index('ix_metrics_type_timestamp', 'metrics', ['metric_type', 'timestamp'])


def downgrade() -> None:
    op.drop_table('metrics')
    op.drop_table('execution_locks')
    op.drop_table('ai_insights')
    op.drop_table('logs')
    op.drop_table('stage_executions')
    op.drop_table('executions')
    op.drop_table('pipeline_stages')
    op.drop_table('pipelines')
