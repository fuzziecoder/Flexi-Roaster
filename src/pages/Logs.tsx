import { useState } from 'react';
import { useExecutions } from '@/lib/hooks';
import { FileText, Search, Filter } from 'lucide-react';

export function LogsPage() {
    const { data: executions } = useExecutions();
    const [searchTerm, setSearchTerm] = useState('');
    const [levelFilter, setLevelFilter] = useState('all');

    // Collect all logs from all executions
    const allLogs: any[] = [];
    (executions || []).forEach((execution: any) => {
        if (execution.stage_executions) {
            execution.stage_executions.forEach((stage: any) => {
                if (stage.error) {
                    allLogs.push({
                        timestamp: stage.completed_at || stage.started_at,
                        level: 'error',
                        message: `Stage ${stage.stage_id}: ${stage.error}`,
                        execution_id: execution.id,
                        pipeline_name: execution.pipeline_name,
                    });
                }
            });
        }
    });

    // Filter logs
    const filteredLogs = allLogs.filter((log) => {
        const matchesSearch =
            searchTerm === '' ||
            log.message.toLowerCase().includes(searchTerm.toLowerCase()) ||
            log.pipeline_name.toLowerCase().includes(searchTerm.toLowerCase());

        const matchesLevel = levelFilter === 'all' || log.level === levelFilter;

        return matchesSearch && matchesLevel;
    });

    const getLevelColor = (level: string) => {
        switch (level) {
            case 'error':
                return 'text-red-400';
            case 'warn':
                return 'text-yellow-400';
            case 'info':
                return 'text-blue-400';
            default:
                return 'text-white/50';
        }
    };

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-semibold text-white/90">Logs</h1>
                    <p className="text-sm text-white/50 mt-1">Execution logs and events</p>
                </div>
            </div>

            {/* Filters */}
            <div className="flex items-center gap-4">
                <div className="flex-1 relative">
                    <Search size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-white/40" />
                    <input
                        type="text"
                        placeholder="Search logs..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="w-full pl-10 pr-4 py-2 bg-[hsl(var(--card))] border border-white/10 rounded-lg text-white/90 placeholder:text-white/40 focus:outline-none focus:border-white/30"
                    />
                </div>

                <div className="flex items-center gap-2">
                    <Filter size={18} className="text-white/40" />
                    <select
                        value={levelFilter}
                        onChange={(e) => setLevelFilter(e.target.value)}
                        className="px-3 py-2 bg-[hsl(var(--card))] border border-white/10 rounded-lg text-white/90 focus:outline-none focus:border-white/30"
                    >
                        <option value="all">All Levels</option>
                        <option value="error">Error</option>
                        <option value="warn">Warning</option>
                        <option value="info">Info</option>
                    </select>
                </div>
            </div>

            {/* Logs List */}
            <div className="bg-[hsl(var(--card))] border border-white/10 rounded-lg">
                <div className="p-4 border-b border-white/10">
                    <div className="flex items-center justify-between">
                        <h2 className="text-sm font-medium text-white/90">Log Entries</h2>
                        <span className="text-xs text-white/50">{filteredLogs.length} entries</span>
                    </div>
                </div>

                <div className="divide-y divide-white/10 max-h-[600px] overflow-y-auto">
                    {filteredLogs.length === 0 ? (
                        <div className="p-8 text-center">
                            <FileText size={48} className="mx-auto text-white/20 mb-4" />
                            <p className="text-white/50">
                                {searchTerm || levelFilter !== 'all'
                                    ? 'No logs match your filters'
                                    : 'No logs available yet'}
                            </p>
                        </div>
                    ) : (
                        filteredLogs.map((log, index) => (
                            <div key={index} className="p-4 hover:bg-white/5 transition-colors font-mono text-xs">
                                <div className="flex items-start gap-4">
                                    <span className="text-white/40 whitespace-nowrap">
                                        {new Date(log.timestamp).toLocaleTimeString()}
                                    </span>
                                    <span className={`font-semibold uppercase ${getLevelColor(log.level)}`}>
                                        [{log.level}]
                                    </span>
                                    <div className="flex-1">
                                        <div className="text-white/70">{log.message}</div>
                                        <div className="text-white/40 mt-1">
                                            {log.pipeline_name} • {log.execution_id}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        ))
                    )}
                </div>
            </div>
        </div>
    );
}
