import { useState } from 'react';
import { Card } from '@/components/common';
import { StatusBadge } from '@/components/common';
import { Search, Download } from 'lucide-react';
import { useLogs } from '@/hooks/useLogs';
import { formatRelativeTime } from '@/lib/utils';
import type { LogLevel } from '@/types/database';

export function LogsPage() {
    const [searchQuery, setSearchQuery] = useState('');
    const [levelFilter, setLevelFilter] = useState<LogLevel | ''>('');

    const { logs, loading, exportLogs } = useLogs({
        level: levelFilter || undefined,
        search: searchQuery || undefined,
    });

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="text-white/70">Loading logs...</div>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-white">Logs</h1>
                    <p className="text-white/50 mt-1">{logs.length} log entries</p>
                </div>
                <button
                    onClick={() => exportLogs('json')}
                    className="flex items-center gap-2 px-4 py-2 bg-white/10 hover:bg-white/20 text-white rounded transition-colors"
                >
                    <Download className="w-4 h-4" />
                    Export Logs
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
                        placeholder="Search logs..."
                        className="w-full pl-10 pr-4 py-2 bg-white/5 border border-white/10 rounded text-white placeholder:text-white/40 focus:outline-none focus:border-white/20 transition-colors"
                    />
                </div>
                <select
                    value={levelFilter}
                    onChange={(e) => setLevelFilter(e.target.value as LogLevel | '')}
                    className="px-4 py-2 bg-[hsl(var(--card))] border border-white/10 rounded text-white focus:outline-none focus:border-white/20 transition-colors [&>option]:bg-[hsl(var(--card))] [&>option]:text-white"
                >
                    <option value="">All Levels</option>
                    <option value="debug">Debug</option>
                    <option value="info">Info</option>
                    <option value="warning">Warning</option>
                    <option value="error">Error</option>
                    <option value="critical">Critical</option>
                </select>
            </div>

            {/* Logs List */}
            {logs.length === 0 ? (
                <Card className="p-12 text-center">
                    <p className="text-white/50">
                        {searchQuery || levelFilter
                            ? 'No logs found matching your filters.'
                            : 'No logs available.'}
                    </p>
                </Card>
            ) : (
                <div className="space-y-2">
                    {logs.map((log) => (
                        <Card key={log.id} className="p-4 hover:border-white/20 transition-colors font-mono text-sm">
                            <div className="flex items-start gap-4">
                                <span className="text-white/40 shrink-0">
                                    {new Date(log.created_at).toLocaleTimeString()}
                                </span>
                                <StatusBadge
                                    variant={log.level}
                                    label={log.level.toUpperCase()}
                                    size="sm"
                                />
                                <p className="flex-1 text-white/80">{log.message}</p>
                            </div>
                        </Card>
                    ))}
                </div>
            )}
        </div>
    );
}
