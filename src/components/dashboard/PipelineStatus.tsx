import { cn, formatRelativeTime } from '@/lib/utils';
import { StatusBadge, Card } from '@/components/common';
import { usePipelineStore } from '@/store';
import { Play, Pause, RefreshCw, MoreVertical, ChevronRight } from 'lucide-react';

export function PipelineStatus() {
    const { pipelines } = usePipelineStore();

    return (
        <Card
            title="Pipeline Status"
            description="Active and recent pipelines"
            headerAction={
                <button className="text-sm text-white/50 hover:text-white/70">
                    View all
                </button>
            }
            noPadding
        >
            <div className="divide-y divide-white/5">
                {pipelines.map((pipeline) => (
                    <div
                        key={pipeline.id}
                        className={cn(
                            'flex items-center gap-4 p-4 transition-colors',
                            'hover:bg-white/[0.02] cursor-pointer group'
                        )}
                    >
                        {/* Status Indicator */}
                        <div
                            className={cn(
                                'w-2 h-2 rounded-full flex-shrink-0 bg-white/40',
                                pipeline.status === 'running' && 'animate-pulse bg-white/60',
                                pipeline.status === 'completed' && 'bg-white/30',
                                pipeline.status === 'failed' && 'bg-white/70',
                                pipeline.status === 'pending' && 'bg-white/20'
                            )}
                        />

                        {/* Pipeline Info */}
                        <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2">
                                <h4 className="font-medium text-white/90 truncate">{pipeline.name}</h4>
                                <StatusBadge variant={pipeline.status} size="sm" />
                            </div>
                            <p className="text-sm text-white/40 truncate">
                                {pipeline.description}
                            </p>
                        </div>

                        {/* Progress */}
                        {pipeline.status === 'running' && (
                            <div className="hidden sm:flex flex-col items-end min-w-[80px]">
                                <span className="text-sm font-medium text-white/70">{pipeline.progress}%</span>
                                <div className="w-full h-1 bg-white/10 rounded-full mt-1 overflow-hidden">
                                    <div
                                        className="h-full bg-white/40 rounded-full transition-all duration-300"
                                        style={{ width: `${pipeline.progress}%` }}
                                    />
                                </div>
                            </div>
                        )}

                        {/* Stages */}
                        <div className="hidden md:flex items-center gap-1">
                            {pipeline.stages.slice(0, 4).map((stage, idx) => (
                                <div
                                    key={stage.id}
                                    className={cn(
                                        'w-6 h-6 rounded flex items-center justify-center text-xs font-medium',
                                        stage.status === 'completed' && 'bg-white/10 text-white/50',
                                        stage.status === 'running' && 'bg-white/15 text-white/70 animate-pulse',
                                        stage.status === 'failed' && 'bg-white/20 text-white/80',
                                        stage.status === 'pending' && 'bg-white/5 text-white/30'
                                    )}
                                    title={`${stage.name}: ${stage.status}`}
                                >
                                    {idx + 1}
                                </div>
                            ))}
                            {pipeline.stages.length > 4 && (
                                <span className="text-xs text-white/30">
                                    +{pipeline.stages.length - 4}
                                </span>
                            )}
                        </div>

                        {/* Last Execution */}
                        <div className="hidden lg:block text-sm text-white/40 min-w-[100px] text-right">
                            {formatRelativeTime(pipeline.lastExecution)}
                        </div>

                        {/* Actions */}
                        <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                            {pipeline.status === 'running' ? (
                                <button className="p-1.5 rounded hover:bg-white/10 text-white/40 hover:text-white/70">
                                    <Pause size={16} />
                                </button>
                            ) : (
                                <button className="p-1.5 rounded hover:bg-white/10 text-white/40 hover:text-white/70">
                                    <Play size={16} />
                                </button>
                            )}
                            <button className="p-1.5 rounded hover:bg-white/10 text-white/40 hover:text-white/70">
                                <RefreshCw size={16} />
                            </button>
                            <button className="p-1.5 rounded hover:bg-white/10 text-white/40 hover:text-white/70">
                                <MoreVertical size={16} />
                            </button>
                        </div>

                        {/* Chevron */}
                        <ChevronRight
                            size={16}
                            className="text-white/30 group-hover:text-white/50 transition-colors"
                        />
                    </div>
                ))}
            </div>
        </Card>
    );
}
