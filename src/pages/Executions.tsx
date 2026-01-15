import { useState } from 'react';
import { Card } from '@/components/common';
import { StatusBadge } from '@/components/common';
import { Play, Search, Calendar } from 'lucide-react';
import { useExecutions } from '@/hooks/useExecutions';
import { TriggerExecutionModal } from '@/components/modals';
import { formatRelativeTime } from '@/lib/utils';

export function ExecutionsPage() {
    const { executions, loading } = useExecutions();
    const [showTriggerModal, setShowTriggerModal] = useState(false);
    const [searchQuery, setSearchQuery] = useState('');
    const [statusFilter, setStatusFilter] = useState<string>('all');

    const filteredExecutions = executions.filter(exec => {
        const matchesSearch = exec.pipeline?.name.toLowerCase().includes(searchQuery.toLowerCase());
        const matchesStatus = statusFilter === 'all' || exec.status === statusFilter;
        return matchesSearch && matchesStatus;
    });

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="text-white/70">Loading executions...</div>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-white">Executions</h1>
                    <p className="text-white/50 mt-1">{filteredExecutions.length} executions</p>
                </div>
                <button
                    onClick={() => setShowTriggerModal(true)}
                    className="flex items-center gap-2 px-4 py-2 bg-white/90 hover:bg-white text-black rounded font-medium transition-colors"
                >
                    <Play className="w-4 h-4" />
                    Trigger Execution
                </button>
            </div>

            {/* Filters */}
            <div className="flex items-center gap-4">
                <div className="relative flex-1">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/40" />
                    <input
                        type="text"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        placeholder="Search by pipeline name..."
                        className="w-full pl-10 pr-4 py-2 bg-white/5 border border-white/10 rounded text-white placeholder:text-white/40 focus:outline-none focus:border-white/20 transition-colors"
                    />
                </div>
                <select
                    value={statusFilter}
                    onChange={(e) => setStatusFilter(e.target.value)}
                    className="px-4 py-2 bg-[hsl(var(--card))] border border-white/10 rounded text-white focus:outline-none focus:border-white/20 transition-colors [&>option]:bg-[hsl(var(--card))] [&>option]:text-white"
                >
                    <option value="all">All Status</option>
                    <option value="pending">Pending</option>
                    <option value="running">Running</option>
                    <option value="completed">Completed</option>
                    <option value="failed">Failed</option>
                    <option value="cancelled">Cancelled</option>
                </select>
            </div>

            {/* Executions List */}
            {filteredExecutions.length === 0 ? (
                <Card className="p-12 text-center">
                    <p className="text-white/50">
                        {searchQuery || statusFilter !== 'all'
                            ? 'No executions found matching your filters.'
                            : 'No executions yet. Trigger your first execution!'}
                    </p>
                </Card>
            ) : (
                <div className="space-y-3">
                    {filteredExecutions.map((execution) => (
                        <Card key={execution.id} className="p-4 hover:border-white/20 transition-colors">
                            <div className="flex items-center justify-between">
                                <div className="flex-1">
                                    <div className="flex items-center gap-3 mb-2">
                                        <h3 className="text-lg font-semibold text-white">
                                            {execution.pipeline?.name || 'Unknown Pipeline'}
                                        </h3>
                                        <StatusBadge
                                            variant={execution.status}
                                            label={execution.status.charAt(0).toUpperCase() + execution.status.slice(1)}
                                            pulse={execution.status === 'running'}
                                        />
                                    </div>
                                    <div className="flex items-center gap-4 text-sm text-white/50">
                                        <span className="flex items-center gap-1.5">
                                            <Calendar className="w-4 h-4" />
                                            {formatRelativeTime(execution.created_at)}
                                        </span>
                                        {execution.started_at && (
                                            <span>
                                                Started: {formatRelativeTime(execution.started_at)}
                                            </span>
                                        )}
                                        {execution.completed_at && (
                                            <span>
                                                Completed: {formatRelativeTime(execution.completed_at)}
                                            </span>
                                        )}
                                    </div>
                                    {execution.error_message && (
                                        <p className="mt-2 text-sm text-red-400">
                                            Error: {execution.error_message}
                                        </p>
                                    )}
                                </div>
                            </div>
                        </Card>
                    ))}
                </div>
            )}

            {/* Trigger Execution Modal */}
            <TriggerExecutionModal
                isOpen={showTriggerModal}
                onClose={() => setShowTriggerModal(false)}
            />
        </div>
    );
}
