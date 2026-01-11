import { cn, formatRelativeTime } from '@/lib/utils';
import { Card } from '@/components/common';
import { mockLogs } from '@/lib/mockData';
import type { LogLevel } from '@/types';

// Muted grey styles for log levels
const levelStyles: Record<LogLevel, string> = {
    info: 'text-white/70',
    warn: 'text-white/60',
    error: 'text-white/90',
    debug: 'text-white/40',
    success: 'text-white/60',
};

const levelBgStyles: Record<LogLevel, string> = {
    info: 'bg-white/10',
    warn: 'bg-white/10',
    error: 'bg-white/15',
    debug: 'bg-white/5',
    success: 'bg-white/5',
};

export function ActivityLog() {
    return (
        <Card
            title="Activity Log"
            description="Recent system events"
            headerAction={
                <div className="flex items-center gap-2">
                    <select className="text-sm bg-white/5 border border-white/10 rounded px-2 py-1 text-white/60">
                        <option value="all">All Levels</option>
                        <option value="info">Info</option>
                        <option value="warn">Warning</option>
                        <option value="error">Error</option>
                    </select>
                    <button className="text-sm text-white/50 hover:text-white/70">
                        View all
                    </button>
                </div>
            }
            noPadding
        >
            <div className="max-h-[400px] overflow-y-auto">
                <div className="divide-y divide-white/5">
                    {mockLogs.map((log) => (
                        <div
                            key={log.id}
                            className={cn(
                                'flex items-start gap-3 p-3 transition-colors',
                                'hover:bg-white/5'
                            )}
                        >
                            {/* Level Badge */}
                            <span
                                className={cn(
                                    'px-2 py-0.5 text-xs font-mono font-semibold rounded flex-shrink-0',
                                    levelBgStyles[log.level],
                                    levelStyles[log.level]
                                )}
                            >
                                {log.level.toUpperCase()}
                            </span>

                            {/* Timestamp */}
                            <span className="text-xs text-white/40 font-mono flex-shrink-0 w-16">
                                {formatRelativeTime(log.timestamp)}
                            </span>

                            {/* Service */}
                            <span className="text-xs text-white/50 font-mono flex-shrink-0 hidden sm:block w-32 truncate">
                                [{log.service}]
                            </span>

                            {/* Message */}
                            <span className="text-sm text-white/70 font-mono flex-1 break-all">
                                {log.message}
                            </span>
                        </div>
                    ))}
                </div>
            </div>

            {/* Live indicator */}
            <div className="flex items-center justify-center gap-2 p-2 border-t border-white/5 bg-white/[0.02]">
                <div className="w-1.5 h-1.5 rounded-full bg-white/50 animate-pulse" />
                <span className="text-xs text-white/40">Live updates enabled</span>
            </div>
        </Card>
    );
}
