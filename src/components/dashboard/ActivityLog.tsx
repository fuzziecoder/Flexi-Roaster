import { Card } from '@/components/common';
import { StatusBadge } from '@/components/common';
import { useLogs } from '@/hooks/useLogs';
import { formatRelativeTime } from '@/lib/utils';

export function ActivityLog() {
    const { logs, loading } = useLogs({}, 10); // Get latest 10 logs

    return (
        <Card
            title="Activity Log"
            description="Recent system events"
            headerAction={
                <div className="flex items-center gap-2">
                    <button className="text-sm text-white/50 hover:text-white/70">
                        View all
                    </button>
                </div>
            }
            noPadding
        >
            <div className="max-h-[400px] overflow-y-auto">
                {loading ? (
                    <div className="flex items-center justify-center py-8">
                        <p className="text-white/50">Loading logs...</p>
                    </div>
                ) : logs.length === 0 ? (
                    <div className="flex items-center justify-center py-12 text-center">
                        <p className="text-white/50">No activity logs yet</p>
                    </div>
                ) : (
                    <div className="divide-y divide-white/5">
                        {logs.map((log) => (
                            <div
                                key={log.id}
                                className="flex items-start gap-3 p-3 transition-colors hover:bg-white/5"
                            >
                                {/* Level Badge */}
                                <StatusBadge
                                    variant={log.level}
                                    label={log.level.toUpperCase()}
                                    size="sm"
                                />

                                {/* Timestamp */}
                                <span className="text-xs text-white/40 font-mono flex-shrink-0 w-16">
                                    {formatRelativeTime(log.created_at)}
                                </span>

                                {/* Message */}
                                <span className="text-sm text-white/70 font-mono flex-1 break-all">
                                    {log.message}
                                </span>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {/* Live indicator */}
            <div className="flex items-center justify-center gap-2 p-2 border-t border-white/5 bg-white/[0.02]">
                <div className="w-1.5 h-1.5 rounded-full bg-white/50 animate-pulse" />
                <span className="text-xs text-white/40">Live updates enabled</span>
            </div>
        </Card>
    );
}
