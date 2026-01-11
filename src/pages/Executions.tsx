import { useExecutions } from '@/lib/hooks';
import { StatusBadge } from '@/components/common';
import { Play, Clock, CheckCircle, XCircle, ChevronRight } from 'lucide-react';
import { formatDate, formatDuration } from '@/lib/formatters';
import { Link } from 'react-router-dom';

export function ExecutionsPage() {
    const { data: executions, isLoading, error } = useExecutions();

    if (isLoading) {
        return (
            <div className="flex items-center justify-center h-96">
                <div className="text-white/50">Loading executions...</div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="flex items-center justify-center h-96">
                <div className="text-red-400">Error loading executions. Make sure backend is running.</div>
            </div>
        );
    }

    const executionsList = executions || [];

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-semibold text-white/90">Executions</h1>
                    <p className="text-sm text-white/50 mt-1">Pipeline execution history</p>
                </div>
                <div className="flex items-center gap-3">
                    <span className="text-sm text-white/50">
                        Total: {executionsList.length}
                    </span>
                </div>
            </div>

            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="bg-[hsl(var(--card))] border border-white/10 rounded-lg p-4">
                    <div className="flex items-center gap-3">
                        <div className="p-2 bg-white/5 rounded">
                            <Play size={20} className="text-white/70" />
                        </div>
                        <div>
                            <div className="text-xs text-white/50">Running</div>
                            <div className="text-xl font-semibold text-white/90">
                                {executionsList.filter((e: any) => e.status === 'running').length}
                            </div>
                        </div>
                    </div>
                </div>

                <div className="bg-[hsl(var(--card))] border border-white/10 rounded-lg p-4">
                    <div className="flex items-center gap-3">
                        <div className="p-2 bg-white/5 rounded">
                            <CheckCircle size={20} className="text-white/70" />
                        </div>
                        <div>
                            <div className="text-xs text-white/50">Completed</div>
                            <div className="text-xl font-semibold text-white/90">
                                {executionsList.filter((e: any) => e.status === 'completed').length}
                            </div>
                        </div>
                    </div>
                </div>

                <div className="bg-[hsl(var(--card))] border border-white/10 rounded-lg p-4">
                    <div className="flex items-center gap-3">
                        <div className="p-2 bg-white/5 rounded">
                            <XCircle size={20} className="text-white/70" />
                        </div>
                        <div>
                            <div className="text-xs text-white/50">Failed</div>
                            <div className="text-xl font-semibold text-white/90">
                                {executionsList.filter((e: any) => e.status === 'failed').length}
                            </div>
                        </div>
                    </div>
                </div>

                <div className="bg-[hsl(var(--card))] border border-white/10 rounded-lg p-4">
                    <div className="flex items-center gap-3">
                        <div className="p-2 bg-white/5 rounded">
                            <Clock size={20} className="text-white/70" />
                        </div>
                        <div>
                            <div className="text-xs text-white/50">Avg Duration</div>
                            <div className="text-xl font-semibold text-white/90">
                                {executionsList.length > 0
                                    ? formatDuration(
                                        executionsList.reduce((sum: number, e: any) => sum + (e.duration || 0), 0) /
                                        executionsList.length
                                    )
                                    : '0s'}
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Executions List */}
            <div className="bg-[hsl(var(--card))] border border-white/10 rounded-lg">
                <div className="p-4 border-b border-white/10">
                    <h2 className="text-sm font-medium text-white/90">Recent Executions</h2>
                </div>

                <div className="divide-y divide-white/10">
                    {executionsList.length === 0 ? (
                        <div className="p-8 text-center text-white/50">
                            No executions yet. Start by executing a pipeline.
                        </div>
                    ) : (
                        executionsList.map((execution: any) => (
                            <Link
                                key={execution.id}
                                to={`/executions/${execution.id}`}
                                className="block p-4 hover:bg-white/5 transition-colors"
                            >
                                <div className="flex items-center justify-between">
                                    <div className="flex-1">
                                        <div className="flex items-center gap-3">
                                            <StatusBadge variant={execution.status} />
                                            <span className="font-medium text-white/90">
                                                {execution.pipeline_name}
                                            </span>
                                        </div>
                                        <div className="flex items-center gap-4 mt-2 text-xs text-white/50">
                                            <span>ID: {execution.id}</span>
                                            <span>Started: {formatDate(execution.started_at)}</span>
                                            {execution.duration && (
                                                <span>Duration: {formatDuration(execution.duration)}</span>
                                            )}
                                        </div>
                                    </div>
                                    <ChevronRight size={20} className="text-white/30" />
                                </div>
                            </Link>
                        ))
                    )}
                </div>
            </div>
        </div>
    );
}
