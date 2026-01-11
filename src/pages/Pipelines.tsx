import { Card } from '@/components/common';
import { usePipelineStore } from '@/store';
import { StatusBadge } from '@/components/common';
import { formatRelativeTime } from '@/lib/utils';
import { Plus, Search, Filter, MoreVertical } from 'lucide-react';

export function PipelinesPage() {
    const { pipelines } = usePipelineStore();

    return (
        <div className="space-y-6 animate-fade-in">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-white/90">Pipelines</h1>
                    <p className="text-white/40">
                        Manage and monitor your automation pipelines
                    </p>
                </div>
                <button className="flex items-center gap-2 px-4 py-2 bg-white/10 text-white/80 rounded hover:bg-white/15 transition-colors">
                    <Plus size={18} />
                    New Pipeline
                </button>
            </div>

            {/* Filters */}
            <div className="flex items-center gap-4">
                <div className="relative flex-1 max-w-md">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-white/40" size={18} />
                    <input
                        type="text"
                        placeholder="Search pipelines..."
                        className="w-full pl-10 pr-4 py-2 bg-white/5 border border-white/10 rounded text-white/80 placeholder:text-white/30 focus:outline-none focus:border-white/20"
                    />
                </div>
                <button className="flex items-center gap-2 px-4 py-2 bg-white/5 border border-white/10 rounded text-white/50 hover:text-white/70 transition-colors">
                    <Filter size={18} />
                    Filter
                </button>
            </div>

            {/* Pipeline Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {pipelines.map((pipeline) => (
                    <Card key={pipeline.id} className="hover:border-white/20 cursor-pointer">
                        <div className="flex items-start justify-between mb-3">
                            <StatusBadge variant={pipeline.status} />
                            <button className="p-1 rounded hover:bg-white/10 text-white/40">
                                <MoreVertical size={16} />
                            </button>
                        </div>
                        <h3 className="font-semibold text-white/90 mb-1">{pipeline.name}</h3>
                        <p className="text-sm text-white/40 mb-4 line-clamp-2">
                            {pipeline.description}
                        </p>
                        <div className="flex items-center justify-between text-xs text-white/40">
                            <span>{pipeline.stages.length} stages</span>
                            <span>Last run: {formatRelativeTime(pipeline.lastExecution)}</span>
                        </div>
                        {pipeline.status === 'running' && (
                            <div className="mt-3">
                                <div className="flex justify-between text-xs mb-1">
                                    <span className="text-white/40">Progress</span>
                                    <span className="text-white/60">{pipeline.progress}%</span>
                                </div>
                                <div className="h-1 bg-white/10 rounded-full overflow-hidden">
                                    <div
                                        className="h-full bg-white/40 rounded-full"
                                        style={{ width: `${pipeline.progress}%` }}
                                    />
                                </div>
                            </div>
                        )}
                    </Card>
                ))}
            </div>
        </div>
    );
}
