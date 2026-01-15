import { useState } from 'react';
import { Card, StatusBadge } from '@/components/common';
import { usePipelines } from '@/hooks/usePipelines';
import { useExecutions } from '@/hooks/useExecutions';
import { formatRelativeTime } from '@/lib/utils';
import {
    Play,
    Pause,
    RefreshCw,
    MoreVertical,
    ChevronRight,
    GitBranch,
    Loader2
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { toast } from '@/components/common';

interface PipelineCardProps {
    pipeline: {
        id: string;
        name: string;
        description?: string | null;
        is_active: boolean;
        updated_at: string;
        config?: unknown;
    };
    execution?: {
        status: string;
        progress?: number;
    } | null;
    onPause?: () => void;
    onRefresh?: () => void;
}

function PipelineCard({ pipeline, execution, onPause, onRefresh }: PipelineCardProps) {
    const [showMenu, setShowMenu] = useState(false);
    const navigate = useNavigate();

    const status = execution?.status || (pipeline.is_active ? 'active' : 'inactive');
    const progress = execution?.progress || (status === 'running' ? 67 : status === 'completed' ? 100 : 0);
    const pipelineConfig = pipeline.config as { stages?: Array<{ id: string; name: string; type: string }> } | null;
    const stages = pipelineConfig?.stages || [];
    const stageCount = stages.length || 4;

    return (
        <div className="flex items-center justify-between p-3 rounded-lg bg-white/[0.02] hover:bg-white/[0.04] border border-white/5 transition-all group">
            {/* Left: Pipeline Info */}
            <div className="flex items-center gap-3 flex-1 min-w-0">
                <div className="w-1.5 h-1.5 rounded-full bg-white/30 flex-shrink-0" />
                <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-0.5">
                        <h4
                            className="text-sm font-medium text-white/90 truncate cursor-pointer hover:text-white"
                            onClick={() => navigate(`/pipelines/${pipeline.id}`)}
                        >
                            {pipeline.name}
                        </h4>
                        <StatusBadge
                            variant={status === 'running' ? 'info' : status === 'completed' ? 'success' : status === 'failed' ? 'error' : 'default'}
                            label={status.charAt(0).toUpperCase() + status.slice(1)}
                            size="sm"
                        />
                    </div>
                    <p className="text-xs text-white/40 truncate">
                        {pipeline.description || 'No description'}
                    </p>
                </div>
            </div>

            {/* Center: Progress (for running) or spacer */}
            <div className="flex items-center gap-3 mx-4">
                {status === 'running' && (
                    <>
                        <span className="text-sm text-white/60">{progress}%</span>
                        <div className="w-20 h-1 bg-white/10 rounded-full overflow-hidden">
                            <div
                                className="h-full bg-white/40 rounded-full"
                                style={{ width: `${progress}%` }}
                            />
                        </div>
                    </>
                )}
            </div>

            {/* Stage Indicators */}
            <div className="flex items-center gap-1 mr-3">
                {Array.from({ length: Math.min(stageCount, 4) }).map((_, i) => (
                    <div
                        key={i}
                        className={`w-5 h-5 rounded text-[10px] font-medium flex items-center justify-center border ${status === 'running' && i < Math.ceil(progress / (100 / stageCount))
                                ? 'bg-white/10 border-white/20 text-white/70'
                                : status === 'completed'
                                    ? 'bg-white/10 border-white/20 text-white/70'
                                    : 'bg-white/5 border-white/10 text-white/30'
                            }`}
                    >
                        {i + 1}
                    </div>
                ))}
                {stageCount > 4 && (
                    <span className="text-[10px] text-white/30 ml-1">+{stageCount - 4}</span>
                )}
            </div>

            {/* Time */}
            <span className="text-xs text-white/40 w-16 text-right">
                {formatRelativeTime(pipeline.updated_at)}
            </span>

            {/* Action Buttons */}
            <div className="flex items-center gap-0.5 ml-2 opacity-0 group-hover:opacity-100 transition-opacity">
                {status === 'running' && onPause && (
                    <button
                        onClick={onPause}
                        className="p-1.5 hover:bg-white/10 rounded transition-colors"
                        title="Pause"
                    >
                        <Pause className="w-3.5 h-3.5 text-white/40" />
                    </button>
                )}
                <button
                    onClick={() => {
                        onRefresh?.();
                        toast.info('Refreshing...');
                    }}
                    className="p-1.5 hover:bg-white/10 rounded transition-colors"
                    title="Refresh"
                >
                    <RefreshCw className="w-3.5 h-3.5 text-white/40" />
                </button>
                <div className="relative">
                    <button
                        onClick={() => setShowMenu(!showMenu)}
                        className="p-1.5 hover:bg-white/10 rounded transition-colors"
                        title="More"
                    >
                        <MoreVertical className="w-3.5 h-3.5 text-white/40" />
                    </button>
                    {showMenu && (
                        <div className="absolute right-0 top-full mt-1 w-32 bg-[#1a1a1a] border border-white/10 rounded-lg shadow-xl z-20 overflow-hidden">
                            <button className="w-full px-3 py-2 text-left text-xs text-white/60 hover:bg-white/5">
                                View Details
                            </button>
                            <button className="w-full px-3 py-2 text-left text-xs text-white/60 hover:bg-white/5">
                                Edit
                            </button>
                            <button className="w-full px-3 py-2 text-left text-xs text-white/60 hover:bg-white/5">
                                Delete
                            </button>
                        </div>
                    )}
                </div>
            </div>

            {/* Chevron */}
            <ChevronRight className="w-4 h-4 text-white/20 ml-1" />
        </div>
    );
}

export function PipelineStatus() {
    const { pipelines, loading, refetch } = usePipelines();
    const { executions } = useExecutions();
    const navigate = useNavigate();

    // Get latest execution for each pipeline
    const pipelineExecutions = new Map(
        executions.map(e => [e.pipeline_id, { status: e.status, progress: e.status === 'running' ? 67 : 0 }])
    );

    // Show recent pipelines
    const recentPipelines = pipelines.slice(0, 5);

    if (loading) {
        return (
            <Card title="Pipeline Status" description="Active and recent pipelines">
                <div className="flex items-center justify-center py-8">
                    <Loader2 className="w-6 h-6 text-white/20 animate-spin" />
                </div>
            </Card>
        );
    }

    return (
        <Card
            title="Pipeline Status"
            description="Active and recent pipelines"
            headerAction={
                <button
                    onClick={() => navigate('/pipelines')}
                    className="flex items-center gap-1 text-xs text-white/40 hover:text-white/60"
                >
                    View all
                </button>
            }
        >
            {recentPipelines.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-10 text-center">
                    <GitBranch className="w-10 h-10 text-white/15 mb-3" />
                    <h3 className="text-sm font-medium text-white/60 mb-1">No Pipelines Yet</h3>
                    <p className="text-xs text-white/30 mb-3">
                        Create your first pipeline to get started
                    </p>
                    <button
                        onClick={() => navigate('/pipelines')}
                        className="px-3 py-1.5 bg-white/10 hover:bg-white/15 text-white/70 text-xs rounded transition-colors flex items-center gap-1.5"
                    >
                        <Play className="w-3 h-3" />
                        Create Pipeline
                    </button>
                </div>
            ) : (
                <div className="space-y-2">
                    {recentPipelines.map((pipeline) => (
                        <PipelineCard
                            key={pipeline.id}
                            pipeline={pipeline}
                            execution={pipelineExecutions.get(pipeline.id)}
                            onPause={() => toast.info('Pipeline paused')}
                            onRefresh={refetch}
                        />
                    ))}
                </div>
            )}
        </Card>
    );
}
